"""Propose IEEE S&P papers using verified Crossref DOI links only."""

import argparse
from collections import Counter
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

HEADING = "### IEEE Symposium on Security and Privacy (IEEE S&P)"
CROSSREF = "https://api.crossref.org/works"


def normalize(text):
    text = unicodedata.normalize("NFKD", unescape(text).casefold().replace("&", "and"))
    return "".join(c for c in text if c.isalnum())


def author_key(name):
    words = re.findall(r"[^\W\d_]+", unicodedata.normalize("NFKD", name.casefold()))
    # Full given/family names must match; an optional middle initial may differ.
    if len(words) > 2:
        words = [w for w in words if len(w) > 1]
    return tuple(sorted(words))


class AcceptedPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.divs = []
        self.cycles = Counter()
        self.papers = []
        self.card = None
        self.card_depth = None
        self.title_active = False
        self.authors_active = False
        self.sup_depth = 0
        self.page_title = []
        self.page_title_active = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "title":
            self.page_title_active = True
        if tag == "div":
            identity = attrs.get("id", "")
            self.divs.append(identity)
            if identity in ("cycle1", "cycle2"):
                self.cycles[identity] += 1
            cycle = next((c for c in reversed(self.divs) if c in ("cycle1", "cycle2")), None)
            if cycle and "list-group-item" in classes:
                if self.card is not None:
                    raise ValueError("Nested S&P paper cards")
                self.card = {"cycle": cycle, "title": [], "authors": [], "anchor": ""}
                self.card_depth = len(self.divs)
            if self.card is not None and "authorlist" in classes:
                self.authors_active = True
        if self.card is not None:
            if tag == "a" and attrs.get("data-toggle") == "collapse":
                if self.card["anchor"]:
                    raise ValueError("Multiple title anchors in a paper card")
                self.title_active = True
                self.card["anchor"] = attrs.get("href", "")
            if tag == "sup":
                self.sup_depth += 1
            if tag == "br":
                self.authors_active = False

    def handle_data(self, text):
        if self.page_title_active:
            self.page_title.append(text)
        if self.card is not None:
            if self.title_active:
                self.card["title"].append(text)
            elif self.authors_active and self.sup_depth == 0:
                self.card["authors"].append(text)

    def handle_endtag(self, tag):
        if tag == "title":
            self.page_title_active = False
        if tag == "a":
            self.title_active = False
        if tag == "sup":
            self.sup_depth = max(0, self.sup_depth - 1)
        if tag == "div" and self.divs:
            if self.card is not None and len(self.divs) == self.card_depth:
                title = " ".join("".join(self.card["title"]).split())
                authors = [" ".join(a.split()) for a in re.split(
                    r",|\band\b", "".join(self.card["authors"])) if a.strip()]
                anchor = self.card["anchor"]
                if not title or not authors or not re.fullmatch(r"#collapse-\d+", anchor):
                    raise ValueError("Missing title, authors or stable anchor in S&P card")
                self.papers.append({"title": title, "authors": authors,
                                    "cycle": self.card["cycle"], "anchor": anchor})
                self.card = None
                self.card_depth = None
                self.authors_active = False
            self.divs.pop()


def accepted(html, year, source):
    page = AcceptedPage()
    page.feed(html)
    page.close()
    if normalize("".join(page.page_title)) != normalize(f"IEEE Symposium on Security and Privacy {year}"):
        raise ValueError("S&P accepted-page year/title does not match")
    if page.cycles != {"cycle1": 1, "cycle2": 1} or page.card or page.divs:
        raise ValueError("Incomplete or changed S&P cycle structure")
    totals = Counter(p["cycle"] for p in page.papers)
    if not all(totals[c] for c in ("cycle1", "cycle2")):
        raise ValueError("Empty S&P cycle; inspect the official page")
    titles = [normalize(p["title"]) for p in page.papers]
    anchors = [p["anchor"] for p in page.papers]
    if len(set(titles)) != len(titles) or len(set(anchors)) != len(anchors):
        raise ValueError("Duplicate S&P title or anchor")
    papers = [{**p, "source": source + p["anchor"]} for p in page.papers
              if "fuzz" in p["title"].casefold()]
    if not papers:
        raise ValueError("No fuzz title candidates; inspect the source")
    return papers, dict(totals)


def doi_url(doi):
    if not isinstance(doi, str) or not re.fullmatch(r"10\.1109/[^\s<>]+", doi, re.I):
        raise ValueError("Expected an IEEE DOI")
    return "https://doi.org/" + quote(doi.lower(), safe="/")


def match_record(paper, record, year):
    reasons = []
    if not any(normalize(t) == normalize(paper["title"]) for t in record.get("title", [])):
        reasons.append("title mismatch")
    venues = {normalize(f"{year} IEEE Symposium on Security and Privacy"),
              normalize(f"{year} IEEE Symposium on Security and Privacy (SP)")}
    if not any(normalize(v) in venues for v in record.get("container-title", [])):
        reasons.append("not the requested S&P main proceedings")
    date = record.get("published", {}).get("date-parts", [[]])
    if not date or not date[0] or date[0][0] != year:
        reasons.append("publication year mismatch")
    if record.get("type") != "proceedings-article" or record.get("publisher") != "IEEE":
        reasons.append("not an IEEE proceedings article")
    expected = Counter(author_key(a) for a in paper["authors"])
    actual = Counter(author_key(a.get("given", "") + " " + a.get("family", ""))
                     for a in record.get("author", []))
    if not expected or actual != expected:
        reasons.append("author list mismatch")
    try:
        doi_url(record.get("DOI"))
    except ValueError:
        reasons.append("missing or invalid IEEE DOI")
    return reasons


def resolve(paper, records, year, lookup):
    comparisons = [{"doi": r.get("DOI"), "title": r.get("title"),
                    "reasons": match_record(paper, r, year)} for r in records]
    matches = {r["doi"].lower() for r in comparisons if not r["reasons"]}
    result = {**paper, "matches": comparisons}
    if len(matches) != 1:
        return {**result, "status": "pending_doi", "reason":
                "No exact bibliographic match" if not matches else "Multiple matching DOIs"}
    doi = matches.pop()
    verified = lookup(doi)
    reasons = match_record(paper, verified, year)
    if reasons or verified.get("DOI", "").lower() != doi:
        return {**result, "status": "pending_doi", "reason": "DOI record failed verification",
                "verification_errors": reasons}
    return {**result, "status": "verified", "doi": doi, "url": doi_url(doi),
            "metadata_source": f"{CROSSREF}/{quote(doi, safe='')}"}


def fetch(url, content_type):
    for attempt in range(3):
        request = Request(url, headers={
            "User-Agent": "awesome-fuzzing-sp/1.0 (https://github.com/cpuu/awesome-fuzzing)",
            "Accept": content_type,
        })
        try:
            with urlopen(request, timeout=30) as response:
                if urlparse(response.url).netloc != urlparse(url).netloc:
                    raise ValueError("Unexpected source redirect")
                if content_type not in response.headers.get("Content-Type", ""):
                    raise ValueError(f"Unexpected content type from {urlparse(url).netloc}")
                return response.read().decode("utf-8")
        except HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            if attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def crossref_message(url):
    response = json.loads(fetch(url, "application/json"))
    if response.get("status") != "ok" or not isinstance(response.get("message"), dict):
        raise ValueError("Malformed Crossref response")
    return response["message"]


def lookup(doi):
    return crossref_message(f"{CROSSREF}/{quote(doi, safe='')}")


def collect(year):
    source = f"https://sp{year}.ieee-security.org/accepted-papers.html"
    papers, totals = accepted(fetch(source, "text/html"), year, source)
    results = []
    for paper in papers:
        # Fuzzy matching in cryptography is not sufficient evidence of fuzz testing.
        if "fuzz" not in re.sub(r"\bfuzzy\b", "", paper["title"], flags=re.I).casefold():
            results.append({**paper, "status": "pending_scope",
                            "reason": "Keyword occurs only in Fuzzy; maintainer scope review required"})
            continue
        query = urlencode({"query.bibliographic": paper["title"], "rows": 10})
        records = crossref_message(f"{CROSSREF}?{query}").get("items")
        if not isinstance(records, list):
            raise ValueError("Missing Crossref result list")
        results.append(resolve(paper, records, year, lookup))
        time.sleep(0.2)
    dois = [p["doi"] for p in results if p["status"] == "verified"]
    if len(dois) != len(set(dois)):
        raise ValueError("Multiple accepted titles resolved to the same DOI")
    return source, totals, results


def markdown_title(title):
    return re.sub(r"([\\`*_\[\]])", r"\\\1", escape(title, quote=False))


def propose(readme, papers, year):
    if readme.count(HEADING) != 1:
        raise ValueError("S&P section missing or ambiguous")
    start = readme.index(HEADING) + len(HEADING)
    following = re.search(r"^###? ", readme[start:], re.M)
    if not following:
        raise ValueError("Cannot locate end of S&P section")
    end = start + following.start()
    section = readme[start:end]
    pattern = rf"<details><summary>{year} \((\d+) papers\)</summary>\n(.*?)</details>"
    blocks = list(re.finditer(pattern, section, re.S))
    if len(blocks) > 1 or (f"<summary>{year}" in section and not blocks):
        raise ValueError("Unexpected or duplicate S&P year block")
    existing = []
    if blocks:
        for line in blocks[0][2].splitlines():
            if not line.strip():
                continue
            entry = re.fullmatch(r"- \[((?:\\.|[^\]])+), (\d{4})\]\(([^\s]+)\)", line)
            if not entry or int(entry[2]) != year:
                raise ValueError("Custom S&P year content; review manually")
            title = re.sub(r"\\(.)", r"\1", entry[1])
            existing.append({"line": line, "title": normalize(title), "url": entry[3]})
        if len(existing) != int(blocks[0][1]):
            raise ValueError("Incorrect existing S&P paper count")
        if len({p['title'] for p in existing}) != len(existing):
            raise ValueError("Duplicate existing S&P title")
    additions, warnings, matched = [], [], set()
    for paper in sorted(papers, key=lambda p: normalize(p["title"])):
        same = [p for p in existing if p["title"] == normalize(paper["title"])
                or (paper.get("url") and p["url"].casefold() == paper["url"].casefold())]
        if len(same) > 1:
            raise ValueError("Multiple existing entries match one S&P candidate")
        if same:
            matched.add(same[0]["line"])
            if paper.get("url") != same[0]["url"]:
                warnings.append(f"Preserved existing entry/link: {paper['title']}")
            continue
        if paper["status"] == "verified":
            url = doi_url(paper["doi"])
            additions.append(f"- [{markdown_title(paper['title'])}, {year}]({url})")
    if len(matched) != len(existing):
        raise ValueError("Existing S&P entries missing from source; no automatic deletion")
    if not additions:
        return readme, additions, warnings
    lines = [p["line"] for p in existing] + additions
    block = f"<details><summary>{year} ({len(lines)} papers)</summary>\n\n" + "\n".join(lines) + "\n\n</details>"
    if blocks:
        section = section[:blocks[0].start()] + block + section[blocks[0].end():]
    else:
        # Keep years descending, including when backfilling an older year.
        older = next((m for m in re.finditer(r"<details><summary>(\d{4}) ", section)
                      if int(m[1]) < year), None)
        pos = older.start() if older else len(section.rstrip())
        prefix, suffix = section[:pos].rstrip(), section[pos:].lstrip()
        section = prefix + "\n\n" + block + "\n\n" + suffix
    updated = readme[:start] + section + readme[end:]
    updated = re.sub(r"(conferences \(2008[\u2013-])(\d{4})(\))",
                     lambda m: m[1] + str(max(int(m[2]), year)) + m[3], updated)
    return updated, additions, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not 2008 <= args.year <= 2100:
        parser.error("Year must be between 2008 and 2100")
    source, totals, papers = collect(args.year)
    original = args.readme.read_text(encoding="utf-8")
    updated, additions, warnings = propose(original, papers, args.year)
    summary = {"cycles": dict(Counter(p["cycle"] for p in papers)),
               "statuses": dict(Counter(p["status"] for p in papers)), "additions": len(additions)}
    report = {"source": source, "year": args.year, "accepted_totals": totals,
              **summary, "papers": papers, "warnings": warnings}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "candidates.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output_dir / "README.md").write_text(updated, encoding="utf-8")
    body = ["<!-- awesome-fuzzing-sp -->", f"IEEE S&P {args.year} DOI-only candidates.",
            f"Source: {source}", f"Summary: {summary}",
            "Only verified DOI records are proposed. Pending candidates are not added.",
            "Review scope and bibliographic matches before merging. No automatic merge.", ""]
    for p in papers:
        body.append(f"- {markdown_title(p['title'])} ({p['cycle']}, {p['status']}): " +
                    (p["url"] if p["status"] == "verified" else p["reason"]))
    body.extend(["", *[markdown_title(w) for w in warnings]])
    (args.output_dir / "pr-body.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    if args.write and updated != original:
        args.readme.write_text(updated, encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
