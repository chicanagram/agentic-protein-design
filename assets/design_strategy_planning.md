## 1) Overall strategy (5–8 bullets)

- Run a **backbone-focused mutant design** campaign on **CviUPO** to tune **heme access-channel / near-heme positioning residues** that control aromatic binding pose and residence time, thereby improving **mono-oxidation selectivity** and reducing **overoxidation** while maintaining activity and stability.
- Treat the core mechanistic risk explicitly: for aromatics, desired peroxygenation competes with **peroxidative follow-up** (phenol → quinone/polymerization). We will therefore screen and gate on **product profiles at matched conversion**, not just “activity”.
- Build the minimum reliable structural context: **validated CviUPO FASTA → single consistent 3D model → ligand pose ensemble** (Boltz-2) to support pocket/tunnel nomination and computational triage.
- Add evolutionary context early (UPObase/UniRef homologs → MSA → conservation) to (i) protect catalytic motifs and (ii) prioritize **mutable tunnel residues**; but do not block early rounds if MSA is delayed.
- Execute **3 experimental rounds** with increasing complexity and explicit decision gates:  
  **Round 1** targeted single mutants (learning) → **Round 2** SSM at experimentally validated leverage sites (local exploration) → **Round 3** surrogate-guided combinatorial library (epistasis exploitation).
- Use computational filters only to keep libraries tractable (PLM zero-shot plausibility, Pythia stability, Boltz-2 pose assessment; **ddG_bind only as a tie-breaker**), and rely on experimental results to choose Round 2/3 directions.
- Integrate a formal **binding_pocket_analysis** module to output: (a) channel/tunnel sites, (b) stability-shell sites, and (c) “do-not-mutate” exclusion masks.

---

## 2) Design choices and assumptions (short)

- **Design mode (explicit choice):** **Backbone-focused mutant design** on **CviUPO** (not de novo; not hybrid).  
  **Justification:** You already have a functional UPO scaffold; the objective is **selectivity tuning** (mono-oxidation vs overoxidation) under constraints (H₂O₂ tolerance, stability, expression compatibility). These are most feasibly addressed by **channel/pocket reshaping + limited robustness tuning** while preserving the fold and catalytic machinery.
- **Assumptions that become decision gates rather than hidden dependencies:**
  1. You can provide a **real CviUPO FASTA** (mature vs full-length with signal peptide annotated). This is **blocking** for residue-numbered design and docking.
  2. You can measure at least one aromatic substrate’s **mono-product vs overoxidation** (e.g., naphthalene: naphthol vs naphthoquinone) plus proxies for **peroxidase activity** (ABTS) and **peroxygenation** (NBD).
  3. Expression host is fixed for the campaign (or at least consistent across rounds); if expression is the bottleneck, we will pivot to an expression-enabling sub-workstream (see fallbacks).

---

## 3) Step-by-step execution summary

### Step 1 — Ingest seed sequence and project config (workflow step 1)
**Goal:** Create a single source of truth for sequence + config; prevent silent placeholder usage.

- **Tooling:** none (I/O + validation).
- **Inputs:** `user_inputs_json.backbone_fasta` (required to unblock structural steps), project constraints/targets/substrates.
- **Outputs:**  
  - `CviUPO.fasta`  
  - `CviUPO.project_config.json` (normalized)  
  - `CviUPO.ingest_status.json` with explicit **blocking items** if FASTA is missing/invalid.
- **Decision gate:** downstream structural/pocket steps **must not run** unless `has_real_fasta=true`.
- **Fallback:** If only a precursor sequence is available, annotate signal peptide and define the **mature numbering scheme** before any residue-indexed libraries are finalized.

---

### Step 2 — Homolog search, MSA, and conservation map (workflow step 2)
**Goal:** Identify mutable vs conserved positions; protect catalytic motifs and structural core.

- **Tools:** sequence database search & alignment; conservation analysis.
- **Inputs:** `CviUPO.fasta`
- **Outputs:**  
  - `CviUPO.msa.a3m`  
  - `CviUPO.homolog_hits.json`  
  - `CviUPO.conservation.json` (entropy/conservation per position)
- **How it’s used:**  
  - Exclude highly conserved residues from mutation unless strongly justified.  
  - Prioritize variable residues lining the access channel/tunnel.
- **Fallback:** If DB search/MSA is delayed, proceed with structure-only pocket nomination (Step 4) but mark conservation-based exclusions as “pending” and tighten experimental library sizes until conservation is available.

---

### Step 3 — Structure modeling and ligand pose ensemble (workflow step 3)
**Goal:** Produce a consistent 3D model and multiple plausible binding poses for aromatic substrates to reduce docking brittleness.

- **Tools:** Boltz-2 docking/pose assessment (and structure prediction/fetch).
- **Inputs:** `CviUPO.fasta`, `substrates_of_interest` (Veratryl alcohol, Naphthalene, NBD, ABTS, S82).
- **Outputs:**  
  - `CviUPO.model.pdb` (AFDB fetch if available; else Boltz-2 predicted)  
  - `docking/CviUPO.poses.json` (e.g., 5 diverse poses per ligand)
- **Decision gate:** If model quality is poor around the heme pocket/channel (e.g., obvious clashes, missing heme context), do not overfit docking scores; use poses only for **site nomination**, not fine ranking.
- **Fallbacks:**  
  - Use closest homolog structure/model and map residues by alignment.  
  - If docking is unstable for ABTS (large/charged), treat ABTS as an assay-only probe and focus docking on naphthalene/veratryl alcohol/NBD.

---

### Step 4 — binding_pocket_analysis, site nomination, and exclusion masks (workflow step 4)
**Goal:** Convert structure + poses + conservation into explicit mutation site sets and “do-not-mutate” masks.

- **Tools:** conservation analysis (+ binding_pocket_analysis module logic).
- **Inputs:** `CviUPO.model.pdb`, `CviUPO.poses.json`, `CviUPO.conservation.json`
- **Outputs:** `CviUPO.site_selection.json` containing:
  - **active_site_channel_sites** (channel/tunnel/gating residues; includes literature-anchored candidates such as **F88/T158 equivalents**, but requires numbering validation)
  - **stability_shell_sites** (second-shell positions for later rescue if selectivity mutations destabilize)
  - **exclusions.do_not_mutate** masks: heme-thiolate Cys region, distal acid/base, disulfides/glycosylation motifs (unless explicitly engineered)
- **Decision gate:** Residue numbering must be consistent with the FASTA used for expression (mature vs full-length). If not, pause library finalization.
- **Fallback:** If tunnel mapping tools are not available, approximate channel sites as residues within 4–6 Å of ligand poses plus visually identified constrictions; keep Round 1 small and interpret results cautiously.

---

### Step 5 — Round 1 targeted single-mutant library + computational triage (workflow step 5)
**Library strategy:** **targeted_mutation_set** (single mutants), small and interpretable.

- **Hypothesis tested:** Channel reshaping at a few constriction/gate residues shifts aromatic binding pose/residence time → improves **mono-oxidation selectivity** and reduces **overoxidation**.
- **Design:** pick **2–3 channel sites** (from Step 4) and propose “smart” amino-acid menus (steric + mild polarity; avoid strongly charged residues in a hydrophobic tunnel in Round 1).
- **Size:** cap at **~24–48 variants** total.
- **Tools for triage:**  
  - **PLM zero-shot scoring** (sequence plausibility)  
  - **Pythia** (stability ΔΔG proxy)  
  - **Boltz-2 pose assessment** (pose feasibility / steric compatibility)
- **Outputs:** `CviUPO.round1_library.json` with ranked variants + menus + explicit gate criteria.
- **Round 1 decision gate (advance criteria):**
  - **Mono-oxidation selectivity improves vs WT at matched conversion**
  - **Overoxidation ratio decreases** (e.g., naphthol:naphthoquinone improves)
  - **Activity maintained** (≥0.5× WT or project-defined threshold)
  - **No major loss** in expression proxy / stability / H₂O₂ tolerance
- **Fallbacks:**  
  - If many variants lose expression/activity, shift Round 2 to include **stability-shell** single mutants (rescue) before deeper selectivity exploration.  
  - If selectivity readout is too noisy, tighten to fewer variants with replicates and add an orthogonal analytic method (HPLC/GC).

---

### Step 6 — Ingest Round 1 experimental results and choose SSM sites (workflow step 6)
**Goal:** Ensure Round 2 site choice is driven by **measured** improvements, not in silico ranks.

- **Tools:** none (results ingestion + simple analytics).
- **Inputs:** `CviUPO.round1_results.csv` with columns such as: activity, mono_selectivity, overoxidation_ratio, Tm, H₂O₂_tolerance, expression.
- **Outputs:** `CviUPO.round2_site_choice.json` listing **1–2 chosen SSM sites** based on enrichment among top performers.
- **Decision gate:** If no Round 1 variant improves selectivity without unacceptable tradeoffs, do not proceed to SSM; instead redesign Round 1 with alternative channel sites or process-condition changes (see fallbacks below).
- **Fallback:** If improvements are substrate-specific, choose SSM sites separately for the primary substrate (e.g., naphthalene) and keep secondary substrates as counterscreens.

---

### Step 7 — Round 2 SSM library design with stability and binding filters (workflow step 7)
**Library strategy:** **site_saturation_mutagenesis** at **1–2 experimentally validated sites**, but screen a **computationally selected subset**.

- **Design:** full SSM is 19×sites, but select **~12 variants per site** (≈24 total) using:
  - PLM plausibility (avoid unlikely sequences)
  - Pythia stability penalty (avoid strongly destabilizing substitutions)
  - Boltz-2 pose assessment (avoid obvious steric clashes / loss of productive pose)
  - Optional **OpenMM/YASARA ddG_bind** as a **tie-breaker only**
- **Outputs:** `CviUPO.round2_library.json` with selected subset and explicit fallback rules.
- **Round 2 decision gate (advance criteria):**
  - Best-in-round improves **mono_selectivity** and reduces **overoxidation** vs Round 1 best
  - Activity acceptable
  - Stability/H₂O₂ tolerance/expression non-inferior (or explicitly traded with justification)
- **Fallbacks:**  
  - If docking is inconsistent across poses, use **pose-ensemble consensus** (rank by robustness across poses) or drop docking from the composite.  
  - If stability collapses, introduce 1–2 **stability-shell** compensatory mutations (targeted set) before moving to combinations.

---

### Step 8 — Ingest Round 2 results, train surrogate, define Round 3 combinatorial space (workflow step 8)
**Goal:** Convert Round 1–2 data into a bounded combinatorial design space and a learnable model.

- **Tools:** supervised surrogate models with OHE/PLM embeddings.
- **Inputs:** `CviUPO.round2_results.csv` (and Round 1 results if available).
- **Outputs:** `CviUPO.round3_space.json` containing:
  - Up to **3 sites** total for combination
  - Up to **4 mutation options per site** (from measured winners), keeping enumeration bounded
  - Surrogate plan: features (PLM embeddings + one-hot mutation indicators + optional structural features), objectives (activity, selectivity, overoxidation, Tm, H₂O₂ tolerance, expression), constrained multi-objective acquisition
- **Decision gate:** If dataset is too small/too noisy to train a useful surrogate, do not pretend otherwise—use the Round 3 fallback selection strategy (below).

---

### Step 9 — Round 3 surrogate-guided combinatorial library selection under constraints (workflow step 9)
**Library strategy:** **combinatorial_library** to capture epistasis while keeping experimental burden tractable.

- **Design:** enumerate the bounded space (≤4³ = 64 if 3 sites capped at 4 each; could be larger if fewer caps are used) and select **~96 variants max** (or fewer if enumeration is smaller) using:
  - Surrogate-predicted multi-objective performance
  - **Hard constraints** via Pythia stability proxy (e.g., ΔΔG ≤ ~1.5 as a starting filter)
  - PLM plausibility as an additional constraint/regularizer
- **Outputs:** `CviUPO.round3_library.json` with selected variants and success criteria.
- **Round 3 success criteria:**
  - Mono-oxidation selectivity improves vs best Round 2 at matched conversion
  - Overoxidation ratio decreases further
  - Activity acceptable for application context
  - Stability/H₂O₂ tolerance/expression non-inferior (or explicitly acceptable tradeoff)
- **Fallback (if surrogate fails):**
  - Select a **fractional factorial / interaction-mapping panel**: all single-site winners + top additive combinations + a small set designed to test pairwise interactions, then choose final leads from measured Pareto front.

---

## 4) Decision gates and immediate next actions (short)

### Decision gates (applied each round)
- **Primary:** improved **mono-oxidation selectivity** and reduced **overoxidation** at **matched conversion** (avoid “selectivity” artifacts from low turnover).
- **Must-haves:** maintain catalytic activity above threshold; maintain or improve **stability**, **H₂O₂ tolerance**, and **expression compatibility**.
- **Data quality gate:** if assay noise is high, require replicate confirmation before promoting variants or choosing SSM sites.

### Immediate next actions
1. Provide the **true CviUPO FASTA** and specify whether it is **mature enzyme** or includes **signal peptide/propeptide** (this unblocks Steps 3–5 and residue numbering).
2. Confirm the **expression host** and secretion strategy (E. coli vs yeast/Pichia), because “expression host compatibility” is a hard constraint that can dominate outcomes.
3. Choose the **primary selectivity substrate/readout** for gating (recommend **naphthalene product ratio** as the main overoxidation sentinel; keep ABTS/NBD as orthogonal activity probes), and define the matched-conversion protocol (timepoints or controlled H₂O₂ feed).
4. Run Steps 2–4 to lock the **site_selection.json**, then execute **Round 1 (24–48 variants)** for maximum information gain with minimal burden.