from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from agentic_protein_design.core import resolve_input_path
from agentic_protein_design.core.chat_store import create_thread, list_threads, load_thread
from agentic_protein_design.core.llm_display import display_llm_output_bundle
from agentic_protein_design.core.pipeline_utils import (
    get_openai_client,
    persist_thread_message,
    save_text_output_with_assets_copy,
    summarize_compact_text,
    table_records,
)
from agentic_protein_design.core.thread_context import build_thread_context_text
from project_config.variables import address_dict, subfolders


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
LLM_PROCESS_TAG = "analyze_mutants_llm"
STEP_OUTPUT_SUBDIR = "analyze_mutants"

mutant_analysis_prompt = """
You are an expert computational protein engineer.

You are given a mutagenesis table where each row is a mutant/variant with one or more mutations
and associated measured/computed properties (for example activity fold-change, stability proxy,
distance to ligand, pocket descriptors, and optional contextual summaries).

Task:
1) For each mutant row, provide a concise, human-interpretable mechanistic explanation linking
   the mutation(s) and relevant columns to expected/observed behavior.
2) Highlight likely causal positions versus likely neutral/passenger changes.
3) Group mutants into a few interpretable mechanism buckets.
4) Identify high-priority mutants to follow up and briefly justify.
5) Identify ambiguous cases and what additional data would disambiguate them.

Output format:
A) Executive summary (5-8 bullets)
B) Per-mutant explanations table-like markdown:
   - mutant_id (or row index)
   - key mutation(s)
   - concise interpretation
   - confidence (high/medium/low)
C) Cross-mutant mechanism patterns
D) Prioritized follow-up list
E) Data gaps and next measurements

Rules:
- Ground reasoning in provided columns; do not invent facts.
- If key columns are missing/ambiguous, state assumptions explicitly.
- Keep explanations compact, practical, and test-oriented.
"""

mutant_analysis_csv_prompt = """
You are an expert computational protein engineer.

You are given a mutagenesis table where each row is a mutant/variant with one or more mutations
and associated measured/computed properties.

Return ONLY a JSON array where each item is one explanatory unit for downstream CSV export.
Each item must include:
- unit_type: one of
  1) "single_mutation"
  2) "single_position_mutation_group"
  3) "phenotypic_cluster"
  4) "unique_multi_mutation_mutant"
  5) "multi_mutation_cluster"
- unit_id: concise unique identifier for this output row
- source_rows: list of source mutant IDs or row indexes used for this unit
- positions: list of residue positions referenced in this unit
- mutations: list of mutation strings (for example ["A23V", "L57F"])
- phenotype_basis: short phrase describing why these were grouped (or "N/A")
- Explanation: concise human-interpretable explanation of likely effect
- confidence: one of "high", "medium", "low"

If no valid units can be formed, return [].
Do not include markdown, prose, or code fences.
"""

MUTANT_EXPLANATION_COLUMNS = [
    "unit_type",
    "unit_id",
    "source_rows",
    "positions",
    "mutations",
    "phenotype_basis",
    "Explanation",
    "confidence",
]


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


def get_step_processed_dir(resolved_dirs: Dict[str, Path]) -> Path:
    step_dir = (resolved_dirs["processed"] / STEP_OUTPUT_SUBDIR).resolve()
    step_dir.mkdir(parents=True, exist_ok=True)
    return step_dir


def init_thread(root_key: str, existing_thread_key: Optional[str] = None) -> Tuple[Dict[str, Any], pd.DataFrame]:
    thread_ref = str(existing_thread_key or "").strip()
    if thread_ref:
        if thread_ref.endswith(".json"):
            thread_ref = thread_ref[:-5]
        m = re.match(r"^(?P<tag>[A-Za-z0-9_]+)_(?P<tid>[0-9a-fA-F]{32})$", thread_ref)
        resolved_thread_id = m.group("tid").lower() if m else thread_ref
        thread = load_thread(root_key, resolved_thread_id, llm_process_tag=LLM_PROCESS_TAG)
    else:
        thread = create_thread(
            root_key=root_key,
            title="Analyze mutants",
            metadata={"notebook": "15_analyze_mutants"},
            llm_process_tag=LLM_PROCESS_TAG,
        )
    preview = pd.DataFrame(list_threads(root_key, llm_process_tag=LLM_PROCESS_TAG)[:5])
    return thread, preview


def default_user_inputs() -> Dict[str, Any]:
    return {
        "focus_question": (
            "Explain which mutated positions are likely driving observed changes in activity/selectivity "
            "and which mutations are likely secondary."
        ),
        "llm_model": "gpt-5.2",
        "llm_temperature": 0.2,
        "llm_max_rows": 500,
        "display_llm_output": True,
        "display_max_height": "640px",
        "context_thread_key": "",
    }


def default_input_paths(data_root: Path) -> Dict[str, str]:
    return {
        "mutants_csv": str((data_root / subfolders["expdata"] / "mutants_to_analyze.csv").resolve()),
    }


def load_mutant_table(mutants_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(mutants_csv)
    if df.empty:
        raise ValueError(f"Mutant table is empty: {mutants_csv}")
    return df


def build_mutant_analysis_prompt(user_inputs: Dict[str, Any]) -> str:
    return (
        f"{mutant_analysis_prompt}\n\n"
        "USER FOCUS\n"
        f"- focus_question: {str(user_inputs.get('focus_question', '')).strip()}\n"
    )


def build_mutant_analysis_csv_prompt(user_inputs: Dict[str, Any]) -> str:
    return (
        f"{mutant_analysis_csv_prompt}\n\n"
        "USER FOCUS\n"
        f"- focus_question: {str(user_inputs.get('focus_question', '')).strip()}\n"
    )


def _extract_json_array(text: str) -> List[Dict[str, Any]]:
    raw = (text or "").strip()
    if not raw:
        return []

    fenced_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        raw = fenced_match.group(1).strip()

    if not raw.startswith("["):
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and end > start:
            raw = raw[start : end + 1]

    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        raise ValueError("LLM output is not a JSON array.")

    rows: List[Dict[str, Any]] = []
    for item in parsed:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _normalize_explanation_rows(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    normalized: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        unit_type = str(row.get("unit_type", "")).strip()
        unit_id = str(row.get("unit_id", "")).strip() or f"unit_{idx}"

        source_rows = row.get("source_rows", [])
        if isinstance(source_rows, (str, int)):
            source_rows = [source_rows]
        if not isinstance(source_rows, list):
            source_rows = []

        positions = row.get("positions", [])
        if isinstance(positions, (str, int)):
            positions = [positions]
        if not isinstance(positions, list):
            positions = []

        mutations = row.get("mutations", [])
        if isinstance(mutations, str):
            mutations = [mutations]
        if not isinstance(mutations, list):
            mutations = []

        confidence = str(row.get("confidence", "medium")).strip().lower()
        if confidence not in {"high", "medium", "low"}:
            confidence = "medium"

        normalized.append(
            {
                "unit_type": unit_type,
                "unit_id": unit_id,
                "source_rows": json.dumps(source_rows, ensure_ascii=True),
                "positions": json.dumps(positions, ensure_ascii=True),
                "mutations": json.dumps(mutations, ensure_ascii=True),
                "phenotype_basis": str(row.get("phenotype_basis", "")).strip(),
                "Explanation": str(row.get("Explanation", "")).strip(),
                "confidence": confidence,
            }
        )

    df = pd.DataFrame.from_records(normalized)
    if df.empty:
        return pd.DataFrame(columns=MUTANT_EXPLANATION_COLUMNS)
    return df.reindex(columns=MUTANT_EXPLANATION_COLUMNS)


def load_optional_context(context_thread_key: Optional[str]) -> Dict[str, Any]:
    return build_thread_context_text(
        context_thread_key,
        include_referenced_files=True,
        max_chars_per_file=20000,
        on_missing="warn",
    )


def generate_llm_mutant_analysis(
    mutant_df: pd.DataFrame,
    user_inputs: Dict[str, Any],
    *,
    supplemental_context: str = "",
) -> str:
    explanations_df, llm_json_text = generate_llm_mutant_explanations(
        mutant_df,
        user_inputs,
        supplemental_context=supplemental_context,
    )
    if explanations_df.empty:
        return "No explanation rows were generated."
    return (
        "Generated explanation units table:\n\n"
        + explanations_df.to_markdown(index=False)
        + "\n\nRaw LLM JSON:\n```json\n"
        + llm_json_text
        + "\n```"
    )


def generate_llm_mutant_explanations(
    mutant_df: pd.DataFrame,
    user_inputs: Dict[str, Any],
    *,
    supplemental_context: str = "",
) -> Tuple[pd.DataFrame, str]:
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    max_rows = int(user_inputs.get("llm_max_rows", 500))

    prompt_text = build_mutant_analysis_csv_prompt(user_inputs)
    payload = {
        "mutant_table": table_records(mutant_df, max_rows),
        "supplemental_context": supplemental_context.strip() or "Not provided.",
    }

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
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty mutant analysis.")

    parsed_rows = _extract_json_array(text)
    explanations_df = _normalize_explanation_rows(parsed_rows)

    if bool(user_inputs.get("display_llm_output", True)):
        preview_text = "No explanation units generated."
        if not explanations_df.empty:
            preview_text = explanations_df.to_markdown(index=False)
        display_llm_output_bundle(
            exchanges=[
                {
                    "title": "Mutant Analysis LLM Call",
                    "prompt_text": prompt_text,
                    "response_text": "(Structured explanation rows generated; preview shown below.)",
                }
            ],
            compact_markdown_blocks=[
                {
                    "heading": "Mutant Explanation Rows (Preview)",
                    "text": preview_text,
                    "max_height": str(user_inputs.get("display_max_height", "640px")),
                }
            ],
            use_compact_markdown=bool(user_inputs.get("display_compact_markdown", False)),
        )
    return explanations_df, text


def save_mutant_outputs(mutant_df: pd.DataFrame, processed_dir: Path) -> Path:
    out_path = processed_dir / "mutants_input_snapshot.csv"
    mutant_df.to_csv(out_path, index=False)
    return out_path


def save_llm_analysis(analysis_text: str, processed_dir: Path) -> Path:
    return save_text_output_with_assets_copy(
        analysis_text,
        processed_dir,
        "mutant_analysis_llm_summary.md",
        assets_filename="mutant_analysis_llm_summary.md",
    )


def save_mutant_explanations_csv(explanations_df: pd.DataFrame, processed_dir: Path) -> Path:
    out_path = processed_dir / "mutant_explanations.csv"
    explanations_df.to_csv(out_path, index=False)
    return out_path


def persist_thread_update(
    root_key: str,
    thread_id: str,
    user_inputs: Dict[str, Any],
    input_paths: Dict[str, str],
    mutants_snapshot_path: Path,
    explanations_csv_path: Optional[Path],
    llm_analysis_path: Optional[Path],
    llm_analysis_text: Optional[str],
    context_thread_key: Optional[str] = None,
) -> str:
    prompt_text = build_mutant_analysis_prompt(user_inputs)
    return persist_thread_message(
        root_key=root_key,
        thread_id=thread_id,
        llm_process_tag=LLM_PROCESS_TAG,
        source_notebook="15_analyze_mutants",
        content=prompt_text,
        metadata={
            "user_inputs": user_inputs,
            "input_paths": input_paths,
            "mutants_snapshot_path": str(mutants_snapshot_path),
            "explanations_csv_path": "" if explanations_csv_path is None else str(explanations_csv_path),
            "llm_analysis_path": "" if llm_analysis_path is None else str(llm_analysis_path),
            "llm_analysis_summary": "" if not llm_analysis_text else summarize_compact_text(llm_analysis_text),
            "context_thread_key": "" if not context_thread_key else str(context_thread_key),
            "llm_model": str(user_inputs.get("llm_model", "")),
        },
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
    Execute end-to-end mutant analysis step.
    """
    data_root, resolved_dirs = setup_data_root(root_key)
    step_processed_dir = get_step_processed_dir(resolved_dirs)
    thread, _ = init_thread(root_key, existing_thread_key)
    thread_id = str(thread["thread_id"])

    mutants_csv = resolve_input_path(data_root, input_paths["mutants_csv"])
    mutant_df = load_mutant_table(mutants_csv)
    mutants_snapshot_path = save_mutant_outputs(mutant_df, step_processed_dir)

    context_thread_key = str(user_inputs.get("context_thread_key", "")).strip() or None
    context_result = load_optional_context(context_thread_key)
    supplemental_context = str(context_result.get("context_text", ""))

    explanations_df, llm_json_text = generate_llm_mutant_explanations(
        mutant_df,
        user_inputs,
        supplemental_context=supplemental_context,
    )
    explanations_csv_path = save_mutant_explanations_csv(explanations_df, step_processed_dir)
    llm_analysis_text = (
        "Mutant explanation units (CSV exported):\n\n"
        + (explanations_df.to_markdown(index=False) if not explanations_df.empty else "No rows.")
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
            mutants_snapshot_path=mutants_snapshot_path,
            explanations_csv_path=explanations_csv_path,
            llm_analysis_path=llm_analysis_path,
            llm_analysis_text=llm_analysis_text,
            context_thread_key=context_thread_key,
        )

    return {
        "root_key": root_key,
        "thread_id": thread_id,
        "thread_updated_at": updated_at,
        "data_root": data_root,
        "resolved_dirs": resolved_dirs,
        "step_processed_dir": step_processed_dir,
        "mutants_csv": mutants_csv,
        "mutant_df": mutant_df,
        "mutants_snapshot_path": mutants_snapshot_path,
        "context_result": context_result,
        "explanations_df": explanations_df,
        "explanations_csv_path": explanations_csv_path,
        "llm_analysis_text": llm_analysis_text,
        "llm_analysis_path": llm_analysis_path,
    }
