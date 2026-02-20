from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from agentic_protein_design.core.chat_store import create_thread, list_threads, load_thread
from agentic_protein_design.core.llm_display import display_llm_output_bundle
from agentic_protein_design.core.pipeline_utils import (
    get_openai_client,
    persist_thread_message,
    save_text_output,
    save_text_output_with_assets_copy,
    summarize_compact_text,
)
from agentic_protein_design.core.thread_context import build_thread_context_text
from project_config.variables import address_dict, subfolders


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
LLM_PROCESS_TAG = "design_strategy_planning"
STEP_OUTPUT_SUBDIR = "01_design_strategy_planning"

design_strategy_base_prompt = """
You are an expert computational protein engineer and workflow architect.

Goal:
Convert project requirements into an executable multi-step protein-design workflow.

Inputs:
- user_inputs_json: project requirements and design preferences
- literature_context (optional): prior literature synthesis and linked full-text summaries

Requirements:
1) Build an end-to-end strategy with clear phases (data, hypothesis, design, evaluation, iteration).
2) Explicitly choose and justify design mode:
   - de novo design, backbone-focused mutant design, or hybrid
3) Propose library strategy aligned to objectives:
   - exact targeted sequences, random mutagenesis, site-saturation mutagenesis (SSM), combinatorial library
4) Plan across the specified number of rounds and approximate size of each round, with clear decision gates and progression criteria.
5) Include concrete implementation details:
   - tools/models to run per step
   - expected inputs/outputs per step
   - fallback or alternative path if a step fails
6) Integrate relevant existing process modules when useful (for example binding_pocket_analysis).
7) Prioritize feasibility, information gain per round, and tractable experimental burden.

Available tool categories (non-exhaustive):
- sequence database search and alignment -> conservation analysis
- receptor-ligand docking / structure prediction (for example Boltz-2)
- ddG_bind style simulations (for example OpenMM or YASARA)
- stability prediction (for example Pythia)
- zero-shot scoring from protein language models
- de novo generation (for example BoltzGen or RFdiffusion2)
- supervised surrogate models (for example OHE/PLM embeddings + constrained acquisition)
"""


design_strategy_planning_prompt_1 = """
PART 1: Build an executable workflow specification as structured JSON.

Output contract (strict):
- Return ONLY a JSON array.
- Each array element must be a JSON object representing one consecutive workflow step.
- Do not include markdown, comments, code fences, or extra prose.

Required fields per step object:
- "step_index": integer (1-based consecutive order)
- "step_name": short unique string
- "tools_from_registry": array of strings selected from the provided available_tools list
- "python_code_to_execute": string containing runnable Python pseudo-code for that step
- "rationale": concise string
- "description": concise string describing what the step does and expected input/output at a high level

Rules:
- Keep python_code_to_execute realistic and implementation-oriented (imports, function calls, key args).
- Ensure sequence is executable as a pipeline (later steps use outputs of earlier steps).
- Include practical fallback logic in rationale/description where relevant.
- Keep total number of steps to 6-12 unless the user context strongly requires otherwise.
"""


design_strategy_planning_prompt_2 = """
PART 2: Write a concise human-readable strategy summary using:
1) the original context, and
2) the PART 1 JSON workflow.

Output contract:
- Return ONLY markdown prose.
- Keep it succinct and action-oriented (target ~350-700 words).

Required sections:
1. Overall strategy (5-8 bullets)
2. Design choices and assumptions (short)
3. Step-by-step execution summary
   - one compact paragraph per step from PART 1
   - if a step proposes using a foundational Protein Language Model or Structure-prediction model is proposed, recommend which models to use.
   - if a step proposes using a supervised Machine Learning model trained on screening data, propose the model type and input features to use (ok to provide options)
4. Decision gates and immediate next actions (short)
"""


design_strategy_reflection_prompt = """
You are reviewing previously generated planning artifacts:
1) a human-readable strategy writeup (Prompt 2 output), and
2) a structured workflow JSON list (Prompt 1 output).

Task:
1) Critique consistency and quality across both artifacts:
   - gaps, weak assumptions, missing decision gates, feasibility risks
   - mismatches between workflow JSON steps and writeup narrative
   - missing or unclear implementation details in either artifact
2) Incorporate explicit user feedback if provided.
3) Regenerate an improved human-readable plan that is aligned with the workflow JSON.

Important output constraint:
- Return ONLY the rewritten final plan.
- Do NOT include a separate critique section.
- Do NOT include "old plan vs new plan" comparison.
- Keep the same overall output structure used for design strategy planning.
"""


design_strategy_reflection_prompt_1 = """
PART 1 REFLECTION: Improve the structured workflow JSON.

You are given:
- original_prompt_1_workflow_json
- original_prompt_2_writeup
- user_inputs_json
- literature_context
- user_feedback (optional)

Task:
- Regenerate an improved workflow JSON list that is more coherent, feasible, and aligned with goals.
- Resolve inconsistencies between original workflow and writeup.

Output contract (strict):
- Return ONLY a JSON array of step objects.
- Keep required fields per step:
  step_index, step_name, tools_from_registry, python_code_to_execute, rationale, description
"""


design_strategy_reflection_prompt_2 = """
PART 2 REFLECTION: Improve the concise human-readable strategy writeup.

You are given:
- improved_prompt_1_workflow_json
- original_prompt_2_writeup
- user_inputs_json
- literature_context
- user_feedback (optional)

Task:
- Regenerate a better concise writeup aligned with improved workflow JSON.

Output contract:
- Return ONLY markdown prose.
- Keep concise/actionable style and the same sectioning as planning prompt part 2.
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


def get_step_processed_dir(resolved_dirs: Dict[str, Path]) -> Path:
    """
    Return/create processed output directory for this notebook step.
    """
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
            title="Design strategy planning",
            metadata={"notebook": "01_design_strategy_planning"},
            llm_process_tag=LLM_PROCESS_TAG,
        )
    preview = pd.DataFrame(list_threads(root_key, llm_process_tag=LLM_PROCESS_TAG)[:5])
    return thread, preview


def default_user_inputs() -> Dict[str, Any]:
    """
    Return editable defaults for design-strategy planning notebook/step.

    Returns:
        Dict of project requirements, tool preferences, and LLM settings.
    """
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
        "display_llm_output": True,
        "display_max_height": "640px",
        "literature_context_thread_key": "",
        "plan_reflection_user_feedback": "",
        "plan_reflection_prompt_override": "",
    }


def _safe_join(items: List[str]) -> str:
    cleaned = [str(x).strip() for x in items if str(x).strip()]
    return "; ".join(cleaned)


def build_design_strategy_prompt(user_inputs: Dict[str, Any]) -> str:
    """
    Build the full planning prompt from structured user inputs.

    Args:
        user_inputs: Dictionary matching `default_user_inputs()` schema.

    Returns:
        Prompt string sent to the LLM planning call.
    """
    return (
        f"{design_strategy_base_prompt}\n\n"
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


def _extract_json_array(text: str) -> List[Dict[str, Any]]:
    raw = str(text or "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
    except Exception:
        pass

    match = re.search(r"\[[\s\S]*\]", raw)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [x for x in parsed if isinstance(x, dict)]
        except Exception:
            return []
    return []


def workflow_steps_to_dataframe(workflow_steps_json: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert prompt-1 workflow JSON into a compact, readable table.
    """
    rows: List[Dict[str, Any]] = []
    for step in workflow_steps_json or []:
        tools = step.get("tools_from_registry", [])
        tools_text = ", ".join([str(t).strip() for t in tools if str(t).strip()]) if isinstance(tools, list) else str(tools)
        code_text = str(step.get("python_code_to_execute", "")).strip().replace("\n", " ")
        rows.append(
            {
                "step_index": step.get("step_index", ""),
                "step_name": str(step.get("step_name", "")).strip(),
                "tools": tools_text,
                "description": str(step.get("description", "")).strip(),
                "rationale": str(step.get("rationale", "")).strip(),
                "python_code_preview": (code_text[:140] + "...") if len(code_text) > 140 else code_text,
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty and "step_index" in df.columns:
        try:
            df = df.sort_values("step_index").reset_index(drop=True)
        except Exception:
            pass
    return df


def load_literature_context(literature_context_thread_key: Optional[str], max_chars_per_file: int = 20000) -> Dict[str, Any]:
    """
    Load optional prior literature-thread context for plan conditioning.

    Args:
        literature_context_thread_key: Tagged thread id or raw thread id.
        max_chars_per_file: Per-file cap when loading referenced artifacts.

    Returns:
        Context bundle dictionary containing assembled text and diagnostics.
    """
    return build_thread_context_text(
        literature_context_thread_key,
        include_referenced_files=True,
        max_chars_per_file=max_chars_per_file,
        on_missing="warn",
    )


def generate_design_strategy_plan(
    user_inputs: Dict[str, Any],
    literature_context: str = "",
    *,
    return_full: bool = False,
) -> Any:
    """
    Generate a design strategy plan from requirements and optional context.

    Args:
        user_inputs: Planning input dictionary.
        literature_context: Optional prior context text.

    Returns:
        Dictionary containing both Prompt-1 JSON workflow output and Prompt-2 writeup.
    """
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
    # PART 1: structured workflow specification
    prompt_1_text = f"{prompt_text}\n\n{design_strategy_planning_prompt_1}"
    response_1 = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer and workflow strategist."},
            {"role": "user", "content": f"{prompt_1_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}"},
        ],
    )
    response_1_text = (response_1.choices[0].message.content or "").strip()
    workflow_steps = _extract_json_array(response_1_text)
    if not workflow_steps:
        raise RuntimeError("LLM returned invalid/empty workflow JSON for design strategy prompt part 1.")

    # PART 2: concise human-readable strategy writeup conditioned on part 1
    payload_2 = {
        "user_inputs_json": user_inputs,
        "literature_context": literature_context.strip() or "Not provided.",
        "workflow_steps_json": workflow_steps,
    }
    prompt_2_text = f"{prompt_text}\n\n{design_strategy_planning_prompt_2}"
    response_2 = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer and workflow strategist."},
            {"role": "user", "content": f"{prompt_2_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload_2, ensure_ascii=True)}"},
        ],
    )
    response_2_text = (response_2.choices[0].message.content or "").strip()
    if not response_2_text:
        raise RuntimeError("LLM returned an empty design strategy writeup for prompt part 2.")

    result = {
        "prompt_1_text": prompt_1_text,
        "prompt_1_output_raw": response_1_text,
        "workflow_steps_json": workflow_steps,
        "prompt_2_text": prompt_2_text,
        "prompt_2_output_text": response_2_text,
        "strategy_writeup": response_2_text,
    }
    if bool(user_inputs.get("display_llm_output", True)):
        display_llm_output_bundle(
            exchanges=[
                {
                    "title": "Design Strategy LLM Call (Prompt 2 Writeup)",
                    "prompt_text": prompt_2_text,
                    "response_text": "(Full strategy shown below in compact view.)",
                }
            ],
            compact_markdown_blocks=[
                {
                    "heading": "Human-Readable Strategy (Prompt 2)",
                    "text": response_2_text,
                    "max_height": str(user_inputs.get("display_max_height", "640px")),
                }
            ],
        )
        try:
            from IPython.display import Markdown, display
        except Exception:
            pass
        else:
            workflow_steps_df = workflow_steps_to_dataframe(workflow_steps)
            display(Markdown("### Structured Workflow Plan (Prompt 1 JSON as table)"))
            if workflow_steps_df.empty:
                print("No workflow steps returned from prompt 1.")
            else:
                display(workflow_steps_df[["step_index", "step_name", "tools", "description", "python_code_preview"]])
    return result


def save_design_strategy_workflow_steps(
    workflow_steps_json: List[Dict[str, Any]],
    processed_dir: Path,
) -> Path:
    out_path = processed_dir / "design_strategy_planning_workflow_steps.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(workflow_steps_json, indent=2, ensure_ascii=True), encoding="utf-8")
    return out_path


def reflect_and_regenerate_design_strategy_plan(
    user_inputs: Dict[str, Any],
    original_prompt_1_output: List[Dict[str, Any]],
    original_prompt_2_output: str,
    *,
    literature_context: str = "",
    user_feedback: str = "",
    critique_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reflect and regenerate both Prompt-1 workflow JSON and Prompt-2 writeup.

    Args:
        user_inputs: Planning input dictionary.
        original_prompt_1_output: Existing Prompt-1 workflow JSON.
        original_prompt_2_output: Existing Prompt-2 strategy writeup.
        literature_context: Optional supporting context text.
        user_feedback: Optional user critique/instructions.
        critique_prompt: Optional override for Prompt-2 reflection template.

    Returns:
        Dictionary containing improved Prompt-1 JSON and Prompt-2 writeup.
    """
    model = str(user_inputs.get("llm_model", "gpt-5.2"))
    temperature = float(user_inputs.get("llm_temperature", 0.2))
    prompt_text_base = build_design_strategy_prompt(user_inputs)
    client = get_openai_client(
        missing_package_message="The `openai` package is required for design-strategy reflection.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running design-strategy reflection.",
    )

    # Part 1: regenerate structured workflow JSON
    payload_1 = {
        "original_prompt_1_workflow_json": original_prompt_1_output or [],
        "original_prompt_2_writeup": str(original_prompt_2_output or "").strip(),
        "user_inputs_json": user_inputs,
        "literature_context": literature_context.strip() or "Not provided.",
        "user_feedback": user_feedback.strip() or "",
    }
    prompt_1_text = f"{prompt_text_base}\n\n{design_strategy_reflection_prompt_1}"
    response_1 = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer and workflow strategist."},
            {"role": "user", "content": f"{prompt_1_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload_1, ensure_ascii=True)}"},
        ],
    )
    response_1_text = (response_1.choices[0].message.content or "").strip()
    workflow_steps = _extract_json_array(response_1_text)
    if not workflow_steps:
        raise RuntimeError("LLM returned invalid/empty workflow JSON for reflection prompt part 1.")

    # Part 2: regenerate concise writeup aligned with improved workflow JSON
    prompt_2_template = critique_prompt or design_strategy_reflection_prompt_2
    prompt_2_text = f"{prompt_text_base}\n\n{prompt_2_template}"
    payload_2 = {
        "improved_prompt_1_workflow_json": workflow_steps,
        "original_prompt_2_writeup": str(original_prompt_2_output or "").strip(),
        "user_inputs_json": user_inputs,
        "literature_context": literature_context.strip() or "Not provided.",
        "user_feedback": user_feedback.strip() or "",
    }
    response_2 = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational protein engineer and workflow strategist."},
            {"role": "user", "content": f"{prompt_2_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload_2, ensure_ascii=True)}"},
        ],
    )
    output = (response_2.choices[0].message.content or "").strip()
    if not output:
        raise RuntimeError("LLM returned an empty writeup for reflection prompt part 2.")

    result = {
        "prompt_1_text": prompt_1_text,
        "prompt_1_output_raw": response_1_text,
        "workflow_steps_json": workflow_steps,
        "prompt_2_text": prompt_2_text,
        "prompt_2_output_text": output,
        "strategy_writeup": output,
    }
    critique_revision_summary = ""
    try:
        summary_prompt = (
            "Summarize the critique and revisions between original and improved planning artifacts.\n"
            "Return 5-6 concise bullet points only.\n"
            "Focus on what was changed and why."
        )
        summary_payload = {
            "original_prompt_1_workflow_json": original_prompt_1_output or [],
            "original_prompt_2_writeup": str(original_prompt_2_output or "").strip(),
            "improved_prompt_1_workflow_json": workflow_steps,
            "improved_prompt_2_writeup": output,
            "user_feedback": user_feedback.strip() or "",
        }
        summary_resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "You are a precise technical editor."},
                {"role": "user", "content": f"{summary_prompt}\n\nINPUT_DATA_JSON:\n{json.dumps(summary_payload, ensure_ascii=True)}"},
            ],
        )
        critique_revision_summary = (summary_resp.choices[0].message.content or "").strip()
    except Exception:
        critique_revision_summary = ""

    if bool(user_inputs.get("display_llm_output", True)):
        if critique_revision_summary:
            print("Critique and revisions summary:")
            print(critique_revision_summary)
        display_llm_output_bundle(
            exchanges=[
                {
                    "title": "Design Strategy Reflection / Rewrite",
                    "prompt_text": prompt_2_text,
                    "response_text": "(Refined strategy shown below in compact view.)",
                }
            ],
            compact_markdown_blocks=[
                {
                    "heading": "Refined Strategy (After Reflection)",
                    "text": output,
                    "max_height": str(user_inputs.get("display_max_height", "640px")),
                }
            ],
        )
        try:
            from IPython.display import Markdown, display
        except Exception:
            pass
        else:
            workflow_steps_df = workflow_steps_to_dataframe(workflow_steps)
            display(Markdown("### Structured Workflow Plan (Prompt 1 JSON as table)"))
            if workflow_steps_df.empty:
                print("No workflow steps returned from reflection prompt 1.")
            else:
                display(workflow_steps_df[["step_index", "step_name", "tools", "description", "python_code_preview"]])
    result["critique_revision_summary"] = critique_revision_summary
    return result


def save_design_strategy_plan(plan_text: str, processed_dir: Path) -> Path:
    """
    Save strategy plan to processed outputs and mirrored assets path.

    Args:
        plan_text: Plan text to persist.
        processed_dir: Target processed output directory.

    Returns:
        Path to the saved plan markdown file.
    """
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
    workflow_steps_path: Optional[Path] = None,
    workflow_steps_json: Optional[List[Dict[str, Any]]] = None,
    literature_context_thread_key: Optional[str] = None,
) -> str:
    """
    Persist planning prompt/metadata into thread history.

    Args:
        root_key: Logical data root key.
        thread_id: Chat thread identifier.
        user_inputs: Planning inputs used for generation.
        design_plan_path: Saved plan artifact path.
        design_plan_text: Full plan text (summarized in metadata).
        literature_context_thread_key: Optional source context thread key.

    Returns:
        Updated thread timestamp string.
    """
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
            "workflow_steps_path": "" if workflow_steps_path is None else str(workflow_steps_path),
            "workflow_steps_count": 0 if not workflow_steps_json else len(workflow_steps_json),
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
    """
    Execute end-to-end design strategy planning step.

    Args:
        root_key: Logical data root key.
        user_inputs: Planning input dictionary.
        existing_thread_key: Optional existing thread identifier.
        run_llm: Whether to run LLM generation.
        persist: Whether to persist thread metadata/messages.

    Returns:
        Dict containing thread ids, paths, context, and generated outputs.
    """
    data_root, resolved_dirs = setup_data_root(root_key)
    step_processed_dir = get_step_processed_dir(resolved_dirs)
    thread, _ = init_thread(root_key, existing_thread_key)
    thread_id = str(thread["thread_id"])

    literature_context_thread_key = str(user_inputs.get("literature_context_thread_key", "")).strip() or None
    context_result = load_literature_context(literature_context_thread_key)
    literature_context = str(context_result.get("context_text", ""))
    literature_context_bundle = context_result.get("context_bundle")

    design_plan_text = ""
    design_plan_outputs: Optional[Dict[str, Any]] = None
    design_plan_path: Optional[Path] = None
    workflow_steps_path: Optional[Path] = None
    workflow_steps_json: List[Dict[str, Any]] = []
    if run_llm:
        design_plan_outputs = generate_design_strategy_plan(
            user_inputs,
            literature_context=literature_context,
            return_full=True,
        )
        design_plan_text = str(design_plan_outputs.get("strategy_writeup", ""))
        workflow_steps_json = list(design_plan_outputs.get("workflow_steps_json", []))
        design_plan_path = save_design_strategy_plan(design_plan_text, step_processed_dir)
        workflow_steps_path = save_design_strategy_workflow_steps(workflow_steps_json, step_processed_dir)

    updated_at: Optional[str] = None
    if persist and design_plan_path is not None:
        updated_at = persist_thread_update(
            root_key=root_key,
            thread_id=thread_id,
            user_inputs=user_inputs,
            design_plan_path=design_plan_path,
            design_plan_text=design_plan_text,
            workflow_steps_path=workflow_steps_path,
            workflow_steps_json=workflow_steps_json,
            literature_context_thread_key=literature_context_thread_key,
        )

    return {
        "root_key": root_key,
        "thread_id": thread_id,
        "thread_updated_at": updated_at,
        "data_root": data_root,
        "resolved_dirs": resolved_dirs,
        "step_processed_dir": step_processed_dir,
        "literature_context": literature_context,
        "literature_context_bundle": literature_context_bundle,
        "design_plan_text": design_plan_text,
        "design_plan_path": design_plan_path,
        "workflow_steps_json": workflow_steps_json,
        "workflow_steps_path": workflow_steps_path,
        "design_plan_outputs": design_plan_outputs,
    }
