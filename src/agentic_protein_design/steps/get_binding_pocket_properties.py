from __future__ import annotations

if __name__ == "__main__" and __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parents[3]
    _src_root = _repo_root / "src"
    for _path in (str(_repo_root), str(_src_root)):
        if _path not in sys.path:
            sys.path.insert(0, _path)

from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd

from agentic_protein_design.core.paths import setup_data_root
from agentic_protein_design.core.pipeline_utils import safe_read_csv


REQUIRED_SUBFOLDERS = ["pdb", "msa", "sce", "processed"]


def default_user_inputs() -> Dict[str, Any]:
    """
    Return editable defaults for binding-pocket property extraction.

    Returns:
        User input dictionary for either ligand-aware or ligand-free pocket analysis.
    """
    return {
        "root_key": "examples",
        "data_subfolder": "",
        "ligand_present": False,
        "protein_molname": "A",
        "ligand_molname": "D",
        "dist_thres": 6,
        "reactive_center_target": {'protein': None, 'cofactor': None, 'ligand': None},
        "keep_pos_with_aa_variation_only": True,
        "plot_properties": False,
        "analyse_binding_pocket_without_ligand": True,
        "seq_align_fname": "reps_ali.fasta",
        "binding_pocket_residues_fname": "residues_near_ligand.csv",
        "struct_csv_subdirectory_name": "structure_csv",
        "pocket_residues_source": "csv",  # csv | inline
        "pocket_residues_dict": {},
        "struct_dict": {},
    }


def _resolve_work_dirs(root_key: str, data_subfolder: str, struct_csv_subdirectory_name: str) -> Dict[str, Path]:
    """
    Resolve standard directories for binding-pocket workflows.

    Args:
        root_key: Key in `address_dict`.
        data_subfolder: Nested project subfolder under the selected root.
        struct_csv_subdirectory_name: Name for structure CSV output folder under the PDB directory.

    Returns:
        Dict of resolved directories.
    """
    data_root, resolved = setup_data_root(root_key, REQUIRED_SUBFOLDERS)
    sub = str(data_subfolder or "").strip().strip("/")
    pdb_dir = resolved["pdb"] / sub if sub else resolved["pdb"]
    msa_dir = resolved["msa"] / sub if sub else resolved["msa"]
    sce_dir = resolved["sce"] / sub if sub else resolved["sce"]
    processed_dir = resolved["processed"] / "08_get_binding_pocket_properties"
    if sub:
        processed_dir = processed_dir / sub
    struct_csv_dir = pdb_dir / str(struct_csv_subdirectory_name or "structure_csv").strip().strip("/")
    for folder in (pdb_dir, msa_dir, sce_dir, processed_dir, struct_csv_dir):
        folder.mkdir(parents=True, exist_ok=True)
    return {
        "data_root": data_root,
        "pdb_dir": pdb_dir,
        "msa_dir": msa_dir,
        "sce_dir": sce_dir,
        "processed_dir": processed_dir,
        "struct_csv_dir": struct_csv_dir,
    }


def _load_pocket_residues_from_csv(csv_path: Path) -> Dict[str, list[int]]:
    """
    Load a per-structure pocket-residue mapping from a CSV file.

    Expected columns:
        - `struct_name`
        - `res_num`

    Returns:
        Dict mapping structure name to list of residue numbers.
    """
    df = safe_read_csv(csv_path)
    if not {"struct_name", "res_num"}.issubset(df.columns):
        raise ValueError(f"Pocket residue CSV must contain 'struct_name' and 'res_num' columns: {csv_path}")
    grouped = (
        df.dropna(subset=["struct_name", "res_num"])
        .groupby("struct_name")["res_num"]
        .apply(lambda values: [int(v) for v in values.tolist()])
        .to_dict()
    )
    return grouped


def _normalize_pocket_residues_dict(raw_mapping: Dict[str, Iterable[Any]]) -> Dict[str, list[int]]:
    """
    Normalize a user-provided pocket residue dict into `str -> list[int]`.
    """
    out: Dict[str, list[int]] = {}
    for key, values in (raw_mapping or {}).items():
        out[str(key)] = [int(v) for v in list(values)]
    return out


def run_binding_pocket_property_extraction(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run ligand-aware or ligand-free binding-pocket property extraction.

    Args:
        inputs: User input dictionary from `default_user_inputs()`.

    Returns:
        Dict containing run metadata, output paths, and available tabular results.
    """
    root_key = str(inputs.get("root_key", "examples"))
    data_subfolder = str(inputs.get("data_subfolder", "") or "")
    ligand_present = bool(inputs.get("ligand_present", False))
    dirs = _resolve_work_dirs(
        root_key=root_key,
        data_subfolder=data_subfolder,
        struct_csv_subdirectory_name=str(inputs.get("struct_csv_subdirectory_name", "structure_csv")),
    )

    pdb_dir = dirs["pdb_dir"]
    msa_dir = dirs["msa_dir"]
    sce_dir = dirs["sce_dir"]
    struct_csv_dir = dirs["struct_csv_dir"]

    if ligand_present:
        from tools.struct.analyse_binding_pocket_with_ligand import LigandPocketAnalysis

        struct_dict = {str(k): str(v) for k, v in dict(inputs.get("struct_dict", {})).items()}
        if not struct_dict:
            raise ValueError("ligand_present=True requires a non-empty `struct_dict` mapping display names to PDB basenames.")

        analysis = LigandPocketAnalysis(
            pdb_dir=f"{pdb_dir}/",
            sce_dir=f"{sce_dir}/",
            msa_dir=f"{msa_dir}/",
            struct_csv_dir=f"{struct_csv_dir}/",
            lig_csv_suffix=f"_Lig{str(inputs.get('ligand_molname', 'D'))}",
        )
        analysis.run_pipeline(
            struct_dict=struct_dict,
            seq_align_fname=str(inputs.get("seq_align_fname", "reps_ali.fasta")),
            binding_pocket_residues_fname=str(inputs.get("binding_pocket_residues_fname", "residues_near_ligand.csv")),
            analyse_binding_pocket_without_ligand=bool(inputs.get("analyse_binding_pocket_without_ligand", True)),
            protein_molname=str(inputs.get("protein_molname", "A")),
            ligand_molname=str(inputs.get("ligand_molname", "D")),
            dist_thres=int(inputs.get("dist_thres", 6)),
            reactive_center_target=inputs.get("reactive_center_target", {'protein':None, 'cofactor':None, 'ligand':None}),
            keep_pos_with_aa_variation_only=bool(inputs.get("keep_pos_with_aa_variation_only", True)),
        )

        combined_csv = pdb_dir / "bindingpocket_analysis.csv"
        ligand_csv = pdb_dir / "bindingpocket_wLig_analysis.csv"
        distal_csv = pdb_dir / "bindingpocket-distal_woLig_analysis.csv"
        proximal_csv = pdb_dir / "bindingpocket-proximal_woLig_analysis.csv"
        return {
            "status": "ok",
            "ligand_present": True,
            "data_root": str(dirs["data_root"]),
            "pdb_dir": str(pdb_dir),
            "msa_dir": str(msa_dir),
            "sce_dir": str(sce_dir),
            "struct_csv_dir": str(struct_csv_dir),
            "combined_analysis_path": str(combined_csv) if combined_csv.exists() else "",
            "ligand_analysis_path": str(ligand_csv) if ligand_csv.exists() else "",
            "distal_analysis_path": str(distal_csv) if distal_csv.exists() else "",
            "proximal_analysis_path": str(proximal_csv) if proximal_csv.exists() else "",
            "combined_analysis": safe_read_csv(combined_csv) if combined_csv.exists() else pd.DataFrame(),
        }

    pocket_residues_source = str(inputs.get("pocket_residues_source", "csv")).strip().lower()
    if pocket_residues_source == "csv":
        csv_path = pdb_dir / str(inputs.get("binding_pocket_residues_fname", "residues_near_ligand.csv"))
        pocket_residues_dict = _load_pocket_residues_from_csv(csv_path)
    elif pocket_residues_source == "inline":
        pocket_residues_dict = _normalize_pocket_residues_dict(dict(inputs.get("pocket_residues_dict", {})))
    else:
        raise ValueError("pocket_residues_source must be 'csv' or 'inline'.")

    if not pocket_residues_dict:
        raise ValueError("No pocket residues were provided for ligand-free pocket analysis.")

    from tools.struct.analyse_binding_pocket import PocketAnalysis

    analysis = PocketAnalysis(
        pdb_dir=f"{pdb_dir}/",
        struct_csv_dir=f"{struct_csv_dir}/",
    )
    bindingpocket_analysis, df_bindingpocket_dict, df_bindingpocket_backbone_dict = analysis(
        pocket_residues_dict=pocket_residues_dict,
        protein_molname=str(inputs.get("protein_molname", "A")),
        plot_properties=bool(inputs.get("plot_properties", False)),
    )

    combined_csv = pdb_dir / "bindingpocket_analysis.csv"
    return {
        "status": "ok",
        "ligand_present": False,
        "data_root": str(dirs["data_root"]),
        "pdb_dir": str(pdb_dir),
        "struct_csv_dir": str(struct_csv_dir),
        "binding_pocket_residues": pocket_residues_dict,
        "combined_analysis_path": str(combined_csv) if combined_csv.exists() else "",
        "combined_analysis": bindingpocket_analysis,
        "pocket_atom_tables": {k: v for k, v in df_bindingpocket_dict.items()},
        "pocket_backbone_tables": {k: v for k, v in df_bindingpocket_backbone_dict.items()},
    }


if __name__ == "__main__":
    from agentic_protein_design.core.pipeline_utils import print_run_summary

    user_inputs = default_user_inputs()
    result = run_binding_pocket_property_extraction(user_inputs)
    print_run_summary(
        result,
        keys=[
            "status",
            "ligand_present",
            "data_root",
            "pdb_dir",
            "msa_dir",
            "sce_dir",
            "struct_csv_dir",
            "combined_analysis_path",
            "ligand_analysis_path",
            "distal_analysis_path",
            "proximal_analysis_path",
        ],
    )
