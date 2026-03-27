from __future__ import annotations

if __name__ == "__main__" and __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parents[3]
    _src_root = _repo_root / "src"
    for _path in (str(_repo_root), str(_src_root)):
        if _path not in sys.path:
            sys.path.insert(0, _path)

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from agentic_protein_design.core.paths import resolve_project_root
from project_config.variables import address_dict
from tools.ml.workflow import run_supervised_ml_workflow


def default_user_inputs() -> Dict[str, Any]:
    return {
        "data_fbase": "examples",
        "data_subfolder": "ET096_R1-2",
        "dataset_fname": "ET096_R1-2.csv",
        "input_filename_prefix": "ET096_R1-2_",
        "sequence_base": None,
        "target_col": "foldchange_NBD_activity_25C",
        "classification_or_regression": "regression",
        "split_type_list": ["random", "mutres-modulo", "contiguous", "custom"],
        "feature_combinations_dict": {
            "onehot": ["one_hot"],
            "georgiev": ["georgiev"],
            "onehot_georgiev": ["one_hot", "georgiev"],
        },
        "model_list": ["rf", "ridge", "mlp_sklearn"],
        "k_folds": 5,
        "split_seed": 42,
        "mutres_col": "mutres_idx",
        "random_split_col": "fold_random_5",
        "mutres_split_col": "fold_mutres-modulo_5",
        "segment_col": "segment_index_final",
        "retrospective_segment_col": "segment_index_final",
        "segment_iterations": "auto",
        "contiguous_split_col": "",
        "custom_split_col": "fold_modulo_5",
        "custom_test_value": 0,
        "custom_test_dataset_fname": "",
        "custom_test_data_subfolder": "",
        "custom_input_filename_prefix": "",
        "csv_suffix": "",
        "save_trained_models": True,
        "save_predictions": True,
        "train_full_data_model": False,
        "featurecombi_model_pair_to_extract_coefficients_for": [],
        "show_progress": True,
        "model_settings_repo_dir": "tools/ml/model_settings",
        "run_label": "",
        "sample_id_col": "",
    }


def _resolve_data_root_dir(data_fbase: str) -> Path:
    project_root = resolve_project_root()
    value = str(data_fbase or "").strip()
    if not value:
        raise ValueError("data_fbase cannot be empty.")

    if value in address_dict:
        return (project_root / address_dict[value]).resolve()

    as_path = Path(value).expanduser()
    if as_path.is_absolute():
        return as_path.resolve()
    return (project_root / as_path).resolve()


def train_evaluate_supervised_ml_models(inputs: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(default_user_inputs())
    payload.update(dict(inputs or {}))

    project_root = resolve_project_root()
    data_root_dir = _resolve_data_root_dir(str(payload.get("data_fbase", "examples")))
    settings_dir = Path(str(payload.get("model_settings_repo_dir", "tools/ml/model_settings"))).expanduser()
    if not settings_dir.is_absolute():
        settings_dir = (project_root / settings_dir).resolve()

    payload["data_root_dir"] = str(data_root_dir)
    payload["model_settings_repo_dir"] = str(settings_dir)

    result = run_supervised_ml_workflow(payload)
    return {
        "status": result.get("status", "ok"),
        "step": "train_evaluate_supervised_ml_models",
        "data_root_dir": str(data_root_dir),
        **result,
    }


def _load_inputs_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    if args.inputs_json:
        return dict(json.loads(args.inputs_json))
    if args.inputs_file:
        p = Path(args.inputs_file).expanduser().resolve()
        return dict(json.loads(p.read_text(encoding="utf-8")))
    return default_user_inputs()


def main() -> None:
    parser = argparse.ArgumentParser(description="Train/evaluate supervised ML models from precomputed encodings.")
    parser.add_argument("--inputs-json", type=str, default="", help="Inline JSON string of step inputs.")
    parser.add_argument("--inputs-file", type=str, default="", help="Path to JSON file of step inputs.")
    args = parser.parse_args()

    user_inputs = _load_inputs_from_args(args)
    result = train_evaluate_supervised_ml_models(user_inputs)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
