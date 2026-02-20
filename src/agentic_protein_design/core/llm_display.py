from __future__ import annotations

from typing import Any, Dict, List, Optional


def apply_notebook_markdown_style(font_size_px: int = 14, line_height: float = 1.4) -> None:
    """
    Apply a subtle global markdown style override in notebook outputs.
    """
    try:
        from IPython.display import HTML, display
    except Exception:
        return

    display(
        HTML(
            f"""
<style>
.jp-RenderedMarkdown, .rendered_html {{
  font-size: {int(font_size_px)}px !important;
  line-height: {float(line_height)} !important;
}}
</style>
"""
        )
    )


def show_markdown_compact(md_text: str, max_height: str = "640px") -> None:
    """
    Display markdown text in a scrollable output container for compact notebooks.
    """
    try:
        import ipywidgets as widgets
        from IPython.display import Markdown, display
    except Exception:
        print(md_text)
        return

    out = widgets.Output(
        layout=widgets.Layout(
            border="1px solid #e0e0e0",
            padding="8px",
            max_height=str(max_height),
            overflow="auto",
        )
    )
    with out:
        display(Markdown(md_text))
    display(out)


def show_llm_exchange(
    *,
    title: str,
    prompt_text: str,
    response_text: str,
    prompt_label: str = "Prompt",
    response_label: str = "Response",
    collapse_prompt: bool = True,
) -> None:
    """
    Render a readable LLM prompt/response exchange in notebook output.

    Args:
        title: Section title displayed above the exchange.
        prompt_text: Prompt text sent to the LLM.
        response_text: LLM response text (markdown/plain text).
        prompt_label: Label for prompt section.
        response_label: Label for response section.
        collapse_prompt: If true, prompt is shown in a collapsible details block.

    Returns:
        None. Displays rich notebook output (falls back to print if IPython missing).
    """
    try:
        from IPython.display import Markdown, display
    except Exception:
        print(f"\n=== {title} ===")
        print(f"\n[{prompt_label}]\n{prompt_text}")
        print(f"\n[{response_label}]\n{response_text}")
        return

    display(Markdown(f"### {title}"))
    if collapse_prompt:
        prompt_md = (
            f"<details><summary>{prompt_label}</summary>\n\n"
            f"```text\n{prompt_text}\n```\n"
            f"</details>"
        )
        display(Markdown(prompt_md))
    else:
        display(Markdown(f"#### {prompt_label}"))
        display(Markdown(f"```text\n{prompt_text}\n```"))

    display(Markdown(f"#### {response_label}"))
    display(Markdown(response_text or "_(empty response)_"))


def display_llm_output_bundle(
    *,
    exchanges: Optional[List[Dict[str, Any]]] = None,
    compact_markdown_blocks: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Generalized notebook renderer for one or more LLM exchanges and compact markdown outputs.

    Args:
        exchanges: List of exchange dictionaries. Supported keys:
            - title (required)
            - prompt_text (required)
            - response_text (required)
            - prompt_label (optional)
            - response_label (optional)
            - collapse_prompt (optional)
        compact_markdown_blocks: List of markdown block dictionaries. Supported keys:
            - heading (optional)
            - text (required)
            - max_height (optional, defaults to 640px)
    """
    exchange_items = list(exchanges or [])
    block_items = list(compact_markdown_blocks or [])

    if not exchange_items and not block_items:
        return

    try:
        from IPython.display import Markdown, display
    except Exception:
        for item in exchange_items:
            print(f"{item.get('title', 'LLM Output')}\n{item.get('response_text', '')}\n")
        for item in block_items:
            heading = str(item.get("heading", "")).strip()
            if heading:
                print(heading)
            print(item.get("text", ""))
        return

    for item in exchange_items:
        show_llm_exchange(
            title=str(item.get("title", "LLM Output")),
            prompt_text=str(item.get("prompt_text", "")),
            response_text=str(item.get("response_text", "")),
            prompt_label=str(item.get("prompt_label", "Prompt")),
            response_label=str(item.get("response_label", "Response")),
            collapse_prompt=bool(item.get("collapse_prompt", True)),
        )

    for item in block_items:
        heading = str(item.get("heading", "")).strip()
        if heading:
            display(Markdown(f"### {heading}"))
        show_markdown_compact(
            str(item.get("text", "")),
            max_height=str(item.get("max_height", "640px")),
        )
