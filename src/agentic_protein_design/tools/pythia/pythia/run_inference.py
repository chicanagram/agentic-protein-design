import argparse
from masked_ddg_scan import main as masked_ddg_scan

pdb_folder = {
    'examples': '../examples/',
    'influenza-resistance': '../../../PIPS/influenza-resistance/pdb/'
    }

class args:
    
    input_dir = False # '../examples/'
    # pdb_filename = pdb_folder['influenza-resistance'] + 'NA/Oseltamivir_preOpt_NA-H1N1-Victoria1162A-5NWE.pdb' # '../examples/ET096.pdb'
    pdb_filename = pdb_folder['influenza-resistance'] + 'NA/Oseltamivir_NA-H1N1-Victoria1162A-5NWE-1_264V-275Y_postOpt.pdb'
    check_plddt = True
    plddt_cutoff = 95
    n_jobs = 2
    device = "cuda:0"

if __name__ == '__main__':
    masked_ddg_scan(args)


