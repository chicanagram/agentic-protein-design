## 1) Design Intent
- **Backbone protein:** **ET096**
- **Objective:** Shift ET096 from a **hydrophobic/permissive, over-oxidation–prone pocket** toward a more **pose-locking / mono-oxidation–biased** catalyst for **peroxygenative mono-oxidation on S82**, while **retaining useful activity** and **reducing Di-Ox (over-oxidation)**.

Mechanistic basis from prompt_2_output: ET096’s permissive/“dry” behavior is linked to (i) lack of a **proximal H-bond anchor** at **A171** (vs CviUPO T158), (ii) lack of a **distal-shell positive electrostatic gate** at **A178** (vs CviUPO K165), and (iii) a **roomier steric environment** at **A80** (vs bulkier/rigidifying residues in other UPOs). We will introduce **minimal polarity/steric “clamping”** at these ET096 positions.

---

## 2) Proposed Mutations (ranked)

### 1) **A171T**
- **Rationale (driver):** Position **ET096 171 = A** corresponds to the **T158 anchor site** in CviUPO; prompt_2 links Thr here to **H-bond anchoring/pose registration** and mono-bias, while Ala correlates with **pose degeneracy and di-oxidation**.
- **Expected effect:** **Increase mono-oxidation selectivity**, reduce Di-Ox by reducing substrate reorientation/rebinding.
- **Risk/tradeoff:** Could **reduce kcat** if the new H-bond network over-constrains binding or perturbs local water structure.
- **Confidence:** **High**

### 2) **A178K**
- **Rationale (driver):** ET096 has **A178** where CviUPO has **K165**, described as an **electrostatic gate / solvent organizer** supporting a more polar/charged environment and pathway bias away from “dry permissive” behavior.
- **Expected effect:** **Reduce over-oxidation** by (i) increasing organized polarity near pocket edge (less “slippery” trajectories) and (ii) potentially altering peroxide/water organization to favor productive peroxygenation over repeated turnovers on product.
- **Risk/tradeoff:** Lys introduction can **destabilize** (buried charge) or **increase peroxidative side activity** depending on how it couples to electron-transfer/water networks (literature notes ABTS is a sensitive peroxidase reporter; this could move the wrong way).
- **Confidence:** **Medium-high** (strong mechanistic lever, but charge burial risk)

### 3) **A80L**
- **Rationale (modulator):** Prompt_2 flags ET096 **A80** as a “small hinge” contributing to a **roomier microcavity** and mobility/di-oxidation. Moving toward **L (as in CviUPO/OA167)** should partially **tighten** and reduce pose multiplicity without extreme bulk.
- **Expected effect:** **Improved mono-selectivity** (more caging), modest activity impact.
- **Risk/tradeoff:** Could **reduce substrate access** if this region is part of the entry path; may lower total turnover.
- **Confidence:** **Medium**

### 4) **A80P**
- **Rationale (modulator):** TE314 has **P84**, proposed to act as a **conformational gate** (rigidifies local backbone). Proline can reduce “breathing” that enables reorientation/rebinding.
- **Expected effect:** **Lower Di-Ox** by restricting pocket dynamics; may sharpen product profile.
- **Risk/tradeoff:** Proline can be **structurally disruptive** (backbone strain) and harm expression/folding.
- **Confidence:** **Low-medium**

### 5) **A77T**
- **Rationale (modulator):** ET096 **A77** sits at a “charge/polarity hotspot” where CviUPO/TE314 have **T** (H-bonding without full charge). This is a conservative way to **increase proximal polarity** without introducing a formal charge (vs D58 in DcaUPO).
- **Expected effect:** Slight **increase in pose registration** / hydration control → **reduced over-oxidation**.
- **Risk/tradeoff:** Effect may be **small** alone.
- **Confidence:** **Medium**

### 6) **A171T + A178K** (double)
- **Rationale:** Combine the two **highest-confidence mechanistic drivers**: add **H-bond anchor** (171) + **electrostatic gate** (178). This is the most direct “ET096 → more clamp-like” conversion per prompt_2.
- **Expected effect:** Strongest predicted **mono-bias**; may also improve coupling/productive trajectories.
- **Risk/tradeoff:** Higher chance of **activity loss** or **mis-tuned peroxidation** (monitor ABTS/NBD-type split; see plan).
- **Confidence:** **Medium-high**

### 7) **A171T + A80L** (double)
- **Rationale:** Pair **pose anchor** (171T) with **steric tightening** (80L) to reduce both rotational freedom and microcavity “slip.”
- **Expected effect:** **Mono-selectivity up**, Di-Ox down; potentially better than either alone.
- **Risk/tradeoff:** Could **over-restrict** and reduce conversion on S82.
- **Confidence:** **Medium**

### 8) **A178K + A80L** (double)
- **Rationale:** Combine **electrostatic steering/solvent organization** (178K) with **steric caging** (80L).
- **Expected effect:** Reduced Di-Ox; may preserve activity better than adding the 171T anchor (depends on S82’s functional groups).
- **Risk/tradeoff:** Same charge-burial concern as A178K; plus possible access limitation.
- **Confidence:** **Medium**

### 9) **Focused exploration at 171: {A171T, A171S}**
- **Rationale:** Prompt_2’s key is “H-bond anchor vs none.” **Ser** is a more conservative anchor than Thr (less steric), sometimes better if space is tight.
- **Expected effect:** Tune mono-bias vs activity tradeoff.
- **Risk/tradeoff:** Requires 1–2 extra constructs; still small.
- **Confidence:** **Medium**

### 10) **Focused exploration at 178: {A178K, A178R}**
- **Rationale:** If positive charge is beneficial, **Arg** can provide a different geometry/H-bonding pattern than Lys (sometimes less destabilizing depending on burial and H-bond partners).
- **Expected effect:** Similar direction as K; may improve stability or reduce unintended peroxidation.
- **Risk/tradeoff:** Arg can be even harder to bury; could worsen expression.
- **Confidence:** **Low-medium**

---

## 3) Minimal Experimental Plan

### First-round variant panel (≤12; high-information)
Include WT as baseline (not counted as a “variant” if you prefer, but include in assays).

1. **A171T**
2. **A171S** (anchor strength titration)
3. **A178K**
4. **A178R** (charge geometry test)
5. **A80L**
6. **A80P** (dynamic gate test; higher risk but informative)
7. **A77T**
8. **A171T/A178K**
9. **A171T/A80L**
10. **A178K/A80L**
11. **A171T/A77T** (anchor + local polarity)
12. **A171T/A178K/A80L** (triple “clamp package”; only if expression is acceptable—otherwise swap for **A171T/A178K + A77T**)

### Assay/readouts aligned to objective (mono-oxidation on S82; suppress Di-Ox)
- **Primary analytics:** Quantify **Mono-Ox vs Di-Ox** on **S82** by **LC-MS (or GC-MS if derivatized/volatile)** at multiple timepoints (early + near-complete conversion). Report **Mono:Di ratio** and **TTN**.
- **Coupling / side-pathway counterscreen (literature-supported):**
  - Run a **peroxidase reporter** (e.g., **ABTS oxidation**) in parallel to detect variants drifting toward 1e⁻ chemistry (literature_context highlights ABTS as robust peroxidase readout).
  - If available, include a **peroxygenation reporter** (e.g., **NBD**) to ensure you’re not selecting “low ABTS because dead enzyme.”
- **Process control (to avoid confounding):** Use **controlled H₂O₂ delivery** (fed-batch or low steady-state) because overoxidation and inactivation are peroxide-sensitive in UPOs (literature_context). Keep identical peroxide profiles across variants.

Decision rule after round 1: advance variants that **increase Mono:Di** at matched conversion (or matched TTN) and do **not** show a disproportionate increase in ABTS activity relative to S82 peroxygenation.

---

## 4) Rejected Alternatives (deprioritized)
1. **Introduce a negative charge at 77 (A77D/E)**  
   - Prompt_2 notes DcaUPO has a D at the analogous site (D58), but ET096 is in the “dry/permissive” cluster; adding a negative charge is **less conservative** and could unpredictably alter peroxide/water networks or destabilize.
2. **Large aromatic “clamp” insertions at ET096 positions not explicitly mapped**  
   - Prompt_2’s aromatic clamp discussion is for **CviUPO F88** vs aliphatic; ET096’s exact equivalent position is not provided here, so proposing new aromatic clamps would violate the “don’t invent numbering/mapping” constraint.
3. **Multi-site broad hydrophobic repacking (many conservative hydrophobe swaps)**  
   - Prompt_2 labels many hydrophobe-only positions as likely **background/neutral**; these are lower leverage than the clear driver sites (171, 178) and would burn mutation budget.
4. **Aggressive pocket plugging with Phe at 80 (A80F)**  
   - Although DcaUPO has a bulky aromatic at the analogous site (F62), this is a **large steric jump** likely to crush activity on S82; start with **L** (and optionally P) first.

If you can share whether S82 has a polar handle (H-bond acceptor/donor) near the oxidation site, I’d prioritize **A171T vs A171S** differently (Thr is better for stronger registration; Ser is safer if space is tight).