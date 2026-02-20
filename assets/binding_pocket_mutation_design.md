## 1) Design Intent
- **Backbone protein:** **ET096**
- **Objective:** Shift ET096 from a “dry-core permissive oxidizer” toward **higher peroxygenative mono-oxidation (Mono-Ox) selectivity on S82**, while **retaining useful turnover** and **reducing Di-Ox/over-oxidation** propensity.

Mechanistic framing from `prompt_2_output`: ET096 lacks (i) the **proximal electrostatic handle** (CviUPO K165 ↔ ET096 A178), and (ii) strong **pose-clamping elements** (ET096 I103 and A171 are permissive). ET096 also has a **bulky bump at L174** where several other scaffolds have **Gly**, suggesting ET096 may deflect substrates into multiple orientations rather than enforcing one productive pose.

---

## 2) Proposed Mutations (ranked)

### 1) **A178K**
- **Rationale (driver):** Directly installs the **CviUPO-like “electrostatic handle”** at the key proximal site (ET096 A178 ↔ CviUPO K165). `prompt_2_output` links this handle to **pose-locking** and to suppressing “permissive” rebinding/reorientation that can enable **Di-Ox drift**.
- **Expected effect:** ↑ Mono-Ox selectivity (better pose steering); potentially ↓ Di-Ox via reduced pose degeneracy.
- **Risk/tradeoff:** Could increase **peroxidative/ET-like side chemistry** (CviUPO K165 is associated with high ABTS peroxidation in the summary) and/or reduce activity if it over-constrains binding.
- **Confidence:** **High**

### 2) **L174G**
- **Rationale (driver):** Converts ET096’s **bulky L174** (unique vs G in CviUPO/DcaUPO/TE314) into a **minimal “void/hinge”** residue. `prompt_2_output` suggests ET096’s L174 may act as an **asymmetric steric bump** that *deflects* substrates into multiple orientations—consistent with permissive over-oxidation.
- **Expected effect:** ↓ Di-Ox (less deflection-driven reorientation); may also ↑ activity if it relieves unproductive clashes.
- **Risk/tradeoff:** Too much openness can also increase binding-mode multiplicity; effect could be substrate-dependent.
- **Confidence:** **Medium**

### 3) **I103F**
- **Rationale (driver):** ET096 has **I103** where CviUPO has **F88**, a rigid **π-wall** that increases **shape complementarity/pose clamp**. Installing Phe is a conservative “one-step” toward a more directive wall without changing size drastically.
- **Expected effect:** ↑ Mono-Ox selectivity via stronger pose control; potentially ↓ Di-Ox by reducing rebinding orientations.
- **Risk/tradeoff:** Could over-stabilize an aromatic pose that is *not* the productive line-of-attack (opposite of the CviUPO F88L logic), lowering rate.
- **Confidence:** **Medium**

### 4) **A171T**
- **Rationale (driver):** ET096 A171 corresponds to CviUPO **T158** (a polar H-bond node). `prompt_2_output` ties T158 to **pose-locking / polar network organization**. Adding Thr may reduce pose degeneracy by introducing a **single anchoring interaction**.
- **Expected effect:** ↑ Mono-Ox selectivity (pose anchoring).
- **Risk/tradeoff:** Added polarity can increase “sticking” and potentially support peroxidative side pathways or slow product release (could worsen Di-Ox if retention dominates).
- **Confidence:** **Medium**

### 5) **A171V (or A171L) — focused exploration**
- **Rationale (driver):** Alternative to A171T: instead of adding polarity, add **steric packing** to enforce proximity/orientation (analogous in spirit to “steric clamp” logic; `prompt_2_output` notes DcaUPO uses hydrophobic clamping rather than polarity).
- **Expected effect:** ↑ Mono-Ox selectivity by narrowing pose space; may ↓ Di-Ox by limiting re-binding orientations.
- **Risk/tradeoff:** Higher chance of activity loss from over-constriction.
- **Confidence:** **Low–Medium**

### 6) **A178K + L174G (double)**
- **Rationale (drivers):** Combine **electrostatic steering** (A178K) with removal of the **deflecting bump** (L174G). Mechanistically: fewer orientations available + stronger steering toward the productive one.
- **Expected effect:** Stronger ↑ Mono-Ox selectivity and ↓ Di-Ox than either alone.
- **Risk/tradeoff:** Epistasis risk (could open pocket too much while adding charge, changing binding unexpectedly).
- **Confidence:** **Medium**

### 7) **A178K + I103F (double)**
- **Rationale (drivers):** Combine the **electrostatic handle** with a **π-wall clamp** to mimic the CviUPO “pose-locking” phenotype (but in ET096 numbering).
- **Expected effect:** ↑ Mono-Ox selectivity; potentially improved catalytic positioning.
- **Risk/tradeoff:** Could push ET096 toward a more CviUPO-like peroxidative tendency (handle-associated) and/or reduce activity by over-constraining.
- **Confidence:** **Medium**

### 8) **L174G + I103F (double)**
- **Rationale (drivers):** Remove the steric “bump” while adding a more directive wall—i.e., **replace accidental sterics with intentional sterics**.
- **Expected effect:** ↓ Di-Ox and ↑ Mono-Ox selectivity.
- **Risk/tradeoff:** If L174 was actually providing needed packing for productive binding, activity could drop.
- **Confidence:** **Low–Medium**

### 9) **Position-level exploration: A178 {K, R, Q}**
- **Rationale (driver):** `prompt_2_output` highlights “charged vs neutral” as dominant. A small set tests: **K** (Cvi-like), **R** (stronger/less flexible guanidinium), **Q** (polar but uncharged “handle-lite”).
- **Expected effect:** Tune steering vs peroxidation risk.
- **Risk/tradeoff:** R may be too strong/rigid; Q may be too weak to matter.
- **Confidence:** **Medium**

---

## 3) Minimal Experimental Plan

### First-round variant panel (12 max; high-information)
Include singles to map main effects + a few doubles for synergy/epistasis:

1. **WT ET096**
2. **A178K**
3. **L174G**
4. **I103F**
5. **A171T**
6. **A178R** (tests “charge strength/geometry” at the handle)
7. **A178Q** (tests “polar handle without full charge”)
8. **A178K/L174G**
9. **A178K/I103F**
10. **L174G/I103F**
11. **A178K/A171T**
12. **A171V** (steric clamp alternative at 171)

(If expression/throughput is tight, drop #6–7 and keep only A178K plus the three doubles.)

### Assay/readout plan (aligned to Mono-Ox vs Di-Ox)
- **Primary selectivity assay (must-have):** Analytical quantification of **S82 Mono-Ox vs Di-Ox** (LC/GC depending on S82 chemistry). Report **%Mono-Ox at fixed conversion** and **Mono/Di ratio**.
- **Activity retention:** Initial rate or TTN under standardized **H₂O₂ delivery** (continuous low-dose preferred to reduce non-enzymatic over-oxidation artifacts).
- **Mode-bias diagnostics (optional but compact):**
  - **NBD** (peroxygenase reporter) and **ABTS** (peroxidase reporter) as a quick screen for shifts in peroxygenative vs peroxidative tendency (literature platforms use this dual readout).
  - Track whether **A178K (and combos)** increases ABTS disproportionately (a warning sign for peroxidative leakage).

---

## 4) Rejected Alternatives (deprioritized)
1. **L174F** (or other bulky aromatics at 174): could create an OA167-like “sticky binder” behavior; `prompt_2_output` links OA167 F177 to **retention + reorientation → Di-Ox drift** risk.
2. **A178A/V/C (staying neutral):** contradicts the strongest mechanistic lever identified (charged vs neutral switch at this proximal site); unlikely to move selectivity meaningfully.
3. **I103L/I103A:** F→L was beneficial in *CviUPO variant context* (relieving π-stacking), but ET096 already lacks π-constraint (I103). Further “softening” likely increases permissiveness/Di-Ox.
4. **Large multi-site libraries beyond these four positions:** violates the “conservative, mechanistically justified” requirement and increases screening burden without clear causal anchors from `prompt_2_output`.
5. **Mutating positions labeled “likely neutral/background” in `prompt_2_output` (e.g., index 100/104 hydrophobes):** expected smaller/indirect effects; lower information per variant in a first round.

If you share what **S82** is (structure/class, where Mono-Ox occurs, what Di-Ox product is), I can tighten the panel further (e.g., choose between **A171T vs A171V** depending on whether you need H-bond anchoring or steric gating).