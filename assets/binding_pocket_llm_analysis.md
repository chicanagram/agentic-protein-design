## Stage 1: Global Pocket Phenotypes

## Per-protein interpretations (proximal <6 Å; distal ~6–11 Å)

### ET096 — **“Small, dry inner pocket that over-oxidizes once it binds.”**
- **Proximal electrostatics:** Essentially *uncharged* (charged_fraction 0.0) and low polar (0.182) with the **most hydrophobic proximal environment** (hw_weighted −0.94) and **high kd_weighted (2.18)** → favors nonpolar binding but offers little H-bond/charge steering for a single productive pose.
- **Proximal sterics:** **Small-residue rich** (small_residue_frac 0.636) with lower mean volumes (mean_volume 88 Å³; weighted 90.8) → a “slick” pocket that can admit S82 but may not *pose-lock* it. Reactive center is **relatively far** (reactive_center_distance 7.10 Å).
- **Distal electrostatics:** Modestly polar/charged (polar 0.368; charged 0.132) but still fairly hydrophobic overall (hw_weighted −0.46). Distal kd_weighted 0.97 suggests moderate distal “stickiness”.
- **Distal sterics / outer size:** Distal centroid distances are the **largest** in the set (mean_dist_to_centroid 10.25; mean_min_dist_to_centroid 8.57) → a more open outer vestibule feeding into a smaller, drier inner pocket.
- **Pocket phenotype & catalytic implications:** Outer openness + inner hydrophobicity tends to support binding/throughput, but weak polar/charged pose control near the reactive center can allow **re-binding/re-orientation** that promotes **over-oxidation (peroxidation-like behavior on S82)**.  
  **Reaction support:** S82 **Mono:Di = 0.3** (strongly Di-Ox biased) and relatively low ABTS (0.146) suggests it’s not a classic surface-peroxidase, but its pocket environment is permissive for **multiple turnovers on the bound product** (Di-Ox). Veratryl alcohol is moderate (0.597), consistent with hydrophobic access but limited steering.

---

### CviUPO — **“Bulky, polar clamp: pose-locking that favors mono-oxygenation selectivity.”**
- **Proximal electrostatics:** More **polar and slightly charged** (polar 0.385; charged 0.077) than most, with hw_weighted −0.825 and kd_weighted 1.06 → a mixed polar/hydrophobic inner pocket that can stabilize a defined binding pose.
- **Proximal sterics:** **Most sterically ‘packed’**: high mean_volume (111 Å³) and **very high bulky_residue_frac (0.615)**; median_min_dist_to_ligand is the **tightest** (3.575 Å) → strong shape complementarity/pose restriction.
- **Distal electrostatics:** **Highest distal polarity** (polar 0.513) with modest charge (0.128) and low kd_weighted (0.387) → distal region is polar but not strongly hydrophobic-binding; likely helps guide substrate entry/solvation rather than “trap” product.
- **Distal sterics / outer size:** Distal centroid distances are moderate (mean_dist_to_centroid 9.91; mean_min 8.08) → not the most open vestibule; more “channeled”.
- **Pocket phenotype & catalytic implications:** A **tight, polarizable inner pocket** tends to favor **productive peroxygenative positioning** (single-hit oxygen transfer) and can reduce over-oxidation by limiting product reorientation.  
  **Reaction support:** S82 **Mono:Di = 1.7** (mono favored) fits a pose-locking pocket. However, ABTS is **very high (3.939)**, implying CviUPO also supports **peroxidative chemistry** (likely via accessible electron-transfer pathways/surface sites not captured fully by this pocket-only analysis). Net: **selective mono-oxygenation in-pocket**, but strong peroxidase capability overall.

---

### CviUPO-F88L+T158A — **“CviUPO opened and de-polarized: easier approach to the reactive center, weaker pose control.”**
*(Variant family analysis vs CviUPO WT is in section 2A; here is the per-structure readout.)*
- **Proximal electrostatics:** Polar fraction drops (0.308 vs 0.385 WT) while charge stays similar (0.077). Proximal hw_weighted becomes slightly **more hydrophobic** (−0.792 vs −0.825) and kd_weighted increases (1.40 vs 1.06) → less polar steering, more hydrophobic “grab”.
- **Proximal sterics:** Mean volumes slightly decrease (108 vs 111), but bulky fraction remains **high** (0.615). **Reactive center distance decreases strongly** (5.83 Å vs 7.72 Å WT) → geometry now places the reactive center closer/more attack-ready.
- **Distal electrostatics:** Distal becomes **less polar** (0.485 vs 0.513) and kd_weighted increases (0.73 vs 0.387) → distal region becomes more hydrophobic/retentive.
- **Distal sterics / outer size:** Slightly more compact outer pocket (mean_dist_to_centroid 9.63 vs 9.91).
- **Pocket phenotype & catalytic implications:** This looks like a shift toward **higher intrinsic reactivity/turnover potential** (shorter reactive-center distance) but **reduced selectivity control** (less proximal polarity; more hydrophobic retention distally), which can increase chances of **secondary oxidation** if product remains bound. (No reaction row provided for this variant, so this is a structural prediction.)

---

### DcaUPO — **“Reactive-center close-in ‘hot pocket’: high peroxygenation capacity with peroxidation competence.”**
- **Proximal electrostatics:** Low polar (0.154) but some charge (0.077) with **very hydrophobic proximal hw_weighted (−1.04)** and high kd_weighted (1.79) → strongly nonpolar inner pocket, but with a bit of electrostatic functionality.
- **Proximal sterics:** High bulky fraction (0.615) and **largest proximal volume variance** (1183) → a pocket that is sterically substantial but heterogeneous (could support multiple poses/substrates). **Reactive center distance is short** (4.93 Å) → favors productive oxygen transfer.
- **Distal electrostatics:** **Most charged distal shell** (charged 0.20) with moderate polarity (0.40) → distal residues can tune proton/electron traffic and substrate approach.
- **Distal sterics / outer size:** Outer pocket size is mid-to-open (mean_dist_to_centroid 10.00; mean_min 8.20).
- **Pocket phenotype & catalytic implications:** Short reactive-center distance supports **high peroxygenative turnover**; distal charge may also facilitate **peroxidative side chemistry** (electron transfer/proton management), especially for peroxidase reporters.  
  **Reaction support:** Very high **veratryl alcohol (1.558)** and **NBD (1.242)** indicate strong peroxygenation; ABTS is also high (2.7), consistent with **dual competence**. S82 **Mono:Di = 1.6** suggests it still maintains mono selectivity despite a reactive geometry—likely because bulky proximal residues restrict product re-binding orientations even in a hydrophobic pocket.

---

### TE314 — **“Balanced, mid-sized pocket: decent binding but limited pose enforcement → mixed oxidation.”**
- **Proximal electrostatics:** Uncharged (0.0) but moderately polar (0.308); hw_weighted −0.894 and kd_weighted 1.82 → hydrophobic leaning with some polar contacts.
- **Proximal sterics:** More “average” sterics (mean_volume 98.5; bulky 0.308) and relatively low variance (559) → fewer strong steric constraints than CviUPO/DcaUPO. Reactive center distance is **very short** (4.08 Å), which can increase oxidation probability once bound.
- **Distal electrostatics:** Distal is fairly hydrophobic (hw_weighted −0.634) with higher kd_weighted (1.43) than most → distal region may retain substrates/products.
- **Distal sterics / outer size:** Distal centroid distances are among the **smallest** (mean_dist_to_centroid 9.73; mean_min 7.86) → a more compact outer pocket.
- **Pocket phenotype & catalytic implications:** Close reactive center promotes oxidation, but moderate steric/polar pose control plus distal retention can allow **secondary oxidation**.  
  **Reaction support:** S82 **Mono:Di = 0.7** (Di favored) fits weaker pose-locking and/or higher product residence time.

---

### OA167 — **“Hydrophobic, bulky inner pocket with a ‘sticky’ distal shell: high throughput but over-oxidation-prone.”**
- **Proximal electrostatics:** Uncharged (0.0) with moderate polar (0.308) but **most hydrophobic proximal hw_weighted (−1.36)** and kd_weighted 1.41 → strongly nonpolar inner environment.
- **Proximal sterics:** High mean_volume (108.5) and high bulky fraction (0.538) with low small fraction (0.154) → substantial steric packing; reactive center distance is short (4.55 Å).
- **Distal electrostatics:** Distal kd_weighted 1.03 and hw_weighted −0.67 → distal region is relatively hydrophobic/retentive.
- **Distal sterics / outer size:** Outer pocket is moderate (mean_dist_to_centroid 9.74; mean_min 8.08).
- **Pocket phenotype & catalytic implications:** Hydrophobic + bulky proximal region can bind aromatic-like motifs well and place them close to the reactive center, but distal hydrophobicity can **retain product**, increasing **Di-Ox** probability.  
  **Reaction support:** Highest S82 total yield (46.8) but **Mono:Di = 0.6** (Di favored) matches “high throughput, lower selectivity”.

---

## 2) Comparative analyses

### 2A) Intra-protein variant analysis (families with variants)

#### Family: **CviUPO (WT) vs CviUPO-F88L+T158A**
Assumption: **CviUPO_S82_glide** is the WT/reference for the named double mutant.

**Changes in structural dimensions (variant vs WT):**
- **(i) Proximal electrostatics:** **Less polar** (polar 0.308 ↓ from 0.385); charge unchanged (0.077). Proximal kd_weighted **increases** (1.40 ↑ from 1.06) → more hydrophobic “binding drive”, less polar steering.
- **(ii) Proximal sterics:** Mean volume slightly **decreases** (108 ↓ from 111) with bulky fraction unchanged (0.615). Key geometric shift: **reactive_center_distance drops** (5.83 ↓ from 7.72) → more attack-ready positioning.
- **(iii) Distal electrostatics:** Distal becomes slightly **less polar** (0.485 ↓ from 0.513) and more hydrophobic-binding (kd_weighted 0.73 ↑ from 0.387).
- **(iv) Distal sterics / outer size:** Slightly **more compact** (mean_dist_to_centroid 9.63 ↓ from 9.91); fewer aligned pocket residues reported (33 vs 39), consistent with altered pocket definition/coverage.

**Mechanistic rationale:** F88L and T158A likely reduce specific polar/π interactions and subtly reshape the channel, giving **closer reactive approach** (potentially higher rate) but **weaker pose-locking** and **greater hydrophobic retention** (especially distally), which can shift the balance toward **more secondary oxidation/peroxidative leakage** if products linger or reorient.

---

### 2B) User-requested pairwise comparison: **CviUPO vs ET096**

**(i) Proximal electrostatics**
- **CviUPO** is **more polar/charged** (polar 0.385; charged 0.077) than **ET096** (polar 0.182; charged 0.0).
- ET096 has **higher proximal kd_weighted** (2.18 vs 1.06) and similar hydrophobicity (both hydrophobic), implying ET096 is a **drier, less electrostatically guided** pocket.

**(ii) Proximal sterics**
- **CviUPO** is far more **bulky/packed** (bulky 0.615; mean_volume 111) than **ET096** (bulky 0.273; mean_volume 88; small_residue_frac 0.636).
- CviUPO is also **tighter to ligand** (median_min_dist 3.58 vs 4.33), consistent with stronger shape complementarity.

**(iii) Distal electrostatics**
- **CviUPO distal is much more polar** (0.513 vs 0.368) and has **lower kd_weighted** (0.387 vs 0.967), suggesting a more solvated/less “sticky” outer region than ET096.

**(iv) Distal sterics / outer pocket size**
- **ET096 outer pocket is more open** (mean_dist_to_centroid 10.25 vs 9.91; mean_min 8.57 vs 8.08), consistent with easier access but also potentially more conformational freedom.

**Mechanistic rationale (link to function):**
- **CviUPO’s** bulky + polar proximal pocket should **pose-lock** S82 and favor **single-hit peroxygenation** → matches **higher Mono:Di (1.7)**.
- **ET096’s** small-residue-rich, uncharged, hydrophobic proximal pocket plus a more open vestibule likely allows **multiple binding modes and easier product re-entry**, promoting **over-oxidation (Di-Ox)** → matches **Mono:Di (0.3)**.  
- The strikingly higher **ABTS** for CviUPO (3.939 vs 0.146) suggests CviUPO also has stronger **peroxidative electron-transfer capability** (likely involving surface/long-range features beyond the immediate pocket), whereas ET096 behaves more like a pocket-driven oxygenation catalyst that over-oxidizes *within* the pocket rather than acting as a strong peroxidase on ABTS.

---

## 3) Cross-protein “pocket phenotypes” (recurring archetypes)

1) **Pose-locking, bulky proximal clamp (selectivity-forward mono-oxygenation)**
   - Hallmarks: high proximal bulky fraction/volume, moderate-to-high proximal polarity/charge.
   - Example: **CviUPO** (Mono:Di 1.7).  
   - Trade-off: can still show strong peroxidation if the enzyme has efficient ET pathways (CviUPO high ABTS), but *in-pocket* selectivity is good.

2) **Reactive-center close-in + bulky but hydrophobic (high peroxygenation capacity; selectivity depends on retention)**
   - Hallmarks: short reactive_center_distance, high proximal hydrophobicity, bulky residues; distal charge can tune side chemistry.
   - Example: **DcaUPO** (high veratryl alcohol/NBD; Mono:Di 1.6; ABTS 2.7).  
   - Trade-off: high turnover; peroxidation competence rises when distal shell is charged/polar enough to support ET/proton traffic.

3) **Hydrophobic “sticky” pocket with distal retention (throughput-forward but over-oxidation-prone)**
   - Hallmarks: very hydrophobic proximal hw_weighted, moderate/high distal kd_weighted (retentive), not enough polar pose control.
   - Examples: **OA167** (highest S82 total; Mono:Di 0.6), **TE314** (Mono:Di 0.7).  
   - Trade-off: good conversions but more Di-Ox/over-oxidation.

4) **Open vestibule + small, dry proximal microenvironment (access-forward, weak steering → over-oxidation)**
   - Hallmarks: large distal centroid distances (open), proximal uncharged/low polar, high small-residue fraction.
   - Example: **ET096** (Mono:Di 0.3).  
   - Trade-off: access and binding are easy, but productive peroxygenative pose is not enforced; repeated oxidation becomes likely.

If you want, I can also (i) map the **specific aligned proximal positions** (from `pocket_alignment_table`) that most plausibly drive these phenotypes (e.g., where ET096 has small residues vs CviUPO bulky/polar), and (ii) propose **minimal mutation sets** to push ET096 toward CviUPO-like mono-selectivity (increase proximal polarity + introduce one “gatekeeper” bulky residue while reducing distal hydrophobic retention).

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue-level mechanistic hypotheses  
(Positions are given in **each protein’s own numbering**; effects are tied back to the pocket phenotypes in `structural_summary_text`.)

### A. “Pose-lock / clamp” positions (primary steric drivers; also tune π/polarizability)

#### **CviUPO 88 / CviUPO-F88L+T158A 88 / ET096 103 / DcaUPO 86 / TE314 108 / OA167 104**
- **Identities:**  
  - ET096 **I103**  
  - CviUPO **F88** → variant **L88** (engineered)  
  - DcaUPO **L86**  
  - TE314 **I108**  
  - OA167 **I104**
- **Substitution class:** mainly **steric + π/polarizability shift** (F ↔ aliphatic I/L).  
- **Mechanistic consequence:**  
  - **CviUPO WT F88** provides a **bulky aromatic wall** that can (i) increase **shape complementarity** and (ii) add **π-contact/dispersion “pose-locking”**, consistent with the “**bulky, polar clamp**” phenotype and higher mono-selectivity.  
  - **F88L (variant)** removes aromaticity while keeping bulk → **weakens specific π-anchoring** and slightly “smooths” the wall. This matches the summary’s prediction: **reduced pose control** and a shift toward **more hydrophobic retention** and potentially more secondary oxidation if product lingers/reorients.
- **Intra-family contrast (CviUPO WT vs variant):**  
  - **F88L** specifically degrades the *quality* of packing (loss of π) more than the *quantity* (still bulky), consistent with “opened/de-polarized” behavior without fully collapsing the clamp.

---

### B. “Reactive-center approach / gating” positions (strong steric gating; can change attack geometry)

#### **ET096 77 / CviUPO 60 / DcaUPO 58 / TE314 80 / OA167 76**
- **Identities:** ET096 **A77**, CviUPO **T60**, DcaUPO **D58**, TE314 **T80**, OA167 **A76**
- **Substitution class:** **polarity/electrostatics shift** (A/T neutral-polar; **D** introduces **negative charge**) + mild sterics (A < T ≈ D).  
- **Mechanistic consequence:**  
  - **ET096 A77** supports the “**small, dry inner pocket**” (low polar/uncharged proximal) → weak steering, more pose degeneracy → consistent with **over-oxidation** tendency.  
  - **CviUPO/TE314 T60/T80** adds an **H-bond-capable polar handle** that can help **orient substrate** and reduce unproductive poses (fits CviUPO’s higher proximal polarity).  
  - **DcaUPO D58** is the standout: introduces a **localized negative electrostatic feature** near the pocket that can (i) bias substrate orientation via dipole interactions and/or (ii) influence local proton/water organization. This is consistent with DcaUPO’s “**hot pocket**” that is hydrophobic overall but retains **some electrostatic functionality** and strong turnover.
- **Confidence note:** D58 is a plausible contributor to DcaUPO’s distal/proximal electrostatic tuning even though the global proximal charged fraction is modest—**a single Asp can matter disproportionately** if it faces the cavity.

---

### C. “Back-wall packing / channel shape” positions (steric architecture; proline kink is notable)

#### **ET096 80 / CviUPO 64 / DcaUPO 62 / TE314 84 / OA167 80**
- **Identities:** ET096 **A80**, CviUPO **L64**, DcaUPO **F62**, TE314 **P84**, OA167 **L80**
- **Substitution class:** strongly **steric** (A small ↔ L/F bulky) plus **conformational** effect (P).  
- **Mechanistic consequence:**  
  - **ET096 A80** contributes to the “**small-residue-rich, slick**” proximal environment → fewer steric constraints → easier reorientation/rebinding → **Di-oxidation bias**.  
  - **DcaUPO F62** adds a **bulky aromatic buttress** that can enforce a productive pose even in a hydrophobic pocket—consistent with DcaUPO maintaining **mono selectivity** despite high intrinsic reactivity.  
  - **TE314 P84** can impose a **backbone kink/rigidity** that reshapes the channel; this can reduce “designed” complementarity and yield the “**balanced, mid-sized pocket**” with weaker pose enforcement (fits TE314’s mixed oxidation).
- **Net:** This position is a major determinant of whether the pocket behaves like a **tight clamp (bulky)** vs a **slippery cavity (small)**.

---

### D. “Distal retention / product trapping” positions (outer-shell hydrophobic stickiness vs openness)

#### **ET096 223 / CviUPO 210 / DcaUPO 206 / TE314 236 / OA167 226**
- **Identities:** ET096 **F223**, CviUPO **M210**, DcaUPO **L206**, TE314 **V236**, OA167 **I226**
- **Substitution class:** **steric/hydrophobic packing** (all nonpolar; aromatic F is more polarizable/bulky).  
- **Mechanistic consequence:**  
  - **ET096 F223** (aromatic) can increase **distal “stickiness”** via dispersion/π interactions, consistent with ET096 having moderate distal kd_weighted and an open vestibule feeding a dry inner pocket—i.e., substrate/product can **linger and re-enter**.  
  - **TE314 V236 / OA167 I226** are hydrophobic but less polarizable than Phe; OA167/TE314 already show “**distal retention**” phenotypes—this position likely contributes but is not uniquely diagnostic alone.

---

### E. “Electrostatic hotspot” position (clear charge vs neutral; likely a major electrostatic driver)

#### **ET096 178 / CviUPO 165 / CviUPO-F88L+T158A 165 / DcaUPO 161 / TE314 190 / OA167 181**
- **Identities:** ET096 **A178**, CviUPO **K165**, DcaUPO **C161**, TE314 **V190**, OA167 **A181**
- **Substitution class:** **electrostatic** (K = + charge vs neutral A/V/C) + steric (K is larger).  
- **Mechanistic consequence:**  
  - **CviUPO K165** introduces a **cationic feature** that can (i) stabilize polar transition-state-like charge distributions, (ii) organize waters, or (iii) bias substrate orientation through long-range electrostatics. This aligns with CviUPO’s **more polar/partly charged proximal environment** and “pose-locking clamp” behavior.  
  - **ET096/OA167 A** and **TE314 V** lack this steering → consistent with their more hydrophobic/uncharged proximal phenotypes and greater over-oxidation propensity (ET096, OA167, TE314).  
  - **DcaUPO C161** is neutral; DcaUPO’s electrostatic tuning likely comes more from other charged residues (e.g., D58 and/or distal charged shell noted in the summary).
- **Intra-family contrast:** K165 is **unchanged** in the CviUPO double mutant, so the variant’s “de-polarization” is better explained by **F88L + T158A** rather than loss of this cation.

---

### F. Variant-defining mutation explicitly present in the table (directly links to the summary)

#### **CviUPO 158 (WT T158) → CviUPO-F88L+T158A 158A** (aligned with **ET096 171A / DcaUPO 154F / TE314 183V / OA167 174P**)
- **Identities:** CviUPO **T158** vs variant **A158**; others vary widely.
- **Substitution class:** **polarity loss** (T → A) + slight steric reduction.  
- **Mechanistic consequence (ties directly to summary):**  
  - Removing the Thr hydroxyl eliminates a potential **H-bond anchor** and reduces local polarity → matches observed/predicted **drop in proximal polar fraction** and weaker “pose-locking” in the variant.  
  - Mechanistically, this should increase the probability of **alternative substrate/product orientations** and—combined with the variant’s more hydrophobic distal shell—raise **secondary oxidation risk** (product residence/rebinding).
- **Intra-family contrast:** This is the cleanest residue-level explanation for the variant’s **“de-polarized”** proximal pocket.

---

## 2) Ranked residue list (mechanistic importance)

### High-confidence mechanistic driver residues
1. **CviUPO F88 → L88 (variant)** (CviUPO 88): loss of aromatic clamp → weaker pose-locking/π anchoring.  
2. **CviUPO T158 → A158 (variant)** (CviUPO 158): direct polarity/H-bond removal → reduced steering, consistent with variant phenotype.  
3. **CviUPO K165** (CviUPO 165): unique **positive charge** among homologs here → strong electrostatic steering candidate.  
4. **ET096 A80 vs DcaUPO F62 / CviUPO L64 / OA167 L80 / TE314 P84**: major steric architecture switch (small vs bulky vs proline-shaped wall) that maps well onto “slick” vs “clamp/hot pocket” behaviors.  
5. **DcaUPO D58** (DcaUPO 58): unique **negative charge** at this aligned site → plausible electrostatic orientation/proton-water organization driver.

### Secondary modulators
- **ET096 F223 / CviUPO M210 / DcaUPO L206 / TE314 V236 / OA167 I226**: distal hydrophobic retention tuning (product trapping vs release).  
- **ET096 A77 vs CviUPO/TE314 T60/T80**: adds/removes a polar contact that can subtly bias pose.

### Likely neutral/background (within this dataset/phenotypes)
- Positions that are largely conservative hydrophobics with similar size across most proteins and no clear linkage to the described phenotype shifts, e.g.:  
  - **ET096 74V / CviUPO 57L / DcaUPO 55L / TE314 77L** (mostly hydrophobic, modest size differences)  
  - **ET096 172S / CviUPO 159S / TE314 184S** (conserved Ser; OA167 T is similar)

If you want, I can convert the “driver residues” into **minimal mutation hypotheses** to push ET096 toward a CviUPO-like mono-selective clamp (e.g., introduce one bulky wall + one polar anchor while avoiding increased distal retention).