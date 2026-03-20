from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

import pandas as pd

from .compile import (
    build_score_source_registry,
    load_score_data_dict,
    merge_score_data_dict,
    standardize_score_table,
)
from .config import build_user_inputs
from .io import (
    check_required_artifacts,
    get_expected_artifacts,
    load_base_data,
    load_score_tables,
    resolve_paths,
)
from .selection import rank_and_select_mutants_prototype

STEP_ORDER: tuple[str, ...] = (
    "plm_scoring",
    "structure_model_scoring",
    "spurs_scoring",
    "structure_annotations",
)

ARTIFACT_STEP_RULES: tuple[tuple[str, str], ...] = (
    ("LLR vect", "plm_scoring"),
    ("meanPLL csv", "plm_scoring"),
    ("ProteinMPNN", "structure_model_scoring"),
    ("SPURS", "spurs_scoring"),
    ("annotations", "structure_annotations"),
)

SCORE_TYPE_RULES: tuple[tuple[str, str], ...] = (
    ("LLR vect", "LLR"),
    ("meanPLL csv", "meanPLL"),
)


def _step_for_artifact(artifact_name: str) -> str:
    # Section 1: map artifact labels to workflow step ids.
    for token, step in ARTIFACT_STEP_RULES:
        if token in artifact_name:
            return step
    return "unknown"


def _determine_steps_to_run(artifact_status: pd.DataFrame) -> List[Dict[str, Any]]:
    """Return placeholder execution plan for all requested steps, with file status."""
    # Section 1: build step buckets from artifact table.
    if artifact_status is None or artifact_status.empty:
        return []
    status_df = artifact_status.copy()
    status_df["step"] = status_df["artifact"].map(lambda x: _step_for_artifact(str(x)))
    status_df = status_df.loc[status_df["step"] != "unknown"].copy()
    if status_df.empty:
        return []

    # Section 2: build ordered step status records.
    actions: List[Dict[str, Any]] = []
    for step in STEP_ORDER:
        step_df = status_df.loc[status_df["step"] == step]
        if step_df.empty:
            continue
        artifacts = []
        for _, row in step_df.iterrows():
            artifacts.append(
                {
                    "artifact": str(row["artifact"]),
                    "target_path": str(row["path"]),
                    "exists": bool(row["exists"]),
                    "missing_for_run": bool(row["missing_for_run"]),
                }
            )
        step_missing = any(x["missing_for_run"] for x in artifacts)
        actions.append(
            {
                "step": step,
                "status": "needs_run" if step_missing else "up_to_date",
                "reason": "One or more required artifacts are missing." if step_missing else "All required artifacts already found.",
                "artifacts": artifacts,
            }
        )
    return actions


def _print_step_status(steps_to_run: List[Dict[str, Any]]) -> None:
    # Section 1: print deterministic per-step status, placeholder execution, and completion.
    for step in steps_to_run:
        step_name = str(step.get("step", "unknown"))
        step_status = str(step.get("status", "unknown"))
        print(f"[Step] {step_name}: START ({step_status})")
        for item in step.get("artifacts", []):
            artifact = str(item.get("artifact", "artifact"))
            target = str(item.get("target_path", ""))
            exists = bool(item.get("exists", False))
            state = "FOUND" if exists else "MISSING"
            print(f"- {artifact}: {state}")
            print(f"  target: {target}")
        # Section 2: placeholder for unimplemented step execution.
        if step_status == "needs_run":
            print(f"[Step] {step_name}: TODO run this step (placeholder, unimplemented).")

        # Section 3: re-check artifacts after attempted step run (or placeholder).
        artifacts = step.get("artifacts", [])
        for item in artifacts:
            target = str(item.get("target_path", ""))
            exists_after = Path(target).exists() if target else False
            item["exists_after"] = exists_after
            item["missing_after_run"] = not exists_after
        all_present_after = all(bool(a.get("exists_after", False)) for a in artifacts) if artifacts else True
        step["completion_status"] = "COMPLETE" if all_present_after else "INCOMPLETE"
        print(f"[Step] {step_name}: {step['completion_status']}")


def _refresh_artifact_status_from_steps(
    artifact_status: pd.DataFrame,
    steps_to_run: List[Dict[str, Any]],
) -> pd.DataFrame:
    # Section 1: update artifact existence flags using post-step checks.
    if artifact_status is None or artifact_status.empty:
        return artifact_status
    refreshed = artifact_status.copy()
    after_map: Dict[str, bool] = {}
    for step in steps_to_run:
        for item in step.get("artifacts", []):
            target = str(item.get("target_path", ""))
            if target:
                after_map[target] = bool(item.get("exists_after", False))
    if not after_map:
        return refreshed
    refreshed["exists"] = refreshed["path"].map(lambda p: after_map.get(str(p), bool(Path(str(p)).exists())))
    refreshed["missing_for_run"] = (~refreshed["exists"]) & refreshed["required"]
    return refreshed


def _expected_compiled_columns(score_source_registry: Mapping[tuple[str, str], Mapping[str, Any]]) -> List[str]:
    # Section 1: generate expected suffixed score columns from requested score sources.
    cols: List[str] = []
    for (score_type, score_name), meta in score_source_registry.items():
        canonical_value_cols = [str(c) for c in dict(meta.get("value_columns", {})).keys()]
        if not canonical_value_cols:
            canonical_value_cols = [str(meta.get("default_value_column", "score"))]
        if score_type == "structure_annotations":
            cols.extend(canonical_value_cols)
            continue
        for prefix in canonical_value_cols:
            cols.append(f"{prefix}_{score_name}")
    return list(dict.fromkeys(cols))


def _standardize_loaded_scores(score_tables: Mapping[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Convert raw loaded score tables into normalized long tables."""
    # Section 1: parse source metadata and standardize each table.
    out: Dict[str, pd.DataFrame] = {}
    for artifact_name, df in score_tables.items():
        parts = artifact_name.split()
        model = parts[0] if parts else "unknown_model"
        score_type = "score"
        for token, resolved in SCORE_TYPE_RULES:
            if token in artifact_name:
                score_type = resolved
                break
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

    # Section 2: determine step statuses and print preflight checks.
    steps_to_run = _determine_steps_to_run(artifact_status)
    _print_step_status(steps_to_run)
    artifact_status = _refresh_artifact_status_from_steps(artifact_status, steps_to_run)

    # Section 3: load available score tables and compile.
    raw_score_tables = load_score_tables(artifact_status)
    score_source_registry = build_score_source_registry(artifact_status, user_inputs)
    score_data_dict = load_score_data_dict(raw_score_tables, score_source_registry)
    compiled_scores = merge_score_data_dict(score_data_dict)
    # Section 3A: enforce id-column order and sorted intermediate display.
    ordered_cols = [c for c in ("resnum", "mutations") if c in compiled_scores.columns] + [
        c for c in compiled_scores.columns if c not in {"resnum", "mutations"}
    ]
    compiled_scores = compiled_scores[ordered_cols]
    sort_cols = [c for c in ("resnum", "mutations") if c in compiled_scores.columns]
    if sort_cols:
        compiled_scores = compiled_scores.sort_values(by=sort_cols, ascending=True).reset_index(drop=True)
    expected_cols = _expected_compiled_columns(score_source_registry)
    missing_cols = [c for c in expected_cols if c not in set(compiled_scores.columns)]
    # Section 3B: save raw compiled score table.
    filename_prefix = str(user_inputs.get("filename_prefix", "") or "")
    compiled_scores_path = Path(paths["proposal_dir"]) / f"{filename_prefix}scores_all.csv"
    compiled_scores.to_csv(compiled_scores_path, index=False)
    print("[Compiled Scores] saved:", str(compiled_scores_path))
    print("[Compiled Scores] size:", compiled_scores.shape)
    print("[Compiled Scores] columns:", list(compiled_scores.columns))
    print("[Compiled Scores] missing expected columns:", missing_cols if missing_cols else "None")

    # Section 3C: build long-form tables for downstream ranking prototype.
    score_tables_long = _standardize_loaded_scores(raw_score_tables)
    scores_long = (
        pd.concat(score_tables_long.values(), ignore_index=True)
        if score_tables_long
        else pd.DataFrame(columns=["resnum", "mutations", "score_raw", "model_name", "score_type", "score_source"])
    )

    # Section 4: run prototype PLM-based mutant selection.
    shortlist_df = rank_and_select_mutants_prototype(compiled_scores, user_inputs)
    output_filename_suffix = str(user_inputs.get("output_filename_suffix", "") or "")
    selected_scores_path = Path(paths["proposal_dir"]) / f"{filename_prefix}scores_all_selected{output_filename_suffix}.csv"
    shortlist_df.to_csv(selected_scores_path, index=False)
    print("[Selection] final shortlist size:", shortlist_df.shape)
    print("[Selection] saved:", str(selected_scores_path))

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
        "score_source_registry": [
            {"score_type": k[0], "score_name": k[1], **v}
            for k, v in score_source_registry.items()
        ],
        "loaded_score_data_keys": [
            {"score_type": k[0], "score_name": k[1]}
            for k in score_data_dict.keys()
        ],
        "loaded_score_sources": list(score_tables_long.keys()),
        "compiled_scores_missing_columns": missing_cols,
        "compiled_scores_path": str(compiled_scores_path),
        "selected_scores_path": str(selected_scores_path),
        "compiled_scores_shape": list(compiled_scores.shape),
        "compiled_scores_columns": list(compiled_scores.columns),
        "compiled_scores_records": compiled_scores.to_dict(orient="records"),
        "shortlist_shape": list(shortlist_df.shape),
        "shortlist_columns": list(shortlist_df.columns),
        "shortlist_records": shortlist_df.to_dict(orient="records"),
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
        output_data_subfolder="ET096_R1-2",
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
