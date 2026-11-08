# Weekly Research: implementation plan (draft)

Status: the user explicitly authorized building the first prototype. App ID: `7c62ae56-b3c5-4a47-a25f-c85281788561`. Build the slices sequentially, leaving the application unpublished. The full node configuration and integration tests are still being developed; no draft should be represented as complete until all required behavior is tested.

## Slice 1: skeleton

Create one Workflow app named `Weekly Research and Knowledge Publishing`. Start node `start` v1 has required `as_of_date` (text) and `window_days` (number). End node `end` v1 returns both inputs, with no article or validated-content output. Connect `start` directly to `end`. Check the DSL, import it, test the full draft with `as_of_date=2026-11-08`, `window_days=7`, and confirm the returned values. Export the draft to `app.yml` and `dify/workflows/weekly-research.yml`. This slice deliberately cannot produce publishable content; it is only a skeleton.

Slice 1 passed: draft run `c8dac9ce-e887-4b0b-bebb-29211c881d3a` returned the two inputs. DSL check reported no issues.

## Slice 2: first research search

Connect `start` → `queries` → `search_ai` → `end`. `queries` is a v1 Python Code node using the exact self-contained `bundle_node.bundle("queries")` source, with inputs `as_of_date` and `window_days` from `start` and string outputs `ai`, `science`, `healthcare`, `astronomy` and `technology`. `search_ai` uses the installed DuckDuckGo `ddgo_search` node data, with `query` from `queries.ai`, `max_results=5`, `require_summary=false`, empty optional proxy and backend. End returns the search node's `json` array as `search_results` and retains both inputs. The slice does not produce publishable content. Check the DSL, test `queries` and `search_ai` individually, then test a full run on the 2026-11-08 seven-day window; verify results contain public URLs. If the configured tool fails, report the failure rather than silently substituting another tool.

Slice 2 passed: the `queries` and `search_ai` node tests succeeded; full draft run `ff63bad7-5856-4999-bb84-3c2597b09dcf` returned five public search results. Several results were older than the requested window, so source dates must be checked after retrieval.

## Slice 3: all requested research areas

Add sequential DuckDuckGo nodes `search_science`, `search_healthcare`, `search_astronomy`, and `search_technology`, each configured exactly like `search_ai` except for its query selector. Add `candidates`, a v1 Python Code node with `bundle_node.bundle("discovery")`, consuming all five tool `json` arrays and returning `candidates` as `array[object]`. Connect the nodes in that order after `search_ai` and return the merged candidates from `end`. The slice remains research-only and produces no publishable article. Check and import the DSL; test each node and then run the full draft. Reject an invalid or failed topic search rather than inventing results.

Slice 3 is blocked: the DSL check and import passed, and `search_science` and `search_healthcare` passed node tests. `search_astronomy` failed twice, including with a broader query: DuckDuckGo's plugin reported no results after three attempts and its diagnostics included rate limits, forbidden responses and CAPTCHA pages. `search_technology`, `candidates`, and the full five-topic draft have not yet passed tests. The local DSL export matches the current draft; do not treat it as a completed workflow.

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
