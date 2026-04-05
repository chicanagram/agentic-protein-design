import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.colors import ListedColormap, BoundaryNorm


def _make_unique_names(names):
    """
    Make sequence names unique while preserving order.

    Args:
        names: Iterable of sequence identifiers.

    Returns:
        List of unique identifiers suitable for DataFrame columns.
    """
    counts = {}
    out = []
    for name in names:
        key = str(name)
        n = counts.get(key, 0)
        if n == 0:
            out.append(key)
        else:
            out.append(f"{key}__{n+1}")
        counts[key] = n + 1
    return out


def _get_color_config(color_scheme='Taylor'):
    """
    Return residue-to-color mapping and palette for supported MSA color schemes.

    Args:
        color_scheme: Name of the color scheme.

    Returns:
        Tuple `(colors, palette, cmap, norm)`.
    """
    aa_to_cmap_color_mapping = {
        'Clustal': {
            '-': 0,
            '.': 0,
            'A': 1, 'V': 1, 'L': 1, 'I': 1, 'M': 1, 'F': 1, 'W': 1, 'C': 1,
            'K': 2, 'R': 2,
            'D': 3, 'E': 3,
            'S': 4, 'T': 4, 'N': 4, 'Q': 4,
            'Y': 5, 'H': 5,
            'G': 6,
            'P': 7,
            'X': 8
        },
        'Taylor': {
            '-': 0,
            '.': 0,
            'A': 1, 'V': 1, 'L': 1, 'I': 1, 'M': 1,
            'F': 2, 'Y': 2, 'W': 2,
            'K': 3, 'R': 3, 'H': 3,
            'D': 4, 'E': 4,
            'S': 5, 'T': 5, 'N': 5, 'Q': 5,
            'C': 6,
            'G': 7,
            'P': 8,
            'X': 9
        }
    }
    palettes = {
        'Clustal': [
            "#d3d3d3", "#32CD32", "#0000FF", "#FF0000", "#00FFFF",
            "#FF00FF", "#FFA500", "#FFFF00", "#000000"
        ],
        'Taylor': [
            "#D3D3D3", "#33FF00", "#0099FF", "#FF0000", "#CC00FF",
            "#00FFFF", "#FFFF00", "#FF9900", "#996633", "#000000"
        ]
    }
    colors = aa_to_cmap_color_mapping[color_scheme]
    palette = palettes[color_scheme]
    cmap = ListedColormap(palette)
    norm = BoundaryNorm(np.arange(len(palette) + 1) - 0.5, len(palette))
    return colors, palette, cmap, norm

def get_consensus_at_position(msa_array, position=0):
    """Calculate the consensus residue at a given position in an MSA."""
    # Extract the column at the specified position
    column = list(msa_array[:,position])
    column = [x for x in column if x!='-']
    # Count frequency of residues
    residue_counts = Counter(column)
    # Identify the most frequent residue
    if len(residue_counts)>0:
        consensus_residue = max(residue_counts, key=residue_counts.get)
    else:
        consensus_residue = ''
    return consensus_residue

def get_consensus_sequence(msa_array):
    """Computes the consensus sequence for the entire MSA."""
    consensus = [get_consensus_at_position(msa_array, i) for i in range(msa_array.shape[1])]
    return consensus

def get_consensus_scores(msa_array):
    """Compute the consensus score for each position in an MSA."""
    num_sequences = msa_array.shape[0]
    sequence_length = msa_array.shape[1]
    consensus_scores = []
    for i in range(sequence_length):
        # Extract column at position i
        column = list(msa_array[:,i])
        # Count frequencies of each residue
        residue_counts = Counter(column)
        # Identify the most frequent residue
        most_common_residue, max_count = residue_counts.most_common(1)[0]
        # Compute consensus score (frequency of the most common residue)
        consensus_score = max_count / num_sequences
        consensus_scores.append(consensus_score)
    return consensus_scores

def plot_msa_seaborn(msa_fpath, color_scheme='Taylor', plot_msa_pos_range=None,
                     wrap_length=300, xtick_interval=25, ytick_interval=100, pos_int_to_label=10,
                     show_seq_names=False, label_residues=None, show_all_sequences=False, fontsize=8, filter_by_refseq_or_idx=None,
                     savefig=None, figsize=(25,20)):
    import seaborn as sns
    from Bio import AlignIO
    colors, palette, cmap, norm = _get_color_config(color_scheme)

    # Load MSA using Biopython
    alignment = AlignIO.read(msa_fpath, "fasta")
    # get sequence names
    seq_names = _make_unique_names([record.id for record in alignment])
    # Convert MSA to a NumPy array
    msa_array = np.array([list(record.seq) for record in alignment])
    msa_df = pd.DataFrame(np.transpose(msa_array), columns=seq_names)
    # Add residue numbers for each sequence
    for seq_idx, seq in enumerate(seq_names):
        resnum = 0
        resnum_list = []
        # Use positional indexing so duplicate raw FASTA headers cannot coerce a
        # column slice into a DataFrame.
        aa_list = msa_df.iloc[:, seq_idx].tolist()
        for aa in aa_list:
            if aa != '-':
                resnum += 1
                resnum_list.append(resnum)
            else:
                resnum_list.append(None)
        msa_df[f'{seq}_resnum'] = resnum_list

    # filter MSA positions by reference sequence
    if filter_by_refseq_or_idx is not None:
        print('filter_by_refseq_or_idx:', filter_by_refseq_or_idx)
        # filter by column with refseq name
        if isinstance(filter_by_refseq_or_idx, str):
            msa_df = msa_df.loc[msa_df[filter_by_refseq_or_idx]!='-', :]
            ref_seq = list(msa_df[filter_by_refseq_or_idx])
            print('Ref Seq:', ''.join(ref_seq))
        # filter by alignment indices
        elif isinstance(filter_by_refseq_or_idx, list):
            msa_df = msa_df.loc[filter_by_refseq_or_idx, :]
    msa_array = msa_df[seq_names].transpose().to_numpy()

    # label residues to annotate (i.e. consensus sequence or reference sequence)
    consensus_seq = np.array(get_consensus_sequence(msa_array))

    if label_residues == 'ref' and isinstance(filter_by_refseq_or_idx,str):
        annotate_seq = ref_seq
        diff_seq = [consensus_aa if consensus_aa!=ref_aa else '' for consensus_aa, ref_aa in zip(consensus_seq, ref_seq)]
    else:
        annotate_seq = consensus_seq
        diff_seq = ['']*len(annotate_seq)

    # get filtered range of positions to plot
    if plot_msa_pos_range is None:
        start_pos_offset = 0
    else:
        [start_res, end_res] = plot_msa_pos_range
        if end_res is None:
            end_res = msa_array.shape[1]+1
        msa_array = msa_array[:,start_res-1:end_res-1]
        annotate_seq = annotate_seq[start_res-1:end_res-1]
        diff_seq = diff_seq[start_res-1:end_res-1]
        start_pos_offset = start_res-1

    # get MSA dimensions
    msa_len = msa_array.shape[1]
    num_sequences = msa_array.shape[0]
    num_rows = int(np.ceil(msa_len / wrap_length))

    # Map residues to color codes
    default_color = colors.get('X', colors.get('-', 0))
    msa_numeric = np.vectorize(lambda aa: colors.get(aa, default_color))(msa_array)
    pos_counter_dict = {seq_num:0 for seq_num in range(len(seq_names))}

    # Plot heatmap of MSA using Seaborn
    fig, ax = plt.subplots(num_rows, 1, figsize=figsize)

    # plot MSA row by row
    for row_idx in range(num_rows):
        if num_rows==1:
            ax_row = ax
            start_pos = 0
            end_pos = msa_len
            row_len = msa_len
        else:
            ax_row = ax[row_idx]
            start_pos = row_idx*wrap_length
            end_pos = min((row_idx+1)*wrap_length, msa_len)
            row_len = end_pos-start_pos
        msa_df_row = msa_df.iloc[start_pos:end_pos, :]
        msa_array_row = msa_array[:, start_pos:end_pos]
        msa_numeric_row = msa_numeric[:,start_pos:end_pos]
        annotate_seq_row = annotate_seq[start_pos:end_pos]
        diff_seq_row = diff_seq[start_pos:end_pos]

        # plot msa segment
        sns.heatmap(msa_numeric_row, ax=ax_row, cmap=cmap, norm=norm, cbar=False, xticklabels=False, yticklabels=False)

        # add vertical lines
        for x in range(row_len):
            ax_row.axvline(x=x, linewidth=0.2, color='k')
        # add tick labels
        ax_row.set_xticks(np.arange(0, row_len, xtick_interval))
        ax_row.set_xticklabels(np.arange(start_pos+1, end_pos+1, xtick_interval)+start_pos_offset, fontsize=fontsize)

        # annotate ref or consensus sequence at the top
        if label_residues is not None:
            for res_idx, (res, diff_res) in enumerate(zip(annotate_seq_row, diff_seq_row)):
                if res!='':
                    ax_row.annotate(res, (res_idx, 0), fontsize=fontsize, c=palette[colors[res]])
                if diff_res!='':
                    ax_row.annotate(diff_res, (res_idx, -num_sequences/80), fontsize=fontsize, annotation_clip=False, c=palette[colors[diff_res]])

        if show_seq_names:
            ax_row.set_yticks(np.arange(0, num_sequences, ytick_interval)+0.5)
            ax_row.set_yticklabels(seq_names, fontsize=10)

            # annotate all sequences with positions at intervals
            if show_all_sequences:
                for seq_num, seq in enumerate(seq_names):
                    if filter_by_refseq_or_idx is None or isinstance(filter_by_refseq_or_idx, str):
                        for res_idx, res in enumerate(msa_array_row[seq_num]):
                            if res != '-':
                                pos_counter_dict[seq_num] += 1
                                pos = pos_counter_dict[seq_num]
                                if pos%pos_int_to_label==0:
                                    ax_row.annotate(str(pos)+'\n'+res, (res_idx, seq_num+0.5), fontsize=fontsize*0.75, c='k')
                                else:
                                    ax_row.annotate(''+'\n'+res, (res_idx, seq_num + 0.5), fontsize=fontsize * 0.75, c='k')
                    elif isinstance(filter_by_refseq_or_idx, list):
                        for res_idx, res in enumerate(msa_array_row[seq_num]):
                            if res != '-':
                                pos = int(msa_df_row.iloc[res_idx][f'{seq}_resnum'])
                                ax_row.annotate(str(pos) + '\n' + res, (res_idx, seq_num + 0.5), fontsize=fontsize * 0.75, c='k')
        else:
            ax_row.set_yticks(np.arange(0, num_sequences, ytick_interval))
            ax_row.set_yticklabels(np.arange(0, num_sequences, ytick_interval), fontsize=10)

    # add labels and title
    plt.suptitle("MSA Visualization", fontsize=18)
    plt.xlabel("Position", fontsize=14)
    plt.savefig(savefig, bbox_inches='tight')
    plt.show()


def plot_msa_matplotlib(msa_fpath, color_scheme='Taylor', wrap_length=300, savefig=None, figsize=(25, 20)):
    """
    Plot an MSA using only matplotlib, for environments without seaborn.

    Args:
        msa_fpath: Input aligned FASTA path.
        color_scheme: Residue coloring scheme.
        wrap_length: Width of each plotted alignment block.
        savefig: Output image path.
        figsize: Figure size.
    """
    from Bio import AlignIO

    colors, _, cmap, norm = _get_color_config(color_scheme)
    alignment = AlignIO.read(msa_fpath, "fasta")
    seq_names = _make_unique_names([record.id for record in alignment])
    msa_array = np.array([list(record.seq) for record in alignment])
    msa_len = msa_array.shape[1]
    num_sequences = msa_array.shape[0]
    num_rows = int(np.ceil(msa_len / wrap_length))
    msa_numeric = np.vectorize(lambda aa: colors.get(aa, colors.get('X', 0)))(msa_array)

    fig, ax = plt.subplots(num_rows, 1, figsize=figsize)
    axes = [ax] if num_rows == 1 else ax
    for row_idx, ax_row in enumerate(axes):
        start_pos = row_idx * wrap_length
        end_pos = min((row_idx + 1) * wrap_length, msa_len)
        msa_numeric_row = msa_numeric[:, start_pos:end_pos]
        ax_row.imshow(msa_numeric_row, aspect='auto', interpolation='nearest', cmap=cmap, norm=norm)
        ax_row.set_ylabel("Seq")
        ax_row.set_xlabel("Position")
        tick_positions = np.arange(0, end_pos - start_pos, max(1, min(25, wrap_length)))
        ax_row.set_xticks(tick_positions)
        ax_row.set_xticklabels((tick_positions + start_pos + 1).tolist(), fontsize=8)
        if num_sequences > 40:
            ax_row.set_yticks([])
        else:
            ax_row.set_yticks(np.arange(num_sequences))
            ax_row.set_yticklabels(np.arange(1, num_sequences + 1), fontsize=8)
    plt.suptitle("MSA Visualization", fontsize=18)
    plt.tight_layout()
    plt.savefig(savefig, bbox_inches='tight')
    plt.show()


def visualize_msa(msa_fpath, how='seaborn', color_scheme='Taylor', plot_msa_pos_range=None,
                  wrap_length=300, xtick_interval=25, ytick_interval=100, pos_int_to_label=10,
                  show_seq_names=False, label_residues=None, show_all_sequences=False, fontsize=8,
                  filter_by_refseq_or_idx=None, savefig=None, figsize=(25,20)):
    # get figure save name
    if savefig is None:
        savefig = msa_fpath.replace('.fasta','.png')
    else:
        savefig = f'{savefig}.png'

    # visualize MSA using Seaborn
    if how=='seaborn':
        try:
            plot_msa_seaborn(msa_fpath, color_scheme, plot_msa_pos_range,
                             wrap_length, xtick_interval, ytick_interval, pos_int_to_label,
                             show_seq_names, label_residues, show_all_sequences, fontsize, filter_by_refseq_or_idx, savefig, figsize)
        except ModuleNotFoundError as exc:
            if exc.name != 'seaborn':
                raise
            print("seaborn is not installed; falling back to matplotlib MSA visualization.")
            plot_msa_matplotlib(msa_fpath, color_scheme=color_scheme, wrap_length=wrap_length, savefig=savefig, figsize=figsize)
