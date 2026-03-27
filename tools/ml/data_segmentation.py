from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from tools.ml.segment_data import run_segmentation_pipeline


def run_data_segmentation(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """High-level wrapper for notebook calls."""
    csv_dir = Path(str(inputs.get("csv_dir", "")).strip()).expanduser()
    csv_file = str(inputs.get("csv_file", "")).strip()
    if not csv_dir or not csv_file:
        raise ValueError("run_data_segmentation requires 'csv_dir' and 'csv_file'.")

    csv_path = (csv_dir / csv_file).resolve()
    output_csv_file = str(inputs.get("output_csv_file", "") or "").strip()
    output_csv_path = (csv_dir / output_csv_file).resolve() if output_csv_file else None

    out_path = run_segmentation_pipeline(
        csv_path=csv_path,
        mutation_separator=str(inputs.get("mutation_separator", ":")).strip() or ":",
        num_mutation_segments_singlemut=int(inputs.get("num_mutation_segments_singlemut", 5)),
        min_layer_size_for_multimut_segmentation=int(
            inputs.get("min_layer_size_for_multimut_segmentation", 1000)
        ),
        smallest_single_mutant_size=int(inputs.get("smallest_single_mutant_size", 100)),
        k_folds=int(inputs.get("k_folds", 5)),
        include_mutation_onehot_for_clustering=bool(
            inputs.get("include_mutation_onehot_for_clustering", True)
        ),
        output_csv_path=output_csv_path,
        verbose=bool(inputs.get("verbose", True)),
        print_group_details=bool(inputs.get("print_group_details", False)),
    )
    return {
        "status": "ok",
        "input_csv_path": str(csv_path),
        "output_csv_path": str(out_path),
        "output_dataset_fname": out_path.name,
    }
