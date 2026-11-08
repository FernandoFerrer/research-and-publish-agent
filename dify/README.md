# Dify integration

An unpublished Workflow draft named `Weekly Research and Knowledge Publishing` exists in Dify (app ID `7c62ae56-b3c5-4a47-a25f-c85281788561`). Its current DSL is saved in `workflows/weekly-research.yml`; the skill working files are in `../difyctl/weekly-research/`. The user-created knowledge base is `weekly-research-database`.

The draft currently contains dated searches and candidate merging only. It has no knowledge-base ingestion or retrieval nodes, evidence validation, content generation, or publishable output. A one-topic draft run succeeded, but the five-topic slice is blocked because the configured DuckDuckGo plugin failed the astronomy node test with rate limiting, forbidden responses and CAPTCHA diagnostics. Do not use this draft as the completed research workflow.

The connected workspace has an active Ollama language model and `qwen3-embedding:0.6b` embedding model. The Knowledge API key in the ignored `.env` works from the host. The dataset is initialized, a public test document is retrievable, and a scoped proxy rule permits access to its API from Dify HTTP nodes. Workflow-triggered ingestion still needs an end-to-end test. Never store API keys or credentials in tracked files or workflow exports.

To test the incomplete draft (it may fail at the astronomy search):

```sh
difyctl test console_app workflow --app-id 7c62ae56-b3c5-4a47-a25f-c85281788561 --inputs '{"as_of_date":"2026-11-08","window_days":7}' --json
```

To restore the reviewed draft, create a Workflow app in the target workspace, export its blank draft to obtain its draft hash, and follow the installed difyctl skill's `import console_app dsl` procedure using `workflows/weekly-research.yml`. Reconfigure the installed search plugin and knowledge base as needed. The saved draft is not production-ready.
