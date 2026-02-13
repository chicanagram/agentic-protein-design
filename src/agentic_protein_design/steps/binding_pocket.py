from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

import pandas as pd

from agentic_protein_design.core import resolve_input_path
from agentic_protein_design.core.chat_store import create_thread, list_threads, load_thread
from agentic_protein_design.core.pipeline_utils import (
    get_openai_client,
    persist_thread_message,
    save_text_output,
    save_text_output_with_assets_copy,
    summarize_compact_text,
    table_records,
)
from project_config.variables import address_dict, subfolders


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
LLM_PROCESS_TAG = "binding_pocket_llm_analysis"
BASE_REQUIRED_COLS = [
    "struct_name",
]

prompt_1 = """
Analyse the uploaded inputs for a set of proteins to interpret how binding-pocket structure relates to catalytic activity and selectivity. 
Consider how both the proximal (<6 Å from docked ligand) and distal (up to ~11 Å from binding pocket centroid) residues affect the binding pocket environment.

INPUTS
- binding_pocket_table: extracted binding-pocket properties (per protein), calculated separately over proximal and distal residue sets where available.
- pocket_alignment_table: filtered residue alignment of pocket-proximal positions.
- reaction_data (optional): enzyme activity data on substrates.

OBJECTIVE
For each protein, integrate structural descriptors with (optional) reaction data to infer mechanistic behavior and classify pocket phenotypes.

TASKS

1) For each protein:
   - Generate a punchy tagline.
   - Provide a concise 5-6 bullet summary addressing:
        (i) proximal electrostatics  
        (ii) proximal sterics  
        (iii) distal electrostatics  
        (iv) distal sterics / outer pocket size  
        (v) overall synthesis of pocket phenotype, integrating structural properties with catalytic implications:
            - Interpret how geometry and chemistry influence productive (peroxygenative) vs competing (peroxidative) pathways.
            - If reaction_data is provided, use it to support structure–function relationships.

   Use the following column groups:

   PROXIMAL ELECTROSTATICS
   - charged_fraction (proximal), polar_fraction (proximal)
   - kd_weighted (proximal), hw_weighted (proximal)
   - median_dist_res_to_ligand_reactive_center

   PROXIMAL STERICS
   - mean_volume (proximal), weighted_mean_volume (proximal)
   - volume_variance (proximal)
   - small_residue_frac (proximal), bulky_residue_frac (proximal)
   - median_min_dist_res_to_ligand
   - reactive_center_distance
   - num_pocket_res_lt6

   DISTAL ELECTROSTATICS
   - charged_fraction (distal), polar_fraction (distal)
   - kd_weighted (distal), hw_weighted (distal)

   DISTAL STERICS / OUTER POCKET SIZE
   - mean_dist_to_centroid
   - mean_min_dist_to_centroid
   - mean_dist_backbone_to_centroid
   - mean_volume (distal)
   - volume_variance (distal)
   - small_residue_frac (distal), bulky_residue_frac (distal)
   - num_pocket_res_ali

   If proximal/distal suffixes are not explicitly present, infer proximal/distal groupings from context and state your assumption briefly.

2) Comparative analysis requirements (do BOTH):
   A) Intra-protein variant analysis (MANDATORY when variants are present):
   - Detect proteins that share the same base protein identity but differ by variant/mutation labels.
   - For each such protein family, explicitly compare each variant against its WT/reference form (if WT/reference is present).
   - If WT is not explicitly labeled, infer the closest reference sequence in that family and state the assumption.
   - For each variant-vs-reference comparison, report which structural dimensions changed:
        (i) proximal electrostatics
        (ii) proximal sterics
        (iii) distal electrostatics
        (iv) distal sterics / outer pocket size
   - Provide a mechanistic rationale linking those differences to functional shifts.

   B) User-requested pairwise comparisons:
   - Pairwise comparisons requested: {pairwise_comparisons}
   - Perform each requested pairwise comparison in addition to section A.
   - Explicitly contrast which structural dimensions changed (prox electrostatics, prox sterics, distal electrostatics, distal sterics).
   - Provide a mechanistic rationale for functional shifts.

3) Distill cross-protein trends or clusters (“pocket phenotypes”):
   - Identify recurring structural archetypes (e.g., tight/polar pose-locking vs open/hydrophobic permissive).
   - Link clusters to turnover vs selectivity trade-offs.

OUTPUT STYLE
- Clear, human-interpretable, mechanistically grounded.
- Emphasize intuition over raw numbers.
- Keep summaries compact and comparative.
"""


prompt_2 = f"""
You are given:
1) pocket_alignment_table: filtered alignment of variable residues located within <6 Å of the ligand in at least one structure.
2) structural_summary_text: prior analysis summarizing proximal/distal sterics, electrostatics, and pocket phenotypes for each protein.

TASK

Use the alignment table together with the structural_summary_text to:

1) Identify specific residue positions that likely drive differences in electrostatics and /or sterics. For each key variable position:
   - Describe residue identities across proteins.
   - Classify substitutions as steric (small↔bulky), electrostatic (neutral↔charged), or polarity shifts.
   - Predict mechanistic consequences (e.g., tighter cage, increased radical escape, altered substrate orientation).
   - Specifically contrast the effect of point mutations in variants of the same base sequence. 
     Explain how the mutations modify the previously identified pocket environment and its chemistry. 

2) Provide a short ranked list of:
   - High-confidence mechanistic driver residues
   - Secondary modulators
   - Likely neutral/background mutations

GUIDELINES
- Use sequence numbering from each protein (not alignment index).
- Explicitly tie residue-level effects back to the structural phenotypes described earlier.
- Emphasize causal mechanistic reasoning over descriptive comparison.
- Keep the output structured and concise.

The goal is to move from global pocket phenotype to residue-level mechanistic hypotheses.
"""

prompt_3 = """
You are designing enzyme variants for rational engineering.

You are given:
1) prompt_2_output: residue-level mechanistic analysis of binding-pocket drivers.
2) literature_context (optional): prior external context (for example literature-review thread outputs).
3) design_requirements: user-provided requirements including:
   - target backbone protein to engineer
   - engineering aims (activity/selectivity/stability/pathway bias)
   - constraints (allowed positions, mutation budget, excluded residues/motifs, expression or assay limits)

TASK
Generate a concrete mutation design proposal grounded primarily in prompt_2_output and supported by literature_context when relevant.

OUTPUT FORMAT
1) Design Intent
   - State backbone protein and explicit engineering objective.

2) Proposed Mutations (ranked)
   - Provide 5-10 proposals total.
   - Include both:
     - specific substitutions (e.g., F88L), and
     - optional position-level exploration suggestions (e.g., site-saturation at position 158 with a small focused set).
   - For each proposal provide:
     - rank
     - proposal (mutation or position-set)
     - rationale linked to prompt_2 mechanistic driver(s)
     - expected directional effect on function
     - risk/tradeoff
     - confidence (high/medium/low)

3) Minimal Experimental Plan
   - Suggest a compact first-round panel (6-12 variants max), prioritizing high-information designs.
   - Include a short assay/readout plan aligned with the objective.

4) Rejected Alternatives
   - Briefly list 3-5 plausible but lower-priority options and why they were deprioritized.

RULES
- Do not invent residue numbering outside the provided context.
- Keep causal links explicit from residue-level mechanism -> mutation -> expected phenotype.
- If literature_context conflicts with prompt_2_output, state the conflict and choose a conservative design.
- Prefer practical, testable proposals over speculative broad recommendations.
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
    thread_ref = str(existing_thread_id or "").strip()
    if thread_ref:
        # Allow passing '{tag}_{thread_id}' key from chats filename stem.
        if thread_ref.endswith(".json"):
            thread_ref = thread_ref[:-5]
        m = re.match(r"^(?P<tag>[A-Za-z0-9_]+)_(?P<tid>[0-9a-fA-F]{32})$", thread_ref)
        resolved_thread_id = m.group("tid").lower() if m else thread_ref
        thread = load_thread(root_key, resolved_thread_id, llm_process_tag=LLM_PROCESS_TAG)
    else:
        thread = create_thread(
            root_key=root_key,
            title="UPO binding pocket analysis",
            metadata={"notebook": "06_binding_pocket_analysis"},
            llm_process_tag=LLM_PROCESS_TAG,
        )
    preview = pd.DataFrame(list_threads(root_key, llm_process_tag=LLM_PROCESS_TAG)[:5])
    return thread, preview


def default_user_inputs() -> Dict[str, Any]:
    return {
        "selected_positions": [100, 103, 104, 107, 141, 222],
        "pairwise_comparisons": None,  # e.g. [("CviUPO", "AaeUPO"), ("MroUPO", "rCviUPO")]
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
    pairwise = user_inputs.get("pairwise_comparisons")
    if pairwise is None:
        pairwise_text = "None"
    elif isinstance(pairwise, (list, tuple)) and pairwise:
        pair_items: List[str] = []
        for p in pairwise:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                pair_items.append(f"{p[0]} vs {p[1]}")
            else:
                pair_items.append(str(p))
        pairwise_text = "; ".join(pair_items)
    else:
        pairwise_text = str(pairwise)

    prompt1_text = prompt_1.format(pairwise_comparisons=pairwise_text)
    return (
        f"{prompt1_text}\n\n"
        "REACTION CONTEXT (OPTIONAL)\n"
        f"{reaction_desc}\n\n"
        f"{reaction_context}"
    )


def run_llm_pocket_analysis_stages(
    pocket: pd.DataFrame,
    ali: pd.DataFrame,
    reaction_df: Optional[pd.DataFrame],
    user_inputs: Dict[str, Any],
) -> Dict[str, str]:
    """
    Run prompt_1 and prompt_2 sequentially and return both stage outputs.
    """
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    max_rows = int(user_inputs.get("llm_max_rows_per_table", 300))

    prompt1_text = build_prompt_with_context(reaction_df, user_inputs)
    payload = {
        "binding_pocket_table": table_records(pocket, max_rows),
        "pocket_alignment_table": table_records(ali, max_rows),
        "reaction_data": None if reaction_df is None else table_records(reaction_df, max_rows),
        "focus_question": user_inputs.get("focus_question", ""),
    }

    client = get_openai_client(
        missing_package_message="The `openai` package is required for LLM analysis.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running LLM analysis.",
    )
    print("=== Prompt 1 Sent To LLM ===")
    print(prompt1_text)
    response_1 = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": "You are an expert computational enzymologist and protein engineer.",
            },
            {
                "role": "user",
                "content": f"{prompt1_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}",
            },
        ],
    )
    response_1_text = (response_1.choices[0].message.content or "").strip()
    if not response_1_text:
        raise RuntimeError("LLM returned an empty analysis response for prompt 1.")
    print("\n=== LLM Output 1 ===")
    print(response_1_text)

    prompt2_text = prompt_2
    payload_2 = {
        "pocket_alignment_table": table_records(ali, max_rows),
        "structural_summary_text": response_1_text,
        "focus_question": user_inputs.get("focus_question", ""),
    }
    print("\n=== Prompt 2 Sent To LLM ===")
    print(prompt2_text)
    response_2 = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": "You are an expert computational enzymologist and protein engineer.",
            },
            {
                "role": "user",
                "content": (
                    f"{prompt2_text}\n\n"
                    f"INPUT_DATA_JSON:\n{json.dumps(payload_2, ensure_ascii=True)}"
                ),
            },
        ],
    )
    response_2_text = (response_2.choices[0].message.content or "").strip()
    if not response_2_text:
        raise RuntimeError("LLM returned an empty analysis response for prompt 2.")
    print("\n=== LLM Output 2 ===")
    print(response_2_text)

    combined = (
        "## Stage 1: Global Pocket Phenotypes\n\n"
        f"{response_1_text}\n\n"
        "## Stage 2: Residue-Level Mechanistic Drivers\n\n"
        f"{response_2_text}"
    )
    return {
        "prompt_1_text": prompt1_text,
        "prompt_1_output": response_1_text,
        "prompt_2_text": prompt2_text,
        "prompt_2_output": response_2_text,
        "combined_analysis": combined,
    }


def generate_llm_pocket_analysis(
    pocket: pd.DataFrame,
    ali: pd.DataFrame,
    reaction_df: Optional[pd.DataFrame],
    user_inputs: Dict[str, Any],
) -> str:
    stage_outputs = run_llm_pocket_analysis_stages(pocket, ali, reaction_df, user_inputs)
    return stage_outputs["combined_analysis"]


def generate_llm_mutation_design_proposal(
    prompt_2_output: str,
    design_requirements: str,
    *,
    user_inputs: Optional[Dict[str, Any]] = None,
    literature_context: str = "",
) -> str:
    """
    Run prompt_3 using stage-2 residue analysis and optional external literature context.
    """
    settings = user_inputs or {}
    model = str(settings.get("llm_model", "gpt-5.2"))
    temperature = float(settings.get("llm_temperature", 0.2))

    literature_context_text = literature_context.strip() or "Not provided."
    design_requirements_text = design_requirements.strip() or "No explicit design requirements provided."

    payload = {
        "prompt_2_output": prompt_2_output.strip(),
        "literature_context": literature_context_text,
        "design_requirements": design_requirements_text,
    }
    client = get_openai_client(
        missing_package_message="The `openai` package is required for LLM analysis.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running LLM analysis.",
    )
    print("\n=== Prompt 3 Sent To LLM ===")
    print(prompt_3)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": "You are an expert computational enzymologist and rational protein engineer.",
            },
            {
                "role": "user",
                "content": f"{prompt_3}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}",
            },
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty mutation design proposal for prompt 3.")
    print("\n=== LLM Output 3 ===")
    print(text)
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


def _detect_metric_cols(pocket: pd.DataFrame) -> List[str]:
    """
    Use all numeric pocket-property columns and exclude metadata/index columns.
    This supports both suffixed distal/proximal columns and unsuffixed core metrics.
    """
    excluded = {
        "struct_name",
        "struct_name.1",
        "struct_name.2",
        "enzyme",
    }
    metric_cols: List[str] = []
    for c in pocket.columns:
        lc = c.lower().strip()
        if lc.startswith("unnamed:"):
            continue
        if c in excluded:
            continue
        series_num = pd.to_numeric(pocket[c], errors="coerce")
        if series_num.notna().any():
            metric_cols.append(c)
    return metric_cols


def analyze_pocket_profiles(
    pocket: pd.DataFrame,
    ali: pd.DataFrame,
    selected_positions: List[int],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    missing_base = [c for c in BASE_REQUIRED_COLS if c not in pocket.columns]
    if missing_base:
        raise KeyError(f"Pocket table missing required columns: {missing_base}")

    if "index" not in ali.columns:
        raise KeyError("Alignment table missing 'index' column for selected positions")

    metric_cols = _detect_metric_cols(pocket)
    if not metric_cols:
        raise KeyError(
            "No numeric pocket metrics detected. Expected columns with '(distal)'/'(proximal)' "
            "suffixes and/or core metric columns."
        )

    if selected_positions is not None:
        ali_sel = ali[ali["index"].isin(selected_positions)].copy()
    else:
        ali_sel = ali.copy()
    pocket_num = pocket.copy()
    for c in metric_cols:
        pocket_num[c] = pd.to_numeric(pocket_num[c], errors="coerce")
    q = pocket_num[metric_cols].quantile([0.33, 0.67])

    def quantile_tag(value: float, metric: str) -> str:
        if pd.isna(value):
            return "na"
        q33 = q.loc[0.33, metric]
        q67 = q.loc[0.67, metric]
        if pd.isna(q33) or pd.isna(q67):
            return "na"
        if value <= q33:
            return "low"
        if value >= q67:
            return "high"
        return "mid"

    rows = []
    for _, r in pocket_num.iterrows():
        struct_name = str(r.get("struct_name", "unknown"))
        enzyme = struct_name.split("_")[0]

        signature = _residue_signature(ali_sel, enzyme)
        metric_values = {m: (None if pd.isna(r[m]) else float(r[m])) for m in metric_cols}
        metric_tags = {m: quantile_tag(r[m], m) for m in metric_cols}

        high_metrics = [m for m in metric_cols if metric_tags[m] == "high"]
        low_metrics = [m for m in metric_cols if metric_tags[m] == "low"]
        # Keep interpretation compact while still using all metrics in stored fields.
        high_preview = ", ".join(high_metrics[:5]) if high_metrics else "none"
        low_preview = ", ".join(low_metrics[:5]) if low_metrics else "none"
        interpretation = (
            f"{enzyme}: metric profile computed from {len(metric_cols)} pocket descriptors "
            f"(distal/proximal + core geometry). High-quantile examples: {high_preview}. "
            f"Low-quantile examples: {low_preview}. "
            f"Selected-position signature [{signature}] can be compared across homologs for activity/property hypotheses."
        )

        rows.append(
            {
                "struct_name": struct_name,
                "enzyme": enzyme,
                "n_metrics_used": len(metric_cols),
                "metric_values": json.dumps(metric_values, ensure_ascii=True),
                "metric_quantile_tags": json.dumps(metric_tags, ensure_ascii=True),
                "selected_position_signature": signature,
                "interpretation": interpretation,
            }
        )

    interp_df = pd.DataFrame(rows)
    pattern_rows: List[Dict[str, Any]] = []
    for m in metric_cols:
        s = pocket_num[["struct_name", m]].dropna()
        if s.empty:
            continue
        min_row = s.sort_values(m, ascending=True).iloc[0]
        max_row = s.sort_values(m, ascending=False).iloc[0]
        pattern_rows.append(
            {
                "pattern": f"min::{m}",
                "struct_name": min_row["struct_name"],
                "metric": m,
                "value": float(min_row[m]),
            }
        )
        pattern_rows.append(
            {
                "pattern": f"max::{m}",
                "struct_name": max_row["struct_name"],
                "metric": m,
                "value": float(max_row[m]),
            }
        )
    pattern_summary = pd.DataFrame(pattern_rows)
    return interp_df, pattern_summary


def save_binding_outputs(interp_df: pd.DataFrame, pattern_summary: pd.DataFrame, processed_dir: Path) -> Tuple[Path, Path]:
    out_interp = processed_dir / "binding_pocket_interpretations.csv"
    out_patterns = processed_dir / "binding_pocket_pattern_summary.csv"
    interp_df.to_csv(out_interp, index=False)
    pattern_summary.to_csv(out_patterns, index=False)
    return out_interp, out_patterns


def save_llm_analysis(analysis_text: str, processed_dir: Path) -> Path:
    return save_text_output_with_assets_copy(
        analysis_text,
        processed_dir,
        "binding_pocket_llm_analysis.md",
        assets_filename="binding_pocket_llm_analysis.md",
    )


def save_mutation_design_proposal(proposal_text: str, processed_dir: Path) -> Path:
    return save_text_output_with_assets_copy(
        proposal_text,
        processed_dir,
        "binding_pocket_mutation_design.md",
        assets_filename="binding_pocket_mutation_design.md",
    )


def summarize_llm_analysis(analysis_text: str, max_chars: int = 1000) -> str:
    return summarize_compact_text(analysis_text, max_chars=max_chars)


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
    mutation_design_path: Optional[Path] = None,
    mutation_design_text: Optional[str] = None,
    literature_context_thread_key: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> str:
    prompt_text = build_prompt_with_context(reaction_df, user_inputs)
    llm_summary = "" if not llm_analysis_text else summarize_llm_analysis(llm_analysis_text)
    mutation_design_summary = "" if not mutation_design_text else summarize_llm_analysis(mutation_design_text)
    return persist_thread_message(
        root_key=root_key,
        thread_id=thread_id,
        llm_process_tag=LLM_PROCESS_TAG,
        source_notebook="06_binding_pocket_analysis",
        content=prompt_text,
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
            "mutation_design_path": "" if mutation_design_path is None else str(mutation_design_path),
            "mutation_design_summary": mutation_design_summary,
            "literature_context_thread_key": "" if not literature_context_thread_key else str(literature_context_thread_key),
            "llm_model": "" if llm_model is None else llm_model,
        },
    )


def run_binding_pocket_step(
    root_key: str,
    user_inputs: Dict[str, Any],
    input_paths: Dict[str, str],
    *,
    existing_thread_id: Optional[str] = None,
    run_llm: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Run the full binding-pocket step and return outputs for downstream composition.
    """
    data_root, resolved_dirs = setup_data_root(root_key)
    thread, _ = init_thread(root_key, existing_thread_id)
    thread_id = str(thread["thread_id"])

    binding_csv = resolve_input_path(data_root, input_paths["binding_csv"])
    alignment_csv = resolve_input_path(data_root, input_paths["alignment_csv"])

    reaction_rel = str(input_paths.get("reaction_data_csv", "")).strip()
    reaction_csv: Optional[Path] = resolve_input_path(data_root, reaction_rel) if reaction_rel else None

    pocket, ali, reaction_df = load_input_tables(binding_csv, alignment_csv, reaction_csv)

    selected_positions = user_inputs.get("selected_positions")
    interp_df, pattern_summary = analyze_pocket_profiles(pocket, ali, selected_positions=selected_positions)
    out_interp, out_patterns = save_binding_outputs(interp_df, pattern_summary, resolved_dirs["processed"])

    llm_analysis_text: Optional[str] = None
    llm_analysis_path: Optional[Path] = None
    if run_llm:
        llm_analysis_text = generate_llm_pocket_analysis(pocket, ali, reaction_df, user_inputs)
        llm_analysis_path = save_llm_analysis(llm_analysis_text, resolved_dirs["processed"])

    updated_at: Optional[str] = None
    if persist:
        updated_at = persist_thread_update(
            root_key=root_key,
            thread_id=thread_id,
            user_inputs=user_inputs,
            input_paths=input_paths,
            selected_positions=[] if selected_positions is None else list(selected_positions),
            reaction_df=reaction_df,
            out_interp=out_interp,
            out_patterns=out_patterns,
            llm_analysis_path=llm_analysis_path,
            llm_analysis_text=llm_analysis_text,
            llm_model=str(user_inputs.get("llm_model", "")),
        )

    return {
        "root_key": root_key,
        "thread_id": thread_id,
        "thread_updated_at": updated_at,
        "data_root": data_root,
        "resolved_dirs": resolved_dirs,
        "user_inputs": user_inputs,
        "input_paths": input_paths,
        "pocket": pocket,
        "alignment": ali,
        "reaction_df": reaction_df,
        "interp_df": interp_df,
        "pattern_summary": pattern_summary,
        "out_interp": out_interp,
        "out_patterns": out_patterns,
        "llm_analysis_text": llm_analysis_text,
        "llm_analysis_path": llm_analysis_path,
    }
