# Weekly Research: implementation plan (draft)

The current Dify draft searches, ranks sources with Ollama, and fetches and checks source metadata. Invalid or unverifiable source metadata produces a rejected record so other sources can continue. A failed fetch or model call produces a null in the same position as its selected source. Accepted sources are not yet validated claims. The current draft is saved in `app.yml`; the published version is saved in `live.yml`.

Draft run `649ddaeb-fc44-490f-8ec4-3f6c6bff202d` completed after two selected sites failed to load. Both fetched-source entries were null, so this test did not demonstrate a usable source.

Still needed: ingestion with safe deduplication, knowledge retrieval, independent claim validation and cited content. The shared knowledge base can also be written by other applications or direct API clients, so a per-app concurrency limit alone cannot guarantee deduplication.

## Proposed data flow

```mermaid
flowchart TD
    start[Start: run date and research window] --> search[Search AI, science, healthcare, astronomy and technology]
    search --> rank[Research: rank discoveries and select topics]
    rank --> fetch[Fetch public source material]
    fetch --> ingest[Serial ingestion, deduplication and metadata]
    ingest --> claims[Extract important claims]
    claims --> retrieve[Retrieve top-5 knowledge-base evidence per claim]
    retrieve --> review[Validation: evaluate support, origin and contradictions]
    review --> gate[Deterministic evidence gate]
    gate --> valid{Validated claims available?}
    valid -- no --> fail[End with failure and rejected claims]
    valid -- yes --> write[Content: article, highlights and visual concept]
    write --> audit[Revalidate writing and references]
    audit --> passed{Audit passed?}
    passed -- no --> fail
    passed -- yes --> end[End with structured cited content]
```

The graph is a business-flow draft, not a complete Dify node graph. Prefer rejecting unsupported claims after the initial research pass; the spec permits this and it bounds retries without a second research agent.

## Confirmed resources

- Dify Workflow; language model `langgenius/ollama/ollama`, `qwen3.5:27b`.
- Search: installed `langgenius/duckduckgo/duckduckgo`, tool `ddgo_search`. It has not yet been exercised in a Dify workflow.
- Source fetch: configured built-in `webscraper` tool. It has not yet been exercised in this workflow.
- Knowledge: `f459de88-bfd5-4bc3-a477-12c1241010fc`, high-quality indexing and semantic retrieval. Override the retrieval-node default to top-k 5.
- Knowledge API from workflow HTTP nodes: `http://nginx/v1/datasets/f459de88-bfd5-4bc3-a477-12c1241010fc`; Dify's environment variable for the bearer token must be secret and supplied without placing the token in a DSL file. A scoped proxy rule has been tested outside a workflow.

## Proposed interfaces

- Start: `as_of_date`, an ISO calendar date, and `window_days`, an integer bounded to 1–31. Reject invalid input rather than assuming the execution host's clock.
- Source record: `source_title`, `source_url`, `publication_date` (null if unavailable), `retrieval_date`, `topic`, `doi` (null if unavailable), and retrieved text. Do not infer publication dates or DOIs from search snippets when not verifiable.
- Claim record: `id`, `text`, `topic`, `evidence` and a validation decision. Each evidence item carries the retrieved `document_id`, an exact `quote`, `origin_id` for its underlying work and `supports` boolean. The verifier must report both supporting and contradicting material; unknown origin cannot establish independence.
- Successful output: JSON containing `status`, `as_of_date`, `main_article`, `highlights`, `visual_concept`, `claims`, and `sources`. Each factual statement must map to accepted claim IDs and references. Failed or insufficient evidence must produce a structured failure and no publishable article.
- Maximums, precise output schemas and prompt wording remain to be specified before build. The final audit must identify new claims and fail closed if it cannot connect them to validated evidence.

## Deterministic checks prepared

- `evidence_gate.py` checks exact quotations against retrieved text, known publisher domains, separate publishers and distinct reviewer-supplied work identifiers. It rejects contradictions and insufficient evidence. **This is not proof of semantic support or source independence**: the reviewer must identify the underlying work and assess support correctly. Require manual or independent evaluation in acceptance testing.
- `source_identity.py` identifies matching canonical URLs or DOIs. The ingestion design must read the complete paginated document list and serialize writers, or fail closed; the helper does not prevent concurrent API creates on its own. It strips common tracking parameters but does not resolve URL redirects.
- `search_candidates.py` maps the configured search plugin's JSON result shape into candidates, deduplicates URLs and rejects selections that were absent from the corresponding topic's search results. Live tool output remains untested.
- `search_queries.py` constructs five dated topic queries and validates the research window. Search date operators are hints; publication dates must still be verified from the retrieved sources because a search provider may not honor them.
- `source_metadata.py` checks extracted titles, publication-date quotes and DOIs against fetched source text. Main stories and highlights require a verified date in the research window. It supports ISO and English full-month dates; unsupported formats fail closed for recent stories.
- `document_page.py` parses one Knowledge API document-list page and fails closed when source identity or pagination metadata is missing. The API's page and document-metadata shapes were inspected against the connected knowledge base; the workflow pagination loop is not yet built.
- `ingestion_payload.py` builds create-document and metadata requests using the configured model, 500-token chunks and 50-token overlap. It rejects missing title/text, invalid dates and unavailable required metadata IDs. Serial execution, requests, error recovery and indexing polling remain to be implemented.
- `bundle_node.py` builds self-contained Python source for proposed Dify Code nodes, so sandbox nodes do not try to import repository-local modules. Generated snippets compile and are unit-tested locally; Dify sandbox execution is not yet tested.
- `retrieval_adapter.py` maps Dify's `knowledge-retrieval` node result structure to the evidence gate, preserving document metadata with each chunk and rejecting missing metadata or a different dataset. The schema was inspected in the connected Dify worker; actual workflow output is not yet tested.
- `render_content.py` is an experimental conservative renderer: a model can choose claim IDs, but factual prose is copied exactly from validated claim records and citations are built from retrieved document metadata. This avoids introducing new factual prose during assembly, at the cost of limited editorial flexibility. Whether this satisfies the requested content stage must be settled in the completed plan.
- `prompts/` contains draft prompts for source selection, metadata extraction, claims, evidence assessment and content selection. These have not been run with the configured model; the exact node configuration and test cases remain open.
- Focused unit tests: `python3 -m unittest discover -v` from this directory.

## Required remaining plan work

1. Specify all Dify node IDs, node versions, prompt text, schemas, iteration/branch edges, input/output selectors, API request bodies, error branches, timeout and bounded indexing checks. The current graph does not meet the skill's node-level planning gate.
2. Complete and test code for parsing tool output, generating safe API bodies, pagination, serial ingestion and indexing checks, writing metadata, matching retrieved chunks to document metadata, and final content auditing.
3. Resolve a reliable serialization mechanism for ingestion and document its failure mode; Dify's create-by-text API cannot be assumed to atomically deduplicate concurrent writers.
4. Map every requirement and acceptance case in `spec.md` to a node and tests, including rejection of same-study reports and new writer claims. Define the independently corroborated real-source test case.
5. Define connected build slices, node tests, full draft runs, and export/secret checks. Preserve the Dify DSL and skill working files.

## Scope

Keep the application unpublished; no Dagster scheduling, website deployment, email, or Git push. Never place credentials in workflow exports or tracked files.
