# 🔬 Weekly Research and Knowledge Publishing Agent

This Carnegie Mellon University Agentic AI Program capstone produces a weekly digest of public developments in AI, science, healthcare, astronomy, and technology. Dify researches and writes the issue, creates a single-page website, publishes it to GitHub Pages, and sends an email. Dagster can run the published workflow on a weekly schedule.

The saved workflows use local Ollama models and ComfyUI. Other Dify-supported model providers can be configured. Local model execution does not make the system offline: search, hosting, and email use external services.

## How it works

```text
Dagster (optional) → published Dify workflow
    → public search → research → snippet review → content editor
    → evidence gate → insufficient evidence: stop and return the review
                    → approved: create and check website
                                → GitHub Pages → email notification
```

1. **Research.** The workflow builds queries from an as-of date and research window, searches the five topics, and gathers arXiv and PubMed results. The research agent selects and summarizes public results with source links.
2. **Review and writing.** The validation agent compares the research with supplied snippets and paper results. The content editor receives that review and the original source data and writes structured stories. Its instructions allow developments up to 30 days old or of uncertain date when necessary.
3. **Evidence gate.** Code checks that the editor's output has `ready` status and at least one story with a nonempty headline, summary, and source URL. It can recover complete stories from a truncated response. If the gate fails, the workflow returns `skipped_content` and `review_decision` without creating a website, hosting it, or sending email. This is a successful Dify completion, so Dagster reports it as successful.
4. **Website.** The website agent turns approved content into a responsive HTML publication and can generate illustrations through the separate ComfyUI workflow. Its prompt requests one lead story and up to four supporting stories; it permits a plain-text reference for an individual story without a URL. Generated images are embedded, and a code node removes complete reasoning blocks, extracts the HTML, and checks its basic structure, image data and alt text, and link syntax. The checker accepts at most three generated images. The agent prompt itself has conflicting instructions: two to three images in one place and up to two in another.
5. **Publish.** After the website check passes, the workflow saves the HTML, creates a temporary download link, hosts the page on GitHub Pages, and sends email. A successful published run returns `public_url` and `download_url`.

## Limits and planned work

The validation agent reviews search snippets and paper metadata; it does not independently verify claims. The evidence gate checks for the presence of a source URL, not whether the link works or supports the story. The HTML check validates link syntax, not destinations or factual accuracy. Model instructions do not guarantee compliance, and generated content may omit or invent links. Review the claims, sources, links, and rendered page independently.

Retrieval-augmented generation, verification against two independent trusted sources, a bounded research feedback loop, and long-term memory remain goals. The repository contains separate knowledge-base ingestion and deduplication experiments, but they are not integrated into the saved publishing workflow.

## Repository

- [Main workflow](difyctl/weekly-research-and-knowledge-publishing/production.yml): a safety copy of the published workflow exported on 19 November 2026. The latest website-agent changes have not been verified end to end in this update. Email addresses are placeholders; later server changes are not automatically synchronized.
- [Image-generation workflow](difyctl/image-generation-workflow.yml): the published ComfyUI workflow used as a tool by the main workflow.
- [Dagster scheduler](dagster/definitions.py): the weekly job and schedule, with tests in `dagster/`.
- [Knowledge-base storage code](difyctl/weekly-research-and-knowledge-publishing/storage_nodes/): separate Python experiments and tests; adjacent plans describe outstanding integration checks.
- [Example publication](website_examples/16_11_2026.html): a historical output to inspect without running the workflow, not an evaluation of factual accuracy. `website_examples/` and `website_styless/` contain other visual references.

## 🚀 Set up the workflow

1. Obtain access to a Dify instance and import `production.yml` through its app import interface, or use the existing app if it is already installed. Importing a local file does not update the existing app automatically. Later server changes are not automatically reflected in the saved copy.
2. Configure local Ollama models or another Dify-supported commercial model provider, and select suitable models in the workflow. Configure its tools, including search, image generation, file tools, GitHub Pages hosting, and the email plugin. Supply provider credentials in Dify. In the email node, replace the placeholder recipient and reply-to addresses, and update the email body links if the hosting destination changes. Review the hosting target and recipients before running: a run can overwrite the page and send email.
3. In Dify, run the draft with an as-of date in `YYYY-MM-DD` format and a research window from 1 to 31 days (for example, `as_of_date: 2026-11-16` and `window_days: 7`). Review the output and independently check its sources, claims, links, and rendered page.
4. When the workflow is ready for scheduled use, publish it in Dify and create an app API key. Dagster calls the **published** version, not the draft.

> ⚠️ **Testing mode (placeholder website)** uses fewer search results and produces a clearly marked placeholder. It still calls models and the image tool, can replace the configured page, and can send email. Enable it only when those side effects are acceptable.

## 🎨 Set up image generation

The main workflow calls the **Image Generation Workflow**, which sends a text prompt to a local ComfyUI instance and returns generated image files.

1. Run ComfyUI where the Dify plugin can reach it. Make sure its model directories contain `z_image_turbo_bf16.safetensors` (diffusion model), `qwen_3_4b.safetensors` (text encoder), and `ae.safetensors` (VAE). The workflow enables model downloads, but the required files must be available to ComfyUI.
2. Import `difyctl/image-generation-workflow.yml` into Dify and install the ComfyUI plugin listed in its dependencies. Configure the plugin's ComfyUI server URL; if Dify runs in a container, use an address reachable from that container rather than assuming `localhost` points to the host. Supply any required credentials in Dify, not in the repository.
3. Publish the image workflow, then publish it as a workflow tool named `text_to_image`. Configure its prompt input `img_generation_prompt` and its `width` and `height` inputs (the workflow defaults to 1024 × 1024). In the main workflow, select the newly published tool for the agents that generate images: an imported workflow tool can have a different provider ID from the saved draft. Publish the main workflow again when ready for scheduled use.

The saved YAML is an export of the published image workflow; importing it creates a separate app and does not automatically update an existing one.

## 🗓️ Schedule weekly runs

Install Python 3 and uv, then from the project root:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r dagster/requirements.txt
cp .env.example .env
```

Edit `.env` and set `DIFY_WORKFLOW_ENDPOINT` to your Dify API base URL ending in `/v1`, and `DIFY_RESEARCH_WORKFLOW_API_KEY` to the published workflow's app API key. Existing environment variables take precedence. Keep `.env` and keys private.

```bash
dagster dev -f dagster/definitions.py
```

Open the local Dagster UI at the address printed by the command. Enable `weekly_schedule` if it is stopped, and keep Dagster and its daemon running. The schedule starts the workflow on Mondays at 07:00 Europe/Madrid, using that day's date and an eight-day window. Check the run log for its Dify run ID and final status.

> ⚠️ A timeout or lost stream fails the Dagster run even if Dify continues running. Check the logged run ID in Dify before retrying, and avoid concurrent workflow runs; the schedule does not enforce a global single-writer lock.

## ✅ Local checks

Run these from the project root. The Dagster tests require the dependencies installed above; the storage tests use Python's standard library.

```bash
python3 -m unittest discover -s dagster -p 'test*.py'
python3 -m unittest discover -s difyctl/weekly-research-and-knowledge-publishing/storage_nodes -p 'test*.py'
```

These checks do not exercise Dify, its plugins, GitHub Pages, or the published workflow.
