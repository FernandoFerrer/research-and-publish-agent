import unittest
import json

from source_metadata import check_source, validate_metadata


class SourceMetadataTests(unittest.TestCase):
    def setUp(self):
        self.selected = {"source_url": "https://example.org/a", "topic": "science", "role": "main"}
        self.text = "Public Report\nPublished November 3, 2026\nDOI: 10.1234/test\nBody"
        self.proposed = {"source_title": "Public Report", "publication_date": "2026-11-03",
                         "publication_quote": "Published November 3, 2026", "doi": "10.1234/test"}

    def test_metadata_is_grounded_in_fetched_source(self):
        result = validate_metadata(self.selected, self.text, self.proposed, "2026-11-08", 7, "2026-11-09")
        self.assertEqual(result["publication_date"], "2026-11-03")
        self.assertEqual(result["doi"], "10.1234/test")

    def test_invented_date_and_old_main_story_are_rejected(self):
        self.proposed["publication_date"] = "2026-11-04"
        with self.assertRaises(ValueError):
            validate_metadata(self.selected, self.text, self.proposed, "2026-11-08", 7, "2026-11-09")
        self.proposed["publication_date"] = "2026-11-03"
        with self.assertRaises(ValueError):
            validate_metadata(self.selected, self.text, self.proposed, "2026-11-08", 3, "2026-11-09")

    def test_missing_date_is_allowed_for_support_only(self):
        self.proposed["publication_date"] = None
        with self.assertRaises(ValueError):
            validate_metadata(self.selected, self.text, self.proposed, "2026-11-08", 7, "2026-11-09")
        self.selected["role"] = "support"
        self.assertIsNone(validate_metadata(self.selected, self.text, self.proposed, "2026-11-08", 7, "2026-11-09")["publication_date"])

    def test_bad_metadata_is_rejected_without_stopping_other_sources(self):
        result = check_source(self.selected, self.text, json.dumps(self.proposed), "2026-11-08", 7, "2026-11-09")
        self.assertEqual(result["status"], "accepted")
        self.proposed["publication_date"] = None
        result = check_source(self.selected, self.text, json.dumps(self.proposed), "2026-11-08", 7, "2026-11-09")
        self.assertEqual(result["status"], "rejected")
        self.assertNotIn("text", result)
        self.assertEqual(check_source(self.selected, self.text, "invalid JSON", "2026-11-08", 7, "2026-11-09")["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
