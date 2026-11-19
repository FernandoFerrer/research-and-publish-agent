import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dagster import Definitions, ScheduleDefinition, job, op
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')


@op
def run_dify_workflow(context):
    endpoint = os.environ.get('DIFY_WORKFLOW_ENDPOINT', '').rstrip('/')
    key = os.environ.get('DIFY_RESEARCH_WORKFLOW_API_KEY', '')
    if not endpoint or not key:
        raise ValueError('Set DIFY_WORKFLOW_ENDPOINT and DIFY_RESEARCH_WORKFLOW_API_KEY')

    date = datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()
    context.log.info('Starting Dify workflow for %s with a 8-day window', date)
    with requests.post(
        f'{endpoint}/workflows/run',
        headers={'Authorization': f'Bearer {key}'},
        json={'inputs': {'as_of_date': date, 'window_days': 8},
              'response_mode': 'streaming', 'user': 'dagster-weekly-research'},
        stream=True, timeout=(10, 120),
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            if not line or not line.startswith('data:'):
                continue
            event = json.loads(line[5:].strip())
            kind = event.get('event')
            data = event.get('data') or {}
            if kind == 'workflow_started':
                context.log.info('Dify workflow started: run_id=%s', event.get('workflow_run_id'))
            elif kind in ('node_started', 'node_finished'):
                context.log.info('Dify %s: %s%s', kind, data.get('title', data.get('node_id', 'unknown')), f" ({data.get('status')})" if kind == 'node_finished' else '')
            elif kind == 'workflow_finished':
                status = data.get('status', 'unknown')
                context.log.info('Dify workflow finished: status=%s', status)
                if status != 'succeeded':
                    raise RuntimeError(f'Dify workflow did not succeed: {status}')
                return
            elif kind in ('error', 'workflow_paused'):
                raise RuntimeError(f'Dify workflow stopped: {kind}')
    raise RuntimeError('Dify stream ended before workflow completion; check the logged run ID before retrying')


@job
def weekly_research():
    run_dify_workflow()


weekly_schedule = ScheduleDefinition(
    name='weekly_schedule',
    job=weekly_research,
    cron_schedule='0 7 * * 1',
    execution_timezone='Europe/Madrid',
)

defs = Definitions(jobs=[weekly_research], schedules=[weekly_schedule])
