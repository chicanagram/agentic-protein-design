from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def run_local_tool(
    executable: str,
    args: List[str],
    *,
    workdir: Optional[Path] = None,
    timeout_s: int = 1800,
) -> Dict[str, object]:
    """
    Execute a local binary and return a normalized payload.
    """
    resolved = shutil.which(executable)
    if not resolved:
        return {
            "status": "error",
            "error": f"Executable not found in PATH: {executable}",
            "executable": executable,
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }

    cmd = [resolved, *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workdir) if workdir else None,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "error": f"Command timed out after {timeout_s}s",
            "executable": executable,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }

    return {
        "status": "ok" if proc.returncode == 0 else "error",
        "error": "" if proc.returncode == 0 else f"Non-zero exit code: {proc.returncode}",
        "executable": executable,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

