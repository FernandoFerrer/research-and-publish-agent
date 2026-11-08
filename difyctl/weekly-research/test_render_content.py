import unittest

from render_content import render_content


class RenderContentTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"document_id": "a", "source_title": "Nature source", "source_url": "https://nature.com/a", "content": "Trial A reports a result."},
            {"document_id": "b", "source_title": "Science source", "source_url": "https://science.org/b", "content": "Trial B reports a similar result."},
        ]
        self.claims = [{"id": "c1", "text": "Two trials reported similar results.", "evidence": [
            {"document_id": "a", "quote": "Trial A reports a result.", "origin_id": "trial-a", "supports": True},
            {"document_id": "b", "quote": "Trial B reports a similar result.", "origin_id": "trial-b", "supports": True},
        ]}]

    def test_output_contains_exact_claim_and_real_citations(self):
        output = render_content(self.claims, self.rows, {"main": ["c1"], "highlights": [], "topic": "science"}, "2026-11-08")
        paragraph = output["main_article"]["paragraphs"][0]
        self.assertEqual(paragraph["text"], self.claims[0]["text"])
        self.assertEqual(set(paragraph["source_document_ids"]), {"a", "b"})
        self.assertEqual(output["sources"]["a"]["source_url"], "https://nature.com/a")

    def test_unsupported_claim_and_unknown_source_title_cannot_be_rendered(self):
        self.claims[0]["evidence"][1]["origin_id"] = "trial-a"
        with self.assertRaises(ValueError):
            render_content(self.claims, self.rows, {"main": ["c1"], "highlights": [], "topic": "science"}, "2026-11-08")
        self.claims[0]["evidence"][1]["origin_id"] = "trial-b"
        self.rows[1]["source_title"] = None
        with self.assertRaises(ValueError):
            render_content(self.claims, self.rows, {"main": ["c1"], "highlights": [], "topic": "science"}, "2026-11-08")


if __name__ == "__main__":
    unittest.main()
