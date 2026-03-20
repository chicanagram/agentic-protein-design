from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Tuple

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
    return token[0], pos, token[-1]


def summarize_mutation_shortlist_stats(df: pd.DataFrame) -> Dict[str, int]:
    """Return number of unique positions and number of mutations."""
    # Section 1: build stats for current mutation pool.
    if df is None or df.empty:
        return {"n_unique_positions": 0, "n_mutations": 0}
    work = df.copy()
    if "resnum" not in work.columns and "mutations" in work.columns:
        work["resnum"] = work["mutations"].map(infer_position_from_mutation)
    n_pos = int(work["resnum"].nunique()) if "resnum" in work.columns else 0
    return {"n_unique_positions": n_pos, "n_mutations": int(len(work))}


def _print_stats(label: str, df: pd.DataFrame) -> None:
    # Section 1: print compact pool stats.
    s = summarize_mutation_shortlist_stats(df)
    print(f"[Selection] {label}: n_unique_positions={s['n_unique_positions']}, n_mutations={s['n_mutations']}")


def _print_mutations_grouped_by_position(df: pd.DataFrame) -> None:
    # Section 1: print shortlisted mutations grouped by residue position.
    if df is None or df.empty or "mutations" not in df.columns:
        print("[Selection] selected mutations by position: <none>")
        return
    work = df.copy()
    if "resnum" not in work.columns:
        work["resnum"] = work["mutations"].map(infer_position_from_mutation)
    if work["resnum"].isna().all():
        print("[Selection] selected mutations by position: <none>")
        return
    print("[Selection] selected mutations by position:")
    grouped = (
        work.dropna(subset=["resnum"])
        .assign(resnum=lambda x: x["resnum"].astype(int))
        .groupby("resnum", sort=True)["mutations"]
        .apply(lambda s: ", ".join([str(x) for x in s.tolist()]))
    )
    for pos, muts in grouped.items():
        print(f"{pos}: {muts}")


def _split_top_level_and(expr: str) -> List[str]:
    # Section 1: split expression into top-level '&' clauses.
    text = str(expr or "").strip()
    if not text:
        return []
    parts: List[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "&" and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return [p for p in parts if p]


def _split_top_level_op(expr: str, op: str) -> List[str]:
    # Section 1: split expression on top-level operator while preserving nested groups.
    text = str(expr or "").strip()
    if not text:
        return []
    parts: List[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == op and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return [p for p in parts if p]


def _strip_outer_parens(expr: str) -> str:
    # Section 1: remove one layer of redundant wrapping parentheses.
    text = str(expr or "").strip()
    if not (text.startswith("(") and text.endswith(")")):
        return text
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and i != len(text) - 1:
                return text
    return text[1:-1].strip()


def _extract_referenced_columns(expr: str) -> List[str]:
    # Section 1: extract identifier-like tokens as candidate dataframe columns.
    tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", str(expr or ""))
    reserved = {"and", "or", "not", "True", "False", "in"}
    out: List[str] = []
    for tok in tokens:
        if tok in reserved:
            continue
        if tok not in out:
            out.append(tok)
    return out


def _prune_clause_by_available_columns(clause: str, available_cols: List[str]) -> tuple[str | None, List[str]]:
    # Section 1: remove top-level OR branches that depend on missing columns.
    available = set(str(c) for c in available_cols)
    raw = _strip_outer_parens(clause)
    or_parts = _split_top_level_op(raw, "|")
    if len(or_parts) <= 1:
        refs = _extract_referenced_columns(raw)
        missing = [c for c in refs if c not in available]
        return (None if missing else raw), missing

    kept: List[str] = []
    missing_all: List[str] = []
    for part in or_parts:
        refs = _extract_referenced_columns(part)
        missing = [c for c in refs if c not in available]
        if missing:
            missing_all.extend([m for m in missing if m not in missing_all])
            continue
        kept.append(part)
    if not kept:
        return None, missing_all
    if len(kept) == 1:
        return kept[0], missing_all
    return "(" + "|".join(f"({p})" for p in kept) + ")", missing_all


def _ensure_mutation_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Section 1: ensure resnum/wt_aa/mt_aa columns are available.
    out = df.copy()
    if "mutations" not in out.columns:
        return out
    parsed = out["mutations"].map(_parse_mutation_token)
    if "resnum" not in out.columns:
        out["resnum"] = parsed.map(lambda x: x[1]).astype("Int64")
    out["wt_aa"] = parsed.map(lambda x: x[0])
    out["mt_aa"] = parsed.map(lambda x: x[2])
    return out


def _apply_column_constraints_stepwise(df: pd.DataFrame, col_constraints: str) -> pd.DataFrame:
    # Section 1: apply score-column constraints clause-by-clause.
    work = df.copy()
    clauses = _split_top_level_and(col_constraints)
    if not clauses and str(col_constraints or "").strip():
        clauses = [str(col_constraints).strip()]
    if not clauses:
        print("[Selection] apply col_constraints: <none>")
        return work
    for clause in clauses:
        adjusted, missing_cols = _prune_clause_by_available_columns(clause, list(work.columns))
        if adjusted is None:
            print(f"[Selection] skip col_constraints clause (missing columns {missing_cols}): {clause}")
            _print_stats("after skipped clause", work)
            continue
        if adjusted != clause:
            print(
                f"[Selection] apply col_constraints: {clause} -> {adjusted} "
                f"(dropped missing columns {missing_cols})"
            )
        else:
            print(f"[Selection] apply col_constraints: {adjusted}")
        try:
            work = work.query(adjusted, engine="python")
        except Exception as exc:
            print(f"[Selection] skipped invalid clause '{adjusted}': {exc}")
            continue
        _print_stats(f"after {adjusted}", work)
    return work.reset_index(drop=True)


def _apply_position_filters(df: pd.DataFrame, user_inputs: Mapping[str, Any]) -> pd.DataFrame:
    # Section 1: apply either allowed_positions or pos_to_exclude.
    work = df.copy()
    allowed_positions = [int(x) for x in (user_inputs.get("allowed_positions") or [])]
    pos_to_exclude = [int(x) for x in (user_inputs.get("pos_to_exclude") or [])]
    if allowed_positions:
        print(f"[Selection] apply allowed_positions: {allowed_positions}")
        work = work.loc[work["resnum"].isin(set(allowed_positions))].reset_index(drop=True)
        _print_stats("after allowed_positions", work)
    elif pos_to_exclude:
        print(f"[Selection] apply pos_to_exclude: {pos_to_exclude}")
        work = work.loc[~work["resnum"].isin(set(pos_to_exclude))].reset_index(drop=True)
        _print_stats("after pos_to_exclude", work)
    else:
        print("[Selection] apply position filter: <none>")
    return work


def _apply_mutation_exclusions(df: pd.DataFrame, user_inputs: Mapping[str, Any]) -> pd.DataFrame:
    # Section 1: filter mutations_to_exclude.
    work = df.copy()
    muts_to_exclude = set(str(x) for x in (user_inputs.get("mutations_to_exclude") or []))
    if not muts_to_exclude:
        print("[Selection] apply mutations_to_exclude: <none>")
        return work
    print(f"[Selection] apply mutations_to_exclude: n={len(muts_to_exclude)}")
    work = work.loc[~work["mutations"].astype(str).isin(muts_to_exclude)].reset_index(drop=True)
    _print_stats("after mutations_to_exclude", work)
    return work


def _select_with_position_cap(df: pd.DataFrame, top_n: int, max_num_mut_per_pos: int) -> pd.DataFrame:
    # Section 1: select max_num_mut_per_pos per position until reaching top_n.
    selected_rows: List[pd.Series] = []
    per_pos_count: Dict[int, int] = {}
    for _, row in df.iterrows():
        pos_val = row.get("resnum", np.nan)
        pos = int(pos_val) if pd.notna(pos_val) else -1
        if per_pos_count.get(pos, 0) >= max_num_mut_per_pos:
            continue
        selected_rows.append(row)
        per_pos_count[pos] = per_pos_count.get(pos, 0) + 1
        if len(selected_rows) >= top_n:
            break
    if not selected_rows:
        return pd.DataFrame(columns=df.columns)
    out = pd.DataFrame(selected_rows).reset_index(drop=True)
    out["selection_rank"] = np.arange(1, len(out) + 1)
    return out


def rank_and_select_mutants_prototype(
    scores_input: pd.DataFrame,
    user_inputs: Mapping[str, Any],
) -> pd.DataFrame:
    """
    Rank and filter mutations from wide compiled score table.

    Required behavior:
    - compute LLR_consensus and LLR_avg from LLR_* columns
    - sort descending by LLR_consensus then LLR_avg
    - apply staged filtering with printed stats
    - cap per-position selection until top_n
    """
    # Section 1: validate input and compute core LLR ranking columns.
    if scores_input is None or scores_input.empty:
        return pd.DataFrame()
    llr_cols = [c for c in scores_input.columns if str(c).startswith("LLR_")]
    if not llr_cols:
        print("[Selection] no LLR_* columns found; skipping shortlist generation.")
        return pd.DataFrame()

    work = _ensure_mutation_columns(scores_input)
    work = work.copy()
    llr_mat = work[llr_cols].apply(pd.to_numeric, errors="coerce")
    work["LLR_consensus"] = (llr_mat > 0).sum(axis=1)
    work["LLR_avg"] = llr_mat.mean(axis=1)
    work = work.sort_values(by=["LLR_consensus", "LLR_avg"], ascending=[False, False]).reset_index(drop=True)

    _print_stats("starting mutation pool", work)

    # Section 2: apply score-column constraints from user_inputs.
    col_constraints = str(user_inputs.get("col_constraints", "") or "").strip()
    work = _apply_column_constraints_stepwise(work, col_constraints)

    # Section 3: apply position filter, mutation exclusions, and final capped selection.
    work = _apply_position_filters(work, user_inputs)
    work = _apply_mutation_exclusions(work, user_inputs)

    top_n = int(user_inputs.get("top_n", 200))
    max_per_pos = int(user_inputs.get("max_num_mut_per_pos", 2))
    print(f"[Selection] apply capped selection: top_n={top_n}, max_num_mut_per_pos={max_per_pos}")
    out = _select_with_position_cap(work, top_n=top_n, max_num_mut_per_pos=max_per_pos)
    _print_stats("final shortlist", out)
    _print_mutations_grouped_by_position(out)
    return out
