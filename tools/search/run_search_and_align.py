from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from tools.align.seq_align import run_msa
from tools.search.blastp import run_blastp
from tools.search.jackhmmer import run_jackhmmer
from tools.search.parse_seqsearch_output import parse_blastp_output, parse_hmmer_output
from tools.search.phmmer import run_phmmer
from tools.utils.seq_utils import write_sequence_to_fasta

def run_seqsearch_api(seed_sequence: str, msa_fasta_path: str) -> None:
    return None


def run_seqsearch(
    search_type: str,
    query_fasta: str,
    db_name: str,
    output_file: str,
    e_thres: float,
    incE_thres: float | None,
    max_target_seqs: int | None,
    num_cpu: int | None,
    query_dir: str | Path,
    db_dir: str | Path,
    output_dir: str | Path,
) -> Path:
    """
    Dispatch a local homolog search backend and return the raw output path.
    """
    search_type = str(search_type).strip().lower()
    if search_type == "blastp":
        return run_blastp(
            query_fasta=query_fasta,
            db_name=db_name,
            output_name=output_file,
            e_thres=e_thres,
            max_target_seqs=max_target_seqs,
            query_dir=str(query_dir),
            db_dir=str(db_dir),
            output_dir=str(output_dir),
        )
    if search_type == "phmmer":
        return run_phmmer(
            query_fasta=query_fasta,
            db_name=db_name,
            output_file=output_file,
            e_thres=e_thres,
            incE_thres=e_thres if incE_thres is None else incE_thres,
            max_target_seqs=max_target_seqs,
            num_cpu=num_cpu,
            query_dir=str(query_dir),
            db_dir=str(db_dir),
            output_dir=str(output_dir),
        )
    if search_type == "jackhmmer":
        return run_jackhmmer(
            query_fasta=query_fasta,
            db_name=db_name,
            output_file=output_file,
            e_thres=e_thres,
            incE_thres=e_thres if incE_thres is None else incE_thres,
            max_target_seqs=max_target_seqs,
            num_cpu=num_cpu,
            query_dir=str(query_dir),
            db_dir=str(db_dir),
            output_dir=str(output_dir),
        )
    raise ValueError(f"Unsupported search_type: {search_type}")


def run_search_and_align_pipeline(
    *,
    query_seq: str,
    query_seq_name: str,
    db_name: str,
    search_type: str,
    sequences_dir: str | Path,
    seqsearch_dir: str | Path,
    msa_dir: str | Path,
    db_dir: str | Path,
    msa_method: str = "mafft",
    mafft_executable: str | None = None,
    e_thres: float = 1e-5,
    incE_thres: float | None = None,
    max_target_seqs: int | None = None,
    num_cpu: int | None = None,
    output_prefix: str | None = None,
) -> Dict[str, Any]:
    """
    Run local homolog search, parse hits to FASTA/CSV, then align with MAFFT.

    Returns:
        Dict with paths to the raw search output, parsed CSV, hits FASTA, query
        FASTA, and final MSA FASTA.
    """
    sequences_dir = Path(sequences_dir)
    seqsearch_dir = Path(seqsearch_dir)
    msa_dir = Path(msa_dir)
    db_dir = Path(db_dir)
    for folder in (sequences_dir, seqsearch_dir, msa_dir):
        folder.mkdir(parents=True, exist_ok=True)

    search_type = str(search_type).strip().lower()
    seed_name = str(query_seq_name).strip() or "query"
    prefix = str(output_prefix).strip() if output_prefix else seed_name
    stem = f"{prefix}_{search_type}_{db_name}"
    if search_type != "blastp" and incE_thres is not None:
        stem += f"_incE{incE_thres:.0e}"
    stem += f"_E{e_thres:.0e}"

    query_fasta_path = sequences_dir / f"{seed_name}_query.fasta"
    write_sequence_to_fasta(query_seq, seed_name, query_fasta_path.stem, f"{query_fasta_path.parent}/")

    raw_output_name = f"{stem}.out"
    raw_output_path = run_seqsearch(
        search_type=search_type,
        query_fasta=query_fasta_path.name,
        db_name=db_name,
        output_file=raw_output_name,
        e_thres=e_thres,
        incE_thres=incE_thres,
        max_target_seqs=max_target_seqs,
        num_cpu=num_cpu,
        query_dir=sequences_dir,
        db_dir=db_dir,
        output_dir=seqsearch_dir,
    )

    parsed_csv_path = seqsearch_dir / f"{stem}.csv"
    hits_fasta_path = sequences_dir / f"{stem}.fasta"
    if search_type == "blastp":
        parsed_df = parse_blastp_output(
            input_fname=raw_output_path,
            output_fname=parsed_csv_path,
            output_fasta_fname=hits_fasta_path,
            query_seq_input=(query_seq, seed_name),
            sequences_dir=sequences_dir,
            seqsearch_dir=seqsearch_dir,
            max_target_seqs=max_target_seqs,
        )
    else:
        parsed_df = parse_hmmer_output(
            input_fname=raw_output_path,
            output_fname=parsed_csv_path,
            output_fasta_fname=hits_fasta_path,
            query_seq_input=([query_seq], [seed_name]),
            sequences_dir=sequences_dir,
            seqsearch_dir=seqsearch_dir,
            max_target_seqs=max_target_seqs,
        )

    msa_path = run_msa(
        seq_fname=hits_fasta_path.name,
        msa_fname=f"{stem}_{msa_method}.fasta",
        method=msa_method,
        seq_dir=sequences_dir,
        msa_dir=msa_dir,
        mafft_executable=mafft_executable,
    )

    return {
        "search_type": search_type,
        "query_fasta_path": str(query_fasta_path),
        "raw_output_path": str(raw_output_path),
        "parsed_csv_path": str(parsed_csv_path),
        "hits_fasta_path": str(hits_fasta_path),
        "msa_path": str(msa_path),
        "n_hits": int(len(parsed_df)),
    }
