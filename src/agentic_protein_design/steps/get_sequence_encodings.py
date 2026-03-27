from __future__ import annotations

if __name__ == "__main__" and __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parents[3]
    _src_root = _repo_root / "src"
    for _path in (str(_repo_root), str(_src_root)):
        if _path not in sys.path:
            sys.path.insert(0, _path)

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from agentic_protein_design.core.paths import resolve_project_root
from project_config.feature_registry import (
    CLASSICAL_ENCODING_FEATURE_SETS,
    FEATURE_SETS_DEFAULT,
    PLM_MODELS_DICT,
    PLM_ENCODING_FEATURE_SETS,
)
from project_config.variables import address_dict
from tools.encodings.classical_encodings import get_classical_encodings
from tools.encodings.common import _sanitize_name
from tools.encodings.plm_encodings import get_plm_encodings
from tools.utils.seq_utils import fetch_sequences_from_fasta, normalize_sequences


FASTA_SUFFIXES = {".fasta", ".fa", ".faa", ".fna"}
PLM_FEATURE_SUFFIXES = ("_mean_pooled", "_mut_pooled", "_svd_pooled", "_per_residue", "_meanPLL", "_LLR")
PLM_CHUNKABLE_SUFFIXES = ("_mean_pooled", "_mut_pooled", "_svd_pooled")
EMBEDDING_TRACE_SUFFIXES = ("_per_residue", "_mean_pooled", "_mut_pooled")


def default_user_inputs() -> Dict[str, Any]:
    """Return editable defaults for sequence-encoding runs."""
    return {
        "root_key": "examples",
        "data_subfolder": "",
        "encodings_subfolder": "encodings/",
        "filename_prefix": "",
        "sequence_input": "",
        "sequence_col": "sequence",
        "sequence_base_col": "sequence_base",
        "mutation_col": "mutations",
        "sequence_base": None,
        "feature_sets": list(FEATURE_SETS_DEFAULT),
        "get_embeddings_for_seq_base": False,
        "classical_max_length": None,
        "marginal_type": "wt",
        "llr_cache_vect_filename_prefix": "",
        "resave_llr_cache_if_found": False,
        "mutations_sep": "+",
        "layers": {k: list(v) for k, v in PLM_MODELS_DICT.items()},
        "n_components": 256,
        "sample_mutants_for_svd": False,
        "svd_data_reduction": None,
        "chunk_size": 4000,
        "cleanup_chunk_files": True,
        "batch_size": 4,
        "device": None,
        "save_per_residue_embeddings": True,
    }


def split_feature_sets(
    feature_sets: Optional[Union[str, Sequence[str]]] = None,
) -> Dict[str, List[str]]:
    """
    Split requested feature-set names into classical vs PLM groups.

    Unknown feature-set names raise an error.
    """
    # Section 1: normalize requested feature-set names.
    if feature_sets is None:
        requested = list(FEATURE_SETS_DEFAULT)
    elif isinstance(feature_sets, str):
        requested = [x.strip() for x in feature_sets.split(",") if x.strip()]
    else:
        requested = [str(x).strip() for x in feature_sets if str(x).strip()]
    if not requested:
        requested = list(FEATURE_SETS_DEFAULT)

    # Section 2: preserve order while de-duplicating names.
    deduped: List[str] = []
    seen = set()
    for name in requested:
        if name not in seen:
            deduped.append(name)
            seen.add(name)
    requested = deduped

    # Section 2: split by backend ownership.
    classical = [f for f in requested if f in CLASSICAL_ENCODING_FEATURE_SETS]
    plm = [f for f in requested if f in PLM_ENCODING_FEATURE_SETS]

    # Section 3: reject unknown feature names early.
    unknown = [
        f
        for f in requested
        if f not in CLASSICAL_ENCODING_FEATURE_SETS and f not in PLM_ENCODING_FEATURE_SETS
    ]
    if unknown:
        raise ValueError(
            "Unknown feature sets: "
            f"{unknown}. Available feature sets are defined in project_config/feature_registry.py"
        )

    return {
        "requested": requested,
        "classical": classical,
        "plm": plm,
    }


def _extract_required_sequence_column(df: pd.DataFrame, sequence_col: str, input_path: Path) -> List[str]:
    # Section 1: enforce required column and null safety.
    if sequence_col not in df.columns:
        raise ValueError(f"Column '{sequence_col}' not found in CSV: {input_path}")

    seq_series = df[sequence_col]
    if seq_series.isnull().any():
        null_idx = seq_series[seq_series.isnull()].index.tolist()[:5]
        raise ValueError(f"Found null values in '{sequence_col}' at rows {null_idx}.")

    # Section 2: normalize and enforce non-empty sequence rows.
    sequence_list = normalize_sequences([str(x).strip() for x in seq_series.tolist()])
    if len(sequence_list) != len(seq_series):
        raise ValueError(f"Could not normalize all values in '{sequence_col}' into non-empty sequences.")
    empty_idx = [i for i, seq in enumerate(sequence_list) if not seq]
    if empty_idx:
        raise ValueError(f"Found empty sequence strings in '{sequence_col}' at rows {empty_idx[:5]}.")
    return sequence_list


def _normalize_sequence_base_input(
    sequence_base: Optional[Union[str, Sequence[Optional[str]]]],
    n_rows: int = 1,
) -> Optional[List[str]]:
    """Normalize optional sequence_base into a list of non-empty sequences."""
    # Section 1: no sequence_base provided.
    if sequence_base is None:
        return None

    # Section 2: single-sequence input.
    if isinstance(sequence_base, str):
        normalized = normalize_sequences(sequence_base)
        if not normalized:
            return None
        return [normalized[0]] * max(int(n_rows), 1)

    # Section 3: list input.
    raw = [str(x).strip() if x is not None else "" for x in sequence_base]
    if not any(raw):
        return None
    if any(not x for x in raw):
        raise ValueError("sequence_base list contains empty rows; provide non-empty sequences only.")
    normalized = normalize_sequences(raw)
    if len(normalized) == 1 and n_rows > 1:
        return [normalized[0]] * n_rows
    if len(normalized) != n_rows:
        raise ValueError(
            f"sequence_base list length ({len(normalized)}) must be 1 or match n_rows ({n_rows})."
        )
    return normalized


def _resolve_sequence_base_user_input(
    sequence_base: Optional[Union[str, Sequence[Optional[str]]]],
    data_fbase: Optional[Path] = None,
) -> Optional[Union[str, Sequence[Optional[str]]]]:
    """
    Resolve `sequence_base` when provided as a FASTA filepath.

    Supported inputs:
    - `None`: unchanged.
    - explicit amino-acid string: unchanged.
    - FASTA path string (absolute or relative to `data_fbase`): replaced with first sequence in FASTA.
    - list input: unchanged.
    """
    # Section 1: no input or non-string types pass through unchanged.
    if sequence_base is None or not isinstance(sequence_base, str):
        return sequence_base

    token = str(sequence_base).strip()
    if not token:
        return None

    # Section 2: treat FASTA-like strings as file paths and load first sequence.
    p = Path(token).expanduser()
    if p.suffix.lower() in FASTA_SUFFIXES:
        candidates: List[Path] = []
        if p.is_absolute():
            candidates.append(p)
        else:
            if data_fbase is not None:
                candidates.append((Path(data_fbase) / p).resolve())
            candidates.append(p.resolve())

        fasta_path = next((c for c in candidates if c.exists()), None)
        if fasta_path is None:
            raise FileNotFoundError(
                f"sequence_base FASTA file not found: '{token}'. "
                f"Checked: {[str(c) for c in candidates]}"
            )

        sequences, _, _ = fetch_sequences_from_fasta(str(fasta_path))
        if not sequences:
            raise ValueError(f"No sequences found in sequence_base FASTA: {fasta_path}")
        return str(sequences[0]).strip()

    # Section 3: explicit sequence string path.
    return sequence_base


def parse_sequence_input(
    *,
    sequence_input: Union[str, Path],
    sequence_col: str = "sequence",
    sequence_base_col: str = "sequence_base",
    mutation_col: str = "mutations",
    sequence_base: Optional[Union[str, Sequence[Optional[str]]]] = None,
) -> Dict[str, Any]:
    """
    Parse CSV or FASTA input into sequence lists used by encoding pipelines.

    Returns keys: `sequence_list`, `sequence_base_list`, `mutations_list`.
    """
    # Section 1: resolve and validate input file path.
    input_path = Path(sequence_input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Section 2: route parser logic by file extension.
    suffix = input_path.suffix.lower()

    # CSV parsing pathway.
    if suffix == ".csv":
        # Section 2A: parse CSV sequence/base/mutation columns.
        df = pd.read_csv(input_path)
        sequence_list = _extract_required_sequence_column(df, sequence_col, input_path)
        n_seq = len(sequence_list)

        # Section 2A.1: resolve sequence_base list from CSV column or fallback input.
        sequence_base_list: Optional[List[str]] = None
        if sequence_base_col in df.columns:
            raw_base = [str(x).strip() if pd.notna(x) else "" for x in df[sequence_base_col].tolist()]
            if any(raw_base):
                if any(not x for x in raw_base):
                    raise ValueError(
                        f"Column '{sequence_base_col}' contains empty rows; fill all rows or remove the column."
                    )
                sequence_base_list = normalize_sequences(raw_base)
                if len(sequence_base_list) != n_seq:
                    raise ValueError(
                        f"Could not normalize all values in '{sequence_base_col}' into non-empty sequences."
                    )
            else:
                sequence_base_list = _normalize_sequence_base_input(sequence_base, n_rows=n_seq)
        else:
            sequence_base_list = _normalize_sequence_base_input(sequence_base, n_rows=n_seq)

        mutations_list: Optional[List[str]] = None
        if mutation_col in df.columns:
            raw_mutations = [str(x).strip() for x in df[mutation_col].fillna("").tolist()]
            if any(raw_mutations):
                mutations_list = raw_mutations

        return {
            "input_path": str(input_path),
            "input_type": "csv",
            "n_sequences": n_seq,
            "sequence_list": sequence_list,
            "sequence_base_list": sequence_base_list,
            "mutations_list": mutations_list,
        }

    # FASTA parsing pathway.
    if suffix in FASTA_SUFFIXES:
        # Section 2B: parse FASTA sequences and optional user-provided base sequence.
        sequence_list, sequence_names, _ = fetch_sequences_from_fasta(str(input_path))
        if not sequence_list:
            raise ValueError(f"No sequences found in FASTA: {input_path}")
        raw_sequence_list = [str(seq).strip() for seq in sequence_list]
        sequence_list = normalize_sequences(raw_sequence_list)
        if len(sequence_list) != len(raw_sequence_list):
            raise ValueError(f"Could not normalize all FASTA entries into non-empty sequences: {input_path}")
        n_seq = len(sequence_list)
        sequence_base_list = _normalize_sequence_base_input(sequence_base, n_rows=n_seq)

        return {
            "input_path": str(input_path),
            "input_type": "fasta",
            "n_sequences": n_seq,
            "sequence_names": sequence_names,
            "sequence_list": sequence_list,
            "sequence_base_list": sequence_base_list,
            "mutations_list": None,
        }

    raise ValueError(
        f"Unsupported input format '{suffix}'. Provide a CSV or FASTA file ({sorted(FASTA_SUFFIXES)})."
    )


def _slice_or_none(values: Optional[Sequence[Any]], start: int, end: int):
    if values is None:
        return None
    return list(values[start:end])


def _get_model_prefix(feature_name: str) -> str:
    name = str(feature_name).strip()
    for suffix in PLM_FEATURE_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _split_chunked_plm_features(plm_features: Sequence[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Split PLM features for chunk mode into:
    - per_residue_features (unsupported in chunk mode)
    - chunked_features (pooled embeddings)
    - passthrough_features (LLR/meanPLL)
    """
    per_residue_features = [f for f in plm_features if str(f).endswith("_per_residue")]
    chunked_features = [f for f in plm_features if str(f).endswith(PLM_CHUNKABLE_SUFFIXES)]
    passthrough_features = [f for f in plm_features if f not in chunked_features]
    return per_residue_features, chunked_features, passthrough_features


def _collect_embedding_shape_trace(plm_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Collect compact embedding shape trace payload from PLM results."""
    embedding_shape_trace: Dict[str, Any] = {}
    for feature_name, meta in plm_results.items():
        if not str(feature_name).endswith(EMBEDDING_TRACE_SUFFIXES):
            continue
        shape_by_layer = meta.get("shape_by_layer")
        base_shape_by_layer = meta.get("base_shape_by_layer")
        if shape_by_layer is None and base_shape_by_layer is None:
            continue
        embedding_shape_trace[feature_name] = {
            "shape_by_layer": shape_by_layer,
            "base_shape_by_layer": base_shape_by_layer,
        }
    return embedding_shape_trace


def _build_plm_call_kwargs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Build shared `get_plm_encodings` kwargs from user inputs."""
    return {
        "marginal_type": str(inputs.get("marginal_type", "wt")),
        "llr_cache_vect_filename_prefix": str(inputs.get("llr_cache_vect_filename_prefix", "") or "").strip(),
        "resave_llr_cache_if_found": bool(inputs.get("resave_llr_cache_if_found", False)),
        "sep": str(inputs.get("mutations_sep", "+")),
        "layers": inputs.get("layers"),
        "n_components": int(inputs.get("n_components", 256)),
        "sample_mutants_for_svd": bool(inputs.get("sample_mutants_for_svd", False)),
        "svd_data_reduction": inputs.get("svd_data_reduction", None),
        "batch_size": int(inputs.get("batch_size", 4)),
        "device": inputs.get("device"),
    }


def _run_chunked_pooled_plm_features(
    *,
    plm_feature_sets: Sequence[str],
    sequence_list: Sequence[str],
    sequence_base_list: Optional[Sequence[str]],
    mutations_list: Optional[Sequence[str]],
    encodings_dir: str,
    filename_prefix: str,
    chunk_size: int,
    cleanup_chunk_files: bool,
    plm_kwargs: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Run pooled PLM features in chunks and merge chunk outputs."""
    # Preserve requested order while grouping by model.
    model_to_features: Dict[str, List[str]] = {}
    ordered_models: List[str] = []
    for feat in plm_feature_sets:
        model = _get_model_prefix(feat)
        if model not in model_to_features:
            model_to_features[model] = []
            ordered_models.append(model)
        model_to_features[model].append(feat)

    n = len(sequence_list)
    merged_all: Dict[str, Dict[str, Any]] = {}
    n_chunks = int(np.ceil(n / chunk_size))

    # Run one model across all chunks before moving to the next model.
    for model in ordered_models:
        model_features = model_to_features[model]
        chunk_results: List[Dict[str, Dict[str, Any]]] = []
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            chunk_idx = (start // chunk_size) + 1
            print(f"[chunk:{model}] Processing {start}:{end} ({chunk_idx}/{n_chunks})")
            chunk_res = get_plm_encodings(
                plm_feature_sets=model_features,
                sequence_list=sequence_list[start:end],
                sequence_base_list=_slice_or_none(sequence_base_list, start, end),
                encodings_dir=encodings_dir,
                filename_prefix=f"{filename_prefix}chunk{chunk_idx:03d}_",
                mutations=_slice_or_none(mutations_list, start, end),
                get_embeddings_for_seq_base=False,
                **plm_kwargs,
            )
            chunk_results.append(chunk_res)

        merged_model = _merge_chunked_plm_results(
            chunk_results=chunk_results,
            requested_features=model_features,
            encodings_dir=encodings_dir,
            filename_prefix=filename_prefix,
            cleanup_chunk_files=cleanup_chunk_files,
        )
        merged_all.update(merged_model)

    return merged_all


def _merge_chunked_plm_results(
    *,
    chunk_results: List[Dict[str, Dict[str, Any]]],
    requested_features: Sequence[str],
    encodings_dir: Union[str, Path],
    filename_prefix: str,
    cleanup_chunk_files: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """
    Merge chunk-level pooled embedding outputs into final full-dataset arrays.
    """
    out_dir = Path(encodings_dir)
    merged: Dict[str, Dict[str, Any]] = {}
    for feature_name in requested_features:
        chunk_feature_meta = [cr[feature_name] for cr in chunk_results if feature_name in cr]
        if not chunk_feature_meta:
            continue
        artifacts0 = chunk_feature_meta[0].get("artifacts", {})
        pooled_key = "pooled_paths" if "pooled_paths" in artifacts0 else "per_residue_paths"
        if pooled_key not in artifacts0:
            # Non-artifact features (e.g., scalar score outputs) are not chunk-merged in this path.
            continue
        layer_keys = sorted(list(artifacts0[pooled_key].keys()), key=lambda x: int(x))
        final_paths: Dict[str, str] = {}
        final_shapes: Dict[int, List[int]] = {}
        for layer in layer_keys:
            arrays = [
                np.load(str(meta["artifacts"][pooled_key][layer]), allow_pickle=False)
                for meta in chunk_feature_meta
            ]
            concat = np.concatenate(arrays, axis=0)
            final_stem = out_dir / f"{str(filename_prefix)}{_sanitize_name(feature_name)}"
            final_path = final_stem.parent / f"{final_stem.name}-{int(layer)}.npy"
            np.save(str(final_path), concat)
            final_paths[str(int(layer))] = str(final_path)
            final_shapes[int(layer)] = list(concat.shape)

            if cleanup_chunk_files:
                for meta in chunk_feature_meta:
                    try:
                        Path(meta["artifacts"][pooled_key][layer]).unlink(missing_ok=True)
                    except TypeError:
                        p = Path(meta["artifacts"][pooled_key][layer])
                        if p.exists():
                            p.unlink()

        merged[feature_name] = {
            "feature_name": feature_name,
            "model_prefix": chunk_feature_meta[0].get("model_prefix"),
            "plm_name": chunk_feature_meta[0].get("plm_name"),
            "artifacts": {
                pooled_key: final_paths,
                "base_pooled_paths": None,
            },
            "shape_by_layer": final_shapes,
        }
    return merged


def get_sequence_encodings(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse sequence input, split feature sets, and dispatch encoding generation.
    """
    # Section 1: resolve high-level inputs.
    sequence_input = str(inputs.get("sequence_input", "") or "").strip()
    print('sequence_input:', sequence_input)
    # Section 2: split requested feature sets by encoding backend.
    split_sets = split_feature_sets(inputs.get("feature_sets", FEATURE_SETS_DEFAULT))

    # Section 3: resolve output root and preprocess sequence_base filepath inputs.
    root_key = str(inputs.get("root_key", "examples") or "").strip() or "examples"
    if root_key not in address_dict:
        raise KeyError(f"Unknown root_key: {root_key}. Available keys: {sorted(address_dict.keys())}")
    project_root = resolve_project_root()
    data_fbase = (project_root / address_dict[root_key]).resolve()
    sequence_base_input = _resolve_sequence_base_user_input(inputs.get("sequence_base"), data_fbase)

    # Section 4: parse input sequences and optional metadata (or base-only mode).
    if sequence_input:
        parsed = parse_sequence_input(
            sequence_input=sequence_input,
            sequence_col=str(inputs.get("sequence_col", "sequence")),
            sequence_base_col=str(inputs.get("sequence_base_col", "sequence_base")),
            mutation_col=str(inputs.get("mutation_col", "mutations")),
            sequence_base=sequence_base_input,
        )
    else:
        sequence_base_list = _normalize_sequence_base_input(sequence_base_input, n_rows=1)
        if not sequence_base_list:
            raise ValueError("Provide either 'sequence_input' (CSV/FASTA) or a non-empty 'sequence_base'.")
        parsed = {
            "input_path": None,
            "input_type": "base_only",
            "n_sequences": 0,
            "sequence_list": None,
            "sequence_base_list": sequence_base_list,
            "mutations_list": None,
        }

    # Section 5: validate feature/input compatibility.
    if split_sets["classical"] and parsed["sequence_list"] is None:
        raise ValueError("Classical encodings require sequence inputs from CSV/FASTA; base-only mode is unsupported.")
    if split_sets["plm"] and parsed["sequence_list"] is None:
        non_llr = [f for f in split_sets["plm"] if not str(f).endswith("_LLR")]
        if non_llr:
            raise ValueError(
                "Base-only mode supports only PLM *_LLR feature sets. "
                f"Unsupported in this mode: {non_llr}"
            )

    # Section 6: resolve output directory from root_key + subfolder settings.
    encodings_subfolder = str(inputs.get("encodings_subfolder", "encodings/") or "").strip().strip("/")
    data_subfolder = str(inputs.get("data_subfolder", "") or "").strip().strip("/")
    encodings_path = data_fbase / encodings_subfolder
    if data_subfolder:
        encodings_path = encodings_path / data_subfolder
    encodings_path.mkdir(parents=True, exist_ok=True)
    encodings_dir = str(encodings_path.resolve())

    # Section 7: run encoding generation backend(s) as requested.
    classical_results = {}
    plm_results = {}
    filename_prefix = str(inputs.get("filename_prefix", "") or "")

    if split_sets["classical"]:
        classical_results = get_classical_encodings(
            classical_feature_sets=split_sets["classical"],
            sequence_list=parsed["sequence_list"],
            sequence_base_list=parsed["sequence_base_list"],
            encodings_dir=encodings_dir,
            filename_prefix=filename_prefix,
            get_embeddings_for_seq_base=bool(inputs.get("get_embeddings_for_seq_base", False)),
            max_length=inputs.get("classical_max_length"),
        )

    if split_sets["plm"]:
        plm_kwargs = _build_plm_call_kwargs(inputs)
        chunk_size = int(inputs.get("chunk_size", 4000))
        cleanup_chunk_files = bool(inputs.get("cleanup_chunk_files", True))
        sequence_list = parsed["sequence_list"]
        use_chunking = bool(sequence_list is not None and len(sequence_list) > chunk_size)

        # For large datasets, chunk only pooled embedding features.
        # Non-embedding PLM features (e.g. LLR/meanPLL) run as regular full calls.
        if use_chunking:
            per_residue_features, chunked_features, passthrough_features = _split_chunked_plm_features(
                split_sets["plm"]
            )
            if per_residue_features:
                raise ValueError(
                    "Chunked mode does not support PLM per-residue features. "
                    f"Please remove: {per_residue_features}"
                )

            # Section 7A: run pooled embedding features in chunks and merge outputs.
            chunked_results: Dict[str, Dict[str, Any]] = {}
            if chunked_features:
                chunked_results = _run_chunked_pooled_plm_features(
                    plm_feature_sets=chunked_features,
                    sequence_list=sequence_list,
                    sequence_base_list=parsed["sequence_base_list"],
                    mutations_list=parsed["mutations_list"],
                    encodings_dir=encodings_dir,
                    filename_prefix=filename_prefix,
                    chunk_size=chunk_size,
                    cleanup_chunk_files=cleanup_chunk_files,
                    plm_kwargs=plm_kwargs,
                )

            # Section 7B: run non-chunked PLM features (e.g. LLR/meanPLL) normally.
            passthrough_results: Dict[str, Dict[str, Any]] = {}
            if passthrough_features:
                passthrough_results = get_plm_encodings(
                    plm_feature_sets=passthrough_features,
                    sequence_list=parsed["sequence_list"],
                    sequence_base_list=parsed["sequence_base_list"],
                    encodings_dir=encodings_dir,
                    filename_prefix=filename_prefix,
                    mutations=parsed["mutations_list"],
                    get_embeddings_for_seq_base=bool(inputs.get("get_embeddings_for_seq_base", False)),
                    **plm_kwargs,
                )
            plm_results = {**passthrough_results, **chunked_results}
        else:
            plm_results = get_plm_encodings(
                plm_feature_sets=split_sets["plm"],
                sequence_list=parsed["sequence_list"],
                sequence_base_list=parsed["sequence_base_list"],
                encodings_dir=encodings_dir,
                filename_prefix=filename_prefix,
                mutations=parsed["mutations_list"],
                get_embeddings_for_seq_base=bool(inputs.get("get_embeddings_for_seq_base", False)),
                **plm_kwargs,
            )

    # Section 8: collect compact shape trace for embedding artifacts.
    embedding_shape_trace = _collect_embedding_shape_trace(plm_results)

    # Section 9: return consolidated execution metadata and outputs.
    return {
        "status": "ok",
        "input": parsed,
        "feature_sets": split_sets,
        "encodings_dir": encodings_dir,
        "classical_results": classical_results,
        "plm_results": plm_results,
        "trace": {
            "embedding_shapes": embedding_shape_trace,
        },
    }


if __name__ == "__main__":
    # Section 1: mirror notebook-style user inputs for IDE/script execution.
    user_inputs = default_user_inputs()

    # Section 1A: Configure output root and subfolders.
    user_inputs["root_key"] = "MUTAGENESIS-DATA-BENCHMARKS"
    user_inputs["data_subfolder"] = "D7PM05_CLYGR_Somermeyer_2022"
    user_inputs["encodings_subfolder"] = "encodings/"
    filename = f'{user_inputs["data_subfolder"]}.csv'
    user_inputs["filename_prefix"] = filename.split(".")[0] + "_" if filename is not None else ""

    # Section 1B: Configure sequence input source.
    project_root = resolve_project_root()
    data_root = (project_root / Path(address_dict[user_inputs["root_key"]])).resolve()
    user_inputs["sequence_input"] = str(
        data_root / "expdata" / user_inputs["data_subfolder"] / filename
    )

    # Section 1C: Configure columns and optional base-sequence fallback.
    user_inputs["sequence_col"] = "sequence"
    user_inputs["sequence_base_col"] = "sequence_base"
    user_inputs["mutation_col"] = "mutations"
    # Leave as None by default so CSV `sequence_base_col` is used when present.
    # Set this to a FASTA path string (e.g. "sequences/<name>.fasta") if desired.
    # user_inputs["sequence_base"] = None
    user_inputs["sequence_base"] = f'sequences/{user_inputs["data_subfolder"]}.fasta'  # None


    # Section 1D: Configure feature sets.
    user_inputs["feature_sets"] = [
        # "one_hot",
        # "georgiev",
        # "esm2-650m_LLR",
        # "esm2-650m_meanPLL",
        # "esm2-650m_per_residue",
        "esm2-650m_mean_pooled",
        "esmc-600m_LLR",
        # "esm2-650m_meanPLL",
        # "esmc-600m_per_residue",
        "esmc-600m_mean_pooled",
        # "poet2_LLR",
        # "poet2_meanPLL",
        # "poet2_per_residue",
        # "poet2_mean_pooled",
        # "poet2_svd_pooled",
    ]

    # Section 1E: Configure runtime controls.
    user_inputs["get_embeddings_for_seq_base"] = False
    user_inputs["classical_max_length"] = None
    user_inputs["marginal_type"] = "masked"
    user_inputs["llr_cache_vect_filename_prefix"] = user_inputs["data_subfolder"] + "_"
    user_inputs["resave_llr_cache_if_found"] = False
    user_inputs["mutations_sep"] = "+"
    user_inputs["layers"] = {"esm2-650m": [33], "esmc-600m": [36], "poet2": [12]}
    user_inputs["n_components"] = 1024
    user_inputs["sample_mutants_for_svd"] = False
    user_inputs["svd_data_reduction"] = None
    user_inputs["chunk_size"] = 3000
    user_inputs["cleanup_chunk_files"] = True
    user_inputs["batch_size"] = 4
    user_inputs["device"] = None

    # Section 2: Execute and print concise run summary.
    result = get_sequence_encodings(user_inputs)
    print("status:", result.get("status", ""))
    print("encodings_dir:", result.get("encodings_dir", ""))
    print("n_classical_features:", len(result.get("feature_sets", {}).get("classical", [])))
    print("n_plm_features:", len(result.get("feature_sets", {}).get("plm", [])))
    print("classical result keys:", sorted(result.get("classical_results", {}).keys()))
    print("plm result keys:", sorted(result.get("plm_results", {}).keys()))
