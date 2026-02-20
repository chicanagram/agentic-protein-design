from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import uuid

def _project_root() -> Path:
    # Keep chat storage in the repository root (same behavior as pre-move module).
    return Path(__file__).resolve().parents[3]


def chats_dir(root_key: str, project_root: Optional[Path] = None) -> Path:
    """
    Resolve and create the repository-local chats directory.

    Args:
        root_key: Logical data root key (kept for API compatibility).
        project_root: Optional project root override.

    Returns:
        Path to `<project_root>/chats` (created if missing).
    """
    # root_key is kept for API compatibility with notebooks; storage is repo-local.
    _ = root_key
    base = project_root or _project_root()
    out = base / "chats"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _sanitize_llm_process_tag(llm_process_tag: Optional[str]) -> str:
    if not llm_process_tag:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", str(llm_process_tag).strip())
    cleaned = cleaned.strip("_")
    return cleaned


def _thread_filename(thread_id: str, llm_process_tag: Optional[str]) -> str:
    tag = _sanitize_llm_process_tag(llm_process_tag)
    if tag:
        return f"{tag}_{thread_id}.json"
    return f"{thread_id}.json"


def _candidate_thread_paths(
    root_key: str,
    thread_id: str,
    llm_process_tag: Optional[str],
    project_root: Optional[Path] = None,
) -> List[Path]:
    base = chats_dir(root_key, project_root)
    candidates: List[Path] = []

    # Preferred path for the current tag scheme.
    candidates.append(base / _thread_filename(thread_id, llm_process_tag))

    # Backward compatibility for legacy thread files with untagged naming.
    legacy = base / _thread_filename(thread_id, None)
    if legacy not in candidates:
        candidates.append(legacy)

    # Additional fallback: any tagged file ending in _<thread_id>.json
    for p in sorted(base.glob(f"*_{thread_id}.json")):
        if p not in candidates:
            candidates.append(p)
    return candidates


def thread_path(
    root_key: str,
    thread_id: str,
    project_root: Optional[Path] = None,
    llm_process_tag: Optional[str] = None,
) -> Path:
    """
    Build the canonical JSON path for a thread file.

    Args:
        root_key: Logical data root key.
        thread_id: Thread identifier.
        project_root: Optional project root override.
        llm_process_tag: Optional process tag prefix for filename namespacing.

    Returns:
        Absolute path to the thread JSON file.
    """
    return chats_dir(root_key, project_root) / _thread_filename(thread_id, llm_process_tag)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_thread(
    root_key: str,
    title: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None,
    llm_process_tag: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Create and persist a new empty chat thread.

    Args:
        root_key: Logical data root key.
        title: Human-readable thread title.
        metadata: Optional thread-level metadata payload.
        thread_id: Optional explicit thread identifier.
        llm_process_tag: Optional process tag used in filename and payload.
        project_root: Optional project root override.

    Returns:
        Serialized thread payload dict written to disk.
    """
    tid = thread_id or uuid.uuid4().hex
    normalized_tag = _sanitize_llm_process_tag(llm_process_tag)
    path = thread_path(
        root_key=root_key,
        thread_id=tid,
        project_root=project_root,
        llm_process_tag=normalized_tag,
    )

    if path.exists():
        raise FileExistsError(f"Thread already exists: {path}")

    now = _now_iso()
    payload: Dict[str, Any] = {
        "thread_id": tid,
        "root_key": root_key,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "llm_process_tag": normalized_tag,
        "metadata": metadata or {},
        "messages": [],
    }

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def load_thread(
    root_key: str,
    thread_id: str,
    project_root: Optional[Path] = None,
    llm_process_tag: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load a thread JSON payload from disk (with legacy filename fallback).

    Args:
        root_key: Logical data root key.
        thread_id: Thread identifier.
        project_root: Optional project root override.
        llm_process_tag: Optional preferred process tag for lookup.

    Returns:
        Parsed thread payload dictionary.
    """
    candidates = _candidate_thread_paths(
        root_key=root_key,
        thread_id=thread_id,
        llm_process_tag=llm_process_tag,
        project_root=project_root,
    )
    for path in candidates:
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not payload.get("llm_process_tag"):
                payload["llm_process_tag"] = _sanitize_llm_process_tag(llm_process_tag)
            return payload
    raise FileNotFoundError(f"Thread file not found for thread_id={thread_id}; searched: {[str(p) for p in candidates]}")


def save_thread(
    root_key: str,
    thread: Dict[str, Any],
    project_root: Optional[Path] = None,
    llm_process_tag: Optional[str] = None,
) -> None:
    """
    Persist a full thread payload back to disk and refresh `updated_at`.

    Args:
        root_key: Logical data root key.
        thread: Full thread payload dictionary.
        project_root: Optional project root override.
        llm_process_tag: Optional process tag override for filename selection.
    """
    tid = thread["thread_id"]
    effective_tag = _sanitize_llm_process_tag(llm_process_tag or thread.get("llm_process_tag"))
    path = thread_path(
        root_key=root_key,
        thread_id=tid,
        project_root=project_root,
        llm_process_tag=effective_tag,
    )
    thread["llm_process_tag"] = effective_tag
    thread["updated_at"] = _now_iso()
    path.write_text(json.dumps(thread, indent=2), encoding="utf-8")


def append_message(
    root_key: str,
    thread_id: str,
    role: str,
    content: str,
    source_notebook: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    project_root: Optional[Path] = None,
    llm_process_tag: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Append a single message to a thread and persist the updated thread.

    Args:
        root_key: Logical data root key.
        thread_id: Thread identifier.
        role: Message role, typically `user` or `assistant`.
        content: Message body text.
        source_notebook: Notebook/source label for traceability.
        metadata: Optional message metadata.
        project_root: Optional project root override.
        llm_process_tag: Optional process tag for thread routing.

    Returns:
        The message dictionary that was appended.
    """
    thread = load_thread(root_key, thread_id, project_root, llm_process_tag=llm_process_tag)

    message = {
        "message_id": uuid.uuid4().hex,
        "ts": _now_iso(),
        "role": role,
        "content": content,
        "source_notebook": source_notebook,
        "metadata": metadata or {},
    }
    thread.setdefault("messages", []).append(message)
    save_thread(root_key, thread, project_root, llm_process_tag=llm_process_tag)
    return message


def list_threads(
    root_key: str,
    project_root: Optional[Path] = None,
    llm_process_tag: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List thread summaries in reverse chronological order.

    Args:
        root_key: Logical data root key.
        project_root: Optional project root override.
        llm_process_tag: Optional tag filter (only matching threads returned).

    Returns:
        List of summary dictionaries with id/title/timestamps/message counts.
    """
    out: List[Dict[str, Any]] = []
    tag_filter = _sanitize_llm_process_tag(llm_process_tag)
    for p in sorted(chats_dir(root_key, project_root).glob("*.json")):
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            payload_tag = _sanitize_llm_process_tag(payload.get("llm_process_tag", ""))
            if tag_filter and payload_tag != tag_filter:
                continue
            out.append(
                {
                    "thread_id": payload.get("thread_id", p.stem),
                    "title": payload.get("title", ""),
                    "updated_at": payload.get("updated_at", ""),
                    "n_messages": len(payload.get("messages", [])),
                    "llm_process_tag": payload_tag,
                    "file": str(p),
                }
            )
        except json.JSONDecodeError:
            continue

    out.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return out
