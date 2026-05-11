from __future__ import annotations
import os
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from agentic_protein_design.tools.yasara import yasara
from agentic_protein_design.tools.struct.pdb_to_csv import pdb_to_dataframe
from agentic_protein_design.tools.struct.residue_structural_annotations import get_residue_polarity, get_residue_sterics
from project_config.variables import address_dict, subfolders

XYZ_COLS = ['x', 'y', 'z']
RESNUM_COL = 'res_num'
ATOM_COL = 'atom_name'
BACKBONE_ATOM = 'CA'

def showres_bindingpocket_struct(pdb_fpath, binding_pocket_residues):
    yasara.LoadPdb(pdb_fpath)
    for resnum in binding_pocket_residues:
        yasara.HideRes('protein')
        yasara.ShowRes(f'protein and Res {resnum}')
        yasara.LabelRes(f'protein and Res {resnum}', 'RESNUM')
    # save as scene
    yasara.SaveSce(pdb_fpath.replace('pdb', 'sce'))


def get_distances_residues_bindingpocket_centroid(df_bindingpocket, centroid, get_residue_min_distance=False):
    """
    Calculate distances between residue and binding pocket center
    """
    df_bindingpocket['distance_to_centroid'] = np.linalg.norm(df_bindingpocket[XYZ_COLS] - centroid, axis=1)
    resnum_list = df_bindingpocket[RESNUM_COL].drop_duplicates().tolist()
    if get_residue_min_distance:
        df_bindingpocket.loc[:, 'min_distance_to_centroid'] = None
        for resnum in resnum_list:
            min_dist_res = df_bindingpocket.loc[df_bindingpocket[RESNUM_COL] == resnum, 'distance_to_centroid'].min()
            df_bindingpocket.loc[
                (df_bindingpocket[RESNUM_COL] == resnum) & (df_bindingpocket[ATOM_COL] == BACKBONE_ATOM),
                'min_distance_to_centroid'
            ] = min_dist_res

    # get stats
    mean_dist_to_centroid = round(df_bindingpocket['distance_to_centroid'].mean(),4)
    mean_min_dist_to_centroid = round(df_bindingpocket['min_distance_to_centroid'].mean(), 4) if get_residue_min_distance else None
    print('Mean distance to binding pocket centroid:', mean_dist_to_centroid)
    print('Mean MIN distance to binding pocket centroid:', mean_min_dist_to_centroid)

    return df_bindingpocket, mean_dist_to_centroid, mean_min_dist_to_centroid


class PocketAnalysis:

    def __init__(
            self,
            pdb_dir,
            struct_csv_dir,
    ):
        self.pdb_dir = pdb_dir
        self.struct_csv_dir = struct_csv_dir

    def pdb_to_csv(self, pdb_name):
        # get filepaths
        pdb_fpath = self.pdb_dir + pdb_name + '.pdb'
        out_csv = pdb_fpath.replace(self.pdb_dir, self.struct_csv_dir).replace('.pdb', '.csv')

        # process pdb
        df = pdb_to_dataframe(pdb_fpath)
        df.to_csv(out_csv, index=False)

        # get backbone of protein only
        df_backbone = df[df[ATOM_COL] == BACKBONE_ATOM]
        df_backbone.to_csv(out_csv.replace('.csv', '_backbone.csv'), index=False)
        print(f"Parsed {len(df)} atoms")
        print(f"Saved CSV to: {out_csv}")

    def _load_structure_tables(self, struct_name):
        """Load full-atom and backbone CSVs for a structure, generating them if missing."""
        csv_fname = struct_name + '.csv'
        csv_fpath = self.struct_csv_dir + csv_fname
        csv_backbone_fpath = csv_fpath.replace('.csv', '_backbone.csv')
        if not os.path.exists(csv_fpath) or os.path.exists(csv_backbone_fpath):
            self.pdb_to_csv(struct_name)
        structure_atoms_df = pd.read_csv(csv_fpath)
        structure_backbone_df = pd.read_csv(csv_backbone_fpath)
        return structure_atoms_df, structure_backbone_df

    def _select_pocket_tables(self, structure_atoms_df, structure_backbone_df, binding_pocket_residues):
        """Filter structure atom tables to binding-pocket residues."""
        pocket_atoms_df = structure_atoms_df[structure_atoms_df[RESNUM_COL].isin(binding_pocket_residues)].copy()
        pocket_backbone_df = structure_backbone_df[structure_backbone_df[RESNUM_COL].isin(binding_pocket_residues)].copy()
        return pocket_atoms_df, pocket_backbone_df

    def _compute_pocket_distance_tables(self, pocket_atoms_df, pocket_backbone_df, centroid):
        """Compute centroid distance features for full-atom and backbone pocket tables."""
        print('--- All Residue Atoms ---')
        pocket_atoms_df, mean_dist_to_centroid, mean_min_dist_to_centroid = get_distances_residues_bindingpocket_centroid(
            pocket_atoms_df, centroid, get_residue_min_distance=True
        )
        print('--- Backbone Only ---')
        pocket_backbone_df, mean_backbone_dist_to_centroid, _ = get_distances_residues_bindingpocket_centroid(
            pocket_backbone_df, centroid, get_residue_min_distance=False
        )
        pocket_backbone_df = pocket_backbone_df.rename(columns={'distance_to_centroid': 'distance_to_centroid_CA'})
        min_dist_by_res = pocket_atoms_df[[RESNUM_COL, 'distance_to_centroid', 'min_distance_to_centroid']].dropna(how='any')
        pocket_backbone_df = pocket_backbone_df.merge(min_dist_by_res, on=RESNUM_COL, how='left')
        return pocket_atoms_df, pocket_backbone_df, mean_dist_to_centroid, mean_min_dist_to_centroid, mean_backbone_dist_to_centroid

    def _build_struct_analysis(self, struct_name, pocket_backbone_df, mean_dist_to_centroid, mean_min_dist_to_centroid, mean_backbone_dist_to_centroid):
        """Compute sterics/polarity descriptors and return one structure summary dict."""
        pocket_polarity = get_residue_polarity(
            pocket_backbone_df,
            aa_col="res",
            aa_polarity_col="aa_polarity",
            dist_col="distance_to_centroid",
            kd_col="kd_hydro",
            hw_col="hw_polarity",
        )
        pocket_sterics = get_residue_sterics(
            pocket_backbone_df,
            dist_col="distance_to_centroid",
            aa_col="res",
            vol_col="aa_vol",
        )
        struct_analysis = {
            'struct_name': struct_name,
            'mean_min_dist_to_centroid': mean_min_dist_to_centroid,
            'mean_dist_to_centroid': mean_dist_to_centroid,
            'mean_dist_backbone_to_centroid': mean_backbone_dist_to_centroid,
        }
        struct_analysis.update(pocket_sterics)
        struct_analysis.update(pocket_polarity)
        return struct_analysis


    def plot_pocket_properties(self, bindingpocket_analysis):
        fig, ax = plt.subplots(1, 3, figsize=(12, 4))
        ax[0].scatter(bindingpocket_analysis['mean_min_dist_to_centroid'],
                      bindingpocket_analysis['mean_dist_to_centroid'])
        ax[0].set_xlabel('mean_min_dist_to_centroid')
        ax[0].set_ylabel('mean_dist_to_centroid')
        ax[1].scatter(bindingpocket_analysis['mean_dist_to_centroid'],
                      bindingpocket_analysis['mean_dist_backbone_to_centroid'])
        ax[1].set_xlabel('mean_dist_to_centroid')
        ax[1].set_ylabel('mean_dist_backbone_to_centroid')
        ax[2].scatter(bindingpocket_analysis['mean_dist_backbone_to_centroid'],
                      bindingpocket_analysis['mean_min_dist_to_centroid'])
        ax[2].set_xlabel('mean_dist_backbone_to_centroid')
        ax[2].set_ylabel('mean_min_dist_to_centroid')
        plt.show()

    def __call__(
            self,
            pocket_residues_dict,
            protein_molname='A',
            plot_properties=False,
    ):
        _ = protein_molname  # retained for API compatibility
        # initialize dict to store binding pocket analyses
        bindingpocket_analysis = []
        df_bindingpocket_backbone_dict = {}
        df_bindingpocket_dict = {}

        for struct_name, binding_pocket_residues in pocket_residues_dict.items():

            # get coordinates of protein atoms and backbone
            structure_atoms_df, structure_backbone_df = self._load_structure_tables(struct_name)

            # get binding pocket residue df
            num_res_binding_pocket_ali = len(binding_pocket_residues)
            df_bindingpocket, df_backbone_bindingpocket = self._select_pocket_tables(
                structure_atoms_df, structure_backbone_df, binding_pocket_residues
            )
            print(f'[{struct_name}] Binding pocket residues ({num_res_binding_pocket_ali}): {binding_pocket_residues}')

            # get binding pocket centroid and other key atoms
            centroid = df_bindingpocket[XYZ_COLS].mean(axis=0).to_numpy()
            print('Centroid:', centroid)

            # get distances to binding pocket centroid
            df_bindingpocket, df_backbone_bindingpocket, mean_dist_to_centroid, mean_min_dist_to_centroid, mean_backbone_dist_to_centroid = self._compute_pocket_distance_tables(
                df_bindingpocket, df_backbone_bindingpocket, centroid
            )

            # update analysis for this struct
            struct_analysis = self._build_struct_analysis(
                struct_name,
                df_backbone_bindingpocket,
                mean_dist_to_centroid,
                mean_min_dist_to_centroid,
                mean_backbone_dist_to_centroid,
            )
            bindingpocket_analysis.append(struct_analysis)
            df_bindingpocket_backbone_dict[struct_name] = df_backbone_bindingpocket
            df_bindingpocket_dict[struct_name] = df_bindingpocket
            print()

        bindingpocket_analysis = pd.DataFrame(bindingpocket_analysis).round(3)
        bindingpocket_analysis.to_csv(self.pdb_dir + 'bindingpocket_analysis.csv')

        # plot
        if plot_properties:
            self.plot_pocket_properties(bindingpocket_analysis)

        return bindingpocket_analysis, df_bindingpocket_dict, df_bindingpocket_backbone_dict



if __name__ == "__main__":
    os.chdir('../')

    # ---- user input ----
    data_folder = address_dict['PIPS2']
    data_subfolder = 'UPOs_peroxygenation_analysis/' # 'CARs' # 'sidestream_cocktail' #
    pdb_dir = data_folder + subfolders['pdb'] + data_subfolder
    struct_csv_dir = data_folder + subfolders['pdb'] + data_subfolder + 'structure_csv/'
    residues_near_ligand_fpath = pdb_dir + 'residues_near_ligand.csv'
    protein_molname = 'A'
    plot_properties = False

    # get binding pocket residues
    residues_near_ligand_df = pd.read_csv(residues_near_ligand_fpath)

    # iterate through structures
    struct_name_list = [
        'ET096',
        'CviUPO',
        'CviUPO-F88L+T158A',
        'DcaUPO',
        'OA167',
        'TE314'
    ]

    analyse_pocket = PocketAnalysis(pdb_dir, struct_csv_dir)
    bindingpocket_analysis, df_bindingpocket_dict, df_bindingpocket_backbone_dict = analyse_pocket(struct_name_list, residues_near_ligand_df, protein_molname, plot_properties)
    print(bindingpocket_analysis)
