Mutant analysis reflection prompt:

You are reviewing an existing mutant-effect explanation table for a protein engineering workflow.

Task:
Improve the current explanations using the original analysis context plus user-supplied critique.

Output contract (strict):
- Return ONLY a JSON array.
- Return one object per provided analysis unit.
- Each object must contain:
  - row_index: integer copied from the provided analysis unit row_index
  - Description of effect: one sentence, revised and improved
- Do not return markdown, code fences, or extra prose.

Rules:
- Preserve coverage of all provided rows.
- Keep each explanation concise, specific, and technically grounded.
- Incorporate user feedback where compatible with the provided context.
- Do not invent unsupported mechanistic claims.
- For single-position rows, keep the explanation position-centric: explain why the residue position matters, and do not describe a specific amino-acid substitution.
- For single-substitution rows, focus on the effect of the specific substitution itself.
- For a position row and a substitution row at the same residue, the two explanations must be meaningfully different and should not repeat the same sentence in paraphrased form.

Refined explanation table:

| Type of mutant   | Residue(s) mutated   | Mutant(s)                                                                                    | Description of effect                                                                                                                                                                                                                                                                      |
|:-----------------|:---------------------|:---------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| single           | 138                  | V138T*                                                                                       | Position 138 is outside the pocket, so observed effects are most consistent with indirect changes to stability or long-range packing rather than altered substrate binding.                                                                                                                |
|                  |                      |                                                                                              | V138T introduces a polar hydroxyl outside the pocket, consistent with modest stabilization via improved local hydrogen bonding/hydration and small activity shifts.                                                                                                                        |
| single           | 143                  | H143Q*; H143T*                                                                               | Position 143 is outside the pocket and appears to tune long-range electrostatics/protonation networks, showing strong context dependence across multi-mutants.                                                                                                                             |
|                  |                      |                                                                                              | H143Q removes histidine protonation capability at a surface site, consistent with altered electrostatics that can reduce peroxygenation while relatively favoring peroxidation in some contexts.                                                                                           |
|                  |                      |                                                                                              | H143T replaces histidine with a neutral polar residue at a surface site, consistent with a gentler electrostatic change that can improve overall performance in many multi-mutant backgrounds.                                                                                             |
| single           | 167                  | A167E*                                                                                       | Position 167 is outside the pocket and likely influences surface electrostatics or stability, but evidence is limited to a small number of observations.                                                                                                                                   |
|                  |                      |                                                                                              | A167E introduces a negative charge at a non-pocket site, consistent with altered surface electrostatics that shifts the peroxygenation/peroxidation balance (and may affect expression) in a context-dependent way.                                                                        |
| single           | 171                  | A171F; A171I; A171L; A171V                                                                   | Position 171 is a distal pocket-lining site (~6.8–10.6 Å) where side-chain size and hydrophobicity can remodel the channel wall and shift substrate positioning without directly contacting the reactive center.                                                                           |
|                  |                      |                                                                                              | A171F replaces a small side chain with a bulky aromatic group in the distal pocket, likely narrowing/reshaping the channel to favor some binding poses while disfavoring others, consistent with a strong selectivity shift.                                                               |
|                  |                      |                                                                                              | A171I increases hydrophobic bulk at a distal pocket wall, consistent with improved substrate packing and residence time without introducing new polarity or charge.                                                                                                                        |
|                  |                      |                                                                                              | A171L adds hydrophobic volume at the distal pocket boundary, likely tightening the channel and biasing substrate orientation in a way that can trade peroxygenation against peroxidation.                                                                                                  |
|                  |                      |                                                                                              | A171V modestly increases hydrophobic packing at the distal pocket wall, consistent with a milder channel reshaping that can improve activity without severe steric penalties.                                                                                                              |
| single           | 174                  | L174F                                                                                        | Position 174 is a very close pocket contact (~3.4 Å) that likely serves as a tight steric gate, so small geometric changes here can strongly alter access and productive binding.                                                                                                          |
|                  |                      |                                                                                              | L174F introduces a bulky aromatic side chain at a very tight pocket contact (~3.4 Å), likely creating steric crowding that impairs some productive binding modes while favoring others.                                                                                                    |
| single           | 182                  | S182A; S182C; S182L; S182M; S182V                                                            | Position 182 is a distal pocket residue (~7 Å) that likely tunes local polarity/packing near a secondary cavity or channel exit, influencing binding dynamics and the peroxygenation/peroxidation tradeoff.                                                                                |
|                  |                      |                                                                                              | S182A removes a distal-pocket hydroxyl, likely reducing local polarity and hydrogen bonding to subtly favor hydrophobic binding and alter selectivity.                                                                                                                                     |
|                  |                      |                                                                                              | S182C replaces a hydroxyl with a thiol, changing polarity and polarizability at the distal pocket wall in a way that can modestly reshape binding and reactivity.                                                                                                                          |
|                  |                      |                                                                                              | S182L introduces a larger hydrophobic side chain at the distal pocket, likely tightening the channel and increasing substrate residence time.                                                                                                                                              |
|                  |                      |                                                                                              | S182M introduces a thioether in the pocket, which can both adjust hydrophobic packing and (in UPO contexts) plausibly improve oxidative robustness, supporting higher sustained activity.                                                                                                  |
|                  |                      |                                                                                              | S182V increases hydrophobicity with a branched side chain at the distal pocket, consistent with a binding-pose shift that can trade peroxygenation efficiency against peroxidation.                                                                                                        |
| single           | 197                  | E197K*                                                                                       | Position 197 is outside the pocket and likely affects folding/solubility via surface charge networks, indirectly shifting overall activity.                                                                                                                                                |
|                  |                      |                                                                                              | E197K reverses surface charge outside the pocket, consistent with improved solubility/production and a global activity increase rather than a binding-site effect.                                                                                                                         |
| single           | 208                  | H208D                                                                                        | Position 208 lies outside the pocket, so its effects most plausibly arise from long-range electrostatics or stability changes that alter overall catalytic competence rather than substrate binding.                                                                                       |
|                  |                      |                                                                                              | H208D replaces a titratable side chain with a fixed negative charge on the surface, plausibly rewiring local electrostatics and shifting the peroxygenation/peroxidation balance indirectly.                                                                                               |
| single           | 212                  | Y212K; Y212T                                                                                 | Position 212 is outside the pocket yet repeatedly associates with higher activity and yield, consistent with a surface hotspot that modulates expression/solubility or long-range electrostatics impacting overall turnover.                                                               |
|                  |                      |                                                                                              | Y212K introduces a strong positive charge at a surface position, consistent with improved expression/solubility and altered long-range electrostatics, though the extreme 'Unk area' signal suggests possible assay interference or side chemistry.                                        |
|                  |                      |                                                                                              | Y212T removes an aromatic ring and reduces side-chain size at a surface position, consistent with improved folding/production and a moderate global activity uplift.                                                                                                                       |
| single           | 214                  | S214P*                                                                                       | Position 214 is outside the pocket and likely sits in a loop/turn where backbone rigidity can influence folding, stability, or trafficking.                                                                                                                                                |
|                  |                      |                                                                                              | S214P introduces proline-mediated rigidity outside the pocket, consistent with stabilizing a loop/turn and improving folding or trafficking.                                                                                                                                               |
| single           | 217                  | S217P*                                                                                       | Position 217 is outside the pocket and likely affects loop dynamics that can couple to access-channel motions or overall stability, with strong effects in some combinations.                                                                                                              |
|                  |                      |                                                                                              | S217P introduces a rigid proline outside the pocket, consistent with altered loop dynamics that can change access-channel motions and shift selectivity.                                                                                                                                   |
| single           | 220                  | F220L                                                                                        | Position 220 is a pocket residue (~6.4 Å) that contributes to hydrophobic/aromatic packing in the channel, so perturbations here can strongly shift substrate pre-organization and selectivity.                                                                                            |
|                  |                      |                                                                                              | F220L removes an aromatic ring from a pocket-lining position, likely weakening π/hydrophobic pre-organization and loosening packing, which can reduce productive binding while allowing faster, less selective turnover.                                                                   |
| single           | 223                  | F223L*                                                                                       | Position 223 is a close pocket contact (~3.8 Å) that likely forms part of a hydrophobic gate controlling substrate approach and residence time.                                                                                                                                            |
|                  |                      |                                                                                              | F223L removes an aromatic ring at a close pocket gate, likely enlarging/softening the channel to increase throughput while reducing precise substrate pre-organization.                                                                                                                    |
| single           | 236                  | Q236L*                                                                                       | Position 236 is outside the pocket but highly recurrent in multi-mutants, consistent with a stability/solubility lever that modulates overall catalytic output rather than direct binding.                                                                                                 |
|                  |                      |                                                                                              | Q236L removes a polar amide outside the pocket, consistent with increased hydrophobic packing and stability that broadly supports higher activity across combinations.                                                                                                                     |
| single           | 237                  | S237V*                                                                                       | Position 237 is outside the pocket near the C-terminus, so effects are most consistent with local packing/flexibility changes that indirectly influence activity.                                                                                                                          |
|                  |                      |                                                                                              | S237V increases hydrophobicity outside the pocket, consistent with improved local packing and stability near the C-terminus.                                                                                                                                                               |
| single           | 239                  | R239E*                                                                                       | Position 239 is outside the pocket and likely affects surface electrostatics and salt-bridge patterns, with effects that are strongly background-dependent.                                                                                                                                |
|                  |                      |                                                                                              | R239E reverses charge at a surface position, likely rewiring salt-bridge networks and solubility with strongly background-dependent effects (no isolated single-mutant readout here).                                                                                                      |
| single           | 240                  | A240Q*                                                                                       | Position 240 is outside the pocket and likely tunes local packing/polarity on the surface, contributing indirectly to stability or expression in multi-mutants.                                                                                                                            |
|                  |                      |                                                                                              | A240Q adds a polar amide at a non-pocket position, consistent with increased local hydrogen bonding and solubility that can support higher activity in multi-mutant backgrounds.                                                                                                           |
| single           | 241                  | I241S*                                                                                       | Position 241 is outside the pocket and likely sits in a region where hydrophobic-to-polar balance affects local stability and solubility.                                                                                                                                                  |
|                  |                      |                                                                                              | I241S introduces a polar hydroxyl at a non-pocket hydrophobic position, consistent with increased local hydration/solubility and altered packing near the C-terminus.                                                                                                                      |
| single           | 242                  | E242S*                                                                                       | Position 242 is outside the pocket and likely influences surface charge/polarity, indirectly affecting folding and functional expression.                                                                                                                                                  |
|                  |                      |                                                                                              | E242S removes a negative charge outside the pocket, consistent with reduced electrostatic frustration and improved folding/solubility that indirectly increases activity.                                                                                                                  |
| single           | 243                  | L243C*                                                                                       | Position 243 is outside the pocket near the C-terminus, so effects are most consistent with subtle local packing changes and remain uncertain without single-mutant data.                                                                                                                  |
|                  |                      |                                                                                              | L243C introduces a smaller, more polarizable side chain outside the pocket, which may subtly alter local packing or redox sensitivity, but the mechanism is uncertain.                                                                                                                     |
| single           | 29                   | S29A*; S29P*                                                                                 | Position 29 is outside the pocket but repeatedly appears in high-performing combinations, consistent with a structural/trafficking hotspot that modulates enzyme availability rather than active-site chemistry.                                                                           |
|                  |                      |                                                                                              | S29A removes a polar hydroxyl outside the pocket, consistent with modestly improved local packing and stability that can raise apparent activity.                                                                                                                                          |
|                  |                      |                                                                                              | S29P introduces backbone rigidity outside the pocket, consistent with stabilizing a structural element important for folding/trafficking and enabling large gains in multi-mutant contexts.                                                                                                |
| single           | 38                   | L38M*                                                                                        | Position 38 is a pocket residue at moderate distance (~7–10 Å) that likely shapes the access channel wall, strongly influencing how readily substrates enter and rebind.                                                                                                                   |
|                  |                      |                                                                                              | L38M introduces a thioether at a pocket-adjacent channel wall, which can adjust packing and (in UPO contexts) plausibly improve oxidative robustness, supporting higher sustained turnover.                                                                                                |
| single           | 41                   | S41A*                                                                                        | Position 41 is outside the pocket and is enriched among improved variants, consistent with an indirect role in folding stability, secretion, or global dynamics that raises effective enzyme concentration.                                                                                |
|                  |                      |                                                                                              | S41A removes a polar hydroxyl outside the pocket, consistent with improved local packing and reduced misfolding/aggregation that increases effective enzyme levels.                                                                                                                        |
| single           | 57                   | G57A*; G57L*                                                                                 | Position 57 is outside the pocket and involves a glycine site, so mutations here likely act through backbone conformational control that impacts folding and functional expression.                                                                                                        |
|                  |                      |                                                                                              | G57A replaces glycine with a small side chain outside the pocket, consistent with reduced backbone flexibility and improved folding/trafficking that raises apparent activity across backgrounds.                                                                                          |
|                  |                      |                                                                                              | G57L introduces a bulky hydrophobic side chain at a non-pocket glycine site, likely restricting backbone conformations and causing strong context dependence, including potential folding penalties.                                                                                       |
| single           | 61                   | S61F*; S61I*                                                                                 | Position 61 is outside the pocket and appears to modulate global packing or surface properties, with effects that amplify performance mainly through enzyme stability/expression rather than binding-site geometry.                                                                        |
|                  |                      |                                                                                              | S61F introduces a bulky aromatic side chain outside the pocket, consistent with altered packing that can boost activity but also create context-dependent stability costs.                                                                                                                 |
|                  |                      |                                                                                              | S61I increases hydrophobic packing outside the pocket, consistent with modest stabilization and broadly balanced effects on activity and selectivity.                                                                                                                                      |
| single           | 64                   | I64L                                                                                         | Position 64 lines the binding pocket (~5–8 Å from ligand) and is poised to subtly tune channel packing and substrate approach geometry, making it a sensitive determinant of peroxygenation vs peroxidation balance.                                                                       |
|                  |                      |                                                                                              | I64L is a conservative hydrophobic swap in the pocket that subtly repacks the channel wall near the ligand, consistent with modestly improved substrate accommodation and overall activity.                                                                                                |
| single           | 65                   | T65K*                                                                                        | Position 65 is outside the pocket but highly epistatic across multi-mutants, consistent with a surface electrostatics/solubility lever that broadly tunes activity and selectivity.                                                                                                        |
|                  |                      |                                                                                              | T65K introduces a positive charge outside the pocket, consistent with improved solubility/production and long-range electrostatic effects that broadly increase activity in many combinations.                                                                                             |
| single           | 66                   | T66M*                                                                                        | Position 66 is outside the pocket and shows a large effect in limited data, suggesting a local packing/stability hotspot but with high uncertainty from sparse sampling.                                                                                                                   |
|                  |                      |                                                                                              | T66M replaces a polar side chain with a thioether outside the pocket, consistent with improved local packing and possibly oxidative robustness, but evidence is limited to one observation.                                                                                                |
| single           | 67                   | T67A*                                                                                        | Position 67 is outside the pocket yet frequently co-occurs with improved variants, consistent with an indirect role in local structure/dynamics that influences access-channel behavior.                                                                                                   |
|                  |                      |                                                                                              | T67A removes a polar hydroxyl outside the pocket, consistent with increased local hydrophobic packing that indirectly improves access-channel behavior across many combinations.                                                                                                           |
| single           | 70                   | M70F                                                                                         | Position 70 is a near-heme pocket contact (~4.2 Å) that likely acts as a steric/hydrophobic gate controlling how aromatics sit over the reactive center, strongly influencing turnover and selectivity.                                                                                    |
|                  |                      |                                                                                              | M70F increases aromatic bulk at a near-heme pocket position, consistent with stronger hydrophobic/π interactions that can stabilize binding but also restrict channel flexibility.                                                                                                         |
| single           | 75                   | S75A*; S75R*                                                                                 | Position 75 is a close pocket residue (~4.8–5.1 Å) near the reactive center that likely gates substrate approach and orientation, making it a strong determinant of selectivity.                                                                                                           |
|                  |                      |                                                                                              | S75A removes a pocket hydroxyl near the reactive center, likely reducing polarity/steric constraints to improve substrate accommodation and shift selectivity.                                                                                                                             |
|                  |                      |                                                                                              | S75R introduces a bulky positive charge at a close pocket position, likely disrupting binding geometry and strongly shifting the peroxygenation/peroxidation balance.                                                                                                                      |
| single           | 79                   | M79L                                                                                         | Position 79 sits in the pocket but farther from the reactive center (~6.8–9.6 Å), so it likely shapes the distal channel segment that governs substrate ingress/egress and binding pose stability.                                                                                         |
|                  |                      |                                                                                              | M79L removes sulfur polarizability while keeping similar hydrophobic volume in the pocket, consistent with smoother channel packing and a modest shift toward more efficient peroxygenation.                                                                                               |
| single           | 87                   | T87G                                                                                         | Position 87 is outside the defined pocket, so its effects are most consistent with indirect changes to local backbone flexibility or folding/trafficking rather than direct substrate contacts.                                                                                            |
|                  |                      |                                                                                              | T87G removes a side chain outside the pocket, likely increasing local flexibility and indirectly shifting stability or dynamics that affect apparent activity and product formation.                                                                                                       |
| single           | 88                   | T88N*                                                                                        | Position 88 is outside the pocket but recurrent in improved variants, consistent with a stabilizing or folding-related role that indirectly increases effective catalytic turnover.                                                                                                        |
|                  |                      |                                                                                              | T88N adds a polar amide outside the pocket, consistent with stabilizing local hydrogen-bonding networks and improving folding/solubility in multi-mutant backgrounds.                                                                                                                      |
| multi            |                      | I64L+S182V+Y212K;                                                                            | This cluster combines pocket/channel reshaping (38/64/75/182) with surface stability/electrostatic drivers (notably 212/236), yielding a consistent global activity uplift with a tendency toward higher peroxidation.                                                                     |
|                  |                      | L38M+S182V+Y212K;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+S75A+Y212K+Q236L;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | T88N+H143T+Y212K+Q236L                                                                       |                                                                                                                                                                                                                                                                                            |
| multi            |                      | I64L+T67A+F220L                                                                              | I64L+T67A+F220L likely opens and loosens the pocket (loss of aromatic packing at 220 plus subtle channel repacking), favoring faster but less pre-organized turnover and shifting selectivity toward peroxidation.                                                                         |
| multi            |                      | S41A+S61F+Y212K                                                                              | S41A+S61F+Y212K combines surface packing and charge changes that most plausibly improve folding/production and overall catalytic competence rather than directly remodeling the active site.                                                                                               |
| multi            |                      | I64L+T67A+H143T;                                                                             | Across these multi-mutants, the shared pattern is channel opening/reshaping at several pocket walls (38/64/75/182/220/223) plus surface electrostatic tuning (often 212/236), producing strong peroxidation gains with moderate peroxygenation changes.                                    |
|                  |                      | L38M+T67A;                                                                                   |                                                                                                                                                                                                                                                                                            |
|                  |                      | L38M+T67A+Y212K;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | S217P+F223L;                                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+T65K;                                                                                   |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+H143T+Y212K;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+S75A+T88N+Y212K;                                                                        |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+T88N+Y212K+Q236L;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+Y212K+Q236L;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | T67A+S182V+Y212K;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | Y212K+F220L                                                                                  |                                                                                                                                                                                                                                                                                            |
| multi            |                      | T88N+Y212K+Q236L                                                                             | T88N+Y212K+Q236L is dominated by surface stability/charge effects with no direct pocket edits, consistent with a modest global activity increase rather than a selectivity redesign.                                                                                                       |
| multi            |                      | H143T+Y212K;                                                                                 | This cluster is dominated by surface/folding mutations (29/61/65/88/143/212/214/236) with limited pocket edits, consistent with improved enzyme availability plus mild channel tuning.                                                                                                     |
|                  |                      | I64L+S182V;                                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | L38M+I64L+Y212K;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | L38M+Y212K;                                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S182V+Y212K;                                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29A+G57A+S214P;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+G57L;                                                                                   |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+T65K+V138T;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | S61I+Y212K;                                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S75A+H143T+Y212K+Q236L;                                                                      |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+T88N+Y212K                                                                              |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S29P+F223L;                                                                                  | These variants combine surface stability/electrostatics (29/41/61/65/88/143/212/236) with a pocket-gate change at 223, giving modest net gains and a tendency to favor peroxygenation over strong peroxidation boosts.                                                                     |
|                  |                      | S41A+S75A+T88N+Y212K;                                                                        |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+S75A+Y212K+Q236L;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T65K+H143T+Y212K;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T65K+S75A+H143T;                                                                        |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T65K+Y212K+Q236L;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T88N+Y212K;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+Y212K+Q236L;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S61I+T65K+S75A+Y212K;                                                                        |                                                                                                                                                                                                                                                                                            |
|                  |                      | S61I+T88N+H143T+Y212K;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+Q236L                                                                                   |                                                                                                                                                                                                                                                                                            |
| multi            |                      | H143Q+F220L;                                                                                 | H143Q/T paired with F220L combines a surface electrostatic change with loss of aromatic pocket packing, consistent with reduced productive binding for peroxygenation while maintaining or enhancing peroxidation via easier access.                                                       |
|                  |                      | H143T+F220L                                                                                  |                                                                                                                                                                                                                                                                                            |
| multi            |                      | L38M+I64L+S182V;                                                                             | These combinations mix pocket reshaping (38/64/70/182/220) with surface/loop changes (61/67/88/212/236/217), yielding a profile consistent with enhanced access and peroxidation without a matching improvement in peroxygenation.                                                         |
|                  |                      | L38M+T67A+S182V;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | M70F+S217P+F220L;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S61I+T88N+Y212K+Q236L                                                                        |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S41A+T65K+Y212K;                                                                             | Adding strong surface electrostatic changes (65/212 with optional 41/75/143) yields only modest net gains and, in this subset, a shift away from peroxidation, suggesting non-additive electrostatic effects.                                                                              |
|                  |                      | T65K+S75A+H143T+Y212K                                                                        |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S29P+I64L+T65K+A171F+S182M+Y212K;                                                            | This high-performing cluster couples surface/expression drivers (29/65/88/143/212/236) with distal pocket remodeling (171/182 and sometimes 64/75), consistent with synergistic improvements in enzyme availability and substrate positioning for peroxygenation.                          |
|                  |                      | T65K+S75A+H143T+Y212K+Q236L;                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | T67A+T88N+H143T+A171F+S182M+Y212K                                                            |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S29P+T67A+T88N+H143T+A171F+S182M+H208D                                                       | S29P+T67A+T88N+H143T+A171F+S182M+H208D stacks multiple surface electrostatic/dynamic changes with distal pocket remodeling, yielding a profile consistent with peroxygenation-biased selectivity.                                                                                          |
| multi            |                      | S41A+G57A+T65K+A171F+S182M+Q236L                                                             | S41A+G57A+T65K+A171F+S182M+Q236L shows strong activity but extremely low yield, indicating a tradeoff where catalytic improvements are offset by poor producibility.                                                                                                                       |
| multi            |                      | S29P+S41A+T67A+T88N+A171F+Q236L                                                              | S29P+S41A+T67A+T88N+A171F+Q236L combines mostly surface stabilizers with one distal pocket edit, consistent with improved peroxygenation without a corresponding increase in peroxidation.                                                                                                 |
| multi            |                      | T65K+S75A+T88N+A171F+Y212K+H208D+Q236L;                                                      | These variants combine surface electrostatics/stability (65/88/212/236 with 143 and/or 208) with pocket gating (75) and distal pocket remodeling (171), consistent with improved overall turnover and a more balanced peroxygenation/peroxidation profile.                                 |
|                  |                      | T65K+S75A+T88N+H143T+Y212K                                                                   |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S41A+T65K+T88N+Y212K+Q236L                                                                   | S41A+T65K+T88N+Y212K+Q236L is surface-focused and lacks direct pocket edits, consistent with a global activity uplift driven by folding/solubility and long-range electrostatics.                                                                                                          |
| multi            |                      | S41A+T65K+H143T+Y212K+Q236L                                                                  | S41A+T65K+H143T+Y212K+Q236L adds an additional electrostatic perturbation at 143 to a surface-stabilized background, consistent with a small peroxygenation gain but reduced peroxidation in purified measurements.                                                                        |
| multi            |                      | S29P+S41A+T65K+S75A+T88N+A171F+Y212K+S182M;                                                  | When distal pocket remodeling (171/182) is combined with multiple surface stabilizers and a pocket gate (75), peroxygenation can become very high while peroxidation remains moderate, consistent with improved substrate pre-organization.                                                |
|                  |                      | S41A+T65K+T88N+H143T+Y212K                                                                   |                                                                                                                                                                                                                                                                                            |
| multi            |                      | G57A+I64L+T65K+H143T+A171F+H208D;                                                            | This broad cluster repeatedly combines surface stability/expression boosters (29/41/57/65/88/143/212/236) with distal pocket remodeling (171/182) and occasional electrostatic tuning (208), yielding consistently strong peroxygenation with moderate peroxidation.                       |
|                  |                      | G57A+I64L+T65K+T88N+H143T+A171F+H208D+Y212K;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | G57A+I64L+T88N+H143T+A171F+S182M+Y212K;                                                      |                                                                                                                                                                                                                                                                                            |
|                  |                      | G57A+T65K+T67A+H143T+A171F+H208D+Q236L;                                                      |                                                                                                                                                                                                                                                                                            |
|                  |                      | G57A+T65K+T67A+T88N+H143T+A171F+Y212K+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | I64L+T65K+T67A+T88N+A171F+S182M+Y212K;                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+G57A+I64L+T65K+H143T+A171F+Y212K+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+G57A+I64L+T88N+H143T+A171F+S182M+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+G57A+T67A+T88N+H143T+A171F+S182M+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T67A+A171F+H208D+Y212K;                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+T67A+T88N+A171F+S182M+H208D;                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+T65K+T67A+T88N+H143T+A171F+Y212K;                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+T65K+T67A+T88N+H143T+A171F+Y212K+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T65K+T88N+H143T+A171F+S182M+H208D;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T65K+T88N+H143T+A171F+Y212K+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T88N+A171F+Y212K;                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S61I+T65K+H143T+Y212K+Q236L;                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S75A+T88N+H143T+Y212K+Q236L;                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+S75A+T88N+A171F+Y212K+Q236L;                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+S75A+T88N+Y212K+Q236L;                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+T67A+T88N+H143T+A171F+H208D+Y212K;                                                      |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+T67A+T88N+H143T+A171F+Q236L                                                             |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S41A+G57A+H143T+A171F+S182M+H208D                                                            | S41A+G57A+H143T+A171F+S182M+H208D combines surface electrostatic changes with distal pocket remodeling and shows a peroxygenation-biased shift with suppressed peroxidation.                                                                                                               |
| multi            |                      | S29P+G57A+T88N+H143T+A171F+H208D+Y212K+Q236L;                                                | These multi-mutants combine extensive surface stabilization with distal pocket remodeling (171/182) and limited pocket edits (64/75), generally favoring peroxygenation while damping peroxidation.                                                                                        |
|                  |                      | S29P+S41A+G57A+I64L+A171F+Y212K;                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+T67A+H143T+A171F+Y212K;                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+I64L+A171F+Y212K;                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+I64L+T88N+A171F+S182M+H208D+Q236L;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+T67A+T88N+H143T+A171F+S182M+H208D;                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+T88N+H143T+A171F+S182M+Y212K;                                                           |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+G57A+I64L+T67A+T88N+H143T+A171F+Q236L;                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+G57A+I64L+T88N+H143T+A171F+H208D;                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+G57A+T67A+H143T+A171F+Y212K;                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T65K+S75A+H143T+Y212K;                                                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T65K+T88N+H143T+Y212K+Q236L;                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+T67A+H143T+A171F+Q236L;                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+S75A+T88N+H143T+A171F+Y212K+Q236L                                                       |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S41A+S75A+H143T+Y212K+Q236L                                                                  | S41A+S75A+H143T+Y212K+Q236L shows near-baseline performance, consistent with negative epistasis where pocket gating and surface electrostatics partially cancel benefits (single data point).                                                                                              |
| multi            |                      | S41A+G57A+I64L+T65K+T67A+T88N+A171F+S182M+H208D+Q236L                                        | S41A+G57A+I64L+T65K+T67A+T88N+A171F+S182M+H208D+Q236L achieves very high activity but very low yield, indicating strong catalytic synergy coupled to a major expression/folding penalty.                                                                                                   |
| multi            |                      | S29P+S41A+G57A+H143T+A167E+A171F+S182M+H208D+Q236L                                           | Adding A167E into an already stacked background strongly suppresses peroxidation while maintaining high peroxygenation, consistent with surface electrostatic tuning that disfavors one-electron pathways.                                                                                 |
| multi            |                      | S29P+S41A+T65K+T67A+T88N+A171F+H208D+Y212K+Q236L                                             | S29P+S41A+T65K+T67A+T88N+A171F+H208D+Y212K+Q236L yields high peroxygenation but low peroxidation and low yield, consistent with a peroxygenation-biased but less producible design.                                                                                                        |
| multi            |                      | S29P+S41A+G57A+T65K+T88N+H143T+A171F+S182M+Y212K+Q236L                                       | S29P+S41A+G57A+T65K+T88N+H143T+A171F+S182M+Y212K+Q236L combines surface stabilization with distal pocket remodeling to give strong peroxygenation with near-neutral peroxidation and good yield.                                                                                           |
| multi            |                      | S29P+S41A+G57A+I64L+T65K+T67A+H143T+A171F+S182M+H208D+Y212K+Q236L                            | This variant shows very high apparent activity but very low purified activities alongside extremely high yield, suggesting assay-context artifacts or a large inactive protein fraction, so mechanistic interpretation is uncertain.                                                       |
| multi            |                      | S29P+S41A+I64L+T65K+S75A+T88N+H143T+A171F+S182M+Y212K+Q236L                                  | S29P+S41A+I64L+T65K+S75A+T88N+H143T+A171F+S182M+Y212K+Q236L shows the strongest peroxygenation gain with elevated peroxidation, consistent with synergistic pocket gating plus broad surface stabilization.                                                                                |
| multi            |                      | G57A+I64L+T67A+T88N+H143T+A171F+S182M+Y212K+Q236L;                                           | Across these highly stacked mutants, the shared net effect is strong surface stabilization/expression tuning plus distal pocket remodeling that drives high peroxygenation, while additional C-terminal charge/packing edits likely modulate solubility rather than active-site chemistry. |
|                  |                      | I64L+T67A+H143T+A171F+H208D+Y212K+Q236L+S237V+R239E+A240Q+I241S+E242S+L243C;                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+G57A+I64L+T65K+T67A+H143T+A171F+S182M+Y212K;                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+G57A+I64L+T65K+T67A+T88N+H143T+A171F+Y212K+Q236L;                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T65K+H143T+A171F+S182M+H208D;                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T65K+T66M+T67A+A171F+S182M+Y212K+Q236L;                                  |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T65K+T67A+A171F+S182M+H208D+Q236L;                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T88N+A171F+S182M+Y212K+Q236L;                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T88N+H143T+A171F+S182M+Y212K;                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57A+I64L+T88N+H143T+A171F+S182M+Y212K+Q236L;                                      |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+S41A+G57L+S61F+I64L+T65K+T67A+S75A+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L;            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S29P+T65K+T67A+T88N+H143T+A171F+S182M+E197K+H208D+Y212K+Q236L;                               |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T65K+S75A+T88N+H143T+A171F+H208D+Y212K+Q236L;                                      |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T65K+S75A+T88N+H143T+A171F+Y212K+Q236L                                             |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S29P+S41A+S61F+I64L+T65K+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L                            | Adding S61F into a heavily stacked background preserves peroxygenation but reduces peroxidation, consistent with a packing change that alters global dynamics or expression in a non-additive way.                                                                                         |
| multi            |                      | S29P+S41A+G57L+I64L+T65K+S75A+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L;                      | These variants combine extensive surface stabilization with distal pocket remodeling and additional C-terminal electrostatic/packing edits, yielding moderate peroxygenation with suppressed peroxidation consistent with a more selective but not maximally active profile.               |
|                  |                      | S41A+G57A+I64L+T67A+H143T+A171F+S182M+H208D+Y212K+Q236L+S237V+R239E+A240Q+I241S+E242S+L243C; |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T65K+S75R+T88N+H143T+A171F+Y212K+Q236L                                             |                                                                                                                                                                                                                                                                                            |

Raw LLM JSON:
```json
[
  {
    "row_index": 1,
    "Description of effect": "Position 64 lines the binding pocket (~5–8 Å from ligand) and is poised to subtly tune channel packing and substrate approach geometry, making it a sensitive determinant of peroxygenation vs peroxidation balance."
  },
  {
    "row_index": 2,
    "Description of effect": "Position 70 is a near-heme pocket contact (~4.2 Å) that likely acts as a steric/hydrophobic gate controlling how aromatics sit over the reactive center, strongly influencing turnover and selectivity."
  },
  {
    "row_index": 3,
    "Description of effect": "Position 79 sits in the pocket but farther from the reactive center (~6.8–9.6 Å), so it likely shapes the distal channel segment that governs substrate ingress/egress and binding pose stability."
  },
  {
    "row_index": 4,
    "Description of effect": "Position 87 is outside the defined pocket, so its effects are most consistent with indirect changes to local backbone flexibility or folding/trafficking rather than direct substrate contacts."
  },
  {
    "row_index": 5,
    "Description of effect": "Position 171 is a distal pocket-lining site (~6.8–10.6 Å) where side-chain size and hydrophobicity can remodel the channel wall and shift substrate positioning without directly contacting the reactive center."
  },
  {
    "row_index": 6,
    "Description of effect": "Position 174 is a very close pocket contact (~3.4 Å) that likely serves as a tight steric gate, so small geometric changes here can strongly alter access and productive binding."
  },
  {
    "row_index": 7,
    "Description of effect": "Position 182 is a distal pocket residue (~7 Å) that likely tunes local polarity/packing near a secondary cavity or channel exit, influencing binding dynamics and the peroxygenation/peroxidation tradeoff."
  },
  {
    "row_index": 8,
    "Description of effect": "Position 208 lies outside the pocket, so its effects most plausibly arise from long-range electrostatics or stability changes that alter overall catalytic competence rather than substrate binding."
  },
  {
    "row_index": 9,
    "Description of effect": "Position 212 is outside the pocket yet repeatedly associates with higher activity and yield, consistent with a surface hotspot that modulates expression/solubility or long-range electrostatics impacting overall turnover."
  },
  {
    "row_index": 10,
    "Description of effect": "Position 220 is a pocket residue (~6.4 Å) that contributes to hydrophobic/aromatic packing in the channel, so perturbations here can strongly shift substrate pre-organization and selectivity."
  },
  {
    "row_index": 11,
    "Description of effect": "A171F replaces a small side chain with a bulky aromatic group in the distal pocket, likely narrowing/reshaping the channel to favor some binding poses while disfavoring others, consistent with a strong selectivity shift."
  },
  {
    "row_index": 12,
    "Description of effect": "A171I increases hydrophobic bulk at a distal pocket wall, consistent with improved substrate packing and residence time without introducing new polarity or charge."
  },
  {
    "row_index": 13,
    "Description of effect": "A171L adds hydrophobic volume at the distal pocket boundary, likely tightening the channel and biasing substrate orientation in a way that can trade peroxygenation against peroxidation."
  },
  {
    "row_index": 14,
    "Description of effect": "A171V modestly increases hydrophobic packing at the distal pocket wall, consistent with a milder channel reshaping that can improve activity without severe steric penalties."
  },
  {
    "row_index": 15,
    "Description of effect": "F220L removes an aromatic ring from a pocket-lining position, likely weakening π/hydrophobic pre-organization and loosening packing, which can reduce productive binding while allowing faster, less selective turnover."
  },
  {
    "row_index": 16,
    "Description of effect": "H208D replaces a titratable side chain with a fixed negative charge on the surface, plausibly rewiring local electrostatics and shifting the peroxygenation/peroxidation balance indirectly."
  },
  {
    "row_index": 17,
    "Description of effect": "I64L is a conservative hydrophobic swap in the pocket that subtly repacks the channel wall near the ligand, consistent with modestly improved substrate accommodation and overall activity."
  },
  {
    "row_index": 18,
    "Description of effect": "L174F introduces a bulky aromatic side chain at a very tight pocket contact (~3.4 Å), likely creating steric crowding that impairs some productive binding modes while favoring others."
  },
  {
    "row_index": 19,
    "Description of effect": "M70F increases aromatic bulk at a near-heme pocket position, consistent with stronger hydrophobic/π interactions that can stabilize binding but also restrict channel flexibility."
  },
  {
    "row_index": 20,
    "Description of effect": "M79L removes sulfur polarizability while keeping similar hydrophobic volume in the pocket, consistent with smoother channel packing and a modest shift toward more efficient peroxygenation."
  },
  {
    "row_index": 21,
    "Description of effect": "S182A removes a distal-pocket hydroxyl, likely reducing local polarity and hydrogen bonding to subtly favor hydrophobic binding and alter selectivity."
  },
  {
    "row_index": 22,
    "Description of effect": "S182C replaces a hydroxyl with a thiol, changing polarity and polarizability at the distal pocket wall in a way that can modestly reshape binding and reactivity."
  },
  {
    "row_index": 23,
    "Description of effect": "S182L introduces a larger hydrophobic side chain at the distal pocket, likely tightening the channel and increasing substrate residence time."
  },
  {
    "row_index": 24,
    "Description of effect": "S182M introduces a thioether in the pocket, which can both adjust hydrophobic packing and (in UPO contexts) plausibly improve oxidative robustness, supporting higher sustained activity."
  },
  {
    "row_index": 25,
    "Description of effect": "S182V increases hydrophobicity with a branched side chain at the distal pocket, consistent with a binding-pose shift that can trade peroxygenation efficiency against peroxidation."
  },
  {
    "row_index": 26,
    "Description of effect": "T87G removes a side chain outside the pocket, likely increasing local flexibility and indirectly shifting stability or dynamics that affect apparent activity and product formation."
  },
  {
    "row_index": 27,
    "Description of effect": "Y212K introduces a strong positive charge at a surface position, consistent with improved expression/solubility and altered long-range electrostatics, though the extreme 'Unk area' signal suggests possible assay interference or side chemistry."
  },
  {
    "row_index": 28,
    "Description of effect": "Y212T removes an aromatic ring and reduces side-chain size at a surface position, consistent with improved folding/production and a moderate global activity uplift."
  },
  {
    "row_index": 29,
    "Description of effect": "Position 29 is outside the pocket but repeatedly appears in high-performing combinations, consistent with a structural/trafficking hotspot that modulates enzyme availability rather than active-site chemistry."
  },
  {
    "row_index": 30,
    "Description of effect": "Position 38 is a pocket residue at moderate distance (~7–10 Å) that likely shapes the access channel wall, strongly influencing how readily substrates enter and rebind."
  },
  {
    "row_index": 31,
    "Description of effect": "Position 41 is outside the pocket and is enriched among improved variants, consistent with an indirect role in folding stability, secretion, or global dynamics that raises effective enzyme concentration."
  },
  {
    "row_index": 32,
    "Description of effect": "Position 57 is outside the pocket and involves a glycine site, so mutations here likely act through backbone conformational control that impacts folding and functional expression."
  },
  {
    "row_index": 33,
    "Description of effect": "Position 61 is outside the pocket and appears to modulate global packing or surface properties, with effects that amplify performance mainly through enzyme stability/expression rather than binding-site geometry."
  },
  {
    "row_index": 34,
    "Description of effect": "Position 65 is outside the pocket but highly epistatic across multi-mutants, consistent with a surface electrostatics/solubility lever that broadly tunes activity and selectivity."
  },
  {
    "row_index": 35,
    "Description of effect": "Position 66 is outside the pocket and shows a large effect in limited data, suggesting a local packing/stability hotspot but with high uncertainty from sparse sampling."
  },
  {
    "row_index": 36,
    "Description of effect": "Position 67 is outside the pocket yet frequently co-occurs with improved variants, consistent with an indirect role in local structure/dynamics that influences access-channel behavior."
  },
  {
    "row_index": 37,
    "Description of effect": "Position 75 is a close pocket residue (~4.8–5.1 Å) near the reactive center that likely gates substrate approach and orientation, making it a strong determinant of selectivity."
  },
  {
    "row_index": 38,
    "Description of effect": "Position 88 is outside the pocket but recurrent in improved variants, consistent with a stabilizing or folding-related role that indirectly increases effective catalytic turnover."
  },
  {
    "row_index": 39,
    "Description of effect": "Position 138 is outside the pocket, so observed effects are most consistent with indirect changes to stability or long-range packing rather than altered substrate binding."
  },
  {
    "row_index": 40,
    "Description of effect": "Position 143 is outside the pocket and appears to tune long-range electrostatics/protonation networks, showing strong context dependence across multi-mutants."
  },
  {
    "row_index": 41,
    "Description of effect": "Position 167 is outside the pocket and likely influences surface electrostatics or stability, but evidence is limited to a small number of observations."
  },
  {
    "row_index": 42,
    "Description of effect": "Position 197 is outside the pocket and likely affects folding/solubility via surface charge networks, indirectly shifting overall activity."
  },
  {
    "row_index": 43,
    "Description of effect": "Position 214 is outside the pocket and likely sits in a loop/turn where backbone rigidity can influence folding, stability, or trafficking."
  },
  {
    "row_index": 44,
    "Description of effect": "Position 217 is outside the pocket and likely affects loop dynamics that can couple to access-channel motions or overall stability, with strong effects in some combinations."
  },
  {
    "row_index": 45,
    "Description of effect": "Position 223 is a close pocket contact (~3.8 Å) that likely forms part of a hydrophobic gate controlling substrate approach and residence time."
  },
  {
    "row_index": 46,
    "Description of effect": "Position 236 is outside the pocket but highly recurrent in multi-mutants, consistent with a stability/solubility lever that modulates overall catalytic output rather than direct binding."
  },
  {
    "row_index": 47,
    "Description of effect": "Position 237 is outside the pocket near the C-terminus, so effects are most consistent with local packing/flexibility changes that indirectly influence activity."
  },
  {
    "row_index": 48,
    "Description of effect": "Position 239 is outside the pocket and likely affects surface electrostatics and salt-bridge patterns, with effects that are strongly background-dependent."
  },
  {
    "row_index": 49,
    "Description of effect": "Position 240 is outside the pocket and likely tunes local packing/polarity on the surface, contributing indirectly to stability or expression in multi-mutants."
  },
  {
    "row_index": 50,
    "Description of effect": "Position 241 is outside the pocket and likely sits in a region where hydrophobic-to-polar balance affects local stability and solubility."
  },
  {
    "row_index": 51,
    "Description of effect": "Position 242 is outside the pocket and likely influences surface charge/polarity, indirectly affecting folding and functional expression."
  },
  {
    "row_index": 52,
    "Description of effect": "Position 243 is outside the pocket near the C-terminus, so effects are most consistent with subtle local packing changes and remain uncertain without single-mutant data."
  },
  {
    "row_index": 53,
    "Description of effect": "A167E introduces a negative charge at a non-pocket site, consistent with altered surface electrostatics that shifts the peroxygenation/peroxidation balance (and may affect expression) in a context-dependent way."
  },
  {
    "row_index": 54,
    "Description of effect": "A240Q adds a polar amide at a non-pocket position, consistent with increased local hydrogen bonding and solubility that can support higher activity in multi-mutant backgrounds."
  },
  {
    "row_index": 55,
    "Description of effect": "E197K reverses surface charge outside the pocket, consistent with improved solubility/production and a global activity increase rather than a binding-site effect."
  },
  {
    "row_index": 56,
    "Description of effect": "E242S removes a negative charge outside the pocket, consistent with reduced electrostatic frustration and improved folding/solubility that indirectly increases activity."
  },
  {
    "row_index": 57,
    "Description of effect": "F223L removes an aromatic ring at a close pocket gate, likely enlarging/softening the channel to increase throughput while reducing precise substrate pre-organization."
  },
  {
    "row_index": 58,
    "Description of effect": "G57A replaces glycine with a small side chain outside the pocket, consistent with reduced backbone flexibility and improved folding/trafficking that raises apparent activity across backgrounds."
  },
  {
    "row_index": 59,
    "Description of effect": "G57L introduces a bulky hydrophobic side chain at a non-pocket glycine site, likely restricting backbone conformations and causing strong context dependence, including potential folding penalties."
  },
  {
    "row_index": 60,
    "Description of effect": "H143Q removes histidine protonation capability at a surface site, consistent with altered electrostatics that can reduce peroxygenation while relatively favoring peroxidation in some contexts."
  },
  {
    "row_index": 61,
    "Description of effect": "H143T replaces histidine with a neutral polar residue at a surface site, consistent with a gentler electrostatic change that can improve overall performance in many multi-mutant backgrounds."
  },
  {
    "row_index": 62,
    "Description of effect": "I241S introduces a polar hydroxyl at a non-pocket hydrophobic position, consistent with increased local hydration/solubility and altered packing near the C-terminus."
  },
  {
    "row_index": 63,
    "Description of effect": "L243C introduces a smaller, more polarizable side chain outside the pocket, which may subtly alter local packing or redox sensitivity, but the mechanism is uncertain."
  },
  {
    "row_index": 64,
    "Description of effect": "L38M introduces a thioether at a pocket-adjacent channel wall, which can adjust packing and (in UPO contexts) plausibly improve oxidative robustness, supporting higher sustained turnover."
  },
  {
    "row_index": 65,
    "Description of effect": "Q236L removes a polar amide outside the pocket, consistent with increased hydrophobic packing and stability that broadly supports higher activity across combinations."
  },
  {
    "row_index": 66,
    "Description of effect": "R239E reverses charge at a surface position, likely rewiring salt-bridge networks and solubility with strongly background-dependent effects (no isolated single-mutant readout here)."
  },
  {
    "row_index": 67,
    "Description of effect": "S214P introduces proline-mediated rigidity outside the pocket, consistent with stabilizing a loop/turn and improving folding or trafficking."
  },
  {
    "row_index": 68,
    "Description of effect": "S217P introduces a rigid proline outside the pocket, consistent with altered loop dynamics that can change access-channel motions and shift selectivity."
  },
  {
    "row_index": 69,
    "Description of effect": "S237V increases hydrophobicity outside the pocket, consistent with improved local packing and stability near the C-terminus."
  },
  {
    "row_index": 70,
    "Description of effect": "S29A removes a polar hydroxyl outside the pocket, consistent with modestly improved local packing and stability that can raise apparent activity."
  },
  {
    "row_index": 71,
    "Description of effect": "S29P introduces backbone rigidity outside the pocket, consistent with stabilizing a structural element important for folding/trafficking and enabling large gains in multi-mutant contexts."
  },
  {
    "row_index": 72,
    "Description of effect": "S41A removes a polar hydroxyl outside the pocket, consistent with improved local packing and reduced misfolding/aggregation that increases effective enzyme levels."
  },
  {
    "row_index": 73,
    "Description of effect": "S61F introduces a bulky aromatic side chain outside the pocket, consistent with altered packing that can boost activity but also create context-dependent stability costs."
  },
  {
    "row_index": 74,
    "Description of effect": "S61I increases hydrophobic packing outside the pocket, consistent with modest stabilization and broadly balanced effects on activity and selectivity."
  },
  {
    "row_index": 75,
    "Description of effect": "S75A removes a pocket hydroxyl near the reactive center, likely reducing polarity/steric constraints to improve substrate accommodation and shift selectivity."
  },
  {
    "row_index": 76,
    "Description of effect": "S75R introduces a bulky positive charge at a close pocket position, likely disrupting binding geometry and strongly shifting the peroxygenation/peroxidation balance."
  },
  {
    "row_index": 77,
    "Description of effect": "T65K introduces a positive charge outside the pocket, consistent with improved solubility/production and long-range electrostatic effects that broadly increase activity in many combinations."
  },
  {
    "row_index": 78,
    "Description of effect": "T66M replaces a polar side chain with a thioether outside the pocket, consistent with improved local packing and possibly oxidative robustness, but evidence is limited to one observation."
  },
  {
    "row_index": 79,
    "Description of effect": "T67A removes a polar hydroxyl outside the pocket, consistent with increased local hydrophobic packing that indirectly improves access-channel behavior across many combinations."
  },
  {
    "row_index": 80,
    "Description of effect": "T88N adds a polar amide outside the pocket, consistent with stabilizing local hydrogen-bonding networks and improving folding/solubility in multi-mutant backgrounds."
  },
  {
    "row_index": 81,
    "Description of effect": "V138T introduces a polar hydroxyl outside the pocket, consistent with modest stabilization via improved local hydrogen bonding/hydration and small activity shifts."
  },
  {
    "row_index": 82,
    "Description of effect": "This cluster combines pocket/channel reshaping (38/64/75/182) with surface stability/electrostatic drivers (notably 212/236), yielding a consistent global activity uplift with a tendency toward higher peroxidation."
  },
  {
    "row_index": 83,
    "Description of effect": "I64L+T67A+F220L likely opens and loosens the pocket (loss of aromatic packing at 220 plus subtle channel repacking), favoring faster but less pre-organized turnover and shifting selectivity toward peroxidation."
  },
  {
    "row_index": 84,
    "Description of effect": "S41A+S61F+Y212K combines surface packing and charge changes that most plausibly improve folding/production and overall catalytic competence rather than directly remodeling the active site."
  },
  {
    "row_index": 85,
    "Description of effect": "Across these multi-mutants, the shared pattern is channel opening/reshaping at several pocket walls (38/64/75/182/220/223) plus surface electrostatic tuning (often 212/236), producing strong peroxidation gains with moderate peroxygenation changes."
  },
  {
    "row_index": 86,
    "Description of effect": "T88N+Y212K+Q236L is dominated by surface stability/charge effects with no direct pocket edits, consistent with a modest global activity increase rather than a selectivity redesign."
  },
  {
    "row_index": 87,
    "Description of effect": "This cluster is dominated by surface/folding mutations (29/61/65/88/143/212/214/236) with limited pocket edits, consistent with improved enzyme availability plus mild channel tuning."
  },
  {
    "row_index": 88,
    "Description of effect": "These variants combine surface stability/electrostatics (29/41/61/65/88/143/212/236) with a pocket-gate change at 223, giving modest net gains and a tendency to favor peroxygenation over strong peroxidation boosts."
  },
  {
    "row_index": 89,
    "Description of effect": "H143Q/T paired with F220L combines a surface electrostatic change with loss of aromatic pocket packing, consistent with reduced productive binding for peroxygenation while maintaining or enhancing peroxidation via easier access."
  },
  {
    "row_index": 90,
    "Description of effect": "These combinations mix pocket reshaping (38/64/70/182/220) with surface/loop changes (61/67/88/212/236/217), yielding a profile consistent with enhanced access and peroxidation without a matching improvement in peroxygenation."
  },
  {
    "row_index": 91,
    "Description of effect": "Adding strong surface electrostatic changes (65/212 with optional 41/75/143) yields only modest net gains and, in this subset, a shift away from peroxidation, suggesting non-additive electrostatic effects."
  },
  {
    "row_index": 92,
    "Description of effect": "This high-performing cluster couples surface/expression drivers (29/65/88/143/212/236) with distal pocket remodeling (171/182 and sometimes 64/75), consistent with synergistic improvements in enzyme availability and substrate positioning for peroxygenation."
  },
  {
    "row_index": 93,
    "Description of effect": "S29P+T67A+T88N+H143T+A171F+S182M+H208D stacks multiple surface electrostatic/dynamic changes with distal pocket remodeling, yielding a profile consistent with peroxygenation-biased selectivity."
  },
  {
    "row_index": 94,
    "Description of effect": "S41A+G57A+T65K+A171F+S182M+Q236L shows strong activity but extremely low yield, indicating a tradeoff where catalytic improvements are offset by poor producibility."
  },
  {
    "row_index": 95,
    "Description of effect": "S29P+S41A+T67A+T88N+A171F+Q236L combines mostly surface stabilizers with one distal pocket edit, consistent with improved peroxygenation without a corresponding increase in peroxidation."
  },
  {
    "row_index": 96,
    "Description of effect": "These variants combine surface electrostatics/stability (65/88/212/236 with 143 and/or 208) with pocket gating (75) and distal pocket remodeling (171), consistent with improved overall turnover and a more balanced peroxygenation/peroxidation profile."
  },
  {
    "row_index": 97,
    "Description of effect": "S41A+T65K+T88N+Y212K+Q236L is surface-focused and lacks direct pocket edits, consistent with a global activity uplift driven by folding/solubility and long-range electrostatics."
  },
  {
    "row_index": 98,
    "Description of effect": "S41A+T65K+H143T+Y212K+Q236L adds an additional electrostatic perturbation at 143 to a surface-stabilized background, consistent with a small peroxygenation gain but reduced peroxidation in purified measurements."
  },
  {
    "row_index": 99,
    "Description of effect": "When distal pocket remodeling (171/182) is combined with multiple surface stabilizers and a pocket gate (75), peroxygenation can become very high while peroxidation remains moderate, consistent with improved substrate pre-organization."
  },
  {
    "row_index": 100,
    "Description of effect": "This broad cluster repeatedly combines surface stability/expression boosters (29/41/57/65/88/143/212/236) with distal pocket remodeling (171/182) and occasional electrostatic tuning (208), yielding consistently strong peroxygenation with moderate peroxidation."
  },
  {
    "row_index": 101,
    "Description of effect": "S41A+G57A+H143T+A171F+S182M+H208D combines surface electrostatic changes with distal pocket remodeling and shows a peroxygenation-biased shift with suppressed peroxidation."
  },
  {
    "row_index": 102,
    "Description of effect": "These multi-mutants combine extensive surface stabilization with distal pocket remodeling (171/182) and limited pocket edits (64/75), generally favoring peroxygenation while damping peroxidation."
  },
  {
    "row_index": 103,
    "Description of effect": "S41A+S75A+H143T+Y212K+Q236L shows near-baseline performance, consistent with negative epistasis where pocket gating and surface electrostatics partially cancel benefits (single data point)."
  },
  {
    "row_index": 104,
    "Description of effect": "S41A+G57A+I64L+T65K+T67A+T88N+A171F+S182M+H208D+Q236L achieves very high activity but very low yield, indicating strong catalytic synergy coupled to a major expression/folding penalty."
  },
  {
    "row_index": 105,
    "Description of effect": "Adding A167E into an already stacked background strongly suppresses peroxidation while maintaining high peroxygenation, consistent with surface electrostatic tuning that disfavors one-electron pathways."
  },
  {
    "row_index": 106,
    "Description of effect": "S29P+S41A+T65K+T67A+T88N+A171F+H208D+Y212K+Q236L yields high peroxygenation but low peroxidation and low yield, consistent with a peroxygenation-biased but less producible design."
  },
  {
    "row_index": 107,
    "Description of effect": "S29P+S41A+G57A+T65K+T88N+H143T+A171F+S182M+Y212K+Q236L combines surface stabilization with distal pocket remodeling to give strong peroxygenation with near-neutral peroxidation and good yield."
  },
  {
    "row_index": 108,
    "Description of effect": "This variant shows very high apparent activity but very low purified activities alongside extremely high yield, suggesting assay-context artifacts or a large inactive protein fraction, so mechanistic interpretation is uncertain."
  },
  {
    "row_index": 109,
    "Description of effect": "S29P+S41A+I64L+T65K+S75A+T88N+H143T+A171F+S182M+Y212K+Q236L shows the strongest peroxygenation gain with elevated peroxidation, consistent with synergistic pocket gating plus broad surface stabilization."
  },
  {
    "row_index": 110,
    "Description of effect": "Across these highly stacked mutants, the shared net effect is strong surface stabilization/expression tuning plus distal pocket remodeling that drives high peroxygenation, while additional C-terminal charge/packing edits likely modulate solubility rather than active-site chemistry."
  },
  {
    "row_index": 111,
    "Description of effect": "Adding S61F into a heavily stacked background preserves peroxygenation but reduces peroxidation, consistent with a packing change that alters global dynamics or expression in a non-additive way."
  },
  {
    "row_index": 112,
    "Description of effect": "These variants combine extensive surface stabilization with distal pocket remodeling and additional C-terminal electrostatic/packing edits, yielding moderate peroxygenation with suppressed peroxidation consistent with a more selective but not maximally active profile."
  }
]
```