## Stage 1: Global Pocket Phenotypes

Assumptions / parsing notes  
- Your `binding_pocket_table` already contains explicit “(proximal)” and “(distal)” suffixes for most descriptors; I treat those as the <6 Å vs ~6–11 Å residue sets you defined.  
- `num_pocket_res<8` is used as a proxy for “how many residues are close enough to matter”; you requested `num_pocket_res_lt6`, but it isn’t present—so I interpret `num_pocket_res<8` as a *looser* proximity count and lean more on distance metrics (`median_min_dist_res_to_ligand`, `reactive_center_distance`) for true proximity.

---

## Per-protein interpretations

### 1) **RML_SucroseOleate**
**Tagline:** *Polar-rimmed, moderately tight pocket that “guides” the sugar while keeping the acyl chain comfortable.*

- **(i) Proximal electrostatics**
  - Proximal charged/polar fractions are fairly high (charged ~0.18; polar ~0.46), suggesting a chemically “wet” microenvironment near the ligand—helpful for positioning sucrose hydroxyls for deacylation (productive synthesis step).
  - Proximal hydropathy is moderately hydrophobic (hw_weighted ≈ -0.40), consistent with a lipase pocket that still tolerates an oleate chain.
  - Proximal kd_weighted is negative (~ -0.16), i.e., overall more hydrophilic/less hydrophobic character than the distal shell—again consistent with a polar alcohol-acceptor region.
  - Median distance of residues to the ligand reactive center is ~10.26 Å (this is relatively large), implying that *many* pocket residues are not tightly “reactive-center clamping”; catalysis likely depends on a smaller subset of key proximal residues plus dynamics (lid/open state).

- **(ii) Proximal sterics**
  - Mean/weighted proximal residue volume ~103/101 Å³ with moderate variance (~881): not extremely tight, but not highly heterogeneous.
  - Bulky residue fraction proximal ~0.34 (weighted ~0.31) with small-residue fraction ~0.25 → a mixed lining that can provide both shape and some compliance.
  - Median minimum distance residue→ligand ~5.00 Å and reactive_center_distance ~6.39 Å: the docked pose is not “deeply buried” against many sidechains; suggests more of a channel/groove binding mode than a snug cavity lock.
  - `num_pocket_res<8` is high (51), consistent with a fairly extensive pocket surface contacting/near the ligand (even if not all are within 6 Å).

- **(iii) Distal electrostatics**
  - Distal shell is slightly *less* polar/charged than proximal (charged ~0.175; polar ~0.456 ~same), and kd_weighted becomes slightly positive (~0.02), i.e., more hydrophobic character outward.
  - This “polar inside / more hydrophobic outside” gradient is consistent with lipase architecture: polar features to manage the alcohol acceptor chemistry, hydrophobic features to stabilize acyl chain occupancy and lid-open state.

- **(iv) Distal sterics / outer pocket size**
  - Distal centroid distances are modest (mean_dist_to_centroid ~10.69 Å; mean_min_dist_to_centroid ~8.86 Å), indicating an outer pocket that is not extremely expanded.
  - Distal mean volume ~102.5 Å³ with variance ~909: similar to proximal—suggesting the pocket doesn’t flare dramatically outward.

- **(v) Pocket phenotype → catalytic implications (peroxygenative vs peroxidative framing)**
  - Phenotype: **balanced amphiphilic channel**—enough polarity near the ligand to support productive positioning of sucrose OH groups, while maintaining a hydrophobic “runway” for oleate.
  - Mechanistic expectation: this kind of pocket tends to **favor productive binding geometries** (less nonspecific oxidation chemistry) because polar proximal residues can enforce orientation/anchoring of the polyol headgroup. If the pocket were too hydrophobic and open, you’d expect more nonproductive poses and side reactions; RML here looks more “pose-guiding” than “promiscuously permissive.”

---

### 2) **TLL_SucroseOleate**
**Tagline:** *Bulkier, more hydrophobic proximal clamp with a roomier outer shell—built for monoacylation-style positioning rather than deep polar anchoring.*

- **(i) Proximal electrostatics**
  - Proximal polar fraction is lower than RML (polar ~0.41 vs ~0.46), while charged fraction is similar (~0.18).
  - Proximal hw_weighted is more negative (~ -0.50), i.e., **more hydrophobic** near the ligand than RML.
  - Proximal kd_weighted is less negative (~ -0.064 vs -0.158), which partially offsets the hydropathy read; net interpretation: **TLL proximal region is less “polyol-friendly” by polarity but still not extremely hydrophobic by kd**—suggesting fewer strong polar anchoring points but not a purely greasy tunnel.

- **(ii) Proximal sterics**
  - Proximal mean/weighted volume is larger (~108/104 Å³) and variance is higher (~1112): **more sterically structured and heterogeneous**.
  - Bulky residue fraction proximal is notably higher (0.477; weighted 0.414) with slightly fewer small residues (0.227): this reads like a **more shape-defining clamp** near the ligand.
  - Median minimum distance residue→ligand is larger (~5.54 Å vs 5.00 Å in RML) even though reactive_center_distance is slightly shorter (~5.97 Å vs 6.39). This combination often indicates: fewer close sidechain contacts overall, but the reactive center sits somewhat closer to the catalytic machinery while the rest of the ligand is less snugly packed.

- **(iii) Distal electrostatics**
  - Distal charged fraction is higher than RML (0.20 vs 0.175) but distal polar fraction is lower (0.40 vs 0.456).
  - Distal hw_weighted ~ -0.40 (less hydrophobic than its own proximal region), suggesting a **hydrophobic “inner clamp” with a slightly more mixed outer shell**.

- **(iv) Distal sterics / outer pocket size**
  - Distal centroid distances are larger than RML (mean_dist_to_centroid ~11.29 Å vs 10.69; mean_min_dist_to_centroid ~9.38 vs 8.86): **roomier outer pocket / more expanded shell**.
  - Distal volume variance is higher (~1060 vs 909): more geometric diversity outward—often correlated with broader substrate tolerance but also more pose degeneracy.

- **(v) Pocket phenotype → catalytic implications (peroxygenative vs peroxidative framing)**
  - Phenotype: **hydrophobic, bulky proximal “gate” + expanded outer shell**.
  - Mechanistic expectation: this architecture tends to **favor selective, geometry-driven outcomes** when the substrate can be “presented” correctly (e.g., primary-OH targeting on sucrose) because bulky proximal residues can restrict which hydroxyl approaches the acyl-enzyme. At the same time, the lower proximal polarity may reduce strong polyol anchoring, making activity more dependent on lid dynamics and transient binding.
  - In the sugar-ester context (literature you included): TLL is often associated with **6-O monoacylation selectivity** on sucrose; a plausible structural rationale is exactly this: **a shape-selective proximal clamp** that biases which sucrose OH can access the reactive center, while the outer pocket remains permissive enough to accommodate the large sucrose headgroup without forcing deep burial.

---

## 2) Comparative analysis

### A) Intra-protein variant analysis
- No variant families are present in the provided dataset (only **RML_SucroseOleate** and **TLL_SucroseOleate**, no WT/mutant labels). Therefore, no WT-vs-variant comparisons can be performed.

### B) Requested pairwise comparison: **RML vs TLL**

**Proximal electrostatics**
- **RML is more polar proximally** (polar ~0.455 vs 0.409) and less hydrophobic by hw_weighted (≈ -0.404 vs -0.497).
- Mechanistic implication: RML should provide **better polar “landing pads”** for sucrose hydroxyl organization near the catalytic center, potentially improving productive deacylation geometry (synthesis step) and reducing reliance on purely hydrophobic packing.

**Proximal sterics**
- **TLL is bulkier and more heterogeneous proximally** (higher mean/weighted volume and higher variance; bulky fraction 0.477 vs 0.341).
- Mechanistic implication: TLL likely imposes **stronger shape constraints** on how sucrose can sit near the reactive center—consistent with **regioselective monoacylation tendencies** (restricting which OH can approach).

**Distal electrostatics**
- TLL distal shell: **more charged but less polar** (charged 0.20 vs 0.175; polar 0.40 vs 0.456).
- Mechanistic implication: TLL may have more discrete ionic features at the rim/outer shell (possible steering/solvent interactions), but fewer overall polar contacts—potentially promoting a more “interfacial” binding mode rather than deep polyol solvation.

**Distal sterics / outer pocket size**
- **TLL has a larger outer pocket** (greater centroid distances) and higher distal variance.
- Mechanistic implication: TLL can accommodate the bulky sucrose headgroup with less penalty (less need to thread deeply), but that extra space can increase **pose multiplicity**—making proximal steric gating more important for selectivity.

**Pocket-phenotype conclusion (RML vs TLL)**
- **RML:** “pose-guiding amphiphilic channel” → likely more robust productive binding for polar acceptors (sucrose) when access is achieved.  
- **TLL:** “bulky hydrophobic clamp + roomy shell” → likely stronger regioselective presentation (monoacylation bias) but potentially more dependent on dynamics/solvent to achieve productive sugar engagement.

---

## 3) Cross-protein pocket phenotypes (clusters)

With only two proteins, the “clusters” reduce to two archetypes:

1) **Amphiphilic, polarity-supported acceptor binding (RML-like)**
- Hallmarks: higher proximal polar fraction; less hydrophobic proximal hw; moderate steric bulk.
- Trade-off intuition: tends toward **more reliable productive chemistry** for polar acceptors (better orientation/anchoring), potentially at the cost of **less extreme shape-enforced regioselectivity**.

2) **Hydrophobic, bulky proximal gating with expanded outer shell (TLL-like)**
- Hallmarks: higher proximal bulky fraction and variance; more hydrophobic proximal hw; larger distal centroid distances.
- Trade-off intuition: tends toward **higher selectivity via steric presentation** (which OH can reach), but can show **greater sensitivity to lid/open-state population and solvent microenvironment** because polar anchoring is weaker.

If you add more homologs/variants (especially CALB/CALA or RML/TLL mutants), I can turn these into a multi-cluster map (e.g., tight/polar “pose-locking” vs open/hydrophobic “permissive”) and explicitly assign each protein to a phenotype with engineering levers (which residues to polarize, which to debulk, which to widen/narrow distally).

## Stage 2: Residue-Level Mechanistic Drivers

## 1) Key variable pocket positions → residue-level mechanistic hypotheses (RML vs TLL)

Below, “key” means (i) within the filtered pocket set and (ii) plausibly causal for the **RML polar/pose-guiding channel** vs **TLL hydrophobic/bulky proximal clamp + roomier shell** phenotype described in the structural summary.

### A. **RML 83 (S) ↔ TLL 84 (R)**  *(min dist ~3.5–3.6 Å; proximal)*
- **Residues:** RML **Ser83** vs TLL **Arg84**
- **Substitution class:** **Electrostatic + steric** (neutral small polar → **positively charged, bulky**)
- **Mechanistic consequence:**
  - In **TLL**, Arg introduces a **localized cationic “hook”** and a larger sidechain that can **sterically gate** nearby sugar hydroxyls. This matches the summary’s **shape-defining proximal clamp** and can bias which sucrose OH can approach the acyl-enzyme (consistent with TLL’s monoacylation/regioselectivity tendency).
  - In **RML**, Ser keeps this region **smaller and more H-bond permissive without strong ionic steering**, consistent with a **more uniformly polar rim** that “guides” sucrose rather than clamping it.
- **Phenotype tie-back:** This single change can simultaneously explain **(i) higher proximal steric bulk/heterogeneity in TLL** and **(ii) reduced “polyol-friendly” polarity (fewer neutral H-bond donors/acceptors arranged as a network) despite similar charged fraction overall**.

---

### B. **RML 91 (D) ↔ TLL 92 (N)**  *(min dist ~2.37 vs 3.30 Å; very proximal)*
- **Residues:** RML **Asp91** vs TLL **Asn92**
- **Substitution class:** **Electrostatic** (negative → neutral polar amide) + **polarity shift** (ionic → H-bonding)
- **Mechanistic consequence:**
  - **RML Asp91** provides a **fixed negative charge** very close to the ligand. That can create a **strong electrostatic anchor/steering point** for sucrose OH patterning (via direct H-bonds or water-mediated networks), supporting the summary’s **polar proximal “landing pads”** and more reliable productive binding geometries.
  - **TLL Asn92** removes the negative charge, weakening ionic steering and making binding more dependent on **steric presentation** (the “clamp”) and dynamics. This aligns with the summary’s view that TLL has **weaker polar anchoring** near the ligand.
- **Mechanistic prediction:** D→N in this location should **increase pose degeneracy** and potentially **increase reliance on proximal bulky residues to enforce regioselectivity** (i.e., selectivity maintained by shape rather than electrostatic anchoring).

---

### C. **RML 215 (F) ↔ TLL 213 (Y)**  *(min dist ~6.8 Å; distal/moderately close)*
- **Residues:** RML **Phe215** vs TLL **Tyr213**
- **Substitution class:** **Polarity shift** (hydrophobic aromatic → aromatic with **phenolic OH**)
- **Mechanistic consequence:**
  - **TLL Tyr213** can add a **rim H-bond donor/acceptor** that may interact with sucrose at the **outer shell**, consistent with the summary’s **more charged/mixed distal shell** and “interfacial” binding mode.
  - **RML Phe215** keeps this region more purely hydrophobic/aromatic, consistent with RML’s **hydrophobic runway outward** while keeping key polarity more proximal.
- **Mechanistic prediction:** This is more likely a **secondary modulator**: it can tune **entry/exit and outer-shell residence time** (and thus effective on-rate/pose filtering), rather than directly controlling reactive-center geometry.

---

### D. **RML 174 (Q) ↔ TLL 171 (Y)**  *(~7.5–7.8 Å; distal)*
- **Residues:** RML **Gln174** vs TLL **Tyr171**
- **Substitution class:** **Steric + polarity shift** (flexible polar amide → bulkier aromatic with phenolic OH)
- **Mechanistic consequence:**
  - **TLL Tyr171** can contribute to the **bulkier, more structured outer shell** (summary: larger distal centroid distances + higher variance). Aromatic packing can create **shape features** that help “stage” the sucrose headgroup without deep burial.
  - **RML Gln174** is more flexible and polar, consistent with a **more continuously polar surface** that can accommodate multiple H-bonding patterns (pose-guiding rather than clamping).
- **Mechanistic prediction:** Likely affects **outer-shell shaping and solvent exposure** of the sugar, influencing **pose multiplicity** and possibly product distribution (mono vs further acylation) indirectly.

---

### E. **RML 265 (T) ↔ TLL 265 (I)**  *(min dist ~2.91 vs 3.97 Å; proximal)*
- **Residues:** RML **Thr265** vs TLL **Ile265**
- **Substitution class:** **Polarity + steric** (small polar → hydrophobic, slightly bulkier)
- **Mechanistic consequence:**
  - **TLL Ile265** increases **local hydrophobicity** near the ligand and removes an H-bonding handle, consistent with the summary’s **more hydrophobic proximal clamp**.
  - **RML Thr265** supports the **polar proximal microenvironment** and could help stabilize a productive sucrose OH orientation (directly or via structured water).
- **Mechanistic prediction:** This position is a plausible contributor to the **RML “polyol-friendly” proximal region** vs **TLL hydrophobic gating**.

---

### F. **RML 264 (N) ↔ TLL 264 (L)**  *(~6–7.9 Å; distal/edge)*
- **Residues:** RML **Asn264** vs TLL **Leu264**
- **Substitution class:** **Polarity shift** (polar → hydrophobic)
- **Mechanistic consequence:**
  - **TLL Leu264** reinforces a **hydrophobic wall** at/near the pocket periphery, consistent with the summary’s **hydrophobic inner clamp** architecture.
  - **RML Asn264** maintains a polar feature that can support **sucrose approach/solvation** at the rim.
- **Mechanistic prediction:** More of a **secondary modulator** (rim wetting/entry energetics) than a direct reactive-center clamp.

---

### G. **RML 303? (L267) ↔ TLL 267 (T)**  *(min dist ~3.78 vs 5.15 Å; proximal-to-mid)*
- **Residues:** RML **Leu267** vs TLL **Thr267**
- **Substitution class:** **Polarity shift** (hydrophobic → polar)
- **Mechanistic consequence (context-dependent):**
  - This is one of the few changes that would make **TLL locally more polar** than RML. If oriented toward the ligand, **Thr267** could partially compensate for TLL’s reduced proximal polarity elsewhere (e.g., D→N at 92; T→I at 265).
  - However, the larger TLL “clamp” phenotype suggests that even if Thr is present, the **net proximal environment** is still more shape/sterics-driven.
- **Mechanistic prediction:** likely a **fine-tuner** of local H-bonding rather than a primary driver.

---

### H. Other variable positions that are mostly steric/background in this context
- **RML 90 (A) ↔ TLL 91 (G):** small↔small; minor packing/dynamics effect.
- **RML 93 (T) ↔ TLL 94 (N):** polar↔polar; modest H-bond pattern change, likely secondary.
- **RML 207 (H) ↔ TLL 205 (R):** charge-capable↔positive; but distances here are ~7 Å min—more likely distal electrostatic steering than direct clamp.
- **RML 254 (V) ↔ TLL 255 (I):** hydrophobic↔hydrophobic; small steric tweak.
- **RML 259 (S) ↔ TLL 260 (W):** big steric change but at ~7.6–7.7 Å; could shape outer shell, but less directly tied to the “proximal clamp” unless this residue points inward in the open state.

---

## 2) Variant-within-family contrasts
Only **two base sequences (RML vs TLL)** are present; there are **no intra-family variants** (WT vs mutants) in the provided alignment table, so I can’t do “point mutations in variants of the same base sequence” comparisons from this dataset.  
If you provide RML-mutant/TLL-mutant rows, the same framework above will map each mutation onto the **polar-channel vs hydrophobic-clamp** axes.

---

## 3) Ranked residue list (mechanistic drivers vs modulators vs likely neutral)

### High-confidence mechanistic driver residues (most likely causal for phenotype differences)
1. **RML Ser83 ↔ TLL Arg84** — introduces **bulky positive gate** in TLL (steric + electrostatic); matches “proximal clamp”.
2. **RML Asp91 ↔ TLL Asn92** — removes **proximal negative anchor** in TLL; matches reduced polyol-friendly anchoring.
3. **RML Thr265 ↔ TLL Ile265** — polar→hydrophobic near ligand; supports RML polar proximal vs TLL hydrophobic clamp.

### Secondary modulators (tune rim wetting, outer-shell shaping, pose multiplicity)
- **RML Asn264 ↔ TLL Leu264** — polar→hydrophobic at rim/edge.
- **RML Gln174 ↔ TLL Tyr171** — flexible polar→aromatic polar; outer-shell shaping.
- **RML Phe215 ↔ TLL Tyr213** — adds phenolic OH; distal H-bonding/entry effects.
- **RML Leu267 ↔ TLL Thr267** — hydrophobic→polar; local compensation/fine-tuning.
- **RML His207 ↔ TLL Arg205** — distal electrostatic steering (context-dependent).

### Likely neutral/background (small effects or conservative swaps in this pocket context)
- **RML Ala90 ↔ TLL Gly91**
- **RML Thr93 ↔ TLL Asn94**
- **RML Val254 ↔ TLL Ile255**
- (Most other listed positions are conserved between RML and TLL in this filtered pocket set.)

If you share the **3D orientation** (sidechain vectors) for the top candidates (83/91/265/264) in the open-state structures, I can tighten these into testable hypotheses (e.g., predicted H-bond partners on sucrose; expected shifts in reactive-center approach angles; which OH becomes sterically excluded).