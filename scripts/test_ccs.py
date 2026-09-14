import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import ccs


def row(title, authors="Alice Smith (Fuzz University)<br />Bob Jones (Example (Branch))"):
    return f"<tr><td>{title}</td><td>{authors}</td></tr>"


def table(title):
    return ('<table class="accepted-papers-table"><tr><th>Title</th><th>Author</th></tr>'
            + row(title) + "</table>")


def page(first="TestFuzz", second=None):
    html = ('<title>ACM CCS 2026</title><h2>ACCEPTED PAPERS</h2>'
            '<h3>First Cycle</h3>' + table(first))
    if second is not None:
        html += "<h3>Second Cycle</h3>" + table(second)
    return html + '<h2>About ACM CCS</h2>'


def paper(title="TestFuzz"):
    return {"title": title, "authors": ["Alice Smith", "Bob Jones"], "cycle": "first"}


def record():
    return {"title": ["TestFuzz"], "DOI": "10.1145/9999999.0000001",
            "container-title": ["Proceedings of the 2026 ACM SIGSAC Conference on Computer and Communications Security"],
            "published": {"date-parts": [[2026, 5, 18]]},
            "type": "proceedings-article", "publisher": "Association for Computing Machinery",
            "author": [{"given": "Alice", "family": "Smith"},
                       {"given": "Bob", "family": "Jones"}]}


def verified():
    doi = record()["DOI"].lower()
    return {**paper(), "status": "verified", "doi": doi, "url": ccs.doi_url(doi)}


def readme(block=""):
    return ("Research conferences (2008-2025).\n\n### NDSS\n\nUnchanged.\n\n"
            + ccs.HEADING + "\n\n" + block + "### USENIX Security\n\nUnchanged.\n")


def year_block(year, title="Old", url="https://example.org/paper.pdf"):
    return (f'<details><summary>{year} (1 papers)</summary>\n\n'
            f'- [{title}, {year}]({url})\n\n</details>\n\n')


class AcceptedTests(unittest.TestCase):
    def test_first_cycle_only_and_comments_excluded(self):
        html = page("TestFuzz &amp; <em>More</em>")
        html += "<!-- <h3>Second Cycle</h3>" + table("OldFuzz") + " -->"
        papers, totals = ccs.accepted(html, 2026, "https://example.org/")
        self.assertEqual(totals, {"first": 1})
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["title"], "TestFuzz & More")
        self.assertEqual(papers[0]["authors"], ["Alice Smith", "Bob Jones"])
        self.assertEqual(papers[0]["source"], "https://example.org/")

    def test_second_cycle_and_title_only_selection(self):
        papers, totals = ccs.accepted(page("TestFuzz", "Other Paper"), 2026, "https://example.org/")
        self.assertEqual(totals, {"first": 1, "second": 1})
        self.assertEqual(len(papers), 1)
        papers, _ = ccs.accepted(page("TestFuzz", "AnotherFuzz"), 2026, "https://example.org/")
        self.assertEqual(papers[1]["cycle"], "second")

    def test_parenthesized_name_and_affiliation(self):
        html = page().replace("Alice Smith (Fuzz University)", "Dave (Jing) Tian (University (Branch))")
        papers, _ = ccs.accepted(html, 2026, "https://example.org/")
        self.assertEqual(papers[0]["authors"][0], "Dave (Jing) Tian")

    def test_rejects_changed_or_incomplete_source(self):
        variants = [
            page().replace("First Cycle", "Third Cycle"),
            page().replace("CCS 2026", "CCS 2025"),
            page().replace("</table>", ""),
            page("TestFuzz", "TestFuzz"),
            page().replace(row("TestFuzz"), ""),
            page().replace("Alice Smith (Fuzz University)<br />Bob Jones (Example (Branch))", ""),
            page().replace("Title</th>", "Paper</th>"),
            page().replace("First Cycle</h3>", "First Cycle</h3><h3>First Cycle</h3>"),
            page().replace("</table>", "</table>" + table("AnotherFuzz")),
            page().replace("<td>TestFuzz</td>", "<td>TestFuzz"),
            page("Nothing"),
        ]
        for html in variants:
            with self.subTest(html=html), self.assertRaises(ValueError):
                ccs.accepted(html, 2026, "https://example.org/")

    @patch("ccs.time.sleep")
    @patch("ccs.lookup", return_value=record())
    @patch("ccs.crossref_message", return_value={"items": [record()]})
    @patch("ccs.fetch", return_value=page("TestFuzz", "Fuzzy PSI"))
    def test_fuzzy_only_requires_scope_review(self, fetch, search, lookup, sleep):
        _, _, papers = ccs.collect(2026)
        self.assertEqual([p["status"] for p in papers], ["verified", "pending_scope"])
        search.assert_called_once()

    @patch("ccs.time.sleep")
    @patch("ccs.crossref_message", return_value={"items": []})
    @patch("ccs.fetch", return_value=page())
    def test_unregistered_doi_is_pending(self, fetch, search, sleep):
        _, _, papers = ccs.collect(2026)
        self.assertEqual(papers[0]["status"], "pending_doi")
        self.assertNotIn("url", papers[0])


class MetadataTests(unittest.TestCase):
    def test_acm_short_publisher_name(self):
        self.assertEqual(ccs.match_record(paper(), {**record(), "publisher": "ACM"}, 2026), [])

    def test_case_punctuation_and_middle_initial(self):
        candidate = paper("TEST-FUZZ")
        metadata = record()
        metadata["author"][0]["given"] = "Alice C."
        self.assertEqual(ccs.match_record(candidate, metadata, 2026), [])
        result = ccs.resolve(candidate, [metadata], 2026, lambda doi: metadata)
        self.assertEqual(result["url"], "https://doi.org/10.1145/9999999.0000001")

    def test_wrong_bibliography_is_not_accepted(self):
        changes = {"title": ["Unrelated"], "container-title": ["Proceedings of the 2026 ACM Workshop on Security"],
                   "published": {"date-parts": [[2025]]}, "type": "journal-article",
                   "publisher": "Other", "author": [{"given": "Alice", "family": "Wrong"}],
                   "DOI": "10.1234/not-acm"}
        for field, value in changes.items():
            with self.subTest(field=field):
                metadata = {**record(), field: value}
                self.assertTrue(ccs.match_record(paper(), metadata, 2026))

    def test_no_match_or_ambiguity_is_pending(self):
        other = {**record(), "DOI": "10.1145/9999999.0000002"}
        for records in ([], [{**record(), "title": ["Unrelated"]}], [record(), other]):
            with self.subTest(records=records):
                with patch("ccs.lookup") as lookup:
                    self.assertEqual(ccs.resolve(paper(), records, 2026, lookup)["status"], "pending_doi")
                    lookup.assert_not_called()

    def test_direct_doi_lookup_must_agree(self):
        metadata = {**record(), "DOI": "10.1145/9999999.9999999"}
        self.assertEqual(ccs.resolve(paper(), [record()], 2026, lambda doi: metadata)["status"], "pending_doi")
        metadata = {**record(), "title": ["Other"]}
        self.assertEqual(ccs.resolve(paper(), [record()], 2026, lambda doi: metadata)["status"], "pending_doi")

    def test_duplicate_search_results_same_doi_are_not_ambiguous(self):
        self.assertEqual(ccs.resolve(paper(), [record(), copy.deepcopy(record())], 2026,
                                    lambda doi: record())["status"], "verified")


class ProposalTests(unittest.TestCase):
    def test_only_verified_dois_added_and_idempotent(self):
        original = readme(year_block(2025))
        papers = [verified(), {**paper("Fuzzy PSI"), "status": "pending_scope"}]
        updated, additions, _ = ccs.propose(original, papers, 2026)
        self.assertEqual(len(additions), 1)
        self.assertIn("2026 (1 papers)", updated)
        self.assertIn(verified()["url"], updated)
        self.assertNotIn("Fuzzy PSI", updated)
        self.assertIn(year_block(2025), updated)
        self.assertTrue(updated.endswith("### USENIX Security\n\nUnchanged.\n"))
        self.assertIn("### NDSS\n\nUnchanged.", updated)
        self.assertEqual(ccs.propose(updated, papers, 2026)[:2], (updated, []))

    def test_preserves_existing_pdf_and_pending_entry(self):
        original = readme(year_block(2026, "TestFuzz"))
        for candidate in (verified(), {**paper(), "status": "pending_doi"}):
            updated, additions, warnings = ccs.propose(original, [candidate], 2026)
            self.assertEqual(updated, original)
            self.assertEqual(additions, [])
            self.assertTrue(warnings)

    def test_no_verified_candidates_leaves_readme_untouched(self):
        original = readme()
        self.assertEqual(ccs.propose(original, [{**paper(), "status": "pending_doi"}], 2026)[0], original)

    def test_rejects_missing_existing_or_bad_count(self):
        for block in (year_block(2026, "MissingFuzz"),
                      year_block(2026, "TestFuzz").replace("1 papers", "2 papers"),
                      year_block(2026, "TestFuzz") * 2):
            with self.subTest(block=block), self.assertRaises(ValueError):
                ccs.propose(readme(block), [verified()], 2026)

    def test_backfill_preserves_descending_years(self):
        original = readme(year_block(2027) + year_block(2025))
        updated, _, _ = ccs.propose(original, [verified()], 2026)
        self.assertLess(updated.index("2027 ("), updated.index("2026 ("))
        self.assertLess(updated.index("2026 ("), updated.index("2025 ("))

    def test_markdown_title_escaping(self):
        candidate = {**verified(), "title": "TestFuzz: [A] & <B>"}
        updated, _, _ = ccs.propose(readme(), [candidate], 2026)
        self.assertIn(r"\[A\] &amp; &lt;B&gt;", updated)
        self.assertEqual(ccs.propose(updated, [candidate], 2026)[0], updated)

    def test_cli_preview_write_and_failure_safety(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            original = readme()
            path.write_text(original)
            argv = ["ccs.py", "--readme", str(path), "--output-dir", str(root / "preview")]
            collected = ("https://example.org/", {"first": 1, "second": 1}, [verified()])
            with patch("sys.argv", argv), patch("ccs.collect", return_value=collected):
                ccs.main()
            self.assertEqual(path.read_text(), original)
            report = json.loads((root / "preview/candidates.json").read_text())
            self.assertEqual(report["additions"], 1)
            with patch("sys.argv", argv + ["--write"]), patch("ccs.collect", side_effect=TimeoutError):
                with self.assertRaises(TimeoutError):
                    ccs.main()
            self.assertEqual(path.read_text(), original)
            with patch("sys.argv", argv + ["--write"]), patch("ccs.collect", return_value=collected):
                ccs.main()
            self.assertIn(verified()["url"], path.read_text())


class OfficialLinkTests(unittest.TestCase):
    def test_2026_title_link_is_used_without_search(self):
        url = "https://dl.acm.org/doi/" + record()["DOI"]
        html = page().replace("<td>TestFuzz</td>", f'<td><a href="{url}">TestFuzz</a></td>')
        with patch("ccs.fetch", return_value=html), patch("ccs.lookup", return_value=record()) as lookup, \
                patch("ccs.crossref_message") as search, patch("ccs.time.sleep"):
            _, _, papers = ccs.collect(2026)
        self.assertEqual(papers[0]["status"], "verified")
        lookup.assert_called_once_with(record()["DOI"].lower())
        search.assert_not_called()

    def test_untrusted_title_link_is_rejected(self):
        html = page().replace("<td>TestFuzz</td>", '<td><a href="https://example.org/doi/10.1145/1">TestFuzz</a></td>')
        with self.assertRaises(ValueError):
            ccs.accepted(html, 2026, "https://example.org/")

    def test_acm_url_identity(self):
        for prefix in ("https://dl.acm.org/doi/", "https://dl.acm.org/doi/pdf/", "https://doi.org/"):
            self.assertEqual(ccs.doi_from_url(prefix + "10.1145/1.2"), "10.1145/1.2")
        for url in ("https://dl.acm.org.evil/doi/10.1145/1.2", "http://dl.acm.org/doi/10.1145/1.2", "https://doi.org/10.1109/1"):
            self.assertIsNone(ccs.doi_from_url(url))

    def test_changed_title_with_same_official_doi_preserves_existing(self):
        url = "https://dl.acm.org/doi/" + record()["DOI"]
        original = readme(year_block(2026, "Old title", url))
        candidate = {**paper(), "status": "pending_doi", "official_doi": record()["DOI"].lower()}
        updated, additions, _ = ccs.propose(original, [candidate], 2026)
        self.assertEqual(updated, original)
        self.assertEqual(additions, [])

    def test_2025_json_cycles_and_number_prefix(self):
        html = '<title>ACM CCS 2025</title><h1>Accepted Papers</h1><h2>First Cycle</h2><h2>Second Cycle</h2>'
        data = {"firstCycle": [{"title": "(#56) TestFuzz", "authors": [{"name": "Alice Smith"}],
                                "url": "https://dl.acm.org/doi/10.1145/1.2"}],
                "secondCycle": [{"title": "Other paper", "authors": [{"name": "Bob Jones"}]}]}
        papers, totals = ccs.accepted_json(html, data, 2025, "source", "data")
        self.assertEqual(totals, {"first": 1, "second": 1})
        self.assertEqual(papers[0]["title"], "TestFuzz")
        self.assertEqual(papers[0]["official_doi"], "10.1145/1.2")
        for bad in ({"firstCycle": data["firstCycle"]}, {**data, "secondCycle": []}):
            with self.assertRaises(ValueError):
                ccs.accepted_json(html, bad, 2025, "source", "data")


if __name__ == "__main__":
    unittest.main()
