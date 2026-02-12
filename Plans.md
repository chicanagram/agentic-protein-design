# Agentic Protein Design - Project Plan

## 1. Purpose and Scope

### Objective
Build a practical agentic workflow for the **initial stage of protein engineering**: selecting promising **wildtype enzyme candidates** for downstream work.

The system is intentionally focused on discovery and prioritization, not later-stage iterative mutagenesis.

### In Scope (MVP)
- Enzyme-class-oriented exploration and candidate selection.
- End-to-end workflow orchestration with transparent intermediate outputs.
- Human-interpretable analysis combining computational outputs and LLM synthesis.
- Local-first execution and storage for rapid prototyping.

### Out of Scope (for MVP)
- Automated mutagenesis campaign optimization loops.
- Wet-lab orchestration/LIMS integration.
- Multi-user auth and enterprise deployment concerns.

## 2. Workflow Requirements

The workflow should support the following capabilities as first-class modules:

1. Literature search and summary
- Gather and summarize knowledge on enzyme class structure, function, reaction mechanism, substrate scope, cofactors, and known engineering constraints.

2. Homolog search
- Start from enzyme class keywords and/or a seed sequence.
- Query external APIs or local tools (provider to be finalized).

3. Structure prediction
- Predict structures for candidates in apo state (without ligand).
- Predict or model structures/complexes with ligand when feasible.

4. Alignment
- Sequence alignment across candidate set.
- Optional structure-aware alignment step when structural models are available.

5. Property extraction and calculation
- Compute features from sequence/alignment/structure (e.g., conservation, active-site context, pocket descriptors, basic stability proxies).
- Implement as Python-coded tools for flexibility.

6. Optional experimental/simulation data integration
- Accept user-provided screening data across reactions.
- Accept simulation outputs (example: MM/GBSA `ddG_bind`) and merge into candidate scoring.

7. LLM-assisted interpretation
- Convert extracted signals into human-readable structural analysis.
- Highlight ligand interaction hypotheses, key residues, and engineering-relevant insights.

## 3. Product Requirements

### Core User Stories
1. As a user, I can define an enzyme class (or provide a seed sequence) and start a discovery run.
2. As a user, I can inspect literature-backed context before trusting model outputs.
3. As a user, I can view homologs, alignments, structures, and computed properties in one place.
4. As a user, I can include optional experimental/simulation evidence when available.
5. As a user, I can get an interpretable rationale for why top wildtype candidates are prioritized.

### Non-Functional Requirements
- Reproducible runs via config snapshots and deterministic seeds where possible.
- Full traceability of prompts, tool calls, and derived tables.
- Clear module boundaries so tools can be swapped without UI rewrite.
- Local-first operation with simple file-based persistence.

## 4. Architecture

### MVP Architecture (Prototype)
- **UI**: Jupyter notebook workflow (`notebooks/`) as the primary interface.
- **Orchestration**: Python pipeline modules invoked from notebook cells.
- **Tools Layer**: Pluggable adapters for search, homolog retrieval, structure prediction, alignment, feature extraction, and reporting.
- **Storage**: Locally stored CSV files for tables + local folders for artifacts.

### Proposed Upgrade Path (Interactive App)
After notebook validation, provide a user-facing app:
- **Recommended first polished UI**: Streamlit
  - Fastest migration from notebook logic.
  - Native handling for tables, charts, file uploads, and iterative workflows.
- **Alternative**: FastAPI + React
  - Better long-term flexibility and multi-user support.
  - Higher initial implementation overhead.

Recommendation: start with Streamlit for speed, then graduate to FastAPI + React if usage grows.

## 5. System Modules

### Module A: Knowledge Retrieval
- Inputs: enzyme class terms, optional reaction descriptors.
- Outputs: literature corpus, extracted facts, concise summary.

### Module B: Candidate Discovery (Homolog Search)
- Inputs: enzyme class and/or seed sequence.
- Outputs: candidate sequence table with metadata (source, identity, annotations).

### Module C: Structural Modeling
- Inputs: selected candidate sequences + optional ligand definition.
- Outputs: apo structures, ligand-bound models (if available), quality metrics.

### Module D: Alignment and Comparative Context
- Inputs: candidate sequences/structures.
- Outputs: alignments, conservation maps, motif/region annotations.

### Module E: Property Engine
- Inputs: sequence/alignment/structure (+ optional external scores).
- Outputs: feature matrix for ranking and interpretation.

### Module F: Interpretation and Prioritization
- Inputs: feature matrix + literature context + optional experimental/simulation data.
- Outputs: ranked wildtype candidates, explanation report, engineering ideas.

## 6. Data Contracts and Storage (CSV-First)

### Directory Layout (Address-Driven)
- Data roots are selected from `address_dict` in `variables.py` (modifiable by dataset/project context).
- Within each selected root, subdirectories are defined via `subfolders` in `variables.py`.
- Standard subdirectories include at least:
  - `sequences/`
  - `msa/`
  - `pdb/`
  - `sce/` (YASARA scene files)
  - `expdata/`
  - `processed/`
- Additional domain-specific subfolders (for example `blast/`, `hmm/`, `seqsearch/`) are also resolved through `subfolders`.

### Path Resolution Rule
- Notebook and pipeline code should resolve paths as:
  - `data_root = Path(address_dict[root_key])`
  - `target_dir = data_root / subfolders[subfolder_key]`
- Avoid hardcoded absolute paths in workflow code.

### Core CSV Tables
- `literature_summary.csv`
- `homolog_candidates.csv`
- `alignment_features.csv`
- `structure_metrics.csv`
- `external_assay_or_simulation.csv` (optional)
- `candidate_scores.csv`
- `candidate_explanations.csv`

### Reproducibility Files
- `run_config.yaml` for parameters and tool settings.
- `run_manifest.csv` for artifact and table lineage.

### Chat Context Persistence
- Store notebook chat context under the repository-local `chats/` folder.
- Use one file per thread + process tag: `chats/<llm_process_tag>_<thread_id>.json`.
- Thread selection should be explicit in each notebook run so users can continue prior context across notebooks.

## 7. UI Plan

### Phase 1: Jupyter Notebook UI
- Notebook sections mirror workflow modules A-F.
- Start with two prototype notebooks:
  - `notebooks/01_literature_review.ipynb`
  - `notebooks/02_binding_pocket_analysis.ipynb`
- Each section emits clearly named CSV outputs and preview tables.
- Include “decision checkpoints” for user review before next stage.

### Phase 2: Streamlit App
- Guided workflow pages:
  - Setup (enzyme class / seed sequence)
  - Retrieval and homologs
  - Structures and alignments
  - Property analysis
  - Ranked candidates + rationale
- Upload controls for optional assay/simulation data.
- Download bundle for CSV outputs and report artifacts.

## 8. Evaluation and Quality

### Quality Metrics
- Coverage and relevance of literature summary.
- Candidate diversity and annotation completeness.
- Alignment/structure feature completeness.
- Ranking stability across reruns/config changes.
- Practical usefulness of LLM-generated interpretations.

### Testing Strategy
- Unit tests for each module’s input/output schema.
- Integration test for complete pipeline run on a small benchmark case.
- Regression tests for ranking output with fixed test fixtures.

## 9. Delivery Roadmap

### Phase 0: Bootstrap (Week 1)
- Create project structure and baseline notebook.
- Define CSV schemas and run manifest format.
- Implement skeleton modules with mock outputs.

### Phase 1: Core Discovery Pipeline (Weeks 2-3)
- Implement literature + homolog + alignment flow.
- Add initial property extraction tools.
- Produce first ranked wildtype candidate list.

### Phase 2: Structure + Optional Data Fusion (Weeks 4-5)
- Add apo/ligand structure modeling hooks.
- Integrate optional assay/simulation CSV ingestion.
- Improve scoring and interpretation layer.

### Phase 3: Polished UI (Weeks 6-7)
- Port notebook flow into Streamlit.
- Add upload/download UX and run summaries.
- Add validation and error handling hardening.

## 10. Risks and Mitigations

### Risk: External tool/API variability
- Mitigation: adapter interfaces + cached raw inputs + graceful fallback behavior.

### Risk: Inconsistent data formats from heterogeneous sources
- Mitigation: strict normalization step and schema validation before merge.

### Risk: Overconfident interpretation text
- Mitigation: force citation of evidence rows/features in explanation output.

### Risk: Scope creep into downstream engineering loops
- Mitigation: explicit boundary: wildtype candidate selection only in this project phase.

## 11. Immediate Next Actions

1. Create module folders and a notebook scaffold aligned to modules A-F.
2. Define canonical CSV schemas and validation utilities.
3. Implement literature and homolog modules first (highest leverage).
4. Add alignment + baseline feature extraction.
5. Generate first end-to-end report for one enzyme class pilot.
