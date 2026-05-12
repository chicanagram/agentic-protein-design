import os
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

# Support both:
# 1) package imports from main workflows, and
# 2) direct script execution from IDE (__main__).
try:
    from project_config.variables import (
        address_dict,
        subfolders,
        aaList,
        mapping_rev,
        kyte_doolittle_hydrophobicity_index,
        hopp_woods_polarity_index,
        aa_sidechain_volume,
        aa_polarity_mapping,
    )
except ModuleNotFoundError:
    import sys
    _ROOT = Path(__file__).resolve().parents[4]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from project_config.variables import (
        address_dict,
        subfolders,
        aaList,
        mapping_rev,
        kyte_doolittle_hydrophobicity_index,
        hopp_woods_polarity_index,
        aa_sidechain_volume,
        aa_polarity_mapping,
    )

try:
    from agentic_protein_design.tools.struct.residue_structural_annotations import (
        get_residue_secondary_structure_surface_area,
    )
except ModuleNotFoundError:
    from residue_structural_annotations import get_residue_secondary_structure_surface_area

def parse_pdb_atom_line(line: str) -> Dict[str, Optional[object]]:
    """
    Parse a single ATOM/HETATM line from a PDB file using fixed-width columns.
    Returns a dict of fields. Missing numeric fields become None.
    """
    line = line.rstrip("\n")
    padded = line + " " * (80 - len(line)) if len(line) < 80 else line

    def to_int(s: str) -> Optional[int]:
        s = s.strip()
        return int(s) if s else None

    def to_float(s: str) -> Optional[float]:
        s = s.strip()
        return float(s) if s else None

    # get residue
    res_name = padded[17:20].strip()
    res_symbol = mapping_rev[res_name] if res_name in mapping_rev else None

    # compose row_dict
    row_dict = {
        "serial": to_int(padded[6:11]),           # 7–11
        "res_num": to_int(padded[22:26]),         # 23–26
        "res_name": res_name,                     # 18–20
        "res": res_symbol,
        "atom_name": padded[12:16].strip(),       # 13–16
        "chain_id": padded[21:22].strip() or None,# 22
        "x": to_float(padded[30:38]),             # 31–38
        "y": to_float(padded[38:46]),             # 39–46
        "z": to_float(padded[46:54]),             # 47–54
        "occupancy": to_float(padded[54:60]),     # 55–60
        "temp_factor": to_float(padded[60:66]),   # 61–66
        "element": padded[76:78].strip() or None, # 77–78

    }
    # update aa properties
    if res_symbol in aaList:
        row_dict.update({
            "aa_polarity": aa_polarity_mapping[res_symbol],
            "kd_hydro": kyte_doolittle_hydrophobicity_index[res_symbol],
            "hw_polarity": hopp_woods_polarity_index[res_symbol],
            "aa_vol": aa_sidechain_volume[res_symbol],
        })

    return row_dict


def pdb_to_dataframe(pdb_path: Path | str) -> pd.DataFrame:
    """
    Parse ATOM and HETATM records from a PDB file into a DataFrame.
    """
    print(f'Processing {pdb_path}...')
    pdb_path = Path(pdb_path)
    rows: List[Dict[str, Optional[object]]] = []

    with pdb_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            rec = line[0:6].strip()
            if rec in {"ATOM", "HETATM"}:
                rows.append(parse_pdb_atom_line(line))
    df = pd.DataFrame(rows)
    df = df[df['element']!='H']

    # sec structure
    df_secondary_structure = get_residue_secondary_structure_surface_area(pdb_path, 'protein')
    df = df.merge(df_secondary_structure, on=['res_num', 'res'], how='left')

    # normalized distance to centroid

    return df


if __name__=='__main__':
    os.chdir('../../../..')
    print(os.getcwd())
    data_folder = address_dict['examples']
    data_subfolder = ''
    pdb_dir = data_folder + subfolders['pdb'] + data_subfolder
    pdb_fname = 'CviUPO_S82.pdb'
    pdb_path = pdb_dir + pdb_fname
    csv_path = pdb_dir + 'structure_csv/' + pdb_fname.replace('.pdb', '_test.csv')
    df = pdb_to_dataframe(pdb_path)
    print(df)
    df.to_csv(csv_path)
    print(f'Saved CSV to: {csv_path}')
