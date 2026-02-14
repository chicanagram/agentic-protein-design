from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
from tools.openprotein import predict_boltz2


def run_structure_prediction(inputs: Dict[str, Any], out_cif_path: Path, out_summary_path: Path) -> Dict[str, Any]:
    tool = str(inputs.get("preferred_structure_tool", "")).strip().lower()

    if tool == "rcsb_search":
        return {
            "tool": tool,
            "implemented": False,
            "message": "RCSB PDB search path is not implemented yet.",
        }

    if tool == "boltz2_local":
        return {
            "tool": tool,
            "implemented": False,
            "message": "Local Boltz-2 path is not implemented yet.",
        }

    if tool == "boltz2_openprotein":
        sequences = list(inputs.get("sequences", []))
        ligands = list(inputs.get("ligands", []))
        if not sequences:
            raise ValueError("No protein sequences provided.")

        summary = predict_boltz2(
            sequences=sequences,
            smiles=ligands,
            ccds=None,
            predict_affinity=bool(inputs.get("predict_affinity", False)),
            wait=True,
            out_cif=out_cif_path,
            out_summary_json=out_summary_path,
        )
        summary["tool"] = tool
        summary["implemented"] = True
        return summary

    return {
        "tool": tool,
        "implemented": False,
        "message": f"Unknown tool option: {tool}",
    }