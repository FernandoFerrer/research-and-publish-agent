import unittest

from ingestion_payload import DATASET_FIELDS, document_payload, metadata_payload


class IngestionPayloadTests(unittest.TestCase):
    def setUp(self):
        self.source = {"source_title": "Public paper", "source_url": "https://EXAMPLE.org/paper?utm_source=x",
                       "publication_date": None, "retrieval_date": "2026-11-08", "topic": "science",
                       "doi": None, "text": "Research material with \"quoted\" text."}
        self.definitions = {name: "id-" + name for name in DATASET_FIELDS}

    def test_configuration_and_metadata_do_not_invent_missing_fields(self):
        payload = document_payload(self.source)
        self.assertTrue(payload["name"].startswith("source-"))
        self.assertEqual(len(payload["name"]), len("source-") + 64)
        self.assertEqual(payload["process_rule"]["rules"]["segmentation"]["chunk_overlap"], 50)
        meta = metadata_payload("doc", self.source, self.definitions)["operation_data"][0]["metadata_list"]
        self.assertNotIn("publication_date", {item["name"] for item in meta})
        self.assertNotIn("doi", {item["name"] for item in meta})

    def test_rejects_invalid_date_and_missing_metadata_field(self):
        self.source["publication_date"] = "2026-11-09"
        with self.assertRaises(ValueError):
            document_payload(self.source)
        self.source["publication_date"] = None
        del self.definitions["source_url"]
        with self.assertRaises(ValueError):
            metadata_payload("doc", self.source, self.definitions)


if __name__ == "__main__":
    unittest.main()
