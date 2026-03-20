from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import pandas as pd

from .config import SCORE_SOURCE_COLUMN_REGISTRY

ScoreKey = Tuple[str, str]


def infer_position_from_mutation(mutation: str) -> int | None:
    """Infer 1-based position index from a mutation token like A123P."""
    m = re.search(r"(\d+)", str(mutation or ""))
    return int(m.group(1)) if m else None


def _artifact_to_registry_entry(
    artifact_name: str,
    artifact_path: str,
    user_inputs: Mapping[str, Any],
    score_type: str,
) -> tuple[ScoreKey, Dict[str, Any]]:
    # Section 1: map artifact labels to canonical (score_type, score_name) keys.
    txt = str(artifact_name)
    score_name = ""
    if score_type in {"plm_llr", "plm_meanpll"}:
        score_name = txt.split()[0]
    elif score_type == "stability_ddg":
        score_name = "SPURS"
    elif score_type == "proteinmpnn":
        score_name = "proteinmpnn"
    else:
        m = re.search(r"\(([^)]+)\)", txt)
        if m:
            score_name = str(m.group(1)).strip()
        else:
            ann = user_inputs.get("score_types_to_run", {}).get("structure_annotations", [])
            score_name = str(ann[0]) if isinstance(ann, list) and ann else "structure_annotations"
    # Section 2: resolve hard-coded registry in config.py (specific key, then wildcard).
    cfg = SCORE_SOURCE_COLUMN_REGISTRY.get((score_type, score_name), SCORE_SOURCE_COLUMN_REGISTRY.get((score_type, "*"), {}))
    value_columns = {
        str(k): [str(x) for x in v]
        for k, v in dict(cfg.get("value_columns", {})).items()
    }
    candidates = [str(x) for x in cfg.get("value_column_candidates", [])]
    if score_type == "structure_annotations" and not candidates and not value_columns:
        candidates = [score_name]
    if not value_columns and candidates:
        default_col = str(cfg.get("default_value_column", candidates[0]))
        value_columns = {default_col: candidates}
    return (
        (score_type, score_name),
        {
            "artifact": txt,
            "path": str(artifact_path),
            "score_type": score_type,
            "score_name": score_name,
            "value_columns": value_columns,
            "default_value_column": str(cfg.get("default_value_column", "score")),
            "id_column_candidates": dict(
                cfg.get("id_column_candidates", {"mutations": ["mutations", "mutation"], "resnum": ["resnum", "position"]})
            ),
        },
    )


def build_score_source_registry(
    artifact_status: pd.DataFrame,
    user_inputs: Mapping[str, Any],
) -> Dict[ScoreKey, Dict[str, Any]]:
    """Build mapping between requested score CSVs and relevant columns."""
    # Section 1: iterate expected artifacts and classify into canonical keys.
    registry: Dict[ScoreKey, Dict[str, Any]] = {}
    if artifact_status is None or artifact_status.empty:
        return registry
    for _, row in artifact_status.iterrows():
        artifact = str(row.get("artifact", ""))
        if " LLR vect" in artifact:
            score_type = "plm_llr"
        elif " meanPLL csv" in artifact:
            score_type = "plm_meanpll"
        elif "SPURS scores" in artifact:
            score_type = "stability_ddg"
        elif "ProteinMPNN scores" in artifact:
            score_type = "proteinmpnn"
        elif "structure annotations" in artifact:
            score_type = "structure_annotations"
        else:
            continue
        item = _artifact_to_registry_entry(
            artifact_name=artifact,
            artifact_path=str(row.get("path", "")),
            user_inputs=user_inputs,
            score_type=score_type,
        )
        key, meta = item
        registry[key] = meta
    return registry


def _find_first_column(df: pd.DataFrame, candidates: Sequence[str]) -> str | None:
    # Section 1: resolve first matching column name (case-insensitive).
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    for c in candidates:
        col = cols_lower.get(str(c).strip().lower())
        if col is not None:
            return str(col)
    return None


def load_score_data_dict(
    raw_score_tables: Mapping[str, pd.DataFrame],
    registry: Mapping[ScoreKey, Mapping[str, Any]],
) -> Dict[ScoreKey, pd.DataFrame]:
    """Load/trim score data to relevant columns as {(score_type, score_name): df}."""
    # Section 1: index raw loaded frames by artifact label.
    by_artifact = {str(k): v for k, v in raw_score_tables.items()}
    data_dict: Dict[ScoreKey, pd.DataFrame] = {}
    # Section 2: select id + requested score columns per registered key.
    for key, meta in registry.items():
        artifact = str(meta.get("artifact", ""))
        df = by_artifact.get(artifact)
        if df is None or df.empty:
            continue
        mut_col = _find_first_column(df, meta.get("id_column_candidates", {}).get("mutations", []))
        res_col = _find_first_column(df, meta.get("id_column_candidates", {}).get("resnum", []))
        # Section 2A: detect all requested canonical value columns and normalize names.
        selected_value_cols: List[str] = []
        rename_map: Dict[str, str] = {}
        value_cols_cfg = dict(meta.get("value_columns", {}))
        for canonical, aliases in value_cols_cfg.items():
            found = _find_first_column(df, [str(x) for x in aliases])
            if found is None:
                continue
            selected_value_cols.append(found)
            if found != canonical:
                rename_map[found] = canonical
        if not selected_value_cols:
            fallback = _find_first_column(df, [str(meta.get("default_value_column", "score"))])
            if fallback is not None:
                selected_value_cols.append(fallback)
                if fallback != str(meta.get("default_value_column", "score")):
                    rename_map[fallback] = str(meta.get("default_value_column", "score"))
        keep_cols = [c for c in [mut_col, res_col] if c is not None] + selected_value_cols
        if not keep_cols:
            continue
        trimmed = df[keep_cols].copy()
        # Section 2B: normalize id column names to canonical schema before merge.
        if mut_col is not None and mut_col != "mutations":
            trimmed = trimmed.rename(columns={mut_col: "mutations"})
        if res_col is not None and res_col != "resnum":
            trimmed = trimmed.rename(columns={res_col: "resnum"})
        if rename_map:
            trimmed = trimmed.rename(columns=rename_map)
        data_dict[key] = trimmed
    return data_dict


def _prepare_merge_table(df: pd.DataFrame, score_type: str, score_name: str) -> pd.DataFrame:
    # Section 1: normalize id columns and guarantee resnum when mutations exist.
    work = df.copy()
    mut_col = _find_first_column(work, ["mutations", "mutation"])
    res_col = _find_first_column(work, ["resnum", "position"])
    if mut_col is not None and mut_col != "mutations":
        work = work.rename(columns={mut_col: "mutations"})
    if res_col is not None and res_col != "resnum":
        work = work.rename(columns={res_col: "resnum"})
    if "mutations" in work.columns:
        work["mutations"] = work["mutations"].astype(str)
    if "resnum" not in work.columns and "mutations" in work.columns:
        work["resnum"] = work["mutations"].map(infer_position_from_mutation)
    # Section 2: suffix non-id columns by score_name to avoid merge collisions.
    id_cols = {"mutations", "resnum"}
    rename_map = {}
    for c in work.columns:
        if c in id_cols:
            continue
        if score_type == "structure_annotations":
            rename_map[c] = c
        else:
            rename_map[c] = c if c.endswith(f"_{score_name}") else f"{c}_{score_name}"
    return work.rename(columns=rename_map)


def merge_score_data_dict(
    score_data_dict: Mapping[ScoreKey, pd.DataFrame],
) -> pd.DataFrame:
    """Merge score dataframes across available id columns (mutations/resnum)."""
    # Section 1: prepare normalized per-source merge tables.
    prepared: List[pd.DataFrame] = []
    for (score_type, score_name), df in score_data_dict.items():
        if df is None or df.empty:
            continue
        table = _prepare_merge_table(df, score_type=score_type, score_name=score_name)
        if "mutations" not in table.columns and "resnum" not in table.columns:
            continue
        prepared.append(table)
    if not prepared:
        return pd.DataFrame(columns=["mutations", "resnum"])
    # Section 2: ensure base table has mutations+resnum when possible.
    base_idx = 0
    for i, t in enumerate(prepared):
        if "mutations" in t.columns and "resnum" in t.columns:
            base_idx = i
            break
    merged = prepared.pop(base_idx)
    # Section 3: merge each table on shared id columns.
    for nxt in prepared:
        join_keys = [k for k in ("mutations", "resnum") if k in merged.columns and k in nxt.columns]
        if not join_keys:
            continue
        merged = merged.merge(nxt, on=join_keys, how="outer")
    return merged


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
