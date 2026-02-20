from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List


def build_tools_registry(repo_root: Path) -> Dict[str, Any]:
    """Build a first-pass registry of public tool/workflow functions.

    Inputs:
        repo_root: Repository root path.

    Returns:
        Registry dictionary containing discovered function metadata.
    """
    scan_roots = [
        repo_root / "src/agentic_protein_design/core",
        repo_root / "src/agentic_protein_design/steps",
        repo_root / "tools",
    ]
    skip_prefixes = [
        repo_root / "tools/pythia/pythia",
        repo_root / "tools/__pycache__",
        repo_root / "src/agentic_protein_design/__pycache__",
    ]

    entries: List[Dict[str, Any]] = []
    for root in scan_roots:
        for path in sorted(root.rglob("*.py")):
            if any(str(path).startswith(str(prefix)) for prefix in skip_prefixes):
                continue
            if path.name == "__init__.py":
                continue
            rel = str(path.relative_to(repo_root))
            try:
                module_ast = ast.parse(path.read_text(encoding="utf-8"))
            except Exception:
                continue

            for node in module_ast.body:
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("_"):
                        continue
                    doc = ast.get_docstring(node) or ""
                    summary = (doc.strip().splitlines() or [""])[0].strip()
                    entries.append(
                        {
                            "module": rel.replace("/", ".").removesuffix(".py"),
                            "file": rel,
                            "function": node.name,
                            "summary": summary,
                            "has_docstring": bool(doc.strip()),
                            "lineno": int(node.lineno),
                        }
                    )

    entries.sort(key=lambda item: (item["module"], item["function"]))
    return {
        "version": "first-pass",
        "generated_from": [
            "src/agentic_protein_design/core",
            "src/agentic_protein_design/steps",
            "tools",
        ],
        "notes": "Public top-level functions intended for workflow composition and tooling.",
        "n_functions": len(entries),
        "functions": entries,
    }


def main() -> None:
    """CLI entrypoint for generating tools/config/tools_registry.first_pass.json."""
    repo_root = Path(__file__).resolve().parents[2]
    registry = build_tools_registry(repo_root)
    out_path = repo_root / "tools/config/tools_registry.first_pass.json"
    out_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Functions: {registry['n_functions']}")


if __name__ == "__main__":
    main()
