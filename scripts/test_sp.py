import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sp


def card(title, anchor=1):
    return (f'<div class="list-group-item"><b><a data-toggle="collapse" '
            f'href="#collapse-{anchor}">{title}<span></span></a></b><br />'
            '<div class="collapse authorlist">Alice Smith<sup>1</sup>, '
            'Bob Jones<sup>2</sup><br /><sup>1</sup>: Fuzz University</div></div>')


def page(first="TestFuzz", second="Other Paper"):
    return ('<title>IEEE Symposium on Security and Privacy 2026</title>'
            f'<div id="cycle1">{card(first)}</div>'
            f'<div id="cycle2">{card(second, 2)}</div>'
            + card("OldFuzz", 3))


def paper(title="TestFuzz"):
    return {"title": title, "authors": ["Alice Smith", "Bob Jones"], "cycle": "cycle1"}


def record():
    return {"title": ["TestFuzz"], "DOI": "10.1109/SP63933.2026.00001",
            "container-title": ["2026 IEEE Symposium on Security and Privacy (SP)"],
            "published": {"date-parts": [[2026, 5, 18]]},
            "type": "proceedings-article", "publisher": "IEEE",
            "author": [{"given": "Alice", "family": "Smith"},
                       {"given": "Bob", "family": "Jones"}]}


def verified():
    doi = record()["DOI"].lower()
    return {**paper(), "status": "verified", "doi": doi, "url": sp.doi_url(doi)}


def readme(block=""):
    return ("Research conferences (2008-2025).\n\n### NDSS\n\nUnchanged.\n\n"
            + sp.HEADING + "\n\n" + block + "### USENIX Security\n\nUnchanged.\n")


def year_block(year, title="Old", url="https://example.org/paper.pdf"):
    return (f'<details><summary>{year} (1 papers)</summary>\n\n'
            f'- [{title}, {year}]({url})\n\n</details>\n\n')


class AcceptedTests(unittest.TestCase):
    def test_cycles_authors_entities_and_title_only(self):
        papers, totals = sp.accepted(page("TestFuzz &amp; <em>More</em>"), 2026, "https://example.org/")
        self.assertEqual(totals, {"cycle1": 1, "cycle2": 1})
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["title"], "TestFuzz & More")
        self.assertEqual(papers[0]["authors"], ["Alice Smith", "Bob Jones"])
        self.assertEqual(papers[0]["source"], "https://example.org/#collapse-1")

    def test_rejects_changed_or_incomplete_source(self):
        variants = [page().replace('id="cycle2"', 'id="unknown"'),
                    page().replace("Privacy 2026", "Privacy 2025"),
                    page()[:-6], page("TestFuzz", "TestFuzz"),
                    page().replace("#collapse-2", "#collapse-1"),
                    page().replace(card("Other Paper", 2), ""),
                    page().replace("Alice Smith<sup>1</sup>, Bob Jones<sup>2</sup>", ""),
                    page("Nothing", "Other Paper")]
        for html in variants:
            with self.subTest(html=html), self.assertRaises(ValueError):
                sp.accepted(html, 2026, "https://example.org/")

    @patch("sp.time.sleep")
    @patch("sp.lookup", return_value=record())
    @patch("sp.crossref_message", return_value={"items": [record()]})
    @patch("sp.fetch", return_value=page("TestFuzz", "Fuzzy PSI"))
    def test_fuzzy_only_requires_scope_review(self, fetch, search, lookup, sleep):
        _, _, papers = sp.collect(2026)
        self.assertEqual([p["status"] for p in papers], ["verified", "pending_scope"])
        search.assert_called_once()


class MetadataTests(unittest.TestCase):
    def test_case_punctuation_and_middle_initial(self):
        candidate = paper("TEST-FUZZ")
        metadata = record()
        metadata["author"][0]["given"] = "Alice C."
        self.assertEqual(sp.match_record(candidate, metadata, 2026), [])
        result = sp.resolve(candidate, [metadata], 2026, lambda doi: metadata)
        self.assertEqual(result["url"], "https://doi.org/10.1109/sp63933.2026.00001")

    def test_wrong_bibliography_is_not_accepted(self):
        changes = {"title": ["Unrelated"], "container-title": ["2026 IEEE Security and Privacy Workshops"],
                   "published": {"date-parts": [[2025]]}, "type": "journal-article",
                   "publisher": "Other", "author": [{"given": "Alice", "family": "Wrong"}],
                   "DOI": "10.1234/not-ieee"}
        for field, value in changes.items():
            with self.subTest(field=field):
                metadata = {**record(), field: value}
                self.assertTrue(sp.match_record(paper(), metadata, 2026))

    def test_no_match_or_ambiguity_is_pending(self):
        other = {**record(), "DOI": "10.1109/sp63933.2026.00002"}
        for records in ([], [{**record(), "title": ["Unrelated"]}], [record(), other]):
            with self.subTest(records=records):
                with patch("sp.lookup") as lookup:
                    self.assertEqual(sp.resolve(paper(), records, 2026, lookup)["status"], "pending_doi")
                    lookup.assert_not_called()

    def test_direct_doi_lookup_must_agree(self):
        metadata = {**record(), "DOI": "10.1109/sp63933.2026.99999"}
        self.assertEqual(sp.resolve(paper(), [record()], 2026, lambda doi: metadata)["status"], "pending_doi")
        metadata = {**record(), "title": ["Other"]}
        self.assertEqual(sp.resolve(paper(), [record()], 2026, lambda doi: metadata)["status"], "pending_doi")

    def test_duplicate_search_results_same_doi_are_not_ambiguous(self):
        self.assertEqual(sp.resolve(paper(), [record(), copy.deepcopy(record())], 2026,
                                    lambda doi: record())["status"], "verified")


class ProposalTests(unittest.TestCase):
    def test_only_verified_dois_added_and_idempotent(self):
        original = readme(year_block(2025))
        papers = [verified(), {**paper("Fuzzy PSI"), "status": "pending_scope"}]
        updated, additions, _ = sp.propose(original, papers, 2026)
        self.assertEqual(len(additions), 1)
        self.assertIn("2026 (1 papers)", updated)
        self.assertIn(verified()["url"], updated)
        self.assertNotIn("Fuzzy PSI", updated)
        self.assertIn(year_block(2025), updated)
        self.assertTrue(updated.endswith("### USENIX Security\n\nUnchanged.\n"))
        self.assertIn("### NDSS\n\nUnchanged.", updated)
        self.assertEqual(sp.propose(updated, papers, 2026)[:2], (updated, []))

    def test_preserves_existing_pdf_and_pending_entry(self):
        original = readme(year_block(2026, "TestFuzz"))
        for candidate in (verified(), {**paper(), "status": "pending_doi"}):
            updated, additions, warnings = sp.propose(original, [candidate], 2026)
            self.assertEqual(updated, original)
            self.assertEqual(additions, [])
            self.assertTrue(warnings)

    def test_no_verified_candidates_leaves_readme_untouched(self):
        original = readme()
        self.assertEqual(sp.propose(original, [{**paper(), "status": "pending_doi"}], 2026)[0], original)

    def test_rejects_missing_existing_or_bad_count(self):
        for block in (year_block(2026, "MissingFuzz"),
                      year_block(2026, "TestFuzz").replace("1 papers", "2 papers"),
                      year_block(2026, "TestFuzz") * 2):
            with self.subTest(block=block), self.assertRaises(ValueError):
                sp.propose(readme(block), [verified()], 2026)

    def test_backfill_preserves_descending_years(self):
        original = readme(year_block(2027) + year_block(2025))
        updated, _, _ = sp.propose(original, [verified()], 2026)
        self.assertLess(updated.index("2027 ("), updated.index("2026 ("))
        self.assertLess(updated.index("2026 ("), updated.index("2025 ("))

    def test_markdown_title_escaping(self):
        candidate = {**verified(), "title": "TestFuzz: [A] & <B>"}
        updated, _, _ = sp.propose(readme(), [candidate], 2026)
        self.assertIn(r"\[A\] &amp; &lt;B&gt;", updated)
        self.assertEqual(sp.propose(updated, [candidate], 2026)[0], updated)

    def test_cli_preview_write_and_failure_safety(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            original = readme()
            path.write_text(original)
            argv = ["sp.py", "--readme", str(path), "--output-dir", str(root / "preview")]
            collected = ("https://example.org/", {"cycle1": 1, "cycle2": 1}, [verified()])
            with patch("sys.argv", argv), patch("sp.collect", return_value=collected):
                sp.main()
            self.assertEqual(path.read_text(), original)
            report = json.loads((root / "preview/candidates.json").read_text())
            self.assertEqual(report["additions"], 1)
            with patch("sys.argv", argv + ["--write"]), patch("sp.collect", side_effect=TimeoutError):
                with self.assertRaises(TimeoutError):
                    sp.main()
            self.assertEqual(path.read_text(), original)
            with patch("sys.argv", argv + ["--write"]), patch("sp.collect", return_value=collected):
                sp.main()
            self.assertIn(verified()["url"], path.read_text())


if __name__ == "__main__":
    unittest.main()
