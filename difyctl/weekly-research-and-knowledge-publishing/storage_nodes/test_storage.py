import copy
import unittest

import check_index
import check_write
import page
import prepare


class StorageChecks(unittest.TestCase):
    def setUp(self):
        self.source = {'status': 'accepted', 'source_url': 'https://example.org/story?utm_source=x',
                       'source_title': 'Story', 'retrieval_date': '2026-11-11', 'topic': 'science',
                       'publication_date': None, 'doi': '10.1234/test', 'text': 'Public source text.'}

    def test_pagination_and_deduplication(self):
        first = page.main([{'data': [{'name': 'old', 'doc_metadata': [{'name': 'source_url', 'value': 'https://example.org/other'}]}],
                            'has_more': True}], [], 1)
        second = page.main([{'data': [{'name': 'match', 'doc_metadata': [{'name': 'doi', 'value': 'https://doi.org/10.1234/test'}]}],
                             'has_more': False}], first['identities'], first['page'])
        result = prepare.main([self.source], second['identities'], second['done'])
        self.assertEqual(result['to_store'], [])
        self.assertEqual(result['skipped'][0]['status'], 'skipped')

    def test_fail_closed_and_ignore_rejected(self):
        with self.assertRaises(ValueError):
            page.main([{'data': [{'doc_metadata': []}], 'has_more': False}], [], 1)
        with self.assertRaises(ValueError):
            page.main([{'data': [{'doc_metadata': []}], 'has_more': True}], [], 100)
        with self.assertRaises(ValueError):
            prepare.main([self.source], [], 0)
        rejected = {'status': 'rejected'}
        result = prepare.main([rejected, self.source, copy.deepcopy(self.source)], [], 1)
        self.assertEqual(len(result['to_store']), 1)
        self.assertEqual(len(result['skipped']), 1)

    def test_write_and_index_states(self):
        write = {'operation': 'create', 'document': {'id': 'doc'}, 'batch': 'batch',
                 'metadata_assignment': {'success': True}}
        self.assertEqual(check_write.main([write])['document_id'], 'doc')
        bad = dict(write, metadata_assignment={'success': False})
        with self.assertRaises(ValueError):
            check_write.main([bad])
        with self.assertRaises(ValueError):
            check_write.main([])
        for raw, expected in [('indexing', 'pending'), ('completed', 'indexed')]:
            result = check_index.main([{'data': [{'id': 'doc', 'indexing_status': raw}]}], self.source, 'doc')
            self.assertEqual(result['result']['status'], expected)
        with self.assertRaises(ValueError):
            check_index.main([{'data': [{'id': 'doc', 'indexing_status': 'error'}]}], self.source, 'doc')


if __name__ == '__main__':
    unittest.main()
