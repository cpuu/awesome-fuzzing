"""Propose NDSS title-keyword matches without removing curated entries."""

import argparse
from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

HOST = "www.ndss-symposium.org"
HEADING = "### The Network and Distributed System Security Symposium (NDSS)"


def official_url(value, base):
    url = urljoin(base, value)
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != HOST:
        raise ValueError(f"Unexpected NDSS link: {url}")
    return url


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.titles = []
        self.heading = []
        self.classes = set()
        self.links = []
        self.capture = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "article":
            self.classes.update(classes)
        if tag == "h1" or (tag == "h2" and "pt-cv-title" in classes):
            self.capture = {"tag": tag, "text": [], "url": ""}
        if tag == "a":
            if self.capture is not None:
                self.capture["url"] = attrs.get("href", "")
            if "pdf-button" in classes:
                self.links.append(attrs.get("href", ""))

    def handle_data(self, text):
        if self.capture is not None:
            self.capture["text"].append(text)

    def handle_endtag(self, tag):
        if self.capture is not None and tag == self.capture["tag"]:
            title = " ".join("".join(self.capture["text"]).split())
            if tag == "h1":
                self.heading.append(title)
            else:
                self.titles.append((title, self.capture["url"]))
            self.capture = None


def accepted(html, year, source):
    page = Page(html)
    if not any(f"{year} Accepted Papers" in h for h in page.heading):
        raise ValueError("Accepted-page title changed or year does not match")
    if not page.titles or len(set(page.titles)) != len(page.titles):
        raise ValueError("Missing or duplicate paper cards; inspect page structure")
    # When supplied by NDSS, the total guards against pagination/truncated HTML.
    total = re.search(r"([\d,]+) papers were accepted", html)
    if total and int(total[1].replace(",", "")) != len(page.titles):
        raise ValueError("Paper-card count does not match the published total")
    candidates = []
    for title, href in page.titles:
        if "fuzz" in title.casefold():
            if not href:
                raise ValueError(f"Missing paper link: {title}")
            candidates.append({"title": title, "page": official_url(href, source)})
    if not candidates:
        raise ValueError("No title matches; inspect source before proposing changes")
    if (len({p["title"].casefold() for p in candidates}) != len(candidates)
            or len({p["page"] for p in candidates}) != len(candidates)):
        raise ValueError("Duplicate candidate title or page URL")
    return candidates


def detail(html, paper, year):
    page = Page(html)
    if paper["title"] not in page.heading:
        raise ValueError(f"Detail title does not match: {paper['title']}")
    if f"category-ndss-{year}" not in page.classes:
        raise ValueError("Detail page belongs to a different or unknown year")
    cycles = [c for c in ("summer", "fall") if f"tag-{c}-cycle-{year}" in page.classes]
    if len(cycles) != 1:
        raise ValueError(f"Unknown submission cycle: {paper['title']}")
    if len(page.links) > 1:
        raise ValueError("Ambiguous paper PDF links")
    pdf = official_url(page.links[0], paper["page"]) if page.links else None
    if pdf and not urlparse(pdf).path.lower().endswith(".pdf"):
        raise ValueError("Paper download is not a PDF URL")
    return {**paper, "cycle": cycles[0], "pdf": pdf, "url": pdf or paper["page"]}


def markdown_title(title):
    # Escape external titles as text, never executable Markdown or HTML.
    title = escape(title, quote=False)
    return re.sub(r"([\\`*_\[\]])", r"\\\1", title)


def propose(readme, papers, year):
    if readme.count(HEADING) != 1:
        raise ValueError("NDSS section missing or ambiguous")
    start = readme.index(HEADING) + len(HEADING)
    following = re.search(r"^###? ", readme[start:], re.M)
    if not following:
        raise ValueError("Cannot locate end of NDSS section")
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
        else:
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
    source = f"https://{HOST}/ndss{args.year}/accepted-papers/"
    papers = [detail(fetch(p["page"]), p, args.year)
              for p in accepted(fetch(source), args.year, source)]
    original = args.readme.read_text()
    updated, additions, warnings = propose(original, papers, args.year)
    counts = dict(Counter(p["cycle"] for p in papers))
    report = {"source": source, "year": args.year, "counts": counts,
              "papers": papers, "additions": len(additions), "warnings": warnings}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "candidates.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    (args.output_dir / "README.md").write_text(updated)
    body = ["<!-- awesome-fuzzing-ndss -->", f"NDSS {args.year} title-keyword candidates.",
            f"Source: {source}", f"Matches: {len(papers)}; cycles: {counts}; additions: {len(additions)}.",
            "Human review required. No automatic merge. Existing entries are never deleted.", ""]
    for p in papers:
        body.append(f"- {markdown_title(p['title'])} ({p['cycle']}): {p['page']}" +
                    (" (PDF not published; using official paper page)" if not p["pdf"] else ""))
    body.extend(["", *warnings])
    (args.output_dir / "pr-body.md").write_text("\n".join(body) + "\n")
    if args.write and updated != original:
        args.readme.write_text(updated)
    print(json.dumps({"counts": counts, "additions": len(additions), "warnings": warnings}))


if __name__ == "__main__":
    main()
