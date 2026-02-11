from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

def _project_root() -> Path:
    return Path(__file__).resolve().parent


def chats_dir(root_key: str, project_root: Optional[Path] = None) -> Path:
    # root_key is kept for API compatibility with notebooks; storage is repo-local.
    _ = root_key
    base = project_root or _project_root()
    out = base / "chats"
    out.mkdir(parents=True, exist_ok=True)
    return out


def thread_path(root_key: str, thread_id: str, project_root: Optional[Path] = None) -> Path:
    return chats_dir(root_key, project_root) / f"{thread_id}.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_thread(
    root_key: str,
    title: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> Dict[str, Any]:
    tid = thread_id or uuid.uuid4().hex
    path = thread_path(root_key, tid, project_root)

    if path.exists():
        raise FileExistsError(f"Thread already exists: {path}")

    now = _now_iso()
    payload: Dict[str, Any] = {
        "thread_id": tid,
        "root_key": root_key,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "metadata": metadata or {},
        "messages": [],
    }

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def load_thread(root_key: str, thread_id: str, project_root: Optional[Path] = None) -> Dict[str, Any]:
    path = thread_path(root_key, thread_id, project_root)
    if not path.exists():
        raise FileNotFoundError(f"Thread file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_thread(
    root_key: str,
    thread: Dict[str, Any],
    project_root: Optional[Path] = None,
) -> None:
    tid = thread["thread_id"]
    path = thread_path(root_key, tid, project_root)
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
) -> Dict[str, Any]:
    thread = load_thread(root_key, thread_id, project_root)

    message = {
        "message_id": uuid.uuid4().hex,
        "ts": _now_iso(),
        "role": role,
        "content": content,
        "source_notebook": source_notebook,
        "metadata": metadata or {},
    }
    thread.setdefault("messages", []).append(message)
    save_thread(root_key, thread, project_root)
    return message


def list_threads(root_key: str, project_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in sorted(chats_dir(root_key, project_root).glob("*.json")):
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            out.append(
                {
                    "thread_id": payload.get("thread_id", p.stem),
                    "title": payload.get("title", ""),
                    "updated_at": payload.get("updated_at", ""),
                    "n_messages": len(payload.get("messages", [])),
                    "file": str(p),
                }
            )
        except json.JSONDecodeError:
            continue

    out.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return out
