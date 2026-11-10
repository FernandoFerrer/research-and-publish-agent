"""Build self-contained Python sources for Dify Code nodes."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CONFIGS = {
    "queries": (
        ("search_queries.py",),
        '''def main(as_of_date, window_days):\n    if type(window_days) is float and window_days.is_integer():\n        window_days = int(window_days)\n    queries = build_search_queries(as_of_date, window_days)\n    return {"ai": queries["AI"], "science": queries["science"], "healthcare": queries["healthcare"], "astronomy": queries["astronomy"], "technology": queries["technology"]}\n''',
    ),
    "discovery": (
        ("source_identity.py", "search_candidates.py"),
        '''def main(ai, science, healthcare, astronomy, technology):\n    return {"candidates": normalize_results({"AI": ai, "science": science, "healthcare": healthcare, "astronomy": astronomy, "technology": technology})}\n''',
    ),
    "selection": (
        ("source_identity.py", "search_candidates.py"),
        '''import json\ndef main(candidates, selection_json):\n    return {"selected": select_candidates(candidates, json.loads(selection_json))}\n''',
    ),
    "ingestion": (
        ("source_identity.py", "ingestion_payload.py"),
        '''def main(source):\n    return {"document": document_payload(source)}\n''',
    ),
    "metadata": (
        ("source_identity.py", "ingestion_payload.py"),
        '''def main(document_id, source, definitions):\n    return {"metadata": metadata_payload(document_id, source, definitions)}\n''',
    ),
    "identity": (
        ("source_identity.py",),
        '''def main(url, doi, existing):\n    return {"duplicate": int(is_duplicate(url, doi, existing))}\n''',
    ),
    "source_metadata": (
        ("source_metadata.py",),
        '''def main(selected, text, proposed_json, as_of_date, window_days, retrieval_date):\n    if type(window_days) is float and window_days.is_integer():\n        window_days = int(window_days)\n    return {"source": check_source(selected, text, proposed_json, as_of_date, window_days, retrieval_date)}\n''',
    ),
    "document_page": (
        ("document_page.py",),
        '''def main(page, expected_page):\n    result = parse_document_page(page, int(expected_page))\n    return {"sources": result["sources"], "next_page": result["next_page"] or 0}\n''',
    ),
    "evidence": (
        ("retrieval_adapter.py", "evidence_gate.py"),
        '''def main(claim, retrieved):\n    return {"decision": validate_claim(claim, adapt_retrieval(retrieved))}\n''',
    ),
    "content": (
        ("retrieval_adapter.py", "evidence_gate.py", "render_content.py"),
        '''def main(claims, retrieved, selection, as_of_date):\n    return {"content": render_content(claims, adapt_retrieval(retrieved), selection, as_of_date)}\n''',
    ),
}


def bundle(name):
    filenames, wrapper = CONFIGS[name]
    local_names = {Path(filename).stem for filename in filenames}
    parts = []
    for filename in filenames:
        module = ast.parse((ROOT / filename).read_text(encoding="utf-8"), filename=filename)
        module.body = [node for node in module.body if not (
            isinstance(node, ast.ImportFrom) and node.module in local_names)]
        parts.append(ast.unparse(module))
    result = "\n\n".join(parts + [wrapper])
    compile(result, "<dify-code-node>", "exec")
    return result
