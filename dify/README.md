# Dify integration

A Workflow named `Weekly Research and Knowledge Publishing` exists in Dify (app ID `7c62ae56-b3c5-4a47-a25f-c85281788561`) and has a published research-only version. `../difyctl/weekly-research/app.yml` is the saved draft export. The user-created knowledge base is `weekly-research-database`.

The current draft searches, selects sources with Ollama, fetches them and checks their metadata. If no source is suitable, the selection is empty. Sources without verifiable metadata are returned as rejected. If a fetch or model call fails, the corresponding entry in `retrieved_sources` is null; it matches the same position in `selected_sources`. An accepted source is not a validated claim. There are no knowledge-base ingestion or retrieval nodes, evidence validation, content generation, or publishable output. The complete agent workflow is not yet implemented.

The connected workspace has an active Ollama language model and `qwen3-embedding:0.6b` embedding model. The Knowledge API key in the ignored `.env` works from the host. The dataset is initialized, a public test document is retrievable, and a scoped proxy rule permits access to its API from Dify HTTP nodes. Workflow-triggered ingestion still needs an end-to-end test. Never store API keys or credentials in tracked files or workflow exports.

To test the incomplete draft:

```sh
difyctl test console_app workflow --app-id 7c62ae56-b3c5-4a47-a25f-c85281788561 --inputs '{"as_of_date":"2026-11-10","window_days":7}' --json
```

To restore the reviewed draft, create a Workflow app in the target workspace, export its blank draft to obtain its draft hash, and follow the installed difyctl skill's `import console_app dsl` procedure using `../difyctl/weekly-research/app.yml`. Reconfigure the installed search plugin and knowledge base as needed. The saved draft is not production-ready.
