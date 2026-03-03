## 1) Design Intent
- **Backbone protein:** **ET096** (UPO).
- **Objective:** Increase **peroxygenative mono‑oxidation selectivity on S82** (raise Mono:Di ratio / suppress di‑oxidation) while **retaining useful activity**. Strategy: **increase pose-locking and guided anisotropic sterics** in the proximal pocket (ET096 is “wide/dry/permissive”), and optionally add a **near-pocket electrostatic handle** to reduce rotational freedom/product rebinding.

---

## 2) Proposed Mutations (ranked)

### 1) **Introduce a “missing hydrophobic wall” at the ET096 deletion (row index 104)**
- **Proposal:** **Insert Leu or Ile at the ET096 gap** corresponding to **CviUPO I61 / DcaUPO L59 / TE314 L81 / OA167 L77**.
- **Rationale (prompt_2 driver A):** This is the strongest single steric driver: ET096 uniquely lacks a side chain at ~3.3–3.6 Å from ligand in other homologs → excess free volume → more microstates and easier product reorientation/rebinding → **di‑oxidation permissiveness**.
- **Expected effect:** **↑ pose-locking, ↓ product rebinding, ↑ Mono:Di**, likely some **↓ overall scope** (tighter pocket).
- **Risk/tradeoff:** Insertion can perturb local backbone/loop geometry and expression; may reduce activity if it blocks productive binding.
- **Confidence:** **High** (mechanistically direct; strongest structural contrast in prompt_2).

### 2) **Add a proximal electrostatic “handle” like CviUPO K165**
- **Proposal:** **A178K** (ET096 A178 → Lys).
- **Rationale (driver B):** CviUPO has **K165 at 3.38 Å** vs ET096 **A178 at 4.18 Å**; a localized + charge can create steering/H-bond networks (direct or water-mediated) that **reduces rotational freedom** and can bias productive approach.
- **Expected effect:** **↑ pose definition / anchoring → ↑ mono-selectivity**, potentially **↑ peroxidative tendency** if it stabilizes charge-transfer/radical pathways (literature flags peroxidation competition; ABTS is a reporter).
- **Risk/tradeoff:** Could increase peroxidase-like 1e⁻ chemistry (undesired overoxidation) or destabilize if it introduces buried charge.
- **Confidence:** **High**

### 3) **Build DcaUPO-like anisotropic sterics near the reactive locus**
- **Proposal:** **A171F** (ET096 A171 → Phe).
- **Rationale (driver F):** DcaUPO **F154 at 3.54 Å** is proposed to enforce **directional walling** that yields “reactive but guided” placement and discourages alternative/second-oxidation poses. ET096 A171 is farther/less guiding.
- **Expected effect:** **↑ guided approach / ↓ alternative poses → ↑ Mono:Di**, may also shift regioselectivity on S82 if multiple sites exist.
- **Risk/tradeoff:** Bulky aromatic may over-restrict and reduce turnover if it blocks access or forces nonproductive binding.
- **Confidence:** **Medium-high** (strong driver in DcaUPO; mapping to ET096 assumes comparable geometry at this aligned row).

### 4) **Add a “cap/roof” residue to reduce vestibule openness**
- **Proposal:** **A173Y** (ET096 A173 → Tyr).
- **Rationale (modulator E):** CviUPO has **Y160 (~5.8 Å)** acting as a bulky polarizable cap; ET096 has **A173 (~8.2 Å)** consistent with open vestibule/weak retention control. Adding Tyr can increase **retention in a defined pose** and reduce re-binding microstates that enable di‑oxidation.
- **Expected effect:** **↑ pose-locking / ↓ di‑oxidation**, possibly **↓ kcat** if product release becomes limiting.
- **Risk/tradeoff:** Tyr can introduce new H-bonding/water structure; may increase residence time and paradoxically allow overoxidation if product remains bound too long (depends on whether di‑ox is rebound-driven vs same-binding-event).
- **Confidence:** **Medium**

### 5) **Tighten inner pocket volume at ET096 A80 (small-residue permissiveness)**
- **Proposal:** **A80L** (or **A80F** as a stronger clamp).
- **Rationale (modulator G2):** ET096 **A80** is much smaller than **F/L/P** in other homologs; contributes to widened inner pocket and weaker shape complementarity.
- **Expected effect:** **↑ shape complementarity / ↓ alternative poses → ↑ Mono:Di**.
- **Risk/tradeoff:** Could reduce activity if it clashes with S82 binding mode; Phe especially may over-pack.
- **Confidence:** **Medium**

### 6) **Increase steric bulk at the very close-contact position V74**
- **Proposal:** **V74L**.
- **Rationale (modulator G1):** ET096 **V74 at 2.94 Å** is a very close contact but relatively small; other homologs often have **Leu** here. Slightly larger hydrophobe can improve packing and reduce microstate diversity without introducing polarity.
- **Expected effect:** **Modest ↑ pose stability → modest ↑ mono-selectivity**, likely minimal effect on expression.
- **Risk/tradeoff:** Small risk of steric clash due to very close distance; could reduce activity if it blocks productive approach.
- **Confidence:** **Medium**

### 7) **Tune the “inner-wall” driver position L174 toward OA167-like bulky walling**
- **Proposal:** **L174F**.
- **Rationale (driver D):** OA167 **F177 at 3.38 Å** creates a bulky hydrophobic wall; ET096 has **L174 at 3.40 Å**. Increasing aromatic bulk can enforce a more constrained orientation.
- **Expected effect:** **↑ hydrophobic caging / ↑ orientation constraint → ↑ Mono:Di**.
- **Risk/tradeoff:** OA167 phenotype is described as **di‑oxidation prone** despite bulky walling (prompt_2), so adding bulk alone may not fix overoxidation unless combined with anchoring/cap; could also increase retention and allow sequential oxidation in-pocket.
- **Confidence:** **Low-medium** (mechanistic ambiguity: bulky wall can either help pose-locking or increase retention/overoxidation).

### 8) **Introduce DcaUPO-like negative electrostatic bias (longer-range steering)**
- **Proposal:** **A77D**.
- **Rationale (modulator C):** DcaUPO has **D58** where others are neutral; could bias approach/orientation and water structure. ET096 has **A77 at 3.94 Å** (closer than DcaUPO’s reported distance at that row), so a carboxylate could have a stronger effect in ET096.
- **Expected effect:** Potential **↑ steering / altered binding trajectory → ↑ mono-selectivity**.
- **Risk/tradeoff:** Acid near pocket can disrupt hydrophobic environment, alter peroxide activation networks indirectly, or increase uncoupling/peroxidation depending on protonation.
- **Confidence:** **Low-medium**

### 9) **Focused exploration suggestion: small “smart set” at A178 (electrostatic handle tuning)**
- **Proposal:** **A178{K,R,Q}** (3-way) rather than full saturation.
- **Rationale:** If Lys is too strong/too buried, Arg/Q can test whether **charge vs H-bonding** is the key driver for pose-locking.
- **Expected effect:** Map anchoring strength vs activity/peroxidation tradeoff.
- **Risk/tradeoff:** Library still small; may miss optimal residue.
- **Confidence:** **Medium**

---

## 3) Minimal Experimental Plan

### First-round variant panel (12 max; high-information)
Include singletons + a few combinations to test additivity between **(i) missing wall insertion**, **(ii) electrostatic handle**, **(iii) anisotropic sterics/cap**.

1. **WT ET096** (baseline)
2. **Gap+L insertion** at row index 104 (Leu)
3. **Gap+I insertion** at row index 104 (Ile)
4. **A178K**
5. **A171F**
6. **A173Y**
7. **A80L**
8. **V74L**
9. **Gap+L + A178K** (wall + electrostatic anchoring)
10. **Gap+L + A171F** (wall + anisotropic sterics)
11. **Gap+L + A173Y** (wall + cap)
12. **Gap+L + A178K + A171F** (triad: reduce microstates + anchor + guide)

(If insertion variants express poorly, swap in **A80L + A178K** and **A171F + A178K** as combination tests.)

### Assay/readout plan aligned to objective
- **Primary screen:** quantify **S82 mono-oxidized vs di-oxidized products** (LC/GC with authentic standards if available; otherwise relative peak areas with MS confirmation). Report **Mono:Di** and **total TTN** at fixed time and controlled H₂O₂ delivery.
- **Counter-screen for peroxidative drift:** **ABTS oxidation rate** (per literature context) to ensure variants don’t simply increase 1e⁻ chemistry that can worsen overoxidation cascades.
- **Process control:** run with **controlled peroxide feed** (e.g., syringe pump or stepwise additions) because UPO overoxidation/inactivation is peroxide-sensitive (literature context). Keep conditions identical across variants to attribute effects to mutations.

---

## 4) Rejected Alternatives (deprioritized)
1. **L174F as a first-line change** — although it increases bulk at a key inner-wall position (driver D), prompt_2 links OA167’s bulky wall to **di‑oxidation-prone behavior** without polar anchoring; ambiguous directionality for Mono:Di.
2. **A77D as a first-line change** — electrostatic effects are longer-range/condition-dependent; higher risk of perturbing pocket hydration/protonation with unclear selectivity outcome.
3. **Distal/background hydrophobic swaps (e.g., ET096 F223 / S227 region)** — prompt_2 flags these as likely secondary/background with weaker phenotype linkage; not ideal under a tight first-round budget.
4. **Broad site-saturation at multiple positions** — violates the “conservative, mechanistically justified” and “compact panel” requirements; start with the strongest mechanistic levers (gap wall, A178 handle, A171 anisotropy, A173 cap).

If you can specify what **S82** is chemically (size/polarity; whether di‑ox is sequential hydroxylations vs hydroxylation+further oxidation), I can slightly re-rank the “cap vs wall vs electrostatics” emphasis and propose a second-round combinatorial set focused on the best-performing axis.