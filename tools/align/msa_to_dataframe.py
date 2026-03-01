import pandas as pd

from tools.utils.seq_utils import fetch_sequences_from_fasta

def convert_msa_to_dataframe(seqs, seq_names, pos_offset={}):
    """
    Build an alignment dataframe from aligned sequences.

    Args:
        seqs: List of aligned sequences (equal length, may include gaps).
        seq_names: Sequence identifiers matching `seqs`.
        pos_offset: Optional starting residue offset per sequence name.

    Returns:
        DataFrame with one row per alignment position and two columns per
        sequence: residue number and residue identity.
    """
    aln_len = len(seqs[0])
    if any(len(seq) != aln_len for seq in seqs):
        raise ValueError("Alignment length mismatch among sequences")

    res_counters = {seq_name: 0 if seq_name not in pos_offset else pos_offset[seq_name] for seq_name in seq_names}  # start from 0; increment before recording
    rows = []
    for i in range(aln_len):
        row = {"index": i+1}
        for seq, seq_name in zip(seqs, seq_names):
            aa = seq[i]
            if aa != "-":
                res_counters[seq_name] += 1
                row[f"{seq_name}_res_num"] = res_counters[seq_name]
            else:
                row[f"{seq_name}_res_num"] = ""
            row[f"{seq_name}_res_aa"] = aa
        rows.append(row)

    df_cols = ['index']
    for seq_name in seq_names:
        df_cols += [f'{seq_name}_res_num', f'{seq_name}_res_aa']
    df = pd.DataFrame(rows, columns=df_cols)
    return df

def convert_dataframe_to_msa(df):
    """
    Reconstruct aligned sequences from an MSA dataframe.

    Args:
        df: DataFrame in the format returned by `convert_msa_to_dataframe`.

    Returns:
        Tuple `(seqs, seq_names)` for the reconstructed alignment.
    """
    cols = df.columns.tolist()
    seq_names = [c.replace('_res_num', '') for c in cols if c.find('_res_num')>-1]
    print(seq_names)
    seqs = []
    for seq_name in seq_names:
        seq = ''.join(df[f'{seq_name}_res_aa'].tolist())
        seqs.append(seq)
    return seqs, seq_names


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/align/msa_to_dataframe.py <alignment.fasta>")

    msa_fpath = sys.argv[1]
    seqs, seq_names, _ = fetch_sequences_from_fasta(msa_fpath)
    df = convert_msa_to_dataframe(seqs, seq_names)
    df.to_csv(msa_fpath.replace('.fasta', '.csv'), index=False)
