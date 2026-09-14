"""Propose ACM CCS papers using verified Crossref DOI links only."""

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
from urllib.parse import quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

HEADING = "### ACM Conference on Computer and Communications Security (ACM CCS)"
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
        self.capture = None
        self.headings = []
        self.page_title = ""
        self.cycle = None
        self.cycles = Counter()
        self.tables = Counter()
        self.in_table = False
        self.row = None
        self.cell = None
        self.header_seen = False
        self.papers = []
        self.row_links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("title", "h2", "h3"):
            if self.in_table or self.capture is not None:
                raise ValueError("Unexpected heading inside CCS table")
            self.capture = {"tag": tag, "text": []}
        if tag == "table":
            if self.in_table:
                raise ValueError("Nested CCS table")
            if "accepted-papers-table" not in attrs.get("class", "").split():
                raise ValueError("Unknown table on CCS accepted page")
            if self.cycle is None:
                raise ValueError("CCS table without a recognized cycle")
            self.in_table = True
            self.tables[self.cycle] += 1
            self.header_seen = False
        if not self.in_table:
            return
        if tag == "tr":
            if self.row is not None:
                raise ValueError("Unclosed CCS table row")
            self.row = []
            self.row_links = []
        elif tag in ("td", "th"):
            if self.row is None or self.cell is not None:
                raise ValueError("Malformed CCS table cell")
            self.cell = {"tag": tag, "text": []}
        elif tag == "br" and self.cell is not None:
            self.cell["text"].append("\n")
        elif tag == "a" and self.cell is not None and not self.row:
            self.row_links.append(attrs.get("href", ""))

    def handle_data(self, text):
        if self.capture is not None:
            self.capture["text"].append(text)
        if self.cell is not None:
            self.cell["text"].append(text)

    def handle_endtag(self, tag):
        if self.capture is not None and tag == self.capture["tag"]:
            text = " ".join("".join(self.capture["text"]).split())
            if tag == "title":
                self.page_title += text
            elif tag == "h2":
                self.headings.append(text)
                self.cycle = None
            else:
                cycles = {"First Cycle": "first", "Second Cycle": "second"}
                if text not in cycles:
                    raise ValueError("Unknown CCS cycle heading")
                self.cycle = cycles[text]
                self.cycles[self.cycle] += 1
            self.capture = None
        if not self.in_table:
            return
        if tag in ("td", "th"):
            if self.cell is None or self.cell["tag"] != tag:
                raise ValueError("Mismatched CCS table cell")
            self.row.append((tag, "".join(self.cell["text"])))
            self.cell = None
        elif tag == "tr":
            if self.cell is not None or self.row is None or len(self.row) != 2:
                raise ValueError("Incomplete CCS table row")
            if [c[0] for c in self.row] == ["th", "th"]:
                if self.header_seen or [c[1].strip() for c in self.row] != ["Title", "Author"]:
                    raise ValueError("Changed CCS table headers")
                self.header_seen = True
            elif [c[0] for c in self.row] == ["td", "td"] and self.header_seen:
                title = " ".join(self.row[0][1].split())
                authors = []
                for line in self.row[1][1].splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    # Remove the trailing affiliation, retaining parenthesized names.
                    match = re.fullmatch(r"(.+?)\s+\((.*)\)", line)
                    if not match:
                        raise ValueError("Missing CCS author affiliation")
                    # A name like Dave (Jing) Tian has a separate final affiliation.
                    depth, start = 0, None
                    for i, char in enumerate(line):
                        if char == "(":
                            if depth == 0:
                                start = i
                            depth += 1
                        elif char == ")":
                            depth -= 1
                            if depth < 0:
                                raise ValueError("Unbalanced author affiliation")
                    if depth or start is None:
                        raise ValueError("Unbalanced author affiliation")
                    name = line[:start].strip()
                    if not name:
                        raise ValueError("Missing CCS author name")
                    authors.append(name)
                if not title or not authors:
                    raise ValueError("Missing CCS title or authors")
                paper = {"title": title, "authors": authors, "cycle": self.cycle}
                if "fuzz" in title.casefold() and self.row_links:
                    dois = {doi_from_url(url) for url in self.row_links}
                    if None in dois or len(dois) != 1:
                        raise ValueError("Unexpected or ambiguous official CCS DOI links")
                    paper.update(official_doi=dois.pop(), official_url=self.row_links[0])
                self.papers.append(paper)
            else:
                raise ValueError("Changed CCS table row structure")
            self.row = None
        elif tag == "table":
            if self.row is not None or self.cell is not None or not self.header_seen:
                raise ValueError("Incomplete CCS table")
            self.in_table = False


def accepted(html, year, source):
    page = AcceptedPage()
    page.feed(html)
    page.close()
    if normalize(page.page_title) != normalize(f"ACM CCS {year}"):
        raise ValueError("CCS accepted-page year/title does not match")
    if page.headings.count("ACCEPTED PAPERS") != 1:
        raise ValueError("Missing or duplicate CCS accepted heading")
    if page.capture or page.in_table or page.row is not None or page.cell is not None:
        raise ValueError("Incomplete CCS page structure")
    if page.cycles not in ({"first": 1}, {"first": 1, "second": 1}):
        raise ValueError("Missing or duplicate CCS cycles")
    if page.tables != page.cycles:
        raise ValueError("Missing or duplicate CCS cycle tables")
    totals = Counter(p["cycle"] for p in page.papers)
    if set(totals) != set(page.cycles):
        raise ValueError("Empty CCS cycle")
    titles = [normalize(p["title"]) for p in page.papers]
    if len(set(titles)) != len(titles):
        raise ValueError("Duplicate CCS title")
    papers = [{**p, "source": source} for p in page.papers
              if "fuzz" in p["title"].casefold()]
    if not papers:
        raise ValueError("No fuzz title candidates; inspect the source")
    return papers, dict(totals)


def doi_url(doi):
    if not isinstance(doi, str) or not re.fullmatch(r"10\.1145/[^\s<>]+", doi, re.I):
        raise ValueError("Expected an ACM DOI")
    return "https://doi.org/" + quote(doi.lower(), safe="/")


def doi_from_url(url):
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.query or parsed.fragment:
        return None
    path = unquote(parsed.path)
    if parsed.netloc == "dl.acm.org":
        match = re.fullmatch(r"/doi/(?:abs/|pdf/|epdf/|full/)?(10\.1145/[^/\s]+)", path)
    elif parsed.netloc == "doi.org":
        match = re.fullmatch(r"/(10\.1145/[^/\s]+)", path)
    else:
        return None
    if not match:
        return None
    try:
        doi_url(match[1])
    except ValueError:
        return None
    return match[1].lower()


class JsonPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = None
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if tag in ("title", "h1", "h2"):
            self.capture = {"tag": tag, "text": []}

    def handle_data(self, text):
        if self.capture is not None:
            self.capture["text"].append(text)

    def handle_endtag(self, tag):
        if self.capture is not None and tag == self.capture["tag"]:
            self.headings.append((tag, " ".join("".join(self.capture["text"]).split())))
            self.capture = None


def accepted_json(html, data, year, source, data_source):
    page = JsonPage()
    page.feed(html)
    page.close()
    expected = [("title", f"ACM CCS {year}"), ("h1", "Accepted Papers"),
                ("h2", "First Cycle"), ("h2", "Second Cycle")]
    if page.capture or any(page.headings.count(item) != 1 for item in expected):
        raise ValueError("CCS JSON page year or cycle headings changed")
    cycles = {"firstCycle": "first", "secondCycle": "second"}
    if not isinstance(data, dict) or set(data) != set(cycles):
        raise ValueError("Changed CCS JSON cycle schema")
    papers, titles, totals = [], set(), {}
    for key, cycle in cycles.items():
        rows = data[key]
        if not isinstance(rows, list) or not rows:
            raise ValueError("Empty CCS JSON cycle")
        totals[cycle] = len(rows)
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("title"), str):
                raise ValueError("Missing CCS JSON title")
            title = re.sub(r"^\(#\d+\)\s+", "", row["title"]).strip()
            if not title or normalize(title) in titles:
                raise ValueError("Empty or duplicate CCS JSON title")
            titles.add(normalize(title))
            authors = row.get("authors")
            if not isinstance(authors, list) or not authors or any(
                    not isinstance(a, dict) or not isinstance(a.get("name"), str)
                    or not a["name"].strip() for a in authors):
                raise ValueError("Missing CCS JSON authors")
            if "fuzz" not in title.casefold():
                continue
            doi = doi_from_url(row.get("url"))
            if not doi:
                raise ValueError("Missing or unexpected official ACM DOI link")
            papers.append({"title": title, "authors": [a["name"].strip() for a in authors],
                           "cycle": cycle, "source": source, "data_source": data_source,
                           "official_url": row["url"], "official_doi": doi})
    if not papers:
        raise ValueError("No fuzz title candidates in CCS JSON")
    dois = [p["official_doi"] for p in papers]
    if len(dois) != len(set(dois)):
        raise ValueError("Duplicate official CCS DOI")
    return papers, totals


def match_record(paper, record, year):
    reasons = []
    if not any(normalize(t) == normalize(paper["title"]) for t in record.get("title", [])):
        reasons.append("title mismatch")
    venues = {normalize(f"Proceedings of the {year} ACM SIGSAC Conference on Computer and Communications Security")}
    if not any(normalize(v) in venues for v in record.get("container-title", [])):
        reasons.append("not the requested CCS main proceedings")
    date = record.get("published", {}).get("date-parts", [[]])
    if not date or not date[0] or date[0][0] != year:
        reasons.append("publication year mismatch")
    if record.get("type") != "proceedings-article" or record.get("publisher") not in {"ACM", "Association for Computing Machinery", "Association for Computing Machinery (ACM)"}:
        reasons.append("not an ACM proceedings article")
    expected = Counter(author_key(a) for a in paper["authors"])
    actual = Counter(author_key(a.get("given", "") + " " + a.get("family", ""))
                     for a in record.get("author", []))
    if not expected or actual != expected:
        reasons.append("author list mismatch")
    try:
        doi_url(record.get("DOI"))
    except ValueError:
        reasons.append("missing or invalid ACM DOI")
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
            "User-Agent": "awesome-fuzzing-ccs/1.0 (https://github.com/cpuu/awesome-fuzzing)",
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
    if year == 2025:
        source = "https://www.sigsac.org/ccs/CCS2025/accepted-papers/"
        data_source = "https://www.sigsac.org/ccs/CCS2025/assets/accepted-papers.json"
        papers, totals = accepted_json(fetch(source, "text/html"),
                                      json.loads(fetch(data_source, "application/json")),
                                      year, source, data_source)
    else:
        source = f"https://www.sigsac.org/ccs/CCS{year}/program/accepted-papers.html"
        papers, totals = accepted(fetch(source, "text/html"), year, source)
    results = []
    for paper in papers:
        # Fuzzy matching in cryptography is not sufficient evidence of fuzz testing.
        if "fuzz" not in re.sub(r"\bfuzzy\b", "", paper["title"], flags=re.I).casefold():
            results.append({**paper, "status": "pending_scope",
                            "reason": "Keyword occurs only in Fuzzy; maintainer scope review required"})
            continue
        if paper.get("official_doi"):
            doi = paper["official_doi"]
            try:
                record = lookup(doi)
            except HTTPError as error:
                if error.code != 404:
                    raise
                results.append({**paper, "status": "pending_doi",
                                "reason": "Official DOI not found in Crossref"})
                continue
            result = resolve(paper, [record], year, lambda _: record)
            if result.get("doi", doi) != doi:
                result = {**paper, "status": "pending_doi",
                          "reason": "Official DOI and returned metadata DOI disagree"}
            results.append(result)
            time.sleep(0.2)
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
        raise ValueError("CCS section missing or ambiguous")
    start = readme.index(HEADING) + len(HEADING)
    following = re.search(r"^###? ", readme[start:], re.M)
    if not following:
        raise ValueError("Cannot locate end of CCS section")
    end = start + following.start()
    section = readme[start:end]
    pattern = rf"<details><summary>{year} \((\d+) papers\)</summary>\n(.*?)</details>"
    blocks = list(re.finditer(pattern, section, re.S))
    if len(blocks) > 1 or (f"<summary>{year}" in section and not blocks):
        raise ValueError("Unexpected or duplicate CCS year block")
    existing = []
    if blocks:
        for line in blocks[0][2].splitlines():
            if not line.strip():
                continue
            entry = re.fullmatch(r"- \[((?:\\.|[^\]])+), (\d{4})\]\(([^\s]+)\)", line)
            if not entry or int(entry[2]) != year:
                raise ValueError("Custom CCS year content; review manually")
            title = re.sub(r"\\(.)", r"\1", entry[1])
            existing.append({"line": line, "title": normalize(title), "url": entry[3]})
        if len(existing) != int(blocks[0][1]):
            raise ValueError("Incorrect existing CCS paper count")
        if len({p['title'] for p in existing}) != len(existing):
            raise ValueError("Duplicate existing CCS title")
    additions, warnings, matched = [], [], set()
    for paper in sorted(papers, key=lambda p: normalize(p["title"])):
        candidate_doi = paper.get("official_doi") or paper.get("doi")
        same = [p for p in existing if p["title"] == normalize(paper["title"])
                or (paper.get("url") and p["url"].casefold() == paper["url"].casefold())
                or (candidate_doi and doi_from_url(p["url"]) == candidate_doi)]
        if len(same) > 1:
            raise ValueError("Multiple existing entries match one CCS candidate")
        if same:
            matched.add(same[0]["line"])
            if paper.get("url") != same[0]["url"]:
                warnings.append(f"Preserved existing entry/link: {paper['title']}")
            continue
        if paper["status"] == "verified":
            url = doi_url(paper["doi"])
            additions.append(f"- [{markdown_title(paper['title'])}, {year}]({url})")
    if len(matched) != len(existing):
        raise ValueError("Existing CCS entries missing from source; no automatic deletion")
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
    body = ["<!-- awesome-fuzzing-ccs -->", f"ACM CCS {args.year} DOI-only candidates.",
            f"Source: {source}", f"Summary: {summary}",
            f"Published cycles (accepted paper totals): {totals}",
            "Only verified DOI records are proposed. Pending candidates are not added.",
            "Review scope and bibliographic matches before merging. No automatic merge.", ""]
    if "second" not in totals:
        body.append("Second Cycle is not published as an active table; HTML comments are excluded.")
    if not additions:
        body.append("No new entries: README is unchanged and no new proposal PR is needed.")
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
