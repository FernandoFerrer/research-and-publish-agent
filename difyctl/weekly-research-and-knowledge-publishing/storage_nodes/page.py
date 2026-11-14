def main(response, identities, page):
    if not isinstance(response, list) or len(response) != 1 or not isinstance(response[0], dict):
        raise ValueError('Document listing failed or returned an invalid response')
    data = response[0]
    documents = data.get('data')
    more = data.get('has_more')
    if not isinstance(documents, list) or type(more) is not bool or not isinstance(identities, list):
        raise ValueError('Document listing is incomplete or invalid')
    if type(page) not in (int, float) or int(page) != page or page < 1:
        raise ValueError('Invalid document listing page')
    if more and (not documents or page >= 100):
        raise ValueError('Document listing exceeded its safety limit or did not advance')
    for document in documents:
        if not isinstance(document, dict) or not isinstance(document.get('doc_metadata'), list):
            raise ValueError('A stored document has no usable source metadata')
        fields = {item.get('name'): item.get('value') for item in document['doc_metadata'] if isinstance(item, dict)}
        if not fields.get('source_url') and not fields.get('doi'):
            raise ValueError('A stored document has no source URL or DOI; refusing unsafe deduplication')
        identities.append({'source_url': fields.get('source_url'), 'doi': fields.get('doi'), 'name': document.get('name')})
    return {'identities': identities, 'page': int(page) + 1, 'done': 0 if more else 1}
