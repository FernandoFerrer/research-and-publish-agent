import unittest

from evidence_gate import validate_claim


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.retrieved = [
            {"document_id": "a", "source_url": "https://www.nature.com/articles/a", "content": "Trial A measured a result."},
            {"document_id": "b", "source_url": "https://www.science.org/doi/b", "content": "Trial B measured a similar result."},
        ]
        self.claim = {"text": "Two trials measured similar results.", "evidence": [
            {"document_id": "a", "quote": "Trial A measured a result.", "origin_id": "trial-a", "supports": True},
            {"document_id": "b", "quote": "Trial B measured a similar result.", "origin_id": "trial-b", "supports": True},
        ]}

    def test_independent_retrieved_evidence_passes(self):
        self.assertTrue(validate_claim(self.claim, self.retrieved)["accepted"])

    def test_two_reports_of_one_study_are_rejected(self):
        self.claim["evidence"][1]["origin_id"] = "trial-a"
        self.assertFalse(validate_claim(self.claim, self.retrieved)["accepted"])
        self.claim["evidence"][0]["origin_id"] = "doi:10.1234/ABC"
        self.claim["evidence"][1]["origin_id"] = "https://doi.org/10.1234/abc"
        self.assertFalse(validate_claim(self.claim, self.retrieved)["accepted"])

    def test_invented_quote_or_work_is_rejected(self):
        self.claim["evidence"][1]["quote"] = "A different invented finding"
        self.assertFalse(validate_claim(self.claim, self.retrieved)["accepted"])
        self.claim["evidence"][1]["quote"] = "Trial B measured a similar result."
        self.claim["evidence"][1]["origin_id"] = ""
        self.assertFalse(validate_claim(self.claim, self.retrieved)["accepted"])

    def test_contradiction_and_lookalike_domain_are_rejected(self):
        self.claim["evidence"][1]["supports"] = False
        self.claim["evidence"][1]["origin_id"] = ""
        self.assertEqual(validate_claim(self.claim, self.retrieved)["reason"], "contradiction")
        self.claim["evidence"][1]["supports"] = True
        self.claim["evidence"][1]["origin_id"] = "trial-b"
        self.retrieved[1]["source_url"] = "https://science.org.evil.example/article"
        self.assertFalse(validate_claim(self.claim, self.retrieved)["accepted"])


if __name__ == "__main__":
    unittest.main()
