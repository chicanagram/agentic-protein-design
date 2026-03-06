from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np
from tools.encodings.common import _sanitize_name, compute_pooled_embeddings, save_layerwise_embeddings


def _parse_plm_feature_name(feature_name: str) -> Tuple[str, str]:
    """
    Parse a PLM feature string into (model_prefix, feature_suffix).

    Supported suffixes:
    - zeroshot / zero_shot
    - per_residue
    - mean_pooled
    - mut_pooled
    """
    name = str(feature_name).strip()
    suffixes = ("mean_pooled", "mut_pooled", "per_residue", "LLR")
    for suffix in suffixes:
        marker = f"_{suffix}"
        if name.endswith(marker):
            return name[: -len(marker)], suffix
    raise ValueError(
        f"Unsupported PLM feature name '{feature_name}'. "
        "Expected '<model>_(LLR|per_residue|mean_pooled|mut_pooled)'."
    )


def _resolve_backend_name(model_prefix: str) -> str:
    """Route a model prefix to an available backend module."""
    lowered = str(model_prefix).strip().lower()
    if lowered.startswith("esmc"):
        return "esmc"
    if lowered.startswith(("esm2", "esm1", "esm")):
        return "esm2"
    if lowered.startswith("poet2"):
        return "poet2"
    raise ValueError(f"Could not infer PLM backend from model prefix '{model_prefix}'.")


def _load_backend_module(backend: str):
    """Import a PLM backend module and return it."""
    module_name = f"tools.encodings.{backend}"
    return importlib.import_module(module_name)


def _normalize_suffix(suffix: str) -> str:
    if str(suffix).strip() == "zero_shot":
        return "zeroshot"
    return str(suffix).strip()


def _load_layerwise_arrays(paths_by_layer: Dict[str, str]) -> Dict[int, np.ndarray]:
    # Section 1: load saved layer-wise `.npy` matrices into memory.
    out: Dict[int, np.ndarray] = {}
    for layer, path in paths_by_layer.items():
        out[int(layer)] = np.load(str(path), allow_pickle=False)
    return out


def _delete_artifact_paths(paths_by_layer: Dict[str, str]) -> None:
    # Section 1: remove temporary files used only for intermediate pooling.
    for _, path in paths_by_layer.items():
        p = Path(path)
        if p.exists():
            p.unlink()


def _resolve_layers_for_model(
    model_prefix: str,
    layers: Optional[Union[Sequence[int], Mapping[str, Sequence[int]]]],
) -> Optional[Sequence[int]]:
    """
    Resolve layer selection for a specific model.

    Supported inputs:
    - `None`: backend default behavior
    - `List[int]`: shared layer list for all PLMs
    - `Dict[str, List[int]]`: per-model layer list keyed by PLM name
    """
    # Section 1: pass through None or shared sequence input.
    if layers is None:
        return None
    if isinstance(layers, (list, tuple)):
        return [int(x) for x in layers]

    # Section 2: resolve per-model dictionary keys.
    if isinstance(layers, Mapping):
        exact = layers.get(model_prefix)
        lowered_map = {str(k).strip().lower(): v for k, v in layers.items()}
        lowered = lowered_map.get(str(model_prefix).strip().lower())
        value = exact if exact is not None else lowered
        if value is None:
            return None
        return [int(x) for x in value]

    raise TypeError(
        "layers must be None, List[int], or Dict[str, List[int]] keyed by PLM model name."
    )


def get_plm_encodings(
    plm_feature_sets: Sequence[str],
    sequence_list: Optional[Sequence[str]],
    sequence_base_list: Optional[Sequence[str]] = None,
    *,
    encodings_dir: str,
    marginal_type: str = "wt",
    mutations: Optional[Sequence[str]] = None,
    sep: str = "+",
    layers: Optional[Union[Sequence[int], Mapping[str, Sequence[int]]]] = None,
    batch_size: int = 4,
    device: Optional[str] = None,
    get_embeddings_for_seq_base: bool = False,
    save_per_residue_embeddings: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """
    Generate PLM-derived encodings by parsing feature-set names and dispatching by backend.

    All artifact paths are rooted under `encodings_dir`.
    """
    # Section 1: validate inputs and create output directory.
    if not plm_feature_sets:
        return {}
    out_dir = Path(encodings_dir)

    # Section 2: group requested features by model so each model is processed once.
    grouped: Dict[str, Dict[str, Any]] = {}
    ordered_features: List[str] = []
    for feature_name in plm_feature_sets:
        model_prefix, suffix = _parse_plm_feature_name(feature_name)
        backend_name = _resolve_backend_name(model_prefix)
        if model_prefix not in grouped:
            grouped[model_prefix] = {
                "backend": backend_name,
                "features": [],
                "suffixes": set(),
            }
        grouped[model_prefix]["features"].append(feature_name)
        grouped[model_prefix]["suffixes"].add(suffix)
        ordered_features.append(feature_name)

    # Section 3: process each model group and build per-feature result records.
    results: Dict[str, Dict[str, Any]] = {}
    for model_prefix, group_info in grouped.items():
        # Section 3.0: resolve model-specific layer selection.
        model_layers = _resolve_layers_for_model(model_prefix, layers)

        backend_name = str(group_info["backend"])
        module = _load_backend_module(backend_name)
        requested_suffixes = set(group_info["suffixes"])

        # Section 3A: run zeroshot once per model if requested.
        if "LLR" in requested_suffixes:
            if not hasattr(module, "get_zeroshot_scores"):
                raise NotImplementedError(
                    f"Backend '{backend_name}' does not implement get_zeroshot_scores."
                )
            zeroshot_feature_name = f"{model_prefix}_LLR"
            zeroshot_stem = _sanitize_name(zeroshot_feature_name)
            zeroshot_base_path = out_dir / zeroshot_stem
            output_path = str(zeroshot_base_path)

            print(f'Obtaining zero-shot scores for {model_prefix}...')
            scores = module.get_zeroshot_scores(
                sequences_base=sequence_base_list,
                sequences=sequence_list,
                mutations=mutations,
                marginal_type=marginal_type,
                output_path=output_path,
                model_name=model_prefix,
                batch_size=batch_size,
                device=device,
            )
            results[zeroshot_feature_name] = {
                "feature_name": zeroshot_feature_name,
                "model_prefix": model_prefix,
                "backend": backend_name,
                "output_path": output_path,
                "shape": list(scores.shape) if isinstance(scores, np.ndarray) else None,
            }

        # Section 3B: run embeddings once per model, then derive requested artifacts.
        embedding_suffixes = {"per_residue", "mean_pooled", "mut_pooled"} & requested_suffixes
        if not embedding_suffixes:
            continue
        if sequence_list is None:
            raise ValueError("Embedding features require a non-empty sequence_list.")
        if "mut_pooled" in embedding_suffixes and mutations is None:
            raise ValueError("mut_pooled feature requested but mutations is None.")
        if not hasattr(module, "get_embeddings"):
            raise NotImplementedError(f"Backend '{backend_name}' does not implement get_embeddings.")

        per_res_feature_name = f"{model_prefix}_per_residue"
        per_res_stem = _sanitize_name(per_res_feature_name)
        per_res_base_path = out_dir / per_res_stem
        # Force one per-residue pass and disable backend pooling to avoid duplicate forward passes.
        print(f'Obtaining embeddings for {model_prefix}...')
        embed_result = module.get_embeddings(
            sequences=sequence_list,
            sequences_base=sequence_base_list,
            save_per_residue_embeddings=True,
            get_embeddings_for_seq_base=bool(get_embeddings_for_seq_base and sequence_base_list is not None),
            pool_method=None,
            mutations=None,
            sep=sep,
            output_path=per_res_base_path,
            layers=model_layers,
            model_name=model_prefix,
            batch_size=batch_size,
            device=device,
        )
        per_res_paths = embed_result.get("per_residue_paths", {})
        if not per_res_paths:
            raise RuntimeError(f"Backend '{backend_name}' did not return per_residue_paths.")
        per_res_arrays = _load_layerwise_arrays(per_res_paths)

        base_per_res_paths = embed_result.get("base_per_residue_paths", {})
        base_per_res_arrays: Optional[Dict[int, np.ndarray]] = None
        if base_per_res_paths:
            base_per_res_arrays = _load_layerwise_arrays(base_per_res_paths)

        # Section 3C: persist per-residue feature if requested.
        if "per_residue" in embedding_suffixes:
            results[per_res_feature_name] = {
                "feature_name": per_res_feature_name,
                "model_prefix": model_prefix,
                "backend": backend_name,
                "artifacts": {
                    "per_residue_paths": per_res_paths,
                    "base_per_residue_paths": base_per_res_paths or None,
                },
            }

        # Section 3D: derive and persist mean-pooled feature from cached per-residue arrays.
        if "mean_pooled" in embedding_suffixes:
            mean_feature_name = f"{model_prefix}_mean_pooled"
            mean_stem = _sanitize_name(mean_feature_name)
            mean_base_path = out_dir / mean_stem
            mean_pooled = compute_pooled_embeddings(per_res_arrays, pool_method="mean", mutations=None, sep=sep)
            mean_paths = save_layerwise_embeddings(
                mean_pooled,
                output_stem=mean_base_path,
                suffix="mean_pooled",
                log_tag="get_plm_encodings",
            )
            base_mean_paths = None
            if base_per_res_arrays is not None and get_embeddings_for_seq_base:
                base_mean = compute_pooled_embeddings(base_per_res_arrays, pool_method="mean", mutations=None, sep=sep)
                base_mean_paths = save_layerwise_embeddings(
                    base_mean,
                    output_stem=mean_base_path,
                    suffix="mean_pooled",
                    file_suffix="_base",
                    log_tag="get_plm_encodings",
                )
            results[mean_feature_name] = {
                "feature_name": mean_feature_name,
                "model_prefix": model_prefix,
                "backend": backend_name,
                "artifacts": {
                    "pooled_paths": mean_paths,
                    "base_pooled_paths": base_mean_paths,
                },
            }

        # Section 3E: derive and persist mutation-pooled feature from cached per-residue arrays.
        if "mut_pooled" in embedding_suffixes:
            mut_feature_name = f"{model_prefix}_mut_pooled"
            mut_stem = _sanitize_name(mut_feature_name)
            mut_base_path = out_dir / mut_stem
            mut_pooled = compute_pooled_embeddings(
                per_res_arrays,
                pool_method="mut",
                mutations=mutations,
                sep=sep,
            )
            mut_paths = save_layerwise_embeddings(
                mut_pooled,
                output_stem=mut_base_path,
                suffix="mut_pooled",
                log_tag="get_plm_encodings",
            )
            base_mut_paths = None
            if base_per_res_arrays is not None and get_embeddings_for_seq_base:
                base_mut = compute_pooled_embeddings(base_per_res_arrays, pool_method="mean", mutations=None, sep=sep)
                base_mut_paths = save_layerwise_embeddings(
                    base_mut,
                    output_stem=mut_base_path,
                    suffix="mut_pooled",
                    file_suffix="_base",
                    log_tag="get_plm_encodings",
                )
            results[mut_feature_name] = {
                "feature_name": mut_feature_name,
                "model_prefix": model_prefix,
                "backend": backend_name,
                "artifacts": {
                    "pooled_paths": mut_paths,
                    "base_pooled_paths": base_mut_paths,
                },
            }

        # Section 3F: optionally delete intermediate per-residue files when not requested.
        keep_per_res = "per_residue" in embedding_suffixes
        if not keep_per_res:
            _delete_artifact_paths(per_res_paths)
            if base_per_res_paths:
                _delete_artifact_paths(base_per_res_paths)

    # Section 4: return only requested features, preserving the original request order.
    ordered_results: Dict[str, Dict[str, Any]] = {}
    for feature_name in ordered_features:
        model_prefix, suffix = _parse_plm_feature_name(feature_name)
        normalized_feature_name = f"{model_prefix}_{_normalize_suffix(suffix)}"
        if normalized_feature_name in results:
            ordered_results[feature_name] = results[normalized_feature_name]
        elif feature_name in results:
            ordered_results[feature_name] = results[feature_name]
        else:
            raise RuntimeError(f"Missing result record for requested PLM feature '{feature_name}'.")

    return ordered_results
