## Stage 1: Global Pocket Phenotypes

## Per-protein interpretations (proximal <6 Å; distal ~6–11 Å)

### ET096 — *“Small, dry inner pocket; big output but leaky selectivity.”*
- **Proximal electrostatics:** Essentially **uncharged** (charged_fraction 0.0) and **low polar** (0.182) with **high hydrophobicity** (hw_weighted −0.94) → weak pose-locking by H-bonds/salt bridges; favors non-specific hydrophobic binding.
- **Proximal sterics:** **Many small residues** (small_residue_frac 0.636) and **lower mean volume** (88 Å³) → a *compliant* inner pocket that can admit multiple poses. Reactive center is **moderately far** (reactive_center_distance 7.10 Å) despite decent closest contacts (median_min_dist 4.33 Å).
- **Distal electrostatics:** Distal shell is **mildly polar/charged** (polar 0.368; charged 0.132) but still not strongly ionic; kd_weighted 0.967 suggests moderate polarity overall.
- **Distal sterics / outer size:** Distal centroid distances are among the **largest** (mean_dist_to_centroid 10.25 Å; mean_min_dist_to_centroid 8.57 Å) → a more open outer vestibule that can feed substrate in multiple orientations.
- **Phenotype & catalytic implication:** “Open-feed + non-polar inner pocket” tends to increase throughput but reduce control of the reactive approach geometry → consistent with **high total S82 conversion (41.1%)** but **peroxidation-biased over-oxidation** (**Mono:Di 0.3**, strong Di-Ox). ABTS is low (0.146), suggesting the peroxidative pathway here is more about *poor geometric control near Cpd I* than a strongly electron-transfer-friendly charged pocket.

---

### CviUPO — *“Polar, bulky clamp: pose-locking that boosts mono-oxidation and peroxidase-like ET.”*
- **Proximal electrostatics:** **More polar and some charge** (polar 0.385; charged 0.077) with still-hydrophobic character (hw_weighted −0.825). This mixed environment can stabilize a productive binding pose while still accommodating hydrophobic substrate faces.
- **Proximal sterics:** **Bulky-rich inner pocket** (bulky_residue_frac 0.615; mean_volume 111 Å³) with **tight closest approach** (median_min_dist 3.58 Å) → a “clamp” that can enforce a specific reactive presentation even if the reactive center distance is not minimal (7.72 Å).
- **Distal electrostatics:** Distal region is **quite polar** (polar 0.513) with moderate charge (0.128) but **overall less polar by kd** (kd_weighted 0.387) → suggests polarity is present but arranged in a way that may not strongly solvate; could support ET networks without making the pocket globally hydrophilic.
- **Distal sterics / outer size:** Outer pocket is **somewhat more compact** than ET096 (mean_dist_to_centroid 9.91; mean_min_dist_to_centroid 8.08), potentially reducing “wrong-way” entry trajectories.
- **Phenotype & catalytic implication:** A **pose-locking, polar/bulky proximal shell** tends to favor **selective peroxygenation** (productive rebound) over uncontrolled secondary oxidation. Matches **Mono:Di 1.7** (mono favored) and decent peroxygenation on NBD (0.169). However, **very high ABTS (3.939)** indicates this pocket/environment also supports **peroxidative electron transfer** (likely via polar/charged residues enabling ET access/positioning), i.e., it can be both pose-locking *and* peroxidase-competent.

---

### CviUPO-F88L+T158A — *“De-aromatized clamp: closer chemistry, slightly less polar guidance.”*  
(Variant of CviUPO; no reaction data provided for this construct.)
- **Proximal electrostatics:** Similar charge (0.077) but **lower polar fraction** than CviUPO (0.308 vs 0.385) and **higher kd_weighted** (1.40 vs 1.06) → net effect: less H-bonding “guidance,” slightly more polarizable/less hydrophobic mix by kd.
- **Proximal sterics:** Still **bulky-dominated** (bulky 0.615) but with **fewer proximal residues** (num_pocket_res<6 = 10 vs 13) and **reactive center brought closer** (reactive_center_distance 5.83 vs 7.72) → potentially more reactive geometry if the pose is productive.
- **Distal electrostatics:** Distal polarity remains high-ish (polar 0.485) but **kd_weighted increases** (0.73 vs 0.387) → distal becomes “more polar” by this metric, possibly altering access/solvent coupling.
- **Distal sterics / outer size:** Slightly **more compact** outer shell (mean_dist_to_centroid 9.63 vs 9.91) with similar volumes.
- **Phenotype & catalytic implication:** Removing an aromatic at 88 (F→L) plus T158A likely **reduces π-stacking/anchoring** and **reduces local H-bond capacity**, while the geometry suggests **easier close approach** to the reactive center. Mechanistically, this often trades *selectivity/pose-locking* for *reactivity* (more poses can reach “close enough”), which can either increase turnover or increase off-pathway oxidation depending on how the remaining clamp residues constrain orientation.

---

### DcaUPO — *“Charged outer ring + hydrophobic inner wall: strong oxidant delivery with controlled mono-oxidation.”*
- **Proximal electrostatics:** **Very low polar proximal** (0.154) with some charge (0.077) and **very hydrophobic** (hw_weighted −1.042) → inner pocket is “dry” and rebound-friendly once substrate is positioned.
- **Proximal sterics:** Bulky-rich (bulky 0.615) with **largest proximal variance** (volume_variance 1183) → heterogeneous wall: some tight blocking features plus some voids. **Reactive center is close** (4.93 Å), supporting efficient HAT/oxygen rebound when aligned.
- **Distal electrostatics:** **Highest distal charge** among the set (charged 0.20) with moderate polarity (polar 0.40) → distal shell can support **substrate pre-orientation, gating, and/or ET pathways**.
- **Distal sterics / outer size:** Outer size is mid-to-open (mean_dist_to_centroid 10.00; mean_min_dist_to_centroid 8.20), not as open as ET096 but not tight.
- **Phenotype & catalytic implication:** This “**charged vestibule + hydrophobic reactive core**” is a classic architecture for strong peroxygenation: distal residues help steer/activate binding while the proximal dry wall favors productive rebound over solvent-mediated side reactions. Consistent with **high peroxygenation on veratryl alcohol (1.558) and NBD (1.242)** and **Mono:Di 1.6** (mono favored). ABTS is also high (2.7), implying the distal charged network may also facilitate peroxidative ET—yet the S82 outcome suggests the pocket still maintains good control against over-oxidation.

---

### TE314 — *“Balanced pocket: neither tight nor guiding—mixed outcomes.”*
- **Proximal electrostatics:** Uncharged (0.0) but **moderately polar** (0.308) with hydrophobicity (hw_weighted −0.894) → some H-bonding possible but no strong ionic steering.
- **Proximal sterics:** More **medium-sized / less bulky** than CviUPO/DcaUPO (bulky 0.308; mean_volume 98.5) with **close reactive center** (4.08 Å) → can be reactive, but may not enforce a single dominant pose.
- **Distal electrostatics:** Distal is modestly polar (0.371) and low charge (0.114); kd_weighted 1.428 suggests a more polar distal environment by that metric.
- **Distal sterics / outer size:** Distal centroid distances are on the **compact side** (mean_dist_to_centroid 9.73; mean_min_dist_to_centroid 7.86) → less vestibule freedom than ET096.
- **Phenotype & catalytic implication:** “Moderate guidance + moderate openness” often yields **mixed selectivity**. Reaction data agrees: **Mono:Di 0.7** (still Di significant) with **good total yield (36.5%)**—suggesting decent turnover but incomplete suppression of secondary oxidation.

---

### OA167 — *“Hydrophobic, bulky inner pocket with an open-ish vestibule: high conversion, over-oxidation prone.”*
- **Proximal electrostatics:** Uncharged (0.0) with moderate polar (0.308) but **very hydrophobic** (hw_weighted −1.359; most negative here) → strongly nonpolar reactive environment.
- **Proximal sterics:** **Bulky proximal wall** (bulky 0.538; weighted_mean_volume 111) with **tight closest approach** (median_min_dist 3.60) and **reactive center close** (4.55 Å) → can drive fast chemistry once bound.
- **Distal electrostatics:** Distal modest polarity/charge (polar 0.40; charged 0.114) with kd_weighted 1.03.
- **Distal sterics / outer size:** Outer pocket is mid-sized (mean_dist_to_centroid 9.74; mean_min_dist_to_centroid 8.08), not extremely open.
- **Phenotype & catalytic implication:** A **very hydrophobic proximal pocket** can increase binding of hydrophobic substrates and accelerate rebound, but if it lacks polar “brakes” to enforce a single productive pose, it can promote **repeat binding/over-oxidation**. Consistent with **highest S82 total yield (46.8%)** but **Mono:Di 0.6** (Di substantial).

---

## 2A) Intra-protein variant analysis (families with variants)

### CviUPO family: CviUPO (reference) vs CviUPO-F88L+T158A
Assumption: **CviUPO_S82_glide** is the WT/reference for the **CviUPO-F88L+T158A** variant.

**(i) Proximal electrostatics changed**
- Polar fraction **decreases** (0.385 → 0.308); kd_weighted **increases** (1.055 → 1.40).
- Mechanistic read: fewer/less optimally placed H-bond donors/acceptors near the ligand can **weaken pose-locking**, increasing pose diversity (risking peroxidative/over-oxidation routes) unless sterics compensate.

**(ii) Proximal sterics changed**
- num_pocket_res<6 **drops** (13 → 10) and reactive_center_distance **drops strongly** (7.72 → 5.83).
- Mechanistic read: fewer close-contact residues but closer reactive approach suggests **a more open “direct line” to Cpd I**—often increases intrinsic reactivity, but can also allow **non-ideal attack vectors**.

**(iii) Distal electrostatics changed**
- kd_weighted distal **increases** (0.387 → 0.73) with similar charged fraction.
- Mechanistic read: distal environment may become more polar/solvent-coupled, potentially shifting the balance toward **ET-competent (peroxidative) behavior** if it improves access for redox mediators/substrates.

**(iv) Distal sterics / outer pocket size changed**
- Slight compaction (mean_dist_to_centroid 9.91 → 9.63) and fewer aligned pocket residues (39 → 33).
- Mechanistic read: subtle reshaping/gating differences could alter substrate entry trajectories and residence time, influencing whether the enzyme favors **single-hit mono-oxidation** vs **multiple-hit** outcomes.

---

## 2B) Requested pairwise comparison: **CviUPO vs ET096**

**Proximal electrostatics**
- **CviUPO is more polar/charged** (polar 0.385; charged 0.077) vs **ET096 is dry/uncharged** (polar 0.182; charged 0.0).
- Mechanistic implication: CviUPO should **better orient/lock** S82-like substrates (favoring productive peroxygenation), while ET096 allows **more pose degeneracy**.

**Proximal sterics**
- CviUPO has a **bulkier, larger proximal wall** (mean_volume 111; bulky 0.615) and **tighter closest approach** (3.58 Å) vs ET096’s **small-residue-rich** inner pocket (small 0.636; mean_volume 88).
- Mechanistic implication: CviUPO’s “clamp” promotes **mono-selectivity**; ET096’s compliant pocket promotes **over-oxidation** via re-binding and multiple accessible reactive poses.

**Distal electrostatics**
- CviUPO distal is **more polar by fraction** (0.513 vs 0.368) but **less polar by kd_weighted** (0.387 vs 0.967).
- Mechanistic implication: CviUPO likely has **structured polarity** (specific polar residues positioned for interactions/ET), whereas ET096 has a more **diffuse** polar character.

**Distal sterics / outer pocket size**
- ET096 is **more open** (mean_dist_to_centroid 10.25; mean_min_dist_to_centroid 8.57) than CviUPO (9.91; 8.08).
- Mechanistic implication: ET096’s larger vestibule increases **access and throughput** but reduces **trajectory control**, consistent with **higher total S82 yield** but **much lower Mono:Di (0.3)**.

**Reaction-data consistency**
- **CviUPO:** Mono:Di **1.7** (mono favored) + ABTS **3.939** (strong peroxidation) → selective mono-oxygenation *and* strong ET capability.
- **ET096:** Mono:Di **0.3** (Di dominates) + ABTS **0.146** → over-oxidation likely driven by **geometric looseness** rather than a highly ET-optimized peroxidase pocket.

---

## 3) Cross-protein “pocket phenotypes” (clusters) and functional trade-offs

1) **Open vestibule + small-residue proximal (“throughput, low control”)**
- Representative: **ET096**
- Signature: large distal centroid distances + proximal small-residue enrichment + low proximal polarity/charge.
- Behavior: **high conversion**, but **over-oxidation/peroxidative leakage** via multiple binding poses and easy re-entry.

2) **Bulky/polar proximal clamp (“pose-locking mono-selective”)**
- Representative: **CviUPO** (and partially DcaUPO)
- Signature: high proximal bulky fraction + elevated proximal polarity/charge.
- Behavior: improved **mono-selectivity** (higher Mono:Di), but can still show **high ABTS** if distal networks support ET.

3) **Charged distal vestibule + hydrophobic reactive core (“steered peroxygenation with strong activity”)**
- Representative: **DcaUPO**
- Signature: high distal charged fraction with a dry/hydrophobic proximal wall and close reactive center.
- Behavior: strong **peroxygenative activity** (veratryl alcohol, NBD) with **mono favored**, while retaining some peroxidative competence.

4) **Hydrophobic bulky core without strong electrostatic guidance (“fast but re-oxidation prone”)**
- Representative: **OA167** (and to a lesser extent TE314)
- Signature: very hydrophobic proximal (very negative hw_weighted) + bulky wall, but limited ionic/polar steering.
- Behavior: **high total yield** but **Mono:Di < 1** due to repeated oxidation cycles.

If you want, I can also (i) map the **pocket_alignment_table** positions onto these phenotypes (identify which aligned sites are likely “clamp” vs “vestibule charge” determinants), and (ii) propose 2–3 concrete mutation ideas per phenotype to push mono-selectivity up without sacrificing total yield.

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue chemistry → mechanistic consequences  
(Positions are given in **each protein’s own numbering**; effects are tied back to the pocket phenotypes in the structural summary.)

### A. **CviUPO 88 / ET096 103 / DcaUPO 86 / TE314 108 / OA167 104**  *(“aromatic clamp” position; proximal wall/pose-locking)*
- **Residues**
  - **ET096 I103**, **TE314 I108**, **OA167 I104** (bulky aliphatic, hydrophobic)
  - **DcaUPO L86** (slightly smaller aliphatic)
  - **CviUPO F88** (bulky aromatic)
  - **Variant:** **CviUPO-F88L+T158A has L88** (de-aromatized)
- **Substitution class**
  - **Steric/shape + π-character shift:** F ↔ I/L (aromatic → aliphatic); also a **polarity shift** (loss of aromatic quadrupole/π surface).
- **Mechanistic consequence**
  - **CviUPO F88** plausibly contributes to the **“bulky clamp”** phenotype: an aromatic face can **buttress a single productive pose** (π/CH–π contacts, flatter wall), consistent with **mono-selective pose-locking** described for CviUPO.
  - **ET096/TE314/OA167 I at this site** keeps hydrophobic bulk but **removes π-anchoring**, which tends to **increase pose degeneracy** (fits ET096 “compliant inner pocket” and OA167 “hydrophobic but not guiding”).
- **Intra-family contrast (CviUPO → F88L variant)**
  - **F88L** removes π-stacking/planar packing, likely **weakening pose-locking** while keeping hydrophobic bulk. This directly matches the summary: **lower proximal polar guidance** and a shift toward “more poses can reach close enough,” i.e., **higher chance of non-ideal attack vectors** and potentially more off-pathway oxidation if other clamp residues don’t compensate.

**Confidence:** High (directly matches the “de-aromatized clamp” narrative and a classic UPO clamp determinant).

---

### B. **CviUPO 158 / ET096 171 / DcaUPO 154 / TE314 183 / OA167 174** *(proximal contact/gating; local H-bond capacity and wall rigidity)*
- **Residues**
  - **ET096 A171** (small, nonpolar)
  - **CviUPO T158** (polar OH; H-bond donor/acceptor)
  - **Variant:** **CviUPO-F88L+T158A has A158**
  - **DcaUPO F154** (bulky aromatic)
  - **TE314 V183** (hydrophobic medium)
  - **OA167 P174** (rigid cyclic; constrains backbone/loop geometry)
- **Substitution class**
  - **Electrostatic/polarity:** T ↔ A (loss of OH; reduced H-bonding)
  - **Steric:** A/T/V ↔ F (bulky aromatic insertion); P is a **conformational/steric modulator** (rigidity more than volume).
- **Mechanistic consequence**
  - **CviUPO T158** can provide **local polar “braking”/pose registration** (even a single OH can bias substrate orientation), supporting the **polar/bulky clamp** phenotype.
  - **ET096 A171** fits the **small, dry inner pocket**: fewer polar anchors → **weaker pose-locking**, more rebinding/over-oxidation risk (consistent with ET096 “leaky selectivity”).
  - **DcaUPO F154** likely contributes to a **hard steric gate** near the reactive approach path: can **exclude unproductive poses** while still allowing close approach (consistent with DcaUPO’s “controlled mono-oxidation” despite high activity).
  - **OA167 P174** can reshape the pocket by **locking loop geometry**, often creating a “hydrophobic funnel” that is fast but not necessarily orienting—consistent with OA167 high conversion but **over-oxidation prone**.
- **Intra-family contrast (CviUPO → F88L+T158A)**
  - **T158A** specifically removes an H-bond handle in the proximal shell, matching the observed **drop in proximal polar fraction** in the summary. Mechanistically: **less polar guidance → more pose diversity**, which synergizes with **F88L** (loss of π-anchoring) to erode the clamp’s orientational control.

**Confidence:** High (directly explains the variant’s reduced polar fraction and the clamp→less-guiding shift).

---

### C. **CviUPO 165 / ET096 178 / DcaUPO 161 / TE314 190 / OA167 181** *(charged vs neutral “electrostatic hotspot” near pocket; proximal steering/ET competence)*
- **Residues**
  - **CviUPO K165** (positively charged)
  - **Variant:** **CviUPO-F88L+T158A K165** (unchanged)
  - **ET096 A178** (neutral small)
  - **DcaUPO C161** (neutral, polarizable thiol; can be weakly polar)
  - **TE314 V190** (neutral hydrophobic)
  - **OA167 A181** (neutral small)
- **Substitution class**
  - **Electrostatic:** K (charged) ↔ A/V/C (neutral)
  - **Steric:** K is also longer/bulkier than A/V.
- **Mechanistic consequence**
  - **CviUPO K165** is a plausible contributor to CviUPO’s **“more polar and some charge” proximal environment** and its **high ABTS/peroxidase-like ET** competence: a Lys can stabilize polar transition states, organize waters, or support an **ET-accessible electrostatic landscape**.
  - **ET096/OA167/TE314 neutral residues here** align with their **uncharged proximal electrostatics**; in ET096 this reinforces the “dry/uncharged” inner pocket that lacks steering.
  - **DcaUPO C161** is neutral but can tune **local polarizability**; however it won’t replicate the strong electrostatic steering of Lys—consistent with DcaUPO’s model where **distal charge** (not necessarily proximal) is the major electrostatic feature.
- **Intra-family contrast**
  - No change between CviUPO and its variant at 165, so **any electrostatic differences in the variant are not due to loss of this positive charge**; instead they are better attributed to **T158A and F88L** (loss of H-bond/π guidance) plus geometry changes noted in the summary.

**Confidence:** Medium–high (clear charge difference across homologs; mechanistic link to ABTS/ET is plausible but would benefit from mapping to the ET pathway geometry).

---

### D. **ET096 77 / CviUPO 60 / DcaUPO 58 / TE314 80 / OA167 76** *(rare charged insertion; local electrostatics + steric micro-gating)*
- **Residues**
  - **ET096 A77**, **OA167 A76** (small neutral)
  - **CviUPO T60**, **TE314 T80** (polar OH)
  - **DcaUPO D58** (negatively charged)
- **Substitution class**
  - **Electrostatic:** D ↔ A/T (introduces negative charge)
  - **Polarity:** A ↔ T (adds OH)
- **Mechanistic consequence**
  - **DcaUPO D58** is a strong candidate for the **“charged vestibule”** concept (even if this specific site is sometimes slightly >6 Å in the table, it is pocket-proximal in the alignment set): a carboxylate can **pre-orient substrates**, stabilize polar entry conformations, or participate in **ET-friendly networks**—consistent with DcaUPO’s high distal charge and strong peroxygenation.
  - **ET096 A77** supports the “uncharged, low polar” proximal phenotype → **less steering**.
  - **CviUPO/TE314 T** provides intermediate polarity: can H-bond but without ionic steering.
- **Intra-family contrast**
  - Not a variant site.

**Confidence:** Medium (because distance-to-ligand varies by structure; still a chemically strong differentiator).

---

### E. **ET096 174 / CviUPO 161 / DcaUPO 157 / TE314 186 / OA167 177** *(“void vs wall” position; steric confinement and radical escape/rebinding propensity)*
- **Residues**
  - **ET096 L174** (bulky aliphatic wall)
  - **CviUPO G161**, **DcaUPO G157**, **TE314 G186** (glycine → creates space/flexibility)
  - **OA167 F177** (bulky aromatic wall)
- **Substitution class**
  - **Steric:** G (minimal) ↔ L/F (bulky)
- **Mechanistic consequence**
  - **Glycine at this site (CviUPO/DcaUPO/TE314)** likely creates a **local void or hinge** that can (i) allow the substrate to nestle deeper or (ii) permit subtle rearrangements that support a **defined productive pose** without over-constraining.
  - **ET096 L174** and **OA167 F177** add a **hard wall**. In OA167, this pairs with an overall hydrophobic pocket to give **tight contact but not necessarily correct orientation**, consistent with fast chemistry + over-oxidation. In ET096, despite being “small-residue-rich” overall, this single wall could still **bias entry trajectories** while the rest of the pocket remains compliant—supporting multiple poses and rebinding.
- **Intra-family contrast**
  - Not a variant site.

**Confidence:** Medium (strong steric effect; directionality depends on exact geometry).

---

## 2) Ranked residue lists (mechanistic drivers vs modulators vs likely neutral)

### High-confidence mechanistic driver residues
1. **CviUPO F88 → (variant) L88** (CviUPO 88; ET096 103; etc.): **π/shape clamp determinant** controlling pose-locking vs pose diversity.  
2. **CviUPO T158 → (variant) A158** (CviUPO 158; ET096 171; etc.): **proximal H-bond guidance** loss; synergizes with F88L to weaken clamp chemistry.  
3. **CviUPO K165 vs neutral residues in others** (CviUPO 165; ET096 178; etc.): **electrostatic hotspot** plausibly tied to CviUPO’s higher proximal charge/polar behavior and ET competence.

### Secondary modulators (context-dependent but plausible contributors)
4. **DcaUPO D58** (DcaUPO 58; ET096 77; etc.): localized **negative charge** supporting the “charged vestibule” steering/ET network.  
5. **Gly vs bulky at the “void vs wall” site** (CviUPO 161 / DcaUPO 157 / TE314 186 vs ET096 174 / OA167 177): tunes **steric confinement**, residence time, and likelihood of **rebinding/over-oxidation**.  
6. **DcaUPO F154 / OA167 P174 / TE314 V183 / ET096 A171** (same aligned position as CviUPO 158): steric rigidity differences that can **gate** approach vectors.

### Likely neutral/background (within this dataset/summary)
- Positions that are **mostly conservative hydrophobics** across proteins and not implicated by the summary as key electrostatic features, e.g. **ET096 74 V / CviUPO 57 L / DcaUPO 55 L / TE314 77 L** (minor steric tuning only), and **ET096 223 F / CviUPO 210 M / DcaUPO 206 L / TE314 236 V / OA167 226 I** (hydrophobic swap; likely second-order unless it directly lines the reactive trajectory in a given structure).

If you share which ligand/reactive atom definition was used for the “reactive_center_distance” metric (heme oxo vs substrate site), I can tighten the causal chain for which of these sites most directly controls **approach geometry vs ET access**.