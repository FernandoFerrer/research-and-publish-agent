# AGENTS.md

## Goal
Build a simple, reliable weekly research and publishing system covering AI, science, healthcare, astronomy, and technology. Use public information only. Publish to GitHub Pages and notify by email.

## Architecture
- **Dify** coordinates three agents:
  1. **Research:** Find and rank sources; ingest relevant documents into the knowledge base.
  2. **Validation:** Extract claims, use RAG, and verify important claims with at least two independent, trusted sources. Reject unsupported claims.
  3. **Content:** Write cited articles and generate the static website using validated claims only.
- **Dagster** triggers weekly runs. Use deterministic steps for ingestion, checks, deployment, and email.

## Working Rules
- **Follow the human developer's instructions.** Do only the requested scope; ask before major changes.
- **Build one module at a time.** Deliver a working, tested result before starting the next module.
- **Use the installed `difyctl` skill** to build, inspect, and test Dify workflows, knowledge bases, and integrations where supported. Read its instructions first; do not guess commands.
- **Use the `ponytail` skill** to keep solutions simple and remove unnecessary complexity.
- Prefer the simplest effective design: minimal agents, dependencies, resource use, and abstractions. Less is more.
- Keep retries bounded, sources traceable, and failures clear. Never invent facts or citations.
- Test relevant changes. Verify citations, links, and website output before publishing; send email only after successful deployment.
- Never commit secrets or private data. Use environment variables for credentials.

### Execution and Approval Policy

- Follow the human developer's instructions as the highest priority within the project.
- Once a task is authorized, execute it end-to-end without requesting repeated approval.
- Create specifications and plans internally when needed, but keep them concise.
- For small changes, skip unnecessary planning and proceed directly.
- Implement one module at a time, always maintaining a working solution.
- Test changes and correct errors autonomously.
- Request additional approval only for ambiguous requirements, destructive operations, publishing, or changes outside the authorized scope.
- Report the results concisely, including any limitations.

**Principle: Minimize bureaucracy, not quality.**

## Simplicity and Resource Efficiency

Follow the **Ponytail** philosophy: less is more. Prefer the simplest solution that works reliably.

- **No unnecessary files:** Remove unnecessary files as soon as possible.
- **Minimal repository:** Keep only essential source code, configuration, and reusable tests. Use temporary directories for intermediate artifacts.
- **Use existing tools:** Prefer `difyctl` capabilities over custom scripts or additional dependencies.
- **Avoid overengineering:** No unnecessary abstractions, frameworks, agents, or infrastructure.
- **Optimize token usage:** Read only relevant files. Avoid repeatedly loading full workflows, large files, or extensive documentation.
- **Incremental development:** Implement one module at a time. Keep each increment working and tested.
- **Autonomous execution:** Complete authorized tasks without unnecessary approval requests. Always follow the human developer's instructions.
- **Concise reporting:** Report only what changed, test results, and any unresolved issues.

**Before creating any file or component, ask: Is it essential for the working solution? If not, do not create it.**
