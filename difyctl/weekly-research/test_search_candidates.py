import unittest

from search_candidates import normalize_results, select_candidates


class SearchCandidateTests(unittest.TestCase):
    def setUp(self):
        self.results = {topic: [] for topic in ("AI", "science", "healthcare", "astronomy", "technology")}
        self.results["science"] = [{"title": "Public report", "href": "https://example.org/p?utm_source=x", "body": "A snippet"}]

    def test_only_real_search_result_is_selected(self):
        candidates = normalize_results(self.results)
        scores = {"relevance": 5, "novelty": 4, "credibility": 4, "reader_interest": 4}
        selected = select_candidates(candidates, [{"source_url": "https://example.org/p", "topic": "science", "role": "main", "scores": scores}])
        self.assertEqual(selected[0]["source_title"], "Public report")
        with self.assertRaises(ValueError):
            select_candidates(candidates, [{"source_url": "https://example.org/invented", "topic": "science", "role": "main", "scores": scores}])

    def test_missing_topic_results_fail_closed(self):
        del self.results["AI"]
        with self.assertRaises(ValueError):
            normalize_results(self.results)


if __name__ == "__main__":
    unittest.main()
