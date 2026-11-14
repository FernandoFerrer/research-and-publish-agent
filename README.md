# Weekly Research and Knowledge Publishing Agent

A weekly research digest covering AI, science, healthcare, astronomy, and technology.

The Dify draft searches public sources, then uses research and validation agents to review the results. The Content agent generates a self-contained publication website, and a quality-check node checks its basic structure and source URLs. The workflow returns `index_html`, `website_file`, and `download_url` outputs. The validation agent compares search snippets; it does not independently verify claims. Open `download_url` on the same Dify site to download `index.html` for GitHub Pages; the signed URL is temporary. The digest links to search results; snippets, dates, and claims are not independently verified. Some topics may have no results.

The simplified workflow is saved in `difyctl/weekly-research-and-knowledge-publishing/mvp.yml`. It accepts an as-of date and a research window of 1–31 days. The draft does not automatically deploy the site, schedule weekly runs, or send email.

Built as a capstone project for the **Carnegie Mellon University Agentic AI Program**.

## Watch a test run

Run the draft with streaming enabled to see workflow and node events as they happen. Replace the date and window as needed:

```bash
difyctl test console_app workflow --app-id 7c62ae56-b3c5-4a47-a25f-c85281788561 --inputs '{"as_of_date":"2026-11-13","window_days":7}' --stream --json
```

Each line is a JSON event. `node_started` and `node_finished` show the agent stages and their inputs, outputs, status, and errors; `workflow_finished` contains the final outputs. Treat the trace as potentially sensitive because it includes inputs and results.
