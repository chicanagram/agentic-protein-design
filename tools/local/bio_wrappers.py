from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from tools.local.runner import run_local_tool


def run_mafft_alignment(
    input_fasta: Path,
    output_fasta: Path,
    *,
    mafft_args: Optional[List[str]] = None,
) -> Dict[str, object]:
    args = list(mafft_args or ["--auto", str(input_fasta)])
    result = run_local_tool("mafft", args)
    if result["status"] == "ok":
        output_fasta.write_text(str(result["stdout"]), encoding="utf-8")
    return {
        **result,
        "output_fasta": str(output_fasta),
    }


def run_mmseqs_easy_search(
    query_fasta: Path,
    target_db: Path,
    result_tsv: Path,
    tmp_dir: Path,
    *,
    extra_args: Optional[List[str]] = None,
) -> Dict[str, object]:
    args = [
        "easy-search",
        str(query_fasta),
        str(target_db),
        str(result_tsv),
        str(tmp_dir),
        *(extra_args or []),
    ]
    result = run_local_tool("mmseqs", args)
    return {
        **result,
        "result_tsv": str(result_tsv),
    }

