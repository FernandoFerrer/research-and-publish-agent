import unittest

from source_identity import canonical_url, is_duplicate


class SourceIdentityTests(unittest.TestCase):
    def test_tracking_variants_match_but_distinct_queries_do_not(self):
        existing = [{"source_url": "https://example.org/article?id=7"}]
        self.assertTrue(is_duplicate("https://EXAMPLE.org/article?utm_source=feed&id=7#top", None, existing))
        self.assertFalse(is_duplicate("https://example.org/article?id=8", None, existing))

    def test_same_doi_matches_across_different_urls(self):
        existing = [{"source_url": "https://example.org/one", "doi": "10.1234/TEST"}]
        self.assertTrue(is_duplicate("https://other.example/article", "https://doi.org/10.1234/test", existing))

    def test_invalid_and_credentials_in_url_are_rejected(self):
        for url in ("file:///tmp/a", "https://user:pass@example.org/a", "https://example.org:bad/a"):
            with self.assertRaises(ValueError):
                canonical_url(url)

    def test_existing_list_must_be_present(self):
        with self.assertRaises(ValueError):
            is_duplicate("https://example.org/", None, None)
        with self.assertRaises(ValueError):
            is_duplicate("https://example.org/", None, [{}])


if __name__ == "__main__":
    unittest.main()
