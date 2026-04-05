from __future__ import annotations

if __name__ == "__main__" and __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parents[3]
    _src_root = _repo_root / "src"
    for _path in (str(_repo_root), str(_src_root)):
        if _path not in sys.path:
            sys.path.insert(0, _path)

from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest import result

from agentic_protein_design.core import resolve_input_path
from agentic_protein_design.core.pipeline_utils import safe_read_csv
from agentic_protein_design.tools.openprotein import (
    assert_valid_design_with_boltzgen_kwargs,
    boltzgen_yaml_to_design_kwargs,
    design_with_boltzgen,
    run_proteinmpnn_postdesign_pipeline,
    run_proteinmpnn_from_structures,
)


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        return [s.strip() for s in stripped.split(",") if s.strip()]
    return [str(value).strip()]


def resolve_optional_path(data_root: Path, path_like: Any) -> Optional[Path]:
    text = str(path_like or "").strip()
    if not text:
        return None
    return resolve_input_path(data_root, text)


def build_denovo_design_kwargs(user_inputs: Dict[str, Any], *, data_root: Path) -> Dict[str, Any]:
    """
    Transform notebook-style inputs into `design_with_boltzgen` kwargs.

    Args:
        user_inputs: Denovo workflow input dictionary.
        data_root: Resolved data root for relative path resolution.

    Returns:
        Keyword-argument dictionary passed to BoltzGen design runner.
    """
    """
    Build kwargs for design_with_boltzgen from notebook user inputs.
    Handles either YAML-driven mode or explicit field mode.
    """
    yaml_spec_path = resolve_optional_path(data_root, user_inputs.get("design_spec_yaml"))
    if yaml_spec_path is not None:
        kwargs = boltzgen_yaml_to_design_kwargs(
            yaml_spec_path,
            include_query_fields=bool(user_inputs.get("yaml_include_query_fields", False)),
        )
        kwargs["n_structures"] = int(user_inputs.get("n_structures", 16))
        return kwargs

    target_structure_path = resolve_optional_path(data_root, user_inputs.get("target_structure_path"))
    target_fasta_path = resolve_optional_path(data_root, user_inputs.get("target_fasta_path"))
    design_structure_path = resolve_optional_path(data_root, user_inputs.get("design_structure_path"))
    design_fasta_path = resolve_optional_path(data_root, user_inputs.get("design_fasta_path"))
    design_spec_path = resolve_optional_path(data_root, user_inputs.get("design_spec_path"))
    ligand_smiles_path = resolve_optional_path(data_root, user_inputs.get("ligand_smiles_path"))

    return {
        "target_chain_id": str(user_inputs.get("target_chain_id", "A")),
        "target_structure_path": target_structure_path,
        "target_pdb_id": str(user_inputs.get("target_pdb_id", "")).strip() or None,
        "target_sequence": str(user_inputs.get("target_sequence", "")).strip() or None,
        "target_fasta_path": target_fasta_path,
        "target_is_cyclic": bool(user_inputs.get("target_is_cyclic", False)),
        "design_chain_id": str(user_inputs.get("design_chain_id", "B")),
        "design_structure_path": design_structure_path,
        "design_pdb_id": str(user_inputs.get("design_pdb_id", "")).strip() or None,
        "design_source_chain_id": str(user_inputs.get("design_source_chain_id", "")).strip() or None,
        "design_sequence": str(user_inputs.get("design_sequence", "")).strip() or None,
        "design_fasta_path": design_fasta_path,
        "design_is_cyclic": bool(user_inputs.get("design_is_cyclic", False)),
        "design_group_id": int(user_inputs.get("design_group_id", 1)),
        "ligand_smiles": _as_list(user_inputs.get("ligand_smiles")),
        "ligand_smiles_path": ligand_smiles_path,
        "ligand_ccds": _as_list(user_inputs.get("ligand_ccds")),
        "ligand_ccd_path": resolve_optional_path(data_root, user_inputs.get("ligand_ccd_path")),
        "design_spec_path": design_spec_path,
        "n_structures": int(user_inputs.get("n_structures", 16)),
    }


def run_denovo_sequence_design(
    user_inputs: Dict[str, Any],
    *,
    data_root: Path,
    out_dir: Path,
    out_summary_json: Path,
) -> Dict[str, Any]:
    """
    Execute de novo sequence design workflow (BoltzGen + optional postdesign).

    Args:
        root_key: Logical data root key.
        user_inputs: Denovo workflow input dictionary.
        run_postdesign: Whether to run postdesign scoring/refolding pipeline.

    Returns:
        Dict containing design outputs, paths, and optional postdesign artifacts.
    """
    tool = str(user_inputs.get("design_tool", "boltzgen_openprotein")).strip().lower()
    if tool != "boltzgen_openprotein":
        return {
            "tool": tool,
            "implemented": False,
            "message": f"Unsupported design tool: {tool}",
        }

    design_kwargs: Dict[str, Any] = build_denovo_design_kwargs(user_inputs, data_root=data_root)
    design_kwargs.update(
        {
            "out_dir": out_dir,
            "out_summary_json": out_summary_json,
            "output_prefix": str(user_inputs.get("output_tag", "boltzgen_design")).strip() or "boltzgen_design",
        }
    )
    assert_valid_design_with_boltzgen_kwargs(design_kwargs)
    result = design_with_boltzgen(**design_kwargs)

    print('Running ProteinMPNN')
    run_mpnn = bool(user_inputs.get("run_proteinmpnn", False))
    if run_mpnn and result.get("structures") is not None:
        tag = str(user_inputs.get("output_tag", "denovo_design")).strip()
        out_csv = out_dir / f"{tag}_proteinmpnn_sequences.csv"
        try:
            records = run_proteinmpnn_from_structures(
                generated_structures=result["structures"],
                target_chain_id=str(user_inputs.get("target_chain_id", "A")),
                design_chain_id=str(user_inputs.get("design_chain_id", "B")),
                scaffold_sequence=str(user_inputs.get("mpnn_scaffold_sequence", "")).strip() or None,
                num_samples=int(user_inputs.get("proteinmpnn_samples", 8)),
                temperature=float(user_inputs.get("proteinmpnn_temperature", 0.1)),
                seed=int(user_inputs.get("proteinmpnn_seed", 42)),
                out_csv=out_csv,
            )
            result["proteinmpnn_records_preview"] = records[:10]
            result["proteinmpnn_n_records"] = len(records)
            result["proteinmpnn_csv"] = str(out_csv)
        except Exception as exc:
            result["proteinmpnn_error"] = (
                f"{type(exc).__name__}: {exc}. "
                "This commonly happens when one of the requested ProteinMPNN chains is not a protein "
                "(for example ligand-target-only designs)."
            )

    result["tool"] = tool
    result["implemented"] = True
    printable = {k: v for k, v in result.items() if k not in {"job", "structures"}}
    return printable


def postdesign_artifact_paths(postdesign_out_dir: Path, output_tag: str = "") -> Dict[str, Path]:
    """
    Build expected artifact paths for postdesign pipeline outputs.

    Args:
        postdesign_out_dir: Output directory for postdesign artifacts.
        output_tag: Optional filename tag prefix.

    Returns:
        Mapping of artifact labels to paths.
    """
    tag = str(output_tag or "").strip()
    return {
        "mpnn_csv_path": postdesign_out_dir / (f"{tag}_proteinmpnn_sequences.csv" if tag else "proteinmpnn_sequences.csv"),
        "metrics_csv_path": postdesign_out_dir
        / (f"{tag}_proteinmpnn_predicted_structure_metrics.csv" if tag else "proteinmpnn_predicted_structure_metrics.csv"),
        "refold_summary_csv_path": postdesign_out_dir
        / (f"{tag}_proteinmpnn_refold_summary.csv" if tag else "proteinmpnn_refold_summary.csv"),
    }


def run_or_load_postdesign_pipeline(
    *,
    user_inputs: Dict[str, Any],
    generated_structures: List[Any],
    out_dir: Path,
    design_kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run postdesign pipeline or load existing artifacts if available.

    Args:
        sequences: Designed sequence list.
        pdb_paths: Optional template structure paths.
        user_inputs: Denovo workflow input dictionary.
        data_root: Resolved data root.
        output_tag: Optional tag prefix for artifact names.
        force_run: If true, rerun pipeline even when outputs exist.
        run_refold: Whether to run Boltz2 refolding stage.

    Returns:
        Dict with status, artifact paths, and parsed summary metrics.
    """
    postdesign_out_dir = (out_dir / "postdesign").resolve()
    postdesign_out_dir.mkdir(parents=True, exist_ok=True)
    tag = str(user_inputs.get("output_tag", "")).strip()
    paths = postdesign_artifact_paths(postdesign_out_dir, tag)

    postdesign = None
    mpnn_df = None
    metrics_df = None
    refold_summaries_df = None

    if bool(user_inputs.get("run_postdesign_pipeline", True)):
        postdesign = run_proteinmpnn_postdesign_pipeline(
            generated_structures=generated_structures,
            output_tag=tag,
            out_dir=postdesign_out_dir,
            target_chain_id=str(user_inputs.get("target_chain_id", "A")),
            design_chain_id=str(user_inputs.get("design_chain_id", "B")),
            scaffold_sequence=str(user_inputs.get("mpnn_scaffold_sequence", "")).strip() or None,
            num_samples=int(user_inputs.get("proteinmpnn_samples", 8)),
            temperature=float(user_inputs.get("proteinmpnn_temperature", 0.1)),
            seed=int(user_inputs.get("proteinmpnn_seed", 42)),
            run_boltz2_refold=bool(user_inputs.get("postdesign_run_boltz2_refold", False)),
            refold_target_mode=str(user_inputs.get("refold_target_mode", "auto")),
            refold_ligand_smiles=list(user_inputs.get("refold_ligand_smiles", [])),
            refold_ligand_ccds=list(user_inputs.get("refold_ligand_ccds", [])),
            refold_target_structure_path=str(user_inputs.get("refold_target_structure_path", "")).strip() or None,
            refold_target_structure_chain_id=str(user_inputs.get("refold_target_structure_chain_id", "A")),
            design_spec_path=design_kwargs.get("design_spec_path"),
            auto_refold_targets_from_design_spec=bool(user_inputs.get("auto_refold_targets_from_design_spec", True)),
            compute_metrics=bool(user_inputs.get("postdesign_compute_metrics", False)),
        )
        mpnn_df = postdesign.get("mpnn_df")
        metrics_df = postdesign.get("metrics_df")
        refold_summaries_df = postdesign.get("refold_summaries_df")

    if mpnn_df is None and paths["mpnn_csv_path"].exists():
        mpnn_df = safe_read_csv(paths["mpnn_csv_path"])
    if metrics_df is None and paths["metrics_csv_path"].exists():
        metrics_df = safe_read_csv(paths["metrics_csv_path"])
        if {"structure_idx", "sequence_idx"}.issubset(metrics_df.columns):
            metrics_df = metrics_df.set_index(["structure_idx", "sequence_idx"])
    if refold_summaries_df is None and paths["refold_summary_csv_path"].exists():
        refold_summaries_df = safe_read_csv(paths["refold_summary_csv_path"])

    return {
        "postdesign": postdesign,
        "postdesign_out_dir": postdesign_out_dir,
        **paths,
        "mpnn_df": mpnn_df,
        "metrics_df": metrics_df,
        "refold_summaries_df": refold_summaries_df,
    }


def render_overlay_views(
    *,
    ranking_df: Any,
    refold_summaries_df: Any,
    out_dir: Path,
    user_inputs: Dict[str, Any],
    n_rows: int = 1,
) -> List[Any]:
    from pathlib import Path as _Path

    from agentic_protein_design.tools.utils.struct_utils import visualize_overlay_structures

    if refold_summaries_df is None or len(refold_summaries_df) == 0:
        return []
    rows = ranking_df.head(max(1, int(n_rows)))
    prefix = str(user_inputs.get("output_tag", "boltzgen_design")).strip() or "boltzgen_design"
    views = []
    for _, top in rows.iterrows():
        structure_idx = int(top["structure_idx"])
        sequence_idx = int(top["sequence_idx"])

        original_pdb = (out_dir / f"{prefix}_{structure_idx:03d}.pdb").resolve()
        if not original_pdb.is_file():
            original_pdb = (out_dir / f"boltzgen_design_{structure_idx:03d}.pdb").resolve()
        if not original_pdb.is_file():
            print(
                f"Skipping overlay s={structure_idx} q={sequence_idx}: missing generated structure PDB "
                f"({original_pdb})."
            )
            continue

        refold_row = refold_summaries_df[
            (refold_summaries_df["structure_idx"] == structure_idx)
            & (refold_summaries_df["sequence_idx"] == sequence_idx)
        ]
        if refold_row.empty:
            continue

        refold_record = refold_row.iloc[0]
        out_pdb_text = str(refold_record.get("out_pdb", "")).strip()
        predicted_pdb = _Path(out_pdb_text).resolve() if out_pdb_text else None
        if predicted_pdb is None or not predicted_pdb.is_file():
            predicted_cif_text = str(refold_record.get("out_cif", "")).strip()
            predicted_cif = _Path(predicted_cif_text).resolve() if predicted_cif_text else None
            predicted_pdb = predicted_cif.with_suffix(".pdb").resolve() if predicted_cif else None

        if predicted_pdb is None or not predicted_pdb.is_file():
            print(
                f"Skipping overlay s={structure_idx} q={sequence_idx}: missing refold PDB "
                f"({predicted_pdb})."
            )
            continue

        view_overlay = visualize_overlay_structures(
            [str(original_pdb), str(predicted_pdb)],
            protein_chain_id=str(user_inputs.get("design_chain_id", "A")),
            ligand_chain_id=str(user_inputs.get("target_chain_id", "B")),
            protein_colors=[
                str(user_inputs.get("overlay_generated_color", "deepskyblue")),
                str(user_inputs.get("overlay_predicted_color", "tomato")),
            ],
            protein_opacities=[
                float(user_inputs.get("overlay_generated_opacity", 1.0)),
                float(user_inputs.get("overlay_predicted_opacity", 0.35)),
            ],
            protein_radius_scales=[
                float(user_inputs.get("overlay_generated_radius_scale", 1.0)),
                float(user_inputs.get("overlay_predicted_radius_scale", 0.85)),
            ],
            ligand_color="lightgrey",
            show_target_representation=bool(user_inputs.get("overlay_show_target_representation", False)),
            target_representation=str(user_inputs.get("overlay_target_representation", "ball+stick")),
            show_res_near_target=bool(user_inputs.get("overlay_show_res_near_target", True)),
            near_distance_angstrom=6,
        )
        views.append(view_overlay)
    return views


if __name__ == "__main__":
    from agentic_protein_design.core.pipeline_utils import print_run_summary, resolve_repo_root
    from project_config.variables import address_dict, subfolders
    from agentic_protein_design.tools.openprotein import validate_design_with_boltzgen_kwargs

    root_key = "examples"
    run_postdesign = True
    run_selection = True

    user_inputs = {
        "design_tool": "boltzgen_openprotein",
        "design_spec_yaml": "",
        "yaml_include_query_fields": False,
        "design_chain_id": "A",
        "design_structure_path": "",
        "design_pdb_id": "",
        "design_source_chain_id": "",
        "design_sequence": "",
        "design_fasta_path": "",
        "design_is_cyclic": False,
        "design_group_id": 1,
        "target_chain_id": "B",
        "target_structure_path": "",
        "target_pdb_id": "",
        "target_sequence": "",
        "target_fasta_path": "",
        "target_is_cyclic": False,
        "ligand_smiles": [],
        "ligand_smiles_path": "",
        "ligand_ccds": [],
        "ligand_ccd_path": "",
        "design_spec_path": "",
        "n_structures": 4,
        "run_proteinmpnn": False,
        "proteinmpnn_samples": 5,
        "proteinmpnn_temperature": 0.1,
        "proteinmpnn_seed": 42,
        "mpnn_scaffold_sequence": "",
        "run_postdesign_pipeline": run_postdesign,
        "postdesign_run_boltz2_refold": True,
        "postdesign_compute_metrics": True,
        "refold_target_mode": "auto",
        "refold_ligand_smiles": [],
        "refold_ligand_ccds": [],
        "refold_target_structure_path": "",
        "refold_target_structure_chain_id": "A",
        "auto_refold_targets_from_design_spec": True,
        "output_tag": "boltzgen_design",
        "filter_rmsd_max": 2.5,
        "filter_ipae_max": 10.0,
        "filter_binder_rmsd_max": 1.0,
        "filter_binder_plddt_min": 80.0,
    }

    repo_root = resolve_repo_root(__file__)
    data_root = (repo_root / address_dict[root_key]).resolve()
    processed_dir = (data_root / subfolders["processed"]).resolve()
    step_dir = (processed_dir / "02_run_denovo_sequence_design").resolve()
    out_dir = (step_dir / str(user_inputs.get("output_tag", "boltzgen_design"))).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_summary = (out_dir / f"{user_inputs['output_tag']}_summary.json").resolve()

    design_kwargs = build_denovo_design_kwargs(user_inputs, data_root=data_root)
    design_kwargs.update({"out_dir": out_dir, "out_summary_json": out_summary})

    validation_report = validate_design_with_boltzgen_kwargs(design_kwargs)
    if not validation_report["ok"]:
        raise ValueError(
            "Pre-run validation failed: "
            + "; ".join(str(err) for err in validation_report.get("errors", []))
        )

    tool = str(user_inputs.get("design_tool", "boltzgen_openprotein")).strip().lower()
    if tool != "boltzgen_openprotein":
        raise ValueError(f"Unsupported design tool: {tool}")

    design_kwargs["output_prefix"] = str(user_inputs.get("output_tag", "boltzgen_design")).strip() or "boltzgen_design"
    assert_valid_design_with_boltzgen_kwargs(design_kwargs)
    design_run_result = design_with_boltzgen(**design_kwargs)
    result = {
        **{k: v for k, v in design_run_result.items() if k not in {"job", "structures"}},
        "tool": tool,
        "implemented": True,
    }

    postdesign_payload = None
    selection_summary = None
    if run_postdesign:
        generated_structures = design_run_result.get("structures")
        if generated_structures is None:
            raise RuntimeError("Design result does not include generated structures for postdesign.")

        postdesign_payload = run_or_load_postdesign_pipeline(
            user_inputs=user_inputs,
            generated_structures=generated_structures,
            out_dir=out_dir,
            design_kwargs=design_kwargs,
        )

        if run_selection:
            metrics_df = postdesign_payload.get("metrics_df")
            if metrics_df is not None and len(metrics_df):
                from agentic_protein_design.tools.openprotein import filter_and_select_designs

                df_filtered, df_selected = filter_and_select_designs(
                    metrics_df,
                    rmsd_max=float(user_inputs.get("filter_rmsd_max", 2.5)),
                    ipae_max=float(user_inputs.get("filter_ipae_max", 10.0)),
                    binder_rmsd_max=float(user_inputs.get("filter_binder_rmsd_max", 1.0)),
                    binder_plddt_min=float(user_inputs.get("filter_binder_plddt_min", 80.0)),
                    rank_by="ipae",
                )
                selection_summary = {
                    "n_filtered_rows": int(len(df_filtered)),
                    "n_selected_rows": int(len(df_selected)),
                }

    print_run_summary(
        {
            "root_key": root_key,
            "data_root": data_root,
            "out_dir": out_dir,
            "out_summary": out_summary,
            "validation_ok": validation_report["ok"],
            "validation_warnings": validation_report.get("warnings", []),
            "design_result": {k: v for k, v in result.items() if k != "structures"},
            "postdesign_out_dir": None if postdesign_payload is None else postdesign_payload.get("postdesign_out_dir"),
            "mpnn_csv_path": None if postdesign_payload is None else postdesign_payload.get("mpnn_csv_path"),
            "metrics_csv_path": None if postdesign_payload is None else postdesign_payload.get("metrics_csv_path"),
            "refold_summary_csv_path": None if postdesign_payload is None else postdesign_payload.get("refold_summary_csv_path"),
            "selection_summary": selection_summary,
        }
    )
