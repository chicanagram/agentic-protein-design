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


def _is_markdown_path(value: str) -> bool:
    text = str(value or "").strip()
    return bool(text and text.lower().endswith(".md") and not re.search(r"[\n\r]", text))


def _is_artifact_path(value: str, allowed_exts: Set[str]) -> bool:
    text = str(value or "").strip()
    if not text or re.search(r"[\n\r]", text):
        return False
    suffix = Path(text).suffix.lower()
    return suffix in allowed_exts


def _walk_metadata_for_markdown_paths(metadata: Any, out: Set[str]) -> None:
    """
    Collect markdown artifact paths from nested metadata structures.
    """
    if isinstance(metadata, dict):
        for k, v in metadata.items():
            key = str(k).strip().lower()
            if isinstance(v, str):
                candidate = v.strip()
                if _is_markdown_path(candidate) and key.endswith("_path"):
                    out.add(candidate)
            _walk_metadata_for_markdown_paths(v, out)
        return
    if isinstance(metadata, list):
        for v in metadata:
            _walk_metadata_for_markdown_paths(v, out)
        return
    if isinstance(metadata, str):
        text = metadata.strip()
        if _is_markdown_path(text):
            out.add(text)


def _walk_metadata_for_artifact_paths(metadata: Any, out: Set[str], allowed_exts: Set[str]) -> None:
    if isinstance(metadata, dict):
        for k, v in metadata.items():
            key = str(k).strip().lower()
            if isinstance(v, str):
                candidate = v.strip()
                if key.endswith("_path") and _is_artifact_path(candidate, allowed_exts):
                    out.add(candidate)
            _walk_metadata_for_artifact_paths(v, out, allowed_exts)
        return
    if isinstance(metadata, list):
        for v in metadata:
            _walk_metadata_for_artifact_paths(v, out, allowed_exts)
        return
    if isinstance(metadata, str):
        text = metadata.strip()
        if _is_artifact_path(text, allowed_exts):
            out.add(text)


def extract_generated_markdown_paths(
    thread_payload: Dict[str, Any],
    project_root: Optional[Path] = None,
) -> List[Path]:
    """
    Extract generated markdown output paths from thread message metadata.

    Args:
        thread_payload: Parsed thread payload.
        project_root: Optional project root override.

    Returns:
        Deduplicated list of existing markdown files, preferring latest message metadata.
    """
    root = project_root or _project_root()
    messages = list(thread_payload.get("messages", []))
    raw_values: Set[str] = set()
    for msg in reversed(messages):
        candidates: Set[str] = set()
        _walk_metadata_for_markdown_paths(msg.get("metadata", {}), candidates)
        if candidates:
            raw_values = candidates
            break

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


def extract_metadata_artifact_paths(
    thread_payload: Dict[str, Any],
    project_root: Optional[Path] = None,
    allowed_extensions: Optional[List[str]] = None,
) -> List[Path]:
    """
    Extract existing artifact paths (for example .md/.json) from latest message metadata.
    """
    root = project_root or _project_root()
    allowed_exts = {
        str(ext).strip().lower() if str(ext).startswith(".") else f".{str(ext).strip().lower()}"
        for ext in (allowed_extensions or [".md", ".json"])
        if str(ext).strip()
    }
    messages = list(thread_payload.get("messages", []))
    raw_values: Set[str] = set()
    for msg in reversed(messages):
        candidates: Set[str] = set()
        _walk_metadata_for_artifact_paths(msg.get("metadata", {}), candidates, allowed_exts)
        if candidates:
            raw_values = candidates
            break

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


def read_files_as_context(paths: List[Path], max_chars_per_file: int = 40000) -> Dict[str, str]:
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
    max_chars_per_file: int = 40000,
    json_artifact_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a context bundle from a prior chat thread.

    Args:
        thread_ref: Thread id, tagged id, or thread filename stem.
        include_referenced_files: Whether to include generated markdown file contents.
        max_chars_per_file: Per-file context character limit.
        project_root: Optional project root override.

    Returns:
        Context bundle including thread payload and generated markdown snippets.
    """
    payload = load_thread_by_id(thread_ref, project_root=project_root)
    paths: List[Path] = []
    file_texts: Dict[str, str] = {}
    if include_referenced_files:
        paths = extract_generated_markdown_paths(payload, project_root=project_root)
        file_texts = read_files_as_context(paths, max_chars_per_file=max_chars_per_file)
    artifact_paths = extract_metadata_artifact_paths(payload, project_root=project_root)
    requested_json_names = {str(x).strip().lower() for x in (json_artifact_names or []) if str(x).strip()}
    json_objects: Dict[str, Any] = {}
    if requested_json_names:
        for p in artifact_paths:
            if p.suffix.lower() != ".json":
                continue
            stem = p.stem.lower()
            name = p.name.lower()
            if stem not in requested_json_names and name not in requested_json_names:
                continue
            try:
                parsed = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            json_objects[stem] = parsed

    return {
        "thread_id": payload.get("thread_id", ""),
        "root_key": payload.get("root_key", ""),
        "llm_process_tag": payload.get("llm_process_tag", ""),
        "thread_file": payload.get("_thread_file", ""),
        "n_messages": len(payload.get("messages", [])),
        "referenced_files": [str(p) for p in paths],
        "referenced_file_contents": file_texts,
        "referenced_artifact_paths": [str(p) for p in artifact_paths],
        "referenced_json_objects": json_objects,
        "thread_payload": payload,
    }


def build_thread_context_text(
    thread_ref: Optional[str],
    *,
    include_referenced_files: bool = True,
    max_chars_per_file: int = 40000,
    on_missing: str = "warn",
    json_artifact_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build plain-text context from generated markdown artifacts only.

    Args:
        thread_ref: Thread reference (`None` to disable).
        include_referenced_files: Whether to include generated markdown file contents.
        max_chars_per_file: Per-file context character limit.
        on_missing: Missing-thread behavior: `warn` or `raise`.

    Returns:
        Dict with `context_text` plus raw bundle/error metadata.
    """
    ref = str(thread_ref or "").strip()
    if not ref:
        return {"context_text": "", "context_bundle": None, "context_error": ""}

    try:
        bundle = build_thread_context_bundle(
            ref,
            include_referenced_files=include_referenced_files,
            max_chars_per_file=max_chars_per_file,
            json_artifact_names=json_artifact_names,
        )
    except FileNotFoundError as exc:
        if on_missing == "raise":
            raise
        msg = str(exc)
        if on_missing == "warn":
            print(f"Skipping thread context: {msg}")
        return {"context_text": "", "context_bundle": None, "context_error": msg}

    file_blocks = [
        f"FILE: {path}\n{text}"
        for path, text in bundle.get("referenced_file_contents", {}).items()
    ]
    context_text = "\n\n".join(file_blocks).strip()
    return {"context_text": context_text, "context_bundle": bundle, "context_error": ""}


def filter_context_text_by_keyword(context_text: str, keyword: str, *, fallback_chars: int = 12000) -> str:
    """
    Filter a context block down to paragraphs/lines containing a keyword.
    """
    text = str(context_text or "").strip()
    if not text:
        return ""
    needle = str(keyword or "").strip()
    if not needle:
        return text

    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    matches = [block for block in blocks if needle.lower() in block.lower()]
    if matches:
        return "\n\n".join(matches)

    lines = [line for line in text.splitlines() if needle.lower() in line.lower()]
    if lines:
        return "\n".join(lines)
    return text[:fallback_chars]


def load_optional_thread_context(
    thread_ref: Optional[str],
    *,
    include_referenced_files: bool = True,
    max_chars_per_file: int = 40000,
    on_missing: str = "warn",
    filter_keyword: str = "",
    json_artifact_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Load optional prior-thread context and optionally add a keyword-filtered view.
    """
    result = build_thread_context_text(
        thread_ref,
        include_referenced_files=include_referenced_files,
        max_chars_per_file=max_chars_per_file,
        on_missing=on_missing,
        json_artifact_names=json_artifact_names,
    )
    if str(filter_keyword or "").strip():
        result["filtered_context_text"] = filter_context_text_by_keyword(
            str(result.get("context_text", "")),
            str(filter_keyword),
        )
    return result
