## Stage 1: Global Pocket Phenotypes

Assumptions/notes on inputs  
- The `binding_pocket_table` already contains **explicit proximal vs distal** columns (e.g., `charged_fraction (proximal)`), so no inference was needed.  
- `pocket_alignment_table` is a **filtered alignment of pocket-proximal positions**; I use it qualitatively to point to “where” steric/electrostatic differences likely come from (e.g., ET096 has deletions at some aligned pocket positions where others have hydrophobics/polars).

---

## Per-protein interpretations (structure → mechanism → observed chemistry)

### 1) **ET096_S82 — “Wide, dry active site: fast access, weak pose-locking → over-oxidation.”**
- **Proximal electrostatics:** essentially **uncharged** (charged_fraction 0.0) and **low polar** (0.182) with **high hydrophobicity** (kd_weighted 2.177; hw_weighted −0.94). Median residue→reactive-center distance is relatively long (7.921 Å), consistent with fewer strong “anchoring” contacts near the reactive locus.
- **Proximal sterics:** **small-residue enriched** (small_residue_frac 0.636; bulky 0.273) with moderate volumes (weighted_mean_volume 90.8) and **12 residues <6 Å**. This reads like a **more permissive, less shape-complementary** inner pocket.
- **Distal electrostatics:** distal shell is mildly polar/charged (polar 0.368; charged 0.132) but still fairly hydrophobic overall (kd_weighted 0.967; hw_weighted −0.464). So the “outer vestibule” doesn’t strongly electrostatically steer/hold a single pose.
- **Distal sterics / outer size:** distal centroid distances are among the **largest** here (mean_dist_to_centroid 10.247; mean_min_dist_to_centroid 8.57) with **38 aligned pocket residues**—an **open outer pocket** that likely tolerates multiple substrate approaches.
- **Pocket phenotype & catalytic implication (with reaction data):** matches **high total turnover but poorer selectivity**: S82 total 41.1% with **Mono:Di = 0.3** (strongly di-oxidation/peroxidation-leaning). A hydrophobic, small-residue-rich proximal pocket tends to **allow re-binding/re-orientation** of mono-oxidized product and/or allow **electron-transfer/peroxidative** events because the substrate isn’t “pose-locked” for a single productive oxygen insertion.
  - Reaction support: ET096 has **low ABTS** (0.146) but still shows strong **Di-Ox** on S82 (32.7%), consistent with “over-oxidation via permissive geometry” rather than classic ABTS-type surface ET alone.

---

### 2) **CviUPO_S82 — “Tight, polar-and-bulky clamp: pose control favors mono-oxygenation, but enables peroxidation too.”**
- **Proximal electrostatics:** more **polar/charged** than ET096 (polar 0.385; charged 0.077) and less hydrophobic (kd_weighted 1.055). Median residue→reactive-center distance is shorter (6.683 Å), consistent with **closer functional groups** shaping the reactive pose.
- **Proximal sterics:** very **bulky** inner pocket (bulky_residue_frac 0.615; small 0.154) with high mean volume (111.0) and **13 residues <6 Å**; median min distance to ligand is tight (3.575 Å). This combination suggests **strong steric guidance** (a “clamp”) rather than a roomy cavity.
- **Distal electrostatics:** distal shell is the **most polar** in the set (polar 0.513) with modest charge (0.128) and low hydrophobicity (kd_weighted 0.387). This can **steer binding trajectories** and stabilize specific entrance/egress paths.
- **Distal sterics / outer size:** distal centroid distances are slightly smaller than ET096 (mean_dist_to_centroid 9.906; mean_min_dist_to_centroid 8.079), implying a **somewhat more compact vestibule**.
- **Pocket phenotype & catalytic implication (with reaction data):** consistent with **higher mono-selectivity** on S82 (Mono:Di 1.7) and decent peroxygenation on small aromatics (NBD 0.169). The bulky/polar proximal environment likely **restricts orientations** that lead to repeated oxidation, favoring a single productive oxygen transfer event.
  - But CviUPO also shows **very high ABTS (3.939)**: the same polar/charged environment (especially in the distal shell) can support **peroxidative electron-transfer competence** (substrate positioning/ET pathways), so CviUPO looks like a “pose-locking oxygenase” that is nevertheless **peroxidation-capable**.

---

### 3) **DcaUPO_S82 — “Reactive-center close approach + hydrophobic inner wall: strong oxygenation power with controlled mono bias.”**
- **Proximal electrostatics:** low polar (0.154) but some charge (0.077) and fairly hydrophobic (kd_weighted 1.785; hw_weighted −1.042). Median residue→reactive-center distance 7.314 Å is mid-range.
- **Proximal sterics:** bulky-rich (bulky 0.615) with **15 residues <6 Å** (highest here) and **very high proximal volume variance** (1183) → a **rugged/anisotropic pocket**: tight in some directions, open in others. Importantly, **reactive_center_distance is small (4.931 Å)**, suggesting the docked reactive atom is positioned **closer to the catalytic center** than in ET096/CviUPO.
- **Distal electrostatics:** distal is relatively charged (0.2; highest) with moderate polarity (0.4) and moderate hydrophobicity (kd_weighted 0.823). This can create **electrostatic steering** without making the vestibule overly polar.
- **Distal sterics / outer size:** distal centroid distances are similar to ET096 (mean_dist_to_centroid 10.004), so access is not especially restricted.
- **Pocket phenotype & catalytic implication (with reaction data):** DcaUPO combines **good access** with **better reactive alignment** (short reactive_center_distance), matching its strong peroxygenation signals (Veratryl 1.558; NBD 1.242). On S82 it is **mono-biased** (Mono:Di 1.6), consistent with a pocket that can place the substrate close for the first oxygenation but—with bulky features and anisotropy—**discourages the second oxidation pose** or slows product re-binding in the “right” orientation.
  - ABTS is also high (2.7), so DcaUPO appears broadly competent; the key differentiator vs CviUPO is likely **geometry (closer reactive placement)** rather than higher polarity.

---

### 4) **TE314_S82 — “Balanced pocket: neither tight clamp nor open funnel → mixed pathway behavior.”**
- **Proximal electrostatics:** uncharged (0.0) but moderately polar (0.308) and moderately hydrophobic (kd_weighted 1.821). Median residue→reactive-center distance is the longest (8.205 Å), implying fewer close electrostatic “handles” near the reactive locus.
- **Proximal sterics:** intermediate volumes (weighted_mean_volume 95.4), moderate small/bulky (small 0.231; bulky 0.308), **12 residues <6 Å**. This looks like a **middle-of-the-road** inner pocket.
- **Distal electrostatics:** distal is relatively hydrophobic (kd_weighted 1.49; hw_weighted −0.661) with modest polarity (0.353) and low charge (0.118) → less electrostatic steering than CviUPO/DcaUPO.
- **Distal sterics / outer size:** among the **most compact** distal shells (mean_dist_to_centroid 9.675; mean_min_dist_to_centroid 7.81), and fewer aligned residues (34), suggesting a **smaller outer pocket/vestibule**.
- **Pocket phenotype & catalytic implication (with reaction data):** S82 total is decent (36.5%) with **Mono:Di 0.7** (di-oxidation somewhat favored). Mechanistically: a slightly tighter outer vestibule can **retain product** (promoting second oxidation), while the proximal site lacks the strong polar “pose lock” that would enforce mono-selectivity.

---

### 5) **OA167_S82 — “Bulky hydrophobic inner pocket + roomy chemistry: high throughput, di-oxidation prone.”**
- **Proximal electrostatics:** uncharged (0.0), moderately polar (0.308), and **most hydrophobic proximal pocket** by hw_weighted (−1.359) with kd_weighted 1.405. This is a “hydrophobic wall” near the ligand.
- **Proximal sterics:** bulky-rich (bulky 0.538; small 0.154) with high weighted volume (111.14) but only **10 residues <6 Å** (fewest), suggesting fewer close contacts but those present are **big/hydrophobic**.
- **Distal electrostatics:** moderate polarity (0.4) and low charge (0.114) with kd_weighted 1.03 → not strongly steering.
- **Distal sterics / outer size:** distal centroid distances are moderate (mean_dist_to_centroid 9.74; mean_min_dist_to_centroid 8.075) with 35 aligned residues—access is not extremely open, not extremely tight.
- **Pocket phenotype & catalytic implication (with reaction data):** highest S82 total (46.8%) but **Mono:Di 0.6** (di-oxidation favored). A plausible mechanism is **hydrophobic capture + weak polar anchoring**: substrate and mono-oxidized product bind readily and can reorient, enabling a second oxidation event.

---

## 2A) Intra-protein variant analysis (families/variants)
No intra-protein variant sets are present in the provided tables in the sense of “same base protein with multiple mutation labels.” All structures are single entries per homolog and all are labeled `_S82` (which appears to be the docked ligand/condition rather than a protein mutation series).  
- Therefore, **no WT vs variant comparisons can be performed** from these inputs.

(If you later provide e.g., `ET096_WT`, `ET096_FxxY`, etc., I can do the mandatory variant-vs-reference deltas.)

---

## 2B) Requested pairwise comparison: **CviUPO vs ET096**

### Dimension-by-dimension contrasts
**(i) Proximal electrostatics**
- CviUPO is **more polar/charged** (polar 0.385; charged 0.077) vs ET096 (polar 0.182; charged 0.0).
- CviUPO is **less hydrophobic** (kd_weighted 1.055) vs ET096 (2.177).
- Mechanistic read: CviUPO should provide **more specific H-bonding / electrostatic pose constraints**, favoring a defined reactive orientation.

**(ii) Proximal sterics**
- CviUPO is **much bulkier** (bulky 0.615; small 0.154) vs ET096 (bulky 0.273; small 0.636).
- CviUPO has tighter median ligand contact (median_min_dist_to_ligand 3.575 Å) vs ET096 (4.33 Å).
- Mechanistic read: CviUPO’s inner pocket is a **steric gate/fixture**; ET096 is a **small-residue, permissive cavity** that allows multiple poses and easier re-binding.

**(iii) Distal electrostatics**
- CviUPO distal shell is **far more polar** (0.513) and less hydrophobic (kd_weighted 0.387) than ET096 (polar 0.368; kd_weighted 0.967).
- Mechanistic read: CviUPO likely has **better electrostatic steering** into a productive binding mode and may support **peroxidative ET competence** (consistent with ABTS).

**(iv) Distal sterics / outer pocket size**
- ET096 has a **more open distal geometry** (mean_dist_to_centroid 10.247; mean_min_dist_to_centroid 8.57) vs CviUPO (9.906; 8.079).
- Mechanistic read: ET096’s larger vestibule can increase throughput but also increases the number of accessible, potentially non-productive orientations.

### Functional consequence (supported by reaction data)
- **Selectivity:** CviUPO is **mono-selective** on S82 (Mono:Di 1.7) vs ET096 strongly **di-oxidation prone** (0.3). This matches “pose-locking clamp” (CviUPO) vs “open/permissive” (ET096).
- **Peroxidation marker:** CviUPO has **very high ABTS** (3.939) vs ET096 low (0.146), consistent with CviUPO’s more polar/charged pocket environment (especially distal) being compatible with peroxidative chemistry.

---

## 3) Cross-protein pocket phenotypes (clusters) and expected trade-offs

### Phenotype 1 — **Open, hydrophobic, small-residue proximal (“permissive funnel”)**
- Representative: **ET096**
- Signature: high proximal kd_weighted, high small_residue_frac, low proximal polarity/charge; larger distal centroid distances.
- Expected behavior: **high throughput**, broader substrate tolerance, but **more over-oxidation (Di-Ox)** and less control over peroxygenation vs competing pathways because substrates/products can **reorient and rebind** easily.

### Phenotype 2 — **Bulky + polar proximal with polar distal steering (“pose-locking clamp”)**
- Representative: **CviUPO**
- Signature: high proximal bulky fraction + higher proximal polarity/charge; very polar distal shell.
- Expected behavior: **higher mono-selectivity** (pose control), but can also show **strong peroxidative competence** (ABTS high), likely because the same polar/charged environment supports ET-friendly configurations.

### Phenotype 3 — **Close reactive placement with anisotropic sterics (“reactive but guided”)**
- Representative: **DcaUPO**
- Signature: small reactive_center_distance + many residues <6 Å + high proximal volume variance (directional constraints), with moderate distal steering.
- Expected behavior: strong **peroxygenation potency** (good reactive alignment) with **mono bias** when steric anisotropy disfavors the second-oxidation pose.

### Phenotype 4 — **Intermediate/balanced pockets (“generalist, mixed outcomes”)**
- Representatives: **TE314, OA167** (OA167 skewing more hydrophobic/bulky proximally)
- Signature: mid-range polarity/hydrophobicity and centroid distances.
- Expected behavior: decent turnover with **mixed mono/di outcomes**, depending on whether the outer pocket retains product (favoring Di-Ox) and whether proximal polarity is sufficient to enforce a single productive pose.

---

If you want, I can also:  
- Extract a **ranked “selectivity index”** from the structural descriptors (a simple heuristic combining proximal polarity + bulky fraction − distal openness) and see how well it tracks the S82 Mono:Di ratios.  
- Use the `pocket_alignment_table` to highlight **specific aligned positions** that most plausibly drive the ET096↔CviUPO differences (e.g., ET096 deletions at positions where others have hydrophobic/polar side chains near the ligand).

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue-level mechanistic hypotheses
(Positions are given in **each protein’s own numbering**; I refer back to the earlier pocket phenotypes: ET096 “wide/dry/permissive”, CviUPO “tight/polar clamp”, DcaUPO “close reactive placement + anisotropic sterics”, TE314 “balanced/compact vestibule”, OA167 “bulky hydrophobic inner wall + weak anchoring”.)

### A. **ET096 has a deletion where others have a hydrophobic wall residue near the ligand**
- **Position (aligned row index 104):**
  - **ET096:** **gap** (no residue)
  - **CviUPO:** **I61** (min dist 3.32 Å)
  - **DcaUPO:** **L59** (3.63 Å)
  - **TE314:** **L81** (3.39 Å)
  - **OA167:** **L77** (3.41 Å)
- **Substitution class:** **steric (missing side chain vs medium hydrophobe)**; also **polarity shift** (loss of hydrophobic surface).
- **Mechanistic consequence:** this is a *direct structural explanation* for ET096’s **more permissive, less shape-complementary proximal pocket**. Removing an Ile/Leu “wall” near ~3.3–3.6 Å:
  - increases local free volume → **more ligand microstates**, weaker pose-locking
  - reduces van der Waals “caging” → **easier product reorientation/rebinding**, consistent with ET096’s **di-oxidation/permissive geometry** phenotype.
- **Tie-back:** matches ET096’s “wide, dry active site” and higher small-residue enrichment; other homologs keep a close hydrophobic contact that contributes to the **clamp** (CviUPO) or **guided anisotropy** (DcaUPO).

**Confidence:** very high (gap vs conserved hydrophobe at <3.6 Å is a strong steric driver).

---

### B. **Charged Lys in CviUPO at a near-pocket position (electrostatic handle)**
- **Position (aligned row index 226):**
  - **ET096:** **A178** (min dist 4.18 Å)
  - **CviUPO:** **K165** (3.38 Å)
  - **DcaUPO:** **C161** (5.54 Å)
  - **TE314:** **V190** (4.58 Å)
  - **OA167:** **A181** (5.86 Å)
- **Substitution class:** **electrostatic (neutral → positively charged)** and **polarity increase**; modest steric increase (A→K).
- **Mechanistic consequence:**
  - In **CviUPO**, **K165** places a **localized + charge** within ~3.4 Å of ligand → can create **stronger electrostatic steering / H-bond networks (via water or direct contacts)**.
  - This supports the earlier phenotype: CviUPO’s **more polar/charged proximal environment** and **shorter median reactive-center distances** (more “handles” near the reactive locus).
  - Functionally, a proximal Lys can **reduce rotational freedom** (pose-locking) and can also support **peroxidative ET competence** (consistent with CviUPO’s high ABTS) by stabilizing polar transition states / charge-separated configurations.
- **Contrast across proteins:** ET096/OA167 keep Ala (nonpolar, no steering) → consistent with “dry/permissive” (ET096) and “hydrophobic capture but weak anchoring” (OA167). DcaUPO has Cys (polarizable but uncharged) and is farther away here, so less direct electrostatic effect.

**Confidence:** high (unique charged residue at closest distance among homologs).

---

### C. **Acidic residue in DcaUPO at a position that is neutral in others (introduces negative electrostatics)**
- **Position (aligned row index 103):**
  - **ET096:** **A77** (min dist 3.94 Å)
  - **CviUPO:** **T60** (5.14 Å)
  - **DcaUPO:** **D58** (5.86 Å)
  - **TE314:** **T80** (5.39 Å)
  - **OA167:** **A76** (7.30 Å)
- **Substitution class:** **electrostatic (neutral → negative)** + polarity increase; small steric change.
- **Mechanistic consequence:**
  - **DcaUPO D58** can contribute to DcaUPO’s **higher distal/proximal charge fraction** and “electrostatic steering without overly polar vestibule”.
  - Even at ~5.9 Å, a carboxylate can bias **substrate approach/orientation** (especially for polarizable aromatics) and influence **local water structure** that affects rebound vs escape.
  - This can help explain DcaUPO’s “reactive but guided” behavior: not necessarily a tight clamp, but **electrostatic biasing** combined with anisotropic sterics.
- **Tie-back:** consistent with DcaUPO having the **highest distal charged fraction** in the summary.

**Confidence:** medium (distance is not ultra-proximal, but charge effects can be long-range in a pocket).

---

### D. **Bulky aromatic vs small residue at a key “inner-wall” position (steric clamp / hydrophobic packing)**
- **Position (aligned row index 221):**
  - **ET096:** **L174** (min dist 3.40 Å)
  - **CviUPO:** **G161** (3.47 Å)
  - **DcaUPO:** **G157** (3.96 Å)
  - **TE314:** **G186** (3.76 Å)
  - **OA167:** **F177** (3.38 Å)
- **Substitution class:** strong **steric** variation (G ↔ L/F) and hydrophobic surface change.
- **Mechanistic consequence:**
  - **OA167 F177** at 3.38 Å creates a **bulky hydrophobic wall** very close to ligand → promotes **hydrophobic capture** and can enforce certain orientations, but without polar anchors it can still allow **reorientation/rebinding**, consistent with OA167’s **di-oxidation-prone** phenotype.
  - **ET096 L174** provides some walling, but ET096 simultaneously lacks the “missing Ile/Leu” position (gap at ET096 in row 104) and is overall small-residue enriched → net effect still **permissive**.
  - **CviUPO/DcaUPO/TE314 Gly** here removes side-chain bulk at this specific spot; in CviUPO the “clamp” must therefore come from *other* bulky residues plus polarity (e.g., K165 and other bulky positions), whereas in OA167 this Phe is a major contributor to the “bulky hydrophobic inner wall”.
- **Tie-back:** explains why OA167 can be “bulky proximally” despite having fewer <6 Å contacts overall: the contacts it does have include **very bulky hydrophobes**.

**Confidence:** high (large steric differences at ~3.4–4.0 Å).

---

### E. **Aromatic “cap” vs small residue in the 170s region (controls pocket roof/retention)**
- **Position (aligned row index 220):**
  - **ET096:** **A173** (min dist 8.19 Å)
  - **CviUPO:** **Y160** (5.80 Å)
  - **DcaUPO:** **L156** (5.90 Å)
  - **TE314:** **L185** (6.09 Å)
  - **OA167:** **Y176** (7.46 Å)
- **Substitution class:** **steric + polarity** (A → Y/L).
- **Mechanistic consequence:**
  - **CviUPO Y160** (closer) can act as a **bulky polarizable cap** that helps **pose-lock** and can increase **product retention** in a defined orientation (mono-selectivity) *while* also shaping ET pathways (aromatic residues can participate in packing networks).
  - **ET096 A173** removes that cap → contributes to ET096’s **open vestibule / weak pose-locking**.
  - **OA167 Y176** is farther (7.46 Å) so it may contribute more to **outer-pocket character** than direct clamping; consistent with OA167 being not strongly steering electrostatically.
- **Tie-back:** aligns with CviUPO’s “tight bulky clamp” and ET096’s “wide/dry”.

**Confidence:** medium-high (distance varies; strongest effect in CviUPO).

---

### F. **Bulky aromatic at DcaUPO 154 near the reactive locus (anisotropic sterics / close placement)**
- **Position (aligned row index 219):**
  - **ET096:** **A171** (6.76 Å)
  - **CviUPO:** **T158** (3.77 Å)
  - **DcaUPO:** **F154** (3.54 Å)
  - **TE314:** **V183** (3.81 Å)
  - **OA167:** **P174** (3.62 Å)
- **Substitution class:** **steric** (A/T/V/P ↔ **F**), plus hydrophobic packing increase.
- **Mechanistic consequence:**
  - **DcaUPO F154** at 3.54 Å is a strong candidate for DcaUPO’s **“rugged/anisotropic” proximal sterics**: a phenyl side chain can create a **directional wall** that forces the ligand to approach the heme/reactive center along a preferred trajectory.
  - This supports DcaUPO’s phenotype of **good reactive alignment** (short reactive-center distance) while still discouraging the “second-oxidation pose” (mono bias).
  - ET096 has **A171** and is far → consistent with less guidance.
- **Tie-back:** matches DcaUPO’s “tight in some directions, open in others” description.

**Confidence:** high (bulky aromatic at ~3.5 Å unique to DcaUPO).

---

### G. **ET096 small residues where others are bulky (general permissiveness drivers)**
Two notable examples:
1) **ET096 V74 vs OA167 T73 / others L** (row index 100; ET096 min dist 2.94 Å)
   - **ET096 V74** close contact but relatively small; **OA167 T73** adds polarity; **others L** add bulk.
   - Likely tunes **local packing vs H-bonding** right at the ligand surface; OA167’s Thr could add weak anchoring but overall OA167 remains hydrophobic/bulky elsewhere.
2) **ET096 A80 vs DcaUPO F62 / CviUPO L64 / OA167 L80 / TE314 P84** (row index 107; ET096 min dist 4.44 Å)
   - **A80** is much smaller than **F/L/P** → contributes to ET096’s **wider inner pocket** and weaker shape complementarity.

**Confidence:** medium (effects depend on exact geometry, but consistent with ET096 “small-residue enriched”).

---

## 1b) Variant-within-same-sequence contrasts
No intra-protein variant series (e.g., WT vs mutants of ET096) are present in the provided alignment/summary; only one entry per homolog. Therefore I cannot satisfy the “point mutations in variants of the same base sequence” requirement from these inputs alone.

---

## 2) Ranked residue list (mechanistic drivers vs modulators vs likely neutral)

### High-confidence mechanistic driver residues (most causal)
1) **ET096 deletion at the position corresponding to CviUPO I61 / DcaUPO L59 / TE314 L81 / OA167 L77** (row index 104)  
   *Primary steric “missing wall” → permissive pocket / weak pose-locking.*
2) **CviUPO K165** (vs ET096 A178, etc.; row index 226)  
   *Primary electrostatic handle near ligand → steering/pose-locking; supports polar clamp + ABTS competence.*
3) **DcaUPO F154** (row index 219)  
   *Primary anisotropic steric wall near ligand → close placement + mono bias via constrained orientations.*
4) **OA167 F177** (row index 221)  
   *Primary bulky hydrophobic inner-wall contact → hydrophobic capture/retention, di-oxidation prone.*

### Secondary modulators (context-dependent, likely real but less singular)
- **CviUPO Y160** (row index 220): aromatic cap contributing to clamp/pose definition.
- **DcaUPO D58** (row index 103): negative electrostatic bias/steering (longer-range).
- **ET096 A80** (row index 107): small residue contributing to widened inner pocket vs L/F/P in others.
- **ET096 V74 / OA167 T73** (row index 100): local packing vs polarity tweak at very close contact.

### Likely neutral/background (within this dataset)
(Conservative or distal-ish changes with weaker mechanistic leverage given distances/chemistry)
- **ET096 S172 / CviUPO S159 / TE314 S184 / OA167 T175** (row index 220): mostly conservative polar small residues and relatively distal in ET096.
- **ET096 F223 vs CviUPO M210 vs DcaUPO L206 vs TE314 V236 vs OA167 I226** (row index 278): hydrophobic swaps; could matter for shape, but without stronger phenotype linkage here they look secondary/background.
- **ET096 S227 vs TE314 S240 vs OA167 T230 vs CviUPO V214 vs DcaUPO M210** (row index 282): mixed but relatively distal in ET096/OA167; likely modest tuning.

If you provide a true variant set (e.g., ET096_WT and ET096 mutants), I can convert these cross-homolog drivers into **specific mutation→phenotype delta predictions** (e.g., “introduce the missing hydrophobe at the ET096 gap position to increase pose-locking and raise Mono:Di”).