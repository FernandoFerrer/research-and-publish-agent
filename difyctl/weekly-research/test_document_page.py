import unittest

from document_page import parse_document_page


class DocumentPageTests(unittest.TestCase):
    def test_extracts_identity_and_next_page(self):
        page = {"page": 1, "has_more": True, "data": [{"id": "abc", "doc_metadata": [
            {"name": "source_url", "value": "https://example.org/paper"},
            {"name": "doi", "value": "10.1234/example"},
        ]}]}
        result = parse_document_page(page, 1)
        self.assertEqual(result["next_page"], 2)
        self.assertEqual(result["sources"][0]["doi"], "10.1234/example")

    def test_empty_last_page_is_valid(self):
        self.assertIsNone(parse_document_page({"page": 2, "has_more": False, "data": []}, 2)["next_page"])

    def test_missing_identity_or_wrong_page_fails_closed(self):
        invalid = {"page": 1, "has_more": False, "data": [{"id": "abc", "doc_metadata": []}]}
        with self.assertRaises(ValueError):
            parse_document_page(invalid, 1)
        with self.assertRaises(ValueError):
            parse_document_page({"page": 1, "has_more": False, "data": []}, 2)


if __name__ == "__main__":
    unittest.main()
