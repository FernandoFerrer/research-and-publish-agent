import hashlib
import json
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

METADATA_IDS = {
    'source_title': 'e27fd733-df1a-485a-a8a9-8facb467e13a',
    'source_url': '60cc76d3-7052-4c12-867b-04226a9a155a',
    'publication_date': 'eff3c4d1-3d2a-4a35-9629-9f035fa4c288',
    'retrieval_date': '8f11b2cf-8886-4efd-858a-a43009240020',
    'topic': 'da3105a6-29ab-4935-89c0-043d50d8aff5',
    'doi': 'd607b371-4543-48be-bf82-c9b23ee50af2',
}


def canonical_url(url):
    if not isinstance(url, str):
        raise ValueError('Source URL must be a string')
    parts = urlsplit(url.strip())
    host = (parts.hostname or '').lower().rstrip('.')
    if parts.scheme.lower() not in {'http', 'https'} or not host or parts.username or parts.password:
        raise ValueError('Source URL must be HTTP(S) without credentials')
    port = parts.port
    scheme = parts.scheme.lower()
    authority = f'[{host}]' if ':' in host else host
    if port and (scheme, port) not in {('http', 80), ('https', 443)}:
        authority += f':{port}'
    tracking = {'fbclid', 'gclid', 'mc_cid', 'mc_eid'}
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in tracking]
    return urlunsplit((scheme, authority, parts.path or '/', urlencode(sorted(query), doseq=True), ''))


def canonical_doi(doi):
    if doi is None or doi == '':
        return None
    if not isinstance(doi, str):
        raise ValueError('DOI must be a string')
    value = doi.strip().lower()
    for prefix in ('https://doi.org/', 'http://doi.org/', 'https://dx.doi.org/', 'doi:'):
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
            break
    if not value.startswith('10.') or '/' not in value or any(c.isspace() for c in value):
        raise ValueError('Invalid DOI')
    return value


def main(sources, identities, listing_complete):
    if listing_complete != 1 or not isinstance(identities, list) or not isinstance(sources, list):
        raise ValueError('Cannot store sources without a complete document listing')
    urls, dois, names = set(), set(), set()
    for item in identities:
        if not isinstance(item, dict) or (not item.get('source_url') and not item.get('doi')):
            raise ValueError('Stored document has no source identity')
        if item.get('source_url'):
            urls.add(canonical_url(item['source_url']))
        if item.get('doi'):
            dois.add(canonical_doi(item['doi']))
        if item.get('name'):
            names.add(item['name'])
    pending, skipped = [], []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError('Source retrieval failed; no source can be stored safely')
        if source.get('status') == 'rejected':
            continue
        if source.get('status') != 'accepted':
            raise ValueError('Source has an unknown retrieval status')
        for field in ('source_url', 'source_title', 'retrieval_date', 'topic', 'text'):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError('Accepted source is missing ' + field)
        url = canonical_url(source['source_url'])
        doi = canonical_doi(source.get('doi'))
        if url in urls or (doi and doi in dois):
            skipped.append({'source_url': url, 'status': 'skipped'})
            continue
        name = 'research-' + hashlib.sha256(url.encode()).hexdigest()
        if name in names:
            raise ValueError('Document name is already in use; inspect it before retrying')
        fields = dict(source)
        fields['source_url'] = url
        metadata = [{'id': identifier, 'name': key, 'value': fields[key]}
                    for key, identifier in METADATA_IDS.items() if fields.get(key) is not None]
        pending.append({'source_url': url, 'name': name, 'text': source['text'],
                        'metadata_json': json.dumps(metadata, ensure_ascii=False)})
        urls.add(url)
        if doi:
            dois.add(doi)
        names.add(name)
    return {'to_store': pending, 'skipped': skipped}
