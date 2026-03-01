from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Optional


def resolve_repo_root(module_file: str) -> Path:
    """Resolve the repository root from a module under src/agentic_protein_design."""
    return Path(module_file).resolve().parents[3]


def load_openai_api_key_from_project_config() -> bool:
    """
    Populate OPENAI_API_KEY from project_config.local_api_keys when available.

    Returns:
        True if OPENAI_API_KEY is set after loading, else False.
    """
    if os.environ.get("OPENAI_API_KEY"):
        return True

    try:
        from project_config.local_api_keys import OPENAI_API_KEY
    except Exception:
        return False

    key = str(OPENAI_API_KEY or "").strip()
    if key and key != "REPLACE_WITH_YOUR_OPENAI_API_KEY":
        os.environ["OPENAI_API_KEY"] = key
        return True
    return False


def print_run_summary(result: Any, *, keys: Optional[Iterable[str]] = None) -> None:
    """
    Print a compact JSON summary for IDE runs.

    Complex objects such as DataFrames are summarized instead of being expanded.
    """

    def _to_jsonable(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {str(k): _to_jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [_to_jsonable(v) for v in value]
        if hasattr(value, "shape"):
            shape = getattr(value, "shape", None)
            return f"<{type(value).__name__} shape={shape}>"
        return repr(value)

    payload = result
    if keys is not None and isinstance(result, dict):
        payload = {str(key): result.get(key) for key in keys}

    print(json.dumps(_to_jsonable(payload), indent=2, ensure_ascii=True))
