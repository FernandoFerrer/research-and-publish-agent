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
