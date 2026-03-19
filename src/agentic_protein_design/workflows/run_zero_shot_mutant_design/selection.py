from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .compile import infer_position_from_mutation


def _parse_mutation_token(mut: str) -> Tuple[str | None, int | None, str | None]:
    token = str(mut or "").strip()
    if len(token) < 3:
        return None, None, None
    pos = infer_position_from_mutation(token)
    if pos is None:
        return None, None, None
    wt = token[0]
    mt = token[-1]
    return wt, pos, mt


def apply_mutation_constraints(
    scores_long: pd.DataFrame,
    user_inputs: Mapping[str, Any],
) -> pd.DataFrame:
    """Apply basic mutation-level constraints to a long score table."""
    # Section 1: annotate mutation tokens for filtering.
    out = scores_long.copy()
    parsed = out["mutations"].map(_parse_mutation_token)
    out["wt_aa"] = parsed.map(lambda x: x[0])
    out["position"] = parsed.map(lambda x: x[1])
    out["mt_aa"] = parsed.map(lambda x: x[2])

    # Section 2: apply user constraints.
    pos_to_exclude = set(int(x) for x in (user_inputs.get("pos_to_exclude") or []))
    allowed_positions = set(int(x) for x in (user_inputs.get("allowed_positions") or []))
    allowed_mut_aas = set(str(x) for x in (user_inputs.get("allowed_mut_aas") or []))
    if pos_to_exclude:
        out = out.loc[~out["position"].isin(pos_to_exclude)]
    if allowed_positions:
        out = out.loc[out["position"].isin(allowed_positions)]
    if allowed_mut_aas:
        out = out.loc[out["mt_aa"].isin(allowed_mut_aas)]
    return out.reset_index(drop=True)


def _zscore_by_group(df: pd.DataFrame, group_key: str) -> pd.Series:
    # Section 1: compute z-score within each group.
    out = pd.Series(np.nan, index=df.index, dtype=float)
    for _, g in df.groupby(group_key):
        vals = g["y_prime"].astype(float)
        mu = float(vals.mean())
        sigma = float(vals.std(ddof=0))
        if sigma <= 0:
            out.loc[g.index] = 0.0
        else:
            out.loc[g.index] = (vals - mu) / sigma
    return out


def rank_and_select_mutants_prototype(
    scores_long: pd.DataFrame,
    user_inputs: Mapping[str, Any],
) -> pd.DataFrame:
    """
    Prototype selection using PLM scores + constraints.

    Protocol implementation:
    - convert LLR to fold-change-like y' = exp(LLR)
    - compute z-scores by substitution type and destination AA
    - tiered FC ranking for non-structure ensemble
    - optional structure-informed y' tie-break
    - apply top_n and max_num_mut_per_pos
    """
    # Section 1: constrain to PLM LLR records and apply user filters.
    if scores_long is None or scores_long.empty:
        return pd.DataFrame()
    work = scores_long.copy()
    work = work.loc[work["score_type"].str.upper() == "LLR"].copy()
    if work.empty:
        return pd.DataFrame()
    work = apply_mutation_constraints(work, user_inputs)
    if work.empty:
        return pd.DataFrame()

    # Section 2: derive protocol features.
    work["y_prime"] = np.exp(work["score_raw"].astype(float))
    work["substitution_type"] = work["wt_aa"].astype(str) + ">" + work["mt_aa"].astype(str)
    work["z_substitution_type"] = _zscore_by_group(work, "substitution_type")
    work["z_to_aa"] = _zscore_by_group(work, "mt_aa")

    # Section 3: split non-structure vs structure-informed model sets.
    struct_models = set(str(x) for x in (user_inputs.get("structure_informed_models") or []))
    non_struct = work.loc[~work["model_name"].isin(struct_models)].copy()
    struct = work.loc[work["model_name"].isin(struct_models)].copy()

    # Section 4: aggregate FC/z metrics at mutation level.
    agg = non_struct.groupby(["position", "mutations"], dropna=False).agg(
        n_models=("model_name", "nunique"),
        count_yprime_gt1=("y_prime", lambda s: int((s > 1.0).sum())),
        mean_yprime=("y_prime", "mean"),
        mean_z_sub_type=("z_substitution_type", "mean"),
        mean_z_to_aa=("z_to_aa", "mean"),
    ).reset_index()
    if agg.empty:
        return pd.DataFrame()
    agg["has_positive_model"] = (agg["count_yprime_gt1"] > 0).astype(int)

    if not struct.empty:
        struct_agg = struct.groupby(["position", "mutations"], dropna=False).agg(
            structure_mean_yprime=("y_prime", "mean"),
            structure_mean_z=("z_substitution_type", "mean"),
        ).reset_index()
        agg = agg.merge(struct_agg, on=["position", "mutations"], how="left")
    else:
        agg["structure_mean_yprime"] = np.nan
        agg["structure_mean_z"] = np.nan

    # Section 5: ranking mode (FC default, z-score optional).
    ranking_mode = str(user_inputs.get("ranking_mode", "fc")).strip().lower()
    if ranking_mode == "zscore":
        agg = agg.sort_values(
            by=["mean_z_sub_type", "mean_z_to_aa"],
            ascending=[False, False],
        )
    else:
        # Two-tier FC rank:
        # 1) mutations with any model y'>1, ranked by count then mean y'
        # 2) remaining mutations ranked by mean y'
        agg = agg.sort_values(
            by=["has_positive_model", "count_yprime_gt1", "mean_yprime", "structure_mean_yprime"],
            ascending=[False, False, False, False],
        )

    # Section 6: shortlist with simple diversity cap.
    top_n = int(user_inputs.get("top_n", 200))
    max_per_pos = int(user_inputs.get("max_num_mut_per_pos", 2))
    selected_rows: List[pd.Series] = []
    per_pos_count: Dict[int, int] = {}
    for _, row in agg.iterrows():
        pos = int(row["position"]) if pd.notna(row["position"]) else -1
        if per_pos_count.get(pos, 0) >= max_per_pos:
            continue
        selected_rows.append(row)
        per_pos_count[pos] = per_pos_count.get(pos, 0) + 1
        if len(selected_rows) >= top_n:
            break
    if not selected_rows:
        return pd.DataFrame(columns=agg.columns)
    out = pd.DataFrame(selected_rows).reset_index(drop=True)
    out["selection_rank"] = np.arange(1, len(out) + 1)
    return out

