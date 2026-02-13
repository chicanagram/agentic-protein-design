#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.local.runner import run_local_tool


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local bioinformatics tool via wrapper.")
    parser.add_argument("executable", help="Executable name in PATH, e.g. mafft, mmseqs")
    parser.add_argument("args", nargs="*", help="Arguments for executable")
    parser.add_argument("--workdir", default="", help="Optional working directory")
    parser.add_argument("--timeout-s", type=int, default=1800, help="Timeout seconds")
    ns = parser.parse_args()

    result = run_local_tool(
        ns.executable,
        ns.args,
        workdir=Path(ns.workdir) if ns.workdir else None,
        timeout_s=ns.timeout_s,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

