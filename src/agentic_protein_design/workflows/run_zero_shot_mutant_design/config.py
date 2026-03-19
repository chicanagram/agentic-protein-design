from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence


def build_user_inputs(
    *,
    root_key: str,
    data_subfolder: str,
    filename_prefix: str = "",
    wt_sequence: str = "",
    plm_models: Optional[Sequence[str]] = None,
    marginal_type: str = "masked",
    score_types_to_run: Optional[Mapping[str, bool]] = None,
    pos_to_exclude: Optional[Sequence[int]] = None,
    allowed_positions: Optional[Sequence[int]] = None,
    allowed_mut_aas: Optional[Sequence[str]] = None,
    dist_to_lig_thres: Optional[float] = None,
    dist_to_lig_filter_direction: str = "le",
    top_n: int = 200,
    max_num_mut_per_pos: int = 2,
) -> Dict[str, Any]:
    """Build a normalized config payload for zero-shot mutant design notebooks."""
    # Section 1: normalize model and score-type defaults.
    models = list(plm_models) if plm_models is not None else ["esm2-650m", "esmc-600m"]
    score_flags = {
        "plm_llr": True,
        "plm_meanpll": False,
        "proteinmpnn": False,
        "spurs": False,
        "structure_annotations": True,
    }
    if score_types_to_run is not None:
        score_flags.update({str(k): bool(v) for k, v in score_types_to_run.items()})

    # Section 2: normalize constraint fields.
    direction = str(dist_to_lig_filter_direction or "le").strip().lower()
    if direction not in {"le", "ge"}:
        raise ValueError("dist_to_lig_filter_direction must be 'le' or 'ge'.")

    # Section 3: return immutable-style config dictionary.
    return {
        "root_key": str(root_key),
        "data_subfolder": str(data_subfolder or "").strip(),
        "filename_prefix": str(filename_prefix or ""),
        "wt_sequence": str(wt_sequence or "").strip(),
        "plm_models": models,
        "marginal_type": str(marginal_type),
        "score_types_to_run": score_flags,
        "pos_to_exclude": [int(x) for x in (pos_to_exclude or [])],
        "allowed_positions": [int(x) for x in (allowed_positions or [])],
        "allowed_mut_aas": [str(x) for x in (allowed_mut_aas or [])],
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
