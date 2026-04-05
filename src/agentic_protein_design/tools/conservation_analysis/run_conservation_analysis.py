import os
import numpy as np
import pandas as pd
from project_config.variables import address_dict, subfolders, aaList
from agentic_protein_design.tools.utils.seq_utils import fetch_sequences_from_fasta, write_sequence_to_fasta, get_ref_seq_idxs_aa_from_msa
from agentic_protein_design.tools.utils.plot_utils import plot_variant_heatmap

def compute_entropy(probs_matrix):
    """
    Computes the entropy for each position in the given probability matrix.
    """
    from scipy.stats import entropy

    # Initialize an empty list to store the entropy values
    entropy_values = []

    # Iterate over the columns of probs_matrix
    for i in range(probs_matrix.shape[1]):
        # Compute the entropy for the probabilities at the current position
        H = entropy(probs_matrix[:, i], base=2)
        entropy_values.append(H)

    # Convert entropy_values to a numpy array for convenience
    entropy_values = np.array(entropy_values)
    return entropy_values


def compute_conservation(msa_fname, analyses_to_run, data_folder, msa_subfolder, conservation_analysis_subfolder, save_csv=True, ref_seq_name_list=[], ref_seq_idxs_list=[], ref_seq_list=[], seq_offset=0):

    if save_csv:
        csv_fpath_list = []
    else:
        csv_fpath_list = None

    if 'ShanEntropy' in analyses_to_run:
        calc_name = 'ShanEntropy'
        # run from python file
        from agentic_protein_design.tools.conservation_analysis import alfa2cons
        csv = alfa2cons.main(
            args={
                'data_folder': data_folder,
                'msa_subfolder': msa_subfolder,
                'conservation_analysis_subfolder': conservation_analysis_subfolder,
                'msa_fname': msa_fname,
            }
        )
        if save_csv:
            csv.to_csv(f'{data_folder}{conservation_analysis_subfolder}{msa_fname}_{calc_name}.csv', index=False)

        print(f'Completed analysis using {calc_name}.')

        # filter ShanEntropy results to leave just ref sequence positions
        if len(ref_seq_idxs_list)>0:
            # initialize excel writer
            csv_fpath = f'{data_folder}{conservation_analysis_subfolder}{msa_fname}_{calc_name}_selected'
            # iterate through ref sequences to get individual filtered dataframes
            for ref_seq_name, ref_seq_idxs, ref_seq in zip(ref_seq_name_list, ref_seq_idxs_list, ref_seq_list):
                csv_filt = csv[csv['Position'].isin(ref_seq_idxs)].copy()
                ref_seq_parsed = list(ref_seq) if ref_seq is not None else None
                if ref_seq_parsed is not None:
                    csv_filt['AA'] = ref_seq_parsed
                csv_filt['RealPos'] = list(np.arange(len(ref_seq_parsed)) + 1 + seq_offset)
                csv_filt = csv_filt.rename(columns={'Position': 'PositionMSA'})
                csv_filt_cols = csv_filt.columns.tolist()
                additional_cols = [c for c in csv_filt_cols if c not in ['AA', 'RealPos', 'PositionMSA', 'shanID', 'shanMS']]
                csv_filt = csv_filt[[col for col in ['AA', 'RealPos', 'PositionMSA', 'shanID', 'shanMS']+additional_cols]]
                # write dataframe to file
                if save_csv:
                    if len(ref_seq_name_list) > 1:
                        fsuffix = '_' + ref_seq_name
                    else:
                        fsuffix = ''
                    csv_fpath_ShanEntropy = csv_fpath + fsuffix + '.csv'
                    csv_filt.to_csv(csv_fpath_ShanEntropy)
                    csv_fpath_list.append(csv_fpath_ShanEntropy)

    if 'sift' in analyses_to_run:
        from agentic_protein_design.tools.conservation_analysis.sift import access_sift_webserver
        calc_name = 'sift'
        msa_path = f'{data_folder}{msa_subfolder}/{msa_fname}'
        msa_path = os.path.abspath(msa_path)
        # parse MSA to get sequences and names
        print('msa_path:', msa_path)
        print('cwd:', os.getcwd())
        msa_seqs, msa_names, _ = fetch_sequences_from_fasta(msa_path)

        # iterate through reference sequences to generate individual SIFT analyses
        csv_fpath = f'{data_folder}{conservation_analysis_subfolder}/{msa_fname.replace(".fasta","")}_{calc_name}_selected'
        for i, (ref_seq_name, ref_seq) in enumerate(zip(ref_seq_name_list, ref_seq_list)):
            print(i, ref_seq_name)
            msa_idx = msa_names.index(ref_seq_name)
            msa_names_rearranged = [msa_names[msa_idx]] + msa_names[:msa_idx] + msa_names[msa_idx+1:]
            msa_seqs_rearranged = [msa_seqs[msa_idx]] + msa_seqs[:msa_idx] + msa_seqs[msa_idx+1:]
            msa_path_rearranged = f'{data_folder}{msa_subfolder}/sift_upload.fasta'
            write_sequence_to_fasta(msa_seqs_rearranged, msa_names_rearranged, 'sift_upload.fasta', f'{data_folder}{msa_subfolder}/')
            sift_out_fpath = f'{data_folder}{conservation_analysis_subfolder}/{msa_fname.replace(".fasta", "")}_sift_{ref_seq_name}.csv'
            csv = access_sift_webserver(
                msa_path_rearranged,
                sift_out_fpath
            )
            # get probabilities pre-normalization
            probs_matrix_norm = np.transpose(csv.iloc[:, -20:].to_numpy()).astype(float)
            score_cols = csv.columns[-20:]
            csv[score_cols] = csv[score_cols].apply(pd.to_numeric, errors="coerce")
            prob_col = csv['prob'].to_numpy()
            probs_matrix = probs_matrix_norm * prob_col
            # get average sift score for each residue
            probs_mean = np.round(np.mean(probs_matrix_norm, axis=0),4)
            csv.insert(2, 'sift_avg', list(probs_mean))
            # calculate entropy for each position
            ent = np.round(compute_entropy(probs_matrix),4)
            csv.insert(2, 'entropy', list(ent))
            # write dataframe to file
            if save_csv:
                csv = csv.rename(columns={'pos': 'RealPos', 'wt': 'AA'})
                # add sequence offset if needed
                csv['RealPos'] = csv['RealPos'] + seq_offset
                if len(ref_seq_name_list)>1:
                    fsuffix = '_'+ref_seq_name
                else:
                    fsuffix = ''
                csv_fpath_sift = csv_fpath+fsuffix+'.csv'
                csv.to_csv(csv_fpath_sift)
                csv_fpath_list.append(csv_fpath_sift)
            os.remove(msa_path_rearranged)
            os.remove(f'{data_folder}{conservation_analysis_subfolder}/{msa_fname.replace(".fasta","")}_sift_{ref_seq_name}.csv')

            # plot variant heatmap
            savefig = f'{data_folder}{conservation_analysis_subfolder}/{msa_fname.replace(".fasta","")}_sift_{ref_seq_name}.png'
            figtitle = 'SIFT scores'
            plot_variant_heatmap(probs_matrix_norm, ref_seq, N_res_per_heatmap_row=100, aa_list=aaList, seq_name=ref_seq_name, savefig=savefig, figtitle=figtitle)

        print(f'Completed analysis using {calc_name}.')

    return csv_fpath_list


def main():
    data_folder = address_dict['ECOHARVEST'] # address_dict['PIPS2']
    data_subfolder = 'CARs' # 'UPO_batch1'
    conservation_analysis_subfolder = subfolders['conservation_analysis'] + data_subfolder + '/'
    msa_subfolder = subfolders['msa'] + data_subfolder + '/'
    sequences_subfolder = subfolders['sequences'] + data_subfolder + '/'
    msa_fname = 'MpCAR-A_openprotein_aligned_subset' # 'NiCAR-A_openprotein_aligned_subset' # 'RML-mature_blastp_nr_E1e-05_mafft'
    msa_path = os.path.abspath(f'{data_folder}{msa_subfolder}{msa_fname}.fasta')
    target_seq_fname = 'MpCAR-A.fasta' # 'NiCAR-A.fasta' # 'RML-mature.fasta' # 'RML-propeptide-mature.fasta'
    target_seq_fpath = f'{data_folder}{sequences_subfolder}{target_seq_fname}'
    analyses_to_run = ['ShanEntropy', 'sift']#  ['ShanEntropy_ProDy', 'ShanEntropy', 'sift'] # ['ShanEntropy', 'sift']
    save_csv = True
    seq_offset = 0 # 4 #

    # get ref sequence list
    _, ref_seq_name_list, _ = fetch_sequences_from_fasta(target_seq_fpath)
    ref_seq_idxs_list = []
    print(len(ref_seq_name_list), ref_seq_name_list)
    # get indices of aligned residues in MSA
    if len(ref_seq_name_list) > 0 and len(ref_seq_idxs_list) == 0:
        ref_seq_name_list, ref_seq_list, ref_seq_idxs_list = get_ref_seq_idxs_aa_from_msa(msa_path, ref_seq_name_list)
        print(len(ref_seq_name_list), ref_seq_name_list)
        print(ref_seq_list)
    else:
        ref_seq_name_list = ['REF'] # to modify
        ref_seq_idxs_list = [[1, 3, 5, 7, 8, 17, 21, 22, 23, 26, 28, 29, 35, 43, 44, 46, 49, 50, 51, 54, 61, 62, 63, 64, 74, 78, 81, 88, 91, 94, 98, 102, 106, 107, 109, 113, 115, 117, 119, 120, 127, 129, 132, 133, 134, 135, 139, 144, 147, 149, 150, 151, 152, 154, 155, 156, 157, 158, 160, 163, 164, 166, 167, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 372, 373, 375, 376, 378, 379, 381, 404, 406, 407, 409, 412, 413, 420, 424, 425, 427, 429, 430, 436, 438, 459, 462, 467, 472, 477, 479, 481, 484, 485, 519, 523, 525, 526, 531, 534, 535, 536, 537, 540, 542, 545, 548, 551, 552, 553, 555, 556, 558, 559, 561, 563, 565, 566, 567, 569, 570, 571, 572, 576, 577, 579, 584, 591, 593, 594, 595, 596, 597, 598, 599, 600, 601, 603, 604, 605, 608, 610, 617, 624, 625, 626, 631, 632, 633, 634, 636, 638, 639]]
        ref_seq_list = ['AAISATAQSENKKYGNPKPTTTQNQQWYSTSSFASYNERPVVANGQSNQSSYTPQPGLRPTDLVPAAAAIEPTSGRVLMWSSYRNDAEGSPGGITLTSSWDPSTGIVSDRTVTVTKHDMFCPGISMDGNGQIVVTGGWDAKKTSLYDSSSDSWIPGPDMQVARGYQSSATMSDGRVFTIGGSFSGGVFEKNGEVYSPSSKTWTSLPNAKVNPMLTADKQGLYMSDNHAWLFGWKKGSVFQAGPSTAMNWYYTSGSGDVKSAGKQSRGAPADTDDTNGTSNVFYARISTVEDYKTFAQNYDSNLTKRTQSKVGRTSDSSTKASYGANPTLTNNGGNSSFQSSYNSAVASTRTQ']

    # calculate entropies
    compute_conservation(msa_fname, analyses_to_run, data_folder, msa_subfolder, conservation_analysis_subfolder, save_csv, ref_seq_name_list, ref_seq_idxs_list, ref_seq_list, seq_offset)

if __name__ == "__main__":
    main()