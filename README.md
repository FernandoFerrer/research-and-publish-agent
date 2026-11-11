# Weekly Research and Knowledge Publishing Agent

An agentic system that researches recent developments in AI, science, healthcare, astronomy, and technology, then creates and publishes an engaging weekly website.

## How it works

1. **Research Agent:** Finds and ranks relevant developments, then adds sources to a vector knowledge base.
2. **Validation Agent:** Extracts key claims and checks them against at least two independent, trusted sources using RAG.
3. **Content Agent:** Writes the publication and generates the website from validated findings.
4. **Automated workflow:** Checks the output, publishes it to GitHub Pages, and sends an email with highlights.

## Technology

- **Dify:** Agent orchestration and RAG
- **Dagster:** Weekly scheduling
- **GitHub Pages:** Website hosting

Built as a capstone project for the **Carnegie Mellon University Agentic AI Program**.
