def main(response):
    if not isinstance(response, list) or len(response) != 1 or not isinstance(response[0], dict):
        raise ValueError('Document write failed or is uncertain; inspect the knowledge base before retrying')
    result = response[0]
    doc = result.get('document')
    metadata = result.get('metadata_assignment')
    if result.get('operation') != 'create':
        raise ValueError('Document was not newly created; inspect the knowledge base before retrying')
    if not isinstance(doc, dict) or not isinstance(doc.get('id'), str) or not doc['id']:
        raise ValueError('Document ID missing; inspect the knowledge base before retrying')
    if not isinstance(metadata, dict) or metadata.get('success') is not True:
        raise ValueError('Document metadata assignment failed; inspect the knowledge base before retrying')
    batch = result.get('batch')
    if not isinstance(batch, str) or not batch:
        raise ValueError('Indexing batch missing; inspect the knowledge base before retrying')
    return {'document_id': doc['id'], 'batch': batch}
