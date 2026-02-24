## 1) Executive Summary (engineering-relevant; ≤10 bullets)

- **UPOs are secreted heme‑thiolate peroxidase-family enzymes (EC 1.11.2.1)** that generate **P450-like Compound I** directly from **H₂O₂** (peroxide shunt), enabling **aromatic hydroxylation via arene epoxidation** without NAD(P)H/redox partners.  
- **Chemoselectivity is a central bottleneck for aromatics**: desired **peroxygenation (2e⁻ oxygen transfer)** competes with **peroxidative (1e⁻) phenoxy-radical chemistry**, causing **overoxidation/oligomerization** (notably for phenolic products).  
- **Active-site access channel geometry is the dominant selectivity lever** across UPOs: “channel opening/reshaping” mutations repeatedly shift **regio-/chemoselectivity** (and for some substrates, enantioselectivity).  
- **H₂O₂ tolerance and oxidative inactivation** remain key process constraints; reaction engineering (controlled peroxide delivery, radical scavengers) can strongly bias product distributions (e.g., rutin work).  
- **Expression is often the rate-limiting step for engineering**; successful platforms include **S. cerevisiae directed evolution** (AaeUPO) and **E. coli production for some short UPOs (e.g., CviUPO)**; newer workflows combine **AlphaFold2 + PROSS + signal peptide shuffling** to unlock diverse UPOs in **Pichia pastoris**.  
- For **aromatic peroxygenation**, **naphthalene** is a useful mechanistic probe: UPOs can yield **naphthol** (peroxygenation) and **naphthoquinone** (sequential peroxidative oxidation).  
- **ABTS** is a robust **peroxidase-activity reporter** (1e⁻), while **NBD** (5‑nitro‑1,3‑benzodioxole) is widely used as a **peroxygenation reporter**; tracking both enables selection for higher **P:p (peroxygenative:peroxidative) ratio**.  
- **Actionable strategy** for aromatic hydroxylation: co-optimize (i) **channel residues** (sterics/orientation), (ii) **surface/ET sites** that drive 1e⁻ oxidation, and (iii) **process conditions** (pH, peroxide feed, radical scavengers) to suppress phenoxy-radical cascades.

---

## 2) Structural Overview

### Fold classification
- **Heme‑thiolate peroxidase (HTP) superfamily**, related to **chloroperoxidase (CPO)** and mechanistically analogous to P450 “peroxide shunt” chemistry (reviewed in multiple UPO engineering papers; see refs below).
- Two broad size classes (phylogeny-linked): **“long” UPOs (~45 kDa)** and **“short” UPOs (~29 kDa)** (UPObase; reviews).

### Domain architecture
- Typically **single-domain**, secreted enzymes with **N‑terminal signal peptide** (native secretion in fungi; engineered secretion in yeast).
- **Glycosylation** common in fungal secreted forms (important for stability/expression; host-dependent).

### Active site organization
- **Protoporphyrin IX heme** with **axial cysteine thiolate ligand** (defining feature vs classical peroxidases).
- **Distal acid–base pair** (classically **Glu/His** in HTPs) supports H₂O₂ activation; UPO vs CPO motif differences are used for annotation (UPObase notes motif patterns distinguishing UPO-like vs CPO-like sequences).

### Access channels / substrate tunnels
- Substrates reach the heme via a **hydrophobic access channel**; multiple studies show **channel residues are prime engineering targets** controlling:
  - aromatic vs benzylic oxidation
  - regioselectivity on aromatics/alkylbenzenes
  - epoxidation vs hydroxylation on unsaturated substrates
- Example (short UPO, CviUPO): **alanine scanning / channel widening** improved oxygenation selectivity for fatty-acid epoxidation (mechanistic principle transferable to aromatics: tune approach angle/distance to Cpd I oxo).

### Cofactor binding
- **No external cofactors** beyond **heme**; **H₂O₂ is cosubstrate**.
- Some assays/conditions include additives (e.g., **ascorbate** as radical scavenger) that modulate product fate rather than binding as cofactors.

### Known motifs / epitopes (engineering-relevant)
- **Heme-thiolate cysteine** motif region conserved (exact sequence varies by subfamily).
- **UPO vs CPO signature motifs** discussed in UPObase (useful for sequence triage when mining homologs).

---

## 3) Reaction Mechanism (focused on aromatic peroxygenation)

### Catalytic cycle (productive peroxygenation)
1. **Resting state Fe(III)–heme** binds/activates **H₂O₂** at distal pocket.
2. Formation of **Compound 0 (Fe(III)–OOH)** then heterolytic O–O cleavage to **Compound I**: **Fe(IV)=O + porphyrin π‑cation radical** (P450-like oxidant).
3. **Aromatic peroxygenation** proceeds primarily via **arene epoxidation** by Cpd I, followed by **spontaneous NIH shift / rearrangement** to yield **phenolic products** (formal hydroxylation).
4. Return to resting state via **Compound II (Fe(IV)=O)** and proton/electron transfers depending on substrate class.

### Key intermediates
- **Compound I** is the central oxidant (explicitly discussed across engineering papers; also highlighted in epoxidation-cycle depictions for UPOs).
- For some reactions (notably epoxidation), a **transient Cpd II*–substrate radical complex** has been proposed (shown in CviUPO epoxidation paper; conceptually relevant for aromatic radical pathways too).

### Rate-limiting steps (what’s known)
- Often **not uniquely assigned** across UPOs; apparent rates depend strongly on **H₂O₂ delivery** (inactivation/uncoupling) and **substrate access/orientation** (channel control).

### Competing pathways (critical for aromatics)
- **Peroxidative (1e⁻) oxidation**: UPOs can oxidize phenols/anilines etc. to **radicals**, leading to **quinones and oligomers/polymers**.
  - For aromatics like **naphthalene**, literature notes formation of **naphthoquinone** likely via **naphthol → peroxidative oxidation** (ACS Catal. 2021).
  - For polyphenols (e.g., **rutin**), peroxidation can drive **oligomerization**; adding **ascorbate** can bias toward hydroxylated products by quenching radicals (New Biotechnol. 2024).

### Determinants of chemo-/regioselectivity
- **Channel sterics**: controls whether substrate presents an aromatic C–C bond vs benzylic C–H to the oxo.
- **Electronic activation**: electron-rich aromatics more prone to radical side chemistry; phenolic products are especially vulnerable to 1e⁻ oxidation.
- **Reaction conditions**: pH and additives can shift halogenation vs oxygenation modes in some UPO contexts (Chem. Eur. J. 2024), and radical scavengers can suppress peroxidative cascades (New Biotechnol. 2024).

---

## 4) Substrate Scope & Selectivity Trends (aromatics emphasized)

### Accepted substrate classes (validated broadly across UPO literature; specific examples in provided sources)
- **Arenes / polycyclic aromatics**: e.g., **naphthalene → naphthol / naphthoquinone** (ACS Catal. 2021 context).
- **Phenolic/polyphenolic compounds**: prone to **peroxidative coupling** unless controlled (rutin study).
- **Benzylic substrates**: ethylbenzene-type hydroxylations can be highly enantioselective after tunnel engineering (JACS Au 2024; though not aromatic-ring hydroxylation, it informs tunnel control principles).
- **Redox dyes**: **ABTS** is readily oxidized (peroxidase readout).

### Trends / limitations for aromatic peroxygenation
- **Phenolic products are “fragile”**: once formed, they can be further oxidized by UPO peroxidase activity → quinones/polymers (major yield limiter).
- **Polycyclic aromatics**: can undergo sequential oxidation (naphthol → naphthoquinone), making time/peroxide control important.
- **Bulky aromatics**: acceptance depends on channel size; “short” vs “long” UPOs differ in pocket architecture (general trend; specific structural mapping requires sequence/structure for your target UPO).

---

## 5) Engineering Landscape

### (A) Expression and evolvability platforms
- **S. cerevisiae directed evolution (AaeUPO)**: 5 generations, >9000 clones screened; **~3250‑fold total activity improvement** with separation of secretion vs catalytic gains; signal peptide mutations alone gave **~27‑fold** secretion improvement; final secretion reported up to **~8 mg/L** in yeast (Molina‑Espeja et al., 2014).  
- **Pichia pastoris (Komagataella) production**: widely used for preparative enzyme supply; recent **AlphaFold2 + PROSS + signal peptide shuffling** enabled functional expression of **9/10 diverse UPOs** including previously recalcitrant ones (Münch et al., 2024).  
- **E. coli engineering enablement**:
  - rCviUPO is produced in **E. coli** for mutagenesis and process optimization (Linde et al., 2022).
  - A new **sfGFP-mediated secretion system** in E. coli enabled efficient UPO engineering and tunnel ISM to tune enantioselectivity (Yan et al., 2024).

### (B) Mutations affecting activity/selectivity (channel/tunnel)
- **CviUPO channel alanine substitutions**: progressive channel enlargement; **F88A/T158A** notably improved epoxidation selectivity for polyunsaturated fatty acids (Linde et al., 2022). Engineering principle: **reduce steric gating** to allow alternative binding modes / deeper access.  
- **MthUPO engineering for aromatic vs benzylic oxidation**: screening in yeast yielded variants with **up to 16.5‑fold improved kcat/KM** on NBD and variants with strong chemo-/regioselectivity shifts; benzylic hydroxylation up to **95% ee** (Knorrscheidt et al., 2021).  
- **AaeUPO peroxygenative:peroxidative ratio tuning**: structure-guided evolution identified hotspots including **positions 120 and 320** affecting P:p ratio (Mate et al., 2017). This is directly relevant for aromatic hydroxylation where peroxidase activity causes overoxidation.

### (C) Computational / ML-guided design
- **Computationally guided “smart libraries”** for enantioselectivity (β‑ionone) in MthUPO: two rounds, **up to 17‑fold activity increase**, **regioselectivity up to 99.6%**, and strong enantiodivergence (Münch et al., 2023).  
- **AlphaFold2 + PROSS**: stability designs on predicted structures to unlock expression and robustness (Münch et al., 2024). This is a practical route when no crystal structure exists for your UPO.

### Quantitative performance notes (from provided sources)
- AaeUPO evolution: **3250× total activity**, secretion **~8 mg/L** in S. cerevisiae; leader swap analysis: **27× secretion**, **18× kcat/KM** oxygen transfer (Molina‑Espeja et al., 2014).
- MthUPO engineering: **kcat/KM up to 16.5×** improved on NBD; **up to 95% ee** for benzylic hydroxylation (Knorrscheidt et al., 2021).
- CviUPO F88A/T158A: **>80% diepoxides** after ~complete conversion for linoleic/α‑linolenic acids; process optimization enabled high substrate loading and **up to 85% epoxidation yield in 1 h** (Linde et al., 2022).

---

## 6) Practical Constraints (stability, solvent, H₂O₂, formulation, expression)

### H₂O₂ sensitivity / inactivation
- H₂O₂ is both required and a major inactivation driver; operational stability often depends on **controlled dosing** and minimizing radical side reactions (review: Monterrey et al., 2023).
- In process setups (e.g., membrane reactor reuse), **inactivation during handling/filtration** can be significant (New Biotechnol. 2024).

### Uncoupling / side chemistry
- **Peroxidative oxidation** of phenolic products is a major sink for aromatic hydroxylation yields; radical scavengers (e.g., **ascorbate**) can redirect product formation (New Biotechnol. 2024).

### Expression hosts used (from provided sources)
- **S. cerevisiae**: high-throughput directed evolution and secretion engineering (AaeUPO; MthUPO).
- **P. pastoris**: scalable secretion; now boosted by signal peptide/promoter shuffling and PROSS designs.
- **E. coli**: feasible for some short UPOs (CviUPO) and increasingly for engineering via secretion/solubility tricks (sfGFP system).

### Solvent tolerance
- Evolved AaeUPO variants reported **high stability in organic cosolvents** (Molina‑Espeja et al., 2014). (Exact solvent panels/percentages depend on the specific variant and assay; use as a starting expectation rather than universal property.)

---

## 7) Comparative Analysis (seed sequence: CviUPO; plus context UPOs)

### CviUPO (Collariella virescens UPO; short-type; recombinant in E. coli)
- Demonstrated amenability to **access-channel engineering** (alanine substitutions; F88A/T158A) with large selectivity effects (Linde et al., 2022).
- While published engineering focus is fatty-acid epoxidation, the **same channel positions are prime candidates** for aromatic peroxygenation tuning because they modulate substrate approach to Cpd I.

### AaeUPO (Agrocybe/Cyclocybe aegerita; long-type; classic model)
- Deeply engineered for secretion and activity in yeast; also a benchmark for aromatic transformations but prone to peroxidative side reactions on phenolic products (Molina‑Espeja 2014; Mate 2017; rutin paper 2024).

### MthUPO (Myceliophthora thermophila; short-type; yeast-expressed)
- Particularly strong for **chemo-/regioselective aromatic vs benzylic oxidations** after engineering; good platform for aromatic oxidation selectivity campaigns (Knorrscheidt 2021; Münch 2023).

**Trade-off pattern:** channel widening often increases activity/broader scope but can **increase overoxidation** unless P:p ratio and peroxide dosing are controlled.

---

## 8) Engineering Opportunities (actionable hypotheses for aromatic peroxygenation)

### A) Mutation target classes (structure-function logic)
1. **Heme access channel “gating” residues** (steric control)
   - Start with **CviUPO positions analogous to F88 and T158** (known channel hotspots) and nearby hydrophobics lining the tunnel.
   - Goal: enforce a binding pose that favors **arene epoxidation leading to a single phenol** and disfavors product rebinding/overoxidation.
2. **Hotspots affecting P:p ratio**
   - In AaeUPO, **positions 120 and 320** modulate peroxygenative vs peroxidative balance (Mate et al., 2017). Map homologous positions in CviUPO (sequence alignment) and test conservative libraries to suppress 1e⁻ oxidation.
3. **Surface electron-transfer / radical sites (putative)**
   - Evidence suggests multiple oxidation sites may exist (Mate et al., 2017). For aromatic hydroxylation, reducing surface 1e⁻ oxidation capacity could reduce quinone/polymer formation. Practical approach: screen variants for **lower ABTS activity at fixed NBD activity**.

### B) Electrostatic tuning
- Aromatic substrates/products often differ in pKa and redox behavior; tuning distal pocket polarity (without disrupting H₂O₂ activation) may shift:
  - phenol release vs retention
  - propensity for 1e⁻ oxidation
- Use **pH profiling** as a fast proxy for altered protonation networks (also relevant given pH-dependent mode switching reported for UPO oxygenation/halogenation behavior in other contexts).

### C) Stability / expression engineering
- If CviUPO expression or stability is limiting under aromatic reaction conditions:
  - Apply **PROSS on AlphaFold2 model** (Münch et al., 2024) to generate a small set of stabilized designs, then reintroduce active-site libraries.
  - Consider **signal peptide/promoter shuffling** in Pichia for secretion scale-up; for E. coli, consider secretion/solubility tags (sfGFP system concept).

### D) Assay design suggestions (directly aligned to your substrates)
- **Dual readout to select for aromatic peroxygenation while suppressing peroxidation:**
  - **NBD** (peroxygenation reporter; used widely in UPO engineering screens).
  - **ABTS** (peroxidase reporter; penalize high ABTS activity or optimize P:p ratio).
- **Naphthalene panel** (GC/LC readout):
  - Quantify **1‑naphthol vs 1,4‑naphthoquinone** ratio as a direct measure of overoxidation tendency (ACS Catal. 2021).
- **Veratryl alcohol**:
  - Track aldehyde/acid formation vs benzylic alcohol hydroxylation/overoxidation; useful to detect peroxidative drift.
- **Additive screen**:
  - Include **ascorbate** (and possibly other radical scavengers) to test whether product distribution is limited by radical coupling (rutin paper shows strong effect).

---

## 9) References (reviews vs primary; with identifiers)

**Primary research**
- Molina-Espeja, P.; García-Ruiz, E.; González-Pérez, D.; Ullrich, R.; Hofrichter, M.; Alcalde, M. (2014). *Directed Evolution of Unspecific Peroxygenase from Agrocybe aegerita.* **Applied and Environmental Microbiology** 80(11), 3496–3507. DOI: **10.1128/AEM.00490-14**.  
- Mate, D. M.; Palomino, M. A.; Molina-Espeja, P.; Martín-Díaz, J.; Alcalde, M. (2017). *Modification of the peroxygenative:peroxidative activity ratio in the unspecific peroxygenase from Agrocybe aegerita by structure-guided evolution.* **Protein Engineering, Design & Selection** 30(3), 191–198. DOI: **10.1093/protein/gzw073**.  
- Knorrscheidt, A.; Soler, J.; Hünecke, N.; Püllmann, P.; Garcia-Borràs, M.; Weissenborn, M. J. (2021). *Accessing Chemo- and Regioselective Benzylic and Aromatic Oxidations by Protein Engineering of an Unspecific Peroxygenase.* **ACS Catalysis** 11, 7327–7338. DOI: **10.1021/acscatal.1c00847**.  
- Linde, D.; González-Benjumea, A.; Aranda, C.; Carro, J.; Gutiérrez, A.; Martínez, A. T. (2022). *Engineering Collariella virescens Peroxygenase for Epoxides Production from Vegetable Oil.* **Antioxidants** 11, 915. DOI: **10.3390/antiox11050915**. (Open access)  
- Olmedo, A.; Ullrich, R.; Hofrichter, M.; del Río, J. C.; Martínez, Á. T.; Gutiérrez, A. (2022). *Novel Fatty Acid Chain-Shortening by Fungal Peroxygenases Yielding 2C-Shorter Dicarboxylic Acids.* **Antioxidants** 11, 744. DOI: **10.3390/antiox11040744**. PMID: **35453429**.  
- Münch, J.; Soler, J.; Hünecke, N.; Homann, D.; Garcia-Borràs, M.; Weissenborn, M. J. (2023). *Computational-Aided Engineering of a Selective Unspecific Peroxygenase toward Enantiodivergent β‑Ionone Hydroxylation.* **ACS Catalysis** 13, 8963–8972. DOI: **10.1021/acscatal.3c00702**.  
- Münch, J.; Dietz, N.; Barber-Zucker, S.; et al. (2024). *Functionally Diverse Peroxygenases by AlphaFold2, Design, and Signal Peptide Shuffling.* **ACS Catalysis** 14, 4738–4748. DOI: **10.1021/acscatal.4c00883**.  
- Yan, X.; Zhang, X.; Li, H.; et al. (2024). *Engineering of Unspecific Peroxygenases Using a Superfolder-GFP-Mediated Secretion System in Escherichia coli.* **JACS Au** 4, 1654–1663. DOI: **10.1021/jacsau.4c00129**.  
- (Process/side-reaction control) *Exploiting UPO versatility to transform rutin in more soluble and bioactive products.* **New Biotechnology** (2024). PMID: **39181196**.  
- Barber, V.; Mielke, T.; Cartwright, J.; Díaz-Rodríguez, A.; Unsworth, W. P.; Grogan, G. (2024). *Unspecific Peroxygenase can be Tuned for Oxygenation or Halogenation Activity by Controlling the Reaction pH.* **Chemistry – A European Journal** 30, e202401706. DOI: **10.1002/chem.202401706**.

**Databases / resources**
- Muniba, F.; Dongming, L.; Huang, S.; Wang, Y. (2019). *UPObase: an online database of unspecific peroxygenases.* **Database (Oxford)** baz122. DOI: **10.1093/database/baz122**. PMID: **31820805**.

**Review**
- Monterrey, D. T.; Menés-Rubio, A.; Keser, M.; Gonzalez-Perez, D.; Alcalde, M. (2023). *Unspecific peroxygenases: The pot of gold at the end of the oxyfunctionalization rainbow?* **Current Opinion in Green and Sustainable Chemistry** 41, 100786. DOI: **10.1016/j.cogsc.2023.100786**.

---

If you share the **CviUPO sequence (FASTA) or UniProt/GenBank accession**, I can (i) place it in the UPObase subfamily context, (ii) align it to AaeUPO/MthUPO/CmaUPO to **map homologous hotspot positions** (e.g., AaeUPO 120/320; CviUPO F88/T158), and (iii) propose a **minimal smart library** specifically for **naphthalene/veratryl alcohol** hydroxylation with an ABTS/NBD counter-screen.