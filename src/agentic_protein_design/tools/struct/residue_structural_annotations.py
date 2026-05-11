from __future__ import annotations
import os
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
from Bio.PDB import PDBParser, PDBIO, Select, is_aa
from typing import Dict, Literal
from project_config.variables import address_dict, subfolders

dssp_property_names = [
    'res_num',
    'res',
    'secondary_structure',
    # {H,B,E,G,I,P,T,S} H = α-helix; B = residue in isolated β-bridge; E = extended strand, participates in β ladder; G = 310-helix; I = π-helix; P = κ-helix (poly-proline II helix); T = hydrogen-bonded turn; S = bend
    'relative ASA',  # relative accessible solvent area
    'phi',  # peptide backbone torsion angle phi
    'psi',  # peptide backbone torsion angle psi
    'NH_O_1_relidx',  # relative index of H-bond 1 (between N-H group of this residue with O of another residue)
    'NH_O_1_energy',  # energy of H-bond 1 (between N-H group of this residue with O of another residue)
    'O_NH_1_relidx',  # relative index of H-bond 1 (between O group of this residue with N-H of another residue)
    'O_NH_1_energy',  # energy of H-bond 1 (between O group of this residue with N-H of another residue)
    'NH_O_2_relidx',  # relative index of H-bond 2 (between N-H group of this residue with O of another residue)
    'NH_O_2_energy',  # energy of H-bond 2 (between N-H group of this residue with O of another residue)
    'O_NH_2_relidx',  # relative index of H-bond 2 (between O group of this residue with N-H of another residue)
    'O_NH_2_energy'  # energy of H-bond 2 (between O group of this residue with N-H of another residue)
]

dssp_secondary_structure_shortform = {
    'H': 'α-helix',
    'B': 'residue in isolated β-bridge',
    'E': 'extended strand, participates in β ladder',
    'G': '310-helix',
    'I': 'π-helix',
    'P': 'κ-helix (poly-proline II helix)',
    'T': 'hydrogen-bonded turn',
    'S': 'bend',
    'C': 'coil',
    '-': 'loop/coil'
}

def compute_index_summary(
    df_residues: pd.DataFrame,
    value_col: Literal["kd_hydro", "hw_polarity"],
    weight_mode: Literal["mean", "weighted"] = "mean",
    dist_col: str = "dist_to_centroid",
    eps: float = 1e-6,
) -> float:
    """
    Compute either an unweighted mean or a distance-weighted mean for a polarity/hydropathy index.

    Parameters
    ----------
    df_residues : pd.DataFrame
        Must contain `value_col` and `dist_col`.
    value_col : {"kd_hydro", "hw_polarity"}
        Column containing numeric index values per residue.
    weight_mode : {"mean", "weighted"}
        "mean" -> simple mean of value_col
        "weighted" -> weights = 1 / (dist_to_centroid + eps)
    dist_col : str
        Column with distance-to-centroid values (smaller means closer to centroid).
    eps : float
        Small constant to avoid divide-by-zero.

    Returns
    -------
    float
        Summary value (NaNs are ignored).
    """
    if value_col not in df_residues.columns:
        raise KeyError(f"Missing required column: {value_col}")
    if weight_mode == "weighted" and dist_col not in df_residues.columns:
        raise KeyError(f"Missing required column: {dist_col}")

    vals = pd.to_numeric(df_residues[value_col], errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(vals)

    if not mask.any():
        return float("nan")

    if weight_mode == "mean":
        return float(np.nanmean(vals))

    # weighted
    d = pd.to_numeric(df_residues.loc[:, dist_col], errors="coerce").to_numpy(dtype=float)
    w = 1.0 / (d + eps)
    w[~np.isfinite(w)] = np.nan

    # Only keep rows where both value and weight are finite
    m = mask & np.isfinite(w)
    if not m.any():
        return float("nan")

    return float(np.average(vals[m], weights=w[m]))

def get_residue_polarity(
    df_residues: pd.DataFrame,
    *,
    aa_col: str = "res",
    aa_polarity_col: str = "aa_polarity",
    dist_col: str = "dist_to_centroid",
    kd_col: str = "kd_hydro",
    hw_col: str = "hw_polarity",
    eps: float = 1e-6,
) -> Dict[str, float]:
    """
    Compute a compact "pocket polarity report" with 6 metrics:
      1) KD_mean
      2) KD_weighted (1/(dist+eps))
      3) HW_mean
      4) HW_weighted (1/(dist+eps))
      5) charged_fraction
      6) polar_fraction

    Assumptions
    -----------
    df_residues already contains:
      - 'res' (1-letter AA)
      - 'aa_polarity' categorical (e.g. np/p~/p-/p+)
      - 'kd_hydro' numeric
      - 'hw_polarity' numeric
      - 'dist_to_centroid' numeric
      - 'res_num' (not used here but expected to exist upstream)

    Returns
    -------
    Dict[str, float]
    """
    # --- KD / HW summaries (re-using the same function) ---
    kd_mean = compute_index_summary(
        df_residues, value_col=kd_col, weight_mode="mean", dist_col=dist_col, eps=eps
    )
    kd_weighted = compute_index_summary(
        df_residues, value_col=kd_col, weight_mode="weighted", dist_col=dist_col, eps=eps
    )
    hw_mean = compute_index_summary(
        df_residues, value_col=hw_col, weight_mode="mean", dist_col=dist_col, eps=eps
    )
    hw_weighted = compute_index_summary(
        df_residues, value_col=hw_col, weight_mode="weighted", dist_col=dist_col, eps=eps
    )

    # --- Composition metrics ---
    if aa_col not in df_residues.columns:
        raise KeyError(f"Missing required column: {aa_col}")
    if aa_polarity_col not in df_residues.columns:
        raise KeyError(f"Missing required column: {aa_polarity_col}")

    aa = df_residues[aa_col].astype(str).str.strip().str.upper()
    cat = df_residues[aa_polarity_col].astype(str).str.strip()

    # Keep only standard 20 AA rows (optional but helps avoid weird residues)
    std_mask = aa.isin(list("ACDEFGHIKLMNPQRSTVWY"))
    cat = cat[std_mask]

    n = int(cat.notna().sum())
    if n == 0:
        charged_fraction = float("nan")
        polar_fraction = float("nan")
    else:
        charged_fraction = float(cat.isin(["p-", "p+"]).sum() / n)
        polar_fraction = float(cat.isin(["p~", "p-", "p+"]).sum() / n)

    return {
        "kd_mean": kd_mean,
        "kd_weighted": kd_weighted,
        "hw_mean": hw_mean,
        "hw_weighted": hw_weighted,
        "charged_fraction": charged_fraction,
        "polar_fraction": polar_fraction,
    }

def get_residue_sterics(
    df_residues: pd.DataFrame,
    *,
    dist_col: str = "distance_to_centroid",
    aa_col: str = "res",
    vol_col: str = "aa_vol",
    eps: float = 1e-6,
) -> Dict[str, float]:
    """
    Compute a compact 6-metric sterics report for a binding pocket.

    Required columns (defaults):
      - distance_to_centroid (float)
      - res (1-letter AA)
      - aa_vol (float; side-chain volume in Å^3 or other consistent units)

    Metrics returned
    ----------------
    1) mean_volume
    2) weighted_mean_volume            (weights = 1/(distance_to_centroid + eps))
    3) volume_variance                 (unweighted variance)
    4) small_residue_frac               ( fraction of {G, A, S})
    5) small_residue_frac_weighted     (weighted fraction of {G, A, S})
    6) bulky_residue_frac               (fraction of {G, A, S})
    7) bulky_residue_frac_weighted     (fraction of {F, Y, W, R, K, L, I, M})

    Notes
    -----
    - NaNs are ignored where possible.
    - Weighted metrics use only rows where both distance and volume are finite.
    """
    for c in (dist_col, aa_col, vol_col):
        if c not in df_residues.columns:
            raise KeyError(f"Missing required column: {c}")

    aa = df_residues[aa_col].astype(str).str.strip().str.upper()

    dist = pd.to_numeric(df_residues[dist_col], errors="coerce").to_numpy(dtype=float)
    vol = pd.to_numeric(df_residues[vol_col], errors="coerce").to_numpy(dtype=float)

    # ---- Unweighted stats (volume only) ----
    if np.isfinite(vol).any():
        mean_volume = float(np.nanmean(vol))
        volume_variance = float(np.nanvar(vol, ddof=1)) if np.isfinite(vol).sum() > 1 else float("nan")
    else:
        mean_volume = float("nan")
        volume_variance = float("nan")

    # ---- Weighted stats ----
    w = 1.0 / (dist + eps)
    w[~np.isfinite(w)] = np.nan

    valid_w = np.isfinite(w) & np.isfinite(vol)
    if valid_w.any():
        weighted_mean_volume = float(np.average(vol[valid_w], weights=w[valid_w]))
        crowding_score = float(np.nansum(vol[valid_w] / (dist[valid_w] + eps)))
    else:
        weighted_mean_volume = float("nan")
        crowding_score = float("nan")

    # ---- composition fractions (unweighted & weighted) ----
    small = {"G", "A", "S"}
    bulky = {"F", "Y", "W", "R", "K", "L", "I", "M"}

    aa_arr = aa.to_numpy()
    valid_comp = np.isfinite(w) & (aa_arr != "")  # use weights even if vol missing

    if valid_comp.any():

        small_residue_frac = float(
            np.average(np.isin(aa_arr[valid_comp], list(small)).astype(float))
        )
        small_residue_frac_weighted = float(
            np.average(np.isin(aa_arr[valid_comp], list(small)).astype(float), weights=w[valid_comp])
        )
        bulky_residue_frac = float(
            np.average(np.isin(aa_arr[valid_comp], list(bulky)).astype(float))
        )
        bulky_residue_frac_weighted = float(
            np.average(np.isin(aa_arr[valid_comp], list(bulky)).astype(float), weights=w[valid_comp])
        )
    else:
        small_residue_frac = float("nan")
        bulky_residue_frac = float("nan")
        small_residue_frac_weighted = float("nan")
        bulky_residue_frac_weighted = float("nan")

    return {
        "mean_volume": mean_volume,
        "weighted_mean_volume": weighted_mean_volume,
        "volume_variance": volume_variance,
        "small_residue_frac": small_residue_frac,
        "small_residue_frac_weighted": small_residue_frac_weighted,
        "bulky_residue_frac": bulky_residue_frac,
        "bulky_residue_frac_weighted": bulky_residue_frac_weighted,
    }


def get_residue_sasa(
        pdb_fpath,
        data_fbase
):
    from Bio.PDB.SASA import ShrakeRupley
    p = PDBParser(QUIET=1)
    struct = p.get_structure(data_fbase, pdb_fpath)
    # residue level SASA
    sr_residue = ShrakeRupley()
    sr_residue.compute(struct, level="R")
    sasa_residues = []
    num_residues = len(struct[0]["A"])
    for i in range(1,num_residues+1):
        residue_id = (" ", i, " ")
        sasa_residues.append(round(struct[0]["A"][residue_id].sasa, 2))
    sasa_residues = np.array(sasa_residues)
    sasa_residues_sum = np.sum(sasa_residues)
    print('Total SASA:', sasa_residues_sum)


    return np.array(sasa_residues)


def get_residue_secondary_structure_surface_area(
        pdb_fpath,
        data_fbase,
        cols_to_return=['res_num', 'res', 'secondary_structure', 'relative_ASA', 'SASA']
):
    from Bio.PDB.DSSP import DSSP
    from Bio.PDB.SASA import ShrakeRupley


    # get model with protein chain
    p = PDBParser()
    structure = p.get_structure(data_fbase, pdb_fpath)
    sr_residue = ShrakeRupley()
    sr_residue.compute(structure, level="R")
    model = structure[0]
    chain_ids = [chain.get_id() for chain in model.get_chains()]
    print(chain_ids)
    protein_chain_id = chain_ids[0]
    chain_ids_to_remove = [id for id in chain_ids if id!=protein_chain_id]
    for id in chain_ids_to_remove:
        model.detach_child(id)
        print(f'Removed chain id {id} for DSSP processing.')
    num_residues = len(list(model[protein_chain_id].get_residues()))

    # remove any extra remark lines which could cause an error when DSSP parses the file
    with open(pdb_fpath, 'r') as f:
        lines = f.readlines()
        lines_cleaned = []
        for l in lines:
            if l[:6]!='REMARK':
                lines_cleaned.append(l)
    if len(lines_cleaned)<len(lines):
        with open(pdb_fpath, 'w') as f:
            f.writelines(lines_cleaned)
        print('Re-saved cleaned up PDB file.')

    # get DSSP & SASA properties for each residue
    dssp = DSSP(model, pdb_fpath, dssp='mkdssp')
    dssp_res = []
    for res_num in range(1,num_residues+1):
        residue_id = (" ", res_num, " ")
        res_key = (protein_chain_id, residue_id)
        if res_key not in dssp:
            continue
        res_vals = dssp[res_key]
        res_dict = {property_name: val for property_name, val in zip(dssp_property_names, res_vals)}
        res_dict.update({'SASA': round(model[protein_chain_id][residue_id].sasa, 2)})
        dssp_res.append(res_dict)
    dssp_res = pd.DataFrame(dssp_res).rename(columns={'relative ASA': 'relative_ASA'})

    # replace shortform secondary structure names
    dssp_res['secondary_structure'] = dssp_res['secondary_structure'].astype(str)
    for letter, description in dssp_secondary_structure_shortform.items():
        dssp_res.loc[dssp_res['secondary_structure']==letter, 'secondary_structure'] = description

    # return selected columns only
    dssp_res = dssp_res[cols_to_return]
    print(dssp_res.head())

    return dssp_res