## Stage 1: Global Pocket Phenotypes

## Per-protein pocket interpretations (proximal <6 Å; distal ~6–11 Å)

### ET096_S82_glide — **“Small, dry inner pocket; roomy outer shell → oxidation-prone throughput.”**
- **Prox electrostatics:** Essentially *uncharged* (charged_fraction 0.0) and weakly polar (polar_fraction 0.182) with relatively high kd_weighted (~2.18) and fairly hydrophobic hw_weighted (~−0.94) → limited H-bond/ionic “pose-locking” near the reactive center. Median residue→reactive-center distance is relatively long (~7.92 Å), consistent with fewer strong directing contacts.
- **Prox sterics:** Many close residues (num_pocket_res<6 = 12) but dominated by *small residues* (small_residue_frac 0.636; bulky 0.273) and lower mean proximal volume (~88 Å³) → a “smooth” cavity that can allow multiple ligand microposes rather than a single constrained reactive pose. Reactive_center_distance is long (~7.10 Å), consistent with less enforced near-attack geometry.
- **Distal electrostatics:** Some charge appears distally (charged_fraction 0.132; polar 0.368) but distal kd_weighted is low (~0.97) → distal region not strongly cationic; more “neutral funnel” than electrostatic steering.
- **Distal sterics / outer size:** Distal centroid distances are among the largest (mean_dist_to_centroid ~10.25 Å; mean_min_dist_to_centroid ~8.57 Å) with moderate distal volume (~100 Å³) → a relatively open outer pocket that can admit/retain alternative orientations.
- **Phenotype & catalytic implication:** **Permissive/underspecified binding**: weak proximal polarity + small-residue lining + open distal region tends to increase pose heterogeneity, which often correlates with **more competing/peroxidative chemistry** (off-pathway electron transfer, less controlled oxygen transfer).
  - **Reaction support:** ET096 shows **high S82 total yield (41.1%) but strongly Di-Ox biased** (Mono:Di 0.3), consistent with a pocket that doesn’t enforce a single productive peroxygenative pose. Peroxygenation on VA is moderate (0.597) while ABTS is low (0.146), suggesting it’s not a classic “ABTS-oxidizer,” but for S82 it behaves like a **throughput oxidizer** rather than a selective mono-oxygenator.

---

### CviUPO_S82_glide — **“Polar, bulky inner clamp → mono-oxygenation selectivity (but also peroxidase-like tendencies).”**
- **Prox electrostatics:** More polar/charged than ET096 (charged_fraction 0.077; polar_fraction 0.385) with lower kd_weighted (~1.06) and hydrophobic hw_weighted (~−0.83) → increased capacity for specific polar contacts near the ligand.
- **Prox sterics:** Proximal region is **bulky and tight** (mean_volume ~111 Å³; bulky_residue_frac 0.615; small_residue_frac 0.154) and the ligand sits closer to residues (median_min_dist_res_to_ligand ~3.58 Å). This looks like a “shape clamp” that can restrict orientations.
- **Distal electrostatics:** Distal region is quite polar (polar_fraction 0.513) with some charge (0.128) and very low kd_weighted (~0.39) → distal environment is not strongly cationic; instead it’s **polar/solvating**, potentially stabilizing ingress/egress and polar transition states.
- **Distal sterics / outer size:** Outer pocket is not especially expanded (mean_dist_to_centroid ~9.91 Å; mean_min_dist_to_centroid ~8.08 Å) and distal volume is slightly higher (~105 Å³) → enough space for binding, but less “open funnel” than ET096.
- **Phenotype & catalytic implication:** **Pose-locking inner pocket** (bulky + polar) tends to favor **productive peroxygenation** by enforcing near-attack geometry and limiting re-binding modes that lead to over-oxidation.
  - **Reaction support:** CviUPO has **Mono:Di = 1.7** (mono favored) despite lower total yield (23.7%), matching a **selectivity-over-throughput** pocket. However, it also has **very high ABTS activity (3.939)**, consistent with a pocket/electrostatic environment that can support peroxidative electron-transfer chemistry as well—i.e., it’s “selective on S82” but still **peroxidase-capable**.

---

### CviUPO-F88L+T158A_S82_chai1_0 — **“Same clamp, slightly ‘de-bulky/polar-tuned’ → closer reactive approach, potentially higher peroxygenation efficiency.”**
*(No reaction row provided for this variant; interpretation is structural relative to CviUPO.)*
- **Prox electrostatics:** Similar charged_fraction (0.077) but **lower polar_fraction** (0.308 vs 0.385 in CviUPO) and higher kd_weighted (~1.40 vs ~1.06) → proximal region becomes a bit less polar/more “hydrophobic-leaning,” which can reduce strong nonproductive H-bonding but may also reduce pose anchoring.
- **Prox sterics:** Mean proximal volume slightly decreases (108 vs 111 Å³) with a modest increase in small_residue_frac (0.231 vs 0.154) while bulky fraction stays high (0.615). Importantly, **reactive_center_distance drops** (5.83 Å vs 7.72 Å) → geometry suggests the docked reactive center is positioned **closer to the catalytic oxidant**, often a hallmark of improved peroxygenative competence (if the pose is correct).
- **Distal electrostatics:** Distal polarity remains high (polar_fraction 0.485) and kd_weighted increases (0.73 vs 0.39) → distal becomes less “polar-solvating” and slightly more hydrophobic/less permissive to water.
- **Distal sterics / outer size:** Distal centroid distances are slightly smaller than CviUPO (mean_dist_to_centroid 9.63 vs 9.91 Å) with similar distal volume (~106 Å³) → marginally more compact outer region.
- **Phenotype & catalytic implication:** Compared to CviUPO, this looks like a **reactive-center positioning optimization** (closer approach) with a mild reduction in polarity. Mechanistically, that combination often **increases oxygen-transfer probability per binding event** (higher peroxygenation efficiency) but could reduce “electrostatic steering” that helps discriminate poses—net effect would depend on whether the new pose is uniquely productive.

---

### DcaUPO_S82_glide — **“Hydrophobic inner wall + charged distal ring → strong oxidant access with mixed pathway propensity.”**
- **Prox electrostatics:** Low proximal polarity (polar_fraction 0.154) with some charge (0.077) and high kd_weighted (~1.79) plus very hydrophobic hw_weighted (~−1.04) → a **hydrophobic proximal microenvironment** that can favor binding of nonpolar substrates and reduce water competition near the oxidant.
- **Prox sterics:** High proximal variance (volume_variance ~1183; highest here) with bulky_residue_frac 0.615 and reactive_center_distance ~4.93 Å (short) → suggests a **structured but heterogeneous** pocket: can achieve close reactive approach, but with multiple microcavity shapes that may enable alternative oxidation trajectories.
- **Distal electrostatics:** Distal region is the most charged in this set (charged_fraction 0.20) with moderate polarity (0.40) and kd_weighted ~0.82 → distal charges could promote **electron-transfer/peroxidative** routes (especially for redox-active substrates) and/or influence H2O2/water organization.
- **Distal sterics / outer size:** Outer pocket size is moderate-large (mean_dist_to_centroid ~10.00 Å) with distal volume ~104 Å³ → accessible pocket with enough space for substrate repositioning after first oxidation.
- **Phenotype & catalytic implication:** **High catalytic competence** (close reactive approach + hydrophobic proximal region) but with **distal electrostatic features** that can support peroxidative chemistry and/or facilitate sequential oxidation (re-binding/reorientation).
  - **Reaction support:** DcaUPO is strong on **peroxygenation reporters** (VA 1.558; NBD 1.242) yet also high on **ABTS (2.7)**. On S82 it is **mono-selective (Mono:Di 1.6)** but with lower total yield (16.2). This matches a pocket that can do peroxygenation very well, while still being **redox-competent** for peroxidation depending on substrate.

---

### TE314_S82_chai1_0 — **“Balanced polarity, less bulky inner pocket → higher turnover but weaker mono-control.”**
- **Prox electrostatics:** Uncharged proximally (charged_fraction 0.0) but moderately polar (polar_fraction 0.308) with kd_weighted ~1.82 and hw_weighted ~−0.89 → polar contacts possible, but no ionic anchoring.
- **Prox sterics:** Lower bulky fraction (0.308) and moderate proximal volume (~98.5 Å³) with relatively short reactive_center_distance (~4.08 Å) → can achieve close approach without a strong steric clamp, which often increases turnover but reduces strict pose control.
- **Distal electrostatics:** Distal is modestly polar (0.371) with low charge (0.114) but **highest distal kd_weighted** (~1.43) in the set → distal region is comparatively more cationic/interaction-prone, potentially stabilizing certain substrate entry orientations.
- **Distal sterics / outer size:** Distal centroid distances are on the smaller side (mean_dist_to_centroid ~9.73 Å; mean_min_dist_to_centroid ~7.86 Å) with moderate distal volume (~102.5 Å³) → somewhat more compact outer pocket than ET096/DcaUPO.
- **Phenotype & catalytic implication:** **Turnover-oriented, moderately guided** pocket: close reactive approach but weaker steric enforcement can allow **more di-oxidation** once substrate is bound/retained.
  - **Reaction support:** S82 total yield is high (36.5) but **Di-Ox dominates** (Mono:Di 0.7), consistent with “good access + weaker mono gatekeeping.”

---

### OA167_S82_swissdock_0 — **“Hydrophobic, bulky proximal pocket with open outer region → strong binding/retention and over-oxidation.”**
- **Prox electrostatics:** Uncharged (0.0) with moderate polarity (0.308) but **very hydrophobic hw_weighted (~−1.36; most hydrophobic proximal)** and kd_weighted ~1.41 → favors nonpolar packing over polar pose constraints.
- **Prox sterics:** High proximal volume (~108.5 Å³; weighted ~111) with high bulky fraction (0.538) and low small fraction (0.154) → strong hydrophobic packing/retention. Reactive_center_distance is short (~4.55 Å), enabling efficient oxidation once bound.
- **Distal electrostatics:** Distal is moderately polar (0.40) with low charge (0.114) and kd_weighted ~1.03 → not strongly electrostatically steering; more neutral.
- **Distal sterics / outer size:** Outer pocket is fairly open (mean_dist_to_centroid ~9.74 Å; mean_min_dist_to_centroid ~8.08 Å) with typical distal volume (~101 Å³) → space for substrate to reorient after first oxidation.
- **Phenotype & catalytic implication:** **Retention + reorientation** phenotype: hydrophobic/bulky proximal packing plus an outer region that doesn’t “kick out” product tends to promote **sequential oxidation (Di-Ox)**.
  - **Reaction support:** Highest S82 total yield (46.8) but **Di-Ox heavy** (Mono:Di 0.6), matching an “efficient but over-oxidizing” pocket.

---

## 2A) Intra-protein variant analysis (families with variants)

### CviUPO family: CviUPO (reference) vs CviUPO-F88L+T158A
Assumption: **CviUPO_S82_glide** is the WT/reference because it matches the reaction_data “CviUPO” label; the double mutant is explicitly labeled.

**Changes in structural dimensions (variant vs reference):**
- **(i) Prox electrostatics:** Polar_fraction decreases (0.385 → 0.308) and kd_weighted increases (~1.06 → ~1.40) → proximal environment becomes **less polar/more hydrophobic-leaning**.
- **(ii) Prox sterics:** Slightly reduced mean proximal volume (111 → 108 Å³) and increased small_residue_frac (0.154 → 0.231) with bulky fraction unchanged (0.615). Net: **a bit less “packed”/more compliant** locally.
- **(iii) Distal electrostatics:** Distal kd_weighted increases (0.39 → 0.73) with similar charge/polar fractions → distal becomes **less strongly polar-solvating** (more interaction-balanced).
- **(iv) Distal sterics / outer size:** Slight compaction (mean_dist_to_centroid 9.91 → 9.63 Å) with similar distal volume → **marginally tighter outer pocket**.

**Mechanistic rationale:**
- The standout functional lever is the **shorter reactive_center_distance** (7.72 → 5.83 Å), suggesting the mutant promotes a **more reactive near-attack geometry**. If that pose is productive, you’d expect improved peroxygenative efficiency (higher mono-oxygenation rate at lower residence time).
- The concurrent **drop in proximal polarity** could reduce “sticky” polar traps that hold nonproductive orientations, but it could also reduce pose-locking; the net effect likely depends on whether F88L/T158A reshapes the pocket to favor a single dominant productive pose.

---

## 2B) Requested pairwise comparison: **CviUPO vs ET096**

### CviUPO_S82_glide vs ET096_S82_glide
**(i) Prox electrostatics**
- **CviUPO is more polar/charged proximally** (charged 0.077; polar 0.385) vs ET096 (charged 0.0; polar 0.182).
- ET096 has higher kd_weighted (~2.18) than CviUPO (~1.06), but without charge/polar residues this likely reflects **non-ionic composition** rather than true cationic steering.
**Mechanistic read:** CviUPO can form **specific polar contacts** that constrain pose; ET096 is more “dry/neutral,” encouraging pose diversity.

**(ii) Prox sterics**
- CviUPO is **bulkier and tighter** (mean proximal volume 111 vs 88 Å³; bulky_frac 0.615 vs 0.273; median_min_dist 3.58 vs 4.33 Å).
- ET096 is **small-residue lined** (small_frac 0.636) and has a longer reactive_center_distance (7.10 vs 7.72 for CviUPO; both long, but ET096 also has larger median residue→reactive-center distance).
**Mechanistic read:** CviUPO’s bulky clamp favors **mono-selective, pose-locked oxygen transfer**; ET096’s smoother cavity favors **reorientation and over-oxidation**.

**(iii) Distal electrostatics**
- CviUPO distal is **more polar** (0.513 vs 0.368) and less “kd-weighted” (0.39 vs 0.97).
**Mechanistic read:** CviUPO’s distal polarity may better manage water/H2O2 organization and substrate ingress in a controlled way; ET096’s distal region is more neutral, supporting broader permissiveness.

**(iv) Distal sterics / outer pocket size**
- ET096 has a **more expanded outer pocket** (mean_dist_to_centroid 10.25 vs 9.91; mean_min_dist_to_centroid 8.57 vs 8.08).
**Mechanistic read:** ET096’s larger outer region supports **product retention/rebinding**, increasing Di-Ox.

**Functional consequence supported by reaction_data**
- **S82:** CviUPO is mono-selective (Mono:Di 1.7) while ET096 is strongly di-oxidizing (0.3). This matches **CviUPO = pose-locking clamp** vs **ET096 = permissive/open**.
- **ABTS:** CviUPO is far more peroxidative (3.939 vs 0.146), consistent with CviUPO’s more polar/charged pocket environment being better suited to electron-transfer substrates.

---

## 3) Cross-protein “pocket phenotypes” (clusters) and likely trade-offs

1) **Pose-locking / mono-selective clamp**
- **Members:** CviUPO, DcaUPO (partially; despite distal charge), possibly CviUPO-F88L+T158A.
- **Signature:** Higher proximal bulky fraction + higher proximal polarity/charge (or at least structured proximal packing) + closer residue contacts.
- **Trade-off:** Often **higher selectivity (mono)** but can reduce total yield if binding becomes too restrictive or product release is slow. Can still show strong peroxidation if distal/proximal electrostatics support ET (e.g., CviUPO, DcaUPO on ABTS).

2) **Permissive / open outer pocket oxidizer (di-oxidation prone)**
- **Members:** ET096, OA167, TE314.
- **Signature:** Lower proximal charge, weaker polar anchoring, and/or more open distal geometry (larger centroid distances) enabling **reorientation and sequential oxidation**.
- **Trade-off:** **Higher total turnover** on S82 (ET096/TE314/OA167 totals are high) but **lower mono selectivity** (Mono:Di < 1).

3) **“Reactive-approach optimized” variants (geometry-first tuning)**
- **Member:** CviUPO-F88L+T158A (structural signal).
- **Signature:** Shorter reactive_center_distance without dramatic global pocket expansion.
- **Trade-off:** Can increase peroxygenation efficiency **if** the enforced pose is productive; otherwise may increase off-pathway oxidation if polarity/sterics no longer uniquely define the reactive pose.

If you want, I can also (i) map the pocket_alignment_table positions onto these phenotypes (highlighting which aligned residues are likely acting as “clamp points” vs “funnel points”), and (ii) propose 2–3 concrete mutation ideas per phenotype to push mono-selectivity or suppress peroxidation.

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue-level mechanistic hypotheses
Below, each “position” is reported in **each protein’s own numbering** (as requested). I focus on sites that (i) are close to ligand in at least one structure and (ii) plausibly explain the **global phenotypes** in the structural summary (pose-locking clamp vs permissive/retentive pockets; distal charge effects).

### A. “Clamp / wall” positions that set **proximal sterics** (pose-locking vs permissive)

#### **Position ~88 (CviUPO 88 / ET096 103 / DcaUPO 86 / TE314 108 / OA167 104)**
- **Identities**
  - ET096 **I103**
  - CviUPO **F88** → variant **L88** (F88L)
  - DcaUPO **L86**
  - TE314 **I108**
  - OA167 **I104**
- **Substitution class**
  - Mostly **steric/aromaticity shift**: **F (bulky aromatic)** ↔ **I/L (bulky aliphatic)**.
- **Mechanistic consequence**
  - **CviUPO WT F88**: aromatic face can act as a **rigid “clamp jaw”** (π/edge packing) that *locks* substrate microposes—consistent with the summary’s **bulky, tight, polar inner clamp** and mono-selectivity.
  - **CviUPO F88L**: removes aromatic planarity while keeping bulk. This typically **reduces directional π-stacking constraints** and makes the wall more “greasy/compliant,” which can:
    - reduce over-specific pose trapping by aromatic contacts,
    - allow a **slightly different near-attack geometry** (consistent with the variant’s **shorter reactive_center_distance** in the summary),
    - but potentially increase pose degeneracy if polarity/other clamps don’t compensate.
- **Variant-specific contrast (CviUPO vs CviUPO-F88L+T158A)**
  - F88L specifically **de-aromatizes** a key clamp point: predicted to **weaken pose-locking specificity** while still maintaining steric occupancy. This matches the summary’s “same clamp, slightly de-bulky/polar-tuned” and could help explain why the variant can place the reactive center closer (less “aromatic docking” constraint, more aliphatic packing freedom).

---

#### **Position ~64 (CviUPO 64 / ET096 80 / DcaUPO 62 / TE314 84 / OA167 80)**
- **Identities**
  - ET096 **A80** (small)
  - CviUPO **L64** (bulky)
  - DcaUPO **F62** (very bulky aromatic)
  - TE314 **P84** (rigid, shape-defining)
  - OA167 **L80** (bulky)
- **Substitution class**
  - Strong **steric/shape** differences: **A (small)** ↔ **L/F/P (bulky/rigid)**.
- **Mechanistic consequence**
  - ET096 A80 supports the summary’s **“small, smooth inner pocket”** → fewer enforced contacts, more microposes, more di-oxidation/peroxidative throughput.
  - CviUPO L64 / DcaUPO F62 create a **thicker inner wall** near the ligand path, consistent with **tight clamp** behavior (CviUPO) and **structured hydrophobic proximal wall** (DcaUPO).
  - TE314 P84 can act as a **geometry gate** (rigid kink) without adding much polar anchoring—consistent with TE314’s “close approach but weaker mono-control”: you can get near-attack geometry, but not necessarily a uniquely constrained pose.
  - OA167 L80 contributes to **hydrophobic retention** (summary: hydrophobic/bulky proximal pocket → over-oxidation via retention/reorientation).

---

#### **Position ~174/161/157/186/177 (ET096 174 / CviUPO 161 / DcaUPO 157 / TE314 186 / OA167 177)**
- **Identities**
  - ET096 **L174**
  - CviUPO **G161**
  - DcaUPO **G157**
  - TE314 **G186**
  - OA167 **F177**
- **Substitution class**
  - **Steric gate**: **G (tiny)** ↔ **L/F (bulky)**.
- **Mechanistic consequence**
  - **Gly at this site (CviUPO/DcaUPO/TE314)** likely creates a **local “notch”/extra void** that can permit subtle ligand shifts or allow water/H2O2 organization—compatible with (i) CviUPO’s polar clamp (pose-locking comes from other bulky/polar points) and (ii) DcaUPO’s heterogeneous pocket (high variance).
  - **ET096 L174** fills that notch → paradoxically can still be “smooth” if surrounding residues are small; but it will **reduce local flexibility** and may bias substrate to sit slightly farther/with fewer microcavity options at that subsite.
  - **OA167 F177** is a strong **retention/stacking plug**: bulky aromatic occupancy promotes **tight hydrophobic packing** and product retention, consistent with OA167’s **over-oxidation (Di-Ox)** phenotype.

---

### B. Positions that drive **electrostatics / polarity** differences (proximal or distal steering)

#### **Position ~60 (CviUPO 60 / ET096 77 / DcaUPO 58 / TE314 80 / OA167 76)**
- **Identities**
  - ET096 **A77** (nonpolar)
  - CviUPO **T60** (polar OH)
  - DcaUPO **D58** (**negative**)
  - TE314 **T80** (polar)
  - OA167 **A76** (nonpolar)
- **Substitution class**
  - **Electrostatic/polarity**: A ↔ T (polarity), and notably **A/T ↔ D (charged)**.
- **Mechanistic consequence**
  - **DcaUPO D58** introduces a **localized negative electrostatic feature** near the pocket region sampled by the ligand (even if not the closest contact in the dock). This can:
    - stabilize/position polar substrate functionality,
    - influence **H2O2/water structuring** and proton-coupled steps,
    - and contribute to DcaUPO’s “mixed pathway propensity” (peroxygenation strong, but peroxidation-capable), by enabling **electrostatic organization** that supports ET chemistry for some substrates.
  - **CviUPO/TE314 Thr** supports the summary’s higher proximal polarity vs ET096/OA167, consistent with **more pose-locking potential** (CviUPO) or “moderately guided” binding (TE314).
  - **ET096/OA167 Ala** fits their more hydrophobic/neutral proximal character and higher pose heterogeneity/retention-driven di-oxidation.

---

#### **Position ~165/178/161/190/181 (CviUPO 165 / ET096 178 / DcaUPO 161 / TE314 190 / OA167 181)**
- **Identities**
  - ET096 **A178**
  - CviUPO **K165** (**positive**; very close in the variant: min dist ~1.4 Å reported)
  - DcaUPO **C161** (weakly polarizable, neutral)
  - TE314 **V190** (hydrophobic)
  - OA167 **A181** (small hydrophobic)
- **Substitution class**
  - Strong **electrostatic** difference: **K (cationic)** ↔ neutral (A/V/C).
- **Mechanistic consequence**
  - **CviUPO K165** is a plausible **major electrostatic “handle”** that can:
    - create a **polar/charged patch** consistent with CviUPO’s higher proximal polarity/charge,
    - reduce radical escape by **electrostatic caging** (stabilize developing charge/polar TS),
    - and/or bias substrate orientation via long-range field effects.
  - The extremely short contact reported for the variant suggests K165 may become an even more direct **pose-directing contact** in that model—potentially contributing to the variant’s **shorter reactive-center distance** (by pulling/positioning the ligand).
  - ET096/OA167/TE314 lacking this Lys supports their more neutral proximal electrostatics and greater pose freedom (ET096) or retention-driven over-oxidation (OA167).

---

### C. Positions that tune **outer-pocket retention / reorientation** (di-oxidation propensity)

#### **Position ~158 (CviUPO 158 / ET096 171 / DcaUPO 154 / TE314 183 / OA167 174)**
- **Identities**
  - ET096 **A171**
  - CviUPO **T158** → variant **A158** (T158A)
  - DcaUPO **F154** (bulky aromatic; close)
  - TE314 **V183**
  - OA167 **P174** (rigid)
- **Substitution class**
  - **Polarity + sterics**: T→A removes an OH (polarity loss); F/P introduce bulky/rigid shaping.
- **Mechanistic consequence**
  - **CviUPO T158A (variant)**: removes a potential H-bond donor/acceptor near the pocket, consistent with the summary’s **decreased proximal polar_fraction** and slightly more hydrophobic-leaning proximal environment. Mechanistically:
    - fewer polar “brakes” can reduce nonproductive sticking and allow the ligand to adopt the **closer near-attack geometry** observed in the variant,
    - but also can reduce pose discrimination, potentially increasing off-pathway orientations unless sterics compensate.
  - **DcaUPO F154** likely increases **retention and hydrophobic packing** at this outer/proximal boundary while still allowing close approach (DcaUPO has short reactive distance). This fits “high competence but mixed pathway propensity”: strong binding + ability to reorient can support sequential events depending on substrate.
  - **OA167 P174** can act as a **reorientation-enabling hinge/gate**: rigidly shapes the channel while not providing polar anchoring—consistent with OA167’s retention + open outer region → di-oxidation.

---

## 2) Ranked residue lists (mechanistic drivers vs modulators vs likely neutral)

### High-confidence mechanistic driver residues (most causal)
1. **CviUPO K165** (vs ET096 A178 / TE314 V190 / OA167 A181 / DcaUPO C161): dominant **electrostatic handle** consistent with CviUPO’s more polar/charged clamp phenotype; likely affects orientation/caging and peroxidase-capability.
2. **Clamp-wall position ~64** (ET096 A80 vs CviUPO L64 vs DcaUPO F62 vs TE314 P84 vs OA167 L80): major **steric shaping** that maps cleanly onto “small smooth” (ET096) vs “tight/bulky” (CviUPO/DcaUPO/OA167) vs “rigid but not clamping” (TE314).
3. **CviUPO 88 (F→L in variant)** / corresponding site (ET096 I103 etc.): key **aromatic-to-aliphatic** change that plausibly explains the variant’s altered geometry (shorter reactive-center distance) and reduced polarity/pose-locking specificity.

### Secondary modulators (context-dependent but plausible)
- **Position ~60** (DcaUPO D58 vs Thr/Ala): tunes **local polarity/charge** and water/H2O2 organization; may contribute to DcaUPO’s distal/proximal electrostatic behavior and mixed pathway propensity.
- **Position ~158** (CviUPO T158A; DcaUPO F154; OA167 P174): tunes **outer-pocket polarity/retention** and reorientation propensity (di-oxidation risk).
- **Position ~174/161/157/186/177** (Gly vs bulky L/F): local **gate/notch** controlling microcavity flexibility and retention (OA167 F177 especially).

### Likely neutral/background (in this dataset/context)
- **Position ~74/57/55/77/73** (ET096 V74; CviUPO/DcaUPO/TE314 L; OA167 T): mostly conservative hydrophobe/polar swap at relatively longer distances in most proteins; unlikely to dominate phenotype alone.
- **Positions ~159–160 and ~172–176 region (Ser/Thr/Tyr/Leu variants)**: appear mostly **distal (often >6 Å)** in these docked poses; may fine-tune solvation/packing but less likely to be primary drivers compared to the clamp/charge sites above.

If you want, I can convert the “driver” sites into **actionable mutation hypotheses** per scaffold (e.g., how to push ET096 toward mono-selective clamp behavior, or how to reduce OA167 di-oxidation by weakening retention) while staying consistent with the phenotypes in the summary.