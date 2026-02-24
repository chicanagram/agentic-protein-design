## Overall strategy (5–8 bullets)

- Use a **backbone-focused mutant design** campaign on **CviUPO** to tune **heme access-channel geometry and heme-proximal positioning** that govern aromatic **mono-oxidation selectivity** vs **sequential over-oxidation/peroxidation**.
- Build a **sequence/structure prior** (UPO homolog MSA + conservation + structure model) to (i) **protect catalytic/heme-thiolate machinery**, (ii) prioritize **mutable pocket/channel residues**, and (iii) reduce the risk of expression/activity collapse.
- Run an explicit **binding_pocket_analysis** module to enumerate **pocket + tunnel residues**, then use **multi-substrate docking** (naphthalene, veratryl alcohol; plus probes) to generate **productive-pose geometry metrics** that translate into mutation hypotheses.
- Execute **3 experimental rounds** with increasing data leverage and decreasing library size:  
  **Round 1 targeted set** (single + limited double mutants) → **Round 2 SSM** at empirically validated hotspots → **Round 3 small combinatorial** library guided by a **supervised surrogate** trained on Round 2 screening data.
- Keep experimental burden tractable by using early **PLM zero-shot** + **Pythia stability** filters and by capping Round 1 to ~48 constructs; Round 3 to ~12 constructs.
- Track the key tradeoff explicitly: **peroxygenation vs peroxidation** using **NBD (peroxygenation proxy)** and **ABTS (peroxidase proxy)** plus **product analytics** (e.g., naphthalene → naphthol vs naphthoquinone) to compute **selectivity_mono_over**.
- Include **process co-optimization hooks** (controlled H₂O₂ feed; ±ascorbate) as a defined pivot when radical-chain over-oxidation dominates apparent selectivity (supported by UPO literature).

---

## Design choices and assumptions (short)

- **Design mode (explicit):** **mutants_of_backbone** (CviUPO). Justification: the scaffold is already functional; the objective is **selectivity reprogramming** (orientation + access control) while preserving **activity, stability, H₂O₂ tolerance, and expression compatibility**. De novo generation (BoltzGen/RFdiffusion2) is kept as a *non-primary fallback* only if the backbone proves non-expressing or structurally unreliable.
- **Library strategy (explicit):**
  1) **Targeted mutation set** (Round 1): information-rich singles + a few doubles to probe epistasis.  
  2) **SSM** (Round 2): saturate 6–8 sites chosen from Round 1 winners + pocket ranking.  
  3) **Combinatorial library** (Round 3): 4 sites × top 3 AAs/site (~81 in silico), downselected to ~12 constructs for synthesis.
- Assumes you can provide **CviUPO FASTA locally** and can run a screening stack that yields: expression proxy, NBD activity, ABTS activity, product ratio/selectivity, H₂O₂ tolerance, and a stability readout (Tm/thermal shift).

---

## Step-by-step execution summary

### Step 1 — Ingest inputs, resolve backbone, define objectives
- **Tools/models:** sequence DB search/alignment (optional fetch); local FASTA validation.
- **Inputs:** `INPUT_DATA_JSON.json`, `data/CviUPO.fasta` (or `data/seed.fasta`).
- **Outputs:**  
  - `artifacts/seed.fasta`, `artifacts/seed.sequence.txt`  
  - `artifacts/config.normalized.json` (objectives + assay readouts placeholders)
- **Gate / failure mode:** if FASTA not found/invalid → provide `data/CviUPO.fasta` and rerun.

### Step 2 — Homolog retrieval, MSA, conservation, and motif safety mask
- **Tools/models:** sequence database search + alignment; conservation analysis.
- **Inputs:** `artifacts/seed.fasta`
- **Outputs:**  
  - `artifacts/upo_msa.a3m`, `artifacts/conservation.csv`  
  - `artifacts/mutable_positions_initial.csv` (non-protected, moderately conserved positions)  
  - `artifacts/upo_hits.json` (traceability)
- **Implementation note:** the workflow encodes a **protected-position mask** (high conservation) to avoid mutating core catalytic machinery; refine later with curated UPO motifs if available.
- **Fallback:** if <100 homologs → relax thresholds / switch db (UniRef50) per step logic.

### Step 3 — Structure prediction, heme annotation, and binding_pocket_analysis
- **Tools/models:** Boltz-2 structure prediction; conservation merge; **binding_pocket_analysis** module.
- **Inputs:** `artifacts/seed.fasta`, `artifacts/conservation.csv`
- **Outputs:**  
  - `artifacts/cviupo_model.pdb`, `artifacts/structure_metrics.json`  
  - `artifacts/active_site_annotation.json` (heme + key residues)  
  - `artifacts/pocket_map.json`, `artifacts/pocket_positions_ranked.csv`
- **Gate:** if model confidence low (e.g., pLDDT_mean < 70) → restrict mutations to high-confidence regions and emphasize conservation-safe sites; optionally generate an alternative model (same step, different settings) before proceeding.
- **Fallback:** if heme annotation fails/missing heme naming → fix heme placement/naming before docking (do not proceed with docking on a heme-less model).

### Step 4 — Multi-substrate docking and productive-pose geometry metrics
- **Tools/models:** Boltz-2 docking/pose assessment.
- **Inputs:** `artifacts/cviupo_model.pdb`, `artifacts/active_site_annotation.json`
- **Outputs:**  
  - `artifacts/docking_pose_table.csv`, `artifacts/docking_pose_summary.csv`  
  - `artifacts/docking_warning.txt` if key aromatics have zero productive poses
- **Decision use:** identify which channel/pocket residues likely control (i) aromatic approach distance/angle to the oxo, (ii) binding modes that enable **sequential oxidation**.
- **Fallback/pivot:** if no productive poses for naphthalene/veratryl alcohol → broaden hypotheses toward channel entrance opening and/or rely more heavily on Round 1 empirical mapping; also consider process levers (controlled H₂O₂ feed) during screening to reduce confounding overoxidation.

### Step 5 — Round 1 targeted mutation set (single + limited double mutants), scoring, selection
- **Library type:** **targeted_mutation_set**
- **Planned size:** score ~96 in silico → **select ~48** for synthesis/testing (with a warning gate if <24 pass filters).
- **Tools/models:** PLM zero-shot scoring; Pythia stability; quick docking proxy.
- **Inputs:** `artifacts/pocket_positions_ranked.csv`, `artifacts/seed.sequence.txt`, `artifacts/cviupo_model.pdb`
- **Outputs:**  
  - `artifacts/round1_all_scored.csv` (full table)  
  - `artifacts/round1_targeted_variants.csv` (selected set)  
  - `artifacts/round1_gate_warning.txt` if selection collapses
- **Selection logic (encoded):** prioritize variants with improved productive-pose proxies across aromatics, while filtering for stability/expression plausibility (Pythia ddG, PLM delta).
- **Fallback:** if too few pass → relax thresholds (e.g., ddG<3.0), expand candidate positions beyond top 18, or switch to a smarter reduced alphabet at fewer sites.

### Step 6 — Round 1 results ingestion, parent selection, and Round 2 SSM site plan
- **Library type:** **SSM** (site-saturation mutagenesis)
- **Planned size:** **6–8 sites**; practical screening size depends on codon scheme (NNK vs smart alphabets). Start with NNK in the plan, but be ready to reduce degeneracy if burden is high.
- **Tools/models:** conservation context; PLM/Pythia available for optional prefiltering of SSM amino-acid sets.
- **Inputs:**  
  - `artifacts/round1_targeted_variants.csv`  
  - Wet-lab filled: `artifacts/round1_experimental_results.csv`
- **Outputs:**  
  - `artifacts/round2_selected_parents.json` (top ~4 parents)  
  - `artifacts/round2_ssm_sites.csv` (sites + codon plan)  
  - `artifacts/round2_pivot_note.txt` if selectivity gains are weak
- **Gate:** if best `selectivity_mono_over` < ~1.5× after Round 1 → pivot Round 2 toward **P:p ratio control hotspots** (alignment-mapped equivalents of known loop positions) and enforce controlled H₂O₂ dosing during screens to decouple intrinsic selectivity from peroxide-driven artifacts.

### Step 7 — Round 2 results → surrogate training → Round 3 small combinatorial design + ddG_bind sanity check
- **Library type:** **combinatorial_library** (small, model-guided)
- **Planned size:** generate **~81** combinations in silico (4 sites × 3 AAs) → filter → **simulate top ~24** with ddG_bind if available → **select ~12** constructs for synthesis/testing.
- **Tools/models:** supervised surrogate (PLM/OHE embeddings); PLM zero-shot optional; Pythia stability; OpenMM/YASARA ddG_bind (optional sanity check).
- **Inputs:**  
  - Wet-lab filled: `artifacts/round2_ssm_results.csv`  
  - `artifacts/seed.fasta`, `artifacts/seed.sequence.txt`, `artifacts/cviupo_model.pdb`
- **Outputs:**  
  - `artifacts/round3_combinatorial_ranked_top200.csv`  
  - `artifacts/round3_combinatorial_selected.csv` (final ~12)  
  - `artifacts/round3_ddgbind_fallback.txt` if ddG_bind fails/unavailable
- **Fallback:** if ddG_bind is unstable or too sparse → select by surrogate acquisition + stability filters only (explicitly encoded).

### Step 8 — Cross-round decision gates, reporting, and failure-mode pivots
- **Tools/models:** conservation analysis (contextual); reporting logic.
- **Inputs:** `artifacts/round1_experimental_results.csv` and/or `artifacts/round2_ssm_results.csv` (if present)
- **Outputs:** `artifacts/decision_gates_report.json` with:
  - Gate summaries (coverage, best selectivity, best H₂O₂ tolerance)
  - Pivot triggers (low coverage, no selectivity, few hits)
  - Recommended next actions (UPO-specific process levers)
- **Core progression criteria (edit to match assay scaling):**
  - **After Round 1:** proceed if ≥1 variant reaches ~**1.5×** selectivity with acceptable activity and H₂O₂ tolerance; otherwise pivot to P:p hotspots + process controls.
  - **After Round 2:** proceed if multiple hits reach **≥2×** selectivity and improved tolerance; otherwise refine sites and reduce degeneracy (smart alphabets), add second-shell/channel-entrance residues.
  - **After Round 3:** target **≥3×** selectivity with stability floor (e.g., Tm ≥45 °C) and no catastrophic activity loss.

---

## Decision gates and immediate next actions (short)

- **Immediate next actions to execute Step 1–4 cleanly:**
  1) Provide `data/CviUPO.fasta` (exact sequence used experimentally).  
  2) Confirm **expression host** and secretion format (important for interpreting “expression proxy” and for library feasibility).  
  3) Define how **selectivity_mono_over** is computed for naphthalene/veratryl alcohol (HPLC/GC product ratio; include overoxidation products like naphthoquinone).
- **Operational controls to run alongside all rounds (high leverage for UPOs):**
  - Screen under **controlled H₂O₂ feed** (avoid bolus) to reduce inactivation and radical-chain artifacts.
  - Screen **±ascorbate (or another radical scavenger)** to distinguish intrinsically less-peroxidative variants from process-suppressed outcomes.
  - Track **NBD vs ABTS** concurrently to quantify the **peroxygenation/peroxidation balance** while maintaining catalytic activity and stability constraints.