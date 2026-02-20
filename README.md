# Agentic Protein Design

![Agentic Protein Design Landing Graphic](assets/landing-page.png)

A notebook-first, local-first workflow for **end-to-end protein engineering** via flexible agent-orchestrated workflows. These can perform multimodal bioinformatic analyses and integrate insights from: literature review and sequence discovery, structure analysis, de novo design, zero-shot sequence refinement with AI models, conservation analysis and other property predictors, supervised ML for directed evolution, binding-energy calculations, and stability-change prediction.

Latest LLM-generated outputs are mirrored as Markdown files in [`assets/`](assets) for quick repo/GitHub viewing (updated on each run).

## Project Scope

This project supports flexible protein-design workflows by combining retrieved scientific knowledge with bioinformatics and modeling tools, so pipelines can be tailored to different design problems and constraints.

Steps executable in the workflow include: 
- Literature review
- Sequence retrieval, alignment, conservation analysis
- Prediction of structural complex and binding pocket analysis 
- De novo structure / sequence design and zero-shot mutant design
- Iterative mutant design via Machine Learning-driven Directed Evolution
- Calculation of binding energies via MD simulations
- Prediction of stability changes

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

- [`notebooks/12_calculate_ddGstability_mutants.ipynb`](notebooks/12_calculate_dGstability_mutants.ipynb)  
  Stability-ddG prediction notebook using **Pythia** via an isolated Python environment.

- [`notebooks/13_obtain_ML_features_compose_datasets.ipynb`](notebooks/13_obtain_sequence_encodings.ipynb)  
  (Placeholder - implementation pending). Compose feature matrices and training/evaluation datasets for supervised ML.

- [`notebooks/14_train_evaluate_supervised_ML_models.ipynb`](notebooks/14_train_evaluate_supervised_ML_models.ipynb)  
  (Placeholder - implementation pending). Train supervised ML models with screening labels (Y), and selected input feature sets (X). 

- [`notebooks/15_run_sequence_patent_search.ipynb`](notebooks/15_run_sequence_patent_search.ipynb)  
  (Placeholder - implementation pending). Run patent search and analysis for sequences of interest. 

In addition to notebook cells, workflow steps can also be run from python scripts found
[`src/agentic_protein_design/steps/`](src/agentic_protein_design/steps/)

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

For notebook LLM calls, set your key in [`project_config/local_api_keys.py`](project_config/local_api_keys.py).  
This file is git-ignored.

# Other Dependencies
## Running Stability Notebook (Pythia)

Notebook: [`notebooks/12_calculate_ddGstability_mutants.ipynb`](notebooks/12_calculate_dGstability_mutants.ipynb)

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


# To-Do

- Populate tools registry after adding more tools
- Improve prompt for workflow planning; return python code to be executed + json workflow description
- Add constraints to BoltzGen specifications

Notebooks to flesh out:
- Sequence retrieval + align
- Simulation-based Energy calculations
- Sequence encodings retrieval
- ML model training and evaluation
- Zero shot and next round workflows
