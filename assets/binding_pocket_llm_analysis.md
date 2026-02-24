## Stage 1: Global Pocket Phenotypes

## Per-protein integrated interpretations (structure → mechanism → selectivity)

### ET096_S82_glide — **“Small, dry inner pocket; chemistry happens at arm’s length.”**
- **Proximal electrostatics:** Very low polarity/charge (charged_fraction **0.00**, polar_fraction **0.18**); high hydropathy (hw_weighted **−0.94**) and high KD (kd_weighted **2.18**) → a **hydrophobic, poorly H-bonding** near-field. Median residue→reactive-center distance **7.92 Å** suggests few residues directly “coach” the reactive geometry.
- **Proximal sterics:** Many small residues (small_residue_frac **0.64**) with modest mean volume (**88 Å³**) and 12 residues <6 Å; ligand closest approach median **4.33 Å** but reactive center sits relatively far (reactive_center_distance **7.10 Å**) → **roomy microcavity but weak pose-locking at the reactive atom**.
- **Distal electrostatics:** Slightly more polar/charged than proximal (charged **0.13**, polar **0.37**) but still overall hydrophobic (hw_weighted **−0.46**) → distal shell not strongly “electrostatic-funneling”.
- **Distal sterics / outer size:** Outer pocket is relatively extended (mean_dist_to_centroid distal **10.25 Å**; mean_min_dist_to_centroid **8.57 Å**) with moderate distal volumes (~**100 Å³**) → **open outer vestibule**.
- **Phenotype synthesis (with reaction data):** ET096 shows **high S82 di-oxidation** (Mono:Di **0.3**) and modest ABTS (**0.146**). The **hydrophobic, small-residue proximal set + long reactive-center distance** is consistent with **substrate mobility and repeated oxidation** (di-ox) rather than a single, well-registered peroxygenative event. The open distal region likely supports **re-binding/reshuffling**, enabling over-oxidation.

---

### CviUPO_S82_glide — **“Polar-and-bulky clamp near the ligand; tuned for single-hit outcomes.”**
- **Proximal electrostatics:** More polar/charged than ET096 (charged **0.077**, polar **0.385**); still hydrophobic overall (hw_weighted **−0.83**) but with **more H-bonding capacity** near-field. Median residue→reactive-center distance **6.68 Å** (closer than ET096) → better geometric “guidance”.
- **Proximal sterics:** Strongly bulky proximal composition (bulky_residue_frac **0.615**) with high mean volume (**111 Å³**); ligand closest approach median **3.58 Å** and 13 residues <6 Å → **tight, shape-complementary inner pocket** that can enforce a preferred pose.
- **Distal electrostatics:** Distal shell is quite polar (polar **0.513**) with modest charge (0.128) and relatively low KD (kd_weighted **0.387**) → **more hydrophilic outer environment** than ET096, potentially affecting access/solvent organization.
- **Distal sterics / outer size:** Distal centroid distances slightly smaller than ET096 (mean_dist_to_centroid **9.91 Å**, mean_min **8.08 Å**) → **somewhat more compact vestibule**.
- **Phenotype synthesis (with reaction data):** CviUPO has **very high ABTS** (**3.939**) yet S82 is **mono-oxidation biased** (Mono:Di **1.7**). A plausible reconciliation is: the **bulky/polar proximal clamp** favors **a single productive orientation** for S82 (mono), while the **polar/charged distal shell** may stabilize **electron-transfer competent states / solvent networks** that enhance **peroxidative turnover** (ABTS). Net: **selective mono-ox on S82 but strong peroxidase-like behavior on ABTS**.

---

### CviUPO-F88L+T158A_S82_chai1_0 — **“Same scaffold, slightly ‘de-bulky’ and closer to the reactive center.”**
*(Variant family analysis vs CviUPO reference is detailed below; here is the per-protein readout.)*
- **Proximal electrostatics:** Similar charge (charged **0.077**) but **lower polarity** than CviUPO (polar **0.308** vs 0.385); kd_weighted **1.40** (higher than CviUPO’s 1.06) → **more hydrophobic/less H-bonding** proximal field.
- **Proximal sterics:** Mean volume slightly down (**108 Å³**) and fewer residues <6 Å (**10** vs 13). Reactive center is **closer** (reactive_center_distance **5.83 Å**) → fewer contacts, but potentially **more direct access** to the oxidizing center.
- **Distal electrostatics:** Distal remains polar (polar **0.485**) with kd_weighted **0.73** → still relatively hydrophilic outer shell.
- **Distal sterics / outer size:** Distal centroid distances slightly smaller (mean_dist_to_centroid **9.63 Å**) and fewer aligned pocket residues (num_pocket_res_ali **33**) → could reflect **a somewhat simplified/less extensive pocket definition** in this model.
- **Phenotype synthesis:** Without reaction data for this variant, the structural shift suggests a pocket that is **less pose-locking** (fewer <6 Å contacts) but places the reactive center **closer**, which can increase raw reactivity yet risk **less controlled selectivity** depending on substrate.

---

### DcaUPO_S82_glide — **“Reactive-center proximity with a charged outer ring: high activity, mixed pathway pressure.”**
- **Proximal electrostatics:** Low proximal polarity (polar **0.154**) with some charge (0.077); very hydrophobic proximal field (hw_weighted **−1.04**) and high KD (kd_weighted **1.79**) → **nonpolar inner cavity**.
- **Proximal sterics:** Many residues <6 Å (**15**, highest here) and bulky proximal fraction **0.615** with high variance (**1183**) → **tight but heterogeneous** inner pocket; reactive center is close (reactive_center_distance **4.93 Å**) → supports **productive HAT/O-transfer geometry**.
- **Distal electrostatics:** Distal is the **most charged** set (charged **0.20**) with moderate polarity (0.40) → a **charged outer shell** that can influence peroxide/water organization and substrate ingress.
- **Distal sterics / outer size:** Distal centroid distances similar to others (mean_dist_to_centroid **10.00 Å**) with moderate volumes (~**104 Å³**).
- **Phenotype synthesis (with reaction data):** DcaUPO is **high on peroxygenative probes** (Veratryl alcohol **1.558**, NBD **1.242**) but also **high ABTS** (**2.7**); S82 is **mono-biased** (Mono:Di **1.6**). The **short reactive-center distance + many close contacts** fits strong peroxygenation. The **charged distal shell** plausibly promotes **peroxidative competence** (ABTS) by stabilizing ET/solvent networks—yielding a **high-activity, less pathway-exclusive** phenotype.

---

### TE314_S82_chai1_0 — **“Balanced pocket: neither clamp nor cavern, tends toward over-oxidation.”**
- **Proximal electrostatics:** No proximal charge (0.00) and moderate polarity (0.308); kd_weighted **1.82**, hw_weighted **−0.89** → **hydrophobic but not extremely**.
- **Proximal sterics:** Mean volume lower (**98.5 Å³**) with moderate bulky fraction (0.308) and 12 residues <6 Å; reactive center very close (**4.08 Å**) but median residue→reactive-center distance is high (**8.21 Å**) → suggests **a close approach exists but not broadly supported by many residues** (less “caging”).
- **Distal electrostatics:** Distal is fairly hydrophobic (hw_weighted **−0.63**) with kd_weighted **1.43** → **less polar outer shell** than CviUPO/DcaUPO.
- **Distal sterics / outer size:** Distal centroid distances are on the smaller side (mean_dist_to_centroid **9.73 Å**) with relatively low proximal variance (**559**) → **more uniform pocket**.
- **Phenotype synthesis (with reaction data):** S82 Mono:Di **0.7** (di-ox favored). A **less polar, less bulky proximal environment** plus a **not-strongly-structured distal shell** is consistent with **substrate reorientation/rebinding**, enabling sequential oxidation.

---

### OA167_S82_swissdock_0 — **“Bulky hydrophobic inner wall with a permissive vestibule: high total turnover, modest control.”**
- **Proximal electrostatics:** No proximal charge (0.00) but moderate polarity (0.308); very hydrophobic proximal field (hw_weighted **−1.36**, most negative here) with kd_weighted **1.41** → **strongly nonpolar inner pocket**.
- **Proximal sterics:** Bulky proximal fraction **0.538** with high mean volume (**108.5 Å³**) and only 10 residues <6 Å → **hydrophobic packing** but fewer close “steering” contacts; reactive center close (**4.55 Å**).
- **Distal electrostatics:** Distal moderately polar (0.40) and mildly hydrophobic (hw_weighted **−0.67**) → outer shell not strongly charged/polar.
- **Distal sterics / outer size:** Distal centroid distances ~**9.74 Å** (moderate) with typical distal volume (~**101 Å³**) → **reasonably open outer pocket**.
- **Phenotype synthesis (with reaction data):** Highest S82 total yield (**46.8%**) but Mono:Di **0.6** (di-ox favored). This matches a **hydrophobic, permissive pocket** that supports binding/turnover but allows **multiple productive poses over time**, increasing total conversion while sacrificing mono-selectivity.

---

## 2A) Intra-protein variant analysis (families with variants)

### Family: **CviUPO** (reference: **CviUPO_S82_glide**; variant: **CviUPO-F88L+T158A_S82_chai1_0**)  
Assumption: CviUPO_S82_glide is the closest “WT/reference” because it is the unmutated label and shares the same base name.

**Variant vs reference — what changed?**
- **(i) Proximal electrostatics:** **Less polar / more hydrophobic** in variant (polar_fraction **0.385 → 0.308**; kd_weighted **1.06 → 1.40**). Likely reduces H-bond anchoring and increases pose degeneracy.
- **(ii) Proximal sterics:** Slightly **less crowded** (num_pocket_res<6 **13 → 10**) and slightly smaller mean volume (**111 → 108 Å³**), but **reactive center gets closer** (**7.72 → 5.83 Å**). Mechanistically: fewer near contacts can reduce “clamping”, while shorter reactive distance can increase intrinsic oxidation probability once bound.
- **(iii) Distal electrostatics:** Distal becomes **less hydrophilic** (polar **0.513 → 0.485**; kd_weighted **0.387 → 0.73**). This could weaken distal solvent structuring that supports peroxidative ET networks (ABTS-like behavior), potentially shifting balance toward peroxygenation *if* proximal geometry remains productive.
- **(iv) Distal sterics / outer size:** Slightly **more compact** (mean_dist_to_centroid **9.91 → 9.63 Å**) and fewer aligned residues (**39 → 33**), consistent with a subtly altered vestibule definition/shape in the model.

**Mechanistic expectation:** F88L+T158A trends toward a **more hydrophobic, less H-bond-directed pocket** with **more direct access** to the reactive center but **less pose-locking**. For substrates where regio-/stereocontrol depends on tight anchoring, expect **reduced selectivity**; for substrates limited by approach distance, expect **maintained or increased turnover**.

---

## 2B) Requested pairwise comparison: **CviUPO vs ET096**

### CviUPO_S82_glide **vs** ET096_S82_glide
- **Proximal electrostatics:** CviUPO is **much more polar/charged** near the ligand (polar **0.385 vs 0.182**; charged **0.077 vs 0.00**) and has lower KD (kd_weighted **1.06 vs 2.18**) → **better capacity to orient/polarize substrate** and stabilize specific binding modes.
- **Proximal sterics:** CviUPO is **bulkier and tighter** (bulky **0.615 vs 0.273**; mean_volume **111 vs 88 Å³**; median_min_dist **3.58 vs 4.33 Å**) → stronger **shape complementarity/pose restriction**. ET096 has many small residues (small **0.64**) → more “slippery” cavity.
- **Distal electrostatics:** CviUPO distal shell is **more polar** (polar **0.513 vs 0.368**) and less hydrophobic (hw_weighted **−0.48 vs −0.46**, similar) but notably lower KD (kd_weighted **0.387 vs 0.967**) → **more hydrophilic vestibule** in CviUPO.
- **Distal sterics / outer size:** ET096 is **more extended/open** distally (mean_dist_to_centroid **10.25 vs 9.91 Å**; mean_min_dist **8.57 vs 8.08 Å**) → easier access and potentially more re-binding/reorientation.

**Mechanistic rationale tied to reaction data:**
- ET096’s **open, hydrophobic, small-residue proximal pocket** aligns with **di-oxidation dominance on S82** (Mono:Di **0.3**)—substrate can reorient and get hit multiple times.
- CviUPO’s **polar + bulky proximal clamp** aligns with **mono-oxidation bias** (Mono:Di **1.7**) by enforcing a preferred pose and limiting over-oxidation.
- CviUPO’s **high ABTS** (3.939 vs 0.146) is consistent with its **more polar/charged pocket environment** (proximal and distal), which can support **peroxidative electron-transfer chemistry** and/or stabilize reactive intermediates/solvent networks relative to ET096’s “dry” pocket.

---

## 3) Cross-protein “pocket phenotypes” (recurring archetypes → turnover/selectivity trade-offs)

### Phenotype 1: **Hydrophobic–permissive cavities (mobility → over-oxidation)**
- **Members:** ET096, TE314, OA167 (strongest in ET096/OA167 by proximal hydropathy and/or low proximal charge).
- **Signature:** Low proximal charge, relatively hydrophobic hw_weighted, fewer polar anchors; often more open distal geometry.
- **Functional tendency:** Higher likelihood of **multiple binding poses and sequential oxidation** → **lower mono-selectivity (lower Mono:Di)** but can give **high total conversion** (OA167).

### Phenotype 2: **Bulky/polar pose-locking inner pockets (control → mono-selectivity)**
- **Members:** CviUPO, DcaUPO (both have high bulky proximal fraction; CviUPO has highest proximal polarity).
- **Signature:** High bulky_residue_frac proximal, closer median_min_dist to ligand, and increased proximal polarity/charge.
- **Functional tendency:** Better **regio-/chemoselective “single-hit” outcomes** on S82 (higher Mono:Di), but can still support peroxidation if distal shell is polar/charged (CviUPO, DcaUPO high ABTS).

### Phenotype 3: **Charged distal shell “peroxidation enabler”**
- **Members:** DcaUPO (charged distal **0.20**), CviUPO (high distal polarity).
- **Signature:** Elevated distal charge/polarity with relatively hydrophilic KD.
- **Functional tendency:** Promotes **peroxidative competence** (ABTS) by stabilizing ET/solvent organization, sometimes at the cost of pathway exclusivity (DcaUPO: high peroxygenation *and* high ABTS).

If you want, I can also (i) map the pocket_alignment_table positions onto these phenotypes (which specific aligned sites are likely “gatekeepers”), and (ii) propose 2–3 mutation ideas per phenotype to push toward mono-selective peroxygenation vs peroxidation suppression.

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue-level mechanistic hypotheses
(Positions are given in each protein’s **own numbering** as requested; I refer back to the earlier pocket phenotypes: **ET096/TE314/OA167 = hydrophobic–permissive/over-oxidation**, **CviUPO/DcaUPO = bulky/polar clamp/mono-bias**, **DcaUPO/CviUPO distal polarity/charge = peroxidation enabler**.)

### A. “Clamp vs permissive wall” near the ligand: **CviUPO 88 / ET096 103 / DcaUPO 86 / TE314 108 / OA167 104**
- **Identities**
  - ET096 **I103**
  - CviUPO **F88** → variant **L88** (F88L)
  - DcaUPO **L86**
  - TE314 **I108**
  - OA167 **I104**
- **Substitution class**
  - **Steric/aromaticity shift:** F ↔ (I/L). Phenylalanine is bulkier and π-capable; Leu/Ile are smaller, purely aliphatic.
  - **Polarity:** all hydrophobic; main change is **shape + π interactions**, not charge.
- **Mechanistic consequence**
  - **CviUPO F88** is a classic **pose-locking “clamp” element**: aromatic face can pack against hydrophobic substrate and reduce pose degeneracy → consistent with CviUPO’s **bulky/polar clamp** phenotype and **mono-oxidation bias** (Mono:Di 1.7).
  - **F88L (variant)** removes π-stacking and slightly reduces sidechain volume → **weakens clamping**, increases microcavity “slipperiness,” matching the summary: **fewer <6 Å contacts** and **lower proximal polarity** → predicted **reduced selectivity / more reorientation**, even if reactive-center access improves.
- **Within-family contrast (CviUPO vs F88L+T158A)**
  - **F88→L88** specifically “de-aromatizes” the clamp: expect **less enforced substrate orientation** (more trajectories that still reach the oxidant), aligning with the variant’s “less pose-locking” description.

**Confidence:** High (directly matches “bulky clamp” vs “de-bulky” narrative and is a large physicochemical change at a proximal site).

---

### B. “Electrostatic gate / distal-shell charge injector”: **CviUPO 165 / ET096 178 / DcaUPO 161 / TE314 190 / OA167 181**
- **Identities**
  - ET096 **A178**
  - CviUPO **K165** (also **K165** in variant)
  - DcaUPO **C161**
  - TE314 **V190**
  - OA167 **A181**
- **Substitution class**
  - **Electrostatic:** Lys (**+1**) vs A/V/C (neutral). This is the strongest explicit charge difference in the table.
  - **Steric:** K is also longer/bulkier than A/V/C.
- **Mechanistic consequence**
  - **CviUPO K165** can create a **local positive electrostatic patch** that:
    - stabilizes/organizes **water/peroxide networks** and polar transition states (supporting the earlier “polar/charged environment → ABTS competence”),
    - can **electrostatically steer** polar substrate moieties or constrain approach vectors (a “soft gate”).
  - In **ET096/TE314/OA167** (A/V/A) the same region is **electrostatically silent**, consistent with their more “dry/permissive” phenotypes and greater tendency toward **reorientation → di-oxidation**.
  - **DcaUPO C161** is neutral but polarizable; it won’t replicate the strong distal/proximal electrostatic steering of Lys—consistent with DcaUPO’s distal charge being distributed elsewhere (summary: **charged distal shell** overall), not necessarily at this exact site.
- **Within-family contrast**
  - No change between CviUPO and its variant at 165, so **K165 likely preserves** part of CviUPO’s electrostatic “peroxidation-enabling” character even as F88L/T158A reduce pose-locking/polar anchoring elsewhere.

**Confidence:** High for electrostatics/pathway bias (charged vs neutral at pocket edge is a canonical driver).

---

### C. “Hydrogen-bond anchor vs hydrophobic release” at the T158A mutation site: **CviUPO 158 / ET096 171 / DcaUPO 154 / TE314 183 / OA167 174**
- **Identities**
  - ET096 **A171**
  - CviUPO **T158** → variant **A158** (T158A)
  - DcaUPO **F154**
  - TE314 **V183**
  - OA167 **P174**
- **Substitution class**
  - **Polarity/H-bonding:** Thr (polar, H-bond donor/acceptor) → Ala (nonpolar).
  - **Steric:** small-to-small (minor volume change), but **loss of hydroxyl** is major chemically.
- **Mechanistic consequence**
  - In **CviUPO (T158)**: provides a **specific H-bonding handle** that can “register” substrate orientation and/or stabilize a local water network → consistent with the **polar proximal clamp** phenotype and mono-selectivity.
  - **T158A (variant)** removes that anchor → **reduced H-bond-directed positioning**, increased pose degeneracy and potentially increased radical/oxygen rebound variability. This directly matches the summary: variant becomes **less polar / more hydrophobic** and **less pose-locking**.
  - Cross-protein context: ET096 already has **A171** (no anchor) and shows **di-oxidation dominance**; T158A pushes CviUPO **toward the ET096-like “dry/permissive” behavior**.
- **Within-family contrast**
  - This is the cleanest causal link to the variant’s reported **polarity drop** (0.385 → 0.308): **T158A is a primary driver** of that shift.

**Confidence:** High (directly changes H-bond capacity at a pocket residue and aligns with the observed phenotype shift).

---

### D. “Bulky plug vs small hinge” controlling local crowding: **ET096 80 / CviUPO 64 / DcaUPO 62 / TE314 84 / OA167 80**
- **Identities**
  - ET096 **A80**
  - CviUPO **L64**
  - DcaUPO **F62**
  - TE314 **P84**
  - OA167 **L80**
- **Substitution class**
  - **Steric:** A (small) ↔ L/P (medium) ↔ F (bulky aromatic).
  - **Polarity:** all largely nonpolar (Pro is nonpolar but conformationally special).
- **Mechanistic consequence**
  - **ET096 A80** contributes to the “small-residue proximal set” → **roomier microcavity**, weaker caging → consistent with **substrate mobility and di-oxidation**.
  - **DcaUPO F62** is a **bulky plug** that can tighten the inner pocket and enforce approach geometry (fits DcaUPO’s **many <6 Å contacts** and close reactive center).
  - **TE314 P84** can rigidify a loop/turn and shape the pocket wall; proline often acts as a **conformational gate** (less about volume, more about fixing backbone geometry), potentially explaining TE314’s “close approach exists but not broadly supported” (a localized gate rather than a global clamp).

**Confidence:** Medium-high (strong steric differences; exact effect depends on sidechain orientation/backbone context).

---

### E. “Charge/polarity hotspot” at a near-ligand position: **ET096 77 / CviUPO 60 / DcaUPO 58 / TE314 80 / OA167 76**
- **Identities**
  - ET096 **A77**
  - CviUPO **T60** (variant also T60)
  - DcaUPO **D58**
  - TE314 **T80**
  - OA167 **A76**
- **Substitution class**
  - **Electrostatic:** D (−1) vs A/T (neutral).
  - **Polarity:** T is polar; A is nonpolar.
- **Mechanistic consequence**
  - **DcaUPO D58** introduces a **fixed negative charge** near the pocket that can:
    - stabilize cationic/polar substrate features,
    - tune local protonation/water structure, potentially supporting DcaUPO’s **mixed peroxygenation + peroxidation pressure** (summary: charged distal shell; this is one concrete contributor).
  - ET096/OA167 (A) lack this, consistent with “dry” permissive cavities.
  - CviUPO/TE314 (T) provide **H-bonding without full charge**, consistent with intermediate polarity.

**Confidence:** Medium (clear electrostatic difference, but distances here are somewhat larger in some structures; still within the filtered pocket set).

---

## 2) Ranked residue list (mechanistic drivers vs modulators vs neutral)

### High-confidence mechanistic driver residues
1. **CviUPO K165** (vs ET096 A178 / TE314 V190 / OA167 A181 / DcaUPO C161): **charge-based electrostatic gating/solvent organization** → ties to CviUPO/DcaUPO peroxidation competence vs ET096-like dryness.
2. **CviUPO T158A (variant)** at **158**: **loss of H-bond anchor** → directly explains variant’s **reduced proximal polarity** and predicted **reduced pose-locking/selectivity**.
3. **CviUPO F88L (variant)** at **88**: **aromatic clamp removal** → reduces shape/π complementarity, increasing pose degeneracy (variant shift toward permissive behavior).

### Secondary modulators (steric shaping; context-dependent)
- **ET096 A80 / CviUPO L64 / DcaUPO F62 / TE314 P84 / OA167 L80**: steric “plug/hinge” controlling local crowding and backbone rigidity.
- **DcaUPO D58** (vs A/T): localized **negative electrostatic feature** that can bias binding/solvent structure.
- **ET096 V74 / OA167 T73 / others L**: small polarity tweak (Thr vs hydrophobe) likely modulates hydration/entry but less decisive alone.

### Likely neutral/background (in this dataset; weaker causal leverage)
- Positions dominated by conservative hydrophobes with similar size and no charge change, e.g. **ET096 223 F vs others M/L/V/I** (mostly hydrophobic packing differences), and **ET096 172/173 region (S/A vs S/T/Y/L)** which are relatively distal in the provided distances and may not strongly control the reactive geometry unless they line the access channel in a specific structure.

If you want, I can convert these into **testable mutation hypotheses** (e.g., “make ET096 more mono-selective by introducing a Thr/Lys at the K165-equivalent site + adding an aromatic clamp at the F88-equivalent site”) while keeping each proposal consistent with the phenotypes you summarized.