from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _pythia_root() -> Path:
    return Path(__file__).resolve().parent


def _masked_scan_script() -> Path:
    return _pythia_root() / "pythia" / "masked_ddg_scan.py"


def _parse_pred_mask_file(pred_mask_path: Path) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    with pred_mask_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            mut, score = parts
            try:
                score_val = float(score)
            except ValueError:
                continue
            rows.append({"mutation": mut, "pythia_score": score_val})
    return pd.DataFrame(rows)


def _read_first_fasta_sequence(fasta_path: Path) -> str:
    seq_parts: List[str] = []
    with fasta_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            s = line.strip()
            if not s:
                continue
            if s.startswith(">"):
                continue
            seq_parts.append(s)
    return "".join(seq_parts)


def _join_path_parts(base_directory: str, subdirectory: str, data_subfolder: str, filename: str) -> Path:
    # Intended user pattern:
    # f'{base_directory}{subdirectory}{data_subfolder}{filename}'
    # Implemented with separator-safe joining.
    base = Path(str(base_directory).strip()).expanduser()
    sub = str(subdirectory).strip().strip("/")
    data = str(data_subfolder).strip().strip("/")
    name = str(filename).strip().lstrip("/")
    out = base
    if sub:
        out = out / sub
    if data:
        out = out / data
    return out / name


def _build_merged_from_file_lists(
    *,
    base_directory: str,
    data_subfolder: str,
    sequence_subdirectory: str,
    structure_subdirectory: str,
    sequence_fasta_filenames: List[str],
    structure_pdb_filenames: List[str],
) -> pd.DataFrame:
    """
    Build a merged structure/sequence table from directory components and filename lists.

    Args:
        base_directory: Base data directory.
        data_subfolder: Optional case subfolder.
        sequence_subdirectory: Sequence folder relative to base.
        structure_subdirectory: Structure folder relative to base.
        sequence_fasta_filenames: FASTA filenames to load.
        structure_pdb_filenames: PDB filenames to score.

    Returns:
        DataFrame with at least `structure_id` and `pdb_path`, plus optional `sequence`.
    """
    if not structure_pdb_filenames:
        raise ValueError("structure_pdb_filenames is required and cannot be empty.")

    sequence_map: Dict[str, str] = {}
    for seq_name in sequence_fasta_filenames:
        seq_path = _join_path_parts(base_directory, sequence_subdirectory, data_subfolder, seq_name)
        if not seq_path.exists():
            continue
        sequence_map[Path(seq_name).stem] = _read_first_fasta_sequence(seq_path)

    rows: List[Dict[str, Any]] = []
    for i, pdb_name in enumerate(structure_pdb_filenames):
        pdb_path = _join_path_parts(base_directory, structure_subdirectory, data_subfolder, pdb_name)
        structure_id = Path(pdb_name).stem
        row: Dict[str, Any] = {
            "structure_id": structure_id,
            "pdb_path": str(pdb_path),
        }

        if sequence_fasta_filenames:
            seq = sequence_map.get(structure_id, "")
            if not seq and i < len(sequence_fasta_filenames):
                seq_path_i = _join_path_parts(
                    base_directory,
                    sequence_subdirectory,
                    data_subfolder,
                    sequence_fasta_filenames[i],
                )
                if seq_path_i.exists():
                    seq = _read_first_fasta_sequence(seq_path_i)
            if seq:
                row["sequence"] = seq
        rows.append(row)

    return pd.DataFrame(rows)


def _run_pythia_from_merged_dataframe(
    *,
    merged: pd.DataFrame,
    structure_id_col: str,
    pdb_path_col: str,
    sequence_col: str,
    n_jobs: int,
    check_plddt: bool,
    plddt_cutoff: float,
    python_executable: str,
    output_csv: Optional[str],
    cleanup_pred_mask_txt: bool,
    isolate_process_env: bool,
) -> Dict[str, Any]:
    """
    Execute Pythia masked scan for rows in a normalized merged dataframe.

    Args:
        merged: DataFrame with structure id/path columns.
        structure_id_col: Structure id column name.
        pdb_path_col: PDB path column name.
        sequence_col: Optional sequence annotation column name.
        n_jobs: Pythia/joblib parallel workers.
        check_plddt: Whether to filter by pLDDT.
        plddt_cutoff: pLDDT cutoff threshold.
        python_executable: Python interpreter used for subprocess call.
        output_csv: Optional output CSV path.
        cleanup_pred_mask_txt: Whether to remove intermediate mask files.
        isolate_process_env: Whether to scrub inherited Python env vars.

    Returns:
        Dict with status, counts, errors/hints, output path, and predictions DataFrame.
    """
    repo_root = _repo_root()
    pythia_root = _pythia_root()
    masked_script = _masked_scan_script()

    outputs: List[pd.DataFrame] = []
    errors: List[str] = []
    runtime_hints: List[str] = []

    resolved_python = shutil.which(python_executable)
    if not resolved_python and Path(python_executable).exists():
        resolved_python = str(Path(python_executable).resolve())
    if not resolved_python:
        return {
            "status": "error",
            "n_structures_input": int(len(merged)),
            "n_structures_scored": 0,
            "n_rows": 0,
            "errors": [f"Python executable not found: {python_executable}"],
            "runtime_hints": [
                "Set user_inputs['pythia_python_executable'] to the full path of the isolated env Python "
                "(for example /Users/charmainechia/miniconda3/envs/pythia/bin/python)."
            ],
            "output_csv": "",
            "predictions": pd.DataFrame(columns=["structure_id", "pdb_path", "mutation", "pythia_score"]),
        }

    proc_env = os.environ.copy()
    if isolate_process_env:
        # Prevent parent notebook/kernel path injections from contaminating subprocess imports.
        proc_env.pop("PYTHONPATH", None)
        proc_env["PYTHONNOUSERSITE"] = "1"

    for _, row in merged.iterrows():
        structure_id = str(row[structure_id_col])
        pdb_path = Path(str(row[pdb_path_col])).expanduser()
        if not pdb_path.is_absolute():
            pdb_path = (repo_root / pdb_path).resolve()

        if not pdb_path.exists():
            errors.append(f"{structure_id}: missing pdb file {pdb_path}")
            continue

        pred_mask_txt = Path(str(pdb_path).replace(".pdb", "_pred_mask.txt"))
        cmd = [
            resolved_python,
            str(masked_script),
            "--input_dir",
            "",
            "--pdb_filename",
            str(pdb_path),
            "--n_jobs",
            str(n_jobs),
        ]
        if check_plddt:
            cmd.extend(["--check_plddt", "--plddt_cutoff", str(plddt_cutoff)])

        proc = subprocess.run(
            cmd,
            cwd=str(pythia_root),
            capture_output=True,
            text=True,
            check=False,
            env=proc_env,
        )
        if proc.returncode != 0:
            stderr_txt = (proc.stderr or "").strip()
            if "OMP: Error #179" in stderr_txt and "SHM2" in stderr_txt:
                runtime_hints.append(
                    "Pythia failed due to OpenMP shared-memory initialization (OMP Error #179 / SHM2). "
                    "This is an environment/runtime issue, not an input-file issue. "
                    "Try running in a local shell/conda env with compatible OpenMP runtime."
                )
            if "OMP: Error #15" in stderr_txt and "already initialized" in stderr_txt:
                runtime_hints.append(
                    "OpenMP duplicate runtime detected (OMP Error #15). "
                    "Use an isolated interpreter for Pythia (set pythia_python_executable to your dedicated env Python), "
                    "and avoid mixing heavy compiled libraries across environments."
                )
            errors.append(
                f"{structure_id}: masked_ddg_scan failed (code={proc.returncode}) stderr={stderr_txt}"
            )
            continue
        if not pred_mask_txt.exists():
            errors.append(
                f"{structure_id}: expected output file not found after scan: {pred_mask_txt}"
            )
            continue

        result_df = _parse_pred_mask_file(pred_mask_txt)
        if result_df.empty:
            errors.append(f"{structure_id}: no predictions parsed from {pred_mask_txt}")
            continue

        result_df.insert(0, "structure_id", structure_id)
        result_df.insert(1, "pdb_path", str(pdb_path))
        if sequence_col in merged.columns:
            result_df["sequence"] = row.get(sequence_col, "")
        outputs.append(result_df)

        if cleanup_pred_mask_txt:
            pred_mask_txt.unlink(missing_ok=True)

    combined = (
        pd.concat(outputs, ignore_index=True)
        if outputs
        else pd.DataFrame(columns=["structure_id", "pdb_path", "mutation", "pythia_score"])
    )
    out_csv_path = None
    if output_csv:
        out_csv_path = Path(output_csv).expanduser()
        if not out_csv_path.is_absolute():
            out_csv_path = (repo_root / out_csv_path).resolve()
        out_csv_path.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(out_csv_path, index=False)

    return {
        "status": "ok" if not errors else ("partial" if len(outputs) > 0 else "error"),
        "n_structures_input": int(len(merged)),
        "n_structures_scored": int(len(outputs)),
        "n_rows": int(len(combined)),
        "errors": errors,
        "runtime_hints": runtime_hints,
        "output_csv": "" if out_csv_path is None else str(out_csv_path),
        "predictions": combined,
    }


def run_pythia_ddg_scan(
    *,
    structure_table_csv: str,
    sequence_table_csv: Optional[str] = None,
    structure_id_col: str = "structure_id",
    pdb_path_col: str = "pdb_path",
    sequence_id_col: str = "sequence_id",
    sequence_col: str = "sequence",
    n_jobs: int = 2,
    check_plddt: bool = False,
    plddt_cutoff: float = 95.0,
    python_executable: str = "python",
    output_csv: Optional[str] = None,
    cleanup_pred_mask_txt: bool = True,
    isolate_process_env: bool = True,
) -> Dict[str, Any]:
    """
    Run Pythia masked ddG scan for one or more structures.

    Inputs are file-driven so notebook/workflow users can provide:
    - a structure CSV (required): must include structure ID + pdb path
    - a sequence CSV (optional): merged by sequence/structure ID for provenance
    """
    structures = pd.read_csv(structure_table_csv)
    if structure_id_col not in structures.columns or pdb_path_col not in structures.columns:
        raise KeyError(
            f"Structure table must contain columns '{structure_id_col}' and '{pdb_path_col}'. "
            f"Found: {list(structures.columns)}"
        )

    merged = structures.copy()
    if sequence_table_csv:
        seq_df = pd.read_csv(sequence_table_csv)
        if sequence_id_col not in seq_df.columns:
            raise KeyError(
                f"Sequence table must contain '{sequence_id_col}'. Found: {list(seq_df.columns)}"
            )
        keep_cols = [sequence_id_col]
        if sequence_col in seq_df.columns:
            keep_cols.append(sequence_col)
        seq_small = seq_df[keep_cols].copy()
        merged = merged.merge(
            seq_small,
            left_on=structure_id_col,
            right_on=sequence_id_col,
            how="left",
        )

    return _run_pythia_from_merged_dataframe(
        merged=merged,
        structure_id_col=structure_id_col,
        pdb_path_col=pdb_path_col,
        sequence_col=sequence_col,
        n_jobs=n_jobs,
        check_plddt=check_plddt,
        plddt_cutoff=plddt_cutoff,
        python_executable=python_executable,
        output_csv=output_csv,
        cleanup_pred_mask_txt=cleanup_pred_mask_txt,
        isolate_process_env=isolate_process_env,
    )


def run_pythia_ddg_scan_from_file_lists(
    *,
    base_directory: str,
    data_subfolder: str,
    sequence_subdirectory: str = "sequences/",
    structure_subdirectory: str = "pdb/",
    sequence_fasta_filenames: Optional[List[str]] = None,
    structure_pdb_filenames: Optional[List[str]] = None,
    n_jobs: int = 2,
    check_plddt: bool = False,
    plddt_cutoff: float = 95.0,
    python_executable: str = "python",
    output_csv: Optional[str] = None,
    cleanup_pred_mask_txt: bool = True,
    isolate_process_env: bool = True,
) -> Dict[str, Any]:
    """
    Run Pythia scan from directory components + filename lists.
    """
    merged = _build_merged_from_file_lists(
        base_directory=base_directory,
        data_subfolder=data_subfolder,
        sequence_subdirectory=sequence_subdirectory,
        structure_subdirectory=structure_subdirectory,
        sequence_fasta_filenames=sequence_fasta_filenames or [],
        structure_pdb_filenames=structure_pdb_filenames or [],
    )
    return _run_pythia_from_merged_dataframe(
        merged=merged,
        structure_id_col="structure_id",
        pdb_path_col="pdb_path",
        sequence_col="sequence",
        n_jobs=n_jobs,
        check_plddt=check_plddt,
        plddt_cutoff=plddt_cutoff,
        python_executable=python_executable,
        output_csv=output_csv,
        cleanup_pred_mask_txt=cleanup_pred_mask_txt,
        isolate_process_env=isolate_process_env,
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    """
    Build CLI argument parser for standalone Pythia runner script.

    Returns:
        Configured `argparse.ArgumentParser`.
    """
    parser = argparse.ArgumentParser(description="Run Pythia masked ddG scan from structure/sequence tables.")
    parser.add_argument("--structure-table-csv", required=True)
    parser.add_argument("--sequence-table-csv", default=None)
    parser.add_argument("--structure-id-col", default="structure_id")
    parser.add_argument("--pdb-path-col", default="pdb_path")
    parser.add_argument("--sequence-id-col", default="sequence_id")
    parser.add_argument("--sequence-col", default="sequence")
    parser.add_argument("--n-jobs", type=int, default=2)
    parser.add_argument("--check-plddt", action="store_true")
    parser.add_argument("--plddt-cutoff", type=float, default=95.0)
    parser.add_argument("--python-executable", default="python")
    parser.add_argument("--output-csv", default=None)
    parser.add_argument("--keep-pred-mask-txt", action="store_true")
    return parser


def main() -> None:
    """
    CLI entrypoint for running Pythia masked ddG scan from tabular inputs.
    """
    parser = _build_arg_parser()
    args = parser.parse_args()
    result = run_pythia_ddg_scan(
        structure_table_csv=args.structure_table_csv,
        sequence_table_csv=args.sequence_table_csv,
        structure_id_col=args.structure_id_col,
        pdb_path_col=args.pdb_path_col,
        sequence_id_col=args.sequence_id_col,
        sequence_col=args.sequence_col,
        n_jobs=args.n_jobs,
        check_plddt=args.check_plddt,
        plddt_cutoff=args.plddt_cutoff,
        python_executable=args.python_executable,
        output_csv=args.output_csv,
        cleanup_pred_mask_txt=not args.keep_pred_mask_txt,
    )
    print(
        f"status={result['status']} "
        f"input={result['n_structures_input']} "
        f"scored={result['n_structures_scored']} "
        f"rows={result['n_rows']}"
    )
    if result["output_csv"]:
        print(f"output_csv={result['output_csv']}")
    if result["errors"]:
        print("errors:")
        for e in result["errors"]:
            print(f"- {e}")


if __name__ == "__main__":
    main()
