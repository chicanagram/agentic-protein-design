## 1) Design Intent
- **Backbone protein:** **ET096**
- **Objective:** Increase **peroxygenative mono‑oxidation selectivity** on **S82** while retaining useful activity and **reducing Di‑Ox (over‑oxidation)**. Strategy: strengthen **pose-locking/steering near the reactive center** and reduce **product trapping/rebinding** that enables secondary oxidation.

---

## 2) Proposed Mutations (ranked)

### 1) **A178K**
- **Rationale (prompt_2 driver):** ET096 **A178** aligns to **CviUPO K165**, identified as a **unique electrostatic hotspot** providing **cationic steering** and water organization that supports “pose-locking clamp” behavior. ET096 lacks this feature (A178), consistent with weaker steering and more over‑oxidation.
- **Expected effect:** **↑ mono-selectivity**, **↓ pose degeneracy**; may also **↑ apparent activity** if productive binding increases.
- **Risk/tradeoff:** Introducing a Lys could **destabilize** if buried or could **increase peroxidative ET** for redox-active substrates by stabilizing charged intermediates; also possible **KM increase** if S82 is hydrophobic and dislikes added polarity.
- **Confidence:** **Medium–High** (strong mechanistic link; single-site, conservative in “function class” though not in chemistry).

### 2) **A77T**
- **Rationale:** ET096 **A77** is a “reactive-center approach/gating” position; CviUPO/TE314 have **Thr** here, providing an **H-bond-capable polar handle** that can bias approach geometry and reduce unproductive orientations.
- **Expected effect:** **↑ mono-selectivity**, potentially **↓ Di‑Ox** by reducing reorientation of product near Fe=O.
- **Risk/tradeoff:** Added polarity could **slow binding** of very hydrophobic substrates or alter water occupancy (possible uncoupling changes).
- **Confidence:** **Medium**

### 3) **A80L** (steric “back-wall packing”)
- **Rationale:** ET096 **A80** is explicitly linked to a **small, slick proximal environment** → easier reorientation/rebinding → **Di‑oxidation bias**. Replacing with a bulkier residue (like **L** seen in CviUPO/OA167 at the aligned site) should convert the cavity toward a **more clamp-like architecture**.
- **Expected effect:** **↓ Di‑Ox**, **↑ mono-selectivity** via tighter pose enforcement; may reduce off-pathway poses.
- **Risk/tradeoff:** Could **reduce activity** if S82 requires space for productive binding/transition state; may increase substrate discrimination (higher KM).
- **Confidence:** **High** (directly tied to the “slick vs clamp” driver in prompt_2)

### 4) **A80F** (stronger clamp / π buttress)
- **Rationale:** DcaUPO has **F62** at the aligned position, proposed to act as an **aromatic buttress** enforcing productive pose even in hydrophobic pockets. For ET096, adding **Phe** at 80 is a direct way to increase **steric + dispersion pose-locking**.
- **Expected effect:** Strong **↓ Di‑Ox** and potentially **↑ regio/mono-selectivity** if S82 benefits from a fixed orientation.
- **Risk/tradeoff:** Higher chance of **over-tightening** (activity loss) vs A80L; could also increase **product retention** if π-stacking traps aromatic products.
- **Confidence:** **Medium**

### 5) **I103F** (introduce aromatic “pose-lock / clamp” wall)
- **Rationale:** ET096 **I103** corresponds to the “pose-lock/clamp” position where CviUPO WT has **F88** (bulky aromatic wall enabling π/dispersion anchoring). ET096 has aliphatic I, consistent with weaker pose-locking.
- **Expected effect:** **↑ mono-selectivity** (better pose control); may reduce Di‑Ox by limiting product reorientation.
- **Risk/tradeoff:** Could **reduce turnover** if steric clash occurs; aromatic wall might **increase distal/proximal stickiness** depending on S82/product aromaticity.
- **Confidence:** **Medium**

### 6) **I103L** (conservative steric smoothing without π)
- **Rationale:** Same clamp position; prompt_2 notes F↔aliphatic changes tune **sterics and polarizability**. If I103F is too aggressive, I103L is a conservative way to subtly reshape packing.
- **Expected effect:** Mild **↑ mono-selectivity** / **↓ Di‑Ox** (smaller effect than I103F).
- **Risk/tradeoff:** Might be **too subtle** to move selectivity.
- **Confidence:** **Low–Medium**

### 7) **F223L** (reduce distal retention / product trapping)
- **Rationale:** ET096 **F223** is highlighted as increasing **distal “stickiness”** via π/dispersion, consistent with **lingering/re-entry** that can promote over‑oxidation in an otherwise dry inner pocket. Swapping to Leu reduces polarizability while keeping hydrophobic packing.
- **Expected effect:** **↓ Di‑Ox** by promoting **product release**; may improve TTN by reducing repeated oxidation cycles.
- **Risk/tradeoff:** Could **lower binding/occupancy** (activity drop) if F223 contributes to initial substrate capture.
- **Confidence:** **Medium**

### 8) **Focused exploration at position 80 (mini-library): A80{L,F}** (if only one “exploration” slot is allowed)
- **Rationale:** Position 80 is the clearest “architecture switch” driver for slick vs clamp behavior in prompt_2. Testing two chemically distinct bulky options (L vs F) quickly maps whether **steric bulk alone** or **aromatic buttressing** is needed.
- **Expected effect:** Identify best tradeoff between **activity vs mono-selectivity**.
- **Risk/tradeoff:** Requires 2 variants but high information yield.
- **Confidence:** **High** (as an exploration strategy)

---

## 3) Minimal Experimental Plan

### First-round variant panel (≤12; high-information, mostly single mutants + 2 doubles)
1. **WT ET096** (baseline)
2. **A80L**
3. **A80F**
4. **A178K**
5. **A77T**
6. **I103F**
7. **F223L**
8. **I103L** (optional if you want a conservative comparator; otherwise drop)
9. **A80L/A178K** (combine steric clamp + electrostatic steering)
10. **A80L/F223L** (clamp + faster product release to suppress Di‑Ox)
11. **A77T/A80L** (gating polar handle + clamp)
12. **I103F/A80L** (two clamp walls; include only if expression/activity is typically robust)

If you need to cut to 10 variants: drop **I103L** and **I103F/A80L** first.

### Assay/readout plan (aligned to mono-oxidation selectivity)
- **Primary analytics:** Quantify **Mono‑Ox vs Di‑Ox** products for **S82** by **LC/GC** (time course recommended to distinguish “true selectivity” from “sequential over-oxidation”).
  - Report: initial rate to Mono‑Ox, **Mono:Di ratio** at fixed conversion (e.g., 20–30% and 80–90%), and apparent **kcat/KM** proxy if feasible.
- **Process control to reveal over-oxidation propensity:** run two peroxide regimes:
  1) **Low, controlled H₂O₂ feed** (minimizes nonproductive oxidation; better reflects intrinsic selectivity)
  2) **Single bolus** (stress test; reveals variants prone to product trapping/rebinding and Di‑Ox)
- **Side-activity channeling check (optional but useful):** a simple **ABTS** rate assay as a *peroxidative flux indicator* (not a success metric). Variants that increase ABTS strongly while not improving Mono:Di may be shifting toward peroxidation rather than productive peroxygenation (consistent with literature_context caution).

---

## 4) Rejected Alternatives (deprioritized)
1. **Large “opening” mutations at clamp sites (e.g., I103A)**  
   - Prompt_2 links “small/slick” pockets to **pose degeneracy and Di‑Ox**; opening further is opposite of the mono-selectivity goal.
2. **Adding a negative charge at ET096 77 (A77D)**  
   - While DcaUPO D58 is a notable negative electrostatic driver, that’s a *different aligned position* (DcaUPO 58). For ET096, introducing Asp at 77 risks **mis-steering** and **uncoupling** without strong support from prompt_2.
3. **Aggressive aromatic increase at distal site (e.g., making F223 even bulkier/polarizable)**  
   - Prompt_2 suggests ET096 F223 already contributes to **distal retention**; increasing this likely **worsens Di‑Ox**.
4. **Mutating “likely neutral/background” positions (e.g., ET096 74V or 172S)**  
   - Prompt_2 explicitly flags these as unlikely to drive the phenotype shifts; low expected information yield for a first round.

If you share what **S82** is chemically (size/polarity; whether Mono‑Ox is hydroxylation vs epoxidation vs something else), I can tighten the ranking (especially I103F vs A178K priority) based on whether you want more **π-clamping** or more **polar steering**.