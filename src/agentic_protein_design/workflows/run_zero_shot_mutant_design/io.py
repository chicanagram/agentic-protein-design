from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import pandas as pd

try:
    from agentic_protein_design.core.paths import join_data_path, setup_data_root
except ModuleNotFoundError:  # pragma: no cover
    import sys

    _repo_root = Path(__file__).resolve().parents[4]
    _src_root = _repo_root / "src"
    if str(_src_root) not in sys.path:
        sys.path.insert(0, str(_src_root))
    from agentic_protein_design.core.paths import join_data_path, setup_data_root


def resolve_paths(user_inputs: Mapping[str, Any], *, repo_root: Path) -> Dict[str, Path]:
    """Resolve canonical roots and key workflow directories from user_inputs."""
    # Section 1: resolve root via shared core path helpers.
    root_key = str(user_inputs.get("root_key", "")).strip()
    if not root_key:
        raise ValueError("user_inputs['root_key'] is required.")
    data_root, _ = setup_data_root(
        root_key=root_key,
        required_subfolders=[],
        project_root=Path(repo_root).resolve(),
    )

    # Section 2: construct deterministic directory paths.
    data_subfolder = str(user_inputs.get("data_subfolder", "")).strip().strip("/")
    expdata_dir = join_data_path(data_root, "expdata", data_subfolder, "")
    enc_dir = join_data_path(data_root, "encodings", data_subfolder, "")
    llr_cache_dir = join_data_path(data_root, "encodings", "LLR", "")
    proposal_dir = join_data_path(data_root, "mutagenesis_proposal", data_subfolder, "")
    Path(proposal_dir).mkdir(parents=True, exist_ok=True)
    return {
        "repo_root": Path(repo_root).resolve(),
        "data_root": data_root,
        "expdata_dir": Path(expdata_dir),
        "enc_dir": Path(enc_dir),
        "llr_cache_dir": Path(llr_cache_dir),
        "proposal_dir": Path(proposal_dir),
    }


def _prefixed(user_inputs: Mapping[str, Any], basename: str) -> str:
    # Section 1: prepend optional filename prefix.
    return f"{str(user_inputs.get('filename_prefix', '') or '')}{basename}"


def _llr_primary_and_fallback_paths(
    user_inputs: Mapping[str, Any],
    paths: Mapping[str, Path],
    model_name: str,
) -> tuple[Path, Path, Path]:
    # Section 1: build primary (with marginal suffix), alt-case WT suffix, and fallback (no suffix).
    marginal = str(user_inputs.get("marginal_type", "") or "").strip()
    suffix = f"-{marginal}" if marginal else ""
    suffix_alt = "-WT" if marginal.lower() == "wt" else suffix
    stem_primary = _prefixed(user_inputs, f"{model_name}_LLR{suffix}")
    stem_alt = _prefixed(user_inputs, f"{model_name}_LLR{suffix_alt}")
    stem_fallback = _prefixed(user_inputs, f"{model_name}_LLR")
    primary = paths["llr_cache_dir"] / f"{stem_primary}_vect.csv"
    alt = paths["llr_cache_dir"] / f"{stem_alt}_vect.csv"
    fallback = paths["llr_cache_dir"] / f"{stem_fallback}_vect.csv"
    return primary, alt, fallback


def _resolve_existing_with_fallback(primary: Path, alt: Path, fallback: Path) -> tuple[Path, bool, bool]:
    # Section 1: prefer primary suffix path; then alt-case WT suffix; then unsuffixed fallback.
    if primary.exists():
        return primary, True, False
    if alt.exists():
        return alt, True, False
    if fallback.exists():
        return fallback, True, True
    return primary, False, False


def _expected_artifacts(user_inputs: Mapping[str, Any], paths: Mapping[str, Path]) -> List[Dict[str, Any]]:
    # Section 1: build deterministic artifact list from requested score types.
    out: List[Dict[str, Any]] = []
    models = [str(x) for x in user_inputs.get("plm_models", [])]
    score_types = dict(user_inputs.get("score_types_to_run", {}))
    marginal = str(user_inputs.get("marginal_type", "masked"))

    for model in models:
        if score_types.get("plm_llr", False):
            llr_primary, llr_alt, llr_fallback = _llr_primary_and_fallback_paths(user_inputs, paths, model)
            llr_resolved, llr_exists, used_fallback = _resolve_existing_with_fallback(llr_primary, llr_alt, llr_fallback)
            out.append(
                {
                    "artifact": f"{model} LLR vect",
                    "path": llr_resolved,
                    "required": True,
                    "exists": llr_exists,
                    "used_fallback_no_suffix": used_fallback,
                    "path_primary": llr_primary,
                    "path_alt": llr_alt,
                    "path_fallback": llr_fallback,
                }
            )
            out.append(
                {
                    "artifact": f"{model} LLR map png",
                    "path": paths["llr_cache_dir"] / f"{_prefixed(user_inputs, f'{model}_LLR-{marginal}')}_map.png",
                    "required": False,
                }
            )
        if score_types.get("plm_meanpll", False):
            out.append(
                {
                    "artifact": f"{model} meanPLL csv",
                    "path": paths["enc_dir"] / f"{_prefixed(user_inputs, f'{model}_meanPLL-{marginal}')}.csv",
                    "required": True,
                }
            )

    if score_types.get("proteinmpnn", False):
        out.append(
            {
                "artifact": "ProteinMPNN scores",
                "path": paths["enc_dir"] / f"{_prefixed(user_inputs, 'proteinmpnn_scores')}.csv",
                "required": True,
            }
        )
    if score_types.get("spurs", False):
        out.append(
            {
                "artifact": "SPURS scores",
                "path": paths["enc_dir"] / f"{_prefixed(user_inputs, 'spurs_scores')}.csv",
                "required": True,
            }
        )
    if score_types.get("structure_annotations", False):
        out.append(
            {
                "artifact": "mutation annotations",
                "path": paths["enc_dir"] / f"{_prefixed(user_inputs, 'mutation_annotations')}.csv",
                "required": False,
            }
        )
    return out


def get_expected_artifacts(
    user_inputs: Mapping[str, Any],
    paths: Mapping[str, Path],
) -> List[Dict[str, Any]]:
    """Public wrapper for deterministic score/annotation artifact expectations."""
    return _expected_artifacts(user_inputs, paths)


def check_required_artifacts(
    user_inputs: Mapping[str, Any],
    paths: Mapping[str, Path],
) -> pd.DataFrame:
    """Return existence status for score/annotation artifacts requested in config."""
    # Section 1: enumerate expected files and mark existence.
    rows = _expected_artifacts(user_inputs, paths)
    table = pd.DataFrame(rows)
    if table.empty:
        return pd.DataFrame(columns=["artifact", "path", "required", "exists", "missing_for_run"])
    if "exists" not in table.columns:
        table["exists"] = table["path"].map(lambda p: Path(p).exists())
    else:
        table["exists"] = table["exists"].astype(bool)
    table["missing_for_run"] = (~table["exists"]) & table["required"]
    table["path"] = table["path"].map(str)
    if "path_primary" in table.columns:
        table["path_primary"] = table["path_primary"].map(lambda p: str(p) if pd.notna(p) else "")
    if "path_alt" in table.columns:
        table["path_alt"] = table["path_alt"].map(lambda p: str(p) if pd.notna(p) else "")
    if "path_fallback" in table.columns:
        table["path_fallback"] = table["path_fallback"].map(lambda p: str(p) if pd.notna(p) else "")
    return table


def load_score_tables(artifact_status: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Load available score tables from existing artifact paths."""
    # Section 1: validate and early-return on empty table.
    if artifact_status is None or artifact_status.empty:
        return {}
    required_cols = {"artifact", "path", "exists"}
    if not required_cols.issubset(set(artifact_status.columns)):
        raise ValueError(f"artifact_status must contain columns {sorted(required_cols)}")

    # Section 2: load existing CSV score artifacts only.
    tables: Dict[str, pd.DataFrame] = {}
    existing = artifact_status.loc[artifact_status["exists"] == True]
    for _, row in existing.iterrows():
        artifact = str(row["artifact"])
        p = Path(str(row["path"]))
        if p.suffix.lower() != ".csv":
            continue
        if any(tag in artifact for tag in ["LLR vect", "meanPLL csv", "ProteinMPNN scores", "SPURS scores"]):
            try:
                tables[artifact] = pd.read_csv(p)
            except Exception:
                continue
    return tables


def load_base_data(
    user_inputs: Mapping[str, Any],
    paths: Mapping[str, Path],
    artifact_status: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Load lightweight base inputs (WT, optional data tables) and return run context."""
    # Section 1: initialize context.
    context: Dict[str, Any] = {
        "wt_sequence": str(user_inputs.get("wt_sequence", "") or "").strip(),
        "candidate_df": None,
        "conservation_df": None,
        "structure_path": None,
        "ligand_path": None,
        "missing_artifacts": [],
    }

    # Section 2: optional file-backed WT sequence.
    wt_filename = str(user_inputs.get("wt_sequence_filename", "") or "").strip()
    if wt_filename:
        wt_path = paths["expdata_dir"] / wt_filename
        context["wt_sequence_path"] = wt_path

    # Section 3: optional candidate/conservation data loading.
    cand_filename = str(user_inputs.get("candidate_sequences_filename", "") or "").strip()
    if cand_filename:
        cand_path = paths["expdata_dir"] / cand_filename
        context["candidate_path"] = cand_path
        if cand_path.exists():
            context["candidate_df"] = pd.read_csv(cand_path)

    cons_filename = str(user_inputs.get("conservation_filename", "") or "").strip()
    if cons_filename:
        cons_path = paths["expdata_dir"] / cons_filename
        context["conservation_path"] = cons_path
        if cons_path.exists():
            context["conservation_df"] = pd.read_csv(cons_path)

    # Section 4: optional structure/ligand paths.
    structure_filename = str(user_inputs.get("structure_filename", "") or "").strip()
    if structure_filename:
        context["structure_path"] = paths["expdata_dir"] / structure_filename
    ligand_filename = str(user_inputs.get("ligand_filename", "") or "").strip()
    if ligand_filename:
        context["ligand_path"] = paths["expdata_dir"] / ligand_filename

    # Section 5: summarize missing run-critical artifacts.
    if artifact_status is not None and not artifact_status.empty:
        missing_df = artifact_status.loc[artifact_status["missing_for_run"] == True, ["artifact", "path"]]
        context["missing_artifacts"] = missing_df.to_dict(orient="records")
    return context
