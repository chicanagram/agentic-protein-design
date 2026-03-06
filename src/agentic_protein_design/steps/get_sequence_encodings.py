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
from tools.encodings.plm_encodings import get_plm_encodings
from tools.utils.seq_utils import fetch_sequences_from_fasta, normalize_sequences


FASTA_SUFFIXES = {".fasta", ".fa", ".faa", ".fna"}


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


def get_sequence_encodings(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse sequence input, split feature sets, and dispatch encoding generation.
    """
    # Section 1: resolve high-level inputs.
    sequence_input = str(inputs.get("sequence_input", "") or "").strip()
    # Section 2: split requested feature sets by encoding backend.
    split_sets = split_feature_sets(inputs.get("feature_sets", FEATURE_SETS_DEFAULT))

    # Section 3: parse input sequences and optional metadata (or base-only mode).
    if sequence_input:
        parsed = parse_sequence_input(
            sequence_input=sequence_input,
            sequence_col=str(inputs.get("sequence_col", "sequence")),
            sequence_base_col=str(inputs.get("sequence_base_col", "sequence_base")),
            mutation_col=str(inputs.get("mutation_col", "mutations")),
            sequence_base=inputs.get("sequence_base"),
        )
    else:
        sequence_base_list = _normalize_sequence_base_input(inputs.get("sequence_base"), n_rows=1)
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

    # Section 4: validate feature/input compatibility.
    if split_sets["classical"] and parsed["sequence_list"] is None:
        raise ValueError("Classical encodings require sequence inputs from CSV/FASTA; base-only mode is unsupported.")
    if split_sets["plm"] and parsed["sequence_list"] is None:
        non_llr = [f for f in split_sets["plm"] if not str(f).endswith("_LLR")]
        if non_llr:
            raise ValueError(
                "Base-only mode supports only PLM *_LLR feature sets. "
                f"Unsupported in this mode: {non_llr}"
            )

    # Section 5: resolve output directory from root_key + subfolder settings.
    root_key = str(inputs.get("root_key", "examples") or "").strip() or "examples"
    if root_key not in address_dict:
        raise KeyError(f"Unknown root_key: {root_key}. Available keys: {sorted(address_dict.keys())}")
    project_root = resolve_project_root()
    data_fbase = (project_root / address_dict[root_key]).resolve()
    encodings_subfolder = str(inputs.get("encodings_subfolder", "encodings/") or "").strip().strip("/")
    data_subfolder = str(inputs.get("data_subfolder", "") or "").strip().strip("/")
    encodings_path = data_fbase / encodings_subfolder
    if data_subfolder:
        encodings_path = encodings_path / data_subfolder
    encodings_path.mkdir(parents=True, exist_ok=True)
    encodings_dir = str(encodings_path.resolve())

    # Section 6: run encoding generation backend(s) as requested.
    classical_results = {}
    plm_results = {}

    if split_sets["classical"]:
        classical_results = get_classical_encodings(
            classical_feature_sets=split_sets["classical"],
            sequence_list=parsed["sequence_list"],
            sequence_base_list=parsed["sequence_base_list"],
            encodings_dir=encodings_dir,
            filename_prefix=str(inputs.get("filename_prefix", "") or ""),
            get_embeddings_for_seq_base=bool(inputs.get("get_embeddings_for_seq_base", False)),
            max_length=inputs.get("classical_max_length"),
        )

    if split_sets["plm"]:
        plm_results = get_plm_encodings(
            plm_feature_sets=split_sets["plm"],
            sequence_list=parsed["sequence_list"],
            sequence_base_list=parsed["sequence_base_list"],
            encodings_dir=encodings_dir,
            filename_prefix=str(inputs.get("filename_prefix", "") or ""),
            marginal_type=str(inputs.get("marginal_type", "wt")),
            llr_cache_vect_filename_prefix=str(inputs.get("llr_cache_vect_filename_prefix", "") or "").strip(),
            resave_llr_cache_if_found=bool(inputs.get("resave_llr_cache_if_found", False)),
            mutations=parsed["mutations_list"],
            sep=str(inputs.get("mutations_sep", "+")),
            layers=inputs.get("layers"),
            batch_size=int(inputs.get("batch_size", 4)),
            device=inputs.get("device"),
            get_embeddings_for_seq_base=bool(inputs.get("get_embeddings_for_seq_base", False)),
            save_per_residue_embeddings=bool(inputs.get("save_per_residue_embeddings", True)),
        )

    # Section 7: return consolidated execution metadata and outputs.
    return {
        "status": "ok",
        "input": parsed,
        "feature_sets": split_sets,
        "encodings_dir": encodings_dir,
        "classical_results": classical_results,
        "plm_results": plm_results,
    }
