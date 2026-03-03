from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from agentic_protein_design.core.chat_store import append_message, load_thread


def resolve_repo_root(module_file: str) -> Path:
    """
    Resolve the repository root from a module path under `src/agentic_protein_design`.
    """
    return Path(module_file).resolve().parents[3]


def load_openai_api_key_from_project_config(env_var: str = "OPENAI_API_KEY") -> bool:
    """
    Populate the OpenAI API key from `project_config.local_api_keys` when available.

    Returns:
        True if the environment variable is set after attempting to load it.
    """
    if os.environ.get(env_var):
        return True

    if env_var != "OPENAI_API_KEY":
        return False

    try:
        from project_config.local_api_keys import OPENAI_API_KEY
    except Exception:
        return False

    key = str(OPENAI_API_KEY or "").strip()
    if key and key != "REPLACE_WITH_YOUR_OPENAI_API_KEY":
        os.environ[env_var] = key
        return True
    return False


def get_openai_client(
    *,
    env_var: str = "OPENAI_API_KEY",
    missing_package_message: str = "The `openai` package is required for LLM operations.",
    missing_key_message: str = "OPENAI_API_KEY is not set. Export it before running LLM operations.",
) -> Any:
    """
    Create an OpenAI client with consistent dependency and key checks.

    Args:
        env_var: Environment variable name that stores API key.
        missing_package_message: Error text if `openai` is not installed.
        missing_key_message: Error text if the API key is unavailable.

    Returns:
        Instantiated `openai.OpenAI` client object.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(missing_package_message) from exc

    load_openai_api_key_from_project_config(env_var=env_var)

    if not os.getenv(env_var):
        raise RuntimeError(missing_key_message)
    return OpenAI()


def table_records(df: pd.DataFrame, max_rows: int) -> List[Dict[str, Any]]:
    """
    Convert a DataFrame into JSON-serializable row records with row cap.

    Args:
        df: Input DataFrame.
        max_rows: Maximum number of rows to include.

    Returns:
        List of dictionaries suitable for LLM payload serialization.
    """
    if df.empty:
        return []
    subset = df.head(max_rows).copy()
    subset = subset.where(pd.notnull(subset), None)
    return subset.to_dict(orient="records")


def summarize_compact_text(text: str, max_chars: int = 1000) -> str:
    """
    Collapse whitespace and truncate text for compact logging/metadata.

    Args:
        text: Input text string.
        max_chars: Maximum output length.

    Returns:
        Normalized summary string.
    """
    compact = " ".join((text or "").split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def save_text_output(text: str, output_dir: Path, filename: str) -> Path:
    """
    Save a text artifact to disk.

    Args:
        text: Text content to write.
        output_dir: Destination directory.
        filename: Output filename.

    Returns:
        Absolute path of the written file.
    """
    out_path = output_dir / filename
    out_path.write_text(text, encoding="utf-8")
    return out_path


def print_run_summary(result: Any, *, keys: Optional[Iterable[str]] = None) -> None:
    """
    Print a compact JSON summary for local IDE/script runs.

    Complex objects such as DataFrames are summarized instead of expanded.
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


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def save_text_output_with_assets_copy(
    text: str,
    output_dir: Path,
    filename: str,
    *,
    assets_filename: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> Path:
    """
    Save a text artifact to output_dir and mirror a copy to <repo>/assets for easy repo viewing.
    """
    out_path = save_text_output(text, output_dir, filename)
    root = project_root or _project_root()
    assets_dir = root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    mirror_name = assets_filename or filename
    (assets_dir / mirror_name).write_text(text, encoding="utf-8")
    return out_path


def persist_thread_message(
    *,
    root_key: str,
    thread_id: str,
    llm_process_tag: str,
    source_notebook: str,
    content: str,
    metadata: Dict[str, Any],
) -> str:
    """
    Append a message to thread history and return new thread timestamp.

    Args:
        root_key: Logical data root key.
        thread_id: Thread identifier.
        llm_process_tag: Process tag for namespaced thread storage.
        source_notebook: Source label for traceability.
        content: Message body text.
        metadata: Structured metadata payload.

    Returns:
        Updated thread timestamp (`updated_at` ISO string).
    """
    append_message(
        root_key=root_key,
        thread_id=thread_id,
        role="user",
        content=content,
        source_notebook=source_notebook,
        llm_process_tag=llm_process_tag,
        metadata=metadata,
    )
    return load_thread(root_key, thread_id, llm_process_tag=llm_process_tag)["updated_at"]
