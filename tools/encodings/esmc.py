from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from scipy.special import softmax
import torch

from tools.encodings.common import _resolve_model_name, compute_pooled_embeddings, save_layerwise_embeddings
from tools.utils.model_utils import get_device
from tools.utils.plot_utils import plot_variant_heatmap
from tools.utils.general_utils import flatten_2D_arr
from project_config.variables import aaList_with_X, aaList

from esm.models.esmc import ESMC
from esm.utils.constants.esm3 import SEQUENCE_VOCAB
from esm.sdk.api import ESMProtein, LogitsConfig

MODEL_NAME_ALIASES: Dict[str, str] = {
    "esmc-300m": "esmc_300m",
    "esmc-600m": "esmc_600m",
}
DEFAULT_MODEL_NAME = "esmc-600m"
DEFAULT_MARGINAL_TYPE = "wt"
_MODEL_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}


def load_model(
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and cache an ESM masked-LM model plus tokenizer.

    Args:
        model_name: ESM alias (for example `esm2_650m`, `esm1v_1`) or raw HF id.
        device: Optional device override. Defaults to `get_device()`.

    Returns:
        Dict containing tokenizer, model, resolved model name, and device.
    """
    resolved_name = _resolve_model_name(model_name, MODEL_NAME_ALIASES, DEFAULT_MODEL_NAME)
    resolved_device = str(device or get_device())
    cache_key = (resolved_name, resolved_device)
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    model = ESMC.from_pretrained(resolved_name).to(resolved_device)
    token_to_idx = {token: idx for idx, token in enumerate(SEQUENCE_VOCAB)}

    bundle = {
        "model_name": resolved_name,
        "device": resolved_device,
        "model": model,
        "token_to_idx": token_to_idx,
    }
    _MODEL_CACHE[cache_key] = bundle
    return bundle


def forward_pass(
    sequences: List[str],
    *,
    model: Optional[Any] = None,
    model_name: str = DEFAULT_MODEL_NAME,
    device: Optional[str] = None,
    output_hidden_states: bool = True,
    layers: Optional[List[int]] = None,
) -> Any:

    embedding_config = LogitsConfig(sequence=True, return_embeddings=output_hidden_states, return_hidden_states=output_hidden_states)
    if model is None:
        bundle = load_model(model_name=model_name, device=device)["model"]
        model, model_name, device = bundle['model'], bundle['model_name'], bundle['device']

    logits = []
    representations = {layer: [] for layer in layers} if layers is not None else None
    for seq in sequences:
        protein = ESMProtein(sequence=seq)
        protein_tensor = model.encode(protein)
        output_seq = model.logits(protein_tensor, embedding_config)
        logits_seq = output_seq.logits.sequence[0, :, :] # logits shape: n, T, V
        logits.append(logits_seq)
        # optionally obtain embeddings
        if output_hidden_states:
            hidden_states_seq = output_seq.hidden_states[:, 0, :, :]
            for layer in layers:
                representations[layer].append(hidden_states_seq[layer - 1, :, :])
    return logits, representations


def get_zeroshot_scores(
    sequences_base: Optional[Union[str, Sequence[str]]] = None,
    sequences: Optional[Union[str, Sequence[str]]] = None,
    mutations: Optional[Union[str, Sequence[str]]] = None,
    marginal_type: str = DEFAULT_MARGINAL_TYPE,
    output_path: Optional[Union[str, Path]] = None,
    model_name: str = DEFAULT_MODEL_NAME,
    batch_size: int = 4,
    device: Optional[str] = None,
):
    """Compute zero-shot scores/LLR using WT or masked marginal scoring."""
    if sequences_base is None:
        raise ValueError("Zero-shot scores requires sequences_base to be set.")
    if marginal_type == "wt":
        score_fn = _compute_wt_marginal_scores
    elif marginal_type == "masked":
        score_fn = _compute_masked_marginal_scores

    sequences = sequences if sequences not in [None, ""] else None
    output_path = output_path.replace('LLR', f'LLR-{marginal_type}')

    # get LLR for sequences and all single-site mutations of unique sequence_base
    LLRsum_seq, llr_by_base = score_fn(sequences_base, sequences, model_name, batch_size, device)

    # save LLR for sequences
    if LLRsum_seq is not None:
        # save as numpy
        np.save(f'{output_path}.npy', np.array(LLRsum_seq).astype(np.float32))
        # save as csv
        pd.DataFrame({'mutations':mutations, 'LLR':LLRsum_seq}).round(4).to_csv(f'{output_path}.csv')
        print(f"[zeroshot/{marginal_type}-marginal] Saved raw scores: {output_path}.csv")

    # save LLR for all mutations
    for seq_base, LLR_all in llr_by_base.items():
        LLR_all_noX = LLR_all[:-1, :]
        LLR_all_df = pd.DataFrame(LLR_all_noX, index=aaList, columns=[f'{i+1}{aa}' for i, aa in enumerate(seq_base)]).round(4)
        LLR_all_df.to_csv(f'{output_path}_map.csv')
        LLR_all_flattened, mutations_all = flatten_2D_arr(LLR_all_noX, seq_base, MT_aa=aaList)
        LLR_all_flattened_df = pd.DataFrame({'mutations':mutations_all,'LLR':LLR_all_flattened})
        LLR_all_flattened_df['is_WT'] = [(mut[0]==mut[-1])*1 for mut in mutations_all]
        LLR_all_flattened_df = LLR_all_flattened_df.loc[LLR_all_flattened_df['is_WT']==0, ['mutations', 'LLR']].reset_index(drop=True).round(4)
        LLR_all_flattened_df.to_csv(f'{output_path}_vect.csv')
        plot_variant_heatmap(
            -LLR_all_noX,
            seq_base,
            N_res_per_heatmap_row=100,
            aa_list=aaList,
            savefig=f'{output_path}_map.png',
            figtitle='Predicted Effects of Mutations on Protein Sequence (LLR)')
    return LLRsum_seq


def _compute_wt_marginal_scores(
    sequences_base: Sequence[str],
    sequences: Optional[Sequence[str]] = None,
    model_name: Optional[str] = DEFAULT_MODEL_NAME,
    batch_size: Optional[int] = 4,
    device: Optional[str] = "cpu",
) -> Tuple[Optional[np.ndarray], Dict[str, np.ndarray]]:
    """
    Compute WT-marginal LLR matrices from one WT forward pass per unique base sequence.

    Returns:
      - llr_sum_per_sequence: shape (n_sequences,) or None if sequences is None
      - llr_by_base: dict {base_seq: matrix shape (len(aaList_with_X), len(base_seq))}
    """
    bundle = load_model(model_name=model_name, device=device)
    model = bundle["model"]
    token_to_idx = bundle["token_to_idx"]
    llr_by_base: Dict[str, np.ndarray] = {}

    # Section 1: one forward pass per unique WT base sequence.
    unique_bases = list(dict.fromkeys(sequences_base))
    for seq_base in unique_bases:
        logits, _ = forward_pass(
            [seq_base],
            model=model,
            output_hidden_states=False,
        )
        logits = logits[0]  # [T, V]
        probs = softmax(logits, axis=-1)

        n = len(seq_base)
        llr_mat = np.zeros((len(aaList_with_X), n), dtype=np.float32)

        for pos_idx, wt_aa in enumerate(seq_base):
            token_pos = pos_idx + 1  # ESM BOS offset
            wt_id = token_to_idx[wt_aa]
            wt_probs = probs[token_pos, wt_id]

            for i, aa in enumerate(aaList_with_X):
                aa_id = token_to_idx[aa]
                aa_probs = probs[token_pos, aa_id]
                llr_mat[i, pos_idx] = np.round(np.log(aa_probs) - np.log(wt_probs), 4)
        llr_by_base[seq_base] = llr_mat

    # Section 2: optionally sum mutation LLR for provided mutant sequences.
    llr_sum_seq = None
    if sequences is not None:
        llr_sum_seq: List[float] = []
        for seq, seq_base in zip(sequences, sequences_base):
            if len(seq) != len(seq_base):
                raise ValueError("Each sequence must have same length as its sequence_base.")
            mat = llr_by_base[seq_base]
            total = 0.0
            for pos_idx, (mut_aa, wt_aa) in enumerate(zip(seq, seq_base)):
                if mut_aa != wt_aa:
                    aa_row = aaList_with_X.index(mut_aa)
                    total += float(mat[aa_row, pos_idx])
            llr_sum_seq.append(total)
        llr_sum_seq = np.asarray(llr_sum_seq, dtype=np.float32)

    return llr_sum_seq, llr_by_base


def _compute_masked_marginal_scores(
    sequences_base: Sequence[str],
    sequences: Optional[Sequence[str]] = None,
    model_name: Optional[str] = DEFAULT_MODEL_NAME,
    batch_size: Optional[int] = 4,  # kept for interface parity
    device: Optional[str] = "cpu",
) -> Tuple[Optional[np.ndarray], Dict[str, np.ndarray]]:
    """
    Compute masked-marginal LLR matrices from one masked sweep per unique base sequence.

    Returns:
      - llr_sum_per_sequence: shape (n_sequences,) or None if sequences is None
      - llr_by_base: dict {base_seq: matrix shape (len(aaList_with_X), len(base_seq))}
    """
    bundle = load_model(model_name=model_name, device=device)
    model = bundle["model"]
    token_to_idx = bundle["token_to_idx"]
    llr_by_base: Dict[str, np.ndarray] = {}

    # Section 1: one masked sweep per unique WT base sequence.
    unique_bases = list(dict.fromkeys(sequences_base))
    for seq_base in unique_bases:
        n = len(seq_base)
        masked_sequences: List[str] = []
        for i in range(n):
            seq_base_masked = seq_base[:i] + '<mask>' + seq_base[i+1:]
            masked_sequences.append(seq_base_masked)
        logits_list, _ = forward_pass(masked_sequences, model=model, output_hidden_states=False)
        logits = torch.cat([logits_list[i][i+1,:].reshape((1,-1)) for i in range(n)], dim=0)  # [n, V]
        log_probs = torch.log_softmax(logits, dim=-1)       # [n, V]

        # Position-specific WT log-probability and full residue-position table
        rows = torch.arange(n, device=device)
        wt_ids = torch.tensor([token_to_idx[aa] for aa in seq_base])  # [n]
        wt_logp = log_probs[rows, wt_ids]                 # [n]
        pos_token_llr = log_probs - wt_logp[:, None]  # [n, V]

        # Convert to shape [aa, pos]
        llr_mat = np.zeros((len(aaList_with_X), n), dtype=np.float32)
        for i, aa in enumerate(aaList_with_X):
            aa_id = token_to_idx[aa]
            llr_mat[i, :] = pos_token_llr[:, aa_id].detach().cpu().numpy()

        llr_by_base[seq_base] = llr_mat

    # Section 2: optionally sum mutation LLR for provided mutant sequences.
    llr_sum_seq = None
    if sequences is not None:
        llr_sum_seq: List[float] = []
        for seq, seq_base in zip(sequences, sequences_base):
            if len(seq) != len(seq_base):
                raise ValueError("Each sequence must have same length as its sequence_base.")
            mat = llr_by_base[seq_base]
            total = 0.0
            for pos_idx, (mut_aa, wt_aa) in enumerate(zip(seq, seq_base)):
                if mut_aa != wt_aa:
                    aa_row = aaList_with_X.index(mut_aa)
                    total += float(mat[aa_row, pos_idx])
            llr_sum_seq.append(total)
        llr_sum_seq = np.asarray(llr_sum_seq, dtype=np.float32)

    return llr_sum_seq, llr_by_base


def get_embeddings(
    sequences: Union[str, Sequence[str]],
    sequences_base: Optional[Union[str, Sequence[str]]] = None,
    save_per_residue_embeddings: bool = False,
    get_embeddings_for_seq_base: bool = False,
    pool_method: Optional[str] = "mean",
    mutations: Optional[Sequence[str]] = None,
    sep: Optional[str] = '+',
    output_path: Optional[Union[str, Path]] = None,
    layers: Optional[Sequence[int]] = None,
    model_name: str = DEFAULT_MODEL_NAME,
    batch_size: int = 4,
    device: Optional[str] = None,
):
    """
    Compute and save layer-wise embeddings for sequences (and optionally WT/base).

    Per-residue embeddings are saved as `*.npy` arrays with suffix `-{layer_number}`.
    If `pool_method` is provided, pooled embeddings are also saved layer-wise.
    """

    # Section 1: prepare output stem and compute per-residue embeddings.
    out_base = Path(output_path) if output_path else Path("embeddings")
    result: Dict[str, Any] = {}
    per_residue = _compute_per_residue_embeddings(
        sequences,
        model_name=model_name,
        layers=layers,
        batch_size=batch_size,
        device=device,
    )

    # Section 2: optionally persist per-residue embeddings for input sequences.
    if save_per_residue_embeddings:
        result["per_residue_paths"] = save_layerwise_embeddings(
            per_residue,
            output_stem=out_base,
            suffix="per_residue",
            log_tag="get_embeddings",
        )

    # Section 3: optionally pool embeddings and persist pooled matrices.
    if pool_method is not None:
        pooled = compute_pooled_embeddings(
            per_residue,
            pool_method=str(pool_method),
            mutations=mutations,
            sep=sep,
        )
        result["pooled_paths"] = save_layerwise_embeddings(
            pooled,
            output_stem=out_base,
            suffix=f"{str(pool_method)}_pooled",
            log_tag="get_embeddings",
        )

    # Section 4: optionally compute/save separate embeddings for base sequences.
    if get_embeddings_for_seq_base:
        base_list = sequences_base if sequences_base is not None else []
        if not base_list:
            raise ValueError("get_embeddings_for_seq_base=True requires non-empty sequences_base.")
        base_per_residue = _compute_per_residue_embeddings(
            base_list,
            model_name=model_name,
            layers=layers,
            batch_size=batch_size,
            device=device,
        )
        if save_per_residue_embeddings:
            result["base_per_residue_paths"] = save_layerwise_embeddings(
                base_per_residue,
                output_stem=out_base,
                suffix="per_residue",
                file_suffix="_base",
                log_tag="get_embeddings",
            )
        if pool_method is not None:
            base_pooled = compute_pooled_embeddings(
                base_per_residue,
                pool_method="mean",
                mutations=None,
                sep=sep,
            )
            result["base_pooled_paths"] = save_layerwise_embeddings(
                base_pooled,
                output_stem=out_base,
                suffix=f"{str(pool_method)}_pooled",
                file_suffix="_base",
                log_tag="get_embeddings",
            )

    return result


def _compute_per_residue_embeddings(
    sequences: Union[str, Sequence[str]],
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    layers: Optional[Sequence[int]] = None,
    batch_size: int = 2,
    device: Optional[str] = None,
) -> Dict[int, np.ndarray]:
    """
    Extract per-residue hidden-state embeddings for one or more ESM layers.

    Args:
        sequences: Single sequence or iterable of sequences.
        model_name: ESM alias or raw HF model id.
        layers: Hidden-state layers to return. Defaults to the final layer.
        batch_size: Batch size for inference.
        device: Optional device override.

    Returns:
        Dict `{layer_index: embedding_matrix}` where each value is
        a dense array shaped `(n_sequences, seq_len, hidden_dim)`.
    """
    # Section 1: Load model
    bundle = load_model(model_name=model_name, device=device)
    collected: Dict[int, List[np.ndarray]] = {layer: [] for layer in layers}

    # Section 2: run batched forward passes and collect residue spans per layer.
    _, representations = forward_pass(
        sequences,
        model=bundle["model"],
        output_hidden_states=True,
        layers=layers
    )

    collected = {layer:[] for layer in layers}
    for layer in layers:
        for i, seq in enumerate(sequences):
            collected[layer].append(representations[layer][i][1:1+len(seq), :].detach().cpu().numpy())

    # Section 3: convert per-layer list outputs to dense matrices.
    out: Dict[int, np.ndarray] = {}
    for layer, arrays in collected.items():
        if not arrays:
            out[int(layer)] = np.asarray([], dtype=np.float32)
            continue
        lengths = {int(np.asarray(a).shape[0]) for a in arrays}
        if len(lengths) != 1:
            raise ValueError(
                f"Layer {int(layer)} embeddings have variable sequence lengths {sorted(lengths)}; "
                "cannot return a single dense matrix."
            )
        out[int(layer)] = np.stack([np.asarray(a) for a in arrays], axis=0)

    return out