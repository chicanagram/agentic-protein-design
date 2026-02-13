#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from tools.api.rcsb import search_rcsb_text
from tools.api.uniprot import search_uniprot


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple bioinformatics API query.")
    parser.add_argument("--provider", choices=["uniprot", "rcsb"], required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--size", type=int, default=25)
    ns = parser.parse_args()

    if ns.provider == "uniprot":
        result = search_uniprot(ns.query, size=ns.size)
    else:
        result = search_rcsb_text(ns.query, rows=ns.size)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

