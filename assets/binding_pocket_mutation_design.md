## 1) Design Intent
- **Backbone protein:** RML lipase
- **Objective:** **Increase esterification of oleic acid with sucrose in a water-containing environment** by shifting RML’s pocket from “polar-permissive/many microposes” toward **more pose-locking steric steering + discrete anchoring**, while retaining enough polar handling to keep sucrose engaged under aqueous conditions.

---

## 2) Proposed Mutations (ranked)

### 1) **S83R**
- **Rationale (mechanistic driver):** prompt_2 identifies **RML 83 Ser ↔ TLL 84 Arg** as a top proximal driver. Introducing **Arg** adds a **bulky cationic anchor + steric post** near sucrose (3.5–3.6 Å), expected to **reduce non-productive sucrose poses** and bias a productive OH presentation.
- **Targets hypothesis:** “TLL-like discrete charge points + steric steering improves regioselective/pose-locked binding.”
- **Expected effect:** ↑ productive sucrose orientation → ↑ esterification rate/extent (especially if RML currently binds sucrose too degenerately).
- **Risk/tradeoff:** In water-containing media, Arg is fine, but in lower-water microenvironments it can be costly to desolvate; may also **over-constrain** binding and reduce turnover if geometry mismatches.
- **Confidence:** **High**

### 2) **D91N**
- **Rationale:** **RML 91 Asp ↔ TLL 92 Asn** is very close contact in RML (~2.37 Å). Removing the **formal negative charge** should reduce “sticky” nonspecific electrostatic trapping of multiple sucrose OH microstates while keeping H-bonding via Asn.
- **Targets hypothesis:** “Reducing near-field charge decreases nonproductive binding and improves catalytic pose selection.”
- **Expected effect:** ↑ catalytic efficiency (less nonproductive binding), potentially ↑ esterification in water by avoiding overly strong/incorrect OH capture.
- **Risk/tradeoff:** Asp might currently help recruit/retain sucrose; neutralizing could reduce apparent binding at low sucrose.
- **Confidence:** **High**

### 3) **S83R + D91N (double)**
- **Rationale:** Combines the two strongest proximal drivers: **add a discrete positive anchor (Arg)** while **removing a potentially promiscuous negative trap (Asp→Asn)**. Mechanistically, this should convert RML’s near-field from “many H-bond solutions” to “fewer, more directed solutions.”
- **Targets hypothesis:** “Near-field electrostatic re-patterning is sufficient to shift RML toward TLL-like pose-locking.”
- **Expected effect:** ↑ esterification and potentially ↑ monoacylation bias (if pose-locking improves).
- **Risk/tradeoff:** Could overspecify sucrose pose and reduce turnover if the productive pose is not the one stabilized.
- **Confidence:** **Medium-High**

### 4) **T265I**
- **Rationale:** **RML 265 Thr ↔ TLL 265 Ile** is near-field (~2.9 Å in RML). Thr provides an H-bond site; Ile creates a **hydrophobic wall** that can **steer sucrose away from that face** and improve acyl-chain packing/organization for oleate.
- **Targets hypothesis:** “Hydrophobizing a near-field wall improves steric steering and acyl-chain accommodation.”
- **Expected effect:** ↑ esterification (better oleate positioning; fewer sucrose microposes).
- **Risk/tradeoff:** Might reduce sucrose residence time in water (loss of a polar contact) and/or reduce activity if Thr participates in a beneficial H-bond network.
- **Confidence:** **Medium**

### 5) **N264L**
- **Rationale:** **RML 264 Asn ↔ TLL 264 Leu** is a distal/vestibule-shaping driver. Leu increases **hydrophobic surface continuity** in the vestibule, pushing behavior toward “park by shape + limited anchors” rather than many distal H-bonds.
- **Targets hypothesis:** “Vestibule hydrophobization reduces solvent-wet, nonproductive parking and improves channeled approach.”
- **Expected effect:** Potential ↑ effective delivery of sucrose into productive near-field pose; may also help oleate access/packing.
- **Risk/tradeoff:** In water-containing media, too much hydrophobization can reduce sucrose capture/partitioning into the pocket.
- **Confidence:** **Medium**

### 6) **S259W**
- **Rationale:** **RML 259 Ser ↔ TLL 260 Trp** is a major distal vestibule sculptor. Trp can act as a **steric gate/wall** and provide **π/CH contacts** for sugar rings, potentially creating a more defined “parking surface” and channeled entry.
- **Targets hypothesis:** “Aromatic gating in the vestibule improves productive approach trajectories.”
- **Expected effect:** ↑ pose filtering; possibly ↑ monoacylation selectivity and ↑ esterification efficiency if sucrose is currently too mobile.
- **Risk/tradeoff:** High steric risk—Trp could **over-occlude** the vestibule and reduce substrate access, especially for bulky sucrose in water.
- **Confidence:** **Medium-Low** (high impact but higher failure risk)

### 7) **H207R**
- **Rationale:** **RML 207 His ↔ TLL 205 Arg** adds a **distal discrete positive charge point** (vestibule shell). In water-containing media, this may help **capture/hold sucrose** without making the whole pocket highly polar.
- **Targets hypothesis:** “Discrete distal anchoring improves sucrose recruitment/retention under aqueous conditions.”
- **Expected effect:** ↑ apparent binding/occupancy of sucrose → could increase esterification rate if binding is limiting.
- **Risk/tradeoff:** Could increase nonproductive binding if it anchors sucrose in a nonproductive vestibule pose; may alter pH dependence.
- **Confidence:** **Medium**

### 8) **Focused exploration at 83 (small set): S83R / S83K / S83H**
- **Rationale:** Position 83 is a top proximal driver. If Arg is too strong/too bulky, Lys or His may provide a **tunable cationic anchor** with different geometry and desolvation cost.
- **Targets hypothesis:** “A cationic post at 83 is beneficial, but optimal strength/geometry matters in water.”
- **Expected effect:** Identify best balance of pose-locking vs turnover.
- **Risk/tradeoff:** Requires a mini-panel; His may be partially protonated depending on pH.
- **Confidence:** **Medium**

---

## 3) Minimal Experimental Plan (first round: 10 variants)
High-information panel emphasizing the strongest mechanistic drivers plus one “vestibule gate” test:

1. WT RML  
2. **S83R**  
3. **D91N**  
4. **S83R/D91N**  
5. **T265I**  
6. **S83R/T265I** (tests synergy: anchor + hydrophobic steering)  
7. **N264L**  
8. **S259W** (single high-impact vestibule gate test)  
9. **H207R**  
10. **D91N/T265I** (tests whether charge removal + hydrophobic wall is sufficient without Arg)

### Assay/readout plan (aligned to esterification in water-containing media)
- **Primary reaction:** sucrose + oleic acid → sucrose oleate(s)
- **Quantification:** HPLC (or LC-MS) to measure:
  - **Total ester formation** (conversion/yield)
  - **Product distribution** (mono-/di-/poly-oleate; if resolvable)
- **Key conditions to include (small matrix):**
  - Fixed enzyme loading; time course (e.g., 0–24 h) to extract initial rates + endpoints
  - At least two water activities (e.g., “low water” vs “higher water” within your transport-relevant range) to see which variants retain activity when water competes.
- **Secondary checks (quick triage):**
  - Residual hydrolytic activity on a simple ester (to ensure enzyme is active/folded)
  - Expression/solubility screen (SDS-PAGE activity band or crude lysate activity)

---

## 4) Rejected Alternatives (lower priority)
1. **A90G** (RML 90 Ala ↔ TLL 91 Gly)  
   - Deprioritized: likely subtle loop flexibility effect; hard to predict benefit without dynamics data.

2. **T93N** (RML 93 Thr ↔ TLL 94 Asn)  
   - Deprioritized: polar↔polar swap; expected to be modulatory and lower impact than 83/91/259/264/265.

3. **F215Y** (RML 215 Phe ↔ TLL 213 Tyr)  
   - Deprioritized: minor distal polarity tweak; unlikely to move esterification strongly.

4. **V254I** (RML 254 Val ↔ TLL 255 Ile)  
   - Deprioritized: conservative hydrophobic packing change; secondary at best.

5. **Large distal rewiring (e.g., Q174Y and/or Q176A)**  
   - Deprioritized for round 1: could help vestibule structuring, but higher uncertainty and more likely to perturb folding/local packing without clear first-order linkage to the sucrose reactive pose.

If you can share whether your main limitation is **(i) sucrose binding/occupancy in water** vs **(ii) productive pose selection/regioselectivity**, I can reorder the panel (e.g., prioritize H207R vs S259W/N264L) and tighten the expected product-profile predictions.