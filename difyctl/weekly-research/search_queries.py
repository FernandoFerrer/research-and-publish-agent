"""Validate the research window and construct fixed-topic search queries."""

from datetime import date, timedelta

TOPIC_TERMS = {
    "AI": "artificial intelligence research development",
    "science": "scientific research discovery",
    "healthcare": "healthcare clinical research",
    "astronomy": "astronomy astrophysics discovery",
    "technology": "technology research innovation",
}


def build_search_queries(as_of_date, window_days):
    if not isinstance(as_of_date, str):
        raise ValueError("Expected an ISO research date")
    try:
        end = date.fromisoformat(as_of_date)
    except ValueError as exc:
        raise ValueError("Invalid research date") from exc
    if end.isoformat() != as_of_date or type(window_days) is not int or not 1 <= window_days <= 31:
        raise ValueError("Expected YYYY-MM-DD and a window of 1–31 days")
    start = end - timedelta(days=window_days - 1)
    return {topic: f"{terms} after:{start.isoformat()} before:{(end + timedelta(days=1)).isoformat()}"
            for topic, terms in TOPIC_TERMS.items()}
