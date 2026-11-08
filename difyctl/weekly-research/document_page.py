"""Strict parsing of one Dify Knowledge API document-list page."""


def parse_document_page(page, expected_page):
    """Return document identities and the next page; fail on incomplete metadata.

    Pagination and write serialization are the caller's responsibility. This
    function does not make a list-and-create sequence atomic.
    """
    if not isinstance(page, dict) or type(expected_page) is not int or expected_page < 1:
        raise ValueError("Invalid document page or page number")
    if page.get("page") != expected_page or type(page.get("has_more")) is not bool:
        raise ValueError("Unexpected or incomplete document pagination")
    documents = page.get("data")
    if not isinstance(documents, list):
        raise ValueError("Document page has no document list")
    identities = []
    for document in documents:
        if not isinstance(document, dict) or not document.get("id"):
            raise ValueError("Document is missing an ID")
        fields = document.get("doc_metadata")
        if not isinstance(fields, list):
            raise ValueError("Document has no metadata list")
        values = {}
        for field in fields:
            if not isinstance(field, dict) or not isinstance(field.get("name"), str):
                raise ValueError("Invalid document metadata field")
            name = field["name"]
            if name in values:
                raise ValueError("Duplicate document metadata field")
            values[name] = field.get("value")
        url, doi = values.get("source_url"), values.get("doi")
        if not isinstance(url, str) or not url.strip():
            raise ValueError("Document is missing source URL metadata")
        if doi is not None and not isinstance(doi, str):
            raise ValueError("Invalid DOI metadata")
        identities.append({"document_id": document["id"], "source_url": url, "doi": doi})
    return {"sources": identities, "next_page": expected_page + 1 if page["has_more"] else None}
