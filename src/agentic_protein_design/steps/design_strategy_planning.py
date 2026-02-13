from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from agentic_protein_design.core.chat_store import create_thread, list_threads, load_thread
from agentic_protein_design.core.pipeline_utils import (
    get_openai_client,
    persist_thread_message,
    save_text_output,
    save_text_output_with_assets_copy,
    summarize_compact_text,
)
from agentic_protein_design.core.reflection import critique_and_regenerate_text
from agentic_protein_design.core.thread_context import build_thread_context_text
from project_config.variables import address_dict, subfolders


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
LLM_PROCESS_TAG = "design_strategy_planning"

design_strategy_planning_prompt = """
You are an expert computational protein engineer and workflow architect.

Goal:
Design a practical multi-round protein design strategy that converts project requirements into an executable workflow.

Inputs:
- user_inputs_json: project requirements and design preferences
- literature_context (optional): prior literature synthesis and linked full-text summaries

Requirements:
1) Build an end-to-end strategy with clear phases (data, hypothesis, design, evaluation, iteration).
2) Explicitly choose and justify design mode:
   - de novo design, backbone-focused mutant design, or hybrid
3) Propose library strategy aligned to objectives:
   - exact targeted sequences, random mutagenesis, site-saturation mutagenesis (SSM), combinatorial library
4) Plan across the specified number of rounds with clear decision gates and progression criteria.
5) Include concrete implementation details:
   - tools/models to run per step
   - expected inputs/outputs per step
   - fallback or alternative path if a step fails
6) Integrate any relevant existing process modules when useful (for example binding_pocket_analysis).
7) Prioritize feasibility, information gain per round, and tractable experimental burden.

Available tool categories (non-exhaustive):
- sequence database search and alignment -> conservation analysis
- receptor-ligand docking / structure prediction (for example Boltz-2)
- ddG_bind style simulations (for example OpenMM or YASARA)
- stability prediction (for example Pythia)
- zero-shot scoring from protein language models
- de novo generation (for example BoltzGen or RFdiffusion2)
- supervised surrogate models (for example OHE/PLM embeddings + constrained acquisition)

Output format:
1. Executive strategy summary (5-10 bullets)
2. Assumptions and objective definition
3. Round-by-round workflow plan
   - For each round: objective, methods/tools, candidate generation strategy, filtering criteria, outputs
4. Library design plan
   - library type(s), size estimates, prioritization rationale
5. Computation stack and implementation notes
   - concrete steps and tool selection
6. Risk register and mitigations
7. Decision gates and go/no-go criteria
8. Suggested immediate next actions (first 1-2 weeks)

Style:
- concise, technically grounded, and action-oriented
- avoid generic advice; tie recommendations to provided requirements and context
"""


design_strategy_reflection_prompt = """
You are reviewing a previously generated enzyme design strategy plan.

Task:
1) Critique the original plan for gaps, weak assumptions, missing decision gates, feasibility risks, and insufficient ties to user goals.
2) Incorporate explicit user feedback if provided.
3) Regenerate an improved plan.

Important output constraint:
- Return ONLY the rewritten final plan.
- Do NOT include a separate critique section.
- Do NOT include "old plan vs new plan" comparison.
- Keep the same overall output structure used for design strategy planning.
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
            title="Design strategy planning",
            metadata={"notebook": "01_design_strategy_planning"},
            llm_process_tag=LLM_PROCESS_TAG,
        )
    preview = pd.DataFrame(list_threads(root_key, llm_process_tag=LLM_PROCESS_TAG)[:5])
    return thread, preview


def default_user_inputs() -> Dict[str, Any]:
    return {
        "enzyme_family": "unspecific peroxygenases (UPOs)",
        "seed_sequences": ["CviUPO"],
        "reactions_of_interest": "peroxygenation of aromatics",
        "substrates_of_interest": ["Veratryl alcohol", "Naphthalene", "NBD", "ABTS", "S82"],
        "application_context": "biocatalysis and green chemistry",
        "constraints": ["H2O2 tolerance", "stability", "expression host compatibility"],
        "design_type_preference": "mutants_of_backbone",
        "backbone_protein": "CviUPO",
        "library_types": [
            "targeted_mutation_set",
            "site_saturation_mutagenesis",
            "combinatorial_library",
        ],
        "num_design_rounds": 3,
        "design_targets": [
            "increase peroxygenative selectivity",
            "reduce over-oxidation",
            "maintain catalytic activity",
            "maintain or improve stability",
        ],
        "use_binding_pocket_analysis_step": True,
        "available_tools": [
            "sequence database search and alignment",
            "conservation analysis",
            "Boltz-2 docking/pose assessment",
            "OpenMM/YASARA ddG_bind simulations",
            "Pythia stability prediction",
            "protein language model zero-shot scoring",
            "BoltzGen or RFdiffusion2 de novo generation",
            "supervised surrogate models with OHE/PLM embeddings",
        ],
        "llm_model": "gpt-5.2",
        "llm_temperature": 0.2,
        "literature_context_thread_key": "",
        "plan_reflection_user_feedback": "",
        "plan_reflection_prompt_override": "",
    }


def _safe_join(items: List[str]) -> str:
    cleaned = [str(x).strip() for x in items if str(x).strip()]
    return "; ".join(cleaned)


def build_design_strategy_prompt(user_inputs: Dict[str, Any]) -> str:
    return (
        f"{design_strategy_planning_prompt}\n\n"
        "PROJECT REQUIREMENTS SNAPSHOT\n"
        f"- enzyme_family: {user_inputs.get('enzyme_family', '')}\n"
        f"- seed_sequences: {_safe_join(user_inputs.get('seed_sequences', []))}\n"
        f"- reactions_of_interest: {user_inputs.get('reactions_of_interest', '')}\n"
        f"- design_type_preference: {user_inputs.get('design_type_preference', '')}\n"
        f"- backbone_protein: {user_inputs.get('backbone_protein', '')}\n"
        f"- library_types: {_safe_join(user_inputs.get('library_types', []))}\n"
        f"- num_design_rounds: {user_inputs.get('num_design_rounds', '')}\n"
        f"- design_targets: {_safe_join(user_inputs.get('design_targets', []))}\n"
        f"- constraints: {_safe_join(user_inputs.get('constraints', []))}\n"
        f"- available_tools: {_safe_join(user_inputs.get('available_tools', []))}\n"
    )


def load_literature_context(literature_context_thread_key: Optional[str], max_chars_per_file: int = 20000) -> Dict[str, Any]:
    return build_thread_context_text(
        literature_context_thread_key,
        include_referenced_files=True,
        max_chars_per_file=max_chars_per_file,
        on_missing="warn",
    )


def generate_design_strategy_plan(
    user_inputs: Dict[str, Any],
    literature_context: str = "",
) -> str:
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))

    prompt_text = build_design_strategy_prompt(user_inputs)
    payload = {
        "user_inputs_json": user_inputs,
        "literature_context": literature_context.strip() or "Not provided.",
    }

    client = get_openai_client(
        missing_package_message="The `openai` package is required for design-strategy planning.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running design-strategy planning.",
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer and workflow strategist."},
            {"role": "user", "content": f"{prompt_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}"},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty design strategy plan.")
    return text


def reflect_and_regenerate_design_strategy_plan(
    user_inputs: Dict[str, Any],
    original_plan: str,
    *,
    literature_context: str = "",
    user_feedback: str = "",
    critique_prompt: Optional[str] = None,
) -> str:
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    prompt_text = critique_prompt or design_strategy_reflection_prompt

    return critique_and_regenerate_text(
        original_text=original_plan,
        critique_prompt=prompt_text,
        user_feedback=user_feedback,
        model=model,
        temperature=temperature,
        system_message="You are an expert computational protein engineer and workflow strategist.",
        additional_context={
            "user_inputs_json": user_inputs,
            "literature_context": literature_context.strip() or "Not provided.",
        },
    )


def save_design_strategy_plan(plan_text: str, processed_dir: Path) -> Path:
    return save_text_output_with_assets_copy(
        plan_text,
        processed_dir,
        "design_strategy_planning.md",
        assets_filename="design_strategy_planning.md",
    )


def summarize_plan_text(plan_text: str, max_chars: int = 1000) -> str:
    return summarize_compact_text(plan_text, max_chars=max_chars)


def persist_thread_update(
    root_key: str,
    thread_id: str,
    user_inputs: Dict[str, Any],
    design_plan_path: Path,
    design_plan_text: str,
    literature_context_thread_key: Optional[str] = None,
) -> str:
    prompt_text = build_design_strategy_prompt(user_inputs)
    return persist_thread_message(
        root_key=root_key,
        thread_id=thread_id,
        llm_process_tag=LLM_PROCESS_TAG,
        source_notebook="01_design_strategy_planning",
        content=prompt_text,
        metadata={
            "user_inputs": user_inputs,
            "design_plan_path": str(design_plan_path),
            "design_plan_summary": summarize_plan_text(design_plan_text),
            "literature_context_thread_key": "" if not literature_context_thread_key else str(literature_context_thread_key),
            "llm_model": str(user_inputs.get("llm_model", "")),
        },
    )


def run_design_strategy_planning_step(
    root_key: str,
    user_inputs: Dict[str, Any],
    *,
    existing_thread_key: Optional[str] = None,
    run_llm: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    data_root, resolved_dirs = setup_data_root(root_key)
    thread, _ = init_thread(root_key, existing_thread_key)
    thread_id = str(thread["thread_id"])

    literature_context_thread_key = str(user_inputs.get("literature_context_thread_key", "")).strip() or None
    context_result = load_literature_context(literature_context_thread_key)
    literature_context = str(context_result.get("context_text", ""))
    literature_context_bundle = context_result.get("context_bundle")

    design_plan_text = ""
    design_plan_path: Optional[Path] = None
    if run_llm:
        design_plan_text = generate_design_strategy_plan(user_inputs, literature_context=literature_context)
        design_plan_path = save_design_strategy_plan(design_plan_text, resolved_dirs["processed"])

    updated_at: Optional[str] = None
    if persist and design_plan_path is not None:
        updated_at = persist_thread_update(
            root_key=root_key,
            thread_id=thread_id,
            user_inputs=user_inputs,
            design_plan_path=design_plan_path,
            design_plan_text=design_plan_text,
            literature_context_thread_key=literature_context_thread_key,
        )

    return {
        "root_key": root_key,
        "thread_id": thread_id,
        "thread_updated_at": updated_at,
        "data_root": data_root,
        "resolved_dirs": resolved_dirs,
        "literature_context": literature_context,
        "literature_context_bundle": literature_context_bundle,
        "design_plan_text": design_plan_text,
        "design_plan_path": design_plan_path,
    }
