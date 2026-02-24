from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Bio import SeqIO
from Bio.PDB import PDBParser, PPBuilder

from project_config.variables import address_dict, subfolders
from tools.openprotein import create_openprotein_msa, save_openprotein_msa


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "processed"]
AA_ORDER = list("ACDEFGHIKLMNPQRSTVWY-")
AA_TO_INT = {aa: i for i, aa in enumerate(AA_ORDER)}


def resolve_project_root() -> Path:
    """Resolve repository root when called from repo root or notebooks subdir."""
    root = Path.cwd().resolve()
    if root.name == "notebooks":
        return root.parent
    return root


def setup_data_root(root_key: str, project_root: Optional[Path] = None) -> Tuple[Path, Dict[str, Path]]:
    """
    Resolve and create standard data-root subfolders for this step.

    Args:
        root_key: Key in `project_config.variables.address_dict`.
        project_root: Optional project-root override.

    Returns:
        Tuple `(data_root, resolved_subfolder_paths)`.
    """
    if root_key not in address_dict:
        raise KeyError(f"Unknown root_key: {root_key}")
    base = project_root or resolve_project_root()
    data_root = (base / address_dict[root_key]).resolve()
    resolved: Dict[str, Path] = {}
    for key in REQUIRED_SUBFOLDERS:
        folder = data_root / subfolders[key]
        folder.mkdir(parents=True, exist_ok=True)
        resolved[key] = folder
    return data_root, resolved


def default_user_inputs() -> Dict[str, Any]:
    """
    Return editable defaults for MSA and conservation workflow.

    Returns:
        Dict containing alignment source/method options, file lists, plotting,
        and conservation-analysis controls.
    """
    return {
        "root_key": "examples",
        "data_subfolder": "",
        "alignment_input_mode": "sequence",  # sequence | structure
        "sequence_alignment_backend": "mafft",  # mafft | openprotein
        "structure_alignment_mode": "extract_sequence_then_align",  # scaffold mode
        "seed_sequence": "",
        "input_sequences": [],
        "sequence_fasta_filenames": [],
        "structure_pdb_filenames": [],
        "sequence_subdirectory": "sequences/",
        "structure_subdirectory": "pdb/",
        "msa_output_filename": "msa_aligned.fasta",
        "plot_output_filename": "msa_visualization.png",
        "conservation_output_filename": "msa_conservation.csv",
        "run_conservation_analysis": True,
        "mafft_executable": "mafft",
        "max_sequences_for_plot": 120,
        "max_positions_for_plot": 600,
    }


def _join_data_path(data_root: Path, subdir: str, data_subfolder: str, filename: str) -> Path:
    sub = str(subdir).strip().strip("/")
    ds = str(data_subfolder or "").strip().strip("/")
    name = str(filename).strip().lstrip("/")
    p = data_root
    if sub:
        p = p / sub
    if ds:
        p = p / ds
    return p / name


def _read_fasta_sequences(fasta_path: Path) -> List[str]:
    seqs: List[str] = []
    for rec in SeqIO.parse(str(fasta_path), "fasta"):
        seqs.append(str(rec.seq))
    return [s for s in seqs if s]


def _extract_sequence_from_pdb(pdb_path: Path) -> str:
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", str(pdb_path))
    builder = PPBuilder()
    peptides = builder.build_peptides(structure)
    if not peptides:
        return ""
    return "".join(str(pp.get_sequence()) for pp in peptides)


def _collect_input_sequences(
    *,
    data_root: Path,
    data_subfolder: str,
    input_mode: str,
    input_sequences: Sequence[str],
    sequence_fasta_filenames: Sequence[str],
    structure_pdb_filenames: Sequence[str],
    sequence_subdirectory: str,
    structure_subdirectory: str,
) -> List[str]:
    seqs: List[str] = [str(s).strip() for s in input_sequences if str(s).strip()]

    for fname in sequence_fasta_filenames:
        p = _join_data_path(data_root, sequence_subdirectory, data_subfolder, fname)
        if p.exists():
            seqs.extend(_read_fasta_sequences(p))

    if input_mode == "structure":
        for fname in structure_pdb_filenames:
            p = _join_data_path(data_root, structure_subdirectory, data_subfolder, fname)
            if p.exists():
                seq = _extract_sequence_from_pdb(p)
                if seq:
                    seqs.append(seq)
    return seqs


def _write_temp_fasta(sequences: Sequence[str], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    for i, seq in enumerate(sequences, start=1):
        lines.append(f">seq_{i}")
        lines.append(seq)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def run_mafft_alignment(
    *,
    sequences: Sequence[str],
    out_msa_fasta: Path,
    mafft_executable: str = "mafft",
) -> Path:
    """
    Run local MAFFT alignment for a sequence set.

    Args:
        sequences: Raw amino-acid sequences to align.
        out_msa_fasta: Output MSA FASTA path.
        mafft_executable: MAFFT executable path or command name.

    Returns:
        Output MSA FASTA path.
    """
    if len(sequences) < 2:
        raise ValueError("MAFFT requires at least 2 sequences.")
    temp_in = out_msa_fasta.with_suffix(".input.fasta")
    _write_temp_fasta(sequences, temp_in)

    cmd = [mafft_executable, "--auto", str(temp_in)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"MAFFT failed ({proc.returncode}): {proc.stderr.strip()}")

    out_msa_fasta.parent.mkdir(parents=True, exist_ok=True)
    out_msa_fasta.write_text(proc.stdout, encoding="utf-8")
    temp_in.unlink(missing_ok=True)
    return out_msa_fasta


def _load_msa_matrix(msa_fasta_path: Path) -> Tuple[np.ndarray, List[str]]:
    records = list(SeqIO.parse(str(msa_fasta_path), "fasta"))
    if not records:
        raise ValueError(f"No sequences found in MSA file: {msa_fasta_path}")
    names = [r.id for r in records]
    seqs = [str(r.seq) for r in records]
    aln_len = len(seqs[0])
    if any(len(s) != aln_len for s in seqs):
        raise ValueError("Alignment file contains unequal sequence lengths.")
    arr = np.array([list(s) for s in seqs], dtype="<U1")
    return arr, names


def plot_msa(
    *,
    msa_fasta_path: Path,
    out_png_path: Path,
    max_sequences: int = 120,
    max_positions: int = 600,
) -> Path:
    """
    Plot a compact MSA heatmap-style visualization and save to PNG.

    Args:
        msa_fasta_path: Input aligned FASTA path.
        out_png_path: Output PNG path.
        max_sequences: Row cap for plotting.
        max_positions: Column cap for plotting.

    Returns:
        Path to saved PNG file.
    """
    arr, names = _load_msa_matrix(msa_fasta_path)
    arr = arr[:max_sequences, :max_positions]
    numeric = np.vectorize(lambda aa: AA_TO_INT.get(aa.upper(), AA_TO_INT["-"]))(arr)

    fig_w = max(10, min(22, arr.shape[1] / 35))
    fig_h = max(4, min(18, arr.shape[0] / 6))
    plt.figure(figsize=(fig_w, fig_h))
    plt.imshow(numeric, aspect="auto", interpolation="nearest")
    plt.title("MSA Visualization")
    plt.xlabel("Alignment Position")
    plt.ylabel("Sequence Index")
    plt.colorbar(label="Residue Category")
    plt.tight_layout()
    out_png_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png_path, dpi=180)
    plt.close()
    return out_png_path


def compute_conservation(msa_fasta_path: Path) -> pd.DataFrame:
    """
    Compute simple per-position conservation metrics for an MSA.

    Args:
        msa_fasta_path: Input aligned FASTA path.

    Returns:
        DataFrame with per-position metrics:
        `position`, `consensus_residue`, `consensus_fraction`, `n_non_gap`.
    """
    arr, _ = _load_msa_matrix(msa_fasta_path)
    rows: List[Dict[str, Any]] = []
    for i in range(arr.shape[1]):
        col = [aa for aa in arr[:, i].tolist() if aa != "-"]
        if not col:
            rows.append(
                {
                    "position": i + 1,
                    "consensus_residue": "",
                    "consensus_fraction": 0.0,
                    "n_non_gap": 0,
                }
            )
            continue
        counts = Counter(col)
        aa, n = counts.most_common(1)[0]
        rows.append(
            {
                "position": i + 1,
                "consensus_residue": aa,
                "consensus_fraction": float(n / len(col)),
                "n_non_gap": int(len(col)),
            }
        )
    return pd.DataFrame(rows)


def run_alignment_and_conservation(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run scaffolded sequence/structure alignment pipeline with optional conservation.

    Args:
        inputs: User input dictionary (see `default_user_inputs()`).

    Returns:
        Dict containing run status and generated artifact paths/dataframes.
    """
    root_key = str(inputs.get("root_key", "examples"))
    data_subfolder = str(inputs.get("data_subfolder", "") or "").strip()
    input_mode = str(inputs.get("alignment_input_mode", "sequence")).strip().lower()
    backend = str(inputs.get("sequence_alignment_backend", "mafft")).strip().lower()

    data_root, resolved = setup_data_root(root_key)
    processed_base = resolved["processed"] / "05_get_sequences_align_and_analyse_conservation"
    if data_subfolder:
        processed_base = processed_base / data_subfolder
    processed_base.mkdir(parents=True, exist_ok=True)

    msa_out = processed_base / str(inputs.get("msa_output_filename", "msa_aligned.fasta"))
    plot_out = processed_base / str(inputs.get("plot_output_filename", "msa_visualization.png"))
    cons_out = processed_base / str(inputs.get("conservation_output_filename", "msa_conservation.csv"))

    sequences = _collect_input_sequences(
        data_root=data_root,
        data_subfolder=data_subfolder,
        input_mode=input_mode,
        input_sequences=inputs.get("input_sequences", []),
        sequence_fasta_filenames=inputs.get("sequence_fasta_filenames", []),
        structure_pdb_filenames=inputs.get("structure_pdb_filenames", []),
        sequence_subdirectory=str(inputs.get("sequence_subdirectory", "sequences/")),
        structure_subdirectory=str(inputs.get("structure_subdirectory", "pdb/")),
    )
    seed_sequence = str(inputs.get("seed_sequence", "")).strip()

    msa_metadata: Dict[str, Any] = {}
    if backend == "openprotein":
        msa_job = create_openprotein_msa(
            seed_sequence=seed_sequence,
            sequences=sequences,
            wait=True,
        )
        msa_text = str(msa_job.get("msa_text", "") or "")
        if not msa_text:
            raise RuntimeError("OpenProtein MSA returned empty text.")
        save_openprotein_msa(msa_text, msa_out)
        msa_metadata = {"msa_id": msa_job.get("msa_id", ""), "backend": "openprotein"}
    else:
        seqs_for_mafft = list(sequences)
        if seed_sequence:
            seqs_for_mafft = [seed_sequence, *seqs_for_mafft]
        run_mafft_alignment(
            sequences=seqs_for_mafft,
            out_msa_fasta=msa_out,
            mafft_executable=str(inputs.get("mafft_executable", "mafft")),
        )
        msa_metadata = {"msa_id": "", "backend": "mafft"}

    plot_msa(
        msa_fasta_path=msa_out,
        out_png_path=plot_out,
        max_sequences=int(inputs.get("max_sequences_for_plot", 120)),
        max_positions=int(inputs.get("max_positions_for_plot", 600)),
    )

    cons_df = pd.DataFrame()
    if bool(inputs.get("run_conservation_analysis", True)):
        cons_df = compute_conservation(msa_out)
        cons_df.to_csv(cons_out, index=False)

    return {
        "status": "ok",
        "root_key": root_key,
        "data_root": str(data_root),
        "processed_dir": str(processed_base),
        "alignment_input_mode": input_mode,
        "alignment_backend": backend,
        "n_input_sequences": int(len(sequences) + (1 if seed_sequence else 0)),
        "msa_path": str(msa_out),
        "plot_path": str(plot_out),
        "conservation_path": str(cons_out) if not cons_df.empty else "",
        "conservation_df": cons_df,
        "msa_metadata": msa_metadata,
    }


def get_sequences_align_and_analyse_conservation(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward-compatible wrapper for this step module.

    Args:
        inputs: Step input dictionary.

    Returns:
        Output dictionary from `run_alignment_and_conservation`.
    """
    return run_alignment_and_conservation(inputs)

