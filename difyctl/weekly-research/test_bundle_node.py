import unittest

from bundle_node import CONFIGS, bundle


class BundleNodeTests(unittest.TestCase):
    def test_every_bundle_is_self_contained_and_exposes_main(self):
        for name in CONFIGS:
            with self.subTest(name=name):
                namespace = {}
                exec(bundle(name), namespace)
                self.assertTrue(callable(namespace["main"]))

    def test_identity_node_detects_existing_canonical_url(self):
        namespace = {}
        exec(bundle("identity"), namespace)
        result = namespace["main"]("https://example.org/article?utm_source=test", None,
                                   [{"source_url": "https://example.org/article"}])
        self.assertEqual(result["duplicate"], 1)


if __name__ == "__main__":
    unittest.main()
