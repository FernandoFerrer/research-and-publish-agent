"""Canonical source identity for draft ingestion planning and tests."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS = frozenset({"fbclid", "gclid", "mc_cid", "mc_eid"})


def canonical_url(url):
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower().rstrip(".")
    if parts.scheme.lower() not in {"http", "https"} or not host or parts.username or parts.password:
        raise ValueError("Expected an HTTP(S) URL without credentials")
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("Invalid URL port") from exc
    scheme = parts.scheme.lower()
    authority = f"[{host}]" if ":" in host else host
    if port and (scheme, port) not in {("http", 80), ("https", 443)}:
        authority += f":{port}"
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if not key.lower().startswith("utm_") and key.lower() not in TRACKING_KEYS]
    return urlunsplit((scheme, authority, parts.path or "/", urlencode(sorted(query), doseq=True), ""))


def canonical_doi(doi):
    if not doi:
        return None
    if not isinstance(doi, str):
        raise ValueError("DOI must be a string")
    value = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
            break
    if not value.startswith("10.") or "/" not in value or any(c.isspace() for c in value):
        raise ValueError("Invalid DOI")
    return value


def is_duplicate(url, doi, existing):
    """Match URL or DOI against all previously indexed sources supplied by caller.

    Caller must fully paginate and serialize ingestion runs. If it cannot do so,
    it must fail closed; this function does not make concurrent creates atomic.
    """
    normalized_url = canonical_url(url)
    normalized_doi = canonical_doi(doi)
    if not isinstance(existing, list):
        raise ValueError("Existing sources must be a complete list")
    for source in existing:
        if not isinstance(source, dict):
            raise ValueError("Invalid existing source")
        old_url = source.get("source_url")
        old_doi = source.get("doi")
        if not old_url and not old_doi:
            raise ValueError("Existing source has no identity; refusing unsafe deduplication")
        if old_url and canonical_url(old_url) == normalized_url:
            return True
        if normalized_doi and old_doi and canonical_doi(old_doi) == normalized_doi:
            return True
    return False
