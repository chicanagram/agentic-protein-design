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
| single           | 138                  | V138T*                                                                                       | Position 138 is outside the pocket and the modest gains observed are most consistent with an indirect effect on local packing/stability rather than altered substrate binding.                                                                                                             |
|                  |                      |                                                                                              | V138T adds polarity outside the pocket, consistent with improved local solvation/packing that produces modest, indirect gains in activity and product formation.                                                                                                                           |
| single           | 143                  | H143Q*; H143T*                                                                               | Position 143 is outside the pocket and appears to be an electrostatic/protonation hotspot that can shift expression and the peroxygenation/peroxidation balance via long-range coupling.                                                                                                   |
|                  |                      |                                                                                              | H143Q removes histidine’s titratable imidazole outside the pocket, consistent with altered long-range electrostatics that shifts the peroxygenation/peroxidation balance.                                                                                                                  |
|                  |                      |                                                                                              | H143T replaces the imidazole with a small polar side chain outside the pocket, consistent with reduced protonation/electrostatic coupling that can broadly alter catalytic balance in a context-dependent manner.                                                                          |
| single           | 167                  | A167E*                                                                                       | Position 167 is outside the pocket and introducing charge here can strongly reweight activity modes, consistent with a long-range electrostatic or stability effect.                                                                                                                       |
|                  |                      |                                                                                              | A167E introduces a negative charge on the surface, consistent with a long-range electrostatic/stability shift that changes the peroxygenation vs peroxidation balance.                                                                                                                     |
| single           | 171                  | A171F; A171I; A171L; A171V                                                                   | Position 171 is a distal pocket-lining site (~7–11 Å) where side-chain size and hydrophobicity can reshape channel volume and pre-organize substrates, often shifting peroxygenation efficiency in a substrate-dependent way.                                                              |
|                  |                      |                                                                                              | A171F introduces a bulky aromatic side chain in the distal pocket, likely narrowing/reshaping the channel to favor a more productive peroxygenation pose while disfavoring some alternative binding modes.                                                                                 |
|                  |                      |                                                                                              | A171I increases hydrophobic bulk in the distal pocket, consistent with improved packing and substrate pre-organization that can raise overall turnover.                                                                                                                                    |
|                  |                      |                                                                                              | A171L enlarges the distal pocket side chain and likely tightens the access channel, tending to favor peroxygenation-competent binding while making outcomes more sensitive to substrate fit.                                                                                               |
|                  |                      |                                                                                              | A171V modestly increases hydrophobic volume in the distal pocket, consistent with mild channel reshaping that can improve peroxygenation without a large penalty to other activities.                                                                                                      |
| single           | 174                  | L174F                                                                                        | Position 174 is a very close pocket contact (~3–4 Å) that likely acts as a steric gate, so small geometric changes can strongly alter productive binding versus alternative turnover modes.                                                                                                |
|                  |                      |                                                                                              | L174F adds aromatic bulk at a very close pocket contact, likely introducing steric crowding that impairs a productive peroxygenation pose more than it limits peroxidation.                                                                                                                |
| single           | 182                  | S182A; S182C; S182L; S182M; S182V                                                            | Position 182 is a distal pocket residue (~7–12 Å) that tunes local polarity/hydration and packing, affecting substrate orientation and the balance between peroxygenation and peroxidation.                                                                                                |
|                  |                      |                                                                                              | S182A removes a distal-pocket hydroxyl and slightly reduces side-chain size, likely decreasing local H-bonding/water retention to modestly favor peroxygenation.                                                                                                                           |
|                  |                      |                                                                                              | S182C replaces a hydroxyl with a thiol in the distal pocket, changing H-bonding and polarizability in a way that can subtly tune the channel microenvironment and overall turnover.                                                                                                        |
|                  |                      |                                                                                              | S182L introduces a larger hydrophobic side chain in the distal pocket, likely tightening the channel and reducing water access to improve substrate pre-organization.                                                                                                                      |
|                  |                      |                                                                                              | S182M adds a larger, polarizable hydrophobe in the distal pocket that can enhance peroxygenation and may improve peroxide tolerance by providing an oxidizable sink near the active site.                                                                                                  |
|                  |                      |                                                                                              | S182V increases hydrophobicity with a branched side chain in the distal pocket, consistent with a binding-pose shift that trades off peroxygenation versus peroxidation rather than a purely stability-driven effect.                                                                      |
| single           | 197                  | E197K*                                                                                       | Position 197 is outside the pocket and charge reversal here most plausibly alters surface electrostatics and stability/processing, increasing apparent activity without direct pocket reshaping.                                                                                           |
|                  |                      |                                                                                              | E197K flips a surface charge outside the pocket, consistent with altered electrostatic networks that increase apparent activity without evidence for direct active-site remodeling.                                                                                                        |
| single           | 208                  | H208D                                                                                        | Position 208 is outside the pocket, so mutations here most plausibly act through surface electrostatics or stability/processing effects that indirectly modulate overall catalytic output.                                                                                                 |
|                  |                      |                                                                                              | H208D replaces a titratable side chain with a fixed negative charge outside the pocket, consistent with an indirect activity/yield change via altered surface electrostatics or processing rather than pocket remodeling.                                                                  |
| single           | 212                  | Y212K; Y212T                                                                                 | Position 212 is outside the pocket but behaves as a strong global modulator, consistent with surface charge/packing effects that impact expression/stability and shift apparent catalytic balance.                                                                                         |
|                  |                      |                                                                                              | Y212K introduces a strong positive charge on the protein surface, consistent with altered expression/solubility and electrostatics that increase apparent activity, though the extreme side-signal suggests possible measurement or side-chemistry effects.                                |
|                  |                      |                                                                                              | Y212T removes an aromatic ring and reduces side-chain bulk on the surface, consistent with improved folding/secretion and moderate activity gains via reduced surface hydrophobicity.                                                                                                      |
| single           | 214                  | S214P*                                                                                       | Position 214 is outside the pocket and proline at this site suggests local backbone rigidification that can indirectly improve turnover, though evidence is limited.                                                                                                                       |
|                  |                      |                                                                                              | S214P introduces a proline outside the pocket, likely rigidifying a loop and indirectly improving turnover (single observation).                                                                                                                                                           |
| single           | 217                  | S217P*                                                                                       | Position 217 is outside the pocket and proline introduction likely rigidifies a loop that affects access dynamics or global stability, strongly boosting peroxidation in the available data.                                                                                               |
|                  |                      |                                                                                              | S217P rigidifies a non-pocket loop via proline, consistent with altered access dynamics that strongly increases peroxidation while only modestly affecting peroxygenation.                                                                                                                 |
| single           | 220                  | F220L                                                                                        | Position 220 is a pocket-wall residue (~6–8 Å) contributing aromatic/hydrophobic packing, so perturbations can disrupt productive substrate positioning for peroxygenation while leaving peroxidation less constrained.                                                                    |
|                  |                      |                                                                                              | F220L removes an aromatic ring from a pocket wall, weakening hydrophobic/π packing and enlarging local space, which likely destabilizes a productive peroxygenation binding pose while still allowing peroxidation.                                                                        |
| single           | 223                  | F223L*                                                                                       | Position 223 is a close pocket residue (~3.8 Å) near the access channel, so reducing steric/aromatic character here can open the pocket and preferentially increase peroxidation relative to peroxygenation.                                                                               |
|                  |                      |                                                                                              | F223L removes an aromatic ring at a close pocket contact, opening space and weakening hydrophobic/π interactions in a way that can favor faster substrate traffic and relatively higher peroxidation.                                                                                      |
| single           | 236                  | Q236L*                                                                                       | Position 236 is outside the pocket but highly recurrent in multi-mutants, consistent with a stability/solubility lever that supports higher activity when combined with pocket reshaping.                                                                                                  |
|                  |                      |                                                                                              | Q236L removes a polar amide outside the pocket and increases hydrophobicity, consistent with improved packing/expression that broadly supports higher apparent activity across many multi-mutant backgrounds.                                                                              |
| single           | 237                  | S237V*                                                                                       | Position 237 is outside the pocket and hydrophobic substitution here likely alters local packing near the terminus, indirectly affecting activity with modest, context-dependent effects.                                                                                                  |
|                  |                      |                                                                                              | S237V increases hydrophobicity outside the pocket, consistent with improved local packing/stability that modestly raises activity with limited, variable effects on catalytic balance.                                                                                                     |
| single           | 239                  | R239E*                                                                                       | Position 239 is outside the pocket and charge reversal here likely rewires surface salt-bridge networks, indirectly affecting folding/solubility and activity (mechanism uncertain from limited data).                                                                                     |
|                  |                      |                                                                                              | R239E flips a surface charge outside the pocket, likely rewiring salt bridges and electrostatics to alter stability/solubility with modest, context-dependent effects on activity.                                                                                                         |
| single           | 240                  | A240Q*                                                                                       | Position 240 is outside the pocket and adding a polar side chain is most consistent with improved local solvation/packing that indirectly supports activity in multi-mutant backgrounds.                                                                                                   |
|                  |                      |                                                                                              | A240Q adds a polar amide outside the pocket, plausibly stabilizing local solvation/packing and indirectly supporting activity, but its isolated contribution is uncertain because it appears only in multi-mutants.                                                                        |
| single           | 241                  | I241S*                                                                                       | Position 241 is outside the pocket and introducing polarity at a hydrophobic site likely perturbs local hydration/packing, indirectly modulating stability and activity in combination mutants.                                                                                            |
|                  |                      |                                                                                              | I241S introduces polarity at a hydrophobic non-pocket site, likely increasing local hydration and altering packing to indirectly modulate stability and activity depending on background.                                                                                                  |
| single           | 242                  | E242S*                                                                                       | Position 242 is outside the pocket and removing a negative charge likely reduces local electrostatic strain or alters surface interactions, indirectly influencing expression and activity in multi-mutant contexts.                                                                       |
|                  |                      |                                                                                              | E242S removes a negative charge outside the pocket, likely reducing surface electrostatic penalties and indirectly supporting stability/expression in combination mutants.                                                                                                                 |
| single           | 243                  | L243C*                                                                                       | Position 243 is outside the pocket and introducing a thiol can change local packing or chemical sensitivity, indirectly affecting stability/activity when combined with other mutations.                                                                                                   |
|                  |                      |                                                                                              | L243C introduces a smaller, polarizable thiol outside the pocket, which may alter local packing or chemical sensitivity and thereby indirectly affect stability/activity (uncertain).                                                                                                      |
| single           | 29                   | S29A*; S29P*                                                                                 | Position 29 is outside the pocket yet repeatedly associates with large performance shifts in multi-mutants, consistent with a folding/processing hotspot that indirectly amplifies catalytic output.                                                                                       |
|                  |                      |                                                                                              | S29A removes a polar hydroxyl outside the pocket, consistent with a small stability/processing improvement that yields modest activity and product gains.                                                                                                                                  |
|                  |                      |                                                                                              | S29P introduces a proline outside the pocket, likely rigidifying an N-terminal/loop region to improve folding/processing and broadly amplify activity across backgrounds.                                                                                                                  |
| single           | 38                   | L38M*                                                                                        | Position 38 is a distal pocket residue (~7–10 Å) that shapes the far end of the access channel, making it a lever for substrate traffic and catalytic partitioning.                                                                                                                        |
|                  |                      |                                                                                              | L38M introduces a sulfur-containing hydrophobe in the distal pocket, subtly reshaping the access channel and tending to increase peroxidation more than peroxygenation.                                                                                                                    |
| single           | 41                   | S41A*                                                                                        | Position 41 is outside the pocket but enriched among improved variants, consistent with a role in global stability/expression or dynamics that indirectly shifts catalytic balance.                                                                                                        |
|                  |                      |                                                                                              | S41A removes a polar hydroxyl outside the pocket, consistent with improved packing/expression that often increases peroxygenation while reducing peroxidation.                                                                                                                             |
| single           | 57                   | G57A*; G57L*                                                                                 | Position 57 is a non-pocket glycine likely controlling local backbone flexibility, so substitutions here can rigidify/repack a loop and indirectly influence expression and access-channel dynamics.                                                                                       |
|                  |                      |                                                                                              | G57A replaces glycine with a small methyl outside the pocket, likely reducing local flexibility to stabilize a loop and indirectly improve expression/stability and overall activity.                                                                                                      |
|                  |                      |                                                                                              | G57L introduces a bulky hydrophobe at a normally flexible non-pocket glycine, likely causing mispacking/rigidification that yields inconsistent performance and strong negative side signals.                                                                                              |
| single           | 61                   | S61F*; S61I*                                                                                 | Position 61 is outside the pocket and appears to tune global packing/solubility, with hydrophobic substitutions often improving apparent activity through expression/stability effects.                                                                                                    |
|                  |                      |                                                                                              | S61F introduces a bulky hydrophobe outside the pocket, which can improve packing but also risk misfolding/aggregation, consistent with higher crude performance but weaker purified performance.                                                                                           |
|                  |                      |                                                                                              | S61I increases hydrophobicity outside the pocket with moderate bulk, consistent with improved packing/stability that yields more balanced gains across activity modes.                                                                                                                     |
| single           | 64                   | I64L                                                                                         | Position 64 is a pocket-lining wall (~5 Å from ligand) that helps define the local steric contour for substrate approach, so small changes here can shift binding pose and the peroxygenation vs peroxidation balance.                                                                     |
|                  |                      |                                                                                              | I64L is a conservative hydrophobic repacking within the pocket that subtly changes wall geometry, consistent with improved substrate fit/access and a modest increase in overall turnover.                                                                                                 |
| single           | 65                   | T65K*                                                                                        | Position 65 is outside the pocket yet a dominant hotspot in multi-mutants, consistent with an electrostatic/processing lever that improves expression and synergizes with pocket changes.                                                                                                  |
|                  |                      |                                                                                              | T65K introduces a positive charge outside the pocket, consistent with improved solubility/expression and altered electrostatics that broadly enhance apparent activity with variable effects on catalytic balance.                                                                         |
| single           | 66                   | T66M*                                                                                        | Position 66 is outside the pocket and shows a strong activity boost in sparse data, consistent with a local packing/dynamics effect on folding or stability rather than direct active-site remodeling.                                                                                     |
|                  |                      |                                                                                              | T66M replaces a polar residue with a hydrophobic methionine outside the pocket, consistent with improved packing/stability and a strong activity boost in limited data (n=1).                                                                                                              |
| single           | 67                   | T67A*                                                                                        | Position 67 is outside the pocket but frequently co-occurs with gains, suggesting it modulates a nearby structural element that affects access-channel dynamics and overall turnover.                                                                                                      |
|                  |                      |                                                                                              | T67A removes a polar hydroxyl outside the pocket, consistent with improved local packing that supports higher turnover in multi-mutant contexts.                                                                                                                                           |
| single           | 70                   | M70F                                                                                         | Position 70 sits very close to the ligand (~4 Å) on the pocket wall, making it a sensitive determinant of substrate positioning and local oxidative robustness under peroxide-driven turnover.                                                                                             |
|                  |                      |                                                                                              | M70F increases aromatic bulk at a near-ligand pocket position, strengthening hydrophobic/π contacts that can stabilize substrate positioning but may reduce local flexibility.                                                                                                             |
| single           | 75                   | S75A*; S75R*                                                                                 | Position 75 is a near-ligand pocket residue (~5 Å) that likely acts as a polar/steric gate, so changes here can strongly tune substrate approach and catalytic partitioning.                                                                                                               |
|                  |                      |                                                                                              | S75A removes a polar hydroxyl at a near-ligand pocket gate, increasing local hydrophobicity/space in a way that can improve access and shift the peroxygenation/peroxidation balance via altered positioning.                                                                              |
|                  |                      |                                                                                              | S75R introduces a bulky positive charge at a near-ligand pocket position, likely restricting access and altering binding orientation to favor peroxygenation while suppressing peroxidation.                                                                                               |
| single           | 79                   | M79L                                                                                         | Position 79 is a mid-distance pocket residue (~7–10 Å) that shapes the distal part of the access channel, influencing substrate ingress/egress and orientation with moderate effects on catalytic partitioning.                                                                            |
|                  |                      |                                                                                              | M79L removes sulfur polarizability while maintaining hydrophobic volume in the pocket, consistent with a smoother channel wall that modestly improves productive binding.                                                                                                                  |
| single           | 87                   | T87G                                                                                         | Position 87 lies outside the defined pocket, so its effects are most consistent with indirect changes to local backbone packing/dynamics that propagate to folding or access-channel motions.                                                                                              |
|                  |                      |                                                                                              | T87G removes a side chain and increases backbone flexibility outside the pocket, consistent with an indirect conformational/dynamic change that can differentially affect peroxygenation and peroxidation.                                                                                 |
| single           | 88                   | T88N*                                                                                        | Position 88 is outside the pocket but recurrent in improved variants, consistent with stabilizing local H-bonding/dynamics that indirectly affects access-channel behavior and turnover.                                                                                                   |
|                  |                      |                                                                                              | T88N introduces a polar amide outside the pocket, consistent with stabilizing local H-bond networks and improving folding/processing to yield broad activity gains across backgrounds.                                                                                                     |
| multi            |                      | I64L+S182V+Y212K;                                                                            | These multi-mutants combine modest pocket-wall repacking (38/64/182) with strong surface tuning (notably 212), yielding higher overall turnover with a shift toward peroxidation.                                                                                                          |
|                  |                      | L38M+S182V+Y212K;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | T65K+S75A+Y212K+Q236L;                                                                       |                                                                                                                                                                                                                                                                                            |
|                  |                      | T88N+H143T+Y212K+Q236L                                                                       |                                                                                                                                                                                                                                                                                            |
| multi            |                      | I64L+T67A+F220L                                                                              | I64L+T67A+F220L combines pocket reshaping at 64/220 with a non-pocket change at 67, producing a profile biased toward peroxidation consistent with a less productive peroxygenation binding geometry.                                                                                      |
| multi            |                      | S41A+S61F+Y212K                                                                              | S41A+S61F+Y212K stacks surface/packing changes that boost crude performance but reduce purified activity, consistent with expression-driven gains and reduced intrinsic stability or catalytic efficiency.                                                                                 |
| multi            |                      | I64L+T67A+H143T;                                                                             | Across these multi-mutants, pocket reshaping (38/64/75/182/220/223) combined with surface/loop tuning (29/65/67/143/212/236) generally increases turnover and tends to favor peroxidation, consistent with improved substrate traffic and expression.                                      |
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
| multi            |                      | T88N+Y212K+Q236L                                                                             | T88N+Y212K+Q236L (all outside the pocket) gives moderate gains consistent with stabilization/electrostatic tuning rather than direct access-channel remodeling.                                                                                                                            |
| multi            |                      | H143T+Y212K;                                                                                 | This cluster mixes one or two pocket mutations with several non-pocket stability/electrostatic changes, producing moderate increases in activity consistent with improved expression plus mild channel tuning.                                                                             |
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
| multi            |                      | S29P+F223L;                                                                                  | These mutants are dominated by non-pocket electrostatic/processing changes with at most one pocket contact (75 or 223), yielding modest peroxygenation gains while suppressing peroxidation consistent with a higher peroxygenation:peroxidation bias.                                     |
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
| multi            |                      | H143Q+F220L;                                                                                 | H143Q/H143T paired with F220L yields low peroxygenation but high peroxidation, consistent with weakened productive binding from pocket aromatic loss combined with surface electrostatic changes.                                                                                          |
|                  |                      | H143T+F220L                                                                                  |                                                                                                                                                                                                                                                                                            |
| multi            |                      | L38M+I64L+S182V;                                                                             | These multi-mutants combine pocket reshaping (including 70/220) with non-pocket loop changes to give near-baseline peroxygenation but elevated peroxidation, consistent with channel configurations favoring one-electron chemistry.                                                       |
|                  |                      | L38M+T67A+S182V;                                                                             |                                                                                                                                                                                                                                                                                            |
|                  |                      | M70F+S217P+F220L;                                                                            |                                                                                                                                                                                                                                                                                            |
|                  |                      | S61I+T88N+Y212K+Q236L                                                                        |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S41A+T65K+Y212K;                                                                             | Adding surface electrostatic tuning (65/212 ±143) to a stability change (41) and a pocket gate change (75) yields only small net improvements, suggesting partial cancellation between expression gains and binding-pose perturbations.                                                    |
|                  |                      | T65K+S75A+H143T+Y212K                                                                        |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S29P+I64L+T65K+A171F+S182M+Y212K;                                                            | These variants combine strong pocket reshaping (171/182 plus 64/75) with multiple non-pocket changes, producing very large peroxygenation gains consistent with synergistic channel optimization supported by improved expression.                                                         |
|                  |                      | T65K+S75A+H143T+Y212K+Q236L;                                                                 |                                                                                                                                                                                                                                                                                            |
|                  |                      | T67A+T88N+H143T+A171F+S182M+Y212K                                                            |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S29P+T67A+T88N+H143T+A171F+S182M+H208D                                                       | S29P+T67A+T88N+H143T+A171F+S182M+H208D combines multiple surface/loop changes with pocket reshaping at 171/182 to give strong peroxygenation with only modest peroxidation, consistent with a peroxygenation-biased variant.                                                               |
| multi            |                      | S41A+G57A+T65K+A171F+S182M+Q236L                                                             | S41A+G57A+T65K+A171F+S182M+Q236L couples pocket reshaping (171/182) to several non-pocket changes and shows high peroxygenation but low peroxidation alongside very low yield, consistent with a potent but expression-limited construct.                                                  |
| multi            |                      | S29P+S41A+T67A+T88N+A171F+Q236L                                                              | S29P+S41A+T67A+T88N+A171F+Q236L combines A171-driven pocket reshaping with non-pocket loop/stability changes to yield high peroxygenation but low peroxidation, consistent with improved productive binding without boosting one-electron chemistry.                                       |
| multi            |                      | T65K+S75A+T88N+A171F+Y212K+H208D+Q236L;                                                      | These mutants combine a pocket gate change (75) with multiple non-pocket electrostatic/loop changes (±171/208/236), giving strong peroxygenation and moderate peroxidation with context-dependent side signals.                                                                            |
|                  |                      | T65K+S75A+T88N+H143T+Y212K                                                                   |                                                                                                                                                                                                                                                                                            |
| multi            |                      | S41A+T65K+T88N+Y212K+Q236L                                                                   | S41A+T65K+T88N+Y212K+Q236L is largely surface/loop tuning and yields moderate peroxygenation gains with small peroxidation changes, consistent with stabilization/expression improvements rather than pocket remodeling.                                                                   |
| multi            |                      | S41A+T65K+H143T+Y212K+Q236L                                                                  | S41A+T65K+H143T+Y212K+Q236L combines surface electrostatic changes that modestly improve both activity modes, consistent with global tuning rather than access-channel reshaping.                                                                                                          |
| multi            |                      | S29P+S41A+T65K+S75A+T88N+A171F+Y212K+S182M;                                                  | These mutants combine strong pocket reshaping (171/182 ±75) with multiple non-pocket changes to achieve very high peroxygenation with only modest peroxidation, consistent with a peroxygenation-favored channel environment supported by improved expression.                             |
|                  |                      | S41A+T65K+T88N+H143T+Y212K                                                                   |                                                                                                                                                                                                                                                                                            |
| multi            |                      | G57A+I64L+T65K+H143T+A171F+H208D;                                                            | Across this large cluster, stacking non-pocket stability/electrostatic mutations with pocket reshaping (64/75/171/182) yields consistently high peroxygenation with moderate peroxidation, consistent with expression gains plus access-channel remodeling favoring oxygen transfer.       |
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
| multi            |                      | S41A+G57A+H143T+A171F+S182M+H208D                                                            | S41A+G57A+H143T+A171F+S182M+H208D combines surface electrostatic/loop changes with pocket reshaping (171/182) and shows modest peroxygenation but low peroxidation, consistent with suppressed one-electron chemistry in this background.                                                  |
| multi            |                      | S29P+G57A+T88N+H143T+A171F+H208D+Y212K+Q236L;                                                | These multi-mutants heavily stack non-pocket tuning with pocket reshaping (64/75/171/182), yielding high peroxygenation but consistently low peroxidation consistent with variants biased toward a higher peroxygenation:peroxidation ratio.                                               |
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
| multi            |                      | S41A+S75A+H143T+Y212K+Q236L                                                                  | S41A+S75A+H143T+Y212K+Q236L combines a pocket gate change with multiple surface changes yet shows little synergy, suggesting the set does not improve the productive binding geometry in this context.                                                                                     |
| multi            |                      | S41A+G57A+I64L+T65K+T67A+T88N+A171F+S182M+H208D+Q236L                                        | S41A+G57A+I64L+T65K+T67A+T88N+A171F+S182M+H208D+Q236L shows very high peroxygenation but low peroxidation and very low yield, consistent with strong channel optimization coupled to expression/stability limitations.                                                                     |
| multi            |                      | S29P+S41A+G57A+H143T+A167E+A171F+S182M+H208D+Q236L                                           | Adding A167E to a pocket-reshaped, peroxygenation-biased background maintains high peroxygenation while further suppressing peroxidation, consistent with an additional long-range electrostatic shift.                                                                                    |
| multi            |                      | S29P+S41A+T65K+T67A+T88N+A171F+H208D+Y212K+Q236L                                             | S29P+S41A+T65K+T67A+T88N+A171F+H208D+Y212K+Q236L yields high peroxygenation but low peroxidation with reduced yield, consistent with strong peroxygenation tuning coupled to expression/stability penalties.                                                                               |
| multi            |                      | S29P+S41A+G57A+T65K+T88N+H143T+A171F+S182M+Y212K+Q236L                                       | S29P+S41A+G57A+T65K+T88N+H143T+A171F+S182M+Y212K+Q236L stacks pocket reshaping (171/182) with multiple surface changes to give high peroxygenation with slightly reduced peroxidation, consistent with a peroxygenation-favored channel environment.                                       |
| multi            |                      | S29P+S41A+G57A+I64L+T65K+T67A+H143T+A171F+S182M+H208D+Y212K+Q236L                            | This heavily stacked variant shows very high crude activity and yield but very low purified activities, suggesting a large inactive fraction or instability such that apparent gains may not reflect intrinsic catalysis.                                                                  |
| multi            |                      | S29P+S41A+I64L+T65K+S75A+T88N+H143T+A171F+S182M+Y212K+Q236L                                  | S29P+S41A+I64L+T65K+S75A+T88N+H143T+A171F+S182M+Y212K+Q236L combines multiple pocket-shaping mutations with several surface changes and shows the strongest peroxygenation with high peroxidation, consistent with broad channel remodeling that boosts overall turnover.                  |
| multi            |                      | G57A+I64L+T67A+T88N+H143T+A171F+S182M+Y212K+Q236L;                                           | This cluster stacks pocket reshaping (64/75/171/182) with broad surface remodeling (including 197 and a C-terminal block 237–243), yielding high peroxygenation with moderate peroxidation, though some constructs show side signals consistent with instability or measurement artifacts. |
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
| multi            |                      | S29P+S41A+S61F+I64L+T65K+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L                            | S29P+S41A+S61F+I64L+T65K+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L adds S61F to a heavily tuned background and yields moderate peroxygenation but low peroxidation, consistent with a peroxygenation bias accompanied by packing/expression tradeoffs.                                      |
| multi            |                      | S29P+S41A+G57L+I64L+T65K+S75A+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L;                      | These constructs combine strong pocket reshaping with extensive surface/terminal remodeling (237–243) and show moderate peroxygenation with low peroxidation, consistent with a peroxygenation-biased but peroxidation-suppressed profile alongside possible stability penalties.          |
|                  |                      | S41A+G57A+I64L+T67A+H143T+A171F+S182M+H208D+Y212K+Q236L+S237V+R239E+A240Q+I241S+E242S+L243C; |                                                                                                                                                                                                                                                                                            |
|                  |                      | S41A+I64L+T65K+S75R+T88N+H143T+A171F+Y212K+Q236L                                             |                                                                                                                                                                                                                                                                                            |

Raw LLM JSON:
```json
[
  {
    "row_index": 1,
    "Description of effect": "Position 64 is a pocket-lining wall (~5 Å from ligand) that helps define the local steric contour for substrate approach, so small changes here can shift binding pose and the peroxygenation vs peroxidation balance."
  },
  {
    "row_index": 2,
    "Description of effect": "Position 70 sits very close to the ligand (~4 Å) on the pocket wall, making it a sensitive determinant of substrate positioning and local oxidative robustness under peroxide-driven turnover."
  },
  {
    "row_index": 3,
    "Description of effect": "Position 79 is a mid-distance pocket residue (~7–10 Å) that shapes the distal part of the access channel, influencing substrate ingress/egress and orientation with moderate effects on catalytic partitioning."
  },
  {
    "row_index": 4,
    "Description of effect": "Position 87 lies outside the defined pocket, so its effects are most consistent with indirect changes to local backbone packing/dynamics that propagate to folding or access-channel motions."
  },
  {
    "row_index": 5,
    "Description of effect": "Position 171 is a distal pocket-lining site (~7–11 Å) where side-chain size and hydrophobicity can reshape channel volume and pre-organize substrates, often shifting peroxygenation efficiency in a substrate-dependent way."
  },
  {
    "row_index": 6,
    "Description of effect": "Position 174 is a very close pocket contact (~3–4 Å) that likely acts as a steric gate, so small geometric changes can strongly alter productive binding versus alternative turnover modes."
  },
  {
    "row_index": 7,
    "Description of effect": "Position 182 is a distal pocket residue (~7–12 Å) that tunes local polarity/hydration and packing, affecting substrate orientation and the balance between peroxygenation and peroxidation."
  },
  {
    "row_index": 8,
    "Description of effect": "Position 208 is outside the pocket, so mutations here most plausibly act through surface electrostatics or stability/processing effects that indirectly modulate overall catalytic output."
  },
  {
    "row_index": 9,
    "Description of effect": "Position 212 is outside the pocket but behaves as a strong global modulator, consistent with surface charge/packing effects that impact expression/stability and shift apparent catalytic balance."
  },
  {
    "row_index": 10,
    "Description of effect": "Position 220 is a pocket-wall residue (~6–8 Å) contributing aromatic/hydrophobic packing, so perturbations can disrupt productive substrate positioning for peroxygenation while leaving peroxidation less constrained."
  },
  {
    "row_index": 11,
    "Description of effect": "A171F introduces a bulky aromatic side chain in the distal pocket, likely narrowing/reshaping the channel to favor a more productive peroxygenation pose while disfavoring some alternative binding modes."
  },
  {
    "row_index": 12,
    "Description of effect": "A171I increases hydrophobic bulk in the distal pocket, consistent with improved packing and substrate pre-organization that can raise overall turnover."
  },
  {
    "row_index": 13,
    "Description of effect": "A171L enlarges the distal pocket side chain and likely tightens the access channel, tending to favor peroxygenation-competent binding while making outcomes more sensitive to substrate fit."
  },
  {
    "row_index": 14,
    "Description of effect": "A171V modestly increases hydrophobic volume in the distal pocket, consistent with mild channel reshaping that can improve peroxygenation without a large penalty to other activities."
  },
  {
    "row_index": 15,
    "Description of effect": "F220L removes an aromatic ring from a pocket wall, weakening hydrophobic/π packing and enlarging local space, which likely destabilizes a productive peroxygenation binding pose while still allowing peroxidation."
  },
  {
    "row_index": 16,
    "Description of effect": "H208D replaces a titratable side chain with a fixed negative charge outside the pocket, consistent with an indirect activity/yield change via altered surface electrostatics or processing rather than pocket remodeling."
  },
  {
    "row_index": 17,
    "Description of effect": "I64L is a conservative hydrophobic repacking within the pocket that subtly changes wall geometry, consistent with improved substrate fit/access and a modest increase in overall turnover."
  },
  {
    "row_index": 18,
    "Description of effect": "L174F adds aromatic bulk at a very close pocket contact, likely introducing steric crowding that impairs a productive peroxygenation pose more than it limits peroxidation."
  },
  {
    "row_index": 19,
    "Description of effect": "M70F increases aromatic bulk at a near-ligand pocket position, strengthening hydrophobic/π contacts that can stabilize substrate positioning but may reduce local flexibility."
  },
  {
    "row_index": 20,
    "Description of effect": "M79L removes sulfur polarizability while maintaining hydrophobic volume in the pocket, consistent with a smoother channel wall that modestly improves productive binding."
  },
  {
    "row_index": 21,
    "Description of effect": "S182A removes a distal-pocket hydroxyl and slightly reduces side-chain size, likely decreasing local H-bonding/water retention to modestly favor peroxygenation."
  },
  {
    "row_index": 22,
    "Description of effect": "S182C replaces a hydroxyl with a thiol in the distal pocket, changing H-bonding and polarizability in a way that can subtly tune the channel microenvironment and overall turnover."
  },
  {
    "row_index": 23,
    "Description of effect": "S182L introduces a larger hydrophobic side chain in the distal pocket, likely tightening the channel and reducing water access to improve substrate pre-organization."
  },
  {
    "row_index": 24,
    "Description of effect": "S182M adds a larger, polarizable hydrophobe in the distal pocket that can enhance peroxygenation and may improve peroxide tolerance by providing an oxidizable sink near the active site."
  },
  {
    "row_index": 25,
    "Description of effect": "S182V increases hydrophobicity with a branched side chain in the distal pocket, consistent with a binding-pose shift that trades off peroxygenation versus peroxidation rather than a purely stability-driven effect."
  },
  {
    "row_index": 26,
    "Description of effect": "T87G removes a side chain and increases backbone flexibility outside the pocket, consistent with an indirect conformational/dynamic change that can differentially affect peroxygenation and peroxidation."
  },
  {
    "row_index": 27,
    "Description of effect": "Y212K introduces a strong positive charge on the protein surface, consistent with altered expression/solubility and electrostatics that increase apparent activity, though the extreme side-signal suggests possible measurement or side-chemistry effects."
  },
  {
    "row_index": 28,
    "Description of effect": "Y212T removes an aromatic ring and reduces side-chain bulk on the surface, consistent with improved folding/secretion and moderate activity gains via reduced surface hydrophobicity."
  },
  {
    "row_index": 29,
    "Description of effect": "Position 29 is outside the pocket yet repeatedly associates with large performance shifts in multi-mutants, consistent with a folding/processing hotspot that indirectly amplifies catalytic output."
  },
  {
    "row_index": 30,
    "Description of effect": "Position 38 is a distal pocket residue (~7–10 Å) that shapes the far end of the access channel, making it a lever for substrate traffic and catalytic partitioning."
  },
  {
    "row_index": 31,
    "Description of effect": "Position 41 is outside the pocket but enriched among improved variants, consistent with a role in global stability/expression or dynamics that indirectly shifts catalytic balance."
  },
  {
    "row_index": 32,
    "Description of effect": "Position 57 is a non-pocket glycine likely controlling local backbone flexibility, so substitutions here can rigidify/repack a loop and indirectly influence expression and access-channel dynamics."
  },
  {
    "row_index": 33,
    "Description of effect": "Position 61 is outside the pocket and appears to tune global packing/solubility, with hydrophobic substitutions often improving apparent activity through expression/stability effects."
  },
  {
    "row_index": 34,
    "Description of effect": "Position 65 is outside the pocket yet a dominant hotspot in multi-mutants, consistent with an electrostatic/processing lever that improves expression and synergizes with pocket changes."
  },
  {
    "row_index": 35,
    "Description of effect": "Position 66 is outside the pocket and shows a strong activity boost in sparse data, consistent with a local packing/dynamics effect on folding or stability rather than direct active-site remodeling."
  },
  {
    "row_index": 36,
    "Description of effect": "Position 67 is outside the pocket but frequently co-occurs with gains, suggesting it modulates a nearby structural element that affects access-channel dynamics and overall turnover."
  },
  {
    "row_index": 37,
    "Description of effect": "Position 75 is a near-ligand pocket residue (~5 Å) that likely acts as a polar/steric gate, so changes here can strongly tune substrate approach and catalytic partitioning."
  },
  {
    "row_index": 38,
    "Description of effect": "Position 88 is outside the pocket but recurrent in improved variants, consistent with stabilizing local H-bonding/dynamics that indirectly affects access-channel behavior and turnover."
  },
  {
    "row_index": 39,
    "Description of effect": "Position 138 is outside the pocket and the modest gains observed are most consistent with an indirect effect on local packing/stability rather than altered substrate binding."
  },
  {
    "row_index": 40,
    "Description of effect": "Position 143 is outside the pocket and appears to be an electrostatic/protonation hotspot that can shift expression and the peroxygenation/peroxidation balance via long-range coupling."
  },
  {
    "row_index": 41,
    "Description of effect": "Position 167 is outside the pocket and introducing charge here can strongly reweight activity modes, consistent with a long-range electrostatic or stability effect."
  },
  {
    "row_index": 42,
    "Description of effect": "Position 197 is outside the pocket and charge reversal here most plausibly alters surface electrostatics and stability/processing, increasing apparent activity without direct pocket reshaping."
  },
  {
    "row_index": 43,
    "Description of effect": "Position 214 is outside the pocket and proline at this site suggests local backbone rigidification that can indirectly improve turnover, though evidence is limited."
  },
  {
    "row_index": 44,
    "Description of effect": "Position 217 is outside the pocket and proline introduction likely rigidifies a loop that affects access dynamics or global stability, strongly boosting peroxidation in the available data."
  },
  {
    "row_index": 45,
    "Description of effect": "Position 223 is a close pocket residue (~3.8 Å) near the access channel, so reducing steric/aromatic character here can open the pocket and preferentially increase peroxidation relative to peroxygenation."
  },
  {
    "row_index": 46,
    "Description of effect": "Position 236 is outside the pocket but highly recurrent in multi-mutants, consistent with a stability/solubility lever that supports higher activity when combined with pocket reshaping."
  },
  {
    "row_index": 47,
    "Description of effect": "Position 237 is outside the pocket and hydrophobic substitution here likely alters local packing near the terminus, indirectly affecting activity with modest, context-dependent effects."
  },
  {
    "row_index": 48,
    "Description of effect": "Position 239 is outside the pocket and charge reversal here likely rewires surface salt-bridge networks, indirectly affecting folding/solubility and activity (mechanism uncertain from limited data)."
  },
  {
    "row_index": 49,
    "Description of effect": "Position 240 is outside the pocket and adding a polar side chain is most consistent with improved local solvation/packing that indirectly supports activity in multi-mutant backgrounds."
  },
  {
    "row_index": 50,
    "Description of effect": "Position 241 is outside the pocket and introducing polarity at a hydrophobic site likely perturbs local hydration/packing, indirectly modulating stability and activity in combination mutants."
  },
  {
    "row_index": 51,
    "Description of effect": "Position 242 is outside the pocket and removing a negative charge likely reduces local electrostatic strain or alters surface interactions, indirectly influencing expression and activity in multi-mutant contexts."
  },
  {
    "row_index": 52,
    "Description of effect": "Position 243 is outside the pocket and introducing a thiol can change local packing or chemical sensitivity, indirectly affecting stability/activity when combined with other mutations."
  },
  {
    "row_index": 53,
    "Description of effect": "A167E introduces a negative charge on the surface, consistent with a long-range electrostatic/stability shift that changes the peroxygenation vs peroxidation balance."
  },
  {
    "row_index": 54,
    "Description of effect": "A240Q adds a polar amide outside the pocket, plausibly stabilizing local solvation/packing and indirectly supporting activity, but its isolated contribution is uncertain because it appears only in multi-mutants."
  },
  {
    "row_index": 55,
    "Description of effect": "E197K flips a surface charge outside the pocket, consistent with altered electrostatic networks that increase apparent activity without evidence for direct active-site remodeling."
  },
  {
    "row_index": 56,
    "Description of effect": "E242S removes a negative charge outside the pocket, likely reducing surface electrostatic penalties and indirectly supporting stability/expression in combination mutants."
  },
  {
    "row_index": 57,
    "Description of effect": "F223L removes an aromatic ring at a close pocket contact, opening space and weakening hydrophobic/π interactions in a way that can favor faster substrate traffic and relatively higher peroxidation."
  },
  {
    "row_index": 58,
    "Description of effect": "G57A replaces glycine with a small methyl outside the pocket, likely reducing local flexibility to stabilize a loop and indirectly improve expression/stability and overall activity."
  },
  {
    "row_index": 59,
    "Description of effect": "G57L introduces a bulky hydrophobe at a normally flexible non-pocket glycine, likely causing mispacking/rigidification that yields inconsistent performance and strong negative side signals."
  },
  {
    "row_index": 60,
    "Description of effect": "H143Q removes histidine’s titratable imidazole outside the pocket, consistent with altered long-range electrostatics that shifts the peroxygenation/peroxidation balance."
  },
  {
    "row_index": 61,
    "Description of effect": "H143T replaces the imidazole with a small polar side chain outside the pocket, consistent with reduced protonation/electrostatic coupling that can broadly alter catalytic balance in a context-dependent manner."
  },
  {
    "row_index": 62,
    "Description of effect": "I241S introduces polarity at a hydrophobic non-pocket site, likely increasing local hydration and altering packing to indirectly modulate stability and activity depending on background."
  },
  {
    "row_index": 63,
    "Description of effect": "L243C introduces a smaller, polarizable thiol outside the pocket, which may alter local packing or chemical sensitivity and thereby indirectly affect stability/activity (uncertain)."
  },
  {
    "row_index": 64,
    "Description of effect": "L38M introduces a sulfur-containing hydrophobe in the distal pocket, subtly reshaping the access channel and tending to increase peroxidation more than peroxygenation."
  },
  {
    "row_index": 65,
    "Description of effect": "Q236L removes a polar amide outside the pocket and increases hydrophobicity, consistent with improved packing/expression that broadly supports higher apparent activity across many multi-mutant backgrounds."
  },
  {
    "row_index": 66,
    "Description of effect": "R239E flips a surface charge outside the pocket, likely rewiring salt bridges and electrostatics to alter stability/solubility with modest, context-dependent effects on activity."
  },
  {
    "row_index": 67,
    "Description of effect": "S214P introduces a proline outside the pocket, likely rigidifying a loop and indirectly improving turnover (single observation)."
  },
  {
    "row_index": 68,
    "Description of effect": "S217P rigidifies a non-pocket loop via proline, consistent with altered access dynamics that strongly increases peroxidation while only modestly affecting peroxygenation."
  },
  {
    "row_index": 69,
    "Description of effect": "S237V increases hydrophobicity outside the pocket, consistent with improved local packing/stability that modestly raises activity with limited, variable effects on catalytic balance."
  },
  {
    "row_index": 70,
    "Description of effect": "S29A removes a polar hydroxyl outside the pocket, consistent with a small stability/processing improvement that yields modest activity and product gains."
  },
  {
    "row_index": 71,
    "Description of effect": "S29P introduces a proline outside the pocket, likely rigidifying an N-terminal/loop region to improve folding/processing and broadly amplify activity across backgrounds."
  },
  {
    "row_index": 72,
    "Description of effect": "S41A removes a polar hydroxyl outside the pocket, consistent with improved packing/expression that often increases peroxygenation while reducing peroxidation."
  },
  {
    "row_index": 73,
    "Description of effect": "S61F introduces a bulky hydrophobe outside the pocket, which can improve packing but also risk misfolding/aggregation, consistent with higher crude performance but weaker purified performance."
  },
  {
    "row_index": 74,
    "Description of effect": "S61I increases hydrophobicity outside the pocket with moderate bulk, consistent with improved packing/stability that yields more balanced gains across activity modes."
  },
  {
    "row_index": 75,
    "Description of effect": "S75A removes a polar hydroxyl at a near-ligand pocket gate, increasing local hydrophobicity/space in a way that can improve access and shift the peroxygenation/peroxidation balance via altered positioning."
  },
  {
    "row_index": 76,
    "Description of effect": "S75R introduces a bulky positive charge at a near-ligand pocket position, likely restricting access and altering binding orientation to favor peroxygenation while suppressing peroxidation."
  },
  {
    "row_index": 77,
    "Description of effect": "T65K introduces a positive charge outside the pocket, consistent with improved solubility/expression and altered electrostatics that broadly enhance apparent activity with variable effects on catalytic balance."
  },
  {
    "row_index": 78,
    "Description of effect": "T66M replaces a polar residue with a hydrophobic methionine outside the pocket, consistent with improved packing/stability and a strong activity boost in limited data (n=1)."
  },
  {
    "row_index": 79,
    "Description of effect": "T67A removes a polar hydroxyl outside the pocket, consistent with improved local packing that supports higher turnover in multi-mutant contexts."
  },
  {
    "row_index": 80,
    "Description of effect": "T88N introduces a polar amide outside the pocket, consistent with stabilizing local H-bond networks and improving folding/processing to yield broad activity gains across backgrounds."
  },
  {
    "row_index": 81,
    "Description of effect": "V138T adds polarity outside the pocket, consistent with improved local solvation/packing that produces modest, indirect gains in activity and product formation."
  },
  {
    "row_index": 82,
    "Description of effect": "These multi-mutants combine modest pocket-wall repacking (38/64/182) with strong surface tuning (notably 212), yielding higher overall turnover with a shift toward peroxidation."
  },
  {
    "row_index": 83,
    "Description of effect": "I64L+T67A+F220L combines pocket reshaping at 64/220 with a non-pocket change at 67, producing a profile biased toward peroxidation consistent with a less productive peroxygenation binding geometry."
  },
  {
    "row_index": 84,
    "Description of effect": "S41A+S61F+Y212K stacks surface/packing changes that boost crude performance but reduce purified activity, consistent with expression-driven gains and reduced intrinsic stability or catalytic efficiency."
  },
  {
    "row_index": 85,
    "Description of effect": "Across these multi-mutants, pocket reshaping (38/64/75/182/220/223) combined with surface/loop tuning (29/65/67/143/212/236) generally increases turnover and tends to favor peroxidation, consistent with improved substrate traffic and expression."
  },
  {
    "row_index": 86,
    "Description of effect": "T88N+Y212K+Q236L (all outside the pocket) gives moderate gains consistent with stabilization/electrostatic tuning rather than direct access-channel remodeling."
  },
  {
    "row_index": 87,
    "Description of effect": "This cluster mixes one or two pocket mutations with several non-pocket stability/electrostatic changes, producing moderate increases in activity consistent with improved expression plus mild channel tuning."
  },
  {
    "row_index": 88,
    "Description of effect": "These mutants are dominated by non-pocket electrostatic/processing changes with at most one pocket contact (75 or 223), yielding modest peroxygenation gains while suppressing peroxidation consistent with a higher peroxygenation:peroxidation bias."
  },
  {
    "row_index": 89,
    "Description of effect": "H143Q/H143T paired with F220L yields low peroxygenation but high peroxidation, consistent with weakened productive binding from pocket aromatic loss combined with surface electrostatic changes."
  },
  {
    "row_index": 90,
    "Description of effect": "These multi-mutants combine pocket reshaping (including 70/220) with non-pocket loop changes to give near-baseline peroxygenation but elevated peroxidation, consistent with channel configurations favoring one-electron chemistry."
  },
  {
    "row_index": 91,
    "Description of effect": "Adding surface electrostatic tuning (65/212 ±143) to a stability change (41) and a pocket gate change (75) yields only small net improvements, suggesting partial cancellation between expression gains and binding-pose perturbations."
  },
  {
    "row_index": 92,
    "Description of effect": "These variants combine strong pocket reshaping (171/182 plus 64/75) with multiple non-pocket changes, producing very large peroxygenation gains consistent with synergistic channel optimization supported by improved expression."
  },
  {
    "row_index": 93,
    "Description of effect": "S29P+T67A+T88N+H143T+A171F+S182M+H208D combines multiple surface/loop changes with pocket reshaping at 171/182 to give strong peroxygenation with only modest peroxidation, consistent with a peroxygenation-biased variant."
  },
  {
    "row_index": 94,
    "Description of effect": "S41A+G57A+T65K+A171F+S182M+Q236L couples pocket reshaping (171/182) to several non-pocket changes and shows high peroxygenation but low peroxidation alongside very low yield, consistent with a potent but expression-limited construct."
  },
  {
    "row_index": 95,
    "Description of effect": "S29P+S41A+T67A+T88N+A171F+Q236L combines A171-driven pocket reshaping with non-pocket loop/stability changes to yield high peroxygenation but low peroxidation, consistent with improved productive binding without boosting one-electron chemistry."
  },
  {
    "row_index": 96,
    "Description of effect": "These mutants combine a pocket gate change (75) with multiple non-pocket electrostatic/loop changes (±171/208/236), giving strong peroxygenation and moderate peroxidation with context-dependent side signals."
  },
  {
    "row_index": 97,
    "Description of effect": "S41A+T65K+T88N+Y212K+Q236L is largely surface/loop tuning and yields moderate peroxygenation gains with small peroxidation changes, consistent with stabilization/expression improvements rather than pocket remodeling."
  },
  {
    "row_index": 98,
    "Description of effect": "S41A+T65K+H143T+Y212K+Q236L combines surface electrostatic changes that modestly improve both activity modes, consistent with global tuning rather than access-channel reshaping."
  },
  {
    "row_index": 99,
    "Description of effect": "These mutants combine strong pocket reshaping (171/182 ±75) with multiple non-pocket changes to achieve very high peroxygenation with only modest peroxidation, consistent with a peroxygenation-favored channel environment supported by improved expression."
  },
  {
    "row_index": 100,
    "Description of effect": "Across this large cluster, stacking non-pocket stability/electrostatic mutations with pocket reshaping (64/75/171/182) yields consistently high peroxygenation with moderate peroxidation, consistent with expression gains plus access-channel remodeling favoring oxygen transfer."
  },
  {
    "row_index": 101,
    "Description of effect": "S41A+G57A+H143T+A171F+S182M+H208D combines surface electrostatic/loop changes with pocket reshaping (171/182) and shows modest peroxygenation but low peroxidation, consistent with suppressed one-electron chemistry in this background."
  },
  {
    "row_index": 102,
    "Description of effect": "These multi-mutants heavily stack non-pocket tuning with pocket reshaping (64/75/171/182), yielding high peroxygenation but consistently low peroxidation consistent with variants biased toward a higher peroxygenation:peroxidation ratio."
  },
  {
    "row_index": 103,
    "Description of effect": "S41A+S75A+H143T+Y212K+Q236L combines a pocket gate change with multiple surface changes yet shows little synergy, suggesting the set does not improve the productive binding geometry in this context."
  },
  {
    "row_index": 104,
    "Description of effect": "S41A+G57A+I64L+T65K+T67A+T88N+A171F+S182M+H208D+Q236L shows very high peroxygenation but low peroxidation and very low yield, consistent with strong channel optimization coupled to expression/stability limitations."
  },
  {
    "row_index": 105,
    "Description of effect": "Adding A167E to a pocket-reshaped, peroxygenation-biased background maintains high peroxygenation while further suppressing peroxidation, consistent with an additional long-range electrostatic shift."
  },
  {
    "row_index": 106,
    "Description of effect": "S29P+S41A+T65K+T67A+T88N+A171F+H208D+Y212K+Q236L yields high peroxygenation but low peroxidation with reduced yield, consistent with strong peroxygenation tuning coupled to expression/stability penalties."
  },
  {
    "row_index": 107,
    "Description of effect": "S29P+S41A+G57A+T65K+T88N+H143T+A171F+S182M+Y212K+Q236L stacks pocket reshaping (171/182) with multiple surface changes to give high peroxygenation with slightly reduced peroxidation, consistent with a peroxygenation-favored channel environment."
  },
  {
    "row_index": 108,
    "Description of effect": "This heavily stacked variant shows very high crude activity and yield but very low purified activities, suggesting a large inactive fraction or instability such that apparent gains may not reflect intrinsic catalysis."
  },
  {
    "row_index": 109,
    "Description of effect": "S29P+S41A+I64L+T65K+S75A+T88N+H143T+A171F+S182M+Y212K+Q236L combines multiple pocket-shaping mutations with several surface changes and shows the strongest peroxygenation with high peroxidation, consistent with broad channel remodeling that boosts overall turnover."
  },
  {
    "row_index": 110,
    "Description of effect": "This cluster stacks pocket reshaping (64/75/171/182) with broad surface remodeling (including 197 and a C-terminal block 237–243), yielding high peroxygenation with moderate peroxidation, though some constructs show side signals consistent with instability or measurement artifacts."
  },
  {
    "row_index": 111,
    "Description of effect": "S29P+S41A+S61F+I64L+T65K+T88N+H143T+A171F+H208D+S182M+Y212K+Q236L adds S61F to a heavily tuned background and yields moderate peroxygenation but low peroxidation, consistent with a peroxygenation bias accompanied by packing/expression tradeoffs."
  },
  {
    "row_index": 112,
    "Description of effect": "These constructs combine strong pocket reshaping with extensive surface/terminal remodeling (237–243) and show moderate peroxygenation with low peroxidation, consistent with a peroxygenation-biased but peroxidation-suppressed profile alongside possible stability penalties."
  }
]
```