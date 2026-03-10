from __future__ import annotations

import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from tools.ml.metrics import compute_metrics
from tools.ml.model_factory import build_model, load_model_params
from tools.ml.feature_matrix import (
    build_feature_matrix,
    load_dataset_table,
    prepare_dataset_bundle,
)
from tools.ml.feature_coefficients import (
    extract_coefficients,
    normalize_feature_model_pairs,
    resolve_sequence_base,
    save_coefficients_csv,
    should_extract_coefficients,
)
from tools.ml.splits import generate_splits


def _utc_now_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_pickle(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(payload, f)


def _append_metrics_row(metrics_csv_path: Path, row: Dict[str, Any]) -> None:
    metrics_csv_path.parent.mkdir(parents=True, exist_ok=True)
    row_df = pd.DataFrame([row])
    if metrics_csv_path.exists():
        existing = pd.read_csv(metrics_csv_path)
        out = pd.concat([existing, row_df], ignore_index=True)
    else:
        out = row_df
    out.to_csv(metrics_csv_path, index=False)


def _build_metrics_csv_name(task_type: str, suffix: str) -> str:
    clean_suffix = str(suffix or "").strip()
    return f"{task_type}_metrics{clean_suffix}.csv"


def _build_summary_csv_name(task_type: str, suffix: str) -> str:
    clean_suffix = str(suffix or "").strip()
    return f"{task_type}_metrics_summary{clean_suffix}.csv"


def _compose_pred_name(run_label: str, feature_label: str, split_id: str, model_name: str, suffix: str) -> str:
    if str(suffix or "").strip():
        return f"{run_label}__{feature_label}__{split_id}__{model_name}__{suffix}.csv"
    return f"{run_label}__{feature_label}__{split_id}__{model_name}.csv"


def _round_metric_dict(metrics: Dict[str, Any], ndigits: int = 4) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in metrics.items():
        try:
            out[k] = round(float(v), ndigits)
        except Exception:
            out[k] = v
    return out


def _progress_row(task_type: str, test_metrics: Dict[str, Any], train_metrics: Dict[str, Any]) -> pd.DataFrame:
    if task_type == "regression":
        cols = [
            "test_spearman",
            "test_pearson",
            "test_r2",
            "test_rmse",
            "train_spearman",
            "train_pearson",
            "train_r2",
            "train_rmse",
        ]
    else:
        cols = [
            "test_mcc",
            "test_accuracy",
            "test_f1_weighted",
            "train_mcc",
            "train_accuracy",
            "train_f1_weighted",
        ]
    row: Dict[str, Any] = {}
    for c in cols:
        if c.startswith("test_"):
            row[c] = test_metrics.get(c.replace("test_", ""), np.nan)
        else:
            row[c] = train_metrics.get(c.replace("train_", ""), np.nan)
    return pd.DataFrame([row])


def _summary_progress_row(task_type: str, test_metrics: Dict[str, Any]) -> pd.DataFrame:
    if task_type == "regression":
        cols = ["test_spearman", "test_pearson", "test_r2", "test_rmse", "n_test_pooled", "n_folds"]
    else:
        cols = ["test_mcc", "test_accuracy", "test_f1_weighted", "n_test_pooled", "n_folds"]
    row = {k: test_metrics.get(k, np.nan) for k in cols}
    return pd.DataFrame([row])


def _build_standard_bundle(
    *,
    dataset_path: Path,
    enc_dir: Path,
    feature_files: List[str],
    target_col: str,
    input_filename_prefix: str = "",
):
    dataset_df = load_dataset_table(dataset_path)
    X = build_feature_matrix(
        encodings_dir=enc_dir,
        feature_files=feature_files,
        feature_prefix=input_filename_prefix or dataset_path.stem,
    )
    bundle = prepare_dataset_bundle(dataset_df=dataset_df, X=X, target_col=target_col)
    return bundle, dataset_df


def _build_custom_external_bundle(
    *,
    train_dataset_path: Path,
    test_dataset_path: Path,
    train_enc_dir: Path,
    test_enc_dir: Path,
    feature_files: List[str],
    target_col: str,
    train_input_filename_prefix: str = "",
    test_input_filename_prefix: str = "",
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame, np.ndarray, np.ndarray]:
    train_df = load_dataset_table(train_dataset_path)
    test_df = load_dataset_table(test_dataset_path)

    X_train = build_feature_matrix(
        encodings_dir=train_enc_dir,
        feature_files=feature_files,
        feature_prefix=train_input_filename_prefix or train_dataset_path.stem,
    )
    X_test = build_feature_matrix(
        encodings_dir=test_enc_dir,
        feature_files=feature_files,
        feature_prefix=test_input_filename_prefix or test_dataset_path.stem,
    )

    train_bundle = prepare_dataset_bundle(dataset_df=train_df, X=X_train, target_col=target_col)
    test_bundle = prepare_dataset_bundle(dataset_df=test_df, X=X_test, target_col=target_col)

    X_all = np.concatenate([train_bundle.X, test_bundle.X], axis=0)
    y_all = np.concatenate([train_bundle.y, test_bundle.y], axis=0)

    combined_df = pd.concat([train_bundle.dataset_df, test_bundle.dataset_df], axis=0, ignore_index=True)
    train_idx = np.arange(len(train_bundle.y), dtype=int)
    test_idx = np.arange(len(train_bundle.y), len(train_bundle.y) + len(test_bundle.y), dtype=int)
    return X_all, y_all, combined_df, train_idx, test_idx


def run_supervised_ml_workflow(inputs: Dict[str, Any]) -> Dict[str, Any]:
    data_root = Path(str(inputs["data_root_dir"]).strip()).expanduser().resolve()
    data_subfolder = str(inputs.get("data_subfolder", "") or "").strip().strip("/")
    dataset_fname = str(inputs["dataset_fname"]).strip()
    target_col_input = inputs.get("target_col", "y")
    if isinstance(target_col_input, (list, tuple)):
        target_col_list = [str(x).strip() for x in target_col_input if str(x).strip()]
    else:
        target_col_list = [str(target_col_input).strip()]
    if not target_col_list:
        raise ValueError("target_col must be a non-empty string or list of non-empty strings.")
    task_type = str(inputs.get("classification_or_regression", "regression")).strip().lower()

    split_type_list = [str(x).strip() for x in inputs.get("split_type_list", ["random"]) if str(x).strip()]
    model_list = [str(x).strip() for x in inputs.get("model_list", ["rf"]) if str(x).strip()]
    feature_combinations_dict = dict(inputs.get("feature_combinations_dict", {}))
    if not feature_combinations_dict:
        raise ValueError("feature_combinations_dict cannot be empty.")

    sample_id_col = str(inputs.get("sample_id_col", "")).strip()
    split_seed = int(inputs.get("split_seed", 42))
    k_folds = int(inputs.get("k_folds", 5))

    mutres_col = str(inputs.get("mutres_col", "mutres_idx")).strip()
    random_split_col = str(inputs.get("random_split_col", f"fold_random_{k_folds}")).strip()
    mutres_split_col = str(inputs.get("mutres_split_col", f"fold_modulo_{k_folds}")).strip()
    contiguous_split_col = str(inputs.get("contiguous_split_col", f"fold_contiguous_{k_folds}")).strip()

    custom_split_col = str(inputs.get("custom_split_col", "split")).strip()
    custom_test_value = inputs.get("custom_test_value", "test")
    custom_split_indices = inputs.get("custom_split_indices")
    custom_test_dataset_fname = str(inputs.get("custom_test_dataset_fname", "")).strip()
    custom_test_data_subfolder_raw = str(inputs.get("custom_test_data_subfolder", "") or "").strip().strip("/")
    custom_test_data_subfolder = custom_test_data_subfolder_raw or data_subfolder
    input_filename_prefix = str(inputs.get("input_filename_prefix", "") or "").strip()
    custom_input_filename_prefix = str(inputs.get("custom_input_filename_prefix", "") or "").strip()
    sequence_base_input = inputs.get("sequence_base")

    settings_repo_dir = Path(str(inputs.get("model_settings_repo_dir", "tools/ml/model_settings"))).expanduser().resolve()
    model_params_override = inputs.get("model_params")

    save_trained_models = bool(inputs.get("save_trained_models", True))
    train_full_data_model = bool(inputs.get("train_full_data_model", False))
    save_predictions = bool(inputs.get("save_predictions", True))
    show_progress = bool(inputs.get("show_progress", True))
    feature_model_pairs = normalize_feature_model_pairs(
        inputs.get("featurecombi_model_pair_to_extract_coefficients_for", [])
    )
    extract_feature_coefficients = bool(feature_model_pairs)

    run_label = str(inputs.get("run_label", _utc_now_label())).strip() or _utc_now_label()
    csv_suffix = str(inputs.get("csv_suffix", "")).strip()

    train_enc_dir = data_root / "encodings"
    train_dataset_dir = data_root / "expdata"
    model_dir = data_root / "ml" / "trained_models"
    pred_dir = data_root / "ml" / "predictions"
    out_dir = data_root / "ml" / "output"

    if data_subfolder:
        train_enc_dir = train_enc_dir / data_subfolder
        train_dataset_dir = train_dataset_dir / data_subfolder
        model_dir = model_dir / data_subfolder
        pred_dir = pred_dir / data_subfolder
        out_dir = out_dir / data_subfolder

    train_dataset_path = train_dataset_dir / dataset_fname

    metrics_csv_path = out_dir / _build_metrics_csv_name(task_type=task_type, suffix=csv_suffix)
    summary_csv_path = out_dir / _build_summary_csv_name(task_type=task_type, suffix=csv_suffix)
    run_rows: List[Dict[str, Any]] = []
    pooled_test_cache: Dict[Tuple[str, str, str, str], Dict[str, List[np.ndarray]]] = {}
    matched_coeff_pairs: set[tuple[str, str]] = set()

    for target_col in target_col_list:
        for split_type in split_type_list:
            for feature_label, feature_files_raw in feature_combinations_dict.items():
                feature_files = list(feature_files_raw)
                split_key = str(split_type).strip().lower()

                if split_key == "custom":
                    if not custom_test_dataset_fname:
                        raise ValueError(
                            "split_type='custom' requires 'custom_test_dataset_fname' for external test evaluation."
                        )
                    test_enc_dir = data_root / "encodings"
                    test_dataset_dir = data_root / "expdata"
                    if custom_test_data_subfolder:
                        test_enc_dir = test_enc_dir / custom_test_data_subfolder
                        test_dataset_dir = test_dataset_dir / custom_test_data_subfolder
                    test_dataset_path = test_dataset_dir / custom_test_dataset_fname

                    X_all, y_all, dataset_df, train_idx, test_idx = _build_custom_external_bundle(
                        train_dataset_path=train_dataset_path,
                        test_dataset_path=test_dataset_path,
                        train_enc_dir=train_enc_dir,
                        test_enc_dir=test_enc_dir,
                        feature_files=feature_files,
                        target_col=target_col,
                        train_input_filename_prefix=input_filename_prefix,
                        test_input_filename_prefix=custom_input_filename_prefix,
                    )
                    split_defs = [
                        {
                            "split_type": "custom",
                            "split_id": "custom_external_0",
                            "train_idx": train_idx,
                            "test_idx": test_idx,
                        }
                    ]
                else:
                    bundle, dataset_df = _build_standard_bundle(
                        dataset_path=train_dataset_path,
                        enc_dir=train_enc_dir,
                        feature_files=feature_files,
                        target_col=target_col,
                        input_filename_prefix=input_filename_prefix,
                    )
                    X_all = bundle.X
                    y_all = bundle.y
                    split_defs = generate_splits(
                        dataset_df=dataset_df,
                        n_rows=len(dataset_df),
                        split_type=split_type,
                        k_folds=k_folds,
                        seed=split_seed,
                        mutres_col=mutres_col,
                        random_split_col=random_split_col,
                        mutres_split_col=mutres_split_col,
                        contiguous_split_col=contiguous_split_col,
                        custom_split_col=custom_split_col,
                        custom_test_value=custom_test_value,
                        custom_split_indices=custom_split_indices,
                    )

                for split_idx, split_info in enumerate(split_defs):
                    split_id = int(split_idx)
                    train_idx = np.asarray(split_info["train_idx"], dtype=int)
                    test_idx = np.asarray(split_info["test_idx"], dtype=int)

                    X_train, X_test = X_all[train_idx], X_all[test_idx]
                    y_train, y_test = y_all[train_idx], y_all[test_idx]

                    for model_name in model_list:
                        if show_progress:
                            print(
                                "[eval-start] "
                                f"target_col={target_col} | split_type={split_info['split_type']} | "
                                f"feature_combi_name={feature_label} | model_name={model_name}"
                            )
                        params = load_model_params(
                            model_name=model_name,
                            task_type=task_type,
                            settings_repo_dir=settings_repo_dir,
                            model_params_override=model_params_override,
                        )
                        model = build_model(model_name=model_name, task_type=task_type, params=params)
                        model.fit(X_train, y_train)

                        yhat_train = model.predict(X_train)
                        yhat_test = model.predict(X_test)

                        y_score_train = None
                        y_score_test = None
                        if task_type == "classification" and hasattr(model, "predict_proba"):
                            try:
                                y_score_train = model.predict_proba(X_train)
                                y_score_test = model.predict_proba(X_test)
                            except Exception:
                                y_score_train = None
                                y_score_test = None

                        train_metrics = _round_metric_dict(compute_metrics(
                            y_true=y_train,
                            y_pred=yhat_train,
                            task_type=task_type,
                            y_score=y_score_train,
                        ))
                        test_metrics = _round_metric_dict(compute_metrics(
                            y_true=y_test,
                            y_pred=yhat_test,
                            task_type=task_type,
                            y_score=y_score_test,
                        ))

                        row = {
                            "target_col": target_col,
                            "feature_label": feature_label,
                            "split_type": split_info["split_type"],
                            "split_id": split_id,
                            "model_name": model_name,
                            "task_type": task_type,
                            "n": int(X_all.shape[0]),
                            "p": int(X_all.shape[1]),
                            "n_train": int(len(train_idx)),
                            "n_test": int(len(test_idx)),
                            "model_params": str(params),
                        }
                        row.update({f"test_{k}": v for k, v in test_metrics.items()})
                        row.update({f"train_{k}": v for k, v in train_metrics.items()})
                        run_rows.append(row)
                        _append_metrics_row(metrics_csv_path, row)
                        if show_progress:
                            fold_progress = _progress_row(task_type, test_metrics, train_metrics)
                            print(f"[fold-result] split_id={split_id}")
                            print(fold_progress.to_string(index=False))

                        pool_key = (target_col, feature_label, str(split_info["split_type"]), model_name)
                        cache = pooled_test_cache.setdefault(pool_key, {"y_true": [], "y_pred": []})
                        cache["y_true"].append(np.asarray(y_test))
                        cache["y_pred"].append(np.asarray(yhat_test))

                        if save_trained_models:
                            model_path = model_dir / f"{run_label}__{feature_label}__{target_col}__{split_id}__{model_name}.pkl"
                            payload = {
                                "model": model,
                                "metadata": {
                                    "feature_label": feature_label,
                                    "feature_files": list(feature_files),
                                    "split_type": split_info["split_type"],
                                    "split_id": split_id,
                                    "model_name": model_name,
                                    "task_type": task_type,
                                    "params": params,
                                    "target_col": target_col,
                                },
                            }
                            _write_pickle(model_path, payload)

                        if save_predictions:
                            pred_df = pd.DataFrame(
                                {
                                    "row_index": test_idx,
                                    "y_true": y_test,
                                    "y_pred": yhat_test,
                                }
                            )
                            if sample_id_col and sample_id_col in dataset_df.columns:
                                pred_df.insert(
                                    1,
                                    "sample_id",
                                    dataset_df.iloc[test_idx][sample_id_col].to_numpy(),
                                )
                            pred_path = pred_dir / _compose_pred_name(
                                run_label=run_label,
                                feature_label=f"{feature_label}__{target_col}",
                                split_id=str(split_id),
                                model_name=model_name,
                                suffix=csv_suffix,
                            )
                            pred_path.parent.mkdir(parents=True, exist_ok=True)
                            pred_df.to_csv(pred_path, index=False)

                if train_full_data_model or extract_feature_coefficients:
                    resolved_sequence_base = resolve_sequence_base(
                        sequence_base_input=sequence_base_input,
                        dataset_df=dataset_df,
                        data_root=data_root,
                        data_subfolder=data_subfolder,
                    )
                    for model_name in model_list:
                        want_coefficients = should_extract_coefficients(
                            feature_label=feature_label,
                            model_name=model_name,
                            feature_files=feature_files,
                            feature_model_pairs=feature_model_pairs,
                        )
                        if not train_full_data_model and not want_coefficients:
                            continue

                        params = load_model_params(
                            model_name=model_name,
                            task_type=task_type,
                            settings_repo_dir=settings_repo_dir,
                            model_params_override=model_params_override,
                        )
                        model = build_model(model_name=model_name, task_type=task_type, params=params)
                        model.fit(X_all, y_all)

                        if train_full_data_model and save_trained_models:
                            model_path = model_dir / f"{run_label}__{feature_label}__{target_col}__full__{model_name}.pkl"
                            payload = {
                                "model": model,
                                "metadata": {
                                    "feature_label": feature_label,
                                    "feature_files": list(feature_files),
                                    "split_type": "full",
                                    "split_id": "full",
                                    "model_name": model_name,
                                    "task_type": task_type,
                                    "params": params,
                                    "target_col": target_col,
                                },
                            }
                            _write_pickle(model_path, payload)

                        if want_coefficients:
                            matched_coeff_pairs.add((str(feature_label).strip().lower(), str(model_name).strip().lower()))
                            if len(feature_files) == 1:
                                matched_coeff_pairs.add((str(feature_files[0]).strip().lower(), str(model_name).strip().lower()))
                            try:
                                coefficients = extract_coefficients(model_name=model_name, model_obj=model)
                                coeff_path = save_coefficients_csv(
                                    coefficients=coefficients,
                                    out_dir=out_dir,
                                    feature_label=feature_label,
                                    model_name=model_name,
                                    feature_files=feature_files,
                                    sequence_base=resolved_sequence_base,
                                )
                                if show_progress:
                                    print(f"[coefficients-saved] {coeff_path}")
                            except Exception as exc:
                                if show_progress:
                                    print(
                                        "[coefficients-skipped] "
                                        f"target_col={target_col} | feature_combi_name={feature_label} | "
                                        f"model_name={model_name} | reason={exc}"
                                    )

    if feature_model_pairs and not matched_coeff_pairs and show_progress:
        print(
            "[coefficients-warning] No requested feature/model pairs matched this run. "
            f"requested={sorted(feature_model_pairs)}"
        )

    run_df = pd.DataFrame(run_rows)

    summary_rows: List[Dict[str, Any]] = []
    for (target_col, feature_label, split_type, model_name), cached in pooled_test_cache.items():
        y_true_all = np.concatenate(cached["y_true"], axis=0)
        y_pred_all = np.concatenate(cached["y_pred"], axis=0)
        pooled_metrics = _round_metric_dict(compute_metrics(
            y_true=y_true_all,
            y_pred=y_pred_all,
            task_type=task_type,
            y_score=None,
        ))
        summary_row = {
            "target_col": target_col,
            "feature_label": feature_label,
            "split_type": split_type,
            "model_name": model_name,
            "task_type": task_type,
            "n_test_pooled": int(len(y_true_all)),
            "n_folds": int(len(cached["y_true"])),
        }
        summary_row.update({f"test_{k}": v for k, v in pooled_metrics.items()})
        summary_rows.append(summary_row)
        if show_progress:
            print(
                "[summary] "
                f"target_col={target_col} | split_type={split_type} | "
                f"feature_combi_name={feature_label} | model_name={model_name}"
            )
            summary_progress = _summary_progress_row(task_type, summary_row)
            print(summary_progress.to_string(index=False))

    summary_df = pd.DataFrame(summary_rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_df.empty:
        if summary_csv_path.exists():
            existing_summary = pd.read_csv(summary_csv_path)
            summary_out = pd.concat([existing_summary, summary_df], ignore_index=True)
        else:
            summary_out = summary_df
        summary_out.to_csv(summary_csv_path, index=False)

    return {
        "status": "ok",
        "run_label": run_label,
        "dataset_path": str(train_dataset_path),
        "metrics_csv_path": str(metrics_csv_path),
        "summary_csv_path": str(summary_csv_path),
        "n_results": int(len(run_df)),
        "n_summary_rows": int(len(summary_df)),
        "model_dir": str(model_dir),
        "prediction_dir": str(pred_dir),
        "output_dir": str(out_dir),
    }
