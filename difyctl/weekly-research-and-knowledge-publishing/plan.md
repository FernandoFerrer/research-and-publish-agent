# Research source storage: node-level plan

App `7c62ae56-b3c5-4a47-a25f-c85281788561`; knowledge base `f459de88-bfd5-4bc3-a477-12c1241010fc`. Spec: `spec.md`, requirements S1–S6. The user selected Dify-only with one run at a time; external writers must also be kept idle. The app's one-request limit is an additional guard, not an atomic lock.

## Graph

```mermaid
flowchart LR
  fetch_sources --> list_pages --> prepare_sources --> store_sources --> end
  subgraph list_pages
    page_start --> list_documents --> check_page --> save_page
  end
  subgraph store_sources
    store_start --> create_document --> check_write --> indexing_status --> check_index
  end
```

`list_pages` breaks when `done = 1`. `store_sources` runs one item at a time. The existing edge `fetch_sources → end` is replaced; existing outputs and all other existing nodes and edges remain. The end node and its existing comment are moved as needed, and a visible note is added for each new node.

## Exact node configuration

All plugin nodes use `abesticode/knowledge_pro/knowledge_pro`, the installed and configured Knowledge Pro provider, its default credential, tool version 2, and the node data returned by `difyctl get tool`; the target dataset ID is constant above. Existing research nodes and credentials are unchanged.

| ID | Type | Inputs, outputs and configuration | Covers |
| --- | --- | --- | --- |
| `list_pages` | loop v1 | `loop_count: 100`; `start_node_id: page_start`; variables `page` number constant 1, `identities` array[object] constant [], `done` number constant 0. Break when `list_pages.done = 1` (operator `=`); logical operator `and`. | S3–S4 |
| `page_start` | loop-start v1 | Start of `list_pages`. | S3 |
| `list_documents` | tool v1 | Knowledge Pro `list_documents`: dataset ID constant; keyword and status empty; page from `[list_pages, page]`, limit 100. | S3–S4 |
| `check_page` | code v1 | Code is exactly `storage_nodes/page.py`; inputs `response=[list_documents,json]`, `identities=[list_pages,identities]`, `page=[list_pages,page]`. Outputs `identities` array[object], `page` number, `done` number. | S3–S4 |
| `save_page` | assigner v2 | Overwrite loop variables `identities`, `page`, and `done` with matching outputs from `check_page`. | S3–S4 |
| `prepare_sources` | code v1 | Code is exactly `storage_nodes/prepare.py`; inputs `sources=[fetch_sources,output]`, `identities=[list_pages,identities]`, `listing_complete=[list_pages,done]`. Outputs `to_store` and `skipped`, both array[object]. | S1–S5 |
| `store_sources` | iteration v1 | Sequential, no parallelism; iterator `[prepare_sources,to_store]`, output `[check_index,result]`, error mode `terminated`. | S1–S4 |
| `store_start` | iteration-start v1 | Start of `store_sources`. | S1 |
| `create_document` | tool v1 | Knowledge Pro `create_document_by_text`: dataset ID constant; name and text from the current iteration item's `name` and `text`; indexing technique `high_quality`; doc form `text_model`; process rule `{"mode":"automatic"}`; metadata JSON from the current item's `metadata_json`; remaining optional fields empty. No automatic retry. | S1, S4–S5 |
| `check_write` | code v1 | Code is exactly `storage_nodes/check_write.py`; input `response=[create_document,json]`; outputs `document_id` and `batch`, strings. | S4 |
| `indexing_status` | tool v1 | Knowledge Pro `get_indexing_status`: dataset ID constant; batch `[check_write,batch]`. No automatic retry. | S4 |
| `check_index` | code v1 | Code is exactly `storage_nodes/check_index.py`; inputs `response=[indexing_status,json]`, `source=[store_sources,item]`, `document_id=[check_write,document_id]`; output `result` object. | S4 |
| `end` | end v1 | Keep existing outputs; add `stored_sources=[store_sources,output]`, `skipped_sources=[prepare_sources,skipped]`. | S1–S4 |

Code files are part of this plan and contain the exact source, metadata IDs, validation and error messages. `page.py` fails when another page remains after page 100. `prepare.py` rejects any pre-existing document without a URL or DOI, skips existing or repeated identities, and fails on a generated-name collision. `check_write.py` verifies the plugin created a document, successfully assigned metadata and returned a batch. `check_index.py` reports only `indexed` or `pending`; failed or unknown statuses fail clearly. A timeout is not retried blindly.

## Slices and tests

1. **Listing slice:** Add the page loop and `prepare_sources` with visible notes; preserve all existing research outputs. Check DSL before import. Test page parsing and source filtering independently; run the whole draft on an existing valid research case and review results. No knowledge documents are written in this slice.
2. **Storage slice:** Add the sequential storage iteration and end outputs, with visible notes; set the app concurrency limit to one and verify it. Check DSL before import. Run node checks for write-result and indexing parsing; test accepted, rejected, duplicate, missing-identity, paginated, metadata-error and indexing-error cases. Run a full draft with a real accepted public source, verify document metadata and indexing, repeat to check no duplicate, and test retrieval once indexed. The write is not undone by deleting documents.

The Python checks in `storage_nodes/test_storage.py` cover pagination, a later-page DOI match, rejected and repeated sources, incomplete listings, missing identity, metadata failure, pending and error indexing. They passed before workflow implementation. Tool behavior, dynamic pagination/metadata bindings, and the app's concurrency setting still require Dify integration tests; any unsupported behavior blocks the slice and is reported rather than silently substituted.

## Changes during build

None yet.
