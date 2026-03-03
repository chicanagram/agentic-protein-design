from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from tools.yasara import yasara
from tools.struct.pdb_to_csv import pdb_to_dataframe
from tools.struct.polarity_sterics_report import polarity_report, sterics_report
from project_config.variables import address_dict, subfolders

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
    df_bindingpocket['distance_to_centroid'] = np.linalg.norm(df_bindingpocket[['x','y','z']] - centroid, axis=1)
    resnum_list = df_bindingpocket['res_num'].drop_duplicates().tolist()
    if get_residue_min_distance:
        df_bindingpocket.loc[:, 'min_distance_to_centroid'] = None
        for resnum in resnum_list:
            min_dist_res = df_bindingpocket.loc[df_bindingpocket['res_num']==resnum, 'distance_to_centroid'].min()
            df_bindingpocket.loc[(df_bindingpocket['res_num']==resnum) & (df_bindingpocket['atom_name']=='CA'), 'min_distance_to_centroid'] = min_dist_res

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
        df_backbone = df[df['atom_name'] == 'CA']
        df_backbone.to_csv(out_csv.replace('.csv', '_backbone.csv'), index=False)
        print(f"Parsed {len(df)} atoms")
        print(f"Saved CSV to: {out_csv}")


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
        # initialize dict to store binding pocket analyses
        bindingpocket_analysis = []
        df_bindingpocket_backbone_dict = {}
        df_bindingpocket_dict = {}

        for struct_name, binding_pocket_residues in pocket_residues_dict.items():

            # get coordinates of protein atoms and backbone
            csv_fname = struct_name + '.csv'
            csv_fpath = self.struct_csv_dir + csv_fname
            csv_backbone_fpath = csv_fpath.replace('.csv', '_backbone.csv')
            if not os.path.exists(csv_fpath) or os.path.exists(csv_backbone_fpath):
                self.pdb_to_csv(struct_name)
            df_coords = pd.read_csv(csv_fpath)
            df_backbone_coords = pd.read_csv(csv_fpath.replace('.csv', '_backbone.csv'))

            # get binding pocket residue df
            num_res_binding_pocket_ali = len(binding_pocket_residues)
            df_bindingpocket = df_coords[df_coords['res_num'].isin(binding_pocket_residues)].copy()
            df_backbone_bindingpocket = df_backbone_coords[df_backbone_coords['res_num'].isin(binding_pocket_residues)].copy()
            print(f'[{struct_name}] Binding pocket residues  ({num_res_binding_pocket_ali}): {binding_pocket_residues}')

            # get binding pocket centroid and other key atoms
            centroid = df_bindingpocket[['x', 'y', 'z']].mean(axis=0).to_numpy()
            print('Centroid:', centroid)

            # get distances to binding pocket centroid
            print('--- All Residue Atoms ---')
            df_bindingpocket, mean_dist_to_centroid, mean_min_dist_to_centroid = get_distances_residues_bindingpocket_centroid(df_bindingpocket, centroid, get_residue_min_distance=True)
            print('--- Backbone Only ---')
            df_backbone_bindingpocket, mean_backbone_dist_to_centroid, _ = get_distances_residues_bindingpocket_centroid(df_backbone_bindingpocket, centroid, get_residue_min_distance=False)
            df_backbone_bindingpocket = df_backbone_bindingpocket.rename(columns={'distance_to_centroid': 'distance_to_centroid_CA'})
            min_dist_by_res = df_bindingpocket[['res_num', 'distance_to_centroid', 'min_distance_to_centroid']].dropna(how='any')
            df_backbone_bindingpocket = df_backbone_bindingpocket.merge(min_dist_by_res, on='res_num', how='left')

            # --- get per-residue polarity and sterics for protein---
            # get pocket polarity report
            pocket_polarity = polarity_report(
                df_backbone_bindingpocket,
                aa_col="res",
                aa_polarity_col="aa_polarity",
                dist_col="distance_to_centroid",
                kd_col="kd_hydro",
                hw_col="hw_polarity",
            )

            # get volume estimate
            pocket_sterics = sterics_report(
                df_backbone_bindingpocket,
                dist_col="distance_to_centroid",
                aa_col="res",
                vol_col="aa_vol",
            )

            # update analysis for this struct
            struct_analysis = {
                'struct_name': struct_name,
                'mean_min_dist_to_centroid': mean_min_dist_to_centroid,
                'mean_dist_to_centroid': mean_dist_to_centroid,
                'mean_dist_backbone_to_centroid': mean_backbone_dist_to_centroid,
            }
            struct_analysis.update(pocket_sterics)
            struct_analysis.update(pocket_polarity)
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
