## 1) Executive Summary (engineering-relevant; <=10 bullets)

- **All four seeds (RML, TLL, CALB, CALA) are α/β-hydrolase serine lipases** using a **Ser–His–Asp/Glu catalytic triad** and an **acyl-enzyme intermediate**; sugar-ester synthesis is the *reverse* of hydrolysis and is governed by **water activity (a_w)** and **mass transfer/solubility** rather than intrinsic chemistry.  
- **Key process bottleneck for sucrose/glucose esters is substrate phase behavior**: sugars are poorly soluble in hydrophobic media; best-performing systems use **(i) polar co-solvents (t-amyl alcohol/DMSO), (ii) ionic liquids, or (iii) solvent-free “sugar crystal suspensions”** plus aggressive water removal. (Ferrer 2005; Lee 2004; Ye 2010; Ye 2016; Shin 2019)  
- **Regioselectivity is lipase-dependent and is a major “design knob”**: in sucrose acylation, **TLL tends to favor monoacylation (notably 6-O-acylsucrose)** while **CALB more readily gives diacylated sucrose (e.g., 6,6′-diacylsucrose)** under comparable solvent-mixture conditions. (Ferrer 2005)  
- **Water management is mechanistically central**: water is a coproduct in esterification and also required for enzyme hydration; optimal synthesis typically occurs at **very low but nonzero a_w**, using **molecular sieves/CaSO₄, N₂/vacuum stripping, or headspace drying**. (Lee 2004; Ye 2016)  
- **Immobilization is not just for reuse—supports tune microenvironment and a_w**: hydrophobic adsorption (octyl supports, acrylic resins like Novozym 435) can “hyperactivate” some lipases and improve stability, but can also change product distribution (mono vs diesters) by shifting effective a_w and local polarity. (Siόdmiak 2025; Ye 2016)  
- **For aqueous/partly aqueous operation (your constraint), expect equilibrium to fight you**: productive sugar esterification generally requires **low water activity**; in water-rich systems, engineering must focus on **(i) shifting equilibrium via activated acyl donors (vinyl esters), (ii) in situ water scavenging, (iii) biphasic/reactive extraction, or (iv) acyltransferase-like behavior**.  
- **RML/TLL have lids (interfacial activation); CALB has minimal/atypical lid behavior**: lid/gating affects access of bulky sugars and can be engineered; CALB’s “lid” remains debated but its active site is relatively accessible and often excels in organic media. (Aloulou 2006; Khan 2017; Siόdmiak 2025)  
- **Engineering successes in RML are strong and transferable as a platform**: directed evolution including the **propeptide** can boost k_cat ~7× (hydrolysis assay) and multiple semi-rational campaigns improved **thermostability and activity** (including cavity redesign giving large T_m and activity gains). (Wang 2012; Zhang 2023 AEM; Moroz 2019)  
- **Opportunity hypothesis**: for sucrose/glucose esters, the best combined strategy is **process-first (solubility + a_w control) + enzyme-second (tunnel/lid/pocket electrostatics)**; engineering alone rarely compensates for poor sugar availability.

---

## 2) Structural Overview (focus: **Rhizomucor miehei lipase, RML**)

**Databases/structures (experimentally solved):**
- RML mature enzyme is a **class 3 fungal lipase** (α/β-hydrolase fold) with **lid-closed and lid-open conformations** (classic interfacial activation behavior). (Moroz 2019; Khan 2017)
- Catalytic triad (mature RML numbering commonly reported): **Ser144–Asp203–His257**. (Huang 2014; Moroz 2019)

### Fold classification
- **α/β-hydrolase fold**: central β-sheet flanked by α-helices; catalytic Ser sits in the conserved “nucleophile elbow” motif typical of lipases.

### Domain architecture
- **Signal peptide + propeptide + mature catalytic domain** in native secretion. Propeptide is ~65–70 aa and is not merely a folding helper: it can bind the mature enzyme and **inhibit/occlude the active site region** (structural complexes solved). (Moroz 2019)

### Active site organization
- **Catalytic triad**: Ser (nucleophile), His (general base/acid), Asp (His polarization).
- **Oxyanion hole**: backbone NH donors stabilize tetrahedral intermediates (canonical for serine hydrolases; specific residues depend on lipase family).
- **Lid helix/loop**: movement exposes a hydrophobic patch and opens access to the catalytic Ser (interfacial activation). (Khan 2017)

### Binding pocket properties (relevant to sugar esters)
- Native pocket is optimized for **long-chain acyl groups**; sugar binding is typically weak because sugars are **polyhydroxylated and bulky**, requiring:
  - sufficient **pocket mouth width / tunnel openness**,
  - **polar anchoring points** near the alcohol-binding region,
  - and/or **solvent-mediated presentation** (DMSO/tert-alcohol/ILs; or solid sugar micro-suspensions).

### Access channels / tunnels
- RML has a substrate access region controlled by the lid; recent computational engineering in RML emphasizes **internal cavities and tunnel optimization** as stability/activity levers (though not yet specifically for sugars). (Zhang 2023 AEM; Chong 2024 review)

### Cofactor binding
- **No cofactors** required.

### Known motifs/epitopes
- **Propeptide–mature enzyme interaction surface** is an engineering handle (expression, folding, activity tuning). (Wang 2012; Moroz 2019)

---

## 3) Reaction Mechanism (lipase-catalyzed esterification → sugar esters)

### Catalytic cycle (esterification direction)
1. **Activation of Ser**: His abstracts proton from Ser-OH (Asp stabilizes His).
2. **Acylation step**: Ser-O⁻ attacks fatty acid (or activated acyl donor like vinyl ester), forming **tetrahedral oxyanion intermediate** → collapses to **acyl-enzyme** + leaving group (water in hydrolysis; alcohol/vinyl alcohol in transesterification).
3. **Deacylation step**: sugar hydroxyl (e.g., sucrose primary OH at C6/C6′; glucose C6) attacks acyl-enzyme → second tetrahedral intermediate → collapses to **sugar ester** + regenerated Ser-OH.

### Key intermediates
- **Acyl-enzyme (Ser–O–C(O)R)** is central.
- Two **tetrahedral oxyanion intermediates** (acylation and deacylation).

### Rate-limiting steps (practically, in sugar ester synthesis)
- Often **not intrinsic chemistry** but:
  - **mass transfer** (sugar availability at enzyme surface),
  - **partitioning into enzyme microenvironment**,
  - **water activity control** (equilibrium + competitive hydrolysis),
  - **product inhibition/phase changes** (sugar ester can act as surfactant and change interfacial properties). (Aloulou 2006; Gumel 2011; Ye 2010)

### Competing pathways
- **Hydrolysis of product** (dominant when a_w too high).
- **Over-acylation** (mono → diesters) depending on enzyme + microenvironment (CALB tends to more diacylation than TLL in sucrose systems). (Ferrer 2005; Ye 2016)

### Determinants of chemo-/regioselectivity
- **Primary vs secondary hydroxyl preference**: lipases typically favor **primary OH** (less hindered), hence sucrose **6-O** and **6′-O** positions are common targets.
- **Enzyme-specific pocket geometry** and **lid-open state population**.
- **Solvent polarity** and **a_w** shift mono/diester distribution.

---

## 4) Substrate Scope & Selectivity Trends (sugar ester focus)

### Sugars / polyols (acyl acceptors)
- Demonstrated acceptors include **glucose, fructose, sucrose, maltose, xylitol, sorbitol, methyl glucoside**; higher conversions correlate strongly with **sugar solubility** in the chosen medium. (Lee 2004; Ferrer 2005; Ye 2010)

### Acyl donors
- **Free fatty acids** (oleic, stearic, lauric, palmitic) in esterification; equilibrium limited by water.
- **Vinyl esters** (vinyl laurate/palmitate) in transesterification: effectively irreversible due to vinyl alcohol → acetaldehyde, often improving yields and simplifying water management. (Ferrer 2005)

### Selectivity trends (not exhaustive)
- **Sucrose**:
  - **TLL**: selectively forms **6-O-acylsucrose (monoester)** under 2-methyl-2-butanol/DMSO mixtures.  
  - **CALB**: particularly useful for **6,6′-diacylsucrose**. (Ferrer 2005)
- **Glucose**: lipases often give **6-O-acylglucose** (primary OH). (Ferrer 2005)
- **Solvent-free suspension systems** can reach high ester content but product distribution depends on lipase and a_w; switching from RML to CALB decreased monoester fraction (<70%) while increasing conversion. (Ye 2016)

### Known limitations
- **Sucrose is hardest** (very low solubility; bulky).
- **Aqueous environments** strongly disfavor esterification unless using activated donors or strong water removal/phase engineering.

---

## 5) Engineering Landscape (mutations, strategies, and effects)

### RML (most engineering detail in provided corpus)
**Directed evolution including propeptide**
- Full-length RML (with propeptide) evolved in *E. coli*; best mutant after 4 rounds had **k_cat increased from ~10.6 to ~71.4 min⁻¹** (hydrolysis assay), with mutations in both **propeptide (L57V, S65A, V67A)** and **mature region (I111T, S168P)**. (Wang et al., 2012, *Appl Microbiol Biotechnol*, DOI: 10.1007/s00253-012-4049-5)

**Propeptide structural/functional insight**
- Propeptide forms complexes with mature enzyme and **inhibits activity**; structures suggest propeptide buries active site region—important for secretion biology and a potential handle for tuning folding vs activity. (Moroz et al., 2019, *ACS Omega*, DOI: 10.1021/acsomega.9b00612)

**Pocket hydrophobicity engineering (structured lipids context)**
- Mutations in/near binding pocket increased esterification activity; e.g. **Asp256Ile/His257Leu** gave **~2.37× esterification activity** vs WT in their assay and improved oleic incorporation in structured lipid synthesis. (Zhang et al., 2013, *PLOS ONE*, DOI: 10.1371/journal.pone.0067892)

**Thermostability/activity via cavity redesign (computational CE)**
- “Inside-out cavity engineering” produced multi-point mutants with large gains; best triple mutant **T21V/S27A/T198L**: **T_m +11 °C**, **t₁/₂ at 65 °C +28.7×**, and **specific activity +9.9×** (reported up to 5828 U mg⁻¹ in their system). (Zhang et al., 2023, *Appl Environ Microbiol*, DOI: 10.1128/aem.02172-22)

**Glycosylation-site engineering (expression/stability/methanol tolerance; biodiesel context)**
- Saturation at N-linked glycosylation sites in propeptide altered activity/stability; some mutants improved methanol tolerance and biodiesel yields (context-specific; not directly sugar esters). (Tian et al., 2021, *Fuel*, DOI: 10.1016/j.fuel.2021.121514)

### CALB / TLL / CALA (engineering mostly formulation/immobilization in provided hits)
- **CALB immobilization on octyl-agarose**: optimized immobilization (citrate buffer pH 4, 300 mM) gave high enantioselectivity (E > 200) and stability (retained performance after 7 days at 65 °C). (Siόdmiak et al., 2025, *Int J Mol Sci*, DOI: 10.3390/ijms26146961)
- **CALA immobilization in MOFs**: in situ encapsulation gave high loading and improved operational stability/reuse. (2023 paper; not sugar-ester-specific)

### ML-guided design
- Not prominent in the provided corpus for sugar esters specifically; recent reviews emphasize computer-aided approaches (FoldX/Rosetta/MD/tunnel tools) as increasingly standard. (Cheng & Nian 2023; Chong 2024)

---

## 6) Practical Constraints (process + formulation)

- **Water activity control is the dominant constraint** for esterification; too high → hydrolysis and low equilibrium conversion; too low → enzyme dehydration/inactivation. (Gumel 2011; Stergiou 2013; Ye 2016)
- **Aqueous environment constraint**: if you must operate with significant water, strongly consider:
  - **vinyl esters** (drives transesterification forward),
  - **biphasic systems** with sugar in aqueous phase and acyl donor in organic phase + interfacial biocatalyst,
  - **in situ water scavengers** compatible with your formulation.
- **Thermostability**: higher T improves sugar solubility and mass transfer; RML/TLL are often used at elevated T (40–65 °C); immobilization and engineered variants can extend operating windows. (Ye 2010; Zhang 2023 AEM)
- **Immobilized enzyme release**: hydrophobic adsorption supports can desorb in detergents or high hydrophobic cosolvent loads. (Siόdmiak 2025)
- **Expression hosts**:
  - RML commonly expressed in **Pichia pastoris** (secretion, glycosylation) and engineered for higher expression and solvent tolerance. (Huang 2014)
  - CALB is widely available as **Novozym 435** (acrylic resin immobilized).

---

## 7) Comparative Analysis (RML vs CALB vs TLL vs CALA)

**RML vs TLL (both fungal, lid-containing, interfacial activation)**
- Similar fold and lid-mediated gating; both good for lipid transformations.
- For sugar esters, literature emphasis is more on **TLL vs CALB** regioselectivity (below), but RML is strong in **solvent-free suspension** workflows. (Ye 2010; Ye 2016)

**TLL vs CALB (most actionable for sucrose esters)**
- **TLL**: tends toward **monoacylation of sucrose (6-O-acylsucrose)** in tert-alcohol/DMSO mixtures; good when monoester is desired (surfactant HLB tuning). (Ferrer 2005)
- **CALB**: more prone to **diacylation (6,6′-diesters)** under similar conditions; also often robust in organic media and immobilized formats. (Ferrer 2005; Ye 2016)

**CALA**
- Known for handling **bulky/branched substrates** (general property); less directly documented here for sucrose/glucose esterification, but could be explored for sterically challenging sugar derivatives or secondary-OH acylation.

---

## 8) Engineering Opportunities (actionable hypotheses + assay suggestions)

### A. If the target is **sucrose oleate monoester** (cosmetics/surfactants)
- **Choose TLL as starting scaffold** (regioselective 6-O-acylsucrose) and engineer for:
  - **thermostability** (to push sugar solubility),
  - **reduced diacylation** (tighten second-acylation access).
- **Directional hypothesis**: narrowing/reshaping the pocket near the sugar-binding region and/or tuning lid-open dwell time can suppress second acylation.

### B. If the target is **high conversion in constrained (more aqueous) systems**
- Switch chemistry: **vinyl oleate (or other activated acyl donors)** to reduce equilibrium penalty.
- Engineer for **acyltransferase bias** (favor alcoholysis over hydrolysis) by:
  - reducing water access to acyl-enzyme (tunnel engineering),
  - increasing sugar OH positioning (introduce polar anchors near alcohol-binding site).

### C. RML as an engineering chassis (because of rich mutational literature)
- Combine **stability-first** mutations (cavity redesign hotspots like T21/S27/T198 region in Zhang 2023 AEM) with **pocket/tunnel mutations** that improve sugar approach.
- Consider **lid/tunnel engineering** (per recent tunnel-engineering frameworks) to improve transport of bulky sugars and expel water. (Chong 2024)

### D. Propeptide engineering (RML)
- Use propeptide variants to improve **expression/folding** in heterologous hosts and potentially tune active-site preorganization.
- But note: propeptide can be **inhibitory** when bound; ensure proper processing/cleavage in your expression system. (Moroz 2019; Wang 2012)

### E. Assay design suggestions (to de-risk false positives)
- Screen directly on **synthetic direction** (esterification/transesterification), not hydrolysis-only:
  - pH-indicator colony screens for esterification exist (caprylic acid + ethanol systems) and can be adapted as a first pass, but confirm with HPLC/LC-MS for sugar esters. (Zhang 2012 Enz Microb Tech)
- Quantify:
  - **conversion**, **mono/diester ratio**, and **regioisomer distribution** (HPLC/ELSD; NMR for definitive assignment).
- Include **a_w series** and **sugar particle size/solubility controls** to separate enzyme effects from mass transfer.

---

## 9) References (reviews and primary; with DOI/PMID where available)

**Sugar ester synthesis / selectivity**
- Ferrer, M.; Soliveri, J.; Plou, F. J.; et al. (2005). *Enzyme and Microbial Technology* 36, 391–398. “Synthesis of sugar esters in solvent mixtures by lipases from Thermomyces lanuginosus and Candida antarctica B…” DOI: **10.1016/j.enzmictec.2004.02.009**  
- Lee, H.-K.; Do, J. S.; Kim, S. J.; et al. (2004). “Enzymatic Sugar Ester Production” (local PDF; journal details not fully captured in excerpt).  
- Ye, R.; Pyo, S.-H.; Hayes, D. G. (2010). *J Am Oil Chem Soc* 87, 281–293. “Lipase-Catalyzed Synthesis of Saccharide–Fatty Acid Esters Using Suspensions…” DOI: **10.1007/s11746-009-1504-2**  
- Ye, R.; Hayes, D. G.; et al. (2016). *Catalysts* 6, 78. “Solvent-Free Lipase-Catalyzed Synthesis of Technical-Grade Sugar Esters…” DOI: **10.3390/catal6060078**

**Mechanism / interfacial enzymology / lid**
- Aloulou, A.; Rodriguez, J. A.; Fernandez, S.; et al. (2006). *Biochim Biophys Acta* 1761, 995–1013. “Exploring the specific features of interfacial enzymology based on lipase studies.” DOI: **10.1016/j.bbalip.2006.06.009**  
- Khan, F. I.; Lan, D.; et al. (2017). *Front Bioeng Biotechnol* 5:16. “The Lid Domain in Lipases…” DOI: **10.3389/fbioe.2017.00016**

**Process/solvent/water activity (review)**
- Gumel, A. M.; Annuar, M. S. M.; et al. (2011). *Process Biochemistry* 46, 2079–2090. “Lipase mediated synthesis of sugar fatty acid esters.” DOI: **10.1016/j.procbio.2011.07.021**  
- Stergiou, P.-Y.; Foukis, A.; et al. (2013). *Biotechnology Advances* 31, 1846–1859. “Advances in lipase-catalyzed esterification reactions.” DOI: **10.1016/j.biotechadv.2013.08.006**

**Ionic liquids / supersaturated sugar**
- Shin, D. W.; Mai, N. L.; et al. (2019). *Enzyme and Microbial Technology* 126, 18–23. “Enhanced lipase-catalyzed synthesis… using supersaturated sugar solution in ionic liquids.” DOI: **10.1016/j.enzmictec.2019.03.004**  
- Zhao, H. (2016). *J Chem Technol Biotechnol* 91. “Protein Stabilization and Enzyme Activation in Ionic Liquids: Specific Ion Effects.” DOI: **10.1002/jctb.4837**

**RML engineering (primary)**
- Wang, J.; Wang, D.; et al. (2012). *Appl Microbiol Biotechnol* 96, 443–450. “Enhanced activity of Rhizomucor miehei lipase by directed evolution with simultaneous evolution of the propeptide.” DOI: **10.1007/s00253-012-4049-5**  
- Moroz, O. V.; Blagova, E.; et al. (2019). *ACS Omega* 4, 9964–9975. “Novel Inhibitory Function of the Rhizomucor miehei Lipase Propeptide…” DOI: **10.1021/acsomega.9b00612**  
- Zhang, J.-H.; Jiang, Y.-Y.; et al. (2013). *PLOS ONE* 8:e67892. “Structure-Guided Modification of Rhizomucor miehei Lipase…” DOI: **10.1371/journal.pone.0067892**  
- Zhang, Z.; Long, M.; et al. (2023). *Appl Environ Microbiol* 89:e02172-22. “Inside Out Computational Redesign of Cavities…” DOI: **10.1128/aem.02172-22**  
- Huang, J.; Xia, J.; et al. (2014). *Biotechnology for Biofuels* 7:111. “Improved production of a recombinant Rhizomucor miehei lipase expressed in Pichia pastoris…” DOI: **10.1186/1754-6834-7-111**

**CALB immobilization (formulation)**
- Siόdmiak, J.; Dulęba, J.; et al. (2025). *Int J Mol Sci* 26, 6961. “CALB Immobilized on Octyl-Agarose…” DOI: **10.3390/ijms26146961** (EuropePMC ID: 40725207)

---

If you tell me your **intended reaction medium** (e.g., biphasic water/solvent, solvent-free, ionic liquid, or aqueous with activated acyl donor) and whether you want **monoester vs diester**, I can propose a short list of **specific residue regions to target** in RML/TLL/CALB (lid hinges, tunnel bottlenecks, polar anchoring sites) and a **minimal screening panel** (a_w × temperature × sugar particle size) tailored to your constraints.