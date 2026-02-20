#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

from project_config.variables import address_dict, subfolders, aaList, aa2idx
from tools.encodings.encoding_variables import GEORGIEV_PARAMETERS, GEORGIEV_AA_TO_VECTOR
from utils import fetch_sequences_from_fasta

def load_sequences_csv(csv_path, sequence_col='sequence', sequence_base_col='sequence_base'):
    """
    Load mutant/base sequence columns from a CSV file.

    Args:
        csv_path: Input CSV path.
        sequence_col: Column containing mutant/target sequences.
        sequence_base_col: Optional base/wildtype sequence column.

    Returns:
        Tuple `(sequence_base_list_or_none, sequence_list)`.
    """
    df = pd.read_csv(csv_path)
    if sequence_col not in df.columns:
        raise ValueError(f"Column '{sequence_col}' not found in {csv_path}")
    if sequence_base_col in df.columns:
        sequence_base_list = df[sequence_base_col].astype(str).tolist()
    else:
        sequence_base_list = None
    sequence_list = df[sequence_col].astype(str).tolist()
    return sequence_base_list, sequence_list


def load_sequences_fasta(fasta_path):
    sequence_list, _, _ = fetch_sequences_from_fasta(fasta_path)
    return None, sequence_list


def get_max_length(sequences, max_length=None):
    if max_length is not None:
        return max_length
    return max(len(seq) for seq in sequences)


def one_hot_encode_sequence(sequence, max_length):
    one_hot = np.zeros((max_length, len(aaList)), dtype=np.float32)
    sequence = sequence.upper()
    for i, aa in enumerate(sequence[:max_length]):
        if aa in aa2idx:
            one_hot[i, aa2idx[aa]] = 1.0
    return one_hot


def georgiev_encode_sequence(sequence, max_length):
    georgiev = np.zeros((max_length, len(GEORGIEV_PARAMETERS)), dtype=np.float32)
    sequence = sequence.upper()
    for i, aa in enumerate(sequence[:max_length]):
        if aa in GEORGIEV_AA_TO_VECTOR:
            georgiev[i, :] = GEORGIEV_AA_TO_VECTOR[aa]
    return georgiev


def protein_lm_encode_sequence(sequence, max_length):
    raise NotImplementedError(
        "Protein language model encoding is not implemented yet. "
        "Add your model call in `protein_lm_encode_sequence`."
    )


ENCODER_REGISTRY = {
    'one_hot': one_hot_encode_sequence,
    'georgiev': georgiev_encode_sequence,
    'protein_lm': protein_lm_encode_sequence,
}


def encode_sequences(sequences, encoder_name, max_length=None):
    """
    Encode a list of amino-acid sequences with selected encoder backend.

    Args:
        sequences: List of sequence strings.
        encoder_name: One of keys in `ENCODER_REGISTRY`.
        max_length: Optional fixed sequence length for padding/truncation.

    Returns:
        Numpy array shaped `(n_sequences, max_length, n_features)`.
    """
    if encoder_name not in ENCODER_REGISTRY:
        raise ValueError(f"Unknown encoder '{encoder_name}'. Available: {sorted(ENCODER_REGISTRY)}")
    max_len = get_max_length(sequences, max_length=max_length)
    encode_fn = ENCODER_REGISTRY[encoder_name]
    encoded = [encode_fn(seq, max_len) for seq in sequences]
    return np.asarray(encoded, dtype=np.float32)


def build_feature_matrix(sequence_list, sequence_base_list=None, encoder_name='one_hot', max_length=None):
    """
    Build flattened feature matrices for mutant-only and base+mutant encodings.

    Args:
        sequence_list: Mutant/target sequence list.
        sequence_base_list: Optional matched base sequence list.
        encoder_name: Encoder backend name.
        max_length: Optional fixed sequence length.

    Returns:
        Tuple `(combined_flat, mutant_only_flat)` feature matrices.
    """
    seq_encoded = encode_sequences(sequence_list, encoder_name=encoder_name, max_length=max_length)
    if sequence_base_list is None:
        seq_flat = seq_encoded.reshape(seq_encoded.shape[0], -1)
        return seq_flat, seq_flat

    base_encoded = encode_sequences(sequence_base_list, encoder_name=encoder_name, max_length=max_length)
    combined_3d = np.concatenate((base_encoded, seq_encoded), axis=1)
    combined_flat = combined_3d.reshape(combined_3d.shape[0], -1)
    mutant_only_flat = seq_encoded.reshape(seq_encoded.shape[0], -1)
    return combined_flat, mutant_only_flat


def save_output(array, output_path, use_sparse=False):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if use_sparse:
        sp.save_npz(str(output_path), sp.csr_matrix(array))
    else:
        np.save(str(output_path), array)


def default_paths(data_key, data_subfolder, input_fname):
    data_folder = address_dict[data_key]
    input_path = Path(data_folder) / subfolders['expdata'] / data_subfolder / input_fname
    output_dir = Path(data_folder) / subfolders['encodings'] / data_subfolder
    return input_path, output_dir


def parse_args():
    """
    Parse CLI arguments for sequence encoding utility.

    Returns:
        Parsed argparse namespace.
    """
    parser = argparse.ArgumentParser(description='General protein sequence encoding utility.')
    parser.add_argument('--encoding', default='one_hot', choices=sorted(ENCODER_REGISTRY.keys()))
    parser.add_argument('--data-key', default='PIPS2', choices=sorted(address_dict.keys()))
    parser.add_argument('--data-subfolder', required=True)
    parser.add_argument('--input-fname', required=True)
    parser.add_argument('--output-prefix', default=None, help='Defaults to encoding name.')
    parser.add_argument('--sequence-col', default='sequence')
    parser.add_argument('--sequence-base-col', default='sequence_base')
    parser.add_argument('--input-type', default='csv', choices=['csv', 'fasta'])
    parser.add_argument('--max-length', type=int, default=None)
    parser.add_argument('--sparse', action='store_true', help='Save as sparse .npz (recommended for one-hot).')
    return parser.parse_args()


def main():
    """
    CLI entrypoint: read sequences, encode features, and save output arrays.
    """
    args = parse_args()
    input_path, output_dir = default_paths(args.data_key, args.data_subfolder, args.input_fname)
    output_prefix = args.output_prefix or args.encoding

    if args.input_type == 'csv':
        seq_base, seq = load_sequences_csv(
            str(input_path),
            sequence_col=args.sequence_col,
            sequence_base_col=args.sequence_base_col,
        )
    else:
        seq_base, seq = load_sequences_fasta(str(input_path))

    combined, mutant_only = build_feature_matrix(
        sequence_list=seq,
        sequence_base_list=seq_base,
        encoder_name=args.encoding,
        max_length=args.max_length,
    )

    use_sparse = args.sparse or args.encoding == 'one_hot'
    if use_sparse:
        combined_path = output_dir / f'{output_prefix}.npz'
        mutant_path = output_dir / f'{output_prefix}MT.npz'
    else:
        combined_path = output_dir / f'{output_prefix}.npy'
        mutant_path = output_dir / f'{output_prefix}MT.npy'

    save_output(combined, combined_path, use_sparse=use_sparse)
    save_output(mutant_only, mutant_path, use_sparse=use_sparse)

    print(f'Encoding: {args.encoding}')
    print(f'Combined shape: {combined.shape} -> {combined_path}')
    print(f'Mutant-only shape: {mutant_only.shape} -> {mutant_path}')


if __name__ == "__main__":
    main()
