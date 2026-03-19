from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

import pandas as pd

from .compile import compile_scores_by_fields, standardize_score_table
from .config import build_user_inputs
from .io import (
    check_required_artifacts,
    get_expected_artifacts,
    load_base_data,
    load_score_tables,
    resolve_paths,
)
from .selection import rank_and_select_mutants_prototype


def _determine_steps_to_run(artifact_status: pd.DataFrame, user_inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Return placeholder execution plan for missing artifacts."""
    # Section 1: compute missing required artifacts.
    if artifact_status is None or artifact_status.empty:
        return []
    missing = artifact_status.loc[artifact_status["missing_for_run"] == True]
    if missing.empty:
        return []

    # Section 2: map missing artifacts to step placeholder actions.
    actions: List[Dict[str, Any]] = []
    for _, row in missing.iterrows():
        artifact = str(row["artifact"])
        path = str(row["path"])
        if "LLR vect" in artifact or "meanPLL csv" in artifact:
            actions.append(
                {
                    "step": "get_sequence_encodings",
                    "status": "needs_run",
                    "reason": f"Missing PLM score artifact: {artifact}",
                    "target_path": path,
                }
            )
        elif "ProteinMPNN" in artifact:
            actions.append(
                {
                    "step": "structure_model_scoring",
                    "status": "needs_run",
                    "reason": f"Missing structure model artifact: {artifact}",
                    "target_path": path,
                }
            )
        elif "SPURS" in artifact:
            actions.append(
                {
                    "step": "spurs_scoring",
                    "status": "needs_run",
                    "reason": f"Missing SPURS artifact: {artifact}",
                    "target_path": path,
                }
            )
        elif "annotations" in artifact:
            actions.append(
                {
                    "step": "annotation_pipeline",
                    "status": "needs_run",
                    "reason": f"Missing annotation artifact: {artifact}",
                    "target_path": path,
                }
            )
    return actions


def _standardize_loaded_scores(score_tables: Mapping[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Convert raw loaded score tables into normalized long tables."""
    # Section 1: parse source metadata and standardize each table.
    out: Dict[str, pd.DataFrame] = {}
    for artifact_name, df in score_tables.items():
        parts = artifact_name.split()
        model = parts[0] if parts else "unknown_model"
        score_type = "LLR" if "LLR vect" in artifact_name else "meanPLL" if "meanPLL csv" in artifact_name else "score"
        try:
            out[artifact_name] = standardize_score_table(
                df,
                source_name=artifact_name,
                model_name=model,
                score_type=score_type,
            )
        except Exception:
            continue
    return out


def run_zero_shot_mutant_design_workflow(
    user_inputs: Mapping[str, Any],
    *,
    repo_root: Path,
) -> Dict[str, Any]:
    """Run preflight + loading + prototype selection for zero-shot mutant design."""
    # Section 1: resolve paths and check existing artifacts.
    paths = resolve_paths(user_inputs, repo_root=repo_root)
    artifact_status = check_required_artifacts(user_inputs, paths)
    expected_artifacts = get_expected_artifacts(user_inputs, paths)
    base_data = load_base_data(user_inputs, paths, artifact_status)

    # Section 2: determine which upstream steps need to be run (placeholder only).
    steps_to_run = _determine_steps_to_run(artifact_status, user_inputs)

    # Section 3: load available score tables and compile.
    raw_score_tables = load_score_tables(artifact_status)
    score_tables_long = _standardize_loaded_scores(raw_score_tables)
    scores_long = (
        pd.concat(score_tables_long.values(), ignore_index=True)
        if score_tables_long
        else pd.DataFrame(columns=["position", "mutations", "score_raw", "model_name", "score_type", "score_source"])
    )
    compiled_scores = compile_scores_by_fields(score_tables_long, merge_fields=("position", "mutations"))

    # Section 4: run prototype PLM-based mutant selection.
    shortlist_df = rank_and_select_mutants_prototype(scores_long, user_inputs)

    # Section 5: return orchestrated workflow payload.
    return {
        "status": "ok",
        "paths": {k: str(v) for k, v in paths.items()},
        "expected_artifacts": [
            {**row, "path": str(row["path"])} for row in expected_artifacts
        ],
        "artifact_status": artifact_status.to_dict(orient="records"),
        "base_data_summary": {
            "wt_sequence_len": len(base_data.get("wt_sequence", "")),
            "missing_artifacts": base_data.get("missing_artifacts", []),
            "has_candidate_df": base_data.get("candidate_df") is not None,
            "has_conservation_df": base_data.get("conservation_df") is not None,
            "structure_path": str(base_data["structure_path"]) if base_data.get("structure_path") else None,
            "ligand_path": str(base_data["ligand_path"]) if base_data.get("ligand_path") else None,
        },
        "steps_to_run": steps_to_run,
        "loaded_score_sources": list(score_tables_long.keys()),
        "scores_long_preview": scores_long.head(20).to_dict(orient="records"),
        "compiled_scores_preview": compiled_scores.head(20).to_dict(orient="records"),
        "shortlist_preview": shortlist_df.head(50).to_dict(orient="records"),
    }


def _load_inputs_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    if args.inputs_json:
        return dict(json.loads(args.inputs_json))
    if args.inputs_file:
        p = Path(args.inputs_file).expanduser().resolve()
        return dict(json.loads(p.read_text(encoding="utf-8")))
    return build_user_inputs(
        root_key="examples",
        data_subfolder="ET096_R1-2",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run zero-shot mutant design workflow (prototype).")
    parser.add_argument("--inputs-json", type=str, default="", help="Inline JSON string of workflow inputs.")
    parser.add_argument("--inputs-file", type=str, default="", help="Path to JSON file of workflow inputs.")
    parser.add_argument("--repo-root", type=str, default="", help="Optional repo root override.")
    args = parser.parse_args()

    inputs = _load_inputs_from_args(args)
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else Path.cwd().resolve()
    if repo_root.name == "notebooks":
        repo_root = repo_root.parent
    result = run_zero_shot_mutant_design_workflow(inputs, repo_root=repo_root)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
