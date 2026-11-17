import importlib.util
import json
import os
import unittest
from unittest.mock import MagicMock, patch

from datetime import datetime
from zoneinfo import ZoneInfo

from dagster import build_op_context

spec = importlib.util.spec_from_file_location('definitions', 'dagster/definitions.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkflowTest(unittest.TestCase):
    def run_events(self, events):
        response = MagicMock()
        response.__enter__.return_value = response
        response.iter_lines.return_value = ['data: ' + json.dumps(event) for event in events]
        with patch.dict(os.environ, {'DIFY_WORKFLOW_ENDPOINT': 'http://example.test/v1',
                                    'DIFY_RESEARCH_WORKFLOW_API_KEY': 'test-key'}), \
             patch.object(module.requests, 'post', return_value=response) as post:
            module.run_dify_workflow(build_op_context())
            self.assertEqual(post.call_args.args[0], 'http://example.test/v1/workflows/run')
            self.assertEqual(post.call_args.kwargs['json']['inputs'], {
                'as_of_date': datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat(),
                'window_days': 7,
            })

    def test_success(self):
        self.run_events([{'event': 'workflow_started', 'workflow_run_id': '123'},
                         {'event': 'node_finished', 'data': {'title': 'Research', 'status': 'succeeded'}},
                         {'event': 'workflow_finished', 'data': {'status': 'succeeded'}}])

    def test_failure_and_incomplete_stream(self):
        for events in ([{'event': 'workflow_finished', 'data': {'status': 'failed'}}],
                       [{'event': 'error'}], []):
            with self.subTest(events=events), self.assertRaises(RuntimeError):
                self.run_events(events)


if __name__ == '__main__':
    unittest.main()
