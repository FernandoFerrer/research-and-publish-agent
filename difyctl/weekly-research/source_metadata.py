"""Check extracted source metadata against fetched public source text."""

from datetime import date, datetime, timedelta
import json
import re


def _date_in_quote(quote):
    patterns = (r"\b\d{4}-\d{2}-\d{2}\b", r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b")
    found = set()
    for pattern in patterns:
        for match in re.findall(pattern, quote, flags=re.IGNORECASE):
            for fmt in ("%Y-%m-%d", "%B %d, %Y"):
                try:
                    found.add(datetime.strptime(match, fmt).date().isoformat())
                    break
                except ValueError:
                    pass
    if len(found) != 1:
        raise ValueError("Publication quote must contain exactly one recognizable date")
    return found.pop()


def validate_metadata(selected, text, proposed, as_of_date, window_days, retrieval_date):
    """Reject metadata claims not grounded in exact source quotations.

    Dates in unsupported formats cannot establish recency. DOI can be omitted
    if unavailable; if supplied, the DOI must occur in the fetched source text.
    """
    if not all(isinstance(x, dict) for x in (selected, proposed)) or not isinstance(text, str) or not text.strip():
        raise ValueError("Missing source content or metadata")
    title = proposed.get("source_title")
    if not isinstance(title, str) or not title.strip() or title.strip() not in text:
        raise ValueError("Source title is not present in the fetched text")
    end = date.fromisoformat(as_of_date)
    if end.isoformat() != as_of_date or type(window_days) is not int or not 1 <= window_days <= 31:
        raise ValueError("Invalid research date or window")
    retrieved = date.fromisoformat(retrieval_date)
    if retrieved.isoformat() != retrieval_date or retrieved < end:
        raise ValueError("Invalid retrieval date")
    published, quote = proposed.get("publication_date"), proposed.get("publication_quote")
    if published is None:
        if selected.get("role") in ("main", "highlight"):
            raise ValueError("Recent story has no verifiable publication date")
    else:
        if not isinstance(quote, str) or not quote.strip() or quote not in text or _date_in_quote(quote) != published:
            raise ValueError("Publication date is not supported by the source quote")
        parsed = date.fromisoformat(published)
        if selected.get("role") in ("main", "highlight") and not end - timedelta(days=window_days - 1) <= parsed <= end:
            raise ValueError("Story publication is outside the research window")
    doi = proposed.get("doi")
    if doi is not None and (not isinstance(doi, str) or not doi.strip() or doi.casefold() not in text.casefold()):
        raise ValueError("DOI is not present in the fetched text")
    return {"source_title": title.strip(), "source_url": selected.get("source_url"),
            "publication_date": published, "retrieval_date": retrieval_date, "topic": selected.get("topic"),
            "doi": doi, "text": text}


def check_source(selected, text, proposed_json, as_of_date, window_days, retrieval_date):
    try:
        source = validate_metadata(selected, text, json.loads(proposed_json), as_of_date, window_days, retrieval_date)
    except (TypeError, ValueError) as exc:
        return {"status": "rejected", "source_url": selected.get("source_url"), "reason": str(exc)}
    return {"status": "accepted", **source}
