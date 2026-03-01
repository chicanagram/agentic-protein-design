from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from tools.openprotein.openprotein_utils import connect_openprotein_session
from tools.utils.seq_utils import write_sequence_to_fasta


def create_openprotein_msa(
    *,
    seed_sequence: Optional[str] = None,
    seed_sequence_name: Optional[str] = None,
    sequences: Optional[Sequence[str]] = None,
    session: Optional[Any] = None,
    seq_fasta_path: Path
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

    # start session and create MSA
    sess = session or connect_openprotein_session()
    msa = sess.align.create_msa(query.encode())

    # parse MSA
    r = msa.wait()
    msa_iterator = msa.get()
    sequences = []
    seq_names = []
    sequences_degapped = []
    for (seq_name, seq) in msa_iterator:
        seq_name = seq_name.split('\t')[0]
        sequences.append(seq)
        seq_names.append(seq_name)
        seq_degapped = seq.replace('-','')
        sequences_degapped.append(seq_degapped)
    seq_names[0] = seed_sequence_name

    # save MSA and degapped sequences
    write_sequence_to_fasta(sequences_degapped, seq_names, os.path.basename(seq_fasta_path), os.path.dirname(seq_fasta_path)+'/')

    return msa