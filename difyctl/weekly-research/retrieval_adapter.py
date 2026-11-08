"""Convert Dify knowledge-retrieval node results into evidence-gate inputs."""

DATASET_ID = "f459de88-bfd5-4bc3-a477-12c1241010fc"


def adapt_retrieval(results):
    if not isinstance(results, list):
        raise ValueError("Knowledge retrieval result must be a list")
    evidence = []
    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Invalid retrieval result")
        metadata = result.get("metadata")
        if not isinstance(metadata, dict) or metadata.get("dataset_id") != DATASET_ID:
            raise ValueError("Retrieval result missing expected dataset metadata")
        doc = metadata.get("doc_metadata")
        if not isinstance(doc, dict):
            raise ValueError("Retrieval result missing document metadata")
        document_id = metadata.get("document_id")
        url = doc.get("source_url")
        content = result.get("content")
        if not all(isinstance(x, str) and x.strip() for x in (document_id, url, content)):
            raise ValueError("Retrieval result missing document ID, source URL or content")
        evidence.append({
            "document_id": document_id,
            "source_url": url,
            "source_title": doc.get("source_title"),
            "publication_date": doc.get("publication_date"),
            "retrieval_date": doc.get("retrieval_date"),
            "topic": doc.get("topic"),
            "doi": doc.get("doi"),
            "content": content,
        })
    return evidence
