"""Validate discovery results and prevent a model from inventing source URLs."""

from source_identity import canonical_url

TOPICS = frozenset({"AI", "science", "healthcare", "astronomy", "technology"})


def normalize_results(results_by_topic):
    if not isinstance(results_by_topic, dict) or set(results_by_topic) != TOPICS:
        raise ValueError("Search results must cover all five topics")
    candidates = {}
    for topic in sorted(TOPICS):
        results = results_by_topic[topic]
        if not isinstance(results, list):
            raise ValueError("Search failed or returned an invalid list")
        for row in results:
            if not isinstance(row, dict):
                continue
            try:
                url = canonical_url(row.get("href"))
            except (ValueError, TypeError):
                continue
            title = row.get("title")
            if not isinstance(title, str) or not title.strip():
                continue
            candidate = candidates.setdefault(url, {"source_url": url, "title": title.strip(),
                                                     "topics": [], "snippet": row.get("body", "")})
            if topic not in candidate["topics"]:
                candidate["topics"].append(topic)
    return list(candidates.values())


def select_candidates(candidates, selection, limit=10):
    if not isinstance(candidates, list) or not isinstance(selection, list):
        raise ValueError("Invalid research selection")
    if type(limit) is not int or limit < 1 or limit > 20:
        raise ValueError("Invalid selection limit")
    if not selection:
        return []
    by_url = {item["source_url"]: item for item in candidates}
    chosen = []
    seen = set()
    for item in selection:
        if not isinstance(item, dict):
            raise ValueError("Invalid selected item")
        url = canonical_url(item.get("source_url"))
        topic = item.get("topic")
        role = item.get("role")
        scores = item.get("scores")
        if role not in {"main", "support", "highlight"} or not isinstance(scores, dict):
            raise ValueError("Missing research role or ranking scores")
        for field in ("relevance", "novelty", "credibility", "reader_interest"):
            score = scores.get(field)
            if type(score) is not int or not 1 <= score <= 5:
                raise ValueError("Invalid research score")
        if url not in by_url or topic not in by_url[url]["topics"] or url in seen:
            raise ValueError("Selected source not found in topic search results, or repeated")
        seen.add(url)
        chosen.append({"source_url": url, "source_title": by_url[url]["title"], "topic": topic,
                       "role": role, "scores": scores})
    if len(chosen) > limit or sum(item["role"] == "main" for item in chosen) != 1:
        raise ValueError("Research selection is empty or exceeds its limit")
    return chosen
