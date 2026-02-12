## 1) Executive strategy summary (5–10 bullets)

- **Design mode: backbone-focused mutant design (CviUPO) with a light hybrid option** (homolog-informed residue choices + optional de novo only as a contingency for expression/stability failure).
- Run a **3-round, information-gain-first campaign**: (R1) map/selectivity levers in the heme access channel + peroxidation suppression, (R2) exploit epistasis with combinatorial channel variants + stability/H₂O₂ tolerance fixes, (R3) ML/surrogate-guided refinement and consolidation into a small “best-in-class” panel.
- Use an explicit **binding_pocket_analysis module** to define channel residues, gating positions, and second-shell electrostatics that control **mono-oxidation vs over-oxidation** on aromatics.
- Couple structure-based design (Boltz-2 docking/pose) with **physics filters** (OpenMM/YASARA ddG_bind proxies) and **developability filters** (Pythia stability + PLM zero-shot).
- Library strategy is staged: **targeted mutation set → SSM at 4–8 positions → combinatorial library** (small, curated) to keep experimental burden tractable.
- Build assays to separate mechanisms: **product analytics for peroxygenation selectivity** (LC/GC) plus **peroxidation reporter** (ABTS/NBD) as a *side-flux metric*, not the primary objective.
- Bake in **process levers** (controlled H₂O₂ feed; radical scavenger condition) to distinguish “protein-limited” vs “process-limited” over-oxidation.
- Decision gates each round: advance only variants that improve **mono-oxidation selectivity at matched conversion** while meeting **activity + stability + H₂O₂ tolerance** thresholds.

---

## 2) Assumptions and objective definition

### Assumptions (explicit)
- You have (or can obtain) a **CviUPO sequence/construct** and a baseline expression system (literature suggests **E. coli recombinant rCviUPO** is feasible).
- You can quantify products for at least one aromatic substrate (e.g., **veratryl alcohol** and/or **naphthalene**) by LC/GC, and can run a quick colorimetric peroxidation assay (ABTS/NBD).
- “Over-oxidation” is primarily driven by (i) **multiple turnovers on product** due to binding/pose permissiveness and/or (ii) **peroxidative radical chemistry** for redox-active aromatics.

### Objective (operationalized)
Primary: **Increase peroxygenative mono-oxidation selectivity** on aromatics (maximize desired mono-oxygenated product fraction at a fixed conversion window, e.g., 20–50%).  
Secondary constraints: **maintain catalytic activity**, **maintain/improve stability**, **increase H₂O₂ tolerance**, and **retain expression compatibility**.

Key measured endpoints per variant:
- **Selectivity metric**: (desired mono-oxidized product) / (total oxidized products) at matched conversion.
- **Activity metric**: initial rate or TTN under controlled H₂O₂ delivery.
- **H₂O₂ tolerance**: residual activity after peroxide challenge (defined protocol).
- **Stability**: thermal/solvent stability proxy + Pythia predicted stability; expression yield/solubility.

---

## 3) Round-by-round workflow plan (3 rounds)

### Round 1 — “Map the levers”: channel/gating scan + mechanism separation
**Objective:** Identify single mutations (and a few rational doubles) that shift aromatic binding/pose to favor **mono-oxidation** and reduce over-oxidation/peroxidation while preserving activity.

**Methods / tools**
1. **Data & structure setup**
   - Input: CviUPO sequence (and any known mutations like F88A/T158A from literature).
   - Structure: predict/relax with **Boltz-2** (or use existing model if available).
   - Output: structural model(s) with heme and defined distal pocket.

2. **binding_pocket_analysis module (required)**
   - Define: residues lining **heme access channel**, “gating” residues, and **second-shell** residues that tune polarity near the oxoferryl approach vector.
   - Output: ranked residue list with annotations (distance to heme Fe=O vector, SASA, conservation, mutability).

3. **Sequence database search + MSA + conservation**
   - Query UPObase / homologs; build MSA; compute conservation and co-variation.
   - Output: per-position conservation; “allowed” amino acids at channel positions (to avoid breaking fold).

4. **Pose assessment for aromatics**
   - Dock/pose with **Boltz-2 docking/pose assessment** for veratryl alcohol + naphthalene (and optionally ABTS as a peroxidation-prone control).
   - Output: pose clusters; distances/orientations consistent with single oxygen transfer vs repeated oxidation.

5. **Scoring / filtering**
   - **PLM zero-shot**: penalize low-likelihood mutations (fold risk).
   - **Pythia stability**: filter out destabilizing variants.
   - **OpenMM/YASARA ddG_bind proxy**: relative binding preference for substrate vs mono-oxidized product (goal: *reduce product rebinding* to limit over-oxidation).

**Candidate generation strategy**
- **Targeted mutation set** (small, high-leverage):
  - Start with known channel hotspots from rCviUPO literature (e.g., **F88, T158**) and add 6–12 pocket/channel residues from binding_pocket_analysis.
  - For each position, test 2–4 substitutions guided by: (i) homolog frequencies, (ii) sterics (open/close channel), (iii) polarity (reduce radical ET propensity), (iv) π-stacking control.
- Include a few **rational doubles**: one “pose” mutation + one “stability”/packing compensation if predicted destabilizing.

**Filtering criteria (advance to wet lab)**
- Pass: PLM score above threshold (relative to WT), Pythia Δstability not strongly negative, no disruption of conserved catalytic motifs (PCP…EGD…R…E region).
- Docking: substrate pose places target C–H/C=C within productive distance/orientation; product pose is less favorable (anti-overoxidation).
- Keep **~24–48 variants** for expression/testing.

**Outputs**
- A ranked list of variants with: predicted stability, expression risk, substrate/product pose metrics, and rationale.
- Experimental plan: 2-condition screen (± radical scavenger; controlled H₂O₂ feed).

**Fallbacks if R1 fails**
- If docking/pose is noisy: rely more on **conservation + alanine/valine scanning** of channel residues (empirically validated in rCviUPO).
- If expression collapses for many variants: shift R1 library to **conservative substitutions only** (homolog-consensus) and add a parallel **stability-only mini-set** (surface salt bridges/disulfide if applicable).

---

### Round 2 — “Exploit epistasis”: SSM at top positions + curated combinatorial set
**Objective:** Combine beneficial mutations to achieve larger selectivity gains while restoring/maintaining activity and improving H₂O₂ tolerance.

**Methods / tools**
- Update structure models for top R1 hits (Boltz-2).
- Re-run binding_pocket_analysis focusing on **new pocket geometry**.
- Build a small **supervised surrogate** (OHE/PLM embeddings → regression/classification) using R1 experimental data:
  - Targets: selectivity at matched conversion, activity, H₂O₂ tolerance, expression yield.
  - Use constrained acquisition to propose combos that satisfy stability/expression constraints.

**Candidate generation strategy**
1. **SSM (site-saturation mutagenesis)** at **4–8 positions**:
   - Choose positions that: (i) repeatedly appear in top R1 hits, (ii) are channel/gating residues, (iii) show substrate-dependent effects (veratryl vs naphthalene).
   - Practical: do SSM in **two blocks** (e.g., 2–4 positions each) to keep screening manageable.

2. **Curated combinatorial library**
   - From SSM + surrogate + structural reasoning, build a **combinatorial set** of **50–200** variants (not full factorial):
     - 2–4 “pose” mutations (channel shape)
     - 1–2 “polarity/electrostatics” mutations (bias oxygen transfer vs ET)
     - 0–2 “stability/H₂O₂ tolerance” mutations (packing/surface)

**Filtering criteria**
- In silico: PLM + Pythia must remain acceptable; eliminate combinations with strong predicted destabilization.
- Surrogate: prioritize Pareto front (selectivity ↑, activity ≥ baseline, H₂O₂ tolerance ↑).
- Experimental: advance variants that meet:
  - Selectivity improvement (e.g., **≥1.5–2×** desired mono-product fraction at matched conversion)
  - Activity **≥50–80%** of WT (or improved TTN under controlled H₂O₂)
  - H₂O₂ tolerance improvement (e.g., **≥2×** residual activity after challenge)

**Outputs**
- A small set of “lead” variants (e.g., 5–10) with replicated analytics on 2 aromatics.
- A trained surrogate model + updated design rules (which positions control over-oxidation vs peroxidation).

**Fallbacks if R2 fails**
- If combinations lose activity: introduce **compensatory stabilizing mutations** (consensus/homolog-derived) and/or reduce channel opening (over-opening can increase uncoupling).
- If selectivity gains are substrate-specific: split into **two specialization tracks** (polar aromatics vs PAHs) rather than forcing one universal variant.

---

### Round 3 — “Refine and lock”: ML-guided micro-optimization + developability consolidation
**Objective:** Deliver a final panel optimized for **selectivity + robustness** (stability, H₂O₂ tolerance, expression), and confirm generalization across substrates/conditions.

**Methods / tools**
- Use the expanded dataset (R1+R2) to retrain the **surrogate** with uncertainty estimates.
- Run **focused local search** around lead sequences:
  - single-step neighbors (1–2 mutations away)
  - targeted reversions if activity dropped
- Re-score with PLM, Pythia, and (where informative) ddG_bind proxies for substrate vs product.

**Candidate generation strategy**
- **Targeted mutation set** of **20–60** “near-lead” variants:
  - Fine-tune 1–3 residues controlling product rebinding/escape.
  - Add 1–2 mutations aimed at H₂O₂ tolerance (reduce oxidizable surface residues near channel mouth; improve packing around heme environment—done conservatively).

**Filtering criteria**
- Must meet a “deployable” profile:
  - Selectivity: best-in-project at matched conversion (or within 10% of best) across ≥2 aromatics
  - Activity: within acceptable window for application
  - Stability: improved Tm/proxy or Pythia + experimental stress test
  - Expression: consistent yield/solubility

**Outputs**
- Final **3–5 top variants** + 5–10 backups.
- A documented workflow + model artifacts enabling future rounds.

**Fallbacks if R3 fails**
- If no further gains: stop and **lock the best R2 lead**, then shift effort to **process optimization** (H₂O₂ feed, scavengers, cosolvent, biphasic) since UPO selectivity is often strongly process-coupled.

---

## 4) Library design plan

### Library types and sizes (aligned to your preferences)
1. **Round 1: targeted mutation set**
   - Size: **24–48 variants**
   - Rationale: maximize information per clone; quickly identify leverage points (channel/gating) without screening thousands.

2. **Round 2: SSM + curated combinatorial**
   - SSM: **4–8 positions**, but executed as **two smaller SSM blocks** (manageable screening).
   - Combinatorial: **50–200 variants** (curated, not full factorial).
   - Rationale: capture epistasis while keeping experimental burden tractable.

3. **Round 3: targeted near-lead set**
   - Size: **20–60 variants**
   - Rationale: micro-optimization and robustness tuning; avoid another large screen.

### Prioritization rationale (what gets mutated)
- **Highest priority:** heme access channel residues (sterics/pose), supported by rCviUPO channel engineering literature (e.g., F88/T158 as proven hotspots).
- **Second priority:** second-shell residues that tune **polarity/electrostatics** near the reactive oxoferryl approach vector (bias oxygen transfer vs ET).
- **Third priority:** conservative stability/H₂O₂ tolerance mutations (homolog-consensus; avoid catalytic motif disruption).

---

## 5) Computation stack and implementation notes

### Concrete pipeline (inputs/outputs)
1. **Homolog mining + MSA**
   - Tools: sequence DB search, UPObase retrieval, MAFFT/Clustal (implementation choice), conservation scoring.
   - In: CviUPO sequence
   - Out: MSA, conservation map, allowed substitutions per position.

2. **Structure prediction & preparation**
   - Tools: **Boltz-2**
   - In: sequence (+ heme constraints if supported)
   - Out: 3D model(s), pocket geometry.

3. **binding_pocket_analysis module**
   - In: structure, heme coordinates, substrate list
   - Out: residue list (channel lining, gating), distances, mutability scores.

4. **Docking/pose assessment**
   - Tools: **Boltz-2 docking/pose**
   - In: structure, substrates (veratryl alcohol, naphthalene; optionally ABTS/NBD)
   - Out: pose clusters + geometric metrics.

5. **Scoring**
   - PLM zero-shot (mutation likelihood)
   - **Pythia** (stability)
   - **OpenMM/YASARA** ddG_bind-style relative scoring (substrate vs product; WT vs mutant)
   - Out: ranked candidates + Pareto front.

6. **Surrogate modeling (R2/R3)**
   - Features: OHE + PLM embeddings; include assay conditions as covariates (± scavenger, H₂O₂ feed).
   - Model: gradient boosting / GP / shallow NN with constraints.
   - Out: proposed variants with uncertainty + constraint satisfaction.

### Implementation notes
- Treat ddG_bind as **relative triage**, not absolute truth; use it mainly to detect “product binds too well” risk.
- Keep a single source of truth for numbering (WT sequence index ↔ structure index) to avoid channel residue mislabeling.

---

## 6) Risk register and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Docking/pose not predictive for UPO chemistry | Mis-ranked variants | Use docking as *filter*, not sole selector; rely on channel scanning + experimental mapping in R1 |
| Over-oxidation is process-driven (H₂O₂ spikes, radicals) more than sequence-driven | Limited gains from mutations | Include controlled H₂O₂ feed and ± scavenger conditions from R1 to separate causes |
| Expression drops for channel mutants | Slows iteration | Use PLM + conservation filters; keep mutations conservative; include expression-enhancing conditions/construct tweaks |
| H₂O₂ inactivation dominates | Low TTN | Screen H₂O₂ tolerance explicitly; add process control; consider stabilizing mutations in R2/R3 |
| Assays confound peroxygenation with peroxidation (ABTS/NBD) | Wrong optimization target | Use ABTS/NBD only as side-flux metric; primary readout is product analytics for aromatics |

---

## 7) Decision gates and go/no-go criteria

### End of Round 1 (go to R2 if)
- At least **3–5 variants** show **clear selectivity improvement** (e.g., ≥1.3–1.5× mono-product fraction at matched conversion) **without catastrophic activity loss**.
- Expression is workable for ≥50% of tested variants.
- Mechanism separation is achieved: you can classify variants as “reduced product rebinding” vs “reduced peroxidation flux” (via ± scavenger and ABTS/NBD side assay).

### End of Round 2 (go to R3 if)
- At least **1–2 lead variants** achieve **≥2× selectivity improvement** (or meet your application threshold) while maintaining activity and showing improved H₂O₂ tolerance.
- Surrogate model shows usable signal (cross-validated performance above baseline; uncertainty not dominating).

### End of Round 3 (stop/lock if)
- A final panel meets deployable profile across ≥2 aromatics and stress conditions; otherwise lock best R2 lead and shift to process optimization.

---

## 8) Suggested immediate next actions (first 1–2 weeks)

1. **Confirm construct + baseline**: CviUPO sequence/variant used (WT vs known F88A/T158A), expression host/format, and baseline activity/selectivity on **veratryl alcohol** and **naphthalene** (even rough).
2. **Stand up the binding_pocket_analysis** on a Boltz-2 CviUPO model; produce a **shortlist of 10–20 channel residues** with conservation annotations.
3. **Define the experimental screen conditions** for R1:
   - Controlled H₂O₂ delivery regimen (at least one low steady-state condition)
   - Two assay modes: (i) product analytics for mono-oxidation selectivity, (ii) ABTS/NBD as peroxidation side metric
   - Optional ± ascorbate condition to quantify radical contribution.
4. **Design the R1 targeted mutation set (24–48 variants)** using: (i) channel shortlist, (ii) homolog frequencies, (iii) PLM/Pythia filters.
5. **Set up data schema** for surrogate modeling (variant sequence, conditions, selectivity/activity/stability/H₂O₂ tolerance, expression yield).

If you share the **CviUPO sequence/construct details** (signal peptide present/absent, tags, any existing mutations) and your **preferred primary aromatic substrate + analytics method**, I can turn this into a concrete R1 mutation table (positions → substitutions → rationale) sized to your screening capacity.