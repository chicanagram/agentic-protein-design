# Agentic Protein Design

![Agentic Protein Design Landing Graphic](assets/landing-page.png)

A notebook-first, local-first workflow for **early-stage enzyme engineering** focused on **enzyme candidate analysis** and **initial selection of engineering targets**.

Latest LLM-generated outputs are mirrored as Markdown files in [`assets/`](assets) for quick repo/GitHub viewing (updated on each run).

## Project Scope

This project is designed to support the discovery and analysis phase of protein engineering by combining:
- literature and database retrieval
- homolog and structure context
- pocket/alignment feature analysis
- LLM-based interpretation for human-readable, engineering-relevant insights

See full architecture and roadmap in [Plans.md](Plans.md).

## Current Workflow Architecture

- **Primary UI (current)**: Jupyter notebooks in [`notebooks/`](notebooks)
- **Reusable package layer**: importable step/workflow modules in [`src/agentic_protein_design/`](src/agentic_protein_design)
- **Tool integration layer**: local-binary/API wrappers and scripts in [`tools/`](tools)
- **Legacy helper modules**: removed; import directly from [`src/agentic_protein_design/`](src/agentic_protein_design)
- **Config-driven data roots**: via `address_dict` and `subfolders` in [`project_config/variables.py`](project_config/variables.py)
- **Local chat memory**: per-thread JSON files under `chats/` (git-ignored)
- **Outputs**: written to each selected data root's standard subfolders (especially `processed/`)

## Available Notebooks

- [`notebooks/00_literature_review.ipynb`](notebooks/00_literature_review.ipynb)  
  Retrieval-backed literature survey and protein database scan, followed by LLM-generated, engineering-focused synthesis.  
  Includes source diagnostics, quality scoring/downweighting, and compact thread-memory persistence.

- [`notebooks/01_design_strategy_planning.ipynb`](notebooks/01_design_strategy_planning.ipynb)  
  Strategy-planning notebook that uses project requirements plus optional prior literature-review thread context to produce a multi-round design workflow with tool choices, decision gates, and implementation details.

- [`notebooks/02_run_denovo_sequence_design.ipynb`](notebooks/02_run_denovo_sequence_design.ipynb)
  (Placeholder - implementation pending). Workflow to run de novo sequence design.

- [`notebooks/03_run_zero_shot_mutant_design.ipynb`](notebooks/03_run_zero_shot_mutant_design.ipynb)  
  (Placeholder - implementation pending). Workflow to design zero-shot mutant sequences in Round 1.

- [`notebooks/04_run_next_round_mutant_design.ipynb`](notebooks/04_run_next_round_mutant_design.ipynb)
  (Placeholder - implementation pending). Workflow to design sequences in Round 2 onwards, after some screening data is available.

- [`notebooks/05_get_sequences_align_and_analyse_conservation.ipynb`](notebooks/05_get_sequences_align_and_analyse_conservation.ipynb)  
  (Placeholder - implementation pending). Retrieve homologs, obtain multiple sequence alignment, perform conservation analysis for seed sequence positions. 

- [`notebooks/06_get_structures_apo_holo.ipynb`](notebooks/06_get_structures_apo_holo.ipynb)  
  (Placeholder - implementation pending). Fetch available crystal structures or predict structures and obtain docked complexes using AI models. 

- [`notebooks/07_get_sequence_structure_physicochemical_properties.ipynb`](notebooks/07_get_sequence_structure_physicochemical_properties.ipynb)
  (Placeholder - implementation pending). Extract sequence-, structure-, and physicochemical-property features.

- [`notebooks/08_get_binding_pocket_properties.ipynb`](notebooks/08_get_binding_pocket_properties.ipynb)
  (Placeholder - implementation pending). Compute and aggregate binding-pocket descriptors.

- [`notebooks/09_binding_pocket_analysis.ipynb`](notebooks/09_binding_pocket_analysis.ipynb)  
  Binding-pocket comparative analysis from pocket descriptors + filtered alignment (+ optional reaction data), with LLM-generated mechanistic interpretation and compact thread-memory persistence.

- [`notebooks/10_run_MD_calculate_dGbind.ipynb`](notebooks/10_run_MD_calculate_dGbind.ipynb)  
  (Placeholder - implementation pending). Run molecular dynamics simulation to calculate dG_bind for protein ligand complex.

- [`notebooks/11_run_minimization_calculate_ddGbind_mutants.ipynb`](notebooks/11_run_minimization_calculate_ddGbind_mutants.ipynb)  
  (Placeholder - implementation pending). Run energy minimization simulation to calculate ddG_bind for mutations of a protein ligand complex.

- [`notebooks/12_calculate_ddGstability_mutants.ipynb`](notebooks/12_calculate_ddGstability_mutants.ipynb)  
  Stability-ddG prediction notebook using **Pythia** via an isolated Python environment.

- [`notebooks/13_obtain_ML_features_compose_datasets.ipynb`](notebooks/13_obtain_ML_features_compose_datasets.ipynb)  
  (Placeholder - implementation pending). Compose feature matrices and training/evaluation datasets for supervised ML.

- [`notebooks/14_train_evaluate_supervised_ML_models.ipynb`](notebooks/14_train_evaluate_supervised_ML_models.ipynb)  
  (Placeholder - implementation pending). Train supervised ML models with screening labels (Y), and selected input feature sets (X). 

- [`notebooks/15_run_sequence_patent_search.ipynb`](notebooks/15_run_sequence_patent_search.ipynb)  
  (Placeholder - implementation pending). Run patent search and analysis for sequences of interest. 

## Programmatic Reuse (for larger workflows)

In addition to notebook cells, you can now import step/workflow functions from:
- [`src/agentic_protein_design/steps/literature_review.py`](src/agentic_protein_design/steps/literature_review.py)
- [`src/agentic_protein_design/steps/design_strategy_planning.py`](src/agentic_protein_design/steps/design_strategy_planning.py)
- [`src/agentic_protein_design/steps/binding_pocket.py`](src/agentic_protein_design/steps/binding_pocket.py)
- [`src/agentic_protein_design/workflows/multistep.py`](src/agentic_protein_design/workflows/multistep.py)

This enables a "master notebook" to run individual steps or a composed multi-step workflow with shared inputs.

## Environment Setup

You can run with either conda or pip:

- Conda:
  - `conda env create -f environment.yml`
  - `conda activate agentic-protein-design`

- Pip:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`

## Running Stability Notebook (Pythia)

Notebook: [`notebooks/12_calculate_ddGstability_mutants.ipynb`](notebooks/12_calculate_ddGstability_mutants.ipynb)

1. Set up a dedicated Pythia environment first (recommended to avoid OpenMP conflicts):
   - `conda create -n pythia python=3.10 -y`
   - `conda run -n pythia python -m pip install -r tools/pythia/requirements.txt`

2. In notebook 12 user inputs, point Pythia to that isolated interpreter:
   - `user_inputs["pythia_python_executable"] = "/Users/charmainechia/miniconda3/envs/pythia/bin/python"`
   - `user_inputs["isolate_pythia_process_env"] = True`
   - keep `user_inputs["n_jobs"] = 1` for runtime portability

3. Provide input paths via:
   - `base_directory_key` (preferred, from `project_config/variables.py` `address_dict`)
   - `data_subfolder` (optional, can be `""`/`None`)
   - `sequence_subdirectory`, `structure_subdirectory`
   - `sequence_fasta_filenames`, `structure_pdb_filenames`

4. Run notebook cells. If `output_csv` is blank, output defaults to:
   - `processed/12_calculate_ddGstability_mutants/{data_subfolder}/pythia_ddg_stability_predictions.csv`

## API Keys

For notebook LLM calls, set your key in [`project_config/local_api_keys.py`](project_config/local_api_keys.py).  
This file is git-ignored.

## Notes

- Place the provided landing image at `assets/landing-page.png` so it renders on GitHub.
- Generated outputs in `processed/` and chat history in `chats/` are excluded from version control.
