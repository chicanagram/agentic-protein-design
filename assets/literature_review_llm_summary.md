## 1) Executive Summary (engineering-relevant; ≤10 bullets)

- **UPOs are secreted fungal heme‑thiolate enzymes (EC 1.11.2.1)** that perform **P450-like oxyfunctionalization** using **H₂O₂ as the sole cosubstrate** (no NAD(P)H/redox partners), but they also catalyze **peroxidative one‑electron oxidations** that can dominate with phenolics/radical-prone substrates.  
- **Chemoselectivity (peroxygenation vs peroxidation)** is a central process variable: radical scavengers (e.g., **ascorbate**) can **suppress peroxidative radical coupling/oligomerization** and bias toward **hydroxylated products** (shown for **AaeUPO + rutin**)—a lever directly relevant to aromatic substrates.  
- **Active-site access channel geometry is a primary determinant of regio/chemoselectivity**; channel “opening” mutations can strongly shift product distributions and increase conversions (e.g., **rCviUPO F88A/T158A** improved epoxidation selectivity/yield in lipids; analogous channel tuning is likely transferable to aromatic peroxygenation).  
- **Conserved catalytic architecture**: proximal **Cys thiolate** heme ligand; distal **acid–base (Glu) and Arg** in a conserved motif (UPO signature often reported as **–PCP–EGD–R–E** vs CPO **–PCP–EHD–E**), supporting efficient H₂O₂ activation.  
- **H₂O₂ tolerance and oxidative inactivation** remain key constraints for scale-up and reuse; membrane reactor reuse of UPO highlighted **activity loss/inactivation during processing** (AaeUPO study), consistent with peroxide-driven heme/protein damage and/or adsorption/denaturation.  
- **Assay choice matters**: ABTS/NBD are primarily **peroxidative reporter substrates** (electron transfer), not clean readouts of peroxygenation; for aromatics, use **GC/LC product analytics** (hydroxylation/epoxidation) plus a separate peroxidase assay to quantify competing flux.  
- **Sequence space is large and underexploited**: **UPObase** catalogs ~**1948** UPO/UPO-like sequences with subfamily classification and motifs—useful for **homolog mining** for stability/solvent tolerance/expression.  
- **Expression**: some UPOs are available recombinantly (notably **rCviUPO in E. coli** for engineering), but many UPOs are secreted glycoproteins where **host choice (fungal/yeast vs E. coli)** impacts folding, secretion, and stability.  
- **Opportunity**: engineer (i) **channel/gating residues** to fit aromatics (veratryl alcohol, naphthalene-like), (ii) **surface/stability** for solvent + peroxide tolerance, and (iii) **reaction engineering** (controlled H₂O₂ delivery + radical quenchers) to suppress peroxidation.

---

## 2) Structural Overview

### Fold classification
- **Heme-thiolate peroxidase (HTP) fold**, related to fungal **chloroperoxidase (CPO)** and distinct from classical plant peroxidases. UPOs are often described as **“extracellular P450-like”** due to shared **Cys-thiolate ligation** and Compound I chemistry, but they are **peroxidase-fold enzymes**.

### Domain architecture
- Typically **single-domain globular enzymes** (~30–45 kDa mature protein; many are secreted and may be glycosylated in native hosts).  
- Secretory signal peptides in native fungi; recombinant constructs may omit signal peptides or use heterologous secretion signals (host-dependent).

### Active site organization
- **Heme b** embedded in a pocket with:
  - **Proximal Cys** as axial ligand (thiolate “push” effect).
  - **Distal acid–base network** (often **Glu** as general acid/base) and **Arg** assisting peroxide binding/heterolysis.
- **Signature motif** reported for UPOs: **–PCP–EGD–R–E** (vs CPO: –PCP–EHD–E), used for annotation/classification (UPObase paper).

### Access channels / substrate tunnels
- A **heme access channel** connects solvent to the distal face; **channel width/shape and hydrophobicity** govern:
  - Substrate entry/pose (regioselectivity on aromatics and aliphatics).
  - Partitioning between **oxygen transfer** (peroxygenation) and **outer-sphere electron transfer** (peroxidation) for redox-active aromatics.
- Engineering evidence: **alanine scanning / channel residue substitutions** in **rCviUPO** improved oxygenation outcomes (epoxidation case), indicating channel residues are “high-leverage” knobs.

### Cofactor binding
- **Noncovalent heme b**; no additional cofactors required.  
- Heme incorporation and correct folding can be limiting in heterologous expression (especially in E. coli), often requiring optimized expression conditions.

---

## 3) Reaction Mechanism (focused on aromatic peroxygenation)

### Catalytic cycle steps (consensus for UPOs; experimentally supported by analogy to peroxidases/CPO and UPO mechanistic work)
1. **Resting state**: ferric heme (Fe(III)).  
2. **H₂O₂ binding** at distal site → formation of **Compound 0** (Fe(III)–OOH, hydroperoxo).  
3. **O–O heterolysis** (acid–base catalysis by distal residues) → **Compound I** (Fe(IV)=O + porphyrin/thiolate radical equivalent).  
4. **Peroxygenation (oxygen transfer)**: Compound I abstracts H•/e⁻ and inserts O (often via rebound) to yield hydroxylated/epoxidized aromatic products; enzyme proceeds through **Compound II** (Fe(IV)=O) back to Fe(III).  
5. **Peroxidation (competing)**: for easily oxidized aromatics/phenolics, Compound I/II can perform **one-electron oxidation** → substrate radicals → **coupling/oligomerization** (observed in rutin work).

### Key intermediates
- **Compound I** and **Compound II** are the central oxidants.  
- For some oxygenations (notably epoxidation), a **transient substrate-radical/Compound II* complex** has been proposed in UPO literature (explicitly discussed in the rCviUPO epoxidation paper’s mechanistic framing).

### Rate-limiting steps (what is known/likely)
- Often governed by a combination of:
  - **H₂O₂ activation efficiency** (distal network).
  - **Substrate access/positioning** (channel + binding pocket).
  - **Uncoupling/inactivation** at elevated peroxide (process-limited rather than intrinsic kinetics).
- Quantitative kinetic constants for the specific aromatic substrates listed (veratryl alcohol, naphthalene, NBD, ABTS) are not in the provided hits; expect strong substrate- and UPO-dependent variability.

### Competing pathways: peroxygenation vs peroxidation
- **Peroxygenation** desired for aromatic hydroxylation/epoxidation.  
- **Peroxidation** dominates with **redox mediators/dyes** (ABTS, many phenolics), generating radicals and side products.
- Process lever demonstrated: **ascorbic acid** shifted AaeUPO+rutin toward hydroxylated derivatives by quenching radicals / altering radical chain chemistry (PMID: 39181196).

### Determinants of chemo-/regioselectivity
- **Channel residues** (sterics) define substrate pose relative to Fe=O.  
- **Local polarity/electrostatics** can favor binding of polar aromatics (e.g., veratryl alcohol) vs hydrophobic PAHs (naphthalene).  
- **Substrate redox potential** influences likelihood of one-electron oxidation (peroxidation) vs oxygen transfer.

---

## 4) Substrate Scope & Selectivity Trends (with emphasis on aromatics)

### Classes accepted (general UPO capability; supported broadly, though not all quantified in provided hits)
- **Aromatics**: hydroxylation, epoxidation, O-/N-dealkylation; also **one-electron oxidations** leading to coupling.  
- **Aliphatics**: (sub)terminal hydroxylation, epoxidation of alkenes, fatty-acid oxygenation and even **chain-shortening** (PMID: 35453429).  
- **Heteroatom oxidations** and halogenation reported historically for AaeUPO lineage.

### Engineering-relevant trends for aromatics
- **Bulky/polycyclic aromatics** tend to be limited by **channel size**; “open-channel” variants can expand scope.  
- **Phenolic/antioxidant-like substrates** (e.g., rutin) are prone to **peroxidative radical chemistry**; controlling radical pathways is essential for clean peroxygenation.

### Known limitations
- **Peroxide-driven inactivation** and **radical side reactions** reduce TTN and complicate scale-up.  
- **Solubility** of hydrophobic aromatics (naphthalene) necessitates cosolvents—raising solvent tolerance requirements.

---

## 5) Engineering Landscape (what is directly supported by provided sources + actionable extrapolation)

### Mutations affecting activity/selectivity (primary evidence)
- **rCviUPO channel engineering** (alanine substitutions; up to six residues) improved oxygenation of unsaturated fatty acids; **F88A/T158A** notably enhanced epoxidation selectivity and process performance (Antioxidants 2022, DOI: 10.3390/antiox11050915).  
  - Engineering principle: **reduce steric constraints / reshape channel** to favor productive binding poses and reduce off-pathway reactions.

### Stability-enhancing mutations
- Not detailed in the provided hits. In UPO practice, stability engineering often targets:
  - **Surface charge networks**, **disulfides**, **glycosylation sites** (host-dependent), and **helix capping**; but specific validated mutations require additional primary sources beyond the current hit list.

### Expression improvements
- **rCviUPO produced in E. coli** (enables rapid mutagenesis/screening) (DOI: 10.3390/antiox11050915).  
- Many UPOs are naturally secreted; expression in yeast/fungi can improve folding/glycosylation but slows iteration.

### Channel reshaping strategies (validated concept)
- **Alanine scanning** of channel residues to map steric hotspots (rCviUPO study).  
- For aromatics: analogous approach—identify residues lining the heme channel and mutate to **Ala/Gly/Val/Leu/Phe** to tune size and π-stacking.

### ML-guided/computational design
- Not present in provided hits. Practical near-term route: use **UPObase** to build a **sequence–function dataset** (subfamily + motifs + predicted stability features) for ML triage, then test a focused panel experimentally.

### Reported performance gains (quantitative from provided hit)
- rCviUPO **F88A/T158A**: >80% desired diepoxides after ~99% conversion (lipid case) and up to **85% epoxidation yield** at higher substrate load after process optimization (DOI: 10.3390/antiox11050915). (Not aromatic, but demonstrates magnitude achievable via channel edits + process control.)

---

## 6) Practical Constraints (stability, H₂O₂, solvents, expression)

### H₂O₂ sensitivity / inactivation
- UPOs require H₂O₂ but are also **damaged by it** (heme bleaching, oxidative modification, formation of inactive states).  
- Process evidence: enzyme reuse in a membrane reactor faced **stability/inactivation challenges** during filtration stages (PMID: 39181196).

**Engineering/process mitigations (actionable):**
- **Controlled H₂O₂ feeding** (syringe pump; in situ generation via oxidase) to keep low steady-state peroxide.  
- Additives: **radical scavengers** (ascorbate demonstrated), catalase “polishing” after dosing pulses, or sacrificial reductants depending on product sensitivity.

### Solvent tolerance
- Not quantified in provided hits; for hydrophobic aromatics expect need for **water-miscible cosolvents** (MeCN, EtOH, DMSO) or biphasic systems. Screen for activity retention and heme integrity.

### Expression hosts used
- **E. coli** for **rCviUPO** (enables engineering).  
- Many canonical UPOs (e.g., AaeUPO) are secreted fungal enzymes; recombinant production often uses yeast/fungal systems in broader literature (not in provided hits).

### Formulation/immobilization
- Membrane reactor reuse suggests immobilization/recovery is feasible but **mechanical/processing stress + peroxide** can accelerate deactivation (PMID: 39181196). Consider gentle immobilization chemistries and peroxide control.

---

## 7) Comparative Analysis (seed sequence: CviUPO; limited by provided data)

- **CviUPO (Collariella virescens UPO)** is explicitly demonstrated as **engineerable in E. coli** and responsive to **heme-channel mutations** (F88A/T158A).  
- **AaeUPO (Agrocybe/Cyclocybe aegerita UPO)** is highlighted for aromatic/phenolic transformations where **peroxidation vs peroxygenation** competition is prominent (rutin case).  
- Trade-off hypothesis: **more open channels** may increase turnover on bulky/hydrophobic substrates but can also increase **uncoupling** or **peroxidative side reactions** by allowing alternative binding modes—needs empirical mapping for aromatics.

---

## 8) Engineering Opportunities (specific, testable hypotheses for aromatic peroxygenation)

### A. Channel/gating residue targets (CviUPO-centric)
- Start from the validated **heme-channel hotspot positions F88 and T158** (CviUPO numbering per the Antioxidants 2022 paper).  
  - For aromatics: test **F88A/F88V/F88L/F88Y** (sterics + π interactions) and **T158A/T158V/T158S** (size/polarity).  
  - Combine with second-shell mutations to restore binding specificity if activity becomes too “leaky”.

### B. Biasing peroxygenation over peroxidation (process + protein)
- **Assay with and without radical scavengers** (ascorbate; possibly Trolox) to quantify peroxidation contribution for each substrate (veratryl alcohol vs naphthalene vs ABTS/NBD).  
- Protein-side: introduce **more hydrophobic/shape-complementary binding** near the oxoferryl to favor close-contact oxygen transfer over outer-sphere ET (requires structure/model; see below).

### C. Electrostatic tuning
- For polar aromatics (veratryl alcohol), add **H-bond donors/acceptors** in the channel to preorganize the benzylic C–H near Fe=O.  
- For PAHs (naphthalene), reduce polar “traps” and increase **hydrophobic packing** to improve occupancy.

### D. Stability / H₂O₂ tolerance strategy
- Screen for variants with improved **residual activity after peroxide challenge** (e.g., incubate with 1–10 mM H₂O₂ for defined times; measure remaining peroxygenation activity).  
- Couple with **low-peroxide feed** in preparative reactions; many “stability” gains are realized by process control rather than mutations alone.

### E. Assay design suggestions (to avoid misleading readouts)
- Use **two orthogonal assays**:
  1) **Peroxygenation analytics**: LC/GC quantification of hydroxylated/epoxidized products for veratryl alcohol and naphthalene.  
  2) **Peroxidation reporter**: ABTS oxidation rate to quantify one-electron activity (useful as a “side reaction” metric, not as the main objective).
- Include **H₂O₂ consumption** and **enzyme inactivation kinetics** (activity vs time) to estimate TTN under realistic dosing.

### F. Homolog mining (UPObase-driven)
- Use **UPObase** to select homologs in different subfamilies with:
  - Predicted **higher thermostability** (more salt bridges, shorter loops),
  - Different **channel motifs** (bulky vs open),
  - Better **expression compatibility** (fewer disulfides/glycosylation dependence for E. coli).
- Build a small panel (10–30 enzymes) for rapid functional screening on your aromatic substrates.

---

## 9) References (provided hits; review vs primary)

1. **(Primary research)** Linde, D.; González-Benjumea, A.; Aranda, C.; Carro, J.; Gutiérrez, A.; Martínez, A. T. (2022). *Engineering Collariella virescens Peroxygenase for Epoxides Production from Vegetable Oil.* **Antioxidants** 11(5):915. DOI: **10.3390/antiox11050915**. PMCID: **PMC9137900**.  
2. **(Primary research / process + selectivity control)** (2024). *Exploiting UPO versatility to transform rutin in more soluble and bioactive products.* **New Biotechnology**. PubMed: **PMID 39181196**.  
3. **(Primary research)** Olmedo, A.; Ullrich, R.; Hofrichter, M.; del Río, J. C.; Martínez, Á. T.; Gutiérrez, A. (2022). *Novel Fatty Acid Chain-Shortening by Fungal Peroxygenases Yielding 2C-Shorter Dicarboxylic Acids.* **Antioxidants** 11(4):744. DOI: **10.3390/antiox11040744**. PMCID: **PMC9025384**.  
4. **(Database/resource)** Muniba, F.; Dongming, L.; Huang, S.; Wang, Y. (2019). *UPObase: an online database of unspecific peroxygenases.* **Database (Oxford)**. DOI: **10.1093/database/baz122**. PMCID: **PMC6902001**.

---

### What I would request next (to sharpen this for CviUPO + aromatics)
If you can provide **CviUPO sequence/construct** (or UniProt/GenBank ID) and any **existing activity data** on veratryl alcohol/naphthalene, I can (i) map **channel residues around F88/T158** onto an AlphaFold/PDB model, (ii) propose a **focused mutational library** (≤50 variants) with predicted effects on aromatic binding poses, and (iii) recommend **H₂O₂ feed regimes** and analytics tailored to your substrates (including how to treat ABTS/NBD as side-activity controls).