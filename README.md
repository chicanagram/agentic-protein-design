# Agentic Protein Design

![Agentic Protein Design Landing Graphic](assets/landing-page.png)

A notebook-first, local-first workflow for **early-stage enzyme engineering** focused on **wildtype candidate selection** (not iterative mutagenesis).

## Project Scope

This project is designed to support the discovery and analysis phase of protein engineering by combining:
- literature and database retrieval
- homolog and structure context
- pocket/alignment feature analysis
- LLM-based interpretation for human-readable, engineering-relevant insights

See full architecture and roadmap in [Plans.md](Plans.md).

## Current Workflow Architecture

- **Primary UI (current)**: Jupyter notebooks in [`notebooks/`](notebooks)
- **Helper modules**: reusable functions in [`notebook_helpers/`](notebook_helpers)
- **Config-driven data roots**: via `address_dict` and `subfolders` in [`variables.py`](variables.py)
- **Local chat memory**: per-thread JSON files under `chats/` (git-ignored)
- **Outputs**: written to each selected data root's standard subfolders (especially `processed/`)

## Available Notebooks (more to come)

- [`notebooks/01_literature_review.ipynb`](notebooks/01_literature_review.ipynb)  
  Retrieval-backed literature survey and protein database scan, followed by LLM-generated, engineering-focused synthesis.  
  Includes source diagnostics, quality scoring/downweighting, and compact thread-memory persistence.

- [`notebooks/02_binding_pocket_analysis.ipynb`](notebooks/02_binding_pocket_analysis.ipynb)  
  Binding-pocket comparative analysis from pocket descriptors + filtered alignment (+ optional reaction data), with LLM-generated mechanistic interpretation and compact thread-memory persistence.

## Environment Setup

You can run with either conda or pip:

- Conda:
  - `conda env create -f environment.yml`
  - `conda activate agentic-protein-design`

- Pip:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`

## API Keys

For notebook LLM calls, set your key in [`local_api_keys.py`](local_api_keys.py).  
This file is git-ignored.

## Notes

- Place the provided landing image at `assets/landing-page.png` so it renders on GitHub.
- Generated outputs in `processed/` and chat history in `chats/` are excluded from version control.
