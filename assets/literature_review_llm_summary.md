## 1. Executive Summary (engineering-relevant; ≤10 bullets)

- **UPOs are secreted heme‑thiolate enzymes (EC 1.11.2.1)** that use **H₂O₂ directly** to generate **Compound I (Fe(IV)=O porphyrin π‑cation radical)**, enabling P450‑like oxyfunctionalization **without NAD(P)H/reductase partners**.  
- **Aromatic peroxygenation** typically proceeds via **arene epoxidation → NIH shift/rearomatization** to phenols; **overoxidation** (e.g., to quinones) often arises from **peroxidase-like 1e⁻ pathways** and radical chemistry (important for naphthalene/phenolics).  
- **Chemoselectivity (peroxygenation vs peroxidation)** is strongly process-dependent: **radical scavengers** (e.g., **ascorbate**) can suppress oligomerization and bias toward hydroxylated products (shown for rutin with AaeUPO).  
- **Active-site access channel geometry is a dominant selectivity lever**: alanine-scanning/channel opening in **rCviUPO** (e.g., **F88A/T158A**) boosts oxygenation selectivity for unsaturated substrates (epoxidation; also a generalizable strategy for aromatics).  
- **Short-type UPOs (e.g., MthUPO, CviUPO)** are currently the most engineerable in heterologous systems; multiple campaigns show that **tunnel residues** are “hotspots” for tuning **regio-/chemo-/enantioselectivity**.  
- **Expression is a primary bottleneck**; solutions now include (i) **signal peptide engineering/shuffling** in yeast, (ii) **stability design (PROSS) on AlphaFold2 models** to unlock secretion in *Pichia*, and (iii) emerging **E. coli secretion/engineering platforms** (sfGFP-mediated).  
- **H₂O₂ tolerance and oxidative inactivation** remain key constraints; practical success often hinges more on **controlled peroxide delivery** and **anti-radical additives** than on catalytic mutations alone.  
- For aromatic targets (veratryl alcohol, naphthalene, NBD-like probes, ABTS), expect **assay-dependent readouts**: ABTS reports **peroxidase activity** (1e⁻ oxidation), not necessarily productive peroxygenation—use orthogonal analytics (GC/LC).  
- **Opportunity:** combine **channel reshaping** (to enforce productive binding poses) with **surface/stability designs** (to survive peroxide/solvent) and **process controls** (fed-batch H₂O₂, scavengers) to reduce peroxidative side chemistry.

---

## 2. Structural Overview

### Fold classification
- **Heme-thiolate peroxidase (HTP) superfamily**, related to **chloroperoxidase (CPO)**.
- Two broad size classes frequently discussed:
  - **Long-type UPOs** (~45 kDa; e.g., AaeUPO)
  - **Short-type UPOs** (~29 kDa; e.g., MthUPO, CviUPO)

### Domain architecture
- Typically **single catalytic domain** with **buried heme** and **solvent-exposed access channel**.
- Secreted fungal enzymes: N‑terminal **signal peptide** (critical for secretion; often engineered).

### Active site organization
- **Protoporphyrin IX heme** with **axial cysteine thiolate ligand** (P450-like).
- Conserved **acid–base catalytic residues** for peroxide activation (general HTP logic): a **distal Glu/Asp** and surrounding H-bond network that supports **heterolytic H₂O₂ cleavage** to Compound I.
- Motif patterns distinguishing UPO vs CPO behavior are used in sequence classification (UPObase notes conserved motifs; UPO vs CPO motif variants are discussed there).

### Access channels / substrate tunnels
- A **heme access channel** governs substrate approach and binding pose; repeatedly shown to control:
  - **Regioselectivity** (which C–H/π-face is presented to Fe=O)
  - **Chemoselectivity** (epoxidation vs hydroxylation vs 1e⁻ oxidation cascades)
- Engineering evidence:
  - **rCviUPO channel alanine substitutions** (including **F88A, T158A**) enlarge/reshape the channel and shift product distributions (demonstrated for fatty-acid epoxidation; conceptually transferable to aromatic binding/orientation).

### Cofactor binding
- Only cofactor is **heme** (no flavins, no NAD(P)H binding).
- Heme incorporation and correct folding/processing are major determinants of functional expression.

---

## 3. Reaction Mechanism (focused on aromatic peroxygenation)

### Catalytic cycle steps (peroxygenase mode)
1. **Resting state:** Fe(III)–heme.
2. **H₂O₂ binding** in distal pocket → **Compound 0 (Fe(III)–OOH)**.
3. **Heterolytic O–O cleavage** (acid–base assisted) → **Compound I** (Fe(IV)=O + porphyrin radical cation).
4. **Oxygen transfer / H‑abstraction chemistry**:
   - **Aromatics:** often **arene epoxidation** by Cpd I → **arene oxide** → **NIH shift/rearomatization** → **phenol** (formal hydroxylation).
   - **Benzylic C–H:** H‑abstraction → substrate radical → OH rebound (typical oxygen rebound logic).
5. Return to Fe(III) resting state.

### Key intermediates
- **Compound I** is the central oxidant (explicitly emphasized in UPO engineering literature).
- **Compound II** (Fe(IV)=O without porphyrin radical) appears after 1e⁻ steps; can participate in rebound chemistry.
- For some transformations (notably epoxidations), a **transient oxoferryl–substrate radical complex** has been proposed (Cpd II* in epoxidation-focused work on UPOs; mechanistic nuance mainly established for alkene epoxidation but relevant to understanding selectivity).

### Rate-limiting steps (what’s known)
- Often **not uniquely assigned across UPOs/substrates**; in practice, apparent rate limitation frequently shifts to:
  - **H₂O₂ activation vs substrate binding** (channel-controlled)
  - **Competition with unproductive peroxide consumption** (catalase-like pathways) and **enzyme inactivation**

### Competing pathways: peroxygenation vs peroxidation
- **Peroxidation (1e⁻ oxidation)** generates **substrate radicals** (phenoxy radicals, etc.) → **coupling/oligomerization**.
- This is central for phenolic/aromatic substrates and explains:
  - **ABTS oxidation** (useful activity assay but not peroxygenation-specific)
  - **Rutin oligomerization** unless radical chemistry is suppressed.

### Determinants of chemo-/regioselectivity
- **Substrate positioning** in the heme channel (distance/angle to Fe=O).
- **Electronic activation** of aromatic ring (electron-rich aromatics oxidize readily; can also overoxidize).
- **Reaction conditions**:
  - **pH** can bias halogenation vs oxygenation modes in some UPO contexts (shown for rAaeUPO-PaDa-I-H; mechanistically via halide oxidation vs direct oxygen transfer).
  - **Radical scavengers** (ascorbate) can suppress peroxidative cascades and favor hydroxylated products (rutin study).

---

## 4. Substrate Scope & Selectivity Trends (with your substrates in mind)

### Broad accepted classes (experimentally established across UPO literature)
- **Aromatics:** hydroxylation (formal), epoxidation of aromatic rings (via arene oxides), oxidative dearomatization/quinone formation (often secondary).
- **Benzylic substrates:** enantioselective benzylic hydroxylation is achievable after engineering (MthUPO work).
- **Alkenes:** epoxidation (often high activity).
- **Heteroatoms:** sulfoxidation, N‑oxidation, dealkylations (common UPO repertoire).

### Selectivity trends relevant to aromatics
- **Electron-rich aromatics** (anisoles, phenols) are prone to **peroxidative radical pathways** → dimers/oligomers unless controlled.
- **Polycyclic aromatics (naphthalene)** can yield **naphthols** and can be further oxidized to **naphthoquinones** (reported as a sequential/side pathway in UPO engineering context).
- **Veratryl alcohol** (electron-rich benzylic alcohol) is likely to undergo **benzylic oxidation/hydroxylation/overoxidation** depending on enzyme and peroxide regime; controlling overoxidation is typically a peroxide-delivery problem plus channel/orientation.

### Notes on your assay substrates
- **ABTS**: primarily reports **peroxidase (1e⁻) activity**; high ABTS activity can correlate with *more* radical side chemistry on phenolics.
- **NBD-type probes**: often used as convenient reporters; interpret carefully because fluorescence changes can reflect multiple oxidation modes.
- **Naphthalene**: good LC/GC target to quantify **1‑naphthol vs 1,4‑naphthoquinone** ratios (a useful chemoselectivity readout).

---

## 5. Engineering Landscape (what has worked, and where)

### Mutations affecting activity/selectivity (channel/tunnel hotspots)
- **rCviUPO (E. coli-produced) channel engineering**:
  - **F88A/T158A** (double mutant) improved epoxidation selectivity for polyunsaturated fatty acids; demonstrates that **opening/reshaping the heme channel** can strongly bias oxygen transfer outcomes.  
  - Broader strategy: **multi-residue alanine substitutions** in the access channel (1–6 residues) to tune access and pose.
- **MthUPO (yeast engineering platform)**:
  - Directed evolution yielded variants with **up to 16.5-fold improved kcat/KM** for an aromatic model substrate (5‑nitro‑1,3‑benzodioxole) and variants with **high chemo-/regioselectivity**; benzylic hydroxylation **up to 95% ee** (primary paper provides these quantitative improvements).
- **CmaUPO (new UPO; E. coli secretion engineering)**:
  - Iterative saturation mutagenesis on **tunnel-lining residues** produced variants switching/enhancing enantioselectivity for ethylbenzene hydroxylation (reported **99% ee (R)** and **84% ee (S)** for different variants).

### Stability / expression improvements
- **AaeUPO directed evolution in *S. cerevisiae***:
  - Large overall improvement (**~3250-fold total activity**) combining secretion + catalytic efficiency; signal peptide mutations alone gave **~27-fold** secretion improvement; catalytic efficiency improved **~18-fold (kcat/KM for oxygen transfer)**; secretion reported up to **~8 mg/L** in that campaign.
- **AlphaFold2 + PROSS + signal peptide shuffling (Pichia pastoris)**:
  - Enabled functional production of **9/10 diverse UPOs**, including previously recalcitrant ones (e.g., CciUPO), indicating a scalable route to “expression-first” enabling technology before selectivity engineering.

### ML-guided / computational design
- **Computationally guided small libraries** (MthUPO β‑ionone work): two rounds yielded **up to 17-fold activity increase**, **regioselectivity up to 99.6%**, and **enantiodivergence** (e.r. up to **96.6:3.4** and **0.3:99.7**). While not aromatic peroxygenation, it validates **structure-guided tunnel shaping** as a high-leverage approach.

---

## 6. Practical Constraints (stability, solvents, H₂O₂, expression)

### H₂O₂ sensitivity / inactivation
- UPOs are **peroxide-driven** and therefore inherently exposed to **oxidative self-damage** (heme bleaching, oxidative modification of residues). Practically:
  - Use **fed-batch/controlled H₂O₂ delivery** (or in situ generation) to reduce inactivation.
  - Expect a tradeoff between **high instantaneous rates** and **TTN**.

### Uncoupling / side reactions
- **Peroxidative radical chemistry** competes strongly for phenolic/aromatic substrates:
  - Leads to **oligomerization** (rutin case).
  - Can be mitigated by **radical scavengers** (ascorbate shown to redirect product formation toward hydroxylated derivatives).

### Expression hosts used (validated)
- **S. cerevisiae**: high-throughput directed evolution platform (AaeUPO, MthUPO).
- **Pichia pastoris**: scalable secretion; now boosted by **signal peptide/promoter shuffling** and **PROSS designs**.
- **E. coli**: feasible for some short-type UPOs (e.g., rCviUPO) and now improved by **sfGFP-mediated secretion** enabling engineering workflows.

### Solvent tolerance
- Evolved AaeUPO variants reported **high stability in organic cosolvents** (qualitatively emphasized; choose cosolvents carefully for aromatic substrates—acetone/MeCN often used in UPO literature).

---

## 7. Comparative Analysis (seed sequence: CviUPO; plus context UPOs)

### CviUPO (short-type; recombinant in E. coli)
- Strength: **engineerable access channel**, good for oxygenation of hydrophobic substrates; demonstrated that **channel opening** can increase oxygen transfer selectivity.
- Likely useful starting scaffold for **aromatic peroxygenation** if expression and peroxide management are adequate.

### AaeUPO (long-type; canonical)
- Strength: broad substrate scope; extensive engineering history for secretion and robustness (PaDa lineage).
- Risk: for phenolic/aromatic substrates, can show strong **peroxidative side chemistry** unless controlled (rutin oligomerization).

### MthUPO (short-type; yeast-friendly)
- Strength: demonstrated **chemo-/regioselectivity engineering** for aromatic/benzylic oxidations with quantitative gains; good platform for library screening.

**Trade-off pattern:** short-type UPOs tend to be more tractable for heterologous expression/engineering and tunnel-focused selectivity tuning; long-type AaeUPO has deep mechanistic/engineering precedent and process know-how.

---

## 8. Engineering Opportunities (actionable hypotheses for aromatic peroxygenation)

### A. Channel/gating targets (highest leverage)
- **Map and mutate tunnel-lining residues** (CAST/ISM style) to:
  - Enforce a **single binding pose** for aromatics (reduce multiple hydroxylation sites).
  - Increase **π-face control** for naphthalene (bias 1‑naphthol vs other isomers; suppress quinone formation by limiting residence time/secondary oxidation).
- For **CviUPO**, start from known channel positions **F88 and T158** (and neighboring channel residues used in alanine-scanning) as a “first shell” library; expand to second-shell residues if activity drops.

### B. Chemoselectivity control: suppress peroxidation
- **Assay with and without radical scavengers** (ascorbate; possibly TEMPO-like controls) to quantify how much product comes from radical pathways.
- Engineer toward lower 1e⁻ oxidation propensity by:
  - Reducing binding/ET competence for phenolic radicals (often hard), but practically by **process**: lower peroxide, shorter residence, scavengers.

### C. H₂O₂ tolerance / operational stability
- If your constraint includes H₂O₂ tolerance, prioritize:
  - **Stability design (PROSS)** on AF2 models for your chosen scaffold (especially if moving to *Pichia*).
  - Screening under **peroxide stress** (e.g., stepwise H₂O₂ pulses) to select variants with higher residual activity.

### D. Expression strategy (choose early)
- If you need **high-throughput engineering** for aromatics:
  - **S. cerevisiae (microtiter secretion)** for directed evolution (proven for MthUPO/AaeUPO).
- If you need **rapid enzyme supply** and can accept lower throughput:
  - **E. coli** for CviUPO-like short UPOs; consider newer secretion/engineering systems (sfGFP-mediated) to accelerate ISM on tunnel residues.
- If you need **scale and formulation**:
  - **Pichia pastoris** + **signal peptide shuffling**; consider **AF2→PROSS** to unlock difficult sequences.

### E. Assay design suggestions (for your substrates)
- Use **orthogonal readouts**:
  - **ABTS** for peroxidase activity (control for radical propensity), but do not optimize solely on ABTS.
  - **GC/LC** for veratryl alcohol (veratraldehyde/acid vs hydroxylated products), naphthalene (naphthol vs naphthoquinone), and NBD probes (confirm structures).
- Include a **peroxide feed regime** in screening (e.g., glucose oxidase or syringe pump) to select variants that perform under realistic conditions.

---

## 9. References (reviews/tools vs primary)

**Primary research**
- Molina-Espeja, P.; García-Ruiz, E.; González-Pérez, D.; Ullrich, R.; Hofrichter, M.; Alcalde, M. (2014). *Directed Evolution of Unspecific Peroxygenase from Agrocybe aegerita.* **Applied and Environmental Microbiology** 80(11), 3496–3507. DOI: **10.1128/AEM.00490-14**.  
- Knorrscheidt, A.; Soler, J.; Hünecke, N.; Püllmann, P.; Garcia-Borràs, M.; Weissenborn, M. J. (2021). *Accessing Chemo- and Regioselective Benzylic and Aromatic Oxidations by Protein Engineering of an Unspecific Peroxygenase.* **ACS Catalysis** 11, 7327–7338. DOI: **10.1021/acscatal.1c00847**.  
- Linde, D.; González-Benjumea, A.; Aranda, C.; Carro, J.; Gutiérrez, A.; Martínez, A. T. (2022). *Engineering Collariella virescens Peroxygenase for Epoxides Production from Vegetable Oil.* **Antioxidants** 11, 915. DOI: **10.3390/antiox11050915**. (Open access)  
- Olmedo, A.; Ullrich, R.; Hofrichter, M.; del Río, J. C.; Martínez, Á. T.; Gutiérrez, A. (2022). *Novel Fatty Acid Chain-Shortening by Fungal Peroxygenases Yielding 2C-Shorter Dicarboxylic Acids.* **Antioxidants** 11(4), 744. DOI: **10.3390/antiox11040744**. PMID: **35453429**. (Open access)  
- Münch, J.; Soler, J.; Hünecke, N.; Homann, D.; Garcia-Borràs, M.; Weissenborn, M. J. (2023). *Computational-Aided Engineering of a Selective Unspecific Peroxygenase toward Enantiodivergent β‑Ionone Hydroxylation.* **ACS Catalysis** 13, 8963–8972. DOI: **10.1021/acscatal.3c00702**.  
- Münch, J.; Dietz, N.; Barber-Zucker, S.; et al. (2024). *Functionally Diverse Peroxygenases by AlphaFold2, Design, and Signal Peptide Shuffling.* **ACS Catalysis** 14, 4738–4748. DOI: **10.1021/acscatal.4c00883**.  
- Barber, V.; Mielke, T.; Cartwright, J.; Díaz-Rodríguez, A.; Unsworth, W. P.; Grogan, G. (2024). *Unspecific Peroxygenase Can be Tuned for Oxygenation or Halogenation Activity by Controlling the Reaction pH.* **Chemistry – A European Journal** 30, e202401706. DOI: **10.1002/chem.202401706**.  
- Yan, X.; Zhang, X.; Li, H.; et al. (2024). *Engineering of Unspecific Peroxygenases Using a Superfolder-Green-Fluorescent-Protein-Mediated Secretion System in Escherichia coli.* **JACS Au** 4, 1654–1663. (DOI in article PDF; not provided in your excerpt.)

**Databases / tools**
- Muniba, F.; Dongming, L.; Huang, S.; Wang, Y. (2019). *UPObase: an online database of unspecific peroxygenases.* **Database (Oxford)**. DOI: **10.1093/database/baz122**. PMID: **31820805**. (Open access)  
- (Process/biotransformation example) 2024 rutin study: PMID **39181196** (*New Biotechnology*). (Not open access; useful for peroxygenation vs peroxidation process control via ascorbate and reactor handling stability issues.)

---

If you share (i) your intended expression host (yeast vs *E. coli*), (ii) target aromatic(s) and desired product(s) (e.g., specific hydroxylation position on veratryl alcohol or naphthalene), and (iii) solvent/peroxide regime, I can propose a **first-round mutational map** for CviUPO (channel residues + second-shell polar network) and a **screening panel** that separates peroxygenation from peroxidation early.