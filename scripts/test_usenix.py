import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import usenix


def listing(cycle=1, title="TestFuzz", slug="test"):
    return (f'<h1 id="page-title">USENIX Security &#039;26 Cycle {cycle} Accepted Papers</h1>'
            f'<article class="node-paper view-mode-schedule"><h2><a href="/conference/usenixsecurity26/presentation/{slug}">'
            f'{title}</a></h2><p>Fuzz in abstract is ignored.</p></article>')


def detail(title="TestFuzz", pdf=True):
    return (f'<h1 id="page-title">{title}</h1>'
            '<meta name="citation_publication_date" content="2026">'
            '<meta name="citation_conference_title" content="35th USENIX Security Symposium (USENIX Security 26)">'
            + ('<meta name="citation_pdf_url" content="https://www.usenix.org/system/files/paper.pdf">' if pdf else '')
            + '<a href="https://www.usenix.org/system/files/slides.pdf">Slides</a>')


SOURCE = "https://www.usenix.org/conference/usenixsecurity26/cycle1-accepted-papers"
README = "### NDSS\n\nUnchanged.\n\n" + usenix.HEADING + "\n\n### ACM CCS\n\nUnchanged.\n"


class UsenixTests(unittest.TestCase):
    def test_fuzzy_only_is_reported_without_addition(self):
        error = HTTPError(SOURCE, 404, "Missing", {}, None)
        with patch("usenix.fetch", side_effect=[listing(title="Fuzzy PSI"), error]) as fetch:
            _, papers = usenix.collect(2026)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(papers[0]["status"], "pending_scope")
        self.assertEqual(usenix.propose(README, papers, 2026)[:2], (README, []))

    def test_title_only_matching(self):
        papers, total = usenix.accepted(listing(), 2026, 1, SOURCE)
        self.assertEqual(total, 1)
        self.assertEqual(papers[0]["title"], "TestFuzz")
        self.assertEqual(usenix.accepted(listing(title="Other"), 2026, 1, SOURCE)[0], [])

    def test_bad_sources_fail(self):
        for html in (listing(2), listing().replace("&#039;26", "&#039;25"),
                     listing().replace("security26/presentation", "security25/presentation"),
                     listing().replace("</article>", ""), listing() + listing()):
            with self.subTest(html=html), self.assertRaises(ValueError):
                usenix.accepted(html, 2026, 1, SOURCE)

    def test_citation_pdf_not_slides_and_fallback(self):
        paper = usenix.accepted(listing(), 2026, 1, SOURCE)[0][0]
        self.assertEqual(usenix.detail(detail(), paper, 2026)["url"], "https://www.usenix.org/system/files/paper.pdf")
        self.assertEqual(usenix.detail(detail(pdf=False), paper, 2026)["url"], paper["page"])
        for html in (detail("Wrong"), detail().replace('content="2026"', 'content="2025"'),
                     detail().replace("www.usenix.org/system", "evil.example/system")):
            with self.assertRaises(ValueError):
                usenix.detail(html, paper, 2026)

    def test_cycle2_404_is_unpublished(self):
        def fetch(url):
            if "cycle1-" in url:
                return listing()
            if "cycle2-" in url:
                raise HTTPError(url, 404, "Missing", {}, None)
            return detail()
        with patch("usenix.fetch", side_effect=fetch):
            sources, papers = usenix.collect(2026)
        self.assertEqual(sources["2"]["status"], "unpublished")
        self.assertEqual(len(papers), 1)

    def test_other_errors_are_not_unpublished(self):
        errors = [HTTPError(SOURCE, code, "Error", {}, None) for code in (403, 429, 500)]
        errors.append(URLError("connection failed"))
        for error in errors:
            with patch("usenix.fetch", side_effect=[listing(), error]), self.assertRaises(type(error)):
                usenix.collect(2026)
        with patch("usenix.fetch", side_effect=HTTPError(SOURCE, 404, "Missing", {}, None)), self.assertRaises(HTTPError):
            usenix.collect(2026)

    def test_cycle2_additions_and_idempotence(self):
        first = usenix.detail(detail(), usenix.accepted(listing(), 2026, 1, SOURCE)[0][0], 2026)
        original, additions, _ = usenix.propose(README, [first], 2026)
        second = {"title": "NextFuzz", "page": "https://www.usenix.org/conference/usenixsecurity26/presentation/next",
                  "url": "https://www.usenix.org/system/files/next.pdf", "pdf": "https://www.usenix.org/system/files/next.pdf", "cycle": "2"}
        updated, additions, _ = usenix.propose(original, [first, second], 2026)
        self.assertEqual(len(additions), 1)
        self.assertIn("2026 (2 papers)", updated)
        self.assertIn("### ACM CCS\n\nUnchanged.", updated)
        self.assertEqual(usenix.propose(updated, [first, second], 2026)[:2], (updated, []))
        with self.assertRaises(ValueError):
            usenix.propose(updated, [first], 2026)

    def test_duplicate_between_cycles_is_not_added_twice(self):
        with patch("usenix.fetch", side_effect=[listing(), listing(2), detail()]):
            _, papers = usenix.collect(2026)
        self.assertEqual(len(papers), 1)
        with patch("usenix.fetch", side_effect=[listing(), listing(2, slug="different")]), self.assertRaises(ValueError):
            usenix.collect(2026)

    def test_existing_page_link_is_preserved_when_pdf_appears(self):
        paper = usenix.accepted(listing(), 2026, 1, SOURCE)[0][0]
        old = usenix.detail(detail(pdf=False), paper, 2026)
        original, _, _ = usenix.propose(README, [old], 2026)
        new = usenix.detail(detail(), paper, 2026)
        updated, additions, warnings = usenix.propose(original, [new], 2026)
        self.assertEqual(updated, original)
        self.assertEqual(additions, [])
        self.assertTrue(warnings)


if __name__ == "__main__":
    unittest.main()
