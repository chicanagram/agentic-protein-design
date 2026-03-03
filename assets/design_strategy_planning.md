## Overall strategy (5–8 bullets)

- Use **backbone-focused mutant design on CviUPO** (primary mode) to tune **access-channel geometry, pocket polarity, and product egress**, which are the dominant levers for **aromatic mono-oxidation selectivity vs overoxidation** in UPOs, while preserving the heme-thiolate catalytic core.
- Run a **dual selectivity screen** each round to explicitly separate desired **peroxygenation (2e⁻ oxygen transfer)** from undesired **peroxidation/1e⁻ radical chemistry**:
  - **NBD** as a peroxygenation proxy (positive selection)
  - **ABTS** as a peroxidation proxy (negative selection)
  - plus **product selectivity** on aromatics (e.g., **naphthalene: 1‑naphthol vs 1,4‑naphthoquinone** by LC/GC).
- Front-load **evolutionary priors** (homolog mining + MSA conservation) to (i) protect catalytic/structural residues and (ii) highlight mutable tunnel residues; combine with **structure-derived pocket/channel residue lists**.
- Build a **structure + binding_pocket_analysis module** (Boltz‑2 structure prediction + pocket/channel mapping + docking) to generate actionable residue sets and pose hypotheses for aromatic substrates (naphthalene, veratryl alcohol, NBD).
- Execute **3 rounds** with increasing information content and controlled experimental burden:  
  **Round 1** targeted single mutants (~48) → **Round 2** SSM at validated hotspots + capped combinatorials (~192) → **Round 3** model-guided recombinants (~48).
- Maintain feasibility with explicit **decision gates** and library caps (**~48 → ~192 → ~48**) compatible with microtiter expression and analytical follow-up.
- Keep **hybrid/de novo** methods strictly as a **contingency**: if CviUPO backbone mutagenesis cannot satisfy selectivity + activity + stability + H₂O₂ tolerance + expression, trigger **hybrid channel-loop redesign** (RFdiffusion2/BoltzGen) or **backbone switch** to a better-expressing homolog mined in Step 2.

---

## Design choices and assumptions (short)

- **Design mode chosen:** **backbone-focused mutant design** (explicitly recorded in `state_step1.json`).  
  **Justification:** user preference is mutants_of_backbone; UPO aromatic selectivity is repeatedly driven by **access-channel/pocket mutations** (literature precedent), and this mode best preserves catalytic machinery and expression/stability risk profile.  
  **Fallback mode:** **hybrid** (loop/channel redesign or backbone switch) only if the campaign stalls after Round 2/3.
- **Key assumptions / hard dependencies:**
  - You can provide a **CviUPO FASTA/accession** (Gate 0 hard stop if missing).
  - You can measure at least: **NBD rate**, **ABTS rate**, and **one aromatic product ratio** (naphthol vs quinone or analogous overoxidation marker), plus basic **activity/expression** and at least one **stability/H₂O₂ tolerance** readout.

---

## Step-by-step execution summary

### Step 1 — Initialize project state + hard gate on seed sequence (Gate 0)
**Goal:** create a single source of truth and prevent downstream work without the actual CviUPO sequence.  
- **Tools/models:** none (state initialization + file checks).  
- **Inputs:** `input_data.json`; expected `CviUPO.fasta` (or it writes a stub).  
- **Outputs:** `workflow_out/state_step1.json`, `workflow_out/CviUPO.fasta` (stub if missing).  
- **Decision gate (hard):** `seed_sequence_available == True` (sequence length sanity check).  
- **If fails (fallback):** provide FASTA/accession in `workflow_out/CviUPO.fasta` and rerun.

---

### Step 2 — Homolog mining + MSA + conservation (UPObase-scale triage)
**Goal:** derive evolutionary priors to protect essential residues and focus mutagenesis on permissive sites.  
- **Tools/models:** sequence DB search + alignment; `conservation_analysis`.  
- **Inputs:** seed FASTA from Step 1.  
- **Process:**
  - Mine homologs (e.g., UniRef/UPObase-like diversity), filter for coverage and identity to avoid near-duplicates.
  - Build MSA (A3M) and compute per-position conservation/entropy.
  - Create an initial **protected list** (e.g., entropy < 0.3) to be refined after structure mapping.
- **Outputs:** `homologs.fasta`, `upo_alignment.a3m`, `conservation.json`, `state_step2.json`.  
- **If search fails/empty (fallback):** proceed with seed-only alignment; mark lower confidence but continue.

---

### Step 3 — Structure prediction + heme-site sanity + binding_pocket_analysis + docking
**Goal:** convert sequence priors into structure-mapped, actionable mutation sites (channel/pocket) and substrate pose hypotheses.  
- **Tools/models:** **Boltz‑2** (structure prediction + docking/pose assessment); **binding_pocket_analysis** module.  
- **Inputs:** seed FASTA; substrate list (Veratryl alcohol, Naphthalene, NBD; ABTS often skipped for docking due to size/charge).  
- **Process:**
  - Predict CviUPO structure (`CviUPO_boltz2.pdb`).
  - Run `binding_pocket_analysis` to enumerate:
    - **channel residues**
    - **pocket residues**
    - **distal pocket residues**
    - **heme-proximal cysteine** and other catalytic candidates (to protect)
  - Dock small aromatic probes where SMILES are available (NBD, naphthalene, veratryl alcohol) to sanity-check access/orientation.
- **Outputs:** `CviUPO_boltz2.pdb`, `binding_pocket.json`, `docking_results.json`, `state_step3.json`.  
- **If docking is noisy/uninformative (fallback):** rely on pocket/channel residue lists + conservation to choose SSM sites; do not block the campaign.

---

### Step 4 — Round 1: targeted single-mutant library (~48) scored by PLM + stability
**Goal:** maximize information gain per variant by probing a small set of channel/pocket positions with conservative chemistry.  
- **Library strategy:** **targeted_mutation_set** (single mutants).  
- **Tools/models:** **PLM zero-shot scoring** (ΔlogP plausibility), **Pythia** stability prediction (ΔΔG).  
- **Inputs:** WT sequence; `binding_pocket.json`; `conservation.json`.  
- **Design logic:**
  - Start from structure-derived **channel/pocket residues**; exclude highly conserved positions (and later exclude catalytic/heme-binding residues).
  - Cap to **≤8 positions** for Round 1 feasibility.
  - Use a **restricted AA set** initially (sterics/polarity tuning without extreme charges) to reduce expression/stability failures.
  - Filter out strongly destabilizing variants (e.g., Pythia ΔΔG > ~3 kcal/mol).
  - Select **~48 variants** (96-well friendly with WT + controls).
- **Outputs:** `round1_targeted_variants.json`, `state_step4.json` (includes Round 1 gate definition).  
- **If pocket mapping is empty (fallback):** seed known CviUPO channel hotspots (e.g., **F88/T158 region**) and proceed with the same scoring/filters.

**Round 1 experimental readouts (expected):**
- NBD rate (↑ desired)
- ABTS rate (↓ desired at fixed NBD)
- Naphthalene product ratio (↑ 1‑naphthol, ↓ quinone)
- Expression proxy (e.g., activity in lysate/supernatant) + basic stability/H₂O₂ tolerance screen

---

### Step 5 — Round 1 results ingestion + hotspot selection for Round 2 (Gate 1)
**Goal:** make Round 2 contingent on real selectivity data; choose the smallest set of positions that actually move the objective.  
- **Library strategy:** decision step (no library built here).  
- **Tools/models:** optional **supervised surrogate** scaffolding (OHE/PLM embeddings) for later; primarily a scoring/triage gate.  
- **Inputs:** `round1_experimental_results.csv` (user-provided; expected columns include mutations, NBD_rate, ABTS_rate, naphthol_fraction, quinone_fraction, activity, Tm, H₂O₂_tolerance, expression).  
- **Decision gate (Gate 1):**
  - Identify **3–4 hotspot positions** from top-performing single mutants that improve:
    - **peroxygenation:peroxidation** (NBD↑ and/or ABTS↓)
    - and/or **mono-oxidation selectivity** (naphthol↑ vs quinone↓)
  - while maintaining minimum thresholds for activity/expression/stability/H₂O₂ tolerance.
- **Outputs:** `state_step5.json` with `round2_hotspots.selected_positions_for_ssm`.  
- **If Round 1 data missing (fallback):** advance conservatively using the Round 1 site list (top 4) to avoid stalling.

---

### Step 6 — Round 2: SSM at hotspots + capped combinatorial set with stability + optional ddG_bind triage (~192) (Gate 2)
**Goal:** (i) fully explore amino-acid identity at validated positions (SSM) and (ii) test epistasis/product-release effects via limited recombination.  
- **Library strategy:** **site_saturation_mutagenesis (SSM)** + **combinatorial_library** (capped).  
- **Tools/models:** **Pythia** stability; optional **OpenMM/YASARA ddG_bind** (probe ligand) for combinatorial prioritization.  
- **Inputs:** WT sequence; hotspot positions from Step 5; structure PDB from Step 3 (if available).  
- **Design logic:**
  - **SSM** at up to **4 hotspots** (20 AAs), but **downselect** with stability filter to keep total manageable.
  - Build a **capped combinatorial** set:
    - pairwise combinations of top single mutants
    - a small number of triples (randomized but position-deduplicated)
  - Optional ddG_bind triage against a representative aromatic probe (e.g., **naphthalene**) to prioritize variants likely to maintain productive binding/orientation (used as a *ranking aid*, not a hard gate).
  - Target total size **~192 variants** (≈2×96 plates).
- **Outputs:** `round2_library.json`, `state_step6.json` (Round 2 composition, filters, and Gate 2 criteria).  
- **If ddG_bind is too slow/unreliable (fallback):** skip ddG_bind and rank using stability + empirical single-mutant performance + PLM plausibility.

**Round 2 experimental readouts (expected):**
- Same as Round 1, but add stronger emphasis on:
  - **overoxidation suppression** (product ratio time-course if possible)
  - **H₂O₂ tolerance** (residual activity after peroxide challenge)
  - stability (Tm or thermal/solvent half-life) if feasible

---

### Step 7 — Round 3: model-guided recombinant panel (~48) balancing selectivity, activity, stability, H₂O₂ tolerance (Gate 3)
**Goal:** produce a small, high-value final panel by exploiting accumulated labeled data and/or physics/priors.  
- **Library strategy:** **targeted recombinant panel** (2–4 mutations) derived from Round 2 winners.  
- **Tools/models:** supervised surrogate (OHE/PLM embeddings) **if enough labeled data**; otherwise **PLM + Pythia + optional ddG_bind** ranking.  
- **Inputs:** `round2_experimental_results.csv` (if available), WT sequence, structure PDB (optional).  
- **Selection logic:**
  - Generate many candidate recombinants from top Round 2 performers.
  - Filter by:
    - stability (Pythia ΔΔG threshold)
    - PLM plausibility (avoid low-likelihood sequences)
    - optional ddG_bind (avoid obvious binding collapse)
  - **If ≥ ~30 labeled Round 2 variants:** train a surrogate on the composite objective (selectivity + activity + stability + H₂O₂ tolerance + expression) and select top ~48 by predicted score.
  - **Else:** rank by priors (ddG_bind, stability, PLM) and select top ~48.
- **Outputs:** `round3_final_panel.json`, `state_step7.json` (includes finalization criteria).  

**Gate 3 (finalize leads):**
- Select **3–5 leads** that meet:
  - improved aromatic mono-oxidation selectivity (e.g., naphthol/quinone ↑)
  - reduced peroxidation signature (ABTS ↓ at fixed NBD)
  - maintained catalytic activity and expression
  - acceptable or improved stability and **H₂O₂ tolerance**
  - compatibility with the chosen expression host/workflow

---

### Step 8 — Optional contingency: hybrid channel-loop redesign or backbone switch (only if triggered)
**Goal:** unblock the program if backbone mutagenesis cannot reach the objective frontier.  
- **Design mode:** **hybrid** (contingency only).  
- **Tools/models:** **RFdiffusion2/BoltzGen** for loop/channel redesign; **PLM** + **Pythia** for filtering.  
- **Trigger condition:** user sets `state["user_trigger_hybrid_fallback"]=true` after reviewing Round 2/3 outcomes (e.g., no variants beat WT on selectivity while maintaining activity/stability/expression).  
- **Inputs:** structure PDB; defined loop regions (from pocket/channel analysis).  
- **Outputs:** `hybrid_redesign_candidates.json` (e.g., top 24 designs), `state_step8.json`.  
- **Fallback:** if no reliable structure/loop definition exists, switch strategy to **backbone selection**: choose a better-expressing homolog from Step 2 and restart Round 1 on that backbone.

---

## Decision gates and immediate next actions (short)

- **Gate 0 (now, hard):** Provide **CviUPO FASTA/accession** (must pass Step 1). Confirm **expression host** and confirm you can run **NBD + ABTS** plus at least one **aromatic product ratio** assay (naphthalene preferred).
- **Gate 1 (post-Round 1):** Advance positions/variants that improve **NBD/ABTS** and/or **naphthol/quinone** without major losses in activity/expression/stability/H₂O₂ tolerance; select **3–4 hotspots** for Round 2 SSM.
- **Gate 2 (post-Round 2):** Advance variants that improve **mono-oxidation selectivity** and suppress overoxidation/peroxidation while meeting stability + H₂O₂ tolerance + expression constraints; decide whether enough labeled data exist to justify a surrogate for Round 3.
- **Gate 3 (post-Round 3):** Finalize **3–5 leads**. If none meet the full objective, trigger **Step 8 hybrid fallback** (loop/channel redesign or backbone switch).