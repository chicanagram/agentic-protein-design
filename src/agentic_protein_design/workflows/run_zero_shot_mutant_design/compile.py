from __future__ import annotations

import re
from typing import Dict, Iterable, Mapping, Sequence

import pandas as pd


def infer_position_from_mutation(mutation: str) -> int | None:
    """Infer 1-based position index from a mutation token like A123P."""
    m = re.search(r"(\d+)", str(mutation or ""))
    return int(m.group(1)) if m else None


def standardize_score_table(
    df: pd.DataFrame,
    *,
    source_name: str,
    model_name: str,
    score_type: str,
) -> pd.DataFrame:
    """Convert a model score table into a normalized long schema."""
    # Section 1: detect mutation/score columns.
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    mut_col = cols_lower.get("mutations", cols_lower.get("mutation"))
    if mut_col is None:
        raise ValueError(f"[{source_name}] missing mutations column.")
    score_col = cols_lower.get("llr", cols_lower.get("meanpll"))
    if score_col is None:
        raise ValueError(f"[{source_name}] missing score column (LLR/meanPLL).")
    pos_col = cols_lower.get("position")

    # Section 2: build normalized records.
    out = pd.DataFrame(
        {
            "mutations": df[mut_col].astype(str),
            "score_raw": pd.to_numeric(df[score_col], errors="coerce"),
            "model_name": str(model_name),
            "score_type": str(score_type),
            "score_source": str(source_name),
        }
    )
    if pos_col is not None:
        out["position"] = pd.to_numeric(df[pos_col], errors="coerce").astype("Int64")
    else:
        out["position"] = out["mutations"].map(infer_position_from_mutation).astype("Int64")
    out = out.dropna(subset=["mutations", "score_raw"])
    return out


def compile_scores_by_fields(
    score_tables: Mapping[str, pd.DataFrame],
    *,
    merge_fields: Sequence[str] = ("position", "mutations"),
) -> pd.DataFrame:
    """Compile multiple score tables into one wide table merged on selected fields."""
    # Section 1: normalize each table to have merge keys and one score column.
    prepared = []
    for name, df in score_tables.items():
        if df is None or df.empty:
            continue
        work = df.copy()
        if "position" not in work.columns and "mutations" in work.columns:
            work["position"] = work["mutations"].map(infer_position_from_mutation)
        missing = [f for f in merge_fields if f not in work.columns]
        if missing:
            continue
        score_col = None
        for c in ["score_raw", "LLR", "meanPLL", "score"]:
            if c in work.columns:
                score_col = c
                break
        if score_col is None:
            continue
        table = work[list(merge_fields) + [score_col]].copy()
        renamed_col = f"score__{name.replace(' ', '_')}"
        table = table.rename(columns={score_col: renamed_col})
        prepared.append(table)

    # Section 2: outer-merge all prepared tables.
    if not prepared:
        return pd.DataFrame(columns=list(merge_fields))
    merged = prepared[0]
    for nxt in prepared[1:]:
        merged = merged.merge(nxt, on=list(merge_fields), how="outer")
    return merged

