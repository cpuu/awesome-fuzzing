"""Propose USENIX Security title-keyword matches without removing curated entries."""

import argparse
from collections import Counter
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError

HOST = "www.usenix.org"
HEADING = "### USENIX Security"


def official_url(value, base):
    url = urljoin(base, value)
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != HOST:
        raise ValueError(f"Unexpected USENIX Security link: {url}")
    return url


def normalize(text):
    return " ".join(unescape(text).split()).casefold()


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.titles = []
        self.heading = []
        self.metadata = {}
        self.articles = []
        self.paper_count = 0
        self.capture = None
        self.feed(html)
        self.close()
        if self.capture or self.articles:
            raise ValueError("Incomplete USENIX HTML structure")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").startswith("citation_"):
            self.metadata.setdefault(attrs["name"], []).append(attrs.get("content", ""))
        if tag == "article":
            classes = attrs.get("class", "").split()
            is_paper = "node-paper" in classes and "view-mode-schedule" in classes
            self.articles.append(is_paper)
            self.paper_count += int(is_paper)
        if tag == "h1" and attrs.get("id") == "page-title" or (
                tag == "h2" and self.articles and self.articles[-1]):
            if self.capture:
                raise ValueError("Nested paper headings")
            self.capture = {"tag": tag, "text": [], "urls": []}
        if tag == "a" and self.capture is not None:
            self.capture["urls"].append(attrs.get("href", ""))

    def handle_data(self, text):
        if self.capture is not None:
            self.capture["text"].append(text)

    def handle_endtag(self, tag):
        if self.capture is not None and tag == self.capture["tag"]:
            title = " ".join("".join(self.capture["text"]).split())
            if tag == "h1":
                self.heading.append(title)
            else:
                if not title or len(self.capture["urls"]) != 1:
                    raise ValueError("Missing or ambiguous USENIX paper title/link")
                self.titles.append((title, self.capture["urls"][0]))
            self.capture = None
        if tag == "article":
            if not self.articles:
                raise ValueError("Unbalanced USENIX article")
            self.articles.pop()


def accepted(html, year, cycle, source):
    page = Page(html)
    expected = f"USENIX Security '{year % 100:02d} Cycle {cycle} Accepted Papers"
    if page.heading != [expected]:
        raise ValueError("Accepted-page title, year or cycle does not match")
    if not page.titles or len(page.titles) != page.paper_count:
        raise ValueError("Missing paper titles; inspect page structure")
    titles, urls, candidates = set(), set(), []
    for title, href in page.titles:
        url = official_url(href, source)
        parsed = urlparse(url)
        if not parsed.path.startswith(f"/conference/usenixsecurity{year % 100:02d}/presentation/") or parsed.query or parsed.fragment:
            raise ValueError("Wrong year or unexpected presentation URL")
        if normalize(title) in titles or url in urls:
            raise ValueError("Duplicate title or paper URL within cycle")
        titles.add(normalize(title))
        urls.add(url)
        if "fuzz" in title.casefold():
            candidates.append({"title": title, "page": url, "cycle": str(cycle)})
    return candidates, len(page.titles)


def detail(html, paper, year):
    page = Page(html)
    if len(page.heading) != 1 or normalize(page.heading[0]) != normalize(paper["title"]):
        raise ValueError("Detail title does not match accepted paper")
    dates = page.metadata.get("citation_publication_date", [])
    venues = page.metadata.get("citation_conference_title", [])
    if dates != [str(year)] or len(venues) != 1 or not re.fullmatch(
            rf"\d+(?:st|nd|rd|th) USENIX Security Symposium \(USENIX Security {year % 100:02d}\)", venues[0]):
        raise ValueError("Wrong or missing USENIX publication metadata")
    # Citation metadata identifies the paper, avoiding slides and supplementary PDFs.
    links = page.metadata.get("citation_pdf_url", [])
    if len(links) > 1:
        raise ValueError("Ambiguous citation PDF")
    pdf = official_url(links[0], paper["page"]) if links else None
    if pdf and (not urlparse(pdf).path.startswith("/system/files/") or
                not urlparse(pdf).path.lower().endswith(".pdf")):
        raise ValueError("Unexpected official paper PDF")
    return {**paper, "pdf": pdf, "url": pdf or paper["page"]}


def collect(year):
    sources, candidates, seen = {}, [], {}
    for cycle in (1, 2):
        source = f"https://{HOST}/conference/usenixsecurity{year % 100:02d}/cycle{cycle}-accepted-papers"
        try:
            html = fetch(source)
        except HTTPError as error:
            if cycle != 2 or error.code != 404:
                raise
            sources[str(cycle)] = {"url": source, "status": "unpublished", "http_status": 404}
            continue
        papers, total = accepted(html, year, cycle, source)
        sources[str(cycle)] = {"url": source, "status": "published", "total": total,
                               "matches": len(papers)}
        for paper in papers:
            key = normalize(paper["title"])
            if key in seen:
                if seen[key] != paper["page"]:
                    raise ValueError("Conflicting paper links across cycles")
                continue
            if paper["page"] in seen.values():
                raise ValueError("Conflicting titles across cycles")
            seen[key] = paper["page"]
            candidates.append(paper)
    if not candidates:
        raise ValueError("No fuzz title candidates; inspect sources")
    papers = []
    for paper in candidates:
        if "fuzz" not in re.sub(r"\bfuzzy\b", "", paper["title"], flags=re.I).casefold():
            papers.append({**paper, "status": "pending_scope", "pdf": None,
                           "url": paper["page"]})
        else:
            papers.append({**detail(fetch(paper["page"]), paper, year), "status": "verified"})
    return sources, papers


def markdown_title(title):
    # Escape external titles as text, never executable Markdown or HTML.
    title = escape(title, quote=False)
    return re.sub(r"([\\`*_\[\]])", r"\\\1", title)


def propose(readme, papers, year):
    if readme.count(HEADING) != 1:
        raise ValueError("USENIX Security section missing or ambiguous")
    start = readme.index(HEADING) + len(HEADING)
    following = re.search(r"^###? ", readme[start:], re.M)
    if not following:
        raise ValueError("Cannot locate end of USENIX Security section")
    end = start + following.start()
    section = readme[start:end]
    block_pattern = rf"<details><summary>{year} \((\d+) papers\)</summary>\n(.*?)</details>"
    blocks = list(re.finditer(block_pattern, section, re.S))
    if len(blocks) > 1 or (f"<summary>{year}" in section and not blocks):
        raise ValueError("Unexpected or duplicate year block")
    existing = []
    if blocks:
        existing = [line for line in blocks[0][2].splitlines() if line.strip()]
        if any(not line.startswith("- [") for line in existing):
            raise ValueError("Year block contains custom content; review manually")
        if len(existing) != int(blocks[0][1]):
            raise ValueError("Existing paper count is incorrect")
    additions = []
    warnings = []
    matched = set()
    for paper in sorted(papers, key=lambda p: p["title"].casefold()):
        prefix = f"- [{markdown_title(paper['title'])}, {year}]"
        same = [line for line in existing if line.casefold().startswith(prefix.casefold())
                or any(f"]({url})" in line for url in (paper["page"], paper["url"]))]
        if same:
            matched.update(same)
            if same != [f"{prefix}({paper['url']})"]:
                warnings.append(f"Review existing title/link for {paper['title']}; preserved unchanged.")
        elif paper.get("status") != "pending_scope":
            additions.append(f"{prefix}({paper['url']})")
    if len(matched) != len(existing):
        raise ValueError("Existing entries disappeared from the source; no automatic deletion or update")
    if not additions:
        return readme, additions, warnings
    entries = existing + additions
    block = f"<details><summary>{year} ({len(entries)} papers)</summary>\n\n" + "\n".join(entries) + "\n\n</details>"
    if blocks:
        section = section[:blocks[0].start()] + block + section[blocks[0].end():]
    else:
        section = "\n\n" + block + section
    updated = readme[:start] + section + readme[end:]
    # Keep the documented coverage range consistent when adding a newer year.
    updated = re.sub(r"(conferences \(2008[–-])(\d{4})(\))",
                     lambda m: m[1] + str(max(int(m[2]), year)) + m[3], updated)
    return updated, additions, warnings


def fetch(url):
    request = Request(url, headers={"User-Agent": "awesome-fuzzing-maintenance/1.0"})
    with urlopen(request, timeout=30) as response:
        official_url(response.url, url)
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise ValueError("Expected an HTML page")
        return response.read().decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not 2008 <= args.year <= 2100:
        parser.error("Year must be between 2008 and 2100")
    sources, papers = collect(args.year)
    original = args.readme.read_text()
    updated, additions, warnings = propose(original, papers, args.year)
    counts = dict(Counter(p["cycle"] for p in papers))
    report = {"sources": sources, "year": args.year, "counts": counts,
              "papers": papers, "additions": len(additions), "warnings": warnings}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "candidates.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    (args.output_dir / "README.md").write_text(updated)
    body = ["<!-- awesome-fuzzing-usenix -->", f"USENIX Security {args.year} title-keyword candidates.",
            f"Sources: {json.dumps(sources)}", f"Matches: {len(papers)}; cycles: {counts}; additions: {len(additions)}.",
            "Human review required. No automatic merge. Existing entries are never deleted.", ""]
    for p in papers:
        body.append(f"- {markdown_title(p['title'])} ({p['cycle']}): {p['page']}" +
                    (" (pending scope review: Fuzzy-only title; not proposed)" if p.get("status") == "pending_scope"
                     else " (PDF not published; using official paper page)" if not p["pdf"] else ""))
    body.extend(["", *warnings])
    (args.output_dir / "pr-body.md").write_text("\n".join(body) + "\n")
    if args.write and updated != original:
        args.readme.write_text(updated)
    print(json.dumps({"counts": counts, "additions": len(additions), "warnings": warnings}))


if __name__ == "__main__":
    main()
