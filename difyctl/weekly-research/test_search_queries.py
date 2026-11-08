import unittest

from search_queries import build_search_queries


class SearchQueryTests(unittest.TestCase):
    def test_all_topics_and_inclusive_seven_day_window(self):
        result = build_search_queries("2026-11-08", 7)
        self.assertEqual(len(result), 5)
        self.assertIn("after:2026-11-02", result["astronomy"])
        self.assertIn("before:2026-11-09", result["astronomy"])

    def test_invalid_inputs_fail(self):
        for day, window in (("2026-02-30", 7), ("2026-11-08", 0), ("2026-11-08", True)):
            with self.assertRaises(ValueError):
                build_search_queries(day, window)


if __name__ == "__main__":
    unittest.main()
