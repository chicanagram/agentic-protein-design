from __future__ import annotations

# Default feature-set selections for notebook-driven sequence encoding runs.
# Keep these editable outside notebooks when the list gets long.

# --- Classical feature sets ---
CLASSICAL_ENCODING_FEATURE_SETS = [
    "one_hot",
    "georgiev",
]

# --- PLM feature sets ---
PLM_MODELS_DICT = {
    "esm2-650m": [33],
    "esmc-600m": [36],
    "poet2": [12],
}

PLM_ENCODING_FEATURE_SETS = [f for f_list in [[f'{plm}_LLR', f'{plm}_per_residue', f'{plm}_mean_pooled', f'{plm}_mut_pooled'] for plm in PLM_MODELS_DICT] for f in f_list]

# combination of classical and PLM
FEATURE_SETS_ALL = CLASSICAL_ENCODING_FEATURE_SETS + PLM_ENCODING_FEATURE_SETS
FEATURE_SETS_DEFAULT = [
    "one_hot",
    "esm2-650m_LLR",
    "esmc-600m_LLR",
    "esm2-650m_mean_pooled",
    "esmc-600m_mean_pooled",
]

# combi feature sets
COMBI_ML_FEATURE_SETS = {

}