from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from agentic_protein_design.tools.struct.analyse_binding_pocket import PocketAnalysis
from agentic_protein_design.tools.yasara import yasara
from agentic_protein_design.tools.yasara.align_struct_yasara import AlignStruct
from agentic_protein_design.tools.align.msa_to_dataframe import convert_msa_to_dataframe
from agentic_protein_design.tools.struct.pdb_to_csv import pdb_to_dataframe
from project_config.variables import address_dict, subfolders
from agentic_protein_design.tools.utils.seq_utils import fetch_sequences_from_fasta, write_sequence_to_fasta
from agentic_protein_design.tools.align.visualize_alignment import visualize_msa


class LigandPocketAnalysis:
    def __init__(
            self,
            pdb_dir,
            sce_dir,
            msa_dir,
            struct_csv_dir,
            lig_csv_suffix,
    ):
        self.pdb_dir = pdb_dir
        self.sce_dir = sce_dir
        self.msa_dir = msa_dir
        self.struct_csv_dir = struct_csv_dir
        self.lig_csv_suffix = lig_csv_suffix


    def align_structs(
            self,
            struct_names,
            pdb_names,
            seq_align_fname,
    ):
        """
        Structurally align PDBs and save aligned structures.
        Obtain sequence alignment.
        """
        align_struct = AlignStruct(
            self.pdb_dir,
            self.sce_dir,
            self.msa_dir,
            delete_residue_str=None,
            superpose_method='struct'
        )

        # run alignment pipeline
        _ = align_struct.run_pipeline(
            pdb_names,
            seq_align_fname,
            run_structure_alignment=True,
            parse_seq_struct_alignments=False,
            save_sce=True,
            join_obj_in_pdb=False,
            save_indiv_aligned_structs=True,
            delete_not_protein=False,
        )
        # convert to dataframe
        seqs, seq_names, _ = fetch_sequences_from_fasta(self.seq_align_fpath)
        pos_offset_bystruct = {}
        for i, struct_name in enumerate(struct_names):
            obj_num = i + 1
            resnum_list = yasara.ListRes(f'Obj {obj_num} and protein', format='RESNUM')
            starting_resnum = resnum_list[0]
            pos_offset = starting_resnum - 1
            if pos_offset != 0:
                pos_offset_bystruct[struct_name] = pos_offset

        # convert MSA to dataframe
        ali_df = convert_msa_to_dataframe(seqs, struct_names, pos_offset_bystruct)
        ali_df_fpath = self.seq_align_fpath.replace('.fasta', '.csv')
        ali_df.to_csv(ali_df_fpath)
        print('Saved alignment dataframe:', ali_df_fpath)
        return ali_df


    def pdb_to_csv(self, pdb_name, ligand_molname=None):
        # get filepaths
        pdb_fpath = Path(self.pdb_dir + pdb_name + '.pdb')
        out_csv = str(pdb_fpath).replace(self.pdb_dir, self.struct_csv_dir).replace('.pdb', '.csv')

        # process pdb
        df = pdb_to_dataframe(pdb_fpath)
        df.to_csv(out_csv, index=False)

        # get backbone of protein only
        df_backbone = df[df['atom_name'] == 'CA']
        df_backbone.to_csv(out_csv.replace('.csv', '_backbone.csv'), index=False)
        print(f"Parsed {len(df)} atoms >> Saved CSV to: {out_csv}")

        # extract ligand data
        if ligand_molname is not None:
            df_ligand = df[df['chain_id'] == ligand_molname].reset_index(drop=True)
            df_ligand.to_csv(out_csv.replace('.csv', f'_Lig{ligand_molname}.csv'))



    def get_binding_pocket_residues(self, struct_names, pdb_names, ligand_molname, ali_df, dist_thres, sce_fpath=None):
        """
        Get binding pocket residues by filtering by proximity to ligand
        """
        if sce_fpath is not None:
            yasara.LoadSce(sce_fpath)

        ali_index_filt = []
        for i, (struct_name, pdb_name) in enumerate(zip(struct_names, pdb_names)):
            obj_num = i + 1
            # pocket residues close to docked ligand
            binding_pocket_res = yasara.ListRes(f'Obj {obj_num} and protein and with distance<{dist_thres} from Mol {ligand_molname}', format='RESNUM')
            # update binding pocket df
            binding_pocket_df_struct = ali_df.loc[ali_df[f'{struct_name}_res_num'].isin(binding_pocket_res), ['index', f'{struct_name}_res_num', f'{struct_name}_res_aa']].copy()
            ali_index_filt += binding_pocket_df_struct['index'].tolist()
            binding_pocket_df_struct = binding_pocket_df_struct.rename(
                columns={f'{struct_name}_res_num': 'res_num', f'{struct_name}_res_aa': 'res_aa'})[['res_num', 'res_aa']]
            binding_pocket_df_struct['struct_name'] = pdb_name
            if i == 0:
                binding_pocket_df = binding_pocket_df_struct.copy()
            else:
                binding_pocket_df = pd.concat([binding_pocket_df, binding_pocket_df_struct])
        binding_pocket_df = binding_pocket_df.reset_index(drop=True)
        ali_index_filt = [idx - 1 for idx in list(set(ali_index_filt))]
        ali_index_filt.sort()
        print('# of positions in alignment:', len(ali_index_filt))

        # --- plot alignment of binding pocket residues only ---
        visualize_msa(self.seq_align_fpath, how='seaborn', color_scheme='Taylor', plot_msa_pos_range=None,
                      wrap_length=100, xtick_interval=5, ytick_interval=1, pos_int_to_label=5,
                      show_seq_names=True, label_residues='ref',
                      show_all_sequences=True, fontsize=10,
                      filter_by_refseq_or_idx=ali_index_filt,
                      savefig=self.seq_align_fpath.replace('.fasta', '_bindingpocket'), figsize=(20, 10))

        return binding_pocket_df, ali_index_filt


    def get_reactive_center_coords(self, df, reactive_center_target, protein_molname, ligand_molname):

        # --- get receptor coords ---
        if 'protein' in reactive_center_target and reactive_center_target['protein'] is not None:
            ## get reactive coords from protein
            target_residue = reactive_center_target['protein']
            print('target_residue:',target_residue)
            df_receptor = df.loc[df['res_num'].isin(target_residue)]
        elif 'cofactor' in reactive_center_target and reactive_center_target['cofactor'] is not None:
            ## get reactive center coords from cofactor element (not protein / not ligand, e.g. Heme)
            target_cofactor_element = reactive_center_target['cofactor']
            if isinstance(target_cofactor_element,str):
                target_cofactor_element = [target_cofactor_element]
            if target_cofactor_element[0][-1].isnumeric():
                df_receptor = df[(~df['chain_id'].isin([protein_molname, ligand_molname])) & (df['atom_name'].isin(target_cofactor_element))].copy()
            else:
                df_receptor = df[(~df['chain_id'].isin([protein_molname, ligand_molname])) & (df['element'].isin(target_cofactor_element))].copy()
        else:
            ## get reactive center from protein binding pocket centroid
            df_receptor = df[~df['chain_id'].isin([ligand_molname])].copy()
        receptor_xyz_coords = df_receptor[['x', 'y', 'z']].mean(axis=0).to_numpy()
        print('[RECEPTOR] Reactive center coords:', receptor_xyz_coords)

        # --- get ligand coords ---
        if 'ligand' in reactive_center_target and reactive_center_target['ligand'] is not None:
            ## get reactive center coords from ligand element
            target_ligand_element = reactive_center_target['ligand']
            if isinstance(target_ligand_element,str):
                target_ligand_element = [target_ligand_element]
            print('target_ligand_element:', target_ligand_element)
            if target_ligand_element[0][-1].isnumeric():
                df_ligand = df[(df['chain_id'].isin([ligand_molname])) & (df['atom_name'].isin(target_ligand_element))].copy()
            else:
                df_ligand = df[(df['chain_id'].isin([ligand_molname])) & (df['element'].isin(target_ligand_element))].copy()
        else:
            ## get reactive center from protein binding pocket centroid
            df_ligand = df[df['chain_id'].isin([ligand_molname])].copy()
        ligand_xyz_coords = df_ligand[['x','y','z']].mean(axis=0).to_numpy()
        print('[LIGAND] Reactive center coords:', ligand_xyz_coords)
        return receptor_xyz_coords, ligand_xyz_coords


    def plot_res_ligand_distances(self, struct_names, pdb_names, binding_pocket_backbone_coords_dict,
                                  binding_pocket_residues_dict, plot_fname=None, reindex_alignment=False):

        fig, ax = plt.subplots(2, 1, figsize=(20, 10))
        min_ali_idx_pos = []
        max_ali_idx_pos = []

        if reindex_alignment:
            index_to_keep = []
            for struct_name, pdb_name in zip(struct_names, pdb_names):
                index_to_keep += self.ali_df.loc[self.ali_df[f'{struct_name}_res_num'].isin(
                    binding_pocket_residues_dict[struct_name]), 'index'].tolist()
            index_to_keep = list(set(index_to_keep))
            index_to_keep.sort()
            alignment = self.ali_df[self.ali_df['index'].isin(index_to_keep)].reset_index(drop=True)
            alignment['index_new'] = list(alignment.index)
            index_col = 'index_new'
        else:
            alignment = self.ali_df.copy()
            index_col = 'index'

        for struct_name, pdb_name in zip(struct_names, pdb_names):
            binding_pocket_residues = binding_pocket_residues_dict[struct_name]
            ali_idx_struct = alignment.loc[
                alignment[f'{struct_name}_res_num'].isin(binding_pocket_residues), index_col].to_numpy()
            df_binding_pocket_backbone = binding_pocket_backbone_coords_dict[pdb_name]
            dists_res_ligand_reactive_center = df_binding_pocket_backbone[
                'dist_res_to_ligand_reactive_center'].to_numpy()
            min_dists_res_ligand = df_binding_pocket_backbone['min_dist_res_to_ligand'].to_numpy()
            if reindex_alignment:
                ali_idx_pos_to_plot = ali_idx_struct.copy()
            else:
                ali_idx_pos_to_plot = np.array(
                    [pos for pos, ali_idx in enumerate(self.ali_index_pocket) if ali_idx in ali_idx_struct])
            ax[0].plot(ali_idx_pos_to_plot, dists_res_ligand_reactive_center, marker='o', markersize=6, alpha=0.7)
            ax[0].set_title('Distance between Ligand reactive center and Residue centroid')
            ax[1].plot(ali_idx_pos_to_plot, min_dists_res_ligand, marker='o', markersize=6, alpha=0.7)
            ax[1].set_title('Minimum distance between Ligand and Residue heavy atoms')
            min_ali_idx_pos.append(ali_idx_pos_to_plot[0])
            max_ali_idx_pos.append(ali_idx_pos_to_plot[-1])

        for ax_num in range(2):
            ax[ax_num].set_xlabel('Alignment index')
            ax[ax_num].set_ylabel('Distance (Å)')
            ax[ax_num].set_xlim([min(min_ali_idx_pos), max(max_ali_idx_pos)])
            ax[ax_num].axhline(y=6, c='k', linestyle='--')
        ax[0].legend(pdb_names, bbox_to_anchor=(1.02, 0.7))
        plt.tight_layout()
        if plot_fname is not None:
            plt.savefig(f'{self.msa_dir}{plot_fname}')
        plt.show()


    def get_all_pairwise_distances(self, res_atom_coords, ligand_coords, how='min'):
        # One residue-atom coordinate (shape=(3,)) against all ligand atoms (shape=(n_lig,3)).
        ligand_coords = np.atleast_2d(np.asarray(ligand_coords, dtype=float))
        res_atom_arr = np.asarray(res_atom_coords, dtype=float)
        if res_atom_arr.ndim != 1 or res_atom_arr.shape[0] != 3:
            raise ValueError(f"Expected single residue atom coordinate with shape (3,), got {res_atom_arr.shape}.")
        all_pairwise_distances = np.linalg.norm(ligand_coords - res_atom_arr, axis=1)
        if all_pairwise_distances.size == 0:
            return np.nan
        if how == 'min':
            return round(float(np.min(all_pairwise_distances)),4)
        if how == 'mean':
            return round(float(np.mean(all_pairwise_distances)),4)
        raise ValueError(f"Unsupported how='{how}'. Use 'min' or 'mean'.")


    def calculate_residue_ligand_distances(self, struct_names, pdb_names, protein_molname,
                                           ligand_molname, dist_thres, reactive_center_target, plot_distances=True, how='min'):
        """
        Calculate atom-wise distances between protein and ligand
        """
        ligand_pocket_analysis = []
        binding_pocket_backbone_coords_dict = {}
        binding_pocket_residues_dict = {}

        # iterate through each structure
        for i, (struct_name, pdb_name) in enumerate(zip(struct_names, pdb_names)):

            # --- load CSV files for receptor and ligand coordinates ---
            struct_coords = pd.read_csv(f'{self.struct_csv_dir}{pdb_name}.csv')
            struct_coords_backbone = pd.read_csv(f'{self.struct_csv_dir}{pdb_name}_backbone.csv')
            df_receptor_dict = {
                pdb_name: struct_coords[struct_coords['chain_id']!=ligand_molname],
                f'{pdb_name}_backbone': struct_coords_backbone[struct_coords_backbone['chain_id'] != ligand_molname]
            }
            df_ligand = pd.read_csv(f'{self.struct_csv_dir}{pdb_name}_Lig{ligand_molname}.csv')
            ligand_coords = df_ligand[['x', 'y', 'z']].to_numpy()

            # --- get minimum distance between heavy atoms of ligand and each residue ---
            for pdbname_wsuffix in df_receptor_dict:
                df_receptor = df_receptor_dict[pdbname_wsuffix].copy()
                min_dists_res_ligand = []
                for atom_idx in range(len(df_receptor)):
                    res_atom_coords = df_receptor.iloc[atom_idx][['x','y','z']].to_numpy()
                    dist_res_ligand = self.get_all_pairwise_distances(res_atom_coords, ligand_coords, how=how)
                    min_dists_res_ligand.append(dist_res_ligand)
                df_receptor.loc[:, f'{how}_dist_res_to_ligand'] = min_dists_res_ligand
                # Keep in-memory receptor tables in sync with newly computed distance column.
                df_receptor_dict[pdbname_wsuffix] = df_receptor
                # update saved CSV coords file with distances
                df_receptor.to_csv(f'{self.struct_csv_dir}{pdbname_wsuffix}.csv')
                # update overall alignment dataframe with distances
                if pdbname_wsuffix.find('backbone') > -1:
                    res_num_list = df_receptor['res_num'].tolist()
                    self.ali_df.loc[self.ali_df[f'{struct_name}_res_num'].isin(res_num_list), f'{struct_name}_min_dist_res_to_ligand'] = min_dists_res_ligand

            # --- get binding pocket residues by applying threshold --- 
            df_receptor = df_receptor_dict[pdb_name]
            df_receptor_backbone = df_receptor_dict[f'{pdb_name}_backbone']
            df_bindingpocket = df_receptor[(df_receptor[f'{how}_dist_res_to_ligand']<dist_thres) & (df_receptor['chain_id']==protein_molname)].copy()
            binding_pocket_residues = list(set(df_bindingpocket['res_num'].tolist()))
            num_res_binding_pocket_ali = len(binding_pocket_residues)
            binding_pocket_residues_dict[struct_name] = binding_pocket_residues
            df_bindingpocket_backbone = df_receptor_backbone[df_receptor_backbone['res_num'].isin(binding_pocket_residues)].copy()

            # --- get reactive coordinates of receptor and ligand (requires binding pocket residues) ---
            if isinstance(reactive_center_target, list):
                reactive_center_target_struct = reactive_center_target[i]
            else:
                reactive_center_target_struct = reactive_center_target
            receptor_reactive_center_coords, ligand_reactive_center_coords = self.get_reactive_center_coords(
                pd.concat([df_bindingpocket, df_ligand], axis=0),
                reactive_center_target_struct, protein_molname, ligand_molname
            )
            
            # --- get distance between receptor residues and ligand reactive coordinates ---
            reactive_center_distance = np.linalg.norm(receptor_reactive_center_coords - ligand_reactive_center_coords)
            dists_res_ligand_reactive_center = []
            for res_num in binding_pocket_residues:
                res_atom_coords = df_bindingpocket.loc[df_bindingpocket['res_num'] == res_num, ['x', 'y', 'z']].to_numpy()
                res_centroid = np.mean(res_atom_coords, axis=0)
                dists_res_ligand_reactive_center.append(np.linalg.norm(res_centroid - ligand_reactive_center_coords))
            # update binding pocket coordinate dataframes
            df_bindingpocket_backbone['dist_res_to_ligand_reactive_center'] = dists_res_ligand_reactive_center
            df_bindingpocket_backbone = df_bindingpocket_backbone.round(3)
            df_bindingpocket_backbone.to_csv(f'{self.struct_csv_dir}{pdb_name}_backbone_bindingpocket.csv')
            binding_pocket_backbone_coords_dict[pdb_name] = df_bindingpocket_backbone
            # update overall alignment dataframe
            self.ali_df.loc[self.ali_df[f'{struct_name}_res_num'].isin(
                binding_pocket_residues), f'{struct_name}_dist_res_to_ligand_reactive_center'] = dists_res_ligand_reactive_center

            # get median stats based on residues strictly < dist_thres from ligand only
            df_bindingpocket_backbone_FILT = df_bindingpocket_backbone.loc[
                df_bindingpocket_backbone['min_dist_res_to_ligand'] < dist_thres]
            num_res_binding_pocket_filt = len(df_bindingpocket_backbone_FILT)
            median_dist_res_ligand_reactive_center = np.median(
                df_bindingpocket_backbone_FILT['dist_res_to_ligand_reactive_center'].to_numpy())
            median_min_dist_res_to_ligand = np.median(
                df_bindingpocket_backbone_FILT['min_dist_res_to_ligand'].to_numpy())

            ligand_pocket_analysis.append({
                'struct_name': pdb_name,
                'num_pocket_res_ali': num_res_binding_pocket_ali,
                f'num_pocket_res<{dist_thres}': num_res_binding_pocket_filt,
                'reactive_center_distance': reactive_center_distance,
                'median_dist_res_to_ligand_reactive_center': median_dist_res_ligand_reactive_center,
                'median_min_dist_res_to_ligand': median_min_dist_res_to_ligand
            })
        ligand_pocket_analysis = pd.DataFrame(ligand_pocket_analysis).round(3)

        if plot_distances:
            self.plot_res_ligand_distances(struct_names, pdb_names, binding_pocket_backbone_coords_dict,
                                           binding_pocket_residues_dict,
                                           plot_fname='res_ligand_distances_bindingpocket.png', reindex_alignment=True)

        return ligand_pocket_analysis, binding_pocket_backbone_coords_dict, binding_pocket_residues_dict


    def identify_target_residues(self, struct_names, pdb_names, dist_thres, plot_distances=True,
                                 binding_pocket_backbone_coords_dict=None, keep_pos_with_aa_variation_only=True):

        # save final alignment dataframe
        self.ali_df = self.ali_df.round(3)
        ali_df_fpath = self.seq_align_fpath.replace('.fasta', '_withDist.csv')
        self.ali_df.to_csv(ali_df_fpath)
        res_aa_cols = [f'{struct_name}_res_aa' for struct_name in struct_names]
        res_num_cols = [f'{struct_name}_res_num' for struct_name in struct_names]
        dist_cols = [f'{struct_name}_min_dist_res_to_ligand' for struct_name in struct_names]

        # filter to select positions where:
        # at least 1 residue is close to ligand
        # if required: aligned residues are NOT all the same amino acid
        ali_index_to_keep = []
        variation_marker_list = []
        counter = 0
        for i in range(len(self.ali_df)):
            resnum_pos = self.ali_df.iloc[i][res_num_cols].tolist()
            aa_pos = self.ali_df.iloc[i][res_aa_cols].tolist()
            dists_pos = self.ali_df.iloc[i][dist_cols].tolist()
            num_diff_aa_at_pos = len(set(aa_pos))
            if num_diff_aa_at_pos==1: variation_marker = " "
            else: variation_marker = "*"
            variation_marker_list.append(variation_marker)
            if len([d for d in dists_pos if d < dist_thres]) > 1:
                counter += 1
                index = self.ali_df.iloc[i]['index']
                ali_index_to_keep.append(index)
                print(variation_marker, counter, index, *[str(resnum) + aa for resnum, aa in zip(resnum_pos, aa_pos)], *dists_pos)
        self.ali_df['variation_marker'] = variation_marker_list

        ali_df_FILT = self.ali_df[self.ali_df['index'].isin(ali_index_to_keep)]
        if keep_pos_with_aa_variation_only:
            ali_df_FILT = ali_df_FILT[ali_df_FILT['variation_marker']=='*']
        ali_df_FILT_index = [idx - 1 for idx in ali_df_FILT['index'].tolist()]
        print(f'Filtered alignment index ({len(ali_df_FILT_index)}):', ali_df_FILT_index)
        ali_df_FILT.to_csv(ali_df_fpath.replace('.csv', '_FILT.csv'))

        # get selected binding pocket positions
        pocket_residues_annotated = {}
        for struct_name, pdb_name in zip(struct_names, pdb_names):
            res_num_list_struct = ali_df_FILT[f'{struct_name}_res_num'].tolist()
            variation_marker_list = ali_df_FILT['variation_marker'].tolist()
            pocket_residues_annotated[pdb_name] = [(res_num, variation_marker) for res_num, variation_marker in zip(res_num_list_struct,variation_marker_list) if isinstance(res_num, int)]
        print('pocket_residues_annotated:', pocket_residues_annotated)

        # --- plot alignment of filtered binding pocket residues only ---
        visualize_msa(self.seq_align_fpath, how='seaborn', color_scheme='Taylor', plot_msa_pos_range=None,
                      wrap_length=100, xtick_interval=5, ytick_interval=1, pos_int_to_label=5,
                      show_seq_names=True, label_residues='ref',
                      show_all_sequences=True, fontsize=18,
                      filter_by_refseq_or_idx=ali_df_FILT_index,
                      savefig=self.seq_align_fpath.replace('.fasta', '_bindingpocket_FILT'), figsize=(20, 10))

        if plot_distances:
            binding_pocket_residues_dict_FILT = {
                struct_name: [res for res in ali_df_FILT[f'{struct_name}_res_num'].tolist() if isinstance(res, int)] for
                struct_name in struct_names}
            binding_pocket_backbone_coords_dict_FILT = {
                pdb_name: df[df['res_num'].isin(binding_pocket_residues_dict_FILT[struct_name])].copy() for
                struct_name, (pdb_name, df) in zip(struct_names, binding_pocket_backbone_coords_dict.items())}
            self.plot_res_ligand_distances(struct_names, pdb_names, binding_pocket_backbone_coords_dict_FILT,
                                           binding_pocket_residues_dict_FILT,
                                           plot_fname='res_ligand_distances_bindingpocket_FILT.png',
                                           reindex_alignment=True)

        return ali_df_FILT, ali_df_FILT_index, pocket_residues_annotated


    def get_binding_pocket_properties(self, residues_near_ligand_df, plot_properties=False):
        """
        Get binding pocket properties independent of ligand
        """
        analyse_pocket = PocketAnalysis(self.pdb_dir, self.struct_csv_dir)
        bindingpocket_analysis = analyse_pocket(residues_near_ligand_df, plot_properties)
        return bindingpocket_analysis


    def format_sce(self, struct_names, pdb_names, ligand_molname, sce_fpath, dist_thres=None, show_res=None,
                   label_res_from_struct=[], color_range=[120, 320]):
        yasara.LoadSce(sce_fpath)
        color_list = np.linspace(color_range[0], color_range[1], num=len(struct_names))
        yasara.HideRes('protein')
        # format non-protein atoms
        yasara.StickMol('not protein')
        # color non-protein atoms by element
        yasara.ColorRes('not protein', 'Element')
        # color heme carbons orange
        yasara.ColorAtom(f'not protein and not Mol {ligand_molname} and Element C', 150)
        # color ligand carbons by cluster
        for i, (struct_name, color) in enumerate(zip(struct_names, color_list)):
            yasara.ColorAtom(f'Obj {i + 1} and Mol D and Element C', int(color))
            yasara.ColorAtom(f'Obj {i + 1} and protein and Element C', int(color))
        # color protein residues by restype
        yasara.ColorRes('protein', 'ResType')

        # show selected residues
        if dist_thres is not None:
            yasara.ShowRes(f'protein and with distance<{dist_thres} from Mol {ligand_molname}')
        if show_res is not None:
            for i, (pdb_name, resnum_variationmarker_list) in enumerate(show_res.items()):
                obj_num = i + 1
                for (res_num, variation_marker) in resnum_variationmarker_list:
                    # show residue
                    yasara.ShowRes(f'Obj {obj_num} and protein and Res {res_num}')
                    # label residue
                    if pdb_name in label_res_from_struct:
                        if variation_marker=='*':
                            label_color = 'yellow'
                        else:
                            label_color = 'white'
                        yasara.LabelRes(f'Obj {obj_num} and protein and Res {res_num}', f'{variation_marker.replace(" ","")}{res_num}', color=label_color)
        # save scene with ALL proteins overlaid
        yasara.SaveSce(sce_fpath)
        print('Saved all aligned proteins to YASARA scene:', sce_fpath)

        # save individual proteins, with residues labelled
        for i_to_show, (struct_name, pdb_name) in enumerate(zip(struct_names, pdb_names)):
            yasara.UnlabelRes('all')
            yasara.ShowObj('all')
            obj_num_to_show = i_to_show + 1
            obj_num_to_hide = [i + 1 for i in range(len(pdb_names)) if i != i_to_show]
            # toggles other proteins off
            for obj_num in obj_num_to_hide:
                yasara.SwitchObj(obj_num, 'Off')

            # formats selected residues to show and label
            yasara.HideRes(f'Obj {obj_num_to_show} and protein')
            if show_res is not None:
                resnum_variationmarker_list = show_res[pdb_name]
                for (res_num, variation_marker) in resnum_variationmarker_list:
                    res_aa = \
                    self.ali_df.loc[self.ali_df[f'{struct_name}_res_num'] == res_num, f'{struct_name}_res_aa'].iloc[0]
                    yasara.ShowRes(f'Obj {obj_num_to_show} and protein and Res {res_num}')
                    if variation_marker == '*':
                        label_color = 'yellow'
                    else:
                        label_color = 'white'
                    yasara.LabelRes(f'Obj {obj_num_to_show} and protein and Res {res_num}', f'{variation_marker.replace(" ","")}{res_num}{res_aa}', color=label_color)

            # save individual scene
            yasara.SaveSce(sce_fpath.replace('.sce', f'_{pdb_name}.sce'))
            print(f'Saved {struct_name} to YASARA scene.')

            # toggles other proteins on
            for obj_num in obj_num_to_hide:
                yasara.SwitchObj(obj_num, 'On')


    def run_pipeline(
            self,
            struct_dict,
            seq_align_fname,
            binding_pocket_residues_fname,
            analyse_binding_pocket_without_ligand,
            protein_molname='A',
            ligand_molname=None,
            dist_thres=6,
            reactive_center_target={'protein':None, 'cofactor': None, 'ligand':None},
            keep_pos_with_aa_variation_only=True,
    ):

        # get inputs
        struct_names = list(struct_dict.keys())
        pdb_names = list(struct_dict.values())
        binding_pocket_residues_fpath = self.pdb_dir + binding_pocket_residues_fname
        self.seq_align_fpath = self.msa_dir + seq_align_fname
        sce_fpath = self.sce_dir + seq_align_fname.replace('.fasta', '.sce')

        # 1. Align complexed structures and update PDB files; obtain MSA
        self.ali_df = self.align_structs(struct_names, pdb_names, seq_align_fname)

        # 2. Get binding pocket <> ligand properties
        pocket_ligand_properties = None
        if ligand_molname is not None:

            # --- Extract CSV for protein and ligand from PDB ---
            for pdb_name in pdb_names:
                self.pdb_to_csv(pdb_name, ligand_molname)

            # --- Calculate ligand-residue distances ---
            pocket_ligand_properties, binding_pocket_backbone_coords_dict, binding_pocket_residues_dict = self.calculate_residue_ligand_distances(
                struct_names, pdb_names, protein_molname, ligand_molname, dist_thres,
                reactive_center_target, plot_distances=True)
            pocket_ligand_properties.to_csv(self.pdb_dir + 'bindingpocket_wLig_analysis.csv')

            # --- Identify residues to pay attention to ---
            ## identify residues that differ
            ali_df_FILT, ali_df_FILT_index, pocket_residues_annotated = self.identify_target_residues(struct_names, pdb_names,
                                                                                                     dist_thres, plot_distances=True,
                                                                                                     binding_pocket_backbone_coords_dict=binding_pocket_backbone_coords_dict,
                                                                                                     keep_pos_with_aa_variation_only=keep_pos_with_aa_variation_only)

            # plot and save YASARA scene with all structs overlaid, and individually
            self.format_sce(struct_names, pdb_names, ligand_molname, sce_fpath, dist_thres=None,
                            show_res=pocket_residues_annotated, label_res_from_struct=[pdb_names[0]],
                            color_range=[120, 320])

        else:
            for pdb_name in pdb_names:
                self.pdb_to_csv(pdb_name)

        # 2. Get binding pocket properties (no ligand)
        pocket_properties_distal, pocket_properties_proximal = None, None
        if analyse_binding_pocket_without_ligand:
            # get distal and proximal ligands
            pocket_residues_proximal = {}
            pocket_residues_distal = {}
            for pdb_name, df_binding_pocket_backbone in binding_pocket_backbone_coords_dict.items():
                pocket_residues_proximal[pdb_name] = df_binding_pocket_backbone.loc[df_binding_pocket_backbone['dist_res_to_ligand_reactive_center'] < 6, 'res_num'].tolist()
                pocket_residues_distal[pdb_name] = df_binding_pocket_backbone.loc[df_binding_pocket_backbone['dist_res_to_ligand_reactive_center'] > 5, 'res_num'].tolist()
            # get properties of all aligned residues
            print('Obtaining distal pocket properties...')
            pocket_properties_distal, _, _ = self.get_binding_pocket_properties(pocket_residues_distal)
            pocket_properties_distal = pd.DataFrame(pocket_properties_distal).round(3)
            pocket_properties_distal.to_csv(self.pdb_dir + 'bindingpocket-distal_woLig_analysis.csv')
            # get properties of only residues close to docked ligand
            print('Obtaining proximal pocket properties...')
            pocket_properties_proximal, _, _ = self.get_binding_pocket_properties(pocket_residues_proximal)
            pocket_properties_proximal = pd.DataFrame(pocket_properties_proximal).round(3)
            pocket_properties_proximal.to_csv(self.pdb_dir + 'bindingpocket-proximal_woLig_analysis.csv')

        # 3. Combine all results
        if pocket_ligand_properties is not None and pocket_properties_distal is not None and pocket_properties_proximal is not None:
            pocket_ligand_cols = [c for c in pocket_ligand_properties.columns.tolist() if c != 'struct_name']
            pocket_cols = [c for c in pocket_properties_distal.columns.tolist() if c != 'struct_name']
            cols = ['struct_name'] + pocket_ligand_cols
            for c in pocket_cols:
                cols += [f'{c} (distal)', f'{c} (proximal)']
            res = pd.concat([
                pocket_ligand_properties, \
                pocket_properties_distal.rename(columns={c: f'{c} (distal)' for c in pocket_cols}), \
                pocket_properties_proximal.rename(columns={c: f'{c} (proximal)' for c in pocket_cols})
            ], axis=1)
            res = res[cols]
            res.to_csv(self.pdb_dir + 'bindingpocket_analysis.csv')

            yasara.Exit()


if __name__ == "__main__":
    os.chdir('../')

    # ---- user input ----
    data_folder = address_dict['PIPS2']
    data_subfolder = 'UPOs_peroxygenation_analysis/docked/REPS/'
    pdb_dir = data_folder + subfolders['pdb'] + data_subfolder
    sce_dir = data_folder + subfolders['pdb'] + data_subfolder + 'sce/'
    msa_dir = data_folder + subfolders['pdb'] + data_subfolder + 'msa/'
    struct_csv_dir = data_folder + subfolders['pdb'] + data_subfolder + 'structure_csv/'
    protein_molname = 'A'
    ligand_molname = 'D'
    dist_thres = 6
    lig_csv_suffix = f'_Lig{ligand_molname}'
    seq_align_fname = 'reps_ali.fasta'
    binding_pocket_residues_fname = 'residues_near_ligand.csv'
    struct_dict = {
        'ET096': 'ET096_S82_glide',
        'CviUPO': 'CviUPO_S82_glide',
        'CviUPO-F88L+T158A': 'CviUPO-F88L+T158A_S82_chai1_0',
        'DcaUPO': 'DcaUPO_S82_glide',
        'TE314': 'TE314_S82_chai1_0',
        'OA167': 'OA167_S82_swissdock_0',
    }
    analyse_binding_pocket_without_ligand = True
    reactive_center_target = {'protein':None, 'cofactor':'FE', 'ligand':'N'}
    keep_pos_with_aa_variation_only = True

    # perform analysis
    analyse_ligand_pocket = LigandPocketAnalysis(
        pdb_dir,
        sce_dir,
        msa_dir,
        struct_csv_dir,
        lig_csv_suffix,
    )
    analyse_ligand_pocket.run_pipeline(
        struct_dict,
        seq_align_fname,
        binding_pocket_residues_fname,
        analyse_binding_pocket_without_ligand,
        protein_molname=protein_molname,
        ligand_molname=ligand_molname,
        dist_thres=6,
        reactive_center_target=reactive_center_target,
        keep_pos_with_aa_variation_only=keep_pos_with_aa_variation_only
    )
