"""Assemble output from exact, checked claims without inventing citations."""

from evidence_gate import validate_claim


def render_content(claims, retrieved, selection, as_of_date):
    """Render model-selected claim IDs using only exact validated claim text.

    Selection is {"main": [IDs], "highlights": [IDs], "topic": one of the
    configured topics}. No model-provided article prose or references are used.
    The final workflow must also validate date/input format and the topic's
    correspondence to the underlying evidence.
    """
    if not isinstance(claims, list) or not isinstance(retrieved, list) or not isinstance(selection, dict):
        raise ValueError("Invalid content inputs")
    if not isinstance(as_of_date, str) or not as_of_date.strip():
        raise ValueError("Missing research date")
    topic = selection.get("topic")
    if topic not in {"AI", "science", "healthcare", "astronomy", "technology"}:
        raise ValueError("Unknown visual topic")
    main = selection.get("main")
    highlights = selection.get("highlights")
    if not isinstance(main, list) or not main or not isinstance(highlights, list):
        raise ValueError("Missing main article or highlight selection")
    all_ids = main + highlights
    if any(not isinstance(x, str) or not x.strip() for x in all_ids) or len(set(all_ids)) != len(all_ids):
        raise ValueError("Invalid or repeated selected claim ID")
    by_id = {}
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str) or not claim["id"]:
            raise ValueError("Invalid claim ID")
        if claim["id"] in by_id:
            raise ValueError("Duplicate claim ID")
        by_id[claim["id"]] = claim

    doc_by_id = {}
    for row in retrieved:
        if isinstance(row, dict) and isinstance(row.get("document_id"), str) and isinstance(row.get("source_url"), str):
            doc_by_id.setdefault((row["document_id"], row["source_url"]), row)

    sources = {}
    def render_claim(claim_id):
        claim = by_id.get(claim_id)
        decision = validate_claim(claim, retrieved)
        if not decision["accepted"]:
            raise ValueError("Selected claim is not validated")
        citations = []
        for doc_id, expected_url in zip(decision["source_document_ids"], decision["source_urls"]):
            doc = doc_by_id.get((doc_id, expected_url), {})
            url = doc.get("source_url")
            title = doc.get("source_title")
            if not isinstance(url, str) or not isinstance(title, str) or not title.strip():
                raise ValueError("Referenced document is missing title or URL")
            sources[doc_id] = {key: doc.get(key) for key in (
                "source_title", "source_url", "publication_date", "retrieval_date", "topic", "doi")}
            citations.append(doc_id)
        return {"claim_id": claim_id, "text": claim["text"], "source_document_ids": citations}

    article = [render_claim(claim_id) for claim_id in main]
    brief = [render_claim(claim_id) for claim_id in highlights]
    return {"status": "validated", "as_of_date": as_of_date,
            "main_article": {"title": article[0]["text"], "paragraphs": article},
            "highlights": brief,
            "visual_concept": "Editorial illustration inspired by " + topic + ".",
            "sources": sources}
