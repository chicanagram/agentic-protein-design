from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from chat_store import append_message, create_thread, list_threads, load_thread
from variables import address_dict, subfolders


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
METRIC_COLS = [
    "reactive_center_distance",
    "mean_volume",
    "kd_weighted",
    "polar_fraction",
    "charged_fraction",
]

prompt = """
Analyse the uploaded inputs for a set of proteins to interpret how binding-pocket structure relates to catalytic activity and selectivity.

INPUTS
- binding_pocket_table: table of extracted binding-pocket properties (per protein)
- pocket_alignment_table: filtered residue alignment of pocket-proximal positions
- reaction_data (optional): table or dict summarising enzyme activity on different substrates

TASKS
1. For each protein, generate a concise **3–4 bullet summary** of its binding-pocket geometry and chemistry.
2. Interpret how these properties are likely to influence **catalytic activity and selectivity**, especially productive (e.g. peroxygenative) vs non-productive or competing (e.g. peroxidative) pathways.
3. If variants of the same protein are present, **explicitly contrast them** and explain how observed pocket differences could rationalise functional changes.
4. Briefly distil **cross-protein trends or clusters** (“pocket phenotypes”) that explain systematic behaviour differences across the panel.
5. Optionally integrate reaction_data to connect structural features to observed substrate-specific behaviour.

POCKET FEATURES TO CONSIDER

Pocket size / alignment coverage
- num_pocket_res_ali: number of aligned positions within a distance cutoff of any docked ligand
- num_pocket_res_lt6: number of residues close to the ligand in each structure

Ligand-dependent geometry
- reactive_center_distance: distance between ligand reactive atom and catalytic center
- median_dist_res_to_ligand_reactive_center: median distance between pocket residue centroids and ligand reactive atom
- median_min_dist_res_to_ligand: median minimum distance between each pocket residue and any ligand heavy atom

Ligand-independent pocket geometry
- mean_dist_backbone_to_centroid
- mean_dist_to_centroid
- mean_min_dist_to_centroid

Side-chain sterics (aligned pocket residues)
- mean_volume, weighted_mean_volume, volume_variance
- small_residue_frac, small_residue_frac_weighted
- bulky_residue_frac, bulky_residue_frac_weighted

Pocket polarity / electrostatics
- kd_mean, kd_weighted (hydrophobicity; higher = more hydrophobic)
- hw_mean, hw_weighted (polarity/exposure; more negative = less polar / less exposed)
- charged_fraction, polar_fraction

ALIGNMENT CONTEXT
The residue alignment has been filtered to include only positions that:
- show sequence variability (≥1 amino-acid type or gap), and
- are within the distance cutoff to the ligand in at least one structure.
Use this information to reason about which **variable positions directly shape the binding pocket** versus those that are peripheral.

REACTION CONTEXT (OPTIONAL)
If reaction_data is provided, use it to support structure–function reasoning.
{reaction_context_text}

OUTPUT STYLE
- Use clear, human-interpretable language.
- Emphasise geometric and chemical intuition over raw numbers.
- Keep summaries compact, comparative, and mechanistically grounded.
"""


def resolve_project_root() -> Path:
    root = Path.cwd().resolve()
    if root.name == "notebooks":
        return root.parent
    return root


def setup_data_root(root_key: str, project_root: Optional[Path] = None) -> Tuple[Path, Dict[str, Path]]:
    if root_key not in address_dict:
        raise KeyError(f"Unknown root_key: {root_key}")

    base = project_root or resolve_project_root()
    data_root = (base / address_dict[root_key]).resolve()

    resolved_dirs: Dict[str, Path] = {}
    for key in REQUIRED_SUBFOLDERS:
        if key not in subfolders:
            raise KeyError(f"Missing subfolder key in variables.subfolders: {key}")
        resolved = data_root / subfolders[key]
        resolved.mkdir(parents=True, exist_ok=True)
        resolved_dirs[key] = resolved

    return data_root, resolved_dirs


def init_thread(root_key: str, existing_thread_id: Optional[str] = None) -> Tuple[Dict[str, Any], pd.DataFrame]:
    if existing_thread_id:
        thread = load_thread(root_key, existing_thread_id)
    else:
        thread = create_thread(
            root_key=root_key,
            title="UPO binding pocket analysis",
            metadata={"notebook": "02_binding_pocket_analysis"},
        )
    preview = pd.DataFrame(list_threads(root_key)[:5])
    return thread, preview


def default_user_inputs() -> Dict[str, Any]:
    return {
        "selected_positions": [100, 103, 104, 107, 141, 222],
        "focus_question": (
            "Identify per-protein structural interpretations and cross-homolog patterns "
            "that could explain activity/property differences."
        ),
        "reaction_data_description": (
            "- Veratryl alcohol: peroxygenative\n"
            "- Naphthalene: peroxygenative\n"
            "- NBD: peroxygenative\n"
            "- ABTS: peroxidative\n"
            "- S82: mixed; Mono-Ox ~ peroxygenation-biased, Di-Ox ~ peroxidation-biased\n"
            "Use ratios (e.g. Mono-Ox : Di-Ox) to infer peroxygenation vs peroxidation balance."
        ),
        "use_reaction_data": True,
        "llm_model": "gpt-5.2",
        "llm_temperature": 0.2,
        "llm_max_rows_per_table": 300,
    }


def default_input_paths(data_root: Path) -> Tuple[Path, Path]:
    base = data_root / subfolders["pdb"] / "UPOs_peroxygenation_analysis/docked/REPS"
    binding_csv = base / "bindingpocket_analysis.csv"
    alignment_csv = base / "msa/reps_ali_withDist_FILT.csv"
    return binding_csv, alignment_csv


def load_input_tables(
    binding_csv: Path,
    alignment_csv: Path,
    reaction_data_csv: Optional[Path] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    if not binding_csv.exists():
        raise FileNotFoundError(f"Missing binding pocket file: {binding_csv}")
    if not alignment_csv.exists():
        raise FileNotFoundError(f"Missing alignment file: {alignment_csv}")

    pocket = pd.read_csv(binding_csv)
    ali = pd.read_csv(alignment_csv)
    reaction_df: Optional[pd.DataFrame] = None
    if reaction_data_csv is not None:
        if not reaction_data_csv.exists():
            raise FileNotFoundError(f"Missing reaction data file: {reaction_data_csv}")
        reaction_df = pd.read_csv(reaction_data_csv)
    return pocket, ali, reaction_df


def build_prompt_with_context(reaction_df: Optional[pd.DataFrame], user_inputs: Dict[str, Any]) -> str:
    if reaction_df is None or reaction_df.empty:
        reaction_context = "REACTION_DATA_STATUS: not provided."
    else:
        reaction_context = (
            "REACTION_DATA_STATUS: provided. "
            f"Rows={len(reaction_df)}, Columns={list(reaction_df.columns)}"
        )
    reaction_desc = str(user_inputs.get("reaction_data_description", "")).strip()
    if not reaction_desc:
        reaction_desc = "If reaction_data is provided, use it to support structure–function reasoning."
    prompt_text = prompt.format(reaction_context_text=reaction_desc)
    return f"{prompt_text}\n\n{reaction_context}"


def _table_records(df: pd.DataFrame, max_rows: int) -> List[Dict[str, Any]]:
    if df.empty:
        return []
    subset = df.head(max_rows).copy()
    subset = subset.where(pd.notnull(subset), None)
    return subset.to_dict(orient="records")


def generate_llm_pocket_analysis(
    pocket: pd.DataFrame,
    ali: pd.DataFrame,
    reaction_df: Optional[pd.DataFrame],
    user_inputs: Dict[str, Any],
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The `openai` package is required for LLM analysis.") from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Export it before running LLM analysis.")

    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    max_rows = int(user_inputs.get("llm_max_rows_per_table", 300))

    prompt_text = build_prompt_with_context(reaction_df, user_inputs)
    payload = {
        "binding_pocket_table": _table_records(pocket, max_rows),
        "pocket_alignment_table": _table_records(ali, max_rows),
        "reaction_data": None if reaction_df is None else _table_records(reaction_df, max_rows),
        "focus_question": user_inputs.get("focus_question", ""),
    }

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": "You are an expert computational enzymologist and protein engineer.",
            },
            {
                "role": "user",
                "content": f"{prompt_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}",
            },
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty analysis response.")
    return text


def _residue_signature(ali_sel: pd.DataFrame, enzyme_name: str) -> str:
    aa_col = f"{enzyme_name}_res_aa"
    if aa_col not in ali_sel.columns:
        return "n/a"

    pairs = []
    for _, row in ali_sel.iterrows():
        aa = row.get(aa_col, "-")
        if pd.isna(aa):
            aa = "-"
        pairs.append(f"{int(row['index'])}:{aa}")
    return "; ".join(pairs)


def analyze_pocket_profiles(
    pocket: pd.DataFrame,
    ali: pd.DataFrame,
    selected_positions: List[int],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if "index" not in ali.columns:
        raise KeyError("Alignment table missing 'index' column for selected positions")

    missing_metrics = [c for c in METRIC_COLS if c not in pocket.columns]
    if missing_metrics:
        raise KeyError(f"Missing expected pocket metrics: {missing_metrics}")

    ali_sel = ali[ali["index"].isin(selected_positions)].copy()
    q = pocket[METRIC_COLS].quantile([0.33, 0.67])

    rows = []
    for _, r in pocket.iterrows():
        struct_name = str(r.get("struct_name", "unknown"))
        enzyme = struct_name.split("_")[0]

        d = float(r["reactive_center_distance"])
        v = float(r["mean_volume"])
        kd = float(r["kd_weighted"])
        polar = float(r["polar_fraction"])
        charged = float(r["charged_fraction"])

        distance_tag = "closer" if d <= q.loc[0.33, "reactive_center_distance"] else (
            "farther" if d >= q.loc[0.67, "reactive_center_distance"] else "intermediate"
        )
        volume_tag = "larger" if v >= q.loc[0.67, "mean_volume"] else (
            "smaller" if v <= q.loc[0.33, "mean_volume"] else "medium"
        )
        kd_tag = "more hydrophobic" if kd >= q.loc[0.67, "kd_weighted"] else (
            "less hydrophobic" if kd <= q.loc[0.33, "kd_weighted"] else "balanced hydrophobicity"
        )
        polar_tag = "polar-enriched" if polar >= q.loc[0.67, "polar_fraction"] else (
            "less polar" if polar <= q.loc[0.33, "polar_fraction"] else "moderate polarity"
        )
        charge_tag = "charge-enriched" if charged >= q.loc[0.67, "charged_fraction"] else (
            "charge-depleted" if charged <= q.loc[0.33, "charged_fraction"] else "moderate charge"
        )

        signature = _residue_signature(ali_sel, enzyme)
        interpretation = (
            f"{enzyme}: {distance_tag} reactive-center geometry with a {volume_tag} pocket; "
            f"{kd_tag}, {polar_tag}, and {charge_tag}. "
            f"Selected-position signature [{signature}] can be compared across homologs for activity/property hypotheses."
        )

        rows.append(
            {
                "struct_name": struct_name,
                "enzyme": enzyme,
                "reactive_center_distance": d,
                "mean_volume": v,
                "kd_weighted": kd,
                "polar_fraction": polar,
                "charged_fraction": charged,
                "selected_position_signature": signature,
                "interpretation": interpretation,
            }
        )

    interp_df = pd.DataFrame(rows)
    pattern_summary = pd.DataFrame(
        [
            {
                "pattern": "closest_reactive_center",
                "struct_name": pocket.sort_values("reactive_center_distance").iloc[0]["struct_name"],
            },
            {
                "pattern": "largest_pocket",
                "struct_name": pocket.sort_values("mean_volume", ascending=False).iloc[0]["struct_name"],
            },
            {
                "pattern": "most_hydrophobic_pocket",
                "struct_name": pocket.sort_values("kd_weighted", ascending=False).iloc[0]["struct_name"],
            },
        ]
    )
    return interp_df, pattern_summary


def save_binding_outputs(interp_df: pd.DataFrame, pattern_summary: pd.DataFrame, processed_dir: Path) -> Tuple[Path, Path]:
    out_interp = processed_dir / "binding_pocket_interpretations.csv"
    out_patterns = processed_dir / "binding_pocket_pattern_summary.csv"
    interp_df.to_csv(out_interp, index=False)
    pattern_summary.to_csv(out_patterns, index=False)
    return out_interp, out_patterns


def save_llm_analysis(analysis_text: str, processed_dir: Path) -> Path:
    out_path = processed_dir / "binding_pocket_llm_analysis.md"
    out_path.write_text(analysis_text, encoding="utf-8")
    return out_path


def summarize_llm_analysis(analysis_text: str, max_chars: int = 1000) -> str:
    text = " ".join((analysis_text or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def persist_thread_update(
    root_key: str,
    thread_id: str,
    user_inputs: Dict[str, Any],
    input_paths: Dict[str, str],
    selected_positions: List[int],
    reaction_df: Optional[pd.DataFrame],
    out_interp: Path,
    out_patterns: Path,
    llm_analysis_path: Optional[Path] = None,
    llm_analysis_text: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> str:
    prompt_text = build_prompt_with_context(reaction_df, user_inputs)
    llm_summary = "" if not llm_analysis_text else summarize_llm_analysis(llm_analysis_text)
    append_message(
        root_key=root_key,
        thread_id=thread_id,
        role="user",
        content=prompt_text,
        source_notebook="02_binding_pocket_analysis",
        metadata={
            "user_inputs": user_inputs,
            "input_paths": input_paths,
            "selected_positions": selected_positions,
            "reaction_data_provided": reaction_df is not None,
            "reaction_data_rows": 0 if reaction_df is None else int(len(reaction_df)),
            "out_interp": str(out_interp),
            "out_patterns": str(out_patterns),
            "llm_analysis_path": "" if llm_analysis_path is None else str(llm_analysis_path),
            "llm_analysis_summary": llm_summary,
            "llm_model": "" if llm_model is None else llm_model,
        },
    )
    return load_thread(root_key, thread_id)["updated_at"]
