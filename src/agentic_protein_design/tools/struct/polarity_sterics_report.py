from __future__ import annotations
import os
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
import matplotlib.pyplot as plt
from typing import Dict, Literal
from project_config.variables import address_dict, subfolders

def compute_index_summary(
    df_pocket: pd.DataFrame,
    value_col: Literal["kd_hydro", "hw_polarity"],
    weight_mode: Literal["mean", "weighted"] = "mean",
    dist_col: str = "dist_to_centroid",
    eps: float = 1e-6,
) -> float:
    """
    Compute either an unweighted mean or a distance-weighted mean for a polarity/hydropathy index.

    Parameters
    ----------
    df_pocket : pd.DataFrame
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
    if value_col not in df_pocket.columns:
        raise KeyError(f"Missing required column: {value_col}")
    if weight_mode == "weighted" and dist_col not in df_pocket.columns:
        raise KeyError(f"Missing required column: {dist_col}")

    vals = pd.to_numeric(df_pocket[value_col], errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(vals)

    if not mask.any():
        return float("nan")

    if weight_mode == "mean":
        return float(np.nanmean(vals))

    # weighted
    d = pd.to_numeric(df_pocket.loc[:, dist_col], errors="coerce").to_numpy(dtype=float)
    w = 1.0 / (d + eps)
    w[~np.isfinite(w)] = np.nan

    # Only keep rows where both value and weight are finite
    m = mask & np.isfinite(w)
    if not m.any():
        return float("nan")

    return float(np.average(vals[m], weights=w[m]))

def polarity_report(
    df_pocket: pd.DataFrame,
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
    df_pocket already contains:
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
        df_pocket, value_col=kd_col, weight_mode="mean", dist_col=dist_col, eps=eps
    )
    kd_weighted = compute_index_summary(
        df_pocket, value_col=kd_col, weight_mode="weighted", dist_col=dist_col, eps=eps
    )
    hw_mean = compute_index_summary(
        df_pocket, value_col=hw_col, weight_mode="mean", dist_col=dist_col, eps=eps
    )
    hw_weighted = compute_index_summary(
        df_pocket, value_col=hw_col, weight_mode="weighted", dist_col=dist_col, eps=eps
    )

    # --- Composition metrics ---
    if aa_col not in df_pocket.columns:
        raise KeyError(f"Missing required column: {aa_col}")
    if aa_polarity_col not in df_pocket.columns:
        raise KeyError(f"Missing required column: {aa_polarity_col}")

    aa = df_pocket[aa_col].astype(str).str.strip().str.upper()
    cat = df_pocket[aa_polarity_col].astype(str).str.strip()

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

def sterics_report(
    df_pocket: pd.DataFrame,
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
        if c not in df_pocket.columns:
            raise KeyError(f"Missing required column: {c}")

    aa = df_pocket[aa_col].astype(str).str.strip().str.upper()

    dist = pd.to_numeric(df_pocket[dist_col], errors="coerce").to_numpy(dtype=float)
    vol = pd.to_numeric(df_pocket[vol_col], errors="coerce").to_numpy(dtype=float)

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