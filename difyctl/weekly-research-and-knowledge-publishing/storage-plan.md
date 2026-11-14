# Research source storage: implementation proposal

App: Weekly Research and Knowledge Publishing. Knowledge base: `weekly-research-database` (`f459de88-bfd5-4bc3-a477-12c1241010fc`). Input: existing `fetch_sources.output`. Preserve the existing search, ranking, retrieval and canvas notes.

## Behavior

1. Keep only sources whose existing metadata check returns `status: accepted`. Preserve rejection details in the existing research outputs.
2. Read all pages of existing documents, retaining their source URL and DOI metadata. Stop with a clear error if the complete listing cannot be read. Normalize source URLs and DOI before comparison. Do not write a source already found by either identity.
3. Process new sources one at a time. Create a document with a source-derived stable name and fetched text, and assign the existing `source_title`, `source_url`, `publication_date`, `retrieval_date`, `topic`, and `doi` metadata fields where values exist.
4. Treat the result as failed if document creation or metadata assignment is missing or failed. Check the returned indexing batch. Report `indexed`, `pending`, `skipped`, or `failed` honestly, with the source URL and any applicable document ID.
5. Return storage results alongside the current outputs. Add visible canvas notes for each new node.

## Integration and safety

- Knowledge Pro is installed and configured using the existing Knowledge API credential. Its tools include `list_documents`, `create_document_by_text` and `get_indexing_status`.
- `create_document_by_text` searches for an exact document name and updates a match. It does not atomically reserve a name, and metadata assignment can fail after document creation. It also converts many errors into text instead of failing the tool call. The workflow must explicitly inspect its JSON result and must not trust a text success message.
- Never blindly retry a create after a timeout: check the document list first because the request may have succeeded.
- List responses are paginated. Pagination must be bounded and fail closed if the full list cannot be verified.
- Only one process may write these sources at a time. A Dify app request limit alone is not an atomic lock, and it cannot control writes made by other apps or external clients. The existing architecture calls for Dagster to serialize deterministic ingestion, but no Dagster module exists in this workspace yet. A safe single-writer mechanism must be established and tested before claiming duplicate protection under concurrency.
- Each source already in the database remains unchanged. An incomplete metadata assignment or pending index must be reported and recoverable, rather than overwritten silently.

## Checks

- Store one accepted public source from a completed research run; inspect its document, metadata and indexing status, then retrieve the indexed text.
- Repeat it and confirm the document count does not increase; cover URL and DOI matches, multi-page listings and unknown identities.
- Check rejected and empty sources, tool errors, timeout/uncertain creates, metadata errors, and pending/error indexing.
- Verify credentials do not appear in exported YAML; ensure existing documents and workflow behavior are intact.

## Current status

The integration tool and credential are configured. No storage nodes have been added and no knowledge documents changed. The exact node configuration, pagination bound, and single-writer mechanism remain to be completed before this can serve as an approved node-level plan.
