from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

ID_COLUMN_CANDIDATES = {
    "mutations": ["mutations", "mutation"],
    "resnum": ["resnum", "res_num", "position"],
}

SCORE_SOURCE_COLUMN_REGISTRY: Dict[tuple[str, str], Dict[str, Any]] = {
    # Section 0A: PLM score sources.
    ("plm_llr", "*"): {
        "value_columns": {"LLR": ["LLR", "llr"]},
        "default_value_column": "LLR",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
    ("plm_meanpll", "*"): {
        "value_columns": {"meanPLL": ["meanPLL", "mean_pll", "meanpll"]},
        "default_value_column": "meanPLL",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
    # Section 0B: structure / stability score sources.
    ("stability_ddg", "SPURS"): {
        "value_columns": {"ddg": ["ddg", "DDG"]},
        "default_value_column": "ddg",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
    ("proteinmpnn", "proteinmpnn"): {
        "value_columns": {"score": ["score", "proteinmpnn_score", "log_prob", "mean_log_prob"]},
        "default_value_column": "score",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
    # Section 0C: structure annotation sources.
    ("structure_annotations", "distance"): {
        "value_columns": {
            "min_dist_to_lig": ["min_dist_to_lig", "min_dist_lig", "min_distance_lig", "min_dist_to_UNK", "min_dist_UNK"]
        },
        "default_value_column": "min_dist_to_lig",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
    ("structure_annotations", "residue_properties"): {
        "value_columns": {
            "kd_hydro": ["kd_hydro"],
            "hw_polarity": ["hw_polarity"],
            "aa_vol": ["aa_vol"],
        },
        "default_value_column": "kd_hydro",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
    ("structure_annotations", "*"): {
        "default_value_column": "annotation_value",
        "id_column_candidates": ID_COLUMN_CANDIDATES,
    },
}


def _normalize_score_targets(value: Any, *, true_default: Optional[Sequence[str]] = None) -> List[str]:
    # Section 1: normalize user-provided score selectors into a string list.
    if value in (None, False):
        return []
    if value is True:
        return [str(x) for x in (true_default or []) if str(x).strip()]
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Sequence):
        return [str(x) for x in value if str(x).strip()]
    return []


def build_user_inputs(
    *,
    root_key: str,
    output_data_subfolder: str,
    filename_prefix: str = "",
    output_filename_suffix: str = "",
    wt_sequence: str = "",
    ligand: str = "",
    plm_models: Optional[Sequence[str]] = None,
    marginal_type: str = "masked",
    score_types_to_run: Optional[Mapping[str, Any]] = None,
    pos_to_exclude: Optional[Sequence[int]] = None,
    allowed_positions: Optional[Sequence[int]] = None,
    allowed_mut_aas: Optional[Sequence[str]] = None,
    mutations_to_exclude: Optional[Sequence[str]] = None,
    col_constraints: str = "",
    dist_to_lig_thres: Optional[float] = None,
    dist_to_lig_filter_direction: str = "le",
    top_n: int = 200,
    max_num_mut_per_pos: int = 2,
) -> Dict[str, Any]:
    """Build a normalized config payload for zero-shot mutant design notebooks."""
    # Section 1: normalize model and score-type defaults.
    models = list(plm_models) if plm_models is not None else ["esm2-650m", "esmc-600m"]
    score_targets: Dict[str, List[str]] = {
        "plm_llr": [str(x) for x in models],
        "plm_meanpll": [],
        "proteinmpnn": [],
        "stability_ddg": [],
        "spurs": [],
        "structure_annotations": ["distance"],
    }
    if score_types_to_run is not None:
        for k, v in score_types_to_run.items():
            key = str(k)
            default = models if key in {"plm_llr", "plm_meanpll"} else []
            score_targets[key] = _normalize_score_targets(v, true_default=default)

    # Section 2: normalize constraint fields.
    direction = str(dist_to_lig_filter_direction or "le").strip().lower()
    if direction not in {"le", "ge"}:
        raise ValueError("dist_to_lig_filter_direction must be 'le' or 'ge'.")

    # Section 3: return immutable-style config dictionary.
    return {
        "root_key": str(root_key),
        "output_data_subfolder": str(output_data_subfolder or "").strip(),
        "filename_prefix": str(filename_prefix or ""),
        "output_filename_suffix": str(output_filename_suffix or ""),
        "wt_sequence": str(wt_sequence or "").strip(),
        "ligand": str(ligand or "").strip(),
        "plm_models": models,
        "marginal_type": str(marginal_type),
        "score_types_to_run": score_targets,
        "pos_to_exclude": [int(x) for x in (pos_to_exclude or [])],
        "allowed_positions": [int(x) for x in (allowed_positions or [])],
        "allowed_mut_aas": [str(x) for x in (allowed_mut_aas or [])],
        "mutations_to_exclude": [str(x) for x in (mutations_to_exclude or [])],
        "col_constraints": str(col_constraints or "").strip(),
        "dist_to_lig_thres": None if dist_to_lig_thres is None else float(dist_to_lig_thres),
        "dist_to_lig_filter_direction": direction,
        "top_n": int(top_n),
        "max_num_mut_per_pos": int(max_num_mut_per_pos),
        # Section 3B: optional filenames for future expansion.
        "wt_sequence_filename": "",
        "candidate_sequences_filename": "",
        "conservation_filename": "",
        "structure_filename": "",
        "ligand_filename": "",
    }
