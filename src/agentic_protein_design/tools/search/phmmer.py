from __future__ import annotations

import subprocess
import time
from pathlib import Path

from project_config.variables import address_dict, subfolders

def _resolve_hmmer_db_path(db_name, db_dir=""):
    base = Path(db_dir)
    candidates = [
        base / db_name / f"{db_name}.fasta",
        base / f"{db_name}.fasta",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]

def run_phmmer(query_fasta, db_name, output_file, e_thres=1e-5, incE_thres=1e-5, max_target_seqs=None, num_cpu=None, query_dir='', db_dir='', output_dir='', outfmt=0):
    """
    Run PHMMER against a local FASTA database.

    Returns:
        Path to the written PHMMER output file.
    """
    query_path = Path(query_dir) / query_fasta
    output_path = Path(output_dir) / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    db_path = _resolve_hmmer_db_path(db_name, db_dir=db_dir)
    cmd = [
        "phmmer",
        "-o", str(output_path),
        "-E", str(e_thres),
        "--incE", str(incE_thres),
        str(query_path),
        str(db_path),
    ]
    if num_cpu is not None:
        cmd[1:1] = ["--cpu", str(num_cpu)]
    print(' '.join(cmd))
    # Run PHMMER
    try:
        start = time.time()
        subprocess.run(cmd, check=True, encoding="utf-8")
        end = time.time()
        print(f"PHMMER search completed ({round((end-start)/60,3)} min). Results saved in {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running PHMMER: {e}")
    except FileNotFoundError:
        print("Error: PHMMER is not installed or not in the system PATH.")
        raise
    return output_path


if __name__ == '__main__':
    # Define input files and output file
    search_type = 'phmmer'
    query_dir = address_dict['ECOHARVEST'] + subfolders['sequences']
    output_dir = address_dict['ECOHARVEST'] + subfolders['seqsearch']
    db_dir = address_dict['databases']
    query_fasta = 'MmCAR.fasta'
    db_name = 'uniprot_trembl' # 'uniprot_sprot' # 'Pfam-A.full' # 'refProteomes'
    e_thres = 0.00001  # 0.01 #
    incE_thres = 0.0001  # 0.1 #
    max_target_seqs = None
    num_cpu = 4
    output_file = query_fasta.split('.')[0] + '_' + search_type + '_' + db_name + '_incE' + "{:.0e}".format(incE_thres) + '_E' + "{:.0e}".format(e_thres)
    # run phmmer
    run_phmmer(query_fasta, db_name, output_file, e_thres, incE_thres, max_target_seqs, num_cpu, query_dir, db_dir, output_dir)
