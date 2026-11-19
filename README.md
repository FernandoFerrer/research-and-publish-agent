# 🔬 Weekly Research and Knowledge Publishing Agent

This capstone project for the **Carnegie Mellon University Agentic AI Program** aims to produce a weekly digest of public research about AI, science, healthcare, astronomy, and technology. Dify runs the research and website-generation workflow; Dagster can start its published version on a schedule. The workflow works with local Ollama models and can also be configured to use commercial model providers supported by Dify.

The project was created using only local LLMs and local computing resources, with zero tokens consumed from consumer-grade LLM providers. The saved workflow uses local models through Ollama, and ComfyUI runs image generation locally. Dify-supported commercial model providers are optional; using one would consume that provider's tokens.

Local model execution does not mean the whole workflow is offline: it searches public internet sources, publishes to GitHub Pages, and sends email through configured services. Dify orchestrates the workflow, Ollama serves the language models, ComfyUI generates images, and Dagster optionally schedules runs.

The main workflow brings together five research and publishing stages:

- 🔎 **Research agent** selects public results across the five topics and summarizes their supplied snippets with exact source links.
- 🔍 **Validation agent** compares the research with supplied results, removes unsupported claims and links, and labels snippet-based material as unverified.
- ✍️ **Content editor** writes articles from the research agent’s supplied evidence, using its source links and distinguishing preliminary research from established results. Its prompt permits developments up to 30 days old when necessary; it does not conduct additional searches.
- 🛑 **Evidence review** checks whether the content is ready to publish. An LLM assesses completeness and sources, and a separate condition blocks content containing `insufficient_evidence`.
- 🎨 **Website Creation Agent** turns the editorial content into a single-page HTML publication, preserving its factual content, uncertainty and source links. It can use the ComfyUI image-generation tool to create illustrations.

## 📍 Current status

The workflow searches public sources across five topics, uses research and validation agents to review and compare search results, and generates a single-page website with links to those results. The validation agent works with search snippets. Its review is not passed to the content editor, which receives the research agent’s output directly.

When the evidence review does not approve the content, the workflow ends with the content in `skipped_content`, before website creation, hosting or email. An approved issue is hosted on GitHub Pages, then the email tool notifies recipients. That branch returns the public page URL and a temporary download URL that can be opened on the same Dify site. A skipped publication is a successful workflow completion, so Dagster reports it as successful. The LLM review can make mistakes and does not independently verify sources. Separate development work explores storing research sources in a knowledge base.

## 📋 Capstone design checklist

- [x] Research recent public developments in AI, science, healthcare, astronomy and technology.
- [x] Evaluate search results and review claims against the supplied snippets.
- [ ] Retrieve additional evidence and independently validate important claims.
- [x] Generate a weekly web publication with written content, source links and image-generation support.
- [x] Check the generated HTML structure and source links before publishing.
- [x] Stop before website creation and email when the evidence review does not approve the content.
- [x] Verify the website for technical errors and inconsistencies.
- [x] Publish to GitHub Pages and send an email notification after hosting.
- [x] Pass research and generated content between workflow stages during a run.
- [ ] Add a bounded feedback loop that uses observations to request additional research and correct problems.
- [ ] Optionally retain published topics, sources and reader preferences between runs, including likes.
- [x] Schedule weekly runs.

Independent validation and long-term memory remain goals; snippet review does not establish that claims are verified.

## 🛡️ Safety checkpoint

Checked items are implemented in the saved workflow or scheduler; unchecked items are incomplete or not yet verified. Prompts and snippet checks alone do not guarantee compliance.

- [x] Search public results and instruct agents to treat retrieved text as untrusted data.
- [x] Check generated HTML structure and source links before creating the publication.
- [x] Log scheduled workflow progress and failures, including the Dify run ID.
- [x] Instruct the content agent to prioritize credible, relevant sources and preserve publication dates.
- [ ] Verify important claims against two independent trusted sources; the validation agent reviews search snippets, which do not independently verify claims.
- [ ] Use RAG to retrieve supporting evidence and preserve source references.
- [ ] Generate only from independently validated findings; the content editor uses the supplied research rather than independently validated findings.
- [x] Apply editorial checks for factual consistency, completeness and clarity.


These targets will be refined through evaluation. 

## 🤝 Agent coordination plan

Checked items are present in the saved workflow or scheduler; agent instructions are not guarantees of the resulting output.

- [x] Search public sources and select useful results across the five research topics.
- [x] Review selected research against supplied search results. The content editor receives the research agent output directly.
- [ ] Download research documents and ingest their contents, embeddings and metadata into a vector database.
- [ ] Retrieve evidence with RAG and verify important claims against two independent trusted sources.
- [ ] Request additional research from the validation stage when evidence is insufficient, with a bounded feedback loop.
- [x] Generate a lead article, supporting articles and source links, then create a visual concept and website.
- [x] Check website structure and source links, deploy to GitHub Pages, and run the email notification after hosting.
- [x] Schedule the published workflow weekly with Dagster.

The saved workflow has a separate website creation agent in addition to the research, validation and content stages. Its validation is based on snippets; independent verification and knowledge-base integration remain goals.

## 📂 What is in this repository

- `difyctl/weekly-research-and-knowledge-publishing/production.yml`: safety copy of the latest tested published workflow, exported on 19 November 2026. Recipient and reply-to addresses are placeholders. The export is not automatically synchronized with the server.
- `difyctl/image-generation-workflow.yml`: the published image-generation workflow used as a tool by the main workflow.
- `dagster/`: the weekly scheduler and its tests.
- `difyctl/weekly-research-and-knowledge-publishing/storage_nodes/`: Python code and tests for the separate knowledge-base storage work. The adjacent plans describe its intended behavior and outstanding integration checks.
- `website_examples/` and `website_styless/`: visual examples and design references, not the deployed website.

## 🚀 Set up the workflow

1. Obtain access to a Dify instance and import `production.yml` through its app import interface, or use the existing app if it is already installed. Importing a local file does not update the existing app automatically. Later server changes are not automatically reflected in the saved copy.
2. Configure local Ollama models or another Dify-supported commercial model provider, and select suitable models in the workflow. Configure its tools, including search, image generation, file tools, GitHub Pages hosting, and the email plugin. Supply provider credentials in Dify. In the email node, replace the placeholder recipient and reply-to addresses, and update the email body links if the hosting destination changes. Review the hosting target and recipients before running: a run can overwrite the page and send email.
3. In Dify, run the draft with an as-of date in `YYYY-MM-DD` format and a research window from 1 to 31 days. Review the output and independently check its sources, claims, links, and rendered page.
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

Open the local Dagster UI at the address printed by the command. Enable `weekly_schedule` if it is stopped, and keep Dagster and its daemon running. The schedule starts the workflow on Mondays at 07:00 Europe/Madrid, using that day's date and a seven-day window. Check the run log for its Dify run ID and final status.

> ⚠️ A timeout or lost stream fails the Dagster run even if Dify continues running. Check the logged run ID in Dify before retrying, and avoid concurrent workflow runs; the schedule does not enforce a global single-writer lock.

## ✅ Local checks

Run these from the project root. The Dagster tests require the dependencies installed above; the storage tests use Python's standard library.

```bash
python3 -m unittest discover -s dagster -p 'test*.py'
python3 -m unittest discover -s difyctl/weekly-research-and-knowledge-publishing/storage_nodes -p 'test*.py'
```

These checks do not exercise Dify, its plugins, GitHub Pages, or the published workflow.
