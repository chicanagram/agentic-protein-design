from __future__ import annotations

from typing import Any, Dict, Optional

from agentic_protein_design.steps.binding_pocket import run_binding_pocket_step
from agentic_protein_design.steps.literature_review import run_literature_review_step


def run_multistep_workflow(
    *,
    root_key: str,
    literature_inputs: Dict[str, Any],
    binding_inputs: Dict[str, Any],
    binding_input_paths: Dict[str, str],
    literature_input_paths: Optional[Dict[str, str]] = None,
    literature_thread_id: Optional[str] = None,
    binding_thread_id: Optional[str] = None,
    run_llm: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Execute literature review and binding-pocket analysis in one callable workflow.
    """
    literature_result = run_literature_review_step(
        root_key=root_key,
        inputs=literature_inputs,
        input_paths=literature_input_paths or {},
        existing_thread_id=literature_thread_id,
        run_llm=run_llm,
        persist=persist,
    )

    binding_result = run_binding_pocket_step(
        root_key=root_key,
        user_inputs=binding_inputs,
        input_paths=binding_input_paths,
        existing_thread_id=binding_thread_id,
        run_llm=run_llm,
        persist=persist,
    )

    return {
        "root_key": root_key,
        "literature": literature_result,
        "binding_pocket": binding_result,
    }
