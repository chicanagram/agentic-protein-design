## Stage 1: Global Pocket Phenotypes

Assumptions/notes on the inputs  
- Your `binding_pocket_table` already contains **explicit proximal vs distal columns** for most descriptors (e.g., `mean_volume (proximal)` and `mean_volume (distal)`), so I treat those as the <6 Å vs ~6–11 Å residue sets, respectively.  
- `num_pocket_res<8` appears to be a *near-pocket count* but not strictly “<6 Å”; since `num_pocket_res_lt6` is not present, I use `num_pocket_res<8` as a **proxy for proximal packing density** and state that explicitly where relevant.  
- No reaction_data were provided, so catalytic/selectivity inferences are **mechanistic hypotheses** grounded in pocket physics + known lipase behavior (RML/TLL lid lipases; sucrose acylation often limited by sugar accommodation).

---

## Per-protein interpretations

### 1) **RML_SucroseOleate**
**Tagline:** *“Balanced, slightly polar pocket with a roomy outer vestibule—good for binding, less for pose-locking.”*

- **(i) Proximal electrostatics**
  - Moderate **charged_fraction ~0.182** and high **polar_fraction ~0.455**: a chemically “wettable” near-field that can H-bond to sucrose hydroxyls.
  - **kd_weighted (prox) = -0.158** (more negative) suggests the proximal shell trends **more hydrophilic/polar** than TLL’s proximal shell in this dataset.
  - **median_dist_res_to_ligand_reactive_center ~10.26 Å** indicates many “pocket residues” are not tightly focused around the reactive center—consistent with a broader cavity where only a subset truly steers chemistry.

- **(ii) Proximal sterics**
  - **median_min_dist_res_to_ligand ~5.00 Å** (closer than TLL) suggests **tighter local contact** to the docked ligand overall.
  - **mean_volume (prox) ~102.9 Å³; weighted_mean_volume (prox) ~100.9 Å³**: moderate sidechain bulk; not an extremely tight, small-residue-lined pocket.
  - **bulky_residue_frac (prox) ~0.341** with **small_residue_frac (prox) ~0.25**: mixed lining → tends to allow multiple microposes rather than a single “keyed” pose.
  - **reactive_center_distance ~6.39 Å**: reactive center is not extremely close to the catalytic machinery/idealized reactive geometry (relative to TLL here), which can reduce probability of a highly productive near-attack conformation.

- **(iii) Distal electrostatics**
  - Distal shell is similarly polar (**polar_fraction ~0.456**) but slightly less charged (**charged_fraction ~0.175**).
  - **kd_weighted (dist) ~0.021** shifts toward more hydrophobic/neutral compared to proximal, implying a **polarity gradient**: polar near-field with a more permissive outer region.

- **(iv) Distal sterics / outer pocket size**
  - Outer pocket distances are **moderate**: `mean_dist_to_centroid (distal) ~10.69 Å`, `mean_min_dist_to_centroid (distal) ~8.86 Å`.
  - Distal bulk is moderate (**mean_volume (dist) ~102.5 Å³; bulky_frac (dist) ~0.351**) with substantial heterogeneity (**volume_variance (dist) ~909**), consistent with a **textured vestibule** that can accommodate different ligand orientations.

- **(v) Pocket phenotype → catalytic implications (peroxygenative vs peroxidative competition)**
  - **Phenotype:** “balanced polar/hydrophobic, moderately open, not strongly pose-locking.”
  - Mechanistically, this kind of pocket tends to **admit sucrose** (polar contacts available) but may **struggle to enforce a single productive alignment** of the acceptor OH relative to the acyl-enzyme (or reactive intermediate), increasing the chance of **non-productive binding** and/or alternative microstates.
  - In a peracid/peroxide context (if that’s your competing-pathway framing), a **less constrained reactive geometry** generally increases the probability of **off-pathway peroxide reactions** (peroxidative) because the pocket does not “funnel” the reactive species into one dominant near-attack trajectory.

---

### 2) **TLL_SucroseOleate**
**Tagline:** *“More hydrophobic and bulkier near the ligand—built to gate and steer, not to solvate.”*

- **(i) Proximal electrostatics**
  - **charged_fraction (prox) ~0.182** (same as RML) but **polar_fraction (prox) ~0.409** (lower than RML): proximal environment is **less H-bond rich**.
  - **kd_weighted (prox) = -0.064** is less negative than RML → proximal shell is **less polar/more hydrophobic-leaning** than RML by this metric.
  - **median_dist_res_to_ligand_reactive_center ~10.36 Å** similar to RML: again suggests many annotated pocket residues are not tightly centered on the reactive center.

- **(ii) Proximal sterics**
  - **median_min_dist_res_to_ligand ~5.54 Å** (larger than RML): fewer very close contacts overall, but…
  - The lining is **bulkier**: **mean_volume (prox) ~107.9 Å³**, **bulky_residue_frac (prox) ~0.477** (substantially higher than RML’s 0.341), and **volume_variance (prox) ~1112** (higher).
  - Interpretation: TLL’s proximal pocket is more like a **sculpted, bulky “funnel”**—not necessarily closer everywhere, but more capable of **steric steering** and excluding certain poses.

- **(iii) Distal electrostatics**
  - Distal shell has **higher charged_fraction ~0.20** but **lower polar_fraction ~0.40** than RML.
  - Net effect: distal region may present **more discrete charge points** (salt-bridge opportunities) but fewer distributed H-bond donors/acceptors—often consistent with **specific anchoring sites** rather than general sugar solvation.

- **(iv) Distal sterics / outer pocket size**
  - Distal distances are **larger** than RML: `mean_dist_to_centroid (distal) ~11.29 Å` and `mean_min_dist_to_centroid (distal) ~9.38 Å` → a **bigger outer vestibule**.
  - Distal bulk is slightly higher (**mean_volume (dist) ~104.3 Å³; bulky_frac (dist) ~0.417**) with high heterogeneity (**volume_variance (dist) ~1060**): suggests an **expanded but structured outer region** that can host the sugar while the acyl chain occupies a hydrophobic groove.

- **(v) Pocket phenotype → catalytic implications (peroxygenative vs peroxidative competition)**
  - **Phenotype:** “outer-vestibule roomy, inner pocket sterically directive and more hydrophobic.”
  - This combination often supports **selectivity**: the distal vestibule can “park” a bulky polar acceptor (sucrose) while the proximal bulky/hydrophobic features **bias which hydroxyl can approach** the reactive center (consistent with literature tendencies of TLL toward **regioselective monoacylation** on sucrose).
  - In the productive-vs-competing framing: stronger steric steering near the reactive center generally **reduces off-pathway chemistry** by limiting reactive species orientations—i.e., it should *favor productive (peroxygenative-like) trajectories* over diffuse peroxidative side reactions, assuming the reactive intermediate is generated in-pocket.

---

## 2) Comparative analysis

### A) Intra-protein variant analysis
- **No variant families detected** in the provided structures: only `RML_SucroseOleate` and `TLL_SucroseOleate`, which are different homologs rather than variants of the same base protein.  
- Therefore, **no WT-vs-variant comparisons** are possible from these inputs.

### B) Requested pairwise comparison: **RML vs TLL**

**Proximal electrostatics**
- **RML is more polar in the near field**: polar_fraction 0.455 (RML) vs 0.409 (TLL); kd_weighted more negative (-0.158 vs -0.064).
- Mechanistic implication: RML likely provides **better H-bonding “landing”** for sucrose near the catalytic region, but that can also stabilize **multiple non-productive sugar poses** unless sterics enforce one.

**Proximal sterics**
- **TLL is markedly bulkier and more heterogeneous proximally**: bulky_residue_frac 0.477 vs 0.341; mean_volume 107.9 vs 102.9; volume_variance 1112 vs 881.
- RML has **closer overall contacts** to the docked ligand (median_min_dist 5.00 vs 5.54), but TLL has **more steric shaping power**.
- Mechanistic implication: TLL’s bulky proximal shell is better suited to **pose selection/regioselectivity** (exclude wrong hydroxyl approaches), whereas RML’s mixed/less-bulky lining is more permissive.

**Distal electrostatics**
- RML distal is **more polar overall** (polar_fraction 0.456 vs 0.400), while TLL distal is **more charged** (0.20 vs 0.175).
- Mechanistic implication: RML distal region may better support **general sugar accommodation**; TLL may rely on **specific charge anchors** (fewer but stronger interaction points).

**Distal sterics / outer pocket size**
- **TLL has a larger outer vestibule** (mean_dist_to_centroid distal 11.29 vs 10.69; mean_min_dist_to_centroid distal 9.38 vs 8.86) and is also bulkier distally (bulky_frac 0.417 vs 0.351).
- Mechanistic implication: TLL can better **host bulky sucrose** in the outer region while still enforcing a constrained approach near the reactive center—often a recipe for **monoacylation selectivity** (park-and-react geometry).

**Pocket-alignment “where the differences likely come from” (proximal positions)**
- Several aligned substitutions increase TLL polarity/charge or bulk at specific sites (examples from your table):
  - RML 83 **S** → TLL 84 **R** (adds a cationic, bulky sidechain near-pocket)
  - RML 91 **D** → TLL 92 **N** (removes negative charge)
  - RML 90 **A** → TLL 91 **G** (local flexibility change)
  - RML 259 **S** → TLL 260 **W** (adds bulky aromatic)
  - RML 264 **N** → TLL 264 **L** (more hydrophobic)
- Net: TLL substitutions skew toward **bulkier/hydrophobic shaping** plus **strategic charge placement**, consistent with the global descriptors.

---

## 3) Cross-protein “pocket phenotypes” (clusters) from this small set

With only two homologs, the clustering is necessarily coarse, but two clear archetypes emerge:

1) **“Polar-permissive pocket” (RML-like)**
- Higher proximal + distal polar fractions; more hydrophilic proximal kd_weighted.
- Moderate steric shaping (lower bulky fraction).
- Trade-off hypothesis: **better acceptance of polar substrates** (sucrose entry/retention) but **lower intrinsic pose discrimination**, which can reduce regioselectivity and increase non-productive binding.

2) **“Vestibule-parking + steric steering” (TLL-like)**
- Larger distal vestibule + higher bulky fraction proximally and distally.
- Slightly more hydrophobic proximal environment with discrete charges.
- Trade-off hypothesis: **higher selectivity (pose filtering/regioselectivity)**, potentially at the cost of requiring the substrate to find a narrower set of productive approaches (which can reduce turnover if docking/entry is limiting).

If you later add reaction_data (conversion, mono/di ratio, regioisomer distribution), we can test these hypotheses directly—especially whether TLL’s “steering” correlates with monoacylation enrichment and whether RML’s polarity correlates with higher binding/occupancy but broader product distributions.

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue-level mechanistic hypotheses (RML vs TLL)

Below I focus on **positions that (a) differ in identity, and (b) are plausibly causal for the global phenotypes** you summarized: **RML = more polar/permissive near-field**, **TLL = bulkier/more hydrophobic steric steering + discrete charge anchors**, with **TLL having a larger distal vestibule**.

> Note: you requested variant-vs-base comparisons; **none exist in these inputs** (only two homologs). I therefore contrast **RML vs TLL** at each position.

---

### A. Proximal / near-field drivers (most likely to impact sucrose OH approach & pose selection)

#### **RML 83 Ser ↔ TLL 84 Arg** (min dist ~3.5–3.6 Å)
- **Substitution class**
  - **Electrostatic:** neutral → **cationic**
  - **Steric:** small → **bulky**
  - **Polarity:** polar uncharged → strongly polar/charged
- **Mechanistic consequence**
  - In **TLL**, Arg introduces a **localized positive electrostatic anchor** and a **steric “post”** near the ligand. This matches your phenotype of **“discrete charge points” + steric steering**.
  - Likely effects:
    - **Bias sucrose orientation** by stabilizing specific hydroxyl/oxygen patterns (or phosphate/sulfate if present; here likely sucrose OH network).
    - **Reduce microstate degeneracy** (fewer non-productive sugar poses) by steric exclusion → consistent with **TLL regioselective monoacylation tendency**.
    - Potential downside: could **penalize entry/retention** of sucrose if it creates an overly specific H-bond/salt-bridge geometry (especially in low-water organics where charge desolvation is costly).
  - In **RML**, Ser keeps the region **H-bond capable but permissive**, consistent with your “polar-permissive, less pose-locking” description.

#### **RML 91 Asp ↔ TLL 92 Asn** (min dist ~2.37 vs 3.30 Å; very close in RML)
- **Substitution class**
  - **Electrostatic:** **negative → neutral**
  - **Polarity:** charged polar → polar amide (still H-bonding)
- **Mechanistic consequence**
  - In **RML**, Asp at very close contact distance can create a **strong, directional electrostatic field** (and potentially a persistent H-bond acceptor) that can:
    - **Over-stabilize multiple sucrose OH binding modes** (many hydroxyls can satisfy Asp), increasing **non-productive binding**—aligns with your “good for binding, less for pose-locking.”
    - Potentially **repel** negatively polarized groups and **attract** hydroxyl protons, altering which OH is presented toward the acyl-enzyme.
  - In **TLL**, Asn removes the formal charge while retaining H-bonding, which likely:
    - **Reduces “sticky” nonspecific electrostatic trapping** of sucrose near the reactive region.
    - Supports your observation that TLL is **less H-bond rich overall** proximally, but can still make **specific** polar contacts.

#### **RML 265 Thr ↔ TLL 265 Ile** (min dist ~2.91 vs 3.97 Å)
- **Substitution class**
  - **Polarity:** polar → **hydrophobic**
  - **Steric:** modest increase in hydrophobic bulk/shape
- **Mechanistic consequence**
  - **TLL Ile** strengthens a **hydrophobic wall** near the ligand, consistent with your “more hydrophobic/bulkier near the ligand—built to gate and steer.”
  - Likely effects:
    - **Favors acyl-chain packing** and can **push sucrose away** from that face, narrowing approach trajectories (pose filtering).
  - **RML Thr** provides an extra **H-bond donor/acceptor** close to ligand, reinforcing the **polar landing pad** behavior and potentially increasing alternative sucrose microposes.

---

### B. Distal / vestibule-shaping drivers (likely to affect sucrose parking, access channel geometry, and “outer vestibule” phenotype)

#### **RML 259 Ser ↔ TLL 260 Trp** (min dist ~7.6–7.7 Å; distal but pocket-facing)
- **Substitution class**
  - **Steric:** small → **very bulky aromatic**
  - **Polarity:** polar → largely hydrophobic (with indole NH)
- **Mechanistic consequence**
  - **TLL Trp** is a classic **steric gate / wall-former**:
    - Can **sculpt the vestibule** and create a **defined “parking surface”** (π/CH contacts) for sugar rings.
    - Can **reduce solvent exposure** and enforce a more **channeled approach** from vestibule → reactive center, consistent with your “vestibule-parking + steric steering” model.
  - **RML Ser** keeps this region **open and wettable**, consistent with a **textured but permissive vestibule** and higher distal polar fraction.

#### **RML 264 Asn ↔ TLL 264 Leu** (min dist ~6.18 vs 7.88 Å)
- **Substitution class**
  - **Polarity:** polar amide → **hydrophobic**
  - **Steric:** similar size but different shape/packing; Leu increases hydrophobic surface continuity
- **Mechanistic consequence**
  - **TLL Leu** supports a **more hydrophobic vestibule wall**, consistent with lower polar_fraction(distal) but slightly higher bulky_frac(distal).
  - Likely shifts sucrose behavior from “solvated/retained by many H-bonds” (RML-like) to “parked by shape + a few anchors” (TLL-like).

---

### C. Additional variable positions (probable secondary effects)

#### **RML 90 Ala ↔ TLL 91 Gly** (min dist ~5.6–6.5 Å)
- **Substitution class**
  - **Steric/flexibility:** Ala → **Gly increases backbone flexibility**
- **Mechanistic consequence**
  - Could subtly alter **local loop/turn mobility** near the pocket, affecting **gating dynamics** (important for lid lipases), but likely **secondary** unless this sits on a key shaping loop.

#### **RML 93 Thr ↔ TLL 94 Asn** (min dist ~5.0–6.7 Å)
- **Substitution class**
  - **Polarity shift:** Thr (OH) → Asn (amide); both polar, Asn more H-bond acceptor-rich
- **Mechanistic consequence**
  - Fine-tunes H-bond patterning; likely **modulatory** compared to the Asp/Arg changes above.

#### **RML 174 Gln ↔ TLL 171 Tyr** (distal; min dist ~7.5–7.8 Å)
- **Substitution class**
  - **Polarity/π:** Gln polar → Tyr aromatic polar (phenolic OH)
  - **Steric:** moderate increase in rigid bulk
- **Mechanistic consequence**
  - Tyr can provide a **rigid aromatic platform** for sugar ring contacts; may contribute to **structured vestibule** in TLL.

#### **RML 176 Gln ↔ TLL 173 Ala** (distal; min dist ~6.6–7.0 Å)
- **Substitution class**
  - **Polarity:** polar → **nonpolar**
  - **Steric:** smaller
- **Mechanistic consequence**
  - Removes a distal H-bond site in TLL, consistent with **lower distal polar_fraction** and more reliance on **shape/limited anchors**.

#### **RML 207 His ↔ TLL 205 Arg** (distal; min dist ~7.0–7.5 Å)
- **Substitution class**
  - **Electrostatic:** potentially neutral/weakly cationic (His) → **strong cation (Arg)**
  - **Steric:** larger
- **Mechanistic consequence**
  - Adds another **discrete positive charge point** in TLL distal shell, consistent with your “more charged distally” observation; could help **capture/position sucrose** in the vestibule without making the whole region highly polar.

#### **RML 215 Phe ↔ TLL 213 Tyr** (distal; min dist ~6.8 Å)
- **Substitution class**
  - **Polarity:** hydrophobic aromatic → aromatic with OH (slightly more polar)
- **Mechanistic consequence**
  - Small tuning of distal H-bonding; likely **minor** relative to Trp/Leu/Arg changes.

#### **RML 254 Val ↔ TLL 255 Ile** (distal; min dist ~5.8 vs 3.5 Å)
- **Substitution class**
  - **Steric:** Val → Ile (slightly bulkier)
- **Mechanistic consequence**
  - Could contribute to **tighter hydrophobic packing** in TLL at that spot; likely **secondary**.

#### **RML 267 Leu ↔ TLL 267 Thr** (distal; min dist ~3.8 vs 5.1 Å)
- **Substitution class**
  - **Polarity:** hydrophobic → polar
- **Mechanistic consequence**
  - This is one of the few changes that could make TLL *more* polar locally; may serve as a **specific H-bond “handle”** amid an otherwise hydrophobic steering surface.

---

## 2) Ranked residue list (mechanistic drivers vs modulators vs likely neutral)

### High-confidence mechanistic driver residues (most causal for your global phenotypes)
1. **RML 83 Ser ↔ TLL 84 Arg** — adds **bulky cationic anchor** near pocket; strong steric + electrostatic steering (fits TLL selectivity phenotype).
2. **RML 91 Asp ↔ TLL 92 Asn** — removes **negative charge** at very close contact; likely major contributor to **RML higher near-field polarity/permissiveness** vs TLL.
3. **RML 259 Ser ↔ TLL 260 Trp** — major **vestibule sculpting/gating** via bulky aromatic; supports “structured vestibule + steering” in TLL.
4. **RML 264 Asn ↔ TLL 264 Leu** — shifts distal wall from **polar to hydrophobic**, reinforcing TLL’s less polar vestibule.

### Secondary modulators (context-dependent; tune rather than define phenotype)
- **RML 265 Thr ↔ TLL 265 Ile** — local hydrophobic wall vs H-bond site near ligand.
- **RML 207 His ↔ TLL 205 Arg** — adds distal discrete positive charge (anchoring).
- **RML 176 Gln ↔ TLL 173 Ala** and **RML 174 Gln ↔ TLL 171 Tyr** — reshape distal H-bond availability / aromatic packing.
- **RML 267 Leu ↔ TLL 267 Thr** — introduces a polar “handle” in TLL; may compensate for other hydrophobization.

### Likely neutral/background (small effects or indirect unless coupled)
- **RML 90 Ala ↔ TLL 91 Gly** — flexibility tweak; probably minor alone.
- **RML 93 Thr ↔ TLL 94 Asn** — polar↔polar swap; subtle.
- **RML 215 Phe ↔ TLL 213 Tyr** — minor polarity increase.
- **RML 254 Val ↔ TLL 255 Ile** — conservative hydrophobic packing change.

---

If you share **which residues are proximal (<6 Å) vs distal (6–11 Å) in your exact definition** (or provide the full pocket table with proximal/distal labels per residue), I can tighten the causal chain further (e.g., explicitly mapping which of these sit in the alcohol-binding region vs acyl groove vs lid-adjacent gate).