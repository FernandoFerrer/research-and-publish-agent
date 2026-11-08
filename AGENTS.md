# AGENTS.md

## Project
Build a weekly research and publishing system covering AI, science, healthcare, astronomy, and technology. Publish one main story plus brief highlights on GitHub Pages, then send an email with the link.

## Architecture
- **Dify** orchestrates three agents:
  1. **Research:** Find and rank recent public sources; trigger ingestion of selected documents and metadata into the vector database.
  2. **Validation:** Extract factual claims, retrieve evidence with RAG, and verify important claims against **at least two independent, trusted sources**. Request more research or reject unsupported claims.
  3. **Content:** Write cited articles and generate the static website using validated claims only.
- **Dagster** schedules weekly runs.
- Use deterministic code for ingestion, checks, deployment, and email. Keep feedback loops bounded; do not add agents or frameworks without a clear need.

## Development Rules
- Prefer simple, modular, testable code and minimal dependencies.
- Keep source URLs, publication dates, and evidence traceable. Two reports of the same study are not independent confirmation.
- Never invent facts or citations. Revalidate any new factual claims introduced during writing.
- Use only public, synthetic, or anonymized data. Never commit secrets, `.env` files, or private data; use environment variables.
- Check citations, links, site build, and accessibility before publishing. Send email only after successful deployment.
- Add focused tests for critical logic; fail clearly and safely when validation or publishing fails.
