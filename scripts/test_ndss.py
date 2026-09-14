import unittest

from ndss import HEADING, accepted, detail, propose

SOURCE = "https://www.ndss-symposium.org/ndss2026/accepted-papers/"
PAGE = 'https://www.ndss-symposium.org/ndss-paper/fuzz/'
HTML = '''<h1>NDSS Symposium 2026 Accepted Papers</h1>
<p>2 papers were accepted</p>
<h2 class="pt-cv-title"><a href="/ndss-paper/fuzz/">A <em>Fuzz</em> &amp; Test</a></h2>
<p>Fuzz Author</p><h2 class="pt-cv-title"><a href="/other/">Other Work</a></h2>'''
DETAIL = '''<h1>A Fuzz &amp; Test</h1>
<article class="category-ndss-2026 tag-summer-cycle-2026">
<a class="pdf-button" href="/wp-content/uploads/paper.pdf">Paper</a></article>'''
README = f'# Awesome Fuzzing\n\n{HEADING}\n\n<details><summary>2025 (1 papers)</summary>\n\n- [Old, 2025](https://example.org/old)\n\n</details>\n\n### Other Conference\n'


class NDSS(unittest.TestCase):
    def paper(self):
        return detail(DETAIL, accepted(HTML, 2026, SOURCE)[0], 2026)

    def test_title_only_entities_and_nested_markup(self):
        self.assertEqual(accepted(HTML, 2026, SOURCE), [{"title": "A Fuzz & Test", "page": PAGE}])

    def test_fail_closed_on_incomplete_or_changed_page(self):
        for html in (HTML.replace('2 papers', '3 papers'), HTML.replace('pt-cv-title', 'changed'),
                     HTML.replace('2026 Accepted', '2027 Accepted'), HTML.replace('/ndss-paper/fuzz/', 'https://evil.example/fuzz')):
            with self.assertRaises(ValueError):
                accepted(html, 2026, SOURCE)

    def test_cycle_pdf_and_missing_pdf_fallback(self):
        paper = self.paper()
        self.assertEqual(paper['cycle'], 'summer')
        self.assertTrue(paper['url'].endswith('/paper.pdf'))
        fallback = detail(DETAIL.replace('pdf-button', 'slides'), {"title": "A Fuzz & Test", "page": PAGE}, 2026)
        self.assertEqual(fallback['url'], PAGE)
        for html in (DETAIL.replace('summer-cycle', 'unknown-cycle'), DETAIL.replace('category-ndss-2026', 'category-ndss-2025')):
            with self.assertRaises(ValueError):
                detail(html, paper, 2026)

    def test_duplicate_candidates_are_rejected(self):
        html = HTML.replace('/other/', '/ndss-paper/fuzz/').replace('Other Work', 'Second Fuzzer')
        with self.assertRaises(ValueError):
            accepted(html, 2026, SOURCE)

    def test_append_updates_count(self):
        paper = self.paper()
        updated, _, _ = propose(README, [paper], 2026)
        another = {**paper, 'title': 'Second Fuzzer', 'page': PAGE + 'second/', 'url': PAGE + 'second/'}
        result, additions, _ = propose(updated, [paper, another], 2026)
        self.assertEqual(len(additions), 1)
        self.assertIn('2026 (2 papers)', result)
        self.assertEqual(propose(result, [paper, another], 2026)[0], result)

    def test_idempotent_insertion_and_preservation(self):
        updated, additions, _ = propose(README, [self.paper()], 2026)
        self.assertEqual(len(additions), 1)
        self.assertIn('2026 (1 papers)', updated)
        self.assertIn('2025 (1 papers)', updated)
        self.assertEqual(propose(updated, [self.paper()], 2026)[0], updated)
        self.assertEqual(updated[updated.index('### Other Conference'):], README[README.index('### Other Conference'):])

    def test_preserve_changed_links_and_abort_disappearing_entries(self):
        updated, _, _ = propose(README, [self.paper()], 2026)
        changed = {**self.paper(), 'url': PAGE}
        result, additions, warnings = propose(updated, [changed], 2026)
        self.assertEqual(result, updated)
        self.assertFalse(additions)
        self.assertTrue(warnings)
        with self.assertRaises(ValueError):
            propose(updated, [], 2026)

    def test_reject_wrong_count_and_custom_year_markup(self):
        updated, _, _ = propose(README, [self.paper()], 2026)
        for invalid in (updated.replace('2026 (1 papers)', '2026 (9 papers)'), updated.replace('2026 (1 papers)', '2026 papers')):
            with self.assertRaises(ValueError):
                propose(invalid, [self.paper()], 2026)


if __name__ == '__main__':
    unittest.main()
