from __future__ import annotations

import json
from typing import Any, Dict, Optional

from agentic_protein_design.core.pipeline_utils import get_openai_client


def critique_and_regenerate_text(
    *,
    original_text: str,
    critique_prompt: str,
    user_feedback: str = "",
    model: str = "gpt-5.2",
    temperature: float = 0.2,
    system_message: str = "You are a rigorous technical reviewer and rewrite assistant.",
    additional_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Ask an LLM to critique an existing output and regenerate an improved rewrite.
    The returned text should be the rewritten artifact only.
    """
    payload = {
        "original_text": original_text,
        "user_feedback": user_feedback.strip() or "No explicit user feedback provided.",
        "additional_context": additional_context or {},
    }

    client = get_openai_client(
        missing_package_message="The `openai` package is required for reflection/critique.",
        missing_key_message="OPENAI_API_KEY is not set. Export it before running reflection/critique.",
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": f"{critique_prompt}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}",
            },
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty response for reflection/critique.")
    return text

