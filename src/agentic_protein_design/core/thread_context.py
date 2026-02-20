from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Set


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _chats_dir(project_root: Optional[Path] = None) -> Path:
    base = project_root or _project_root()
    return base / "chats"


def _iter_thread_files(project_root: Optional[Path] = None) -> Iterable[Path]:
    chats = _chats_dir(project_root)
    if not chats.exists():
        return []
    return sorted(chats.glob("*.json"))


def resolve_thread_identifier(thread_ref: str) -> str:
    """
    Normalize a user-provided thread reference to raw thread id.

    Accepts values such as `<tag>_<thread_id>`, `<thread_id>`, or filenames
    ending with `.json`.

    Args:
        thread_ref: Raw thread reference string.

    Returns:
        Normalized thread id.
    """
    """
    Accept either:
    - raw thread_id (hex uuid string), or
    - thread file key/stem: f\"{tag}_{thread_id}\" (optionally with .json)
    and return normalized thread_id.
    """
    ref = str(thread_ref or "").strip()
    if not ref:
        return ref
    if ref.endswith(".json"):
        ref = ref[:-5]
    m = re.match(r"^(?P<tag>[A-Za-z0-9_]+)_(?P<tid>[0-9a-fA-F]{32})$", ref)
    if m:
        return m.group("tid").lower()
    return ref


def find_thread_file(thread_ref: str, project_root: Optional[Path] = None) -> Path:
    """
    Locate the on-disk chat thread JSON file from thread reference.

    Args:
        thread_ref: Thread id, tagged id, or JSON filename.
        project_root: Optional project root override.

    Returns:
        Path to matching thread JSON file.
    """
    """
    Find a thread JSON file by thread identifier or file key.
    """
    ref = str(thread_ref or "").strip()
    if not ref:
        raise FileNotFoundError("Thread reference is empty.")

    # Direct filename/stem match first, if caller passed '{tag}_{thread_id}'.
    ref_stem = ref[:-5] if ref.endswith(".json") else ref
    by_name = _chats_dir(project_root) / f"{ref_stem}.json"
    if by_name.exists():
        return by_name

    thread_id = resolve_thread_identifier(ref)
    for path in _iter_thread_files(project_root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if str(payload.get("thread_id", "")).strip() == thread_id:
            return path
    raise FileNotFoundError(f"Thread not found for reference={thread_ref}")


def load_thread_by_id(thread_ref: str, project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load a thread payload by thread reference.

    Args:
        thread_ref: Thread id, tagged id, or JSON filename.
        project_root: Optional project root override.

    Returns:
        Parsed thread payload dictionary.
    """
    path = find_thread_file(thread_ref, project_root)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["_thread_file"] = str(path)
    return payload


def _collect_path_candidates(value: str, root: Path) -> List[Path]:
    p = Path(value).expanduser()
    candidates: List[Path] = []
    if p.is_absolute():
        candidates.append(p)
    else:
        candidates.append((root / p).resolve())
        candidates.append(p.resolve())
    return candidates


def _walk_metadata_for_paths(metadata: Any, out: Set[str]) -> None:
    if isinstance(metadata, dict):
        for _, v in metadata.items():
            _walk_metadata_for_paths(v, out)
        return
    if isinstance(metadata, list):
        for v in metadata:
            _walk_metadata_for_paths(v, out)
        return
    if isinstance(metadata, str):
        text = metadata.strip()
        if not text:
            return
        if len(text) > 400:
            return
        if "\n" in text or "\r" in text:
            return
        if re.search(r"\s", text):
            return
        if re.search(r"^(?:/|\\./|\\.\\./|~\\/)", text) or re.search(
            r"\.(?:md|csv|json|txt|tsv|parquet|yaml|yml)$", text, flags=re.IGNORECASE
        ):
            out.add(text)


def extract_referenced_file_paths(
    thread_payload: Dict[str, Any],
    project_root: Optional[Path] = None,
) -> List[Path]:
    """
    Extract file-path references from thread messages and metadata.

    Args:
        thread: Parsed thread payload.
        project_root: Optional project root override.

    Returns:
        Deduplicated list of existing file paths referenced by the thread.
    """
    """
    Extract existing file paths referenced in thread metadata across all messages.
    """
    root = project_root or _project_root()
    raw_values: Set[str] = set()
    for msg in thread_payload.get("messages", []):
        _walk_metadata_for_paths(msg.get("metadata", {}), raw_values)

    resolved: List[Path] = []
    seen: Set[str] = set()
    for raw in sorted(raw_values):
        for candidate in _collect_path_candidates(raw, root):
            try:
                exists = candidate.exists()
            except OSError:
                continue
            if exists:
                key = str(candidate.resolve())
                if key not in seen:
                    seen.add(key)
                    resolved.append(candidate.resolve())
                break
    return resolved


def read_files_as_context(paths: List[Path], max_chars_per_file: int = 20000) -> Dict[str, str]:
    """
    Read referenced files into bounded text snippets for LLM context.

    Args:
        paths: List of files to read.
        max_chars_per_file: Per-file character limit.

    Returns:
        Mapping `{absolute_path: bounded_text}`.
    """
    out: Dict[str, str] = {}
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        compact = text[:max_chars_per_file]
        out[str(p)] = compact
    return out


def build_thread_context_bundle(
    thread_ref: str,
    *,
    project_root: Optional[Path] = None,
    include_referenced_files: bool = True,
    max_chars_per_file: int = 20000,
) -> Dict[str, Any]:
    """
    Build a structured context bundle from a prior chat thread.

    Args:
        thread_ref: Thread reference (`None` to disable).
        include_referenced_files: Whether to include referenced file contents.
        max_chars_per_file: Per-file context character limit.
        on_missing: Missing-thread behavior: `warn` or `raise`.
        project_root: Optional project root override.

    Returns:
        Context bundle including thread payload, text snippets, and errors.
    """
    """
    Generic accessor for historical thread context and referenced output traces.
    """
    payload = load_thread_by_id(thread_ref, project_root=project_root)
    paths: List[Path] = []
    file_texts: Dict[str, str] = {}
    if include_referenced_files:
        paths = extract_referenced_file_paths(payload, project_root=project_root)
        file_texts = read_files_as_context(paths, max_chars_per_file=max_chars_per_file)

    messages = payload.get("messages", [])
    latest_assistant = ""
    latest_user = ""
    for msg in reversed(messages):
        role = str(msg.get("role", ""))
        content = str(msg.get("content", ""))
        if not latest_assistant and role == "assistant":
            latest_assistant = content
        if not latest_user and role == "user":
            latest_user = content
        if latest_assistant and latest_user:
            break

    return {
        "thread_id": payload.get("thread_id", ""),
        "root_key": payload.get("root_key", ""),
        "llm_process_tag": payload.get("llm_process_tag", ""),
        "thread_file": payload.get("_thread_file", ""),
        "n_messages": len(messages),
        "latest_user_message": latest_user,
        "latest_assistant_message": latest_assistant,
        "referenced_files": [str(p) for p in paths],
        "referenced_file_contents": file_texts,
        "thread_payload": payload,
    }


def build_thread_context_text(
    thread_ref: Optional[str],
    *,
    include_referenced_files: bool = True,
    max_chars_per_file: int = 20000,
    on_missing: str = "warn",
) -> Dict[str, Any]:
    """
    Build concatenated plain-text context for prompt injection.

    Args:
        thread_ref: Thread reference (`None` to disable).
        include_referenced_files: Whether to include referenced file contents.
        max_chars_per_file: Per-file context character limit.
        on_missing: Missing-thread behavior: `warn` or `raise`.
        project_root: Optional project root override.

    Returns:
        Dict with `context_text` plus raw bundle/error metadata.
    """
    """
    Build a compact text context block from a prior thread, plus the raw bundle.

    Returns:
    - context_text: merged text for downstream prompts
    - context_bundle: parsed thread bundle or None
    - context_error: error message when missing/unreadable and on_missing != "raise"
    """
    ref = str(thread_ref or "").strip()
    if not ref:
        return {"context_text": "", "context_bundle": None, "context_error": ""}

    try:
        bundle = build_thread_context_bundle(
            ref,
            include_referenced_files=include_referenced_files,
            max_chars_per_file=max_chars_per_file,
        )
    except FileNotFoundError as exc:
        if on_missing == "raise":
            raise
        msg = str(exc)
        if on_missing == "warn":
            print(f"Skipping thread context: {msg}")
        return {"context_text": "", "context_bundle": None, "context_error": msg}

    file_blocks: List[str] = []
    for path, text in bundle.get("referenced_file_contents", {}).items():
        file_blocks.append(f"FILE: {path}\n{text}")

    context_text = "\n\n".join(
        [
            str(bundle.get("latest_user_message", "")),
            str(bundle.get("latest_assistant_message", "")),
            "\n\n".join(file_blocks),
        ]
    ).strip()
    return {"context_text": context_text, "context_bundle": bundle, "context_error": ""}
