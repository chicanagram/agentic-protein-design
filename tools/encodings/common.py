from __future__ import annotations

import re
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Union
from project_config.variables import aaList, aaList_with_X
from tools.utils.plot_utils import plot_variant_heatmap

def extract_sequence_token_spans(attention_mask: np.ndarray) -> List[slice]:
    """
    Compute per-sequence residue slices excluding BOS/EOS and padding tokens.
    """
    spans: List[slice] = []
    lengths = attention_mask.sum(axis=1).tolist()
    for length in lengths:
        usable = max(int(length) - 2, 0)
        spans.append(slice(1, 1 + usable))
    return spans


def _sanitize_name(value: str) -> str:
    """Build a filesystem-safe stem for output files."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(value).strip()).strip("_")


def _resolve_model_name(
        model_name: str,
        model_name_aliases: Dict[str, str],
        default_model_name: str
) -> str:
    """Resolve a shorthand alias or pass through a raw Hugging Face model id."""
    key = str(model_name or default_model_name).strip().lower()
    return model_name_aliases.get(key, str(model_name or default_model_name).strip())


def save_layerwise_embeddings(
    value: Dict[int, np.ndarray],
    output_stem: Union[str, Path],
    suffix: str,
    file_suffix: str = "",
    log_tag: str = "get_embeddings",
) -> Dict[str, str]:
    """
    Save one embedding matrix per layer as `.npy`.

    Output filenames follow:
    - default: `{output_stem}{file_suffix}-{suffix}-{layer}.npy`
    - when `single_layer_flat=True` and one layer: `{output_stem}{file_suffix}.npy`
    """
    # normalize output stem and iterate layer payloads.
    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, str] = {}

    # default layerwise filename pattern with duplicate-suffix guard.
    for layer, layer_value in value.items():
        arr = np.asarray(layer_value)
        stem_name = stem.name
        normalized_suffix = str(suffix).strip()
        if normalized_suffix and (
            stem_name.endswith(f"_{normalized_suffix}") or stem_name.endswith(f"-{normalized_suffix}")
        ):
            fpath = stem.parent / f"{stem_name}{str(file_suffix)}-{int(layer)}.npy"
        else:
            fpath = stem.parent / f"{stem_name}{str(file_suffix)}-{normalized_suffix}-{int(layer)}.npy"
        np.save(str(fpath), arr.astype(arr.dtype, copy=False))
        paths[str(int(layer))] = str(fpath)
        print(f"[{log_tag}] Saved {suffix} layer {int(layer)}: {fpath}")
    return paths


def _resolve_layers(requested_layers: Optional[Sequence[int]], model: Any) -> List[int]:
    """Resolve requested hidden-state layers into positive layer indices."""
    max_layer = int(getattr(model.config, "num_hidden_layers", 0))
    if requested_layers is None:
        return [max_layer]
    resolved: List[int] = []
    for layer in requested_layers:
        value = int(layer)
        if value < 0:
            value = max_layer + 1 + value
        if value < 0 or value > max_layer:
            raise ValueError(f"Requested layer {layer} is outside valid range [0, {max_layer}].")
        if value not in resolved:
            resolved.append(value)
    return resolved


def compute_pooled_embeddings(
    embeddings_per_residue: Dict[int, np.ndarray],
    pool_method: str = "mean",
    mutations: Optional[Sequence[str]] = None,
    sep: Optional[str] = "+",
) -> Dict[int, np.ndarray]:
    """
    Pool per-residue embedding matrices by layer.

    `mean`: mean over all residues.
    `mut`: mean over mutated residue positions parsed from mutation strings.
    """
    # Section 1: normalize pooling mode and define mutation parsing helper.
    method = str(pool_method or "mean").strip().lower()

    def _parse_mutation_positions(mut: str, token_sep: str) -> List[int]:
        positions: List[int] = []
        for token in str(mut or "").split(token_sep):
            tok = token.strip()
            if len(tok) < 3:
                continue
            if not tok[0].isalpha() or not tok[-1].isalpha():
                continue
            pos_txt = tok[1:-1]
            if pos_txt.isdigit():
                positions.append(int(pos_txt) - 1)  # convert to 0-based
        return positions

    # Section 2: pool each layer matrix to shape (n_sequences, hidden_dim).
    out: Dict[int, np.ndarray] = {}
    for layer, layer_matrix in embeddings_per_residue.items():
        matrix = np.asarray(layer_matrix)
        if matrix.ndim != 3:
            raise ValueError("Expected per-residue matrix with shape (n_sequences, seq_len, hidden_dim).")
        if method == "mean":
            out[int(layer)] = matrix.mean(axis=1)
            continue
        if method != "mut":
            raise ValueError("pool_method must be 'mean' or 'mut'.")
        if mutations is None or sep is None:
            raise ValueError("mut pooling requires mutations and sep.")
        if len(mutations) != matrix.shape[0]:
            raise ValueError("mutations must have same length as number of sequences.")
        pooled_rows: List[np.ndarray] = []
        for emb_arr, mut in zip(matrix, mutations):
            pos = _parse_mutation_positions(str(mut), str(sep))
            pos = [p for p in pos if 0 <= p < emb_arr.shape[0]]
            if not pos:
                raise ValueError(f"No valid mutated positions parsed for mutation '{mut}'.")
            pooled_rows.append(emb_arr[pos, :].mean(axis=0))
        out[int(layer)] = np.asarray(pooled_rows)
    return out