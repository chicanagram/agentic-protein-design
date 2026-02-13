from __future__ import annotations

from typing import Any, Dict, Optional


def http_get_json(url: str, *, headers: Optional[Dict[str, str]] = None, timeout_s: int = 30) -> Dict[str, Any]:
    """
    Small GET helper to keep API wrappers consistent.
    """
    try:
        import requests
    except ImportError as exc:
        return {
            "status": "error",
            "error": "requests package is not installed",
            "data": None,
        }

    try:
        resp = requests.get(url, headers=headers or {}, timeout=timeout_s)
        return {
            "status": "ok" if resp.ok else "error",
            "error": "" if resp.ok else f"HTTP {resp.status_code}",
            "status_code": resp.status_code,
            "data": resp.json() if resp.ok else None,
            "text": resp.text,
            "url": url,
        }
    except Exception as exc:  # pragma: no cover
        return {
            "status": "error",
            "error": str(exc),
            "data": None,
            "url": url,
        }

