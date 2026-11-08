import unittest

from retrieval_adapter import DATASET_ID, adapt_retrieval


class RetrievalAdapterTests(unittest.TestCase):
    def test_preserves_source_metadata_with_its_chunk(self):
        source = {"metadata": {"dataset_id": DATASET_ID, "document_id": "doc1", "doc_metadata": {
            "source_title": "A public source", "source_url": "https://www.nasa.gov/example",
            "publication_date": "2026-11-01", "retrieval_date": "2026-11-08", "topic": "astronomy"}},
            "content": "Evidence text."}
        result = adapt_retrieval([source])
        self.assertEqual(result[0]["source_url"], "https://www.nasa.gov/example")
        self.assertEqual(result[0]["content"], "Evidence text.")
        self.assertEqual(result[0]["publication_date"], "2026-11-01")

    def test_rejects_missing_metadata_and_wrong_dataset(self):
        for metadata in ({"dataset_id": DATASET_ID, "document_id": "doc1"},
                         {"dataset_id": "other", "document_id": "doc1", "doc_metadata": {}}):
            with self.assertRaises(ValueError):
                adapt_retrieval([{"metadata": metadata, "content": "Evidence"}])


if __name__ == "__main__":
    unittest.main()
