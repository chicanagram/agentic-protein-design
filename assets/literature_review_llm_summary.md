## 1. Executive Summary (engineering-relevant takeaways; ≤10 bullets)

- **UPOs are secreted heme‑thiolate enzymes (EC 1.11.2.1)** that generate **P450-like Compound I** directly from **H₂O₂** (peroxide shunt), enabling high-rate **aromatic hydroxylation (formal), benzylic hydroxylation, epoxidation**, etc., without NAD(P)H/redox partners.  
- **Chemoselectivity is a central bottleneck for aromatics**: desired **peroxygenation (2e⁻ O‑transfer)** competes with **peroxidative 1e⁻ oxidation** of phenolic products → **radicals/quinones/polymerization**; radical scavengers (e.g., **ascorbate**) can bias toward hydroxylated products (rutin case).  
- **Active-site access channel geometry is the dominant selectivity lever** across UPOs: multiple studies show that **reshaping the heme channel/tunnel** shifts **regio-, chemo-, and enantioselectivity** (e.g., CviUPO F88A/T158A; MthUPO engineered variants; CmaUPO tunnel ISM).  
- **Short- vs long-type UPOs** differ in size and pocket architecture; short-type enzymes (e.g., **MthUPO**) are particularly amenable to **yeast HT screening** and selectivity engineering for aromatic/benzylic oxidations.  
- **Expression is often the rate-limiting step for engineering**, not catalysis: signal peptide engineering/shuffling and stability design (PROSS on AF2 models) can unlock production for otherwise “recalcitrant” UPOs.  
- **H₂O₂ tolerance and oxidative inactivation** remain key constraints; reaction engineering (controlled dosing, in situ generation) and protein engineering (stability designs, surface/loop mutations) are both used.  
- **Aromatic substrates of interest (ABTS, NBD, naphthalene)** map well onto established UPO screening paradigms: ABTS reports peroxidase activity; NBD and related probes report peroxygenation; naphthalene reports aromatic hydroxylation/overoxidation propensity.  
- **pH can switch reaction manifolds** (oxygenation vs halogenation) in AaeUPO variants, highlighting that **process conditions can re-route Compound I usage** and should be co-optimized with mutations.  
- **Best near-term engineering strategy for aromatic peroxygenation**: (i) pick a UPO with good heterologous expression (MthUPO-like) or enable expression via signal peptide/PROSS; (ii) **tunnel/channel libraries**; (iii) **screen for high peroxygenation/peroxidation ratio** under controlled H₂O₂ feed + radical quenchers.

---

## 2. Structural Overview

### Fold classification
- **Heme-thiolate peroxidase (HTP) superfamily**; structurally related to **chloroperoxidase (CPO)** and functionally bridging **heme peroxidases** and **P450s** (peroxide shunt).

### Domain architecture
- Typically **single-domain globular heme enzyme**, secreted fungal proteins.
- Two broad size classes (phylogeny-based):  
  - **Long-type UPOs** (~45 kDa; e.g., AaeUPO)  
  - **Short-type UPOs** (~29 kDa; e.g., MthUPO)  
  (classification summarized in reviews; UPObase organizes subfamilies/motifs).

### Active site organization
- **Buried heme** with **axial cysteine thiolate ligand** (P450-like).
- **Acid–base residues** in the distal pocket support H₂O₂ activation (general HTP logic; specific residue identities vary by UPO and are typically inferred from homology/structures—experimentally validated for only a few UPOs).

### Access channels / substrate tunnels
- **Hydrophobic heme access channel** is repeatedly identified as the **primary determinant** of:
  - substrate scope (size/polarity)
  - **regioselectivity** (which aromatic position/benzylic site approaches oxo)
  - **chemoselectivity** (epoxidation vs hydroxylation; aromatic hydroxylation vs overoxidation)
- Engineering examples directly target channel residues:
  - **CviUPO**: alanine substitutions in the access channel; **F88A/T158A** notably improves epoxidation selectivity for polyunsaturated fatty acids (demonstrates channel control principle).  
  - **CmaUPO**: ISM on tunnel residues (T125/A129 etc.) tunes enantioselectivity in benzylic hydroxylation.

### Cofactor binding
- **Protoporphyrin IX heme b** (noncovalent) is the only cofactor; no reductase domain.

### Known motifs / signatures
- UPObase reports **signature motifs** distinguishing UPOs vs CPO-like sequences and subdividing UPOs into multiple subfamilies (useful for sequence selection and annotation).  
  - Practical note: for new sequences, motif checks + secretion signal + predicted heme-thiolate cysteine region are fast triage before expression work.

---

## 3. Reaction Mechanism (focused on aromatic peroxygenation)

### Catalytic cycle (productive peroxygenation)
1. **Resting state Fe(III)–heme** binds/activates **H₂O₂** in distal pocket.
2. Formation of **Compound 0 (Fe(III)–OOH)** (often invoked).
3. Heterolytic O–O cleavage → **Compound I** (**Fe(IV)=O + porphyrin radical cation**).
4. **Aromatic oxidation**:
   - Often described as **initial arene epoxidation** (arene oxide) followed by **NIH shift/rearomatization** → **phenol (formal hydroxylation)**.
5. Return to Fe(III) resting state.

### Key intermediates
- **Compound I** is the central oxidant (experimentally supported in UPO literature; emphasized in directed evolution paper context).
- For some reactions (notably alkene epoxidation), a **Compound II*–substrate radical complex** has been proposed to facilitate cyclization (reported in fatty-acid epoxidation context; conceptually relevant to aromatic vs benzylic pathways).

### Rate-limiting steps (what’s known)
- Often **mass transfer / substrate access** and **H₂O₂ delivery** dominate observed rates in preparative settings; intrinsic chemical step can be fast once productive binding occurs. Quantitative RLS assignments are substrate/UPO-specific and not consistently established across the family.

### Competing pathways (critical for aromatics)
- **Peroxidative (1e⁻) oxidation**: UPOs also oxidize electron-rich aromatics/phenols via 1e⁻ steps → **phenoxyl radicals → quinones/oligomers**.
  - This is especially problematic because **peroxygenation products (phenols)** become **peroxidase substrates**, reducing yield and causing polymerization/fouling.
  - **Ascorbic acid** can suppress radical propagation and bias toward hydroxylated products (rutin study).

### Determinants of chemo-/regioselectivity
- **Channel geometry + substrate positioning** relative to Fe(IV)=O is the dominant structural determinant (supported by multiple engineering campaigns).
- **Reaction conditions** (pH, halides, radical scavengers, H₂O₂ feed) can re-route Compound I usage:
  - pH-dependent switching between **halogenation vs oxygenation** has been demonstrated for an AaeUPO variant (process lever).

---

## 4. Substrate Scope & Selectivity Trends (with emphasis on aromatics)

### Accepted substrate classes (validated broadly across UPO literature; specific examples in provided sources)
- **Aromatics**: hydroxylation (formal), epoxidation/overoxidation to quinones (e.g., naphthalene → naphthol/naphthoquinone in MthUPO work).
- **Benzylic C–H**: hydroxylation with tunable enantioselectivity (MthUPO engineering; CmaUPO engineering).
- **Phenolic/redox dyes**: **ABTS** is widely used as a **peroxidase activity reporter** (and in CmaUPO screening).
- **Peroxygenation probes**: **NBD** used as a peroxygenase activity reporter (CmaUPO paper).
- **Bulky polyphenols**: rutin transformation shows both peroxygenation and peroxidation/oligomerization.

### Trends relevant to aromatic peroxygenation
- **Electron-rich aromatics/phenols** are prone to **peroxidative radical chemistry** → lower isolated yields unless radical pathways are suppressed.
- **Polycyclic aromatics (e.g., naphthalene)** can show **sequential oxidation** (naphthol → naphthoquinone) depending on enzyme and conditions (MthUPO study context).
- **Selectivity is highly enzyme-dependent**; short-type vs long-type UPOs can differ markedly in product ratios even for the same aromatic substrate.

### Known limitations
- **Overoxidation** and **polymerization** for phenolic products.
- **Solubility constraints** for hydrophobic aromatics; cosolvents help but can trade off with stability and H₂O₂ sensitivity.

---

## 5. Engineering Landscape

### (A) Mutations affecting activity/selectivity (channel/tunnel-centric)
- **CviUPO (E. coli recombinant)**: systematic alanine substitutions in access channel; **F88A/T158A** improved epoxidation selectivity (demonstrates that **opening/reshaping** the channel can increase productive binding/orientation).  
  - Ref: Linde et al., 2022 (Antioxidants) DOI: 10.3390/antiox11050915.
- **MthUPO (S. cerevisiae engineering)**: screening of >5300 transformants yielded variants with **up to 16.5-fold improved kcat/KM** for **5‑nitro‑1,3‑benzodioxole** and strong shifts in chemo-/regioselectivity for aromatic vs benzylic oxidations; benzylic hydroxylation up to **95% ee**.  
  - Ref: Knorrscheidt et al., 2021 (ACS Catal.) DOI: 10.1021/acscatal.1c00847.
- **CmaUPO (E. coli sfGFP secretion platform + ISM)**: tunnel residue targeting produced variants with **enantioselectivity reversal/enhancement** in ethylbenzene hydroxylation: WT ~21% ee (R) → **99% ee (R)** (T125A/A129G) or **84% ee (S)** (T125A/A129V/A247H/T244A/F243G).  
  - Ref: Yan et al., 2024 (JACS Au) DOI: 10.1021/jacsau.4c00129.

### (B) Peroxygenase vs peroxidase ratio engineering (aromatics-critical)
- **AaeUPO structure-guided evolution** targeted flexible loops; mutations at **positions 120 and 320** strongly affected the **peroxygenative:peroxidative (P:p) ratio**, sometimes at stability cost; subsequent combinatorial saturation recovered stability.  
  - Ref: Mate et al., 2017 (Protein Eng. Des. Sel.) DOI: 10.1093/protein/gzw073.

### (C) Expression improvements (major enabler)
- **Directed evolution in S. cerevisiae (AaeUPO)** achieved **~3250-fold total activity improvement**, decomposed into **~27-fold secretion gain** from signal peptide mutations and **~18-fold catalytic efficiency gain** for oxygen transfer; reported functional expression up to **~8 mg/L** in yeast in that campaign.  
  - Ref: Molina-Espeja et al., 2014 (Appl. Environ. Microbiol.) DOI: 10.1128/AEM.00490-14.
- **AF2 + PROSS + signal peptide shuffling (P. pastoris)**: enabled functional production of **9/10 diverse UPOs**, including previously recalcitrant enzymes (e.g., CciUPO) and even oomycete UPOs; establishes a scalable route to expand the enzyme panel before selectivity engineering.  
  - Ref: Münch et al., 2024 (ACS Catal.) DOI: 10.1021/acscatal.4c00883.
- **sfGFP-mediated secretion in E. coli** provides a faster engineering chassis for UPOs (demonstrated generality across multiple UPOs).  
  - Ref: Yan et al., 2024 (JACS Au) DOI: 10.1021/jacsau.4c00129.

### (D) Computational/ML-guided design
- **Computational-aided smart libraries** for MthUPO enabled **enantiodivergent** β‑ionone hydroxylation with **e.r. up to 96.6:3.4 (R)** and **0.3:99.7 (S)**; activity up to **17-fold** and regioselectivity up to **99.6%** for a single hydroxylation site.  
  - Ref: Münch et al., 2023 (ACS Catal.) DOI: 10.1021/acscatal.3c00702.
- PROSS stability design (above) is a key computational lever for expression/stability rather than selectivity per se.

---

## 6. Practical Constraints (stability, expression, formulation)

### H₂O₂ sensitivity / inactivation
- H₂O₂ is both cosubstrate and inactivator; operational stability often depends on **controlled dosing** and minimizing local peroxide spikes.
- In process contexts (e.g., membrane reactor reuse), **inactivation during handling/filtration** can be significant (rutin study).

### Uncoupling / side reactions
- For aromatics: **peroxidative radical chain chemistry** is a major yield killer; mitigation includes:
  - radical scavengers (ascorbate shown)
  - minimizing residence time of phenolic products with active enzyme
  - tuning P:p ratio via mutations (AaeUPO loop engineering)

### Expression hosts used (from provided sources)
- **S. cerevisiae**: high-throughput directed evolution platform (AaeUPO, MthUPO).
- **P. pastoris**: scalable secretion; compatible with signal peptide/promoter shuffling; used with AF2+PROSS workflow.
- **E. coli**: possible for some UPOs (CviUPO, CmaUPO) but historically difficult; improved by **sfGFP secretion** strategy.

### Solvent tolerance
- Evolved AaeUPO variants reported **high stability in organic cosolvents** (Molina-Espeja 2014), relevant for aromatic substrate solubility.

---

## 7. Comparative Analysis (seed sequence: CviUPO; plus engineering workhorses)

### CviUPO (Collariella virescens UPO)
- Strength: **E. coli recombinant availability** and demonstrated **channel mutability** (F88A/T158A) with large selectivity effects (shown for fatty-acid epoxidation; principle transferable to aromatic access/orientation problems).
- Likely short-type (ascomycete UPOs often are; confirm by sequence length/motifs).

### AaeUPO (Agrocybe/Cyclocybe aegerita UPO; long-type archetype)
- Deep mechanistic/engineering history; strong secretion engineering precedent; but aromatic products often suffer from peroxidative follow-up unless controlled.

### MthUPO (Myceliophthora thermophila; short-type)
- Demonstrated **high heterologous expression** and **amenability to selectivity engineering** for **aromatic vs benzylic** oxidation; good candidate chassis for aromatic peroxygenation campaigns.

### CmaUPO (Coprinopsis marcescibilis)
- Newer enzyme with **E. coli engineering platform**; tunnel ISM yields strong enantioselectivity control (benzylic). For aromatic peroxygenation, would need substrate-specific validation.

---

## 8. Engineering Opportunities (actionable hypotheses for aromatic peroxygenation)

### A. Reduce peroxidative follow-up on phenolic products (increase “true peroxygenation yield”)
- **Target P:p ratio hotspots** (AaeUPO positions analogous to **120/320**; map by alignment to your chosen UPO) and screen explicitly on **aromatic hydroxylation product stability** (phenol → quinone/polymer).
- **Assay design**: couple product analytics (HPLC/GC) with a **polymerization/quinone readout** (UV-vis signatures) to penalize peroxidative pathways.

### B. Channel/tunnel reshaping for aromatic binding pose control
- Build **focused libraries** on residues lining:
  - **channel entrance “gate”** (often aromatic residues; CviUPO F88 is an example of a gate-like position)
  - **mid-channel constrictions** (positions analogous to T158 in CviUPO)
  - **near-heme positioning residues** (determine face/edge approach of aromatic ring)
- Use **small smart libraries** (2–6 positions) guided by AF2 models + docking/MD (as in MthUPO β‑ionone work).

### C. Process co-optimization as a selectivity lever (especially for aromatics)
- **Controlled H₂O₂ feed** (syringe pump or in situ generation) to reduce oxidative inactivation and radical chemistry.
- **Radical scavengers** (ascorbate) as a tunable knob; screen with/without scavenger to identify variants intrinsically less peroxidative.
- **pH profiling**: since pH can switch manifolds (oxygenation vs halogenation), also use pH to suppress unwanted side chemistry for your aromatic targets.

### D. Expression/stability-first strategy to expand the UPO panel
- If your constraint includes “expression host” and you need throughput:
  - **P. pastoris + signal peptide shuffling** (and optionally **AF2+PROSS**) is currently one of the most reliable ways to obtain multiple UPOs for head-to-head aromatic screening.
  - For rapid mutational cycles, consider **E. coli sfGFP secretion** if your target UPO is compatible.

### E. Suggested screening stack for your listed substrates
- **ABTS**: track peroxidase activity (undesired for aromatic hydroxylation yield, but useful as expression/activity proxy).
- **NBD**: track peroxygenation activity (used in CmaUPO characterization).
- **Naphthalene**: track aromatic hydroxylation vs overoxidation (naphthol vs naphthoquinone ratio; sensitive to chemoselectivity).
- **Veratryl alcohol**: benzylic oxidation model; can reveal whether variants bias toward benzylic vs aromatic ring oxidation.
- Add a **phenol “overoxidation challenge”** (e.g., start from naphthol or guaiacol-like phenols) to quantify peroxidative propensity directly.

---

## 9. References (reviews and primary; with DOI/PMID where available)

**Databases / resources**
- Muniba, F.; Dongming, L.; Huang, S.; Wang, Y. (2019). *UPObase: an online database of unspecific peroxygenases.* **Database (Oxford)**. DOI: **10.1093/database/baz122**. PMID: **31820805**.

**Expression & directed evolution**
- Molina-Espeja, P.; García-Ruiz, E.; González-Pérez, D.; Ullrich, R.; Hofrichter, M.; Alcalde, M. (2014). *Directed Evolution of Unspecific Peroxygenase from Agrocybe aegerita.* **Applied and Environmental Microbiology** 80, 3496–3507. DOI: **10.1128/AEM.00490-14**.
- Münch, J.; Dietz, N.; Barber-Zucker, S.; et al. (2024). *Functionally Diverse Peroxygenases by AlphaFold2, Design, and Signal Peptide Shuffling.* **ACS Catalysis** 14, 4738–4748. DOI: **10.1021/acscatal.4c00883**.

**Selectivity engineering (aromatics/benzylic)**
- Knorrscheidt, A.; Soler, J.; Hünecke, N.; et al. (2021). *Accessing Chemo- and Regioselective Benzylic and Aromatic Oxidations by Protein Engineering of an Unspecific Peroxygenase.* **ACS Catalysis** 11, 7327–7338. DOI: **10.1021/acscatal.1c00847**.
- Münch, J.; Soler, J.; Hünecke, N.; et al. (2023). *Computational-Aided Engineering of a Selective Unspecific Peroxygenase toward Enantiodivergent β‑Ionone Hydroxylation.* **ACS Catalysis** 13, 8963–8972. DOI: **10.1021/acscatal.3c00702**.
- Yan, X.; Zhang, X.; Li, H.; et al. (2024). *Engineering of Unspecific Peroxygenases Using a Superfolder-Green-Fluorescent-Protein-Mediated Secretion System in Escherichia coli.* **JACS Au** 4, 1654–1663. DOI: **10.1021/jacsau.4c00129**.

**Peroxygenation vs peroxidation control**
- Mate, D. M.; Palomino, M. A.; Molina-Espeja, P.; et al. (2017). *Modification of the peroxygenative-peroxidative activity ratio in the unspecific peroxygenase from Agrocybe aegerita by structure-guided evolution.* **Protein Engineering, Design & Selection** 30, 191–198. DOI: **10.1093/protein/gzw073**.

**CviUPO engineering (channel)**
- Linde, D.; González-Benjumea, A.; Aranda, C.; Carro, J.; Gutiérrez, A.; Martínez, A. T. (2022). *Engineering Collariella virescens Peroxygenase for Epoxides Production from Vegetable Oil.* **Antioxidants** 11, 915. DOI: **10.3390/antiox11050915**. PMID: **35624779**.

**Mechanism/process & side reactions (aromatic polyphenols)**
- (2024). *Exploiting UPO versatility to transform rutin in more soluble and bioactive products.* **New Biotechnology**. PMID: **39181196**.
- Barber, V.; Mielke, T.; Cartwright, J.; Díaz-Rodríguez, A.; Unsworth, W. P.; Grogan, G. (2024). *Unspecific Peroxygenase can be Tuned for Oxygenation or Halogenation Activity by Controlling the Reaction pH.* **Chemistry – A European Journal**. DOI: **10.1002/chem.202401706**.
- Monterrey, D. T.; Menés-Rubio, A.; Keser, M.; Gonzalez-Perez, D.; Alcalde, M. (2023). *Unspecific peroxygenases: The pot of gold at the end of the oxyfunctionalization rainbow?* **Current Opinion in Green and Sustainable Chemistry** 41, 100786. DOI: **10.1016/j.cogsc.2023.100786**. (Review)

---

If you share the **CviUPO sequence (FASTA) and your intended expression host**, I can (i) map **channel/tunnel residues** by alignment to published engineered positions (e.g., F88/T158 equivalents), (ii) propose a **10–30 variant smart library** for aromatic peroxygenation, and (iii) outline an **ABTS/NBD/naphthalene triage screen** that explicitly selects against peroxidative overoxidation.