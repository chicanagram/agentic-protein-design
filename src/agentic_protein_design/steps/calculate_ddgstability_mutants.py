from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from project_config.variables import address_dict
from tools.pythia.pythia_runner import run_pythia_ddg_scan_from_file_lists


def _resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_base_directory(inputs: Dict[str, Any]) -> str:
    """
    Resolve base directory from either:
    1) base_directory_key in project_config.variables.address_dict
    2) direct base_directory path fallback
    """
    root = _resolve_repo_root()

    base_key = str(inputs.get("base_directory_key", "")).strip()
    if base_key:
        if base_key not in address_dict:
            raise KeyError(
                f"Unknown base_directory_key: {base_key}. "
                f"Available keys: {sorted(address_dict.keys())}"
            )
        resolved = (root / str(address_dict[base_key])).resolve()
        return str(resolved)

    base_directory = str(inputs.get("base_directory", "")).strip()
    if not base_directory:
        raise ValueError("Missing required input: set base_directory_key or base_directory")
    return base_directory


def default_user_inputs() -> Dict[str, Any]:
    return {
        "stability_backend": "pythia",  # options: pythia (more backends later)
        "base_directory_key": "",  # recommended: key from address_dict in project_config/variables.py
        "base_directory": "",
        "data_subfolder": "",
        "sequence_subdirectory": "sequences/",
        "structure_subdirectory": "pdb/",
        "sequence_fasta_filenames": [],
        "structure_pdb_filenames": [],
        "available_base_directory_keys": sorted(address_dict.keys()),
        "n_jobs": 1,
        "check_plddt": False,
        "plddt_cutoff": 95.0,
        "pythia_python_executable": "/Users/charmainechia/miniconda3/envs/pythia/bin/python",
        "python_executable": "python",  # backward-compatible fallback
        "isolate_pythia_process_env": True,
        "output_csv_prefix": "",
        "output_csv": "",
        "save_outputs": True,
    }


def run_ddg_stability_predictions(
    inputs: Dict[str, Any],
    *,
    processed_dir: Path | None = None,
) -> Dict[str, Any]:
    """
    Wrapper used by notebook 12 to compute mutation stability ddG predictions.

    Currently implemented backends:
    - pythia
    """
    backend = str(inputs.get("stability_backend", "pythia")).strip().lower()
    if backend != "pythia":
        raise ValueError(
            f"Unsupported stability backend: {backend}. "
            "Supported backends: ['pythia']"
        )

    base_directory = _resolve_base_directory(inputs)
    data_subfolder_raw = inputs.get("data_subfolder", "")
    data_subfolder = "" if data_subfolder_raw is None else str(data_subfolder_raw).strip()

    sequence_subdirectory = str(inputs.get("sequence_subdirectory", "sequences/")).strip()
    structure_subdirectory = str(inputs.get("structure_subdirectory", "pdb/")).strip()
    sequence_fasta_filenames = [str(x).strip() for x in inputs.get("sequence_fasta_filenames", []) if str(x).strip()]
    structure_pdb_filenames = [str(x).strip() for x in inputs.get("structure_pdb_filenames", []) if str(x).strip()]
    if not structure_pdb_filenames:
        raise ValueError("Missing required input: structure_pdb_filenames (list)")

    output_csv_raw = str(inputs.get("output_csv", "")).strip()
    output_csv = output_csv_raw or None
    if not output_csv and bool(inputs.get("save_outputs", True)):
        output_csv_prefix = str(inputs.get("output_csv_prefix", "")).strip()
        data_subfolder_clean = str(data_subfolder).strip().strip("/")
        base_processed = Path(base_directory).expanduser() / "processed"
        filename = f"{output_csv_prefix}pythia_ddg_stability_predictions.csv"
        out_path = (
            base_processed / data_subfolder_clean / "12_calculate_ddGstability_mutants" / filename
            if data_subfolder_clean
            else base_processed / "12_calculate_ddGstability_mutants" / filename
        )
        output_csv = str(out_path.resolve())

    pythia_python_executable = str(
        inputs.get("pythia_python_executable", inputs.get("python_executable", "python"))
    ).strip()
    if not pythia_python_executable:
        pythia_python_executable = "python"

    result = run_pythia_ddg_scan_from_file_lists(
        base_directory=base_directory,
        data_subfolder=data_subfolder,
        sequence_subdirectory=sequence_subdirectory,
        structure_subdirectory=structure_subdirectory,
        sequence_fasta_filenames=sequence_fasta_filenames,
        structure_pdb_filenames=structure_pdb_filenames,
        n_jobs=int(inputs.get("n_jobs", 2)),
        check_plddt=bool(inputs.get("check_plddt", False)),
        plddt_cutoff=float(inputs.get("plddt_cutoff", 95.0)),
        python_executable=pythia_python_executable,
        output_csv=output_csv,
        isolate_process_env=bool(inputs.get("isolate_pythia_process_env", True)),
    )

    return {
        "status": result["status"],
        "backend": backend,
        "output_csv": result["output_csv"],
        "n_structures_input": result["n_structures_input"],
        "n_structures_scored": result["n_structures_scored"],
        "n_rows": result["n_rows"],
        "errors": result["errors"],
        "runtime_hints": result.get("runtime_hints", []),
        "predictions": result["predictions"],
    }
