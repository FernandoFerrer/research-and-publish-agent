"""Build Dify Knowledge API ingestion requests without storing credentials."""

from datetime import date
from hashlib import sha256

from source_identity import canonical_doi, canonical_url

TOPICS = {"AI", "science", "healthcare", "astronomy", "technology"}
DATASET_FIELDS = ("source_title", "source_url", "publication_date", "retrieval_date", "topic", "doi")


def _iso_date(value, *, optional=False):
    if value is None and optional:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid ISO date") from exc
    if parsed.isoformat() != value:
        raise ValueError("Date must use YYYY-MM-DD")
    return value


def normalize_source(source):
    if not isinstance(source, dict):
        raise ValueError("Source must be an object")
    title, text = source.get("source_title"), source.get("text")
    if not isinstance(title, str) or not title.strip() or not isinstance(text, str) or not text.strip():
        raise ValueError("Source title and retrieved text are required")
    topic = source.get("topic")
    if topic not in TOPICS:
        raise ValueError("Unknown topic")
    retrieval = _iso_date(source.get("retrieval_date"))
    published = _iso_date(source.get("publication_date"), optional=True)
    if published and published > retrieval:
        raise ValueError("Publication date cannot be after retrieval")
    return {"source_title": title.strip(), "source_url": canonical_url(source.get("source_url")),
            "publication_date": published, "retrieval_date": retrieval, "topic": topic,
            "doi": canonical_doi(source.get("doi")), "text": text.strip()}


def document_payload(source):
    source = normalize_source(source)
    # Use a deterministic name to help recovery, but do not rely on names as an
    # atomic uniqueness guarantee. The caller must serialize ingestion runs.
    document_name = "source-" + sha256(source["source_url"].encode("utf-8")).hexdigest()
    return {"name": document_name, "text": source["text"],
            "indexing_technique": "high_quality", "embedding_model": "qwen3-embedding:0.6b",
            "embedding_model_provider": "langgenius/ollama/ollama",
            "process_rule": {"mode": "custom", "rules": {
                "pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True},
                                         {"id": "remove_urls_emails", "enabled": False}],
                "segmentation": {"separator": "\n\n", "max_tokens": 500, "chunk_overlap": 50}}}}


def metadata_payload(document_id, source, definitions):
    source = normalize_source(source)
    if not isinstance(document_id, str) or not document_id.strip() or not isinstance(definitions, dict):
        raise ValueError("Missing document ID or metadata definitions")
    fields = []
    for name in DATASET_FIELDS:
        value = source[name]
        if value is not None:
            field_id = definitions.get(name)
            if not isinstance(field_id, str) or not field_id.strip():
                raise ValueError("Missing dataset metadata field: " + name)
            fields.append({"id": field_id, "name": name, "value": value})
    return {"operation_data": [{"document_id": document_id, "metadata_list": fields, "partial_update": True}]}
