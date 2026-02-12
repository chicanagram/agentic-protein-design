from __future__ import annotations

from pathlib import Path
from typing import Dict, MutableMapping, Sequence


def resolve_input_path(data_root: Path, path_value: str) -> Path:
    """Resolve an input path relative to a selected data root."""
    p = Path(path_value).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (data_root / p).resolve()


def _read_nonempty_lines(path: Path) -> Sequence[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def apply_optional_text_inputs(
    user_inputs: MutableMapping[str, object],
    input_paths: Dict[str, str],
    data_root: Path,
) -> MutableMapping[str, object]:
    """
    Populate user_inputs from optional text files when provided.
    - seed_sequences_file: one sequence name per line
    - constraints_file: one constraint per line
    """
    seed_file_val = str(input_paths.get("seed_sequences_file", "")).strip()
    if seed_file_val:
        seed_file = resolve_input_path(data_root, seed_file_val)
        if seed_file.exists():
            seed_lines = _read_nonempty_lines(seed_file)
            if seed_lines:
                user_inputs["seed_sequences"] = list(seed_lines)

    constraints_file_val = str(input_paths.get("constraints_file", "")).strip()
    if constraints_file_val:
        constraints_file = resolve_input_path(data_root, constraints_file_val)
        if constraints_file.exists():
            constraint_lines = _read_nonempty_lines(constraints_file)
            if constraint_lines:
                user_inputs["constraints"] = list(constraint_lines)

    return user_inputs
