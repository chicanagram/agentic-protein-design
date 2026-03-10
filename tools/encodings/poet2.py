from __future__ import annotations

import os
os.environ["HF_HUB_OFFLINE"] = "1"
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from tools.encodings.common import (
    _resolve_model_name,
    _resolve_layers,
    _coerce_sequence_list,
    _print_progress,
    compute_pooled_embeddings,
    extract_sequence_token_spans,
    resolve_llr_cache_paths,
    save_layerwise_embeddings,
    save_llr_vect_and_heatmap,
    score_mutants_from_llr_map,
)
from tools.openprotein.openprotein_utils import connect_openprotein_session, create_prompt
from tools.openprotein.align_msa_openprotein import create_openprotein_msa, upload_openprotein_msa
from project_config.variables import aaList_with_X

DEFAULT_MODEL_NAME = 'poet2' # 'poet'
DEFAULT_MARGINAL_TYPE = "wt"


def get_poet_prompts(
        sequences_seed: Union[str, Sequence[str]],
        msa_fpaths: Optional[Union[str, Sequence[str]]] = None,
        session: Optional[Any] = None,
        num_prompts: Optional[int] = 3,
):
    # create session
    sess = session or connect_openprotein_session()
    # get prompt for each MSA
    processed_prompts = {}
    prompts = []
    for msa_fpath, sequence_base in zip(msa_fpaths, sequences_seed):
        # create msa from scratch
        if msa_fpath is None:
            msa = create_openprotein_msa(seed_sequence=sequence_base, session=sess, seq_fasta_path=None)
            prompt = create_prompt(msa, num_prompts=num_prompts, show_prompt=False)
            processed_prompts[sequence_base] = prompt
        # upload msa
        else:
            if msa_fpath not in processed_prompts:
                msa = upload_openprotein_msa(msa_fpath, session=session)
                prompt = create_prompt(msa, num_prompts=num_prompts, show_prompt=False)
                processed_prompts[msa_fpath] = prompt
            else:
                prompt = processed_prompts[msa_fpath]
        prompts.append(prompt)
    return prompts


def get_LLR_scores(
        sequences_base: Optional[Union[str, Sequence[str]]] = None,
        sequences: Optional[Union[str, Sequence[str]]] = None,
        mutations: Optional[Union[str, Sequence[str]]] = None,
        output_path: Optional[Union[str, Path]] = None,
        llr_cache_vect_filename_prefix: str = "",
        resave_llr_cache_if_found: bool = False,
        model_name: str = DEFAULT_MODEL_NAME,
        batch_size: int = 4,
        num_prompts: int = 3,
        msa_fpaths: Optional[Union[str, Sequence[str]]] = None,
        session: Optional[Any] = None
):
    # Section 1: normalize sequence inputs and scoring backend.
    base_list = _coerce_sequence_list(sequences_base, name="get_LLR_scores(sequences_base)", required=True)
    seq_list = _coerce_sequence_list(sequences, name="get_LLR_scores(sequences)", required=False)
    unique_bases = list(dict.fromkeys(base_list))
    if len(unique_bases) != 1:
        raise ValueError(
            "LLR cache/vector scoring currently supports exactly one unique sequence_base."
        )

    # Section 2: resolve output/cache paths.
    output_path = str(output_path) if output_path is not None else f"{model_name}_LLR"
    output_path = output_path.replace('LLR', f'LLR-{DEFAULT_MARGINAL_TYPE}')
    output_stem = Path(str(output_path))
    cache_stem = output_stem.with_name(f"{str(model_name)}_LLR-{DEFAULT_MARGINAL_TYPE}")
    cache_info = resolve_llr_cache_paths(
        cache_stem,
        llr_cache_vect_filename_prefix=llr_cache_vect_filename_prefix,
    )
    vect_cache_path = Path(cache_info["vect_cache_path"])
    map_png_cache_path = Path(cache_info["map_png_cache_path"])

    # Cache resolution for vect CSV.
    cache_hit = bool(cache_info["vect_exists"])
    if cache_hit:
        print(f"[zeroshot/{DEFAULT_MARGINAL_TYPE}-marginal] Loaded LLR cache: {vect_cache_path}")

    # Section 3: compute and persist full marginal map only on cache miss (or explicit refresh).
    if (not cache_hit) or bool(resave_llr_cache_if_found):

        # standardize msa_fpath
        if msa_fpaths is None or isinstance(msa_fpaths,str):
            msa_fpaths = [msa_fpaths] * len(unique_bases)
        session = connect_openprotein_session()
        poet = session.embedding.get_model(model_name)

        # get prompts
        prompts = get_poet_prompts(unique_bases, msa_fpaths, session, num_prompts)

        # get single site prediction jobs
        sspjobs = []
        for prompt, sequence_base in zip(prompts, unique_bases):
            sspjob = poet.single_site(prompt=prompt, sequence=sequence_base.encode())
            ssp_results = sspjob.wait()
            llr_flattened = []
            for mut, scores in ssp_results.items():
                mut = mut.decode()
                score = np.mean(scores)
                if mut == 'WT':
                    wt_score = score
                else:
                    llr_flattened.append({'mutations':mut.decode(), 'LLR': score - wt_score})
            llr_flattened = pd.DataFrame(llr_flattened).round(4)
            llr_flattened.to_csv(vect_cache_path)

    # Section 4: score provided sequences by summing cached mutation LLRs.
    LLRsum_seq = score_mutants_from_llr_map(
        llr_vect_csv_path=vect_cache_path,
        sequences_base=base_list,
        sequences=seq_list,
    )


    return None


def get_mean_PLL_scores(
        sequences: Optional[Union[str, Sequence[str]]] = None,
        output_path: Optional[Union[str, Path]] = None,
        model_name: str = DEFAULT_MODEL_NAME,
        batch_size: int = 4,
):
    session = connect_openprotein_session()
    poet = session.embedding.get_model(model_name)

    scorejob = poet.score(prompt=prompt.prompt_id, sequences=sequences)
    return None


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
    return None


def get_pooled_embeddings():
    return None


def get_svd_model():
    return None
