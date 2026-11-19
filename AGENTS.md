# AGENTS.md

## Goal
Build a simple, reliable weekly research and publishing system covering AI, science, healthcare, astronomy, and technology. Use public information only. Publish to GitHub Pages and notify by email.

## Current Status
- **Dify publishing workflow:** The published workflow researches public search results, reviews claims against snippets, and writes sourced content. A code-based evidence review and a condition stop insufficient content before website creation, hosting, and email; a skipped publication is a successful workflow completion. Approved content becomes a single-page HTML publication hosted on GitHub Pages, followed by email. The website agent can use the separate ComfyUI image-generation workflow. Testing mode can still overwrite the configured page and send email.
- **Models:** The workflow works with local Ollama models and can be configured for other commercial model providers supported by Dify.
- **Validation is limited:** Search snippets are not independent verification. RAG and verification against two independent trusted sources remain goals, not established behavior.
- **Knowledge-base storage:** Plans and Python node code explore source ingestion and deduplication. Integration and indexing checks remain outstanding; this is not part of the saved publishing workflow.
- **Dagster:** `dagster/definitions.py` schedules the published Dify workflow for Mondays at 07:00 Europe/Madrid with an eight-day window. It reports workflow status but does not enforce a global single-writer lock. Check the logged Dify run ID before retrying a timeout or lost stream.
- **Production safety copy:** `production.yml` captures the latest published workflow; its latest website-agent changes have not been verified end to end in this update. Email addresses are placeholders and must be configured in Dify. Later server changes are not automatically synchronized. See `README.md` for setup and local checks.

## Working Rules
- **Follow the human developer's instructions.** Do only the requested scope; ask before major changes.
- **Build one module at a time.** Deliver a working result before starting the next module; the human tests Dify workflows.
- **Use the installed `difyctl` skill** to build and inspect Dify workflows, knowledge bases, and integrations where supported. Read its instructions first; do not guess commands.
- **Dify workflow testing:** The human runs tests in Dify. Edit the workflow and correct issues based on their feedback; do not run workflow or node tests unless explicitly asked.
- **Use the `ponytail` skill** to keep solutions simple and remove unnecessary complexity.
- Prefer the simplest effective design: minimal agents, dependencies, resource use, and abstractions. Less is more.
- Keep retries bounded, sources traceable, and failures clear. Never invent facts or citations.
- Test relevant changes outside Dify workflows. Verify citations, links, and website output before publishing; send email only after successful deployment.
- Never commit secrets or private data. Use environment variables for credentials.

### Execution and Approval Policy

- Follow the human developer's instructions over project and skill guidance, within applicable higher-priority instructions.
- Never ignore the human developer's instructions or imply a requested change is complete without verifying the actual target state; report any failure or uncertainty clearly.
- Execute authorized requests end-to-end, including Dify server updates and integrations, without repeated approval or unnecessary intermediate steps.
- Use only checks needed for the requested change; fix failures autonomously and use a simpler supported route when a tool fails. Do not claim success if a technical blocker remains; report it and ask only for information needed to proceed.
- Ask for decisions only when requirements or authorization are unclear. Explicit authorization covers publishing and other requested actions.
- Minimize token use: read only what is needed, avoid repeated inspection, and keep plans and reports brief.
- Report the results concisely, including any limitations.

**Principle: Minimize bureaucracy, not quality.**

## Simplicity and Resource Efficiency

Follow the **Ponytail** philosophy: less is more. Prefer the simplest solution that works reliably.

- **No unnecessary files:** Remove unnecessary files as soon as possible.
- **Minimal repository:** Keep only essential source code, configuration, and reusable tests. Use temporary directories for intermediate artifacts.
- **Use existing tools:** Prefer `difyctl` capabilities over custom scripts or additional dependencies.
- **Avoid overengineering:** No unnecessary abstractions, frameworks, agents, or infrastructure.
- **Optimize token usage:** Read only relevant files. Avoid repeatedly loading full workflows, large files, or extensive documentation.
- **Incremental development:** Implement one module at a time. Keep each increment working and tested by the appropriate person.
- **Autonomous execution:** Complete authorized tasks without unnecessary approval requests. Always follow the human developer's instructions.
- **Concise reporting:** Report only what changed, test results, and any unresolved issues.

**Before creating any file or component, ask: Is it essential for the working solution? If not, do not create it.**
