from pymol import cmd
from project_config.variables import mapping_rev, aa_polarity_mapping

def convert_cif_to_pdb_pymol(cif_fpath, pdb_fpath):
    """
    Convert CIF fpath into PDB fpath.
    """
    cmd.reinitialize()
    cmd.load(cif_fpath)
    cmd.save(pdb_fpath)
    return pdb_fpath

def filter_residues(pdb_fpath, selection_condition="byres (chain A within 5 of chain B)", selection_name='selection'):
    cmd.reinitialize()
    cmd.load(pdb_fpath, "obj")
    cmd.select(selection_name, selection_condition)
    res_filt = sorted({(a.resn, int(a.resi)) for a in cmd.get_model(f"{selection_name} and name CA").atom}, key=lambda x: x[1])
    print(res_filt)
    return res_filt

def visualize_structures(pdb_list, show_res_near_ligand=6, protein_chain_id='A', ligand_chain_id='B'):
    """
    Visualize structures in pdb_list using NGLview
    """
    import nglview as nv
    view = nv.NGLWidget()
    for i, pdb in enumerate(pdb_list):
        print(i, pdb)
        # base context
        view.add_component(pdb, default_representation=False)
        view[i].clear_representations()
        view[i].add_cartoon(selection=f":{protein_chain_id}", colorScheme='residueindex')
        view[i].add_ball_and_stick(selection=':B', colorValue="orange")
        view[i].add_ball_and_stick(selection=':C', colorValue="orange")
        view[i].add_ball_and_stick(selection=f':{ligand_chain_id}')

        # color nearby protein residues close to ligand
        if show_res_near_ligand is not None:
            res_near_ligand = filter_residues(pdb, f"byres (chain {protein_chain_id} within {show_res_near_ligand} of chain {ligand_chain_id})", f'near_{protein_chain_id}_{ligand_chain_id}')
            for aa, res_num in res_near_ligand:
                polarity_grp = aa_polarity_mapping[mapping_rev[aa]]
                color = {"np": "lime", "p~": "cyan", "p+": "red", "p-": "blue"}[polarity_grp]
                view[i].add_licorice(selection=f':{protein_chain_id} and {res_num}', colorValue=color)
    view.center()
    return view