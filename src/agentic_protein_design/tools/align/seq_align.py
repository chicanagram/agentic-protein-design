from __future__ import annotations

import subprocess
from pathlib import Path

from agentic_protein_design.tools.utils.seq_utils import fetch_sequences_from_fasta


def _default_mafft_executable() -> Path:
    """
    Return the bundled MAFFT launcher path shipped with this repository.

    Returns:
        Absolute path to `tools/align/mafft-mac/mafft.bat`.
    """
    return (Path(__file__).resolve().parent / 'mafft-mac' / 'mafft.bat').resolve()


def run_msa(
    seq_fname,
    msa_fname,
    method,
    seq_dir,
    msa_dir,
    fmt='fasta',
    seed_ali=None,
    mafft_executable=None,
):
    """
    Run a multiple-sequence alignment command on an input FASTA file.

    Args:
        seq_fname: Input sequence FASTA filename.
        msa_fname: Output alignment FASTA filename.
        method: Alignment backend. Currently implemented: `mafft`.
        seq_dir: Directory containing `seq_fname`.
        msa_dir: Directory where `msa_fname` should be written.
        fmt: Alignment format label. Currently informational only.
        seed_ali: Optional seed alignment file path for MAFFT `--seed`.
        mafft_executable: Optional MAFFT executable path. If omitted, blank, or
            set to the placeholder string `mafft`, uses the bundled
            `tools/align/mafft-mac/mafft.bat`.

    Returns:
        Path to the written alignment file.
    """
    seq_dir = Path(seq_dir)
    msa_dir = Path(msa_dir)
    in_file = seq_dir / seq_fname
    out_file = msa_dir / msa_fname
    msa_dir.mkdir(parents=True, exist_ok=True)

    if method != 'mafft':
        raise ValueError(f"Unsupported MSA method: {method}")

    mafft = mafft_executable
    if mafft in (None, '', 'mafft'):
        mafft = _default_mafft_executable()
    mafft = str(Path(mafft).expanduser().resolve())
    print('mafft path:', mafft)
    cmd = [mafft]
    if seed_ali is not None:
        cmd.extend(['--seed', str(seed_ali)])
    cmd.append(str(in_file))
    print('Running MSA:', ' '.join(cmd), '>', out_file)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"MAFFT failed ({proc.returncode}): {proc.stderr.strip()}")
    out_file.write_text(proc.stdout, encoding='utf-8')
    return out_file


def get_mutations_on_sk_wrt_s0(seq_ali, mutations_ref_s0, reorder_seqs=None):
    '''
    # Given a sequence alignment, convert mutations
    # indexed in terms of one sequence's residue positions
    # to another sequence's residue positions
    '''
    if isinstance(seq_ali, str):
        # convert MSA to sequence tuple
        seq_ali, _, _ = fetch_sequences_from_fasta(seq_ali)

    if reorder_seqs is not None:
        seq_ali_ = [seq_ali[i] for i in reorder_seqs]
        seq_ali = seq_ali_

    seq_ref_list = []
    for i in range(len(seq_ali)):
        seq_ref_list.append(seq_ali[i].replace('-', ''))

    mutations_conversion = {mut_s0: [] for mut_s0 in mutations_ref_s0}
    for mut_s0 in mutations_ref_s0:
        print(mut_s0, '(s0)', end='')
        for k in range(1, len(seq_ali)):
            # get residue index
            res_ref_s0 = int(mut_s0[1:-1])
            idx_ref_s0 = res_ref_s0 - 1
            # get alignment position corresponding to mutation
            idx_ali = seq_ali[0][:idx_ref_s0].count('-') + idx_ref_s0
            # get position corresponding to s1
            idx_ref_sk = idx_ali - seq_ali[k][:idx_ali].count('-')
            res_ref_sk = idx_ref_sk + 1
            mut_sk = seq_ref_list[k][idx_ref_sk] + str(res_ref_sk) + mut_s0[-1]
            mutations_conversion[mut_s0].append(mut_sk)
            print(f' <> {mut_sk} (s{k})', end='')
            if k==len(seq_ali)-1:
                print()
    return mutations_conversion
