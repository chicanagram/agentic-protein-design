## 1. Executive Summary (engineering-relevant takeaways; ≤10 bullets)

- **UPOs are secreted heme-thiolate enzymes (EC 1.11.2.1)** that generate a **P450-like Compound I** directly from **H₂O₂** (no NAD(P)H/redox partners), enabling high-value **aromatic hydroxylations** and related oxyfunctionalizations under mild conditions.  
- **Chemoselectivity is a central bottleneck for aromatics**: desired *peroxygenation* (2e⁻ oxygen transfer) competes with *peroxidation* (1e⁻ oxidation → phenoxy radicals/quinones → oligomerization/polymerization). This is explicitly observed in aromatic antioxidant chemistry (e.g., rutin) and in naphthalene overoxidation scenarios.  
- **Active-site access channel geometry is a dominant selectivity lever** across UPOs: multiple studies show that **tunnel/channel reshaping** can strongly shift product distributions (epoxidation vs hydroxylation; benzylic vs aromatic; overoxidation propensity).  
- **H₂O₂ management is non-negotiable**: UPOs are prone to oxidative inactivation and uncoupling; reaction engineering (controlled dosing, in situ generation, scavengers) often matters as much as protein engineering.  
- **Expression is historically limiting**, but the field now has multiple workable platforms: (i) **S. cerevisiae directed evolution** for secretion (AaeUPO), (ii) **E. coli soluble expression** for some short UPOs (e.g., CviUPO) and now **sfGFP-mediated secretion in E. coli** enabling faster engineering cycles, and (iii) **Pichia pastoris** with **signal peptide shuffling + stability design (PROSS on AF2 models)** enabling broad access to diverse UPOs.  
- For your **seed enzyme rCviUPO**, **channel alanine scanning** and **F88A/T158A** are validated “go-to” mutations for altering access/positioning (shown for fatty-acid epoxidation; conceptually transferable to aromatic access/pose control).  
- **Assay choice can bias evolution outcomes**: ABTS reports peroxidase-like 1e⁻ activity; NBD and other oxygen-transfer probes report peroxygenation. Dual assays are useful to tune the **peroxygenation:peroxidation (P:p) ratio**.  
- **Radical scavengers can redirect aromatic outcomes** (ascorbate in rutin work), suggesting a practical knob to suppress peroxidative radical cascades while maintaining oxygen transfer.  
- **Key opportunity for aromatics**: engineer (a) **tunnel polarity/shape** to favor productive aromatic binding near the oxo, and (b) **surface ET/radical pathways** (putative LRET sites) to reduce phenoxy-radical formation and overoxidation.

---

## 2. Structural Overview

### Fold classification
- **Heme-thiolate peroxidase (HTP) superfamily**, related to **chloroperoxidase (CPO)** and mechanistically analogous to **P450 peroxide shunt** chemistry.
- Two broad size classes frequently discussed: **“long” (~45 kDa)** and **“short” (~29 kDa)** UPOs (phylogeny/architecture correlate with substrate profiles and expression behavior).

### Domain architecture
- Typically **single-domain globular heme enzyme**, secreted; long UPOs often glycosylated in native fungal hosts.
- **Signal peptide** is essential for secretion in yeast/fungi; signal peptide identity is a major determinant of functional expression.

### Active site organization
- **Buried heme** with **axial cysteine thiolate ligand** (defining feature vs classical peroxidases).
- **Distal acid–base residues** (classically a **Glu/His** pair in HTPs) support H₂O₂ activation and O–O cleavage; exact identities vary by subfamily but the functional motif is conserved.

### Access channels / substrate tunnels
- A **hydrophobic heme access channel** governs:
  - substrate entry/egress,
  - pose relative to the oxoferryl oxygen,
  - and thus **regio-/chemoselectivity**.
- Engineering repeatedly targets **channel-lining residues** (often bulky aromatics like Phe/Ile/Leu) to tune space and positioning.

### Cofactor binding
- **Protoporphyrin IX heme b** (noncovalent) is the only cofactor required.
- No reductase domain; no flavins; no NAD(P)H.

### Known motifs / signatures (sequence-level)
- UPObase reports motif-based classification and distinguishes UPO-like vs CPO-like signatures; UPOs and CPOs differ in conserved motif patterns (reviewed in UPObase paper).  
  - Practical use: **motif screening** helps avoid misannotated peroxidases when mining homologs.

---

## 3. Reaction Mechanism (focused on aromatic peroxygenation)

### Catalytic cycle (productive peroxygenation)
1. **Resting state Fe(III)-heme** binds/activates **H₂O₂** on the distal side.
2. Formation of **Compound 0 (Fe(III)-OOH)** (hydroperoxo intermediate).
3. **Heterolytic O–O cleavage** → **Compound I**: **Fe(IV)=O + porphyrin π-cation radical** (the key oxidant).
4. **Oxygen transfer to substrate**:
   - For **aromatics**, initial step is often described as **arene epoxidation / radical-type addition** followed by **NIH shift / rearrangement** to yield **phenols** (formal hydroxylation).
5. Return to Fe(III) resting state after product release.

### Competing pathways: peroxidation vs peroxygenation
- **Peroxidative (1e⁻) oxidation**: Compound I/II can oxidize phenols/anilines/etc. to **radicals** → **quinones/oligomers**.
- For aromatic hydroxylation, this is especially problematic because **phenolic products are better peroxidase substrates than the parent aromatic**, driving **overoxidation and polymerization** (explicitly highlighted in the AaeUPO engineering literature and recent reviews).

### Rate-limiting / inactivation considerations (what matters experimentally)
- Often not a single intrinsic chemical step but **effective rate** is dominated by:
  - **H₂O₂ delivery regime** (local high [H₂O₂] accelerates inactivation),
  - **substrate access/pose** (tunnel gating),
  - and **uncoupling** (H₂O₂ consumption without productive oxygen transfer).

### Determinants of chemo-/regioselectivity for aromatics
- **Distance/orientation** of the target C–H (or π-system) to the **Fe(IV)=O**.
- **Channel sterics** (bulky residues enforce a binding pose).
- **Electrostatics/polarity** in the channel (important for polar aromatics like veratryl alcohol, ABTS-like probes, flavonoids).
- **Peroxidation susceptibility** of products (phenols) and presence/absence of **radical sinks** (ascorbate, other scavengers).

---

## 4. Substrate Scope & Selectivity Trends (with your substrates in mind)

### Broad accepted classes (validated across UPO literature)
- Aromatics: hydroxylation, epoxidation-derived hydroxylation, oxidative dearomatization/overoxidation in some cases.
- Benzylic C–H hydroxylation (often high enantioselectivity possible after engineering).
- Alkenes (epoxidation), fatty acids (ω-1/ω-2 hydroxylation, epoxidation), heteroatom oxidations (S/N).

### Aromatic peroxygenation trends (actionable heuristics)
- **Electron-rich aromatics** (anisoles, phenoxy motifs, lignin-like units) tend to react readily but also **overoxidize** due to phenolic products.
- **Bulky polyaromatics** (e.g., naphthalene) can show **product branching**: naphthol vs naphthoquinone (secondary peroxidative oxidation) depending on enzyme and conditions (reported for MthUPO vs AaeUPO variants in engineering literature).
- **Highly redox-active dyes/mediators (ABTS)** primarily report **peroxidase-like activity**, not necessarily productive peroxygenation.

### Your listed substrates (engineering implications)
- **Veratryl alcohol**: lignin-model aromatic alcohol; expect benzylic oxidation/hydroxylation pathways and potential overoxidation depending on enzyme and H₂O₂ regime.
- **Naphthalene**: prone to **naphthol → naphthoquinone** sequences; controlling peroxidation is key if you want to stop at naphthol.
- **NBD (oxygen-transfer probe)**: useful to track peroxygenation activity in HTS (used in UPO discovery/engineering workflows).
- **ABTS**: strong for secretion/activity screening but biases toward **1e⁻ peroxidase**; best used alongside an oxygen-transfer assay to avoid evolving “better peroxidases”.
- **(Not in your list but relevant) aromatic antioxidants/flavonoids**: rutin study shows strong sensitivity to radical pathways and scavengers.

---

## 5. Engineering Landscape

### (A) Mutations affecting activity/selectivity (channel/tunnel engineering)
- **rCviUPO access-channel alanine substitutions** improved oxygenation selectivity in lipid epoxidation; **F88A/T158A** is a validated double mutant that strongly shifts product distribution (diepoxide enrichment in polyunsaturated substrates).  
  - Engineering lesson: **positions analogous to F88 and T158** are prime targets for **aromatic pose control** (widening/narrowing; changing π-stacking contacts).
- **MthUPO engineering in S. cerevisiae** achieved **up to 16.5-fold kcat/KM improvement** on an aromatic model substrate (5-nitro-1,3-benzodioxole) and enabled **chemo-/regioselective aromatic vs benzylic oxidation**; variants reached **up to 95% ee** for benzylic hydroxylation.  
  - Lesson: even without many structures, **active-site reshaping** can deliver large selectivity gains for aromatic chemistry.

### (B) Tuning peroxygenation vs peroxidation (P:p ratio)
- **Structure-guided evolution on AaeUPO** targeted flexible loops and identified hotspots (notably **positions 120 and 320** in that numbering) that strongly affect **P:p ratio**, albeit sometimes with stability tradeoffs; combinatorial saturation was used to recover stability while tuning P:p.  
  - Lesson: **separate “oxygen transfer” and “radical oxidation” phenotypes** can be evolved, but stability must be co-selected.

### (C) Expression improvements (major enabler)
- **Directed evolution in S. cerevisiae (AaeUPO)**: 5 generations, ~9000 clones screened; **3250-fold total activity improvement** with **27-fold secretion gain** attributable to signal peptide mutations and **~18-fold kcat/KM improvement** for oxygen transfer. Reported functional expression up to **~8 mg/L** in yeast for evolved variants.  
- **E. coli expression/engineering acceleration**: **sfGFP-mediated secretion system** enables UPO engineering in E. coli; demonstrated on a newly identified UPO (CmaUPO) and shown applicable to other UPOs (AaeUPO, CciUPO, PabUPO-I). Tunnel-site ISM delivered **enantioselectivity reversal/enhancement** for ethylbenzene hydroxylation (WT 21% ee R → variants up to **99% ee R** or **84% ee S**).  
  - Lesson: for rapid iteration under your constraints, **E. coli-based platforms are becoming realistic** for UPOs (especially short-type).
- **Pichia pastoris + AF2/PROSS + signal peptide shuffling (2024)**: PROSS designs on **AlphaFold2 models** plus signal peptide shuffling enabled functional production of **9/10 diverse UPOs**, including previously recalcitrant enzymes (e.g., CciUPO) and even **oomycete UPOs**.  
  - Lesson: if your target UPO is hard to express, **stability design + secretion engineering** is now a practical first step.

### (D) ML-guided / computational design
- Explicitly validated in the provided set: **AlphaFold2 → PROSS** stability design workflow (structure-based computational design) enabling expression and stability improvements at scale (screening only a few constructs per enzyme target).

---

## 6. Practical Constraints (stability, solvent tolerance, H₂O₂ tolerance, formulation)

### H₂O₂ sensitivity / inactivation
- Recurrent limitation across UPO applications and reviews: **oxidative inactivation by H₂O₂** and **uncoupling**.
- Practical mitigation:
  - **controlled feeding** (syringe pump),
  - **in situ H₂O₂ generation** (enzymatic/electro/photo; noted as a major process-engineering theme in recent reviews),
  - **lower steady-state [H₂O₂]** with higher total delivered oxidant.

### Peroxidation-driven byproducts (especially for aromatics)
- Aromatic hydroxylation products (phenols) can undergo **peroxidase-type 1e⁻ oxidation** → radicals → oligomerization.
- **Radical scavengers** can shift outcomes: in rutin transformations, **ascorbic acid** redirected product formation toward hydroxylated derivatives (interpretable as suppressing radical chain chemistry).

### Solvent tolerance
- Evolved AaeUPO variants reported **high stability in organic cosolvents** (important for aromatic substrates with low aqueous solubility). Exact solvent windows depend on enzyme/variant; typically co-solvents (acetone, etc.) are used in UPO work.

### Expression hosts used (relevant to your constraints)
- **S. cerevisiae**: strong for HTS-directed evolution of secretion and activity.
- **P. pastoris**: scalable secretion; compatible with signal peptide/promoter shuffling; now paired with AF2/PROSS.
- **E. coli**: historically difficult but feasible for some short UPOs (e.g., rCviUPO) and now improved by sfGFP-mediated secretion.

---

## 7. Comparative Analysis (seed sequence: CviUPO context)

### CviUPO (Collariella virescens UPO; typically short-type recombinant)
- Experimentally used as an **E. coli-produced recombinant enzyme** suitable for mutagenesis and analytical optimization.
- Demonstrated sensitivity of selectivity to **heme access channel residues**; **F88A/T158A** is a validated channel-widening combination that changes oxygenation outcomes (shown for fatty-acid epoxidation; mechanistically consistent with altered substrate pose/access).
- Compared to long-type AaeUPO (classic model), CviUPO is often treated as a **more engineerable E. coli-compatible scaffold**, which is advantageous under constraints emphasizing rapid engineering cycles.

Trade-off expectation:
- **Short-type/E. coli-friendly** scaffolds: faster iteration, potentially less glycosylation dependence; may differ in substrate scope for bulky aromatics.
- **Long-type/secreted fungal** scaffolds (AaeUPO): deep mechanistic/structural literature and robust aromatic chemistry, but expression/engineering cycles can be slower unless using established yeast platforms.

---

## 8. Engineering Opportunities (actionable hypotheses + assay suggestions)

### A. Channel/tunnel engineering for aromatic peroxygenation (primary lever)
**Goal:** increase productive aromatic binding near the oxo while reducing residence time/pose that favors 1e⁻ oxidation of phenolic products.

- Start with **CviUPO channel positions analogous to F88 and T158** (already validated for access reshaping). For aromatics, consider:
  - **F→A/L/V** to tune π-stacking vs space,
  - **T→A/S/V** to tune polarity and sterics.
- Extend to a **small “smart library”** of 6–12 channel residues (CAST/ISM style) rather than full random mutagenesis:
  - prioritize residues lining the narrowest constrictions (“gates”) and those facing the heme distal oxo.

### B. Shift peroxygenation:peroxidation ratio (P:p) for aromatic products
**Goal:** suppress radical pathways that convert phenols to quinones/oligomers.

- Use **dual screening**:
  - **ABTS** (peroxidase proxy) + **NBD** (peroxygenation proxy) to explicitly evolve higher **P:p**.
- Consider importing the **AaeUPO concept** of loop/hotspot tuning (positions 120/320 in AaeUPO numbering) by mapping to CviUPO via alignment and targeting the **structurally corresponding regions** (often flexible loops near access channel / surface ET sites).

### C. Reaction engineering as a parallel “mutation”
For aromatic peroxygenation, you can often gain more by controlling chemistry than by single mutations:

- **H₂O₂ dosing**: implement **fed-batch** (e.g., 0.1–1.0 mM/h equivalent) rather than bolus.
- **Radical suppression**: test **ascorbate** (as in rutin work) or alternative radical sinks (careful: can also reduce reactive intermediates or interfere with assays).
- **pH as a selectivity knob**: UPOs can switch between oxygenation and halogenation modes with pH in some systems; more generally, pH shifts can change peroxidation propensity and substrate ionization.

### D. Expression/stability strategy under your constraints
- If you need **fast cycles**: consider **E. coli sfGFP-mediated secretion** as an engineering chassis (demonstrated generality across multiple UPOs).
- If expression is limiting: use **AlphaFold2 model → PROSS stability designs** + **signal peptide shuffling** in **Pichia** to unlock production before doing selectivity engineering.

### E. Assay design suggestions (for your substrate set)
- **Primary HTS**: NBD oxygen-transfer activity (peroxygenation) + ABTS (peroxidation) to compute a **P:p score**.
- **Secondary analytics**:
  - **Veratryl alcohol**: GC/HPLC for benzylic oxidation products; monitor overoxidation.
  - **Naphthalene**: quantify **1-naphthol vs 1,4-naphthoquinone** ratio as a direct readout of peroxygenation vs sequential peroxidation.
- Include **H₂O₂ consumption** and **residual activity** measurements to capture **H₂O₂ tolerance** phenotype.

---

## 9. References (primary vs review; with identifiers)

**Primary research**
1. Molina-Espeja, P.; Garcia-Ruiz, E.; Gonzalez-Perez, D.; Ullrich, R.; Hofrichter, M.; Alcalde, M. (2014). *Directed Evolution of Unspecific Peroxygenase from Agrocybe aegerita.* **Applied and Environmental Microbiology** 80(11), 3496–3507. DOI: **10.1128/AEM.00490-14**.  
2. Mate, D. M.; Palomino, M. A.; Molina-Espeja, P.; Martin-Diaz, J.; Alcalde, M. (2017). *Modification of the peroxygenative:peroxidative activity ratio in the unspecific peroxygenase from Agrocybe aegerita by structure-guided evolution.* **Protein Engineering, Design & Selection** 30(3), 191–198. DOI: **10.1093/protein/gzw073**.  
3. Linde, D.; González-Benjumea, A.; Aranda, C.; Carro, J.; Gutiérrez, A.; Martínez, A. T. (2022). *Engineering Collariella virescens Peroxygenase for Epoxides Production from Vegetable Oil.* **Antioxidants** 11, 915. DOI: **10.3390/antiox11050915**. (Primary; open access)  
4. Knorrscheidt, A.; Soler, J.; Hünecke, N.; Püllmann, P.; Garcia-Borràs, M.; Weissenborn, M. J. (2021). *Accessing Chemo- and Regioselective Benzylic and Aromatic Oxidations by Protein Engineering of an Unspecific Peroxygenase.* **ACS Catalysis** 11, 7327–7338. DOI: **10.1021/acscatal.1c00847**.  
5. Münch, J.; Soler, J.; Hünecke, N.; Homann, D.; Garcia-Borràs, M.; Weissenborn, M. J. (2023). *Computational-Aided Engineering of a Selective Unspecific Peroxygenase toward Enantiodivergent β-Ionone Hydroxylation.* **ACS Catalysis** 13, 8963–8972. DOI: **10.1021/acscatal.3c00702**.  
6. Münch, J.; Dietz, N.; Barber-Zucker, S.; et al. (2024). *Functionally Diverse Peroxygenases by AlphaFold2, Design, and Signal Peptide Shuffling.* **ACS Catalysis** 14, 4738–4748. DOI: **10.1021/acscatal.4c00883**.  
7. Yan, X.; Zhang, X.; Li, H.; et al. (2024). *Engineering of Unspecific Peroxygenases Using a Superfolder-Green-Fluorescent-Protein-Mediated Secretion System in Escherichia coli.* **JACS Au** 4, 1654–1663. DOI: **10.1021/jacsau.4c00129**.  
8. Barber, V.; Mielke, T.; Cartwright, J.; Díaz-Rodríguez, A.; Unsworth, W. P.; Grogan, G. (2024). *Unspecific Peroxygenase (UPO) can be Tuned for Oxygenation or Halogenation Activity by Controlling the Reaction pH.* **Chemistry – A European Journal** e202401706. DOI: **10.1002/chem.202401706**.  
9. (Process/aromatics) [AaeUPO + rutin] (2024). *Exploiting UPO versatility to transform rutin in more soluble and bioactive products.* **New Biotechnology**. PubMed: **39181196**.  
10. Olmedo, A.; Ullrich, R.; Hofrichter, M.; et al. (2022). *Novel Fatty Acid Chain-Shortening by Fungal Peroxygenases Yielding 2C-Shorter Dicarboxylic Acids.* **Antioxidants** 11(4), 744. DOI: **10.3390/antiox11040744**. PubMed: **35453429**.

**Databases / resources**
11. Muniba, F.; Dongming, L.; Huang, S.; Wang, Y. (2019). *UPObase: an online database of unspecific peroxygenases.* **Database (Oxford)**. DOI: **10.1093/database/baz122**. PubMed: **31820805**.

**Review**
12. Monterrey, D. T.; Menés-Rubio, A.; Keser, M.; Gonzalez-Perez, D.; Alcalde, M. (2023). *Unspecific peroxygenases: The pot of gold at the end of the oxyfunctionalization rainbow?* **Current Opinion in Green and Sustainable Chemistry** 41, 100786. DOI: **10.1016/j.cogsc.2023.100786**.

---

If you share the **CviUPO sequence (FASTA)** or a UniProt/GenBank accession, I can (i) map **channel residues (F88/T158 equivalents)** precisely, (ii) propose a **minimal smart library** for aromatic peroxygenation (veratryl alcohol/naphthalene), and (iii) suggest **screening thresholds** (P:p ratio cutoffs) aligned with your ABTS/NBD assays.