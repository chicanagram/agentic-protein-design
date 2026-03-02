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
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from project_config.variables import address_dict
from agentic_protein_design.core.paths import join_data_path, resolve_project_root, setup_data_root
from tools.align.msa_to_dataframe import convert_msa_to_dataframe
from tools.align.seq_align import _default_mafft_executable, run_msa
from tools.align.visualize_alignment import visualize_msa
from tools.openprotein.align_msa_openprotein import create_openprotein_msa
from tools.search.run_search_and_align import run_seqsearch_api
from tools.conservation_analysis.run_conservation_analysis import compute_conservation
from tools.utils.seq_utils import fetch_sequences_from_fasta
from tools.yasara.align_struct_yasara import AlignStruct


REQUIRED_SUBFOLDERS = ["sequences", "msa", "conservation_analysis", "seqsearch", "pdb", "sce"]


def default_user_inputs() -> Dict[str, Any]:
    """
    Return editable defaults for MSA and conservation_analysis workflow.

    Returns:
        Dict containing alignment source/method options, file lists, plotting,
        and conservation_analysis-analysis controls.
    """
    return {
        "mafft_executable": str(_default_mafft_executable()),
        "root_key": "examples",
        "data_subfolder": "",
        "align_mode": "seq",  # seq | struct
        "skip_align": False,
        "convert_msa_to_dataframe": True,
        "sequence_input": "",
        "structure_pdb_filenames": [],
        "msa_output_filename": "msa_aligned.fasta",
        "msa_dataframe_output_filename": "msa_dataframe.csv",
        "seqsearch_output_filename": "homologs_openprotein.fasta",
        "struct_alignment_sce_filename": "aligned_structures.sce",
        "plot_output_filename": "msa_visualization.png",
        "homolog_search_backend": "blastp",  # blastp | phmmer | jackhmmer | openprotein
        "search_db_name": "uniprot_trembl",
        "search_db_root_key": "databases",
        "search_e_thres": 1e-5,
        "search_incE_thres": 1e-5,
        "search_max_target_seqs": 250,
        "search_num_cpu": None,
        "run_conservation_analysis": True,
        "filter_by_refseq_or_idx": None,
        "indiv_seq_display_thres": 20,
        "msa_plot_wrap_length": 100,
    }


def _parse_sequence_input(
    *,
    sequence_input: str,
    data_root: Path,
    data_subfolder: str,
    sequence_subdirectory: str,
) -> Dict[str, Any]:
    """
    Infer whether `sequence_input` is a raw seed sequence or a FASTA filename.

    Args:
        sequence_input: Raw amino-acid sequence string or FASTA filename.
        data_root: Resolved data root.
        data_subfolder: Optional nested data subfolder.
        sequence_subdirectory: Relative sequence folder under the selected root.

    Returns:
        Dict with parsed input metadata:
        `input_kind`, `fasta_path`, `sequences`, and `n_sequences`.
    """
    raw = str(sequence_input or "").strip()
    if not raw:
        return {
            "input_kind": "empty",
            "fasta_path": None,
            "sequences": [],
            "n_sequences": 0,
        }

    if raw.lower().endswith(".fasta"):
        fasta_path = join_data_path(data_root, sequence_subdirectory, data_subfolder, raw)
        if not fasta_path.exists():
            raise FileNotFoundError(f"FASTA file not found: {fasta_path}")
        sequences, sequence_names, _ = fetch_sequences_from_fasta(str(fasta_path))
        if not sequences:
            raise ValueError(f"No sequences found in FASTA file: {fasta_path}")
        kind = "fasta_single" if len(sequences) == 1 else "fasta_multi"
        return {
            "input_kind": kind,
            "fasta_path": fasta_path,
            "sequences": sequences,
            "sequence_names": sequence_names,
            "n_sequences": len(sequences),
        }

    return {
        "input_kind": "raw_sequence",
        "fasta_path": None,
        "sequences": [raw],
        "sequence_names": ['REF'],
        "n_sequences": 1,
    }



def run_structural_alignment_to_msa(
    *,
    struct_fpaths: Sequence[Path],
    msa_out: Path,
    sce_out: Path,
    pdb_dir: Path,
    sce_dir: Path,
    msa_dir: Path,
) -> Dict[str, Any]:
    """
    Run structural alignment with YASARA and export the resulting sequence MSA.

    Args:
        struct_fpaths: Ordered list of input PDB file paths.
        msa_out: FASTA path for the derived sequence alignment.
        sce_out: YASARA scene output path (without requiring user-side path logic).
        pdb_dir: Directory context passed into `AlignStruct`.
        sce_dir: Scene directory context passed into `AlignStruct`.
        msa_dir: Alignment directory context passed into `AlignStruct`.

    Returns:
        Metadata describing the structural-alignment artifacts created.
    """

    aligner = AlignStruct(
        pdb_dir=str(pdb_dir),
        sce_dir=str(sce_dir),
        msa_dir=str(msa_dir),
    )
    aligner.yasara_align_structures(
        [str(p) for p in struct_fpaths],
        seq_align_fpath=str(msa_out),
        output_sce_fpath=str(sce_out),
        join_obj_in_pdb=False,
        save_indiv_aligned_structs=False,
        delete_not_protein=False,
    )
    return {
        "mode": "struct_yasara_alignment",
        "backend": "yasara",
        "n_structures": len(struct_fpaths),
        "scene_path": str(sce_out),
    }


def plot_msa(msa_fpath, savefig, num_sequences, filter_by_refseq_or_idx=None, wrap_length=100, indiv_seq_display_thres=20):
    """
    Configure and plot MSA visualization using custom plotting function
    """
    plot_msa_pos_range = None
    xtick_interval = 5
    ytick_interval = 1 if num_sequences < indiv_seq_display_thres else 100
    if ytick_interval == 1:
        show_all_sequences = True
        show_seq_names = True
        pos_int_to_label = 5
    else:
        show_all_sequences = False
        show_seq_names = False
        pos_int_to_label = None
    fontsize = 8
    label_residues = 'ref'
    figsize = (20, 10)
    visualize_msa(msa_fpath, how='seaborn', color_scheme='Taylor', plot_msa_pos_range=plot_msa_pos_range,
                  wrap_length=wrap_length, xtick_interval=xtick_interval, ytick_interval=ytick_interval,
                  pos_int_to_label=pos_int_to_label,
                  show_seq_names=show_seq_names, label_residues=label_residues, show_all_sequences=show_all_sequences,
                  fontsize=fontsize,
                  filter_by_refseq_or_idx=filter_by_refseq_or_idx, savefig=savefig, figsize=figsize)



def run_alignment_and_conservation(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run scaffolded sequence/structure alignment pipeline with optional conservation_analysis.

    Args:
        inputs: User input dictionary (see `default_user_inputs()`).

    Returns:
        Dict containing run status and generated artifact paths/dataframes.
    """
    ##########################################
    # --- Resolve inputs and directories --- #
    ##########################################
    root_key = str(inputs.get("root_key", "examples"))
    data_subfolder = str(inputs.get("data_subfolder", "") or "").strip()
    align_mode = str(inputs.get("align_mode", "seq")).strip().lower()
    skip_align = bool(inputs.get("skip_align", False))
    convert_msa = bool(inputs.get("convert_msa_to_dataframe", True))
    homolog_search_backend = str(inputs.get("homolog_search_backend", "blastp")).strip().lower()

    data_root, resolved = setup_data_root(root_key, REQUIRED_SUBFOLDERS)
    sequence_dir = resolved["sequences"]
    msa_dir = resolved["msa"]
    seqsearch_dir = resolved["seqsearch"]
    conservation_analysis_dir = resolved["conservation_analysis"]
    sce_dir = resolved["sce"]
    pdb_dir = resolved["pdb"]
    if data_subfolder:
        sequence_dir = sequence_dir / data_subfolder
        msa_dir = msa_dir / data_subfolder
        seqsearch_dir = seqsearch_dir / data_subfolder
        sce_dir = sce_dir / data_subfolder
        pdb_dir = pdb_dir / data_subfolder
    for folder in (sequence_dir, msa_dir, seqsearch_dir, sce_dir, pdb_dir):
        folder.mkdir(parents=True, exist_ok=True)
    search_db_root_key = str(inputs.get("search_db_root_key", "databases"))
    if search_db_root_key not in address_dict:
        raise KeyError(f"Unknown search_db_root_key: {search_db_root_key}")

    msa_out = msa_dir / str(inputs.get("msa_output_filename", "msa_aligned.fasta"))
    msa_df_out = msa_dir / str(inputs.get("msa_dataframe_output_filename", "msa_dataframe.csv"))
    seqsearch_out = sequence_dir / str(
        inputs.get("seqsearch_output_filename", "openprotein_homologs.fasta")
    )
    struct_sce_name = str(inputs.get("struct_alignment_sce_filename", "aligned_structures.sce")).strip() or "aligned_structures.sce"
    if not struct_sce_name.lower().endswith(".sce"):
        struct_sce_name = f"{struct_sce_name}.sce"
    struct_sce_out = sce_dir / struct_sce_name
    plot_out = msa_dir / str(inputs.get("plot_output_filename", "msa_visualization.png"))

    sequence_subdirectory = 'sequences/'
    structure_subdirectory = 'pdb/'
    parsed_sequence_input = _parse_sequence_input(
        sequence_input=str(inputs.get("sequence_input", "")),
        data_root=data_root,
        data_subfolder=data_subfolder,
        sequence_subdirectory=sequence_subdirectory,
    )
    print('Parsed sequence input kind:', parsed_sequence_input["input_kind"])

    status = "ok"
    message = ""
    seq_stage_dir = sequence_dir
    seq_stage_dir.mkdir(parents=True, exist_ok=True)

    if skip_align:
        if msa_out.exists():
            existing_msa_input = msa_out
        else:
            raise FileNotFoundError(
                "skip_align=True requires an existing MSA FASTA either as sequence_input (.fasta) "
                "or already saved at the configured msa_output_filename."
            )
        if existing_msa_input != msa_out:
            msa_out.write_text(existing_msa_input.read_text(encoding="utf-8"), encoding="utf-8")
        existing_seqs, _, _ = fetch_sequences_from_fasta(str(msa_out))
        message = "Alignment step skipped; downstream MSA processing only."

    else:
        if align_mode == "seq":

            ###################################################
            # --- Run sequence search using seed sequence --- #
            ###################################################
            if parsed_sequence_input["input_kind"] in {"raw_sequence", "fasta_single"}:
                msa_out = Path(str(msa_out).replace('_aligned', '_homologs_aligned'))
                msa_df_out = Path(str(msa_df_out).replace('_aligned', '_homologs_aligned'))
                plot_out = Path(str(plot_out).replace('_aligned', '_homologs_aligned'))
                seed_sequence = parsed_sequence_input["sequences"][0]
                # run sequence search + align with OpenProtein
                if homolog_search_backend == "openprotein":
                    msa_job = create_openprotein_msa(
                        seed_sequence=seed_sequence,
                        seed_sequence_name=parsed_sequence_input["sequence_names"][0],
                        seq_fasta_path=seqsearch_out,
                    )
    
                # run sequence search with Blastp, Phmmer, or Jackmmer
                elif homolog_search_backend in {"blastp", "phmmer", "jackhmmer"}:
                    # !! UPDATE WITH API-BASED TOOLS TO QUERY UNIPROT DATABASE !!
                    run_seqsearch_api(seed_sequence, fasta_fpath=msa_out)
                    pass
                else:
                    raise ValueError(f"Unknown homolog_search_backend: {homolog_search_backend}")

                # update parsed_sequence_input fasta path for subsequent alignment processing
                parsed_sequence_input["fasta_path"] = seqsearch_out

            ##################################
            # --- Run Sequence Alignment --- #
            ##################################
            source_fasta = parsed_sequence_input["fasta_path"]
            if source_fasta is None:
                raise ValueError(f"No source fasta found: {source_fasta}")

            run_msa(
                seq_fname=source_fasta.name,
                msa_fname=msa_out.name,
                method="mafft",
                seq_dir=f"{source_fasta.parent}/",
                msa_dir=f"{msa_out.parent}/",
                mafft_executable=str(inputs.get("mafft_executable", "mafft")),
            )

        ####################################
        # --- Run Structural Alignment --- #
        ####################################
        elif align_mode == "struct":
            struct_fpaths: List[Path] = []
            for fname in inputs.get("structure_pdb_filenames", []):
                p = join_data_path(data_root, structure_subdirectory, data_subfolder, str(fname))
                if p.exists():
                    struct_fpaths.append(p)
            if len(struct_fpaths) < 2:
                raise ValueError("align_mode='struct' requires at least two existing PDB files.")

        else:
            raise ValueError(
                "For align_mode='seq', provide `sequence_input` as a raw sequence or FASTA filename. "
                "For align_mode='struct', provide at least two `structure_pdb_filenames`."
            )

    ###############################
    # --- Post-MSA processing --- #
    ###############################
    seqs, seq_names, _ = fetch_sequences_from_fasta(str(msa_out))
    n_input_sequences = len(seqs)
    print('msa_out:', msa_out, n_input_sequences)

    # --- Convert FASTA-format MSA to dataframe ---
    if convert_msa:
        msa_df = pd.DataFrame()
        msa_df = convert_msa_to_dataframe(seqs, seq_names)
        msa_df.to_csv(msa_df_out, index=False)

    # --- Plot visualization ---
    plot_msa(
        msa_out,
        plot_out,
        num_sequences=n_input_sequences,
        filter_by_refseq_or_idx=inputs.get("filter_by_refseq_or_idx", None),
        wrap_length=int(inputs.get("msa_plot_wrap_length", 100)),
        indiv_seq_display_thres=int(inputs.get("indiv_seq_display_thres", 20)),
    )

    # --- Run conservation_analysis analysis ---
    cons_df = pd.DataFrame()
    csv_fpath_list = None
    if bool(inputs.get("run_conservation_analysis", True)):
        csv_fpath_list = compute_conservation(
            msa_fname=msa_out.name,
            analyses_to_run=['sift'],
            data_folder=data_root,
            msa_subfolder=str(msa_dir).replace(str(data_root),""),
            conservation_analysis_subfolder=str(conservation_analysis_dir).replace(str(data_root),""),
            save_csv=True,
            ref_seq_name_list=[seq_names[0]],
            ref_seq_idxs_list=None,
            ref_seq_list=[seqs[0].replace('-','')],
            seq_offset=0
        )


    return {
        "status": status,
        "message": message,
        "root_key": root_key,
        "data_root": str(data_root),
        "artifact_dir": str(msa_dir),
        "align_mode": align_mode,
        "skip_align": skip_align,
        "input_kind": parsed_sequence_input["input_kind"],
        "n_input_sequences": int(n_input_sequences),
        "msa_path": str(msa_out) if msa_out.exists() else "",
        "msa_dataframe_path": str(msa_df_out) if not msa_df.empty else "",
        "msa_dataframe": msa_df,
        "seqsearch_path": str(seqsearch_out) if seqsearch_out.exists() else "",
        "struct_scene_path": str(struct_sce_out) if struct_sce_out.exists() else "",
        "plot_path": str(plot_out) if plot_out.exists() else "",
        "conservation_path": csv_fpath_list
    }


if __name__ == "__main__":
    from agentic_protein_design.core.ide_runner import print_run_summary

    user_inputs = default_user_inputs()
    result = run_alignment_and_conservation(user_inputs)
    print_run_summary(
        result,
        keys=[
            "status",
            "root_key",
            "data_root",
            "artifact_dir",
            "input_kind",
            "alignment_backend",
            "n_input_sequences",
            "msa_path",
            "plot_path",
            "conservation_path",
        ],
    )
