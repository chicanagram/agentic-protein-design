from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from tools.openprotein.openprotein_utils import connect_openprotein_session


def create_openprotein_msa(
    *,
    seed_sequence: Optional[str] = None,
    sequences: Optional[Sequence[str]] = None,
    session: Optional[Any] = None,
    wait: bool = True,
) -> Dict[str, Any]:
    """
    Create an MSA job via OpenProtein API from a seed sequence or sequence set.

    Args:
        seed_sequence: Optional seed sequence for homolog-based MSA generation.
        sequences: Optional explicit sequence list. If multiple are provided they
            are joined with ":" and submitted as one MSA seed string.
        session: Optional authenticated OpenProtein session.
        wait: If true, block until MSA job finishes.

    Returns:
        Dict containing `msa_id`, `status`, `job`, and optional `msa_text`.
    """
    seed = (seed_sequence or "").strip()
    seqs = [str(s).strip() for s in (sequences or []) if str(s).strip()]
    if not seed and not seqs:
        raise ValueError("Provide `seed_sequence` or non-empty `sequences`.")

    if seed and seqs:
        query = seed
    elif seed:
        query = seed
    elif len(seqs) == 1:
        query = seqs[0]
    else:
        query = ":".join(seqs)

    sess = session or connect_openprotein_session()
    msa_job = sess.align.create_msa(query.encode())
    out: Dict[str, Any] = {
        "msa_id": str(getattr(msa_job, "id", "")),
        "status": "submitted",
        "job": msa_job,
        "msa_text": "",
    }
    if not wait:
        return out

    msa_job.wait()
    msa_text = msa_job.get_msa()
    if isinstance(msa_text, bytes):
        msa_text = msa_text.decode("utf-8", errors="replace")
    out["status"] = "completed"
    out["msa_text"] = str(msa_text or "")
    return out


def save_openprotein_msa(msa_text: str, out_fasta_path: Path) -> Path:
    """
    Save OpenProtein MSA text output to FASTA/alignment file.

    Args:
        msa_text: Alignment text returned by OpenProtein MSA API.
        out_fasta_path: Destination file path.

    Returns:
        Path to the saved MSA file.
    """
    out_fasta_path.parent.mkdir(parents=True, exist_ok=True)
    out_fasta_path.write_text(msa_text, encoding="utf-8")
    return out_fasta_path

