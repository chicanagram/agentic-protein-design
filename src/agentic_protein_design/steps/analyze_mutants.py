from __future__ import annotations

if __name__ == "__main__" and __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parents[3]
    _src_root = _repo_root / "src"
    for _path in (str(_repo_root), str(_src_root)):
        if _path not in sys.path:
            sys.path.insert(0, _path)

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from agentic_protein_design.core import resolve_input_path
from agentic_protein_design.core.llm_display import display_llm_output_bundle
from agentic_protein_design.core.paths import get_step_processed_dir as core_get_step_processed_dir, setup_data_root
from agentic_protein_design.core.pipeline_utils import (
    clean_table,
    coerce_jsonable,
    get_openai_client,
    init_step_thread,
    persist_step_thread_update,
    save_text_output_with_assets_copy,
    safe_read_csv,
    select_existing_columns,
    summarize_compact_text,
    table_records,
)
from agentic_protein_design.core.thread_context import load_optional_thread_context


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
LLM_PROCESS_TAG = "analyze_mutants_llm"
STEP_OUTPUT_SUBDIR = "15_analyze_mutants"
FINAL_OUTPUT_COLUMNS = [
    "Type of mutant",
    "Residue(s) mutated",
    "Mutant(s)",
    "Description of effect",
]
MUTATION_RE = re.compile(r"([A-Za-z*])\s*(\d+)\s*([A-Za-z*])")
PREFERRED_MUTANT_METRIC_COLUMNS = [
    "foldchange_NBD_activity_25C",
    "foldchange_ABTS_activity_25C",
    "FC_NBD_1mM_purified",
    "FC_ABTS_1mM_purified",
    "FC_protein_yield",
    "Foldchange_Unk_Area_Norm_Subtracted",
    "Ketone%",
    "Alcohol%",
    "Total%",
]
PREFERRED_RESIDUE_CONTEXT_COLUMNS = [
    "res_num",
    "res_name",
    "res",
    "aa_polarity",
    "kd_hydro",
    "hw_polarity",
    "aa_vol",
    "secondary_structure",
    "relative_ASA",
    "SASA",
    "exposure_bucket",
    "dist_res_to_ligand_reactive_center",
    "min_dist_res_to_ligand",
]
PREFERRED_BINDING_SUMMARY_COLUMNS = [
    "struct_name",
    "num_pocket_res_ali",
    "num_pocket_res<8",
    "num_pocket_res<6",
    "reactive_center_distance",
    "median_dist_res_to_ligand_reactive_center",
    "median_min_dist_res_to_ligand",
    "mean_volume (proximal)",
    "mean_volume (distal)",
    "kd_weighted (proximal)",
    "kd_weighted (distal)",
    "hw_weighted (proximal)",
    "hw_weighted (distal)",
    "charged_fraction (proximal)",
    "charged_fraction (distal)",
    "polar_fraction (proximal)",
    "polar_fraction (distal)",
]
RESIDUE_CONTEXT_EXPORT_COLUMNS = [
    "res_num",
    "res_name",
    "res",
    "in_binding_pocket",
    "dist_res_to_ligand_reactive_center",
    "min_dist_res_to_ligand",
    "secondary_structure",
    "relative_ASA",
    "SASA",
    "exposure_bucket",
    "aa_polarity",
    "kd_hydro",
    "hw_polarity",
    "aa_vol",
]
MUTATION_EVIDENCE_EXCLUDE_COLUMNS = {"mutation", "mutant", "Mutation", "Mutant"}
AMINO_ACID_PROPERTIES: Dict[str, Dict[str, Any]] = {
    "A": {"name": "Ala", "aa_polarity": "np", "kd_hydro": 1.8, "hw_polarity": -0.5, "aa_vol": 67.0, "charge_class": "neutral"},
    "R": {"name": "Arg", "aa_polarity": "p+", "kd_hydro": -4.5, "hw_polarity": 3.0, "aa_vol": 148.0, "charge_class": "positive"},
    "N": {"name": "Asn", "aa_polarity": "p~", "kd_hydro": -3.5, "hw_polarity": 0.2, "aa_vol": 96.0, "charge_class": "neutral"},
    "D": {"name": "Asp", "aa_polarity": "p-", "kd_hydro": -3.5, "hw_polarity": 3.0, "aa_vol": 91.0, "charge_class": "negative"},
    "C": {"name": "Cys", "aa_polarity": "p~", "kd_hydro": 2.5, "hw_polarity": -1.0, "aa_vol": 86.0, "charge_class": "neutral"},
    "Q": {"name": "Gln", "aa_polarity": "p~", "kd_hydro": -3.5, "hw_polarity": 0.2, "aa_vol": 114.0, "charge_class": "neutral"},
    "E": {"name": "Glu", "aa_polarity": "p-", "kd_hydro": -3.5, "hw_polarity": 3.0, "aa_vol": 109.0, "charge_class": "negative"},
    "G": {"name": "Gly", "aa_polarity": "np", "kd_hydro": -0.4, "hw_polarity": 0.0, "aa_vol": 48.0, "charge_class": "neutral"},
    "H": {"name": "His", "aa_polarity": "p+", "kd_hydro": -3.2, "hw_polarity": -0.5, "aa_vol": 118.0, "charge_class": "positive"},
    "I": {"name": "Ile", "aa_polarity": "np", "kd_hydro": 4.5, "hw_polarity": -1.8, "aa_vol": 124.0, "charge_class": "neutral"},
    "L": {"name": "Leu", "aa_polarity": "np", "kd_hydro": 3.8, "hw_polarity": -1.8, "aa_vol": 124.0, "charge_class": "neutral"},
    "K": {"name": "Lys", "aa_polarity": "p+", "kd_hydro": -3.9, "hw_polarity": 3.0, "aa_vol": 135.0, "charge_class": "positive"},
    "M": {"name": "Met", "aa_polarity": "np", "kd_hydro": 1.9, "hw_polarity": -1.3, "aa_vol": 124.0, "charge_class": "neutral"},
    "F": {"name": "Phe", "aa_polarity": "np", "kd_hydro": 2.8, "hw_polarity": -2.5, "aa_vol": 135.0, "charge_class": "neutral"},
    "P": {"name": "Pro", "aa_polarity": "np", "kd_hydro": -1.6, "hw_polarity": 0.0, "aa_vol": 90.0, "charge_class": "neutral"},
    "S": {"name": "Ser", "aa_polarity": "p~", "kd_hydro": -0.8, "hw_polarity": 0.3, "aa_vol": 73.0, "charge_class": "neutral"},
    "T": {"name": "Thr", "aa_polarity": "p~", "kd_hydro": -0.7, "hw_polarity": -0.4, "aa_vol": 93.0, "charge_class": "neutral"},
    "W": {"name": "Trp", "aa_polarity": "np", "kd_hydro": -0.9, "hw_polarity": -3.4, "aa_vol": 163.0, "charge_class": "neutral"},
    "Y": {"name": "Tyr", "aa_polarity": "p~", "kd_hydro": -1.3, "hw_polarity": -2.3, "aa_vol": 141.0, "charge_class": "neutral"},
    "V": {"name": "Val", "aa_polarity": "np", "kd_hydro": 4.2, "hw_polarity": -1.5, "aa_vol": 105.0, "charge_class": "neutral"},
}
MUTANT_ANALYSIS_REFLECTION_PROMPT = """
You are reviewing an existing mutant-effect explanation table for a protein engineering workflow.

Task:
Improve the current explanations using the original analysis context plus user-supplied critique.

Output contract (strict):
- Return ONLY a JSON array.
- Return one object per provided analysis unit.
- Each object must contain:
  - row_index: integer copied from the provided analysis unit row_index
  - Description of effect: one sentence, revised and improved
- Do not return markdown, code fences, or extra prose.

Rules:
- Preserve coverage of all provided rows.
- Keep each explanation concise, specific, and technically grounded.
- Incorporate user feedback where compatible with the provided context.
- Do not invent unsupported mechanistic claims.
- For single-position rows, keep the explanation position-centric: explain why the residue position matters, and do not describe a specific amino-acid substitution.
- For single-substitution rows, focus on the effect of the specific substitution itself.
- For a position row and a substitution row at the same residue, the two explanations must be meaningfully different and should not repeat the same sentence in paraphrased form.
""".strip()

MUTANT_ANALYSIS_PROMPT = """
You are a protein engineer analyzing a mutagenesis dataset for a backbone enzyme.

Goal:
Generate concise, human-interpretable mechanistic explanations for prioritized mutation units.
These units are already grouped for you as:
- single-position groups from single mutants,
- single substitutions,
- clusters of multi-mutation mutants.

Use the provided assay data, residue-level structural context, binding-pocket membership, ligand distances,
secondary structure, solvent exposure, mutation-level stability or developability scores when available,
and backbone binding-pocket summary metrics to infer likely effects on activity, selectivity, expression,
stability, solubility, and binding-pocket behavior.

Output contract (strict):
- Return ONLY a JSON array.
- Return one object per provided analysis unit.
- Each object must contain:
  - row_index: integer copied from the provided analysis unit row_index
  - Description of effect: one sentence, compact but specific
- Do not return markdown, code fences, or extra prose.

Rules:
- Ground all reasoning in the provided context, as well as any background knowledge of the amino acid substitutions, enzyme and reaction.
- If a residue is absent from the binding-pocket residue table, treat it as likely outside the defined binding pocket/tunnel region.
- Prioritize the most mutation-specific evidence first: pocket membership, ligand proximity, solvent exposure, secondary structure,
  amino-acid chemistry changes, and strong consensus mutation scores.
- For single-position groups, describe only why that residue position is important or sensitive in the enzyme context.
- Do not mention any specific substitution (for example Val -> Thr) in the position-level explanation, even if only one substitution is available for that position.
- For single substitutions, describe the likely effect of that exact amino-acid substitution (for example Ala -> Phe), with emphasis on the chemistry/size/polarity change introduced by the substitution itself rather than repeating the generic position-level effect.
- For multi-mutation clusters, describe the shared or net effect of the cluster.
- If mutation-level stability or solubility scores are weak, mixed, or conflicting, avoid overclaiming and mention uncertainty briefly.
- If a residue is pocket-proximal and the substitution changes size, polarity, or aromaticity, prefer a pocket-shape or ligand-positioning explanation over generic wording.
- If a residue is solvent-exposed or outside the pocket, prefer stability, solubility, expression, or long-range conformational explanations unless stronger catalytic evidence is present.
- Mention uncertainty briefly when the evidence is weak or conflicting.
""".strip()

def get_step_processed_dir(resolved_dirs: Dict[str, Path]) -> Path:
    return core_get_step_processed_dir(resolved_dirs, STEP_OUTPUT_SUBDIR)


def init_thread(root_key: str, existing_thread_key: Optional[str] = None) -> Tuple[Dict[str, Any], pd.DataFrame]:
    return init_step_thread(
        root_key=root_key,
        llm_process_tag=LLM_PROCESS_TAG,
        title="Analyze mutants",
        source_notebook="15_analyze_mutants",
        existing_thread_key=existing_thread_key,
    )


def default_user_inputs() -> Dict[str, Any]:
    return {
        "enzyme_name": "ET096",
        "ligand_name": "S82",
        "focus_question": (
            "Explain how prioritized mutations likely alter activity, selectivity, expression, or pocket behavior "
            "for the selected backbone enzyme."
        ),
        "llm_model": "gpt-5.2",
        "llm_temperature": 0.2,
        "llm_max_rows": 200,
        "display_llm_output": True,
        "display_max_height": "640px",
        "display_compact_markdown": False,
        "binding_pocket_context_thread_key": "",
        "literature_context_thread_key": "",
    }


def default_input_paths(data_root: Path) -> Dict[str, str]:
    _ = data_root
    return {
        "selected_mutations_csv": "mutagenesis_proposal/SelectedMuts_ET096_mutagenesis_wEthylBenzene&Purified_2026-02-05.csv",
        "residue_structure_csv": "pdb/structure_csv/ET096_S82_backbone.csv",
        "binding_residues_csv": "pdb/structure_csv/ET096_S82_backbone_bindingpocket.csv",
        "binding_summary_csv": "pdb/bindingpocket_analysis.csv",
        "mutation_evidence_csv": "",
    }


# Input loading and normalization.
def _split_mutation_tokens(value: str) -> List[str]:
    raw = str(value or "").strip()
    if not raw:
        return []
    parts = re.split(r"[+,;/_\s]+", raw)
    return [p for p in (part.strip() for part in parts) if p]


def parse_mutation_tokens(value: str) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for token in _split_mutation_tokens(value):
        match = MUTATION_RE.fullmatch(token)
        if not match:
            continue
        wt, pos, mut = match.groups()
        parsed.append(
            {
                "token": f"{wt.upper()}{int(pos)}{mut.upper()}",
                "wt": wt.upper(),
                "position": int(pos),
                "mut": mut.upper(),
            }
        )
    return parsed


def load_selected_mutations(path: Path) -> pd.DataFrame:
    df = safe_read_csv(path)
    if "mutations" not in df.columns:
        raise KeyError(f"Expected a 'mutations' column in {path}")

    parsed = df["mutations"].apply(parse_mutation_tokens)
    enriched = df.copy()
    enriched["_parsed_tokens"] = parsed
    enriched["_parsed_count"] = parsed.apply(len)
    enriched["_positions_tuple"] = parsed.apply(lambda items: tuple(sorted({int(item['position']) for item in items})))
    enriched["_mutant_label"] = enriched["mutations"].astype(str).str.strip()
    if "num_mutations" in enriched.columns:
        enriched["_is_single"] = enriched["num_mutations"].fillna(enriched["_parsed_count"]).astype(float) <= 1
    else:
        enriched["_is_single"] = enriched["_parsed_count"] <= 1
    return enriched


def load_residue_structure_context(path: Path) -> pd.DataFrame:
    return safe_read_csv(path)


def load_binding_residue_context(path: Optional[Path]) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame()
    return safe_read_csv(path)


def load_mutation_evidence_context(path: Optional[Path]) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame()
    df = safe_read_csv(path)
    mutation_col = next((col for col in df.columns if str(col).strip().lower() == "mutation"), None)
    if mutation_col is None:
        raise KeyError(f"Optional mutation evidence CSV must contain a 'mutation' column: {path}")
    if mutation_col != "mutation":
        df = df.rename(columns={mutation_col: "mutation"})
    df["mutation"] = df["mutation"].astype(str).str.strip()
    return df[df["mutation"] != ""].copy()


def _match_binding_summary_row(summary_df: pd.DataFrame, enzyme_name: str, ligand_name: str) -> pd.Series:
    if "struct_name" not in summary_df.columns:
        raise KeyError("Binding summary CSV must contain 'struct_name'.")

    enzyme = str(enzyme_name or "").strip().lower()
    ligand = str(ligand_name or "").strip().lower()
    candidates = summary_df.copy()
    names = candidates["struct_name"].astype(str).str.lower()

    if enzyme and ligand:
        exact = candidates[names.str.contains(enzyme) & names.str.contains(ligand)]
        if not exact.empty:
            return exact.iloc[0]
    if enzyme:
        enzyme_only = candidates[names.str.contains(enzyme)]
        if not enzyme_only.empty:
            return enzyme_only.iloc[0]
    return candidates.iloc[0]


def load_binding_summary_context(path: Path, enzyme_name: str, ligand_name: str) -> Tuple[pd.DataFrame, pd.Series]:
    df = safe_read_csv(path)
    row = _match_binding_summary_row(df, enzyme_name, ligand_name)
    return df, row


def _build_residue_context_map(structure_df: pd.DataFrame, binding_df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
    structure_map: Dict[int, Dict[str, Any]] = {}
    if "res_num" in structure_df.columns:
        for _, row in structure_df.drop_duplicates(subset=["res_num"]).iterrows():
            pos = int(row["res_num"])
            structure_map[pos] = {
                "res_num": pos,
                "res_name": row.get("res_name"),
                "res": row.get("res"),
                "aa_polarity": row.get("aa_polarity"),
                "kd_hydro": row.get("kd_hydro"),
                "hw_polarity": row.get("hw_polarity"),
                "aa_vol": row.get("aa_vol"),
                "in_binding_pocket": False,
                "dist_res_to_ligand_reactive_center": None,
                "min_dist_res_to_ligand": None,
            }

    if "res_num" in binding_df.columns:
        for _, row in binding_df.drop_duplicates(subset=["res_num"]).iterrows():
            pos = int(row["res_num"])
            base = structure_map.get(pos, {"res_num": pos})
            base.update(
                {
                    "res_name": row.get("res_name", base.get("res_name")),
                    "res": row.get("res", base.get("res")),
                    "aa_polarity": row.get("aa_polarity", base.get("aa_polarity")),
                    "kd_hydro": row.get("kd_hydro", base.get("kd_hydro")),
                    "hw_polarity": row.get("hw_polarity", base.get("hw_polarity")),
                    "aa_vol": row.get("aa_vol", base.get("aa_vol")),
                    "in_binding_pocket": True,
                    "dist_res_to_ligand_reactive_center": row.get("dist_res_to_ligand_reactive_center"),
                    "min_dist_res_to_ligand": row.get("min_dist_res_to_ligand"),
                }
            )
            structure_map[pos] = base

    return structure_map


# Analysis-unit construction.
def _metric_summary(df: pd.DataFrame) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    for col in select_existing_columns(df, PREFERRED_MUTANT_METRIC_COLUMNS):
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue
        metrics[col] = {
            "mean": round(float(series.mean()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "n": int(series.shape[0]),
        }
    return metrics


def _mutation_count_bucket(count: int) -> str:
    n = int(count)
    if n <= 4:
        return "2-4"
    if n <= 8:
        return "5-8"
    return "9+"


def _categorize_metric_value(value: Any) -> str:
    if value is None:
        return "na"
    try:
        numeric = float(value)
    except Exception:
        return "na"
    if pd.isna(numeric):
        return "na"
    if numeric <= 0.8:
        return "low"
    if numeric >= 1.3:
        return "high"
    return "mid"


def _select_multi_cluster_metric_columns(df: pd.DataFrame) -> List[str]:
    priority = [
        "FC_NBD_1mM_purified",
        "FC_ABTS_1mM_purified",
        "foldchange_NBD_activity_25C",
        "foldchange_ABTS_activity_25C",
        "FC_protein_yield",
    ]
    selected: List[str] = []
    for col in priority:
        if col in df.columns and pd.to_numeric(df[col], errors="coerce").notna().any():
            selected.append(col)
        if len(selected) >= 4:
            break
    return selected


def _multi_mutant_cluster_key(row: pd.Series, metric_columns: List[str]) -> Tuple[Any, ...]:
    count_bucket = _mutation_count_bucket(int(row.get("num_mutations", row.get("_parsed_count", 2)) or 2))
    metric_signature = tuple(_categorize_metric_value(row.get(col)) for col in metric_columns)
    return (count_bucket,) + metric_signature


def _format_residue_positions(positions: List[int]) -> str:
    return ", ".join(str(p) for p in sorted({int(p) for p in positions}))


def _residue_context_for_positions(positions: List[int], residue_map: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    context_rows: List[Dict[str, Any]] = []
    for pos in sorted({int(p) for p in positions}):
        base = residue_map.get(pos, {"res_num": pos, "in_binding_pocket": False})
        context_rows.append({k: coerce_jsonable(v) for k, v in base.items() if k in PREFERRED_RESIDUE_CONTEXT_COLUMNS or k == "in_binding_pocket"})
    return context_rows


def prepare_analysis_units(mutant_df: pd.DataFrame, residue_map: Dict[int, Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    row_index = 1

    single_df = mutant_df[mutant_df["_is_single"]].copy()
    multi_df = mutant_df[~mutant_df["_is_single"]].copy()
    represented_single_positions: set[int] = set()

    if not single_df.empty:
        single_valid = single_df[single_df["_parsed_count"] >= 1].copy()

        for position, group in single_valid.groupby(single_valid["_positions_tuple"].apply(lambda xs: xs[0] if xs else None)):
            if pd.isna(position):
                continue
            pos_int = int(position)
            represented_single_positions.add(pos_int)
            mutants = sorted(group["_mutant_label"].dropna().astype(str).unique().tolist())
            rows.append(
                {
                    "row_index": row_index,
                    "_analysis_kind": "single_position_group",
                    "Type of mutant": "single",
                    "Residue(s) mutated": str(pos_int),
                    "Mutant(s)": "; ".join(mutants),
                    "_source_rows": group.index.astype(int).tolist(),
                    "_metric_summary": _metric_summary(group),
                    "_residue_context": _residue_context_for_positions([pos_int], residue_map),
                }
            )
            row_index += 1

        for mutation, group in single_valid.groupby("_mutant_label"):
            positions = sorted({int(item["position"]) for sub in group["_parsed_tokens"] for item in sub})
            rows.append(
                {
                    "row_index": row_index,
                    "_analysis_kind": "single_substitution",
                    "Type of mutant": "single",
                    "Residue(s) mutated": _format_residue_positions(positions),
                    "Mutant(s)": str(mutation),
                    "_source_rows": group.index.astype(int).tolist(),
                    "_metric_summary": _metric_summary(group),
                    "_residue_context": _residue_context_for_positions(positions, residue_map),
                }
            )
            row_index += 1

        represented_single_mutations = set(single_valid["_mutant_label"].dropna().astype(str).tolist())
    else:
        represented_single_mutations = set()

    all_positions: Dict[int, List[int]] = {}
    all_parsed_tokens: Dict[str, List[int]] = {}
    for idx, parsed_tokens in mutant_df["_parsed_tokens"].items():
        for item in parsed_tokens:
            token = str(item.get("token", "")).strip()
            if not token:
                continue
            all_parsed_tokens.setdefault(token, []).append(int(idx))
            pos = int(item["position"])
            all_positions.setdefault(pos, []).append(int(idx))

    missing_single_positions = sorted(pos for pos in all_positions if pos not in represented_single_positions)
    for pos in missing_single_positions:
        source_idx = all_positions[pos]
        group = mutant_df.loc[source_idx].copy()
        inferred_tokens = sorted(
            {
                str(item.get("token", "")).strip()
                for parsed_tokens in group["_parsed_tokens"]
                for item in parsed_tokens
                if int(item["position"]) == int(pos) and str(item.get("token", "")).strip()
            }
        )
        rows.append(
            {
                "row_index": row_index,
                "_analysis_kind": "single_position_group_inferred_from_multi",
                "Type of mutant": "single",
                "Residue(s) mutated": str(int(pos)),
                "Mutant(s)": "; ".join(inferred_tokens),
                "_source_rows": [int(i) for i in source_idx],
                "_metric_summary": _metric_summary(group),
                "_residue_context": _residue_context_for_positions([int(pos)], residue_map),
            }
        )
        row_index += 1

    missing_single_tokens = sorted(token for token in all_parsed_tokens if token not in represented_single_mutations)
    for token in missing_single_tokens:
        source_idx = all_parsed_tokens[token]
        group = mutant_df.loc[source_idx].copy()
        positions = sorted({int(item["position"]) for sub in group["_parsed_tokens"] for item in sub if str(item.get("token", "")).strip() == token})
        rows.append(
            {
                "row_index": row_index,
                "_analysis_kind": "single_substitution_inferred_from_multi",
                "Type of mutant": "single",
                "Residue(s) mutated": _format_residue_positions(positions),
                "Mutant(s)": token,
                "_source_rows": [int(i) for i in source_idx],
                "_metric_summary": _metric_summary(group),
                "_residue_context": _residue_context_for_positions(positions, residue_map),
            }
        )
        row_index += 1

    if not multi_df.empty:
        multi_valid = multi_df[multi_df["_parsed_count"] >= 2].copy()
        metric_columns = _select_multi_cluster_metric_columns(multi_valid)
        if not multi_valid.empty:
            multi_valid["_multi_cluster_key"] = multi_valid.apply(
                lambda row: _multi_mutant_cluster_key(row, metric_columns),
                axis=1,
            )
        grouped = multi_valid.groupby("_multi_cluster_key", sort=True) if not multi_valid.empty else []
        for _, group in grouped:
            all_positions = sorted(
                {
                    int(item["position"])
                    for parsed_tokens in group["_parsed_tokens"]
                    for item in parsed_tokens
                }
            )
            mutants = sorted(group["_mutant_label"].dropna().astype(str).unique().tolist())
            rows.append(
                {
                    "row_index": row_index,
                    "_analysis_kind": "multi_cluster",
                    "Type of mutant": "multi",
                    "Residue(s) mutated": _format_residue_positions(all_positions),
                    "Mutant(s)": ";\n".join(mutants),
                    "_source_rows": group.index.astype(int).tolist(),
                    "_metric_summary": _metric_summary(group),
                    "_residue_context": _residue_context_for_positions(all_positions, residue_map),
                }
            )
            row_index += 1

    prepared = pd.DataFrame.from_records(rows)
    if prepared.empty:
        raise ValueError("No analyzable mutation units were generated from the selected mutations CSV.")
    return prepared


def load_optional_binding_pocket_context(binding_pocket_context_thread_key: Optional[str], enzyme_name: str) -> Dict[str, Any]:
    return load_optional_thread_context(
        binding_pocket_context_thread_key,
        filter_keyword=enzyme_name,
    )


def load_optional_literature_context(literature_context_thread_key: Optional[str]) -> Dict[str, Any]:
    return load_optional_thread_context(
        literature_context_thread_key,
    )


# Prompt assembly and LLM calls.
def build_mutant_analysis_prompt(
    user_inputs: Dict[str, Any],
    analysis_units_df: pd.DataFrame,
    mutant_df: pd.DataFrame,
    binding_summary_row: pd.Series,
) -> str:
    enzyme_name = str(user_inputs.get("enzyme_name", "")).strip() or "selected backbone enzyme"
    ligand_name = str(user_inputs.get("ligand_name", "")).strip() or "selected ligand"
    focus_question = str(user_inputs.get("focus_question", "")).strip()
    mutant_metric_cols = select_existing_columns(mutant_df, PREFERRED_MUTANT_METRIC_COLUMNS)
    residue_cols_present = [c for c in PREFERRED_RESIDUE_CONTEXT_COLUMNS if c in analysis_units_df.iloc[0].get("_residue_context", [{}])[0]] if not analysis_units_df.empty and analysis_units_df.iloc[0].get("_residue_context") else []
    binding_cols = [col for col in PREFERRED_BINDING_SUMMARY_COLUMNS if col in binding_summary_row.index]

    prompt = [MUTANT_ANALYSIS_PROMPT]
    prompt.append("\nPROJECT CONTEXT")
    prompt.append(f"- Backbone enzyme: {enzyme_name}")
    prompt.append(f"- Ligand / analysis context: {ligand_name}")
    if focus_question:
        prompt.append(f"- Objective: {focus_question}")
    prompt.append(f"- Selected mutants loaded: {len(mutant_df)} rows")
    prompt.append(f"- Analysis units to explain: {len(analysis_units_df)} rows")
    prompt.append(f"- Key mutant assay/property columns present: {', '.join(mutant_metric_cols) if mutant_metric_cols else 'none'}")
    prompt.append(
        "- Residue-level structural columns available: "
        + (", ".join(residue_cols_present) if residue_cols_present else "residue identity / pocket membership only")
    )
    prompt.append(
        "- Backbone binding-pocket summary columns highlighted: "
        + (", ".join(binding_cols) if binding_cols else "none")
    )
    prompt.append(
        "- Important interpretation rule: residues absent from the binding-pocket residue table should be treated as outside the defined pocket/tunnel region and typically farther from the ligand than listed pocket residues."
    )
    return "\n".join(prompt)


def _build_llm_payload(
    mutant_df: pd.DataFrame,
    analysis_units_df: pd.DataFrame,
    binding_summary_row: pd.Series,
    supplemental_context: str,
    *,
    max_rows: int,
) -> Dict[str, Any]:
    payload_units: List[Dict[str, Any]] = []
    for _, row in analysis_units_df.iterrows():
        payload_units.append(
            {
                "row_index": int(row["row_index"]),
                "analysis_kind": coerce_jsonable(row["_analysis_kind"]),
                "Type of mutant": coerce_jsonable(row["Type of mutant"]),
                "Residue(s) mutated": coerce_jsonable(row["Residue(s) mutated"]),
                "Mutant(s)": coerce_jsonable(row["Mutant(s)"]),
                "source_rows": coerce_jsonable(row["_source_rows"]),
                "metric_summary": coerce_jsonable(row["_metric_summary"]),
                "residue_context": coerce_jsonable(row["_residue_context"]),
            }
        )

    binding_summary = {
        str(col): coerce_jsonable(binding_summary_row[col])
        for col in PREFERRED_BINDING_SUMMARY_COLUMNS
        if col in binding_summary_row.index
    }

    return {
        "analysis_units": payload_units[:max_rows],
        "selected_mutation_rows_preview": coerce_jsonable(
            table_records(
                clean_table(mutant_df.drop(columns=[c for c in mutant_df.columns if c.startswith("_")], errors="ignore")),
                min(max_rows, 50),
            )
        ),
        "selected_backbone_binding_summary": binding_summary,
        "optional_md_context": coerce_jsonable(supplemental_context.strip() or "Not provided."),
    }


def _extract_json_array(text: str) -> List[Dict[str, Any]]:
    raw = (text or "").strip()
    if not raw:
        return []
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        raw = fenced.group(1).strip()
    if not raw.startswith("["):
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and end > start:
            raw = raw[start : end + 1]
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        raise ValueError("LLM output is not a JSON array.")
    return [item for item in parsed if isinstance(item, dict)]


def _apply_llm_descriptions(analysis_units_df: pd.DataFrame, llm_rows: List[Dict[str, Any]]) -> pd.DataFrame:
    descriptions = {int(item.get("row_index")): str(item.get("Description of effect", "")).strip() for item in llm_rows if item.get("row_index") is not None}
    final_rows: List[Dict[str, Any]] = []

    single_units = analysis_units_df[analysis_units_df["Type of mutant"] == "single"].copy()
    if not single_units.empty:
        single_units["_position_key"] = single_units["Residue(s) mutated"].astype(str)
        for position_key, group in single_units.groupby("_position_key", sort=True):
            position_rows = group[group["_analysis_kind"].isin(["single_position_group", "single_position_group_inferred_from_multi"])]
            explicit_mut_rows = group[group["_analysis_kind"] == "single_substitution"]
            inferred_mut_rows = group[group["_analysis_kind"] == "single_substitution_inferred_from_multi"]

            explicit_muts = explicit_mut_rows["Mutant(s)"].astype(str).tolist()
            inferred_muts = inferred_mut_rows["Mutant(s)"].astype(str).tolist()
            mutant_labels = list(explicit_muts) + [f"{mut}*" for mut in inferred_muts]

            description_parts: List[str] = []
            if not position_rows.empty:
                pos_desc = descriptions.get(int(position_rows.iloc[0]["row_index"]), "").strip()
                if pos_desc:
                    description_parts.append(pos_desc)
            else:
                pos_desc = ""

            per_mutation_rows = explicit_mut_rows
            if explicit_mut_rows.empty and not inferred_mut_rows.empty:
                per_mutation_rows = inferred_mut_rows
            mutation_descriptions: List[str] = []
            for _, row in per_mutation_rows.iterrows():
                desc = descriptions.get(int(row["row_index"]), "").strip()
                if desc and desc != pos_desc:
                    mutation_descriptions.append(desc)
            if mutation_descriptions:
                description_parts.extend(mutation_descriptions)

            final_rows.append(
                {
                    "Type of mutant": "single",
                    "Residue(s) mutated": position_key,
                    "Mutant(s)": "; ".join(mutant_labels),
                    "Description of effect": "\n".join(part for part in description_parts if part).strip(),
                }
            )

    multi_units = analysis_units_df[analysis_units_df["Type of mutant"] == "multi"].copy()
    for _, row in multi_units.iterrows():
        final_rows.append(
            {
                "Type of mutant": "multi",
                "Residue(s) mutated": "",
                "Mutant(s)": str(row["Mutant(s)"]),
                "Description of effect": descriptions.get(int(row["row_index"]), "").strip(),
            }
        )

    final_df = pd.DataFrame.from_records(final_rows)
    if final_df.empty:
        return pd.DataFrame(columns=FINAL_OUTPUT_COLUMNS)
    return final_df.reindex(columns=FINAL_OUTPUT_COLUMNS)


def generate_llm_mutant_explanations(
    analysis_units_df: pd.DataFrame,
    mutant_df: pd.DataFrame,
    binding_summary_row: pd.Series,
    user_inputs: Dict[str, Any],
    *,
    supplemental_context: str = "",
) -> Tuple[pd.DataFrame, str, str]:
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    max_rows = int(user_inputs.get("llm_max_rows", 200))

    prompt_text = build_mutant_analysis_prompt(user_inputs, analysis_units_df, mutant_df, binding_summary_row)
    payload = _build_llm_payload(
        mutant_df,
        analysis_units_df,
        binding_summary_row,
        supplemental_context,
        max_rows=max_rows,
    )

    client = get_openai_client(
        missing_package_message="The `openai` package is required for mutant analysis.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running mutant analysis.",
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer."},
            {"role": "user", "content": f"{prompt_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}"},
        ],
    )
    llm_json_text = (response.choices[0].message.content or "").strip()
    if not llm_json_text:
        raise RuntimeError("LLM returned an empty mutant analysis response.")

    llm_rows = _extract_json_array(llm_json_text)
    final_df = _apply_llm_descriptions(analysis_units_df, llm_rows)

    if bool(user_inputs.get("display_llm_output", True)):
        preview_text = final_df[['Mutant(s)', 'Description of effect']].to_markdown(index=False) if not final_df.empty else "No explanation rows generated."
        display_llm_output_bundle(
            exchanges=[
                {
                    "title": "Mutant Analysis LLM Call",
                    "prompt_text": prompt_text,
                    "response_text": "(Final explanation table preview shown below.)",
                }
            ],
            compact_markdown_blocks=[
                {
                    "heading": "Mutant Explanation Table",
                    "text": preview_text,
                    "max_height": str(user_inputs.get("display_max_height", "640px")),
                }
            ],
            use_compact_markdown=bool(user_inputs.get("display_compact_markdown", False)),
        )

    return final_df, llm_json_text, prompt_text


def reflect_and_regenerate_mutant_explanations(
    analysis_units_df: pd.DataFrame,
    current_explanations_df: pd.DataFrame,
    mutant_df: pd.DataFrame,
    binding_summary_row: pd.Series,
    user_inputs: Dict[str, Any],
    *,
    supplemental_context: str = "",
    user_feedback: str = "",
    critique_prompt: Optional[str] = None,
    original_prompt_text: str = "",
    original_unit_level_output_json: str = "",
) -> Dict[str, Any]:
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    max_rows = int(user_inputs.get("llm_max_rows", 200))
    prompt_text = critique_prompt or MUTANT_ANALYSIS_REFLECTION_PROMPT

    payload = _build_llm_payload(
        mutant_df,
        analysis_units_df,
        binding_summary_row,
        supplemental_context,
        max_rows=max_rows,
    )
    payload["current_explanation_rows"] = coerce_jsonable(table_records(current_explanations_df, max_rows))
    payload["user_feedback"] = coerce_jsonable(user_feedback.strip() or "")
    payload["original_prompt_text"] = coerce_jsonable(str(original_prompt_text or "").strip())
    payload["reflection_prompt_text"] = coerce_jsonable(str(prompt_text).strip())
    payload["original_unit_level_output_json"] = coerce_jsonable(str(original_unit_level_output_json or "").strip())

    client = get_openai_client(
        missing_package_message="The `openai` package is required for mutant analysis reflection.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running mutant analysis reflection.",
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer."},
            {"role": "user", "content": f"{prompt_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}"},
        ],
    )
    llm_json_text = (response.choices[0].message.content or "").strip()
    if not llm_json_text:
        raise RuntimeError("LLM returned an empty mutant analysis reflection response.")

    llm_rows = _extract_json_array(llm_json_text)
    refined_df = _apply_llm_descriptions(analysis_units_df, llm_rows)

    critique_revision_summary = ""
    try:
        summary_prompt = (
            "Summarize the critique and revisions between the original and improved mutant-effect tables.\n"
            "Return 5-6 concise bullet points only."
        )
        summary_payload = {
            "original_rows": coerce_jsonable(table_records(current_explanations_df, max_rows)),
            "improved_rows": coerce_jsonable(table_records(refined_df, max_rows)),
            "user_feedback": coerce_jsonable(user_feedback.strip() or ""),
        }
        summary_response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "You are a precise technical editor."},
                {"role": "user", "content": f"{summary_prompt}\n\nINPUT_DATA_JSON:\n{json.dumps(summary_payload, ensure_ascii=True)}"},
            ],
        )
        critique_revision_summary = (summary_response.choices[0].message.content or "").strip()
    except Exception:
        critique_revision_summary = ""

    if bool(user_inputs.get("display_llm_output", True)):
        if critique_revision_summary:
            print("Critique and revisions summary:")
            print(critique_revision_summary)
        preview_text = refined_df[['Mutant(s)', 'Description of effect']].to_markdown(index=False) if not refined_df.empty else "No explanation rows generated."
        display_llm_output_bundle(
            exchanges=[
                {
                    "title": "Mutant Analysis Reflection / Rewrite",
                    "prompt_text": prompt_text,
                    "response_text": "(Refined explanation table shown below.)",
                }
            ],
            compact_markdown_blocks=[
                {
                    "heading": "Refined Mutant Explanation Table",
                    "text": preview_text,
                    "max_height": str(user_inputs.get("display_max_height", "640px")),
                }
            ],
            use_compact_markdown=bool(user_inputs.get("display_compact_markdown", False)),
        )

    return {
        "prompt_text": prompt_text,
        "llm_json_text": llm_json_text,
        "explanations_df": refined_df,
        "critique_revision_summary": critique_revision_summary,
    }


def save_mutant_inputs_snapshot(mutant_df: pd.DataFrame, processed_dir: Path) -> Path:
    out_path = processed_dir / "selected_mutations_input_snapshot.csv"
    clean_table(mutant_df.drop(columns=[c for c in mutant_df.columns if c.startswith("_")], errors="ignore")).to_csv(out_path, index=False)
    return out_path


def save_analysis_units_snapshot(analysis_units_df: pd.DataFrame, processed_dir: Path) -> Path:
    out_path = processed_dir / "mutant_analysis_units_snapshot.csv"
    export_df = analysis_units_df.copy()
    for col in ["_source_rows", "_metric_summary", "_residue_context"]:
        if col in export_df.columns:
            export_df[col] = export_df[col].apply(lambda v: json.dumps(coerce_jsonable(v), ensure_ascii=True))
    export_df.to_csv(out_path, index=False)
    return out_path


def save_mutant_explanations_csv(explanations_df: pd.DataFrame, processed_dir: Path, filename: str = "mutant_effect_explanations.csv") -> Path:
    out_path = processed_dir / filename
    explanations_df.to_csv(out_path, index=False)
    return out_path


def save_llm_analysis(analysis_text: str, processed_dir: Path) -> Path:
    return save_text_output_with_assets_copy(
        analysis_text,
        processed_dir,
        "mutant_analysis_llm_summary.md",
        assets_filename="mutant_analysis_llm_summary.md",
    )


# End-to-end execution.
def persist_thread_update(
    root_key: str,
    thread_id: str,
    user_inputs: Dict[str, Any],
    input_paths: Dict[str, str],
    input_snapshot_path: Optional[Path],
    analysis_units_path: Optional[Path],
    explanations_csv_path: Optional[Path],
    llm_analysis_path: Optional[Path],
    llm_analysis_text: Optional[str],
    binding_pocket_context_thread_key: Optional[str] = None,
    literature_context_thread_key: Optional[str] = None,
) -> str:
    prompt_text = str(user_inputs.get("focus_question", "")).strip() or "Analyze prioritized mutants"
    metadata = {
        "user_inputs": user_inputs,
        "input_paths": input_paths,
        "input_snapshot_path": input_snapshot_path,
        "analysis_units_path": analysis_units_path,
        "explanations_csv_path": explanations_csv_path,
        "llm_analysis_path": llm_analysis_path,
        "llm_analysis_summary": "" if not llm_analysis_text else summarize_compact_text(llm_analysis_text),
        "binding_pocket_context_thread_key": binding_pocket_context_thread_key,
        "literature_context_thread_key": literature_context_thread_key,
        "llm_model": str(user_inputs.get("llm_model", "")),
    }
    return persist_step_thread_update(
        root_key=root_key,
        thread_id=thread_id,
        llm_process_tag=LLM_PROCESS_TAG,
        source_notebook="15_analyze_mutants",
        content=prompt_text,
        metadata=metadata,
    )


def run_analyze_mutants_step(
    root_key: str,
    user_inputs: Dict[str, Any],
    input_paths: Dict[str, str],
    *,
    existing_thread_key: Optional[str] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Execute the end-to-end mutant-analysis step.
    """
    data_root, resolved_dirs = setup_data_root(root_key, REQUIRED_SUBFOLDERS)
    step_processed_dir = get_step_processed_dir(resolved_dirs)
    thread, _ = init_thread(root_key, existing_thread_key)
    thread_id = str(thread["thread_id"])

    enzyme_name = str(user_inputs.get("enzyme_name", "")).strip()
    ligand_name = str(user_inputs.get("ligand_name", "")).strip()

    selected_mutations_csv = resolve_input_path(data_root, input_paths["selected_mutations_csv"])
    residue_structure_csv = resolve_input_path(data_root, input_paths["residue_structure_csv"])
    binding_residues_csv = resolve_input_path(data_root, input_paths["binding_residues_csv"])
    binding_summary_csv = resolve_input_path(data_root, input_paths["binding_summary_csv"])

    mutant_df = load_selected_mutations(selected_mutations_csv)
    residue_structure_df = load_residue_structure_context(residue_structure_csv)
    binding_residue_df = load_binding_residue_context(binding_residues_csv)
    binding_summary_df, binding_summary_row = load_binding_summary_context(binding_summary_csv, enzyme_name, ligand_name)

    residue_map = _build_residue_context_map(residue_structure_df, binding_residue_df)
    analysis_units_df = prepare_analysis_units(mutant_df, residue_map)

    input_snapshot_path: Optional[Path] = None
    analysis_units_path: Optional[Path] = None

    binding_pocket_context_thread_key = str(user_inputs.get("binding_pocket_context_thread_key", "")).strip() or None
    literature_context_thread_key = str(user_inputs.get("literature_context_thread_key", "")).strip() or None
    binding_pocket_context_result = load_optional_binding_pocket_context(binding_pocket_context_thread_key, enzyme_name)
    literature_context_result = load_optional_literature_context(literature_context_thread_key)
    context_parts = [
        str(binding_pocket_context_result.get("filtered_context_text") or binding_pocket_context_result.get("context_text") or "").strip(),
        str(literature_context_result.get("context_text", "")).strip(),
    ]
    supplemental_context = "\n\n".join(part for part in context_parts if part)

    explanations_df, llm_json_text, prompt_text = generate_llm_mutant_explanations(
        analysis_units_df,
        mutant_df,
        binding_summary_row,
        user_inputs,
        supplemental_context=supplemental_context,
    )
    explanations_csv_path = save_mutant_explanations_csv(explanations_df, step_processed_dir)

    llm_analysis_text = (
        "Mutant analysis prompt:\n\n"
        + prompt_text
        + "\n\nFinal explanation table:\n\n"
        + explanations_df.to_markdown(index=False)
        + "\n\nRaw LLM JSON:\n```json\n"
        + llm_json_text
        + "\n```"
    )
    llm_analysis_path = save_llm_analysis(llm_analysis_text, step_processed_dir)

    updated_at: Optional[str] = None
    if persist:
        updated_at = persist_thread_update(
            root_key=root_key,
            thread_id=thread_id,
            user_inputs=user_inputs,
            input_paths=input_paths,
            input_snapshot_path=input_snapshot_path,
            analysis_units_path=analysis_units_path,
            explanations_csv_path=explanations_csv_path,
            llm_analysis_path=llm_analysis_path,
            llm_analysis_text=llm_analysis_text,
            binding_pocket_context_thread_key=binding_pocket_context_thread_key,
            literature_context_thread_key=literature_context_thread_key,
        )

    return {
        "root_key": root_key,
        "thread_id": thread_id,
        "thread_updated_at": updated_at,
        "data_root": data_root,
        "resolved_dirs": resolved_dirs,
        "step_processed_dir": step_processed_dir,
        "selected_mutations_csv": selected_mutations_csv,
        "residue_structure_csv": residue_structure_csv,
        "binding_residues_csv": binding_residues_csv,
        "binding_summary_csv": binding_summary_csv,
        "mutant_df": mutant_df,
        "residue_structure_df": residue_structure_df,
        "binding_residue_df": binding_residue_df,
        "binding_summary_df": binding_summary_df,
        "binding_summary_row": binding_summary_row,
        "analysis_units_df": analysis_units_df,
        "input_snapshot_path": input_snapshot_path,
        "analysis_units_path": analysis_units_path,
        "binding_pocket_context_result": binding_pocket_context_result,
        "literature_context_result": literature_context_result,
        "explanations_df": explanations_df,
        "explanations_csv_path": explanations_csv_path,
        "llm_json_text": llm_json_text,
        "prompt_text": prompt_text,
        "llm_analysis_path": llm_analysis_path,
    }


if __name__ == "__main__":
    from agentic_protein_design.core.pipeline_utils import (
        load_openai_api_key_from_project_config,
        print_run_summary,
    )

    load_openai_api_key_from_project_config()

    root_key = "examples"
    existing_thread_key = None
    persist = True

    data_root, _ = setup_data_root(root_key, REQUIRED_SUBFOLDERS)
    user_inputs = default_user_inputs()
    input_paths = default_input_paths(data_root)

    result = run_analyze_mutants_step(
        root_key=root_key,
        user_inputs=user_inputs,
        input_paths=input_paths,
        existing_thread_key=existing_thread_key,
        persist=persist,
    )
    print_run_summary(
        result,
        keys=[
            "root_key",
            "thread_id",
            "thread_updated_at",
            "step_processed_dir",
            "explanations_csv_path",
            "llm_analysis_path",
        ],
    )
