def main(response, source, document_id):
    if not isinstance(response, list) or len(response) != 1 or not isinstance(response[0], dict):
        raise ValueError('Indexing status could not be checked')
    rows = response[0].get('data')
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise ValueError('Indexing status is missing or ambiguous')
    item = rows[0]
    if item.get('id') and item['id'] != document_id:
        raise ValueError('Indexing status belongs to another document')
    status = item.get('indexing_status')
    if status == 'completed':
        state = 'indexed'
    elif status in ('waiting', 'parsing', 'cleaning', 'splitting', 'indexing'):
        state = 'pending'
    elif status == 'error':
        raise ValueError('Document indexing failed: ' + str(item.get('error') or 'unknown error'))
    else:
        raise ValueError('Unrecognized document indexing status: ' + str(status))
    return {'result': {'source_url': source['source_url'], 'document_id': document_id, 'status': state}}
