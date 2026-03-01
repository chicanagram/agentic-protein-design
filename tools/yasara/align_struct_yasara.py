import os
from pathlib import Path

import numpy as np
import pandas as pd

from project_config.variables import address_dict, subfolders
from tools.align.seq_align import get_mutations_on_sk_wrt_s0, run_msa
from tools.utils.seq_utils import fetch_sequences_from_fasta
from tools.utils.struct_utils import run_tmalign
from tools.yasara import yasara


class AlignStruct:
    AA_GROUPS = {
        'hypho': (['ALA', 'ILE', 'LEU', 'MET', 'VAL', 'PHE', 'TRP', 'TYR'], 'yellow'),
        'polar': (['ASN', 'GLN', 'SER', 'THR', 'GLY', 'PRO'], 'green'),
        'posit': (['LYS', 'ARG'], 'blue'),
        'negat': (['GLU', 'ASP'], 'red'),
        'speci': (['CYS', 'HIS'], 'cyan'),
    }

    def __init__(self, pdb_dir, sce_dir, msa_dir, delete_residue_str=None, superpose_method='resnum'):
        self.pdb_dir = Path(pdb_dir)
        self.sce_dir = None if sce_dir is None else Path(sce_dir)
        self.msa_dir = None if msa_dir is None else Path(msa_dir)
        self.delete_residue_str = delete_residue_str
        self.superpose_method = superpose_method

    @staticmethod
    def _with_tag(struct_fpath, tag, suffix=None):
        path = Path(struct_fpath)
        target_suffix = path.suffix if suffix is None else suffix
        return path.with_name(f'{path.stem}{tag}{target_suffix}')

    @staticmethod
    def _csv_output_path(seq_align_fpath):
        seq_align_path = Path(seq_align_fpath)
        parent = seq_align_path.parent
        if parent.name == 'msa':
            parent = parent.parent / 'pdb'
        return parent / f'{seq_align_path.stem}.csv'

    def save_aligned_structures(self, struct_fpaths, output_sce_fpath=None, join_obj_in_pdb=False, save_indiv_aligned_structs=False):
        print('struct_fpaths:', len(struct_fpaths), struct_fpaths)
        if output_sce_fpath is not None:
            yasara.SaveSce(str(output_sce_fpath))
            print('Saved SCE output:', output_sce_fpath)

        num_obj = yasara.CountObj('All')
        if join_obj_in_pdb:
            for obj_num in range(2, num_obj + 1):
                yasara.JoinObj(obj_num, 1, center='No')

        if save_indiv_aligned_structs:
            for i in range(num_obj):
                obj_num = i + 1
                output_pdb_fpath = struct_fpaths[i]
                yasara.SavePDB(obj_num, str(output_pdb_fpath))
                print('Saved PDB output:', output_pdb_fpath)

    def check_and_color(self, residues, calist):
        num_iden = 0
        num_sim = 0
        num_iden_hypho = 0
        num_sim_hypho = 0

        for j in range(residues):
            atom1 = calist[j * 2]
            atom2 = calist[j * 2 + 1]
            k = yasara.NameRes(f'Atom {atom1}')[0]
            l = yasara.NameRes(f'Atom {atom2}')[0]
            for aagroup_type, (aalist_group, aagroup_color) in self.AA_GROUPS.items():
                if k in aalist_group and l in aalist_group:
                    num_sim += 1
                    if aagroup_type == 'hypho':
                        num_sim_hypho += 1
                    yasara.ColorRes(f'Atom {atom1} or Atom {atom2}', aagroup_color)
                    if k == l:
                        num_iden += 1
                        if aagroup_type == 'hypho':
                            num_iden_hypho += 1
                    break

        return num_iden, num_iden_hypho, num_sim, num_sim_hypho

    def _collect_superpose_positions_by_resnum(self, obj_num, resnum_list_ref, resnum_list):
        pos_ref_ali = []
        pos_target_ali = []
        for resnum_ref, resnum in zip(resnum_list_ref, resnum_list):
            pos_ref = yasara.PosRes(f'Obj 1 and Protein and Res {resnum_ref}')
            pos_target = yasara.PosRes(f'Obj {obj_num} and Protein and Res {resnum}')
            pos_ref_ali.append(pos_ref)
            pos_target_ali.append(pos_target)
        return pos_ref_ali, pos_target_ali

    def _collect_superpose_positions_by_alignment(self, obj_num, resnum_list_ref, resnum_list, ali_seqs_template):
        residx_ref = 0
        residx = 0
        pos_ref_ali = []
        pos_target_ali = []
        for res_ref, res_target in zip(ali_seqs_template[0], ali_seqs_template[1]):
            pos_ref, pos_target = [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]
            if res_ref != '-':
                residx_ref += 1
                if residx_ref - 1 < len(resnum_list_ref):
                    resnum_ref = resnum_list_ref[residx_ref - 1]
                    pos_ref = yasara.PosRes(f'Obj 1 and Protein and Res {resnum_ref}')
            if res_target != '-':
                residx += 1
                if residx - 1 < len(resnum_list):
                    resnum = resnum_list[residx - 1]
                    pos_target = yasara.PosRes(f'Obj {obj_num} and Protein and Res {resnum}')
            pos_ref_ali.append(pos_ref)
            pos_target_ali.append(pos_target)
        return pos_ref_ali, pos_target_ali

    def _compute_superposed_rmsd(self, obj_num, pos_ref_ali, pos_target_ali):
        pos_ref_ali = np.array(pos_ref_ali)
        pos_target_ali = np.array(pos_target_ali)
        try:
            rmsd_sup_byres = np.sqrt(np.sum((pos_ref_ali - pos_target_ali) ** 2, axis=1))
            return round(np.nanmean(rmsd_sup_byres), 2)
        except Exception as exc:
            print(f'Failed to compute superposed RMSD for Obj {obj_num}: {exc}')
            return None

    def yasara_align_structures(
        self,
        struct_fpaths,
        seq_align_fpath,
        output_sce_fpath,
        join_obj_in_pdb=False,
        save_indiv_aligned_structs=False,
        delete_not_protein=False,
    ):
        struct_fpaths = [Path(f) for f in struct_fpaths]

        yasara.info.mode = 'txt'
        yasara.Console('off')
        yasara.FormatRes('RESName')

        temp_struct_fpaths = []
        try:
            for i, struct_fpath in enumerate(struct_fpaths):
                yasara.LoadPDB(str(struct_fpath))
                yasara.ColorObj(i + 1, 'magenta')

                if delete_not_protein:
                    yasara.DelWater()
                    yasara.DelRes('not Protein')

                if self.delete_residue_str is not None:
                    if isinstance(self.delete_residue_str, str):
                        del_target = self.delete_residue_str
                    elif isinstance(self.delete_residue_str, list):
                        del_target = self.delete_residue_str[i]
                    else:
                        del_target = None
                    if del_target is not None:
                        yasara.DelRes(f'Obj {i + 1} and {del_target}')
                        print(f'Deleted selected residues for Obj {i + 1}:', del_target)

                temp_struct_fpath = self._with_tag(struct_fpath, '_TEMP')
                temp_struct_fpaths.append(temp_struct_fpath)
                yasara.SavePDB(f'Obj {i + 1}', str(temp_struct_fpath))

            obj_ref = struct_fpaths[0].name
            num_res_ref = yasara.CountRes('Obj 1 and Protein')
            resnum_list_ref = yasara.ListRes('Obj 1 and Protein', format='RESNUM')
            print(f'Ref Object: {obj_ref} ({num_res_ref} residues)', '\n')

            for obj_num in range(2, len(struct_fpaths) + 1):
                struct_fpath = struct_fpaths[obj_num - 1]

                if delete_not_protein:
                    tm_res = round(run_tmalign(str(temp_struct_fpaths[0]), str(temp_struct_fpaths[obj_num - 1])), 3)
                else:
                    tm_res = None

                res = yasara.AlignObj(f'{obj_num} and Protein', '1 and Protein', method='MUSTANGPP', results=4)
                rmsd_ali_residues, _, num_ali_residues = res[0], res[1], res[2]
                pairwise_ali_fpath = self._with_tag(struct_fpath, '_ALI', '.fasta')
                try:
                    yasara.SaveAli(obj_num, 1, method='Structure', filename=str(pairwise_ali_fpath), format='FASTA')
                    ali_seqs, _, _ = fetch_sequences_from_fasta(pairwise_ali_fpath)
                finally:
                    if pairwise_ali_fpath.exists():
                        pairwise_ali_fpath.unlink()

                if obj_num == 3:
                    ali_seqs_TEMPLATE = ali_seqs

                if obj_num < 3:
                    rmsd_sup = 0
                else:
                    resnum_list = yasara.ListRes(f'Obj {obj_num} and Protein', format='RESNUM')
                    if self.superpose_method == 'resnum':
                        pos_ref_ali, pos_target_ali = self._collect_superpose_positions_by_resnum(
                            obj_num,
                            resnum_list_ref,
                            resnum_list,
                        )
                    elif self.superpose_method == 'struct':
                        pos_ref_ali, pos_target_ali = self._collect_superpose_positions_by_alignment(
                            obj_num,
                            resnum_list_ref,
                            resnum_list,
                            ali_seqs_TEMPLATE,
                        )
                    else:
                        pos_ref_ali, pos_target_ali = [], []

                    rmsd_sup = self._compute_superposed_rmsd(obj_num, pos_ref_ali, pos_target_ali)

                calist = res[3:]
                obj = struct_fpath.name
                num_res = yasara.CountRes(f'Obj {obj_num} and Protein')
                percent_ali_res = round(num_ali_residues / num_res * 100, 1)
                print(f'{obj} ({num_res} residues)')
                print('TM-align score:', tm_res)
                print('RMSD (superposed residues):', rmsd_sup)
                print('RMSD (aligned residues):', round(rmsd_ali_residues, 2))
                print(f'# of aligned residues: {num_ali_residues}/{num_res} ({percent_ali_res}%)')

                num_iden, num_iden_hypho, num_sim, num_sim_hypho = self.check_and_color(num_ali_residues, calist)

                print(f'[IDENTICAL] all: {num_iden} ({100 * num_iden / num_ali_residues:.1f}%); hydrophobic: {num_iden_hypho} ({100 * num_iden_hypho / num_ali_residues:.1f}%); non-hydrophobic: {num_iden - num_iden_hypho} ({100 * (num_iden - num_iden_hypho) / num_ali_residues:.1f}%)')
                print(f'[SIMILAR] all: {num_sim} ({100 * num_sim / num_ali_residues:.1f}%); hydrophobic: {num_sim_hypho} ({100 * num_sim_hypho / num_ali_residues:.1f}%); non-hydrophobic: {num_sim - num_sim_hypho} ({100 * (num_sim - num_sim_hypho) / num_ali_residues:.1f}%)')
                print()

            if seq_align_fpath is not None:
                yasara.SaveAli('!1', '1', filename=str(seq_align_fpath), format='FASTA')

            self.save_aligned_structures(struct_fpaths, output_sce_fpath, join_obj_in_pdb, save_indiv_aligned_structs)
        finally:
            for temp_struct_fpath in temp_struct_fpaths:
                if temp_struct_fpath.exists():
                    temp_struct_fpath.unlink()

    def parse_aligned_struct_info(self, seq_align_fpath, struct_fpaths, csv_fpath):
        seqs_aligned, _, _ = fetch_sequences_from_fasta(seq_align_fpath)
        pdbs_as_string_byresidue = []
        for i, struct_fpath_unaligned in enumerate(struct_fpaths):
            other_struct_fpaths = [struct_fpaths[k] for k in range(len(struct_fpaths)) if i != k]
            other_structs_str = '-'.join([Path(f).stem for f in other_struct_fpaths])
            aligned_pdb_fpath = self._with_tag(struct_fpath_unaligned, f'_aligned_{other_structs_str}')
            with open(aligned_pdb_fpath, 'r') as f:
                pdb_string = f.read()
                pdb_string_list = [
                    line for line in pdb_string.split('\n')
                    if (line[:4] == 'ATOM' or (line[:6] == 'HETATM' and line.find('HIP') > -1) or line[:3] == 'TER')
                ]
                pdb_as_string_byresidue = {}
                for line in pdb_string_list:
                    line_list = ' '.join(line.split()).split(' ')
                    if line_list[0] == 'ATOM' or (line_list[0] == 'HETATM' and line_list[3] in ['HIP']):
                        res_num = int(line_list[5])
                    elif line_list[0] == 'TER':
                        res_num = int(line_list[4])
                    if res_num not in pdb_as_string_byresidue:
                        pdb_as_string_byresidue[res_num] = []
                    pdb_as_string_byresidue[res_num].append(line)

            for res_num, pdb_string_list_res in pdb_as_string_byresidue.items():
                pdb_as_string_byresidue[res_num] = '\n'.join(pdb_string_list_res)

            pdbs_as_string_byresidue.append(pdb_as_string_byresidue)

        df = pd.DataFrame()
        for i, (seq_ali, pdb_as_string_byresidue) in enumerate(zip(seqs_aligned, pdbs_as_string_byresidue)):
            seq_nogaps = seq_ali.replace('-', '')
            pos_list = list(pdb_as_string_byresidue.keys())
            pos_list_ali = []
            pos_list.sort()
            if pos_list and len(seq_nogaps) != len(pos_list):
                print(f'Warning: sequence length {len(seq_nogaps)} does not match residue count {len(pos_list)} for seq_{i}.')
            pdb_str_byresidue = []
            pos_idx = 0
            for aa in seq_ali:
                if aa != '-':
                    pos = pos_list[pos_idx]
                    pos_list_ali.append(int(pos))
                    pdb_str_byresidue.append(pdb_as_string_byresidue[pos])
                    pos_idx += 1
                else:
                    pos_list_ali.append(-1)
                    pdb_str_byresidue.append('')
            df[f'seq_{i}'] = list(seq_ali)
            df[f'pos_{i}'] = pos_list_ali
            df[f'pdb_by_residue_{i}'] = pdb_str_byresidue
        df.to_csv(csv_fpath)
        return df

    def run_pipeline(
        self,
        struct_names,
        seq_align_fname,
        run_structure_alignment=True,
        parse_seq_struct_alignments=False,
        save_sce=False,
        join_obj_in_pdb=False,
        save_indiv_aligned_structs=False,
        delete_not_protein=False,
    ):
        struct_fpaths = [self.pdb_dir / f'{f}.pdb' for f in struct_names]
        seq_align_fpath = None
        if self.msa_dir is not None and seq_align_fname is not None:
            seq_align_fpath = self.msa_dir / seq_align_fname

        output_sce_fpath = None
        if save_sce and self.sce_dir is not None and seq_align_fname is not None:
            output_sce_fpath = self.sce_dir / Path(seq_align_fname).with_suffix('.sce')

        if run_structure_alignment:
            self.yasara_align_structures(
                struct_fpaths,
                seq_align_fpath,
                output_sce_fpath,
                join_obj_in_pdb,
                save_indiv_aligned_structs,
                delete_not_protein,
            )

        if parse_seq_struct_alignments:
            if seq_align_fpath is None:
                raise ValueError('parse_seq_struct_alignments requires both msa_dir and seq_align_fname.')
            csv_fpath = self._csv_output_path(seq_align_fpath)
            return self.parse_aligned_struct_info(seq_align_fpath, struct_fpaths, csv_fpath)

        return None

    def use_seed_alignment_to_get_msa(self, seq_fname, output_msa_fpath, seq_align_fpath, seq_dir, msa_dir):
        run_msa(seq_fname, output_msa_fpath, 'mafft', seq_dir, msa_dir, fmt='fasta', seed_ali=seq_align_fpath)


if __name__ == '__main__':
    repo_root = Path(__file__).resolve().parents[2]
    os.chdir(repo_root)
    print('CWD:', os.getcwd())

    root_key = 'example'
    user_inputs = {
        'data_subfolder': '',
        'use_msa_dir': False,
        'seq_align_fname': 'UPOs_peroxygenation.fasta',
        'run_structure_alignment': True,
        'save_sce': False,
        'join_obj_in_pdb': False,
        'save_indiv_aligned_structs': True,
        'parse_seq_struct_alignments': False,
        'delete_not_protein': False,
        'struct_base': 'OA167',
        'struct_name_ref': 'OA167_S82_swissdock_0',
        'delete_residue_str': None,
        'superpose_method': 'struct',
        'mutations_ref_s0': None,  # e.g. ['F88A', 'T157A']
        'reorder_seqs': None,  # e.g. [2, 0, 1]
    }

    data_folder = (repo_root / address_dict[root_key]).resolve()
    data_subfolder = Path(str(user_inputs.get('data_subfolder', '')).strip())
    pdb_dir = data_folder / subfolders['pdb'] / data_subfolder
    sce_dir = data_folder / subfolders['sce'] / data_subfolder
    seq_dir = data_folder / subfolders['sequences'] / data_subfolder
    msa_dir = data_folder / subfolders['msa'] / data_subfolder if bool(user_inputs.get('use_msa_dir', False)) else None
    seq_align_fname = str(user_inputs.get('seq_align_fname', '')).strip() or None

    struct_base = str(user_inputs.get('struct_base', '')).strip()
    struct_name_ref = str(user_inputs.get('struct_name_ref', '')).strip() or f'{struct_base}_S82_swissdock_0'
    struct_names = [struct_name_ref] + [
        f.stem for f in pdb_dir.iterdir()
        if (f.suffix == '.pdb' and f.stem != struct_name_ref and struct_base in f.stem)
    ]

    print(struct_names)
    align_struct = AlignStruct(
        pdb_dir,
        sce_dir,
        msa_dir,
        user_inputs.get('delete_residue_str'),
        str(user_inputs.get('superpose_method', 'resnum')),
    )

    df = align_struct.run_pipeline(
        struct_names,
        seq_align_fname,
        bool(user_inputs.get('run_structure_alignment', True)),
        bool(user_inputs.get('parse_seq_struct_alignments', False)),
        bool(user_inputs.get('save_sce', False)),
        bool(user_inputs.get('join_obj_in_pdb', False)),
        bool(user_inputs.get('save_indiv_aligned_structs', False)),
        bool(user_inputs.get('delete_not_protein', False)),
    )

    mutations_ref_s0 = user_inputs.get('mutations_ref_s0')
    reorder_seqs = user_inputs.get('reorder_seqs')
    if mutations_ref_s0 is not None:
        if msa_dir is None:
            raise ValueError('mutations_ref_s0 requires msa_dir to be set.')
        seq_align_fpath = msa_dir / seq_align_fname
        mutations_conversion = get_mutations_on_sk_wrt_s0(seq_align_fpath, mutations_ref_s0, reorder_seqs)
