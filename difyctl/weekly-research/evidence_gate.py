"""Fail-closed structural checks for the proposed Dify validation stage.

The reviewer must judge entailment, contradictions and the underlying work IDs.
These checks cannot prove any of those judgments; they check that citations and
quotes are present in the actual retrieved evidence and enforce separation.
"""

from urllib.parse import urlsplit


# Exact host or subdomain matching. Each group is one publisher/organization,
# not an independent study. Extend through a reviewed configuration change.
TRUSTED_PUBLISHERS = {
    "nasa": ("nasa.gov",),
    "esa": ("esa.int",),
    "nih": ("nih.gov",),
    "cdc": ("cdc.gov",),
    "who": ("who.int",),
    "nature": ("nature.com",),
    "science": ("science.org",),
    "pnas": ("pnas.org",),
    "nejm": ("nejm.org",),
    "bmj": ("bmj.com",),
    "thelancet": ("thelancet.com",),
}


def _publisher(url):
    if not isinstance(url, str):
        return None
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower().rstrip(".")
        if parts.scheme not in ("https", "http") or not host or parts.username or parts.password:
            return None
    except (TypeError, ValueError):
        return None
    for group, domains in TRUSTED_PUBLISHERS.items():
        if any(host == domain or host.endswith("." + domain) for domain in domains):
            return group
    return None


def _origin_id(value):
    value = value.strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if value.startswith(prefix):
            return value[len(prefix):].strip()
    return value


def validate_claim(claim, retrieved):
    """Return a decision for one claim against exact retrieved snippets.

    `retrieved` items must include `document_id`, `source_url`, and `content`.
    Each reviewer evidence item supplies `document_id`, a verbatim `quote`, an
    `origin_id` for the underlying independent work, and a boolean `supports`.
    Missing origin, unverified quotes, unknown publishers and contradictions
    never count as confirmation. A contradiction rejects the entire claim.
    """
    if not isinstance(claim, dict) or not isinstance(retrieved, list):
        return {"accepted": False, "reason": "invalid_input"}
    if not isinstance(claim.get("text"), str) or not claim["text"].strip():
        return {"accepted": False, "reason": "empty_claim"}
    evidence = claim.get("evidence")
    if not isinstance(evidence, list):
        return {"accepted": False, "reason": "missing_evidence"}

    # Multiple chunks can share a document ID; each quote must match one chunk.
    matched = []
    contradiction = False
    for item in evidence:
        if not isinstance(item, dict):
            continue
        document_id, quote, origin = item.get("document_id"), item.get("quote"), item.get("origin_id")
        if not all(isinstance(x, str) and x.strip() for x in (document_id, quote)):
            continue
        for row in retrieved:
            if not isinstance(row, dict) or row.get("document_id") != document_id:
                continue
            content = row.get("content")
            publisher = _publisher(row.get("source_url"))
            if not publisher or not isinstance(content, str) or quote not in content:
                continue
            if item.get("supports") is False:
                contradiction = True
            elif item.get("supports") is True and isinstance(origin, str) and _origin_id(origin):
                matched.append((publisher, _origin_id(origin), row.get("source_url"), document_id))
            break
    if contradiction:
        return {"accepted": False, "reason": "contradiction"}
    # Two separate publishers and two separately identified underlying works.
    for i, first in enumerate(matched):
        for second in matched[i + 1 :]:
            if first[0] != second[0] and first[1] != second[1] and first[2] != second[2] and first[3] != second[3]:
                return {"accepted": True, "reason": "two_independent_evidence_items",
                        "source_document_ids": [first[3], second[3]],
                        "source_urls": [first[2], second[2]]}
    return {"accepted": False, "reason": "insufficient_independent_evidence"}
