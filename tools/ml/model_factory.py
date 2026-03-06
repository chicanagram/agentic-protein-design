from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple


def _import_sklearn_models():
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.neural_network import MLPClassifier, MLPRegressor

    return {
        "rf": (RandomForestClassifier, RandomForestRegressor),
        "random_forest": (RandomForestClassifier, RandomForestRegressor),
        "ridge": (LogisticRegression, Ridge),
        "mlp_sklearn": (MLPClassifier, MLPRegressor),
    }


def _import_xgboost_models():
    from xgboost import XGBClassifier, XGBRegressor

    return XGBClassifier, XGBRegressor


def _import_lightgbm_models():
    from lightgbm import LGBMClassifier, LGBMRegressor

    return LGBMClassifier, LGBMRegressor


def _default_params(model_name: str, task_type: str) -> Dict[str, Any]:
    defaults = {
        "rf": {
            "classification": {"n_estimators": 300, "random_state": 42, "n_jobs": -1},
            "regression": {"n_estimators": 300, "random_state": 42, "n_jobs": -1},
        },
        "random_forest": {
            "classification": {"n_estimators": 300, "random_state": 42, "n_jobs": -1},
            "regression": {"n_estimators": 300, "random_state": 42, "n_jobs": -1},
        },
        "ridge": {
            "classification": {"C": 1.0, "max_iter": 1000},
            "regression": {"alpha": 1.0},
        },
        "mlp_sklearn": {
            "classification": {
                "hidden_layer_sizes": (64, 64),
                "solver": "adam",
                "learning_rate_init": 1e-3,
                "batch_size": 32,
                "max_iter": 400,
                "early_stopping": True,
                "n_iter_no_change": 15,
                "tol": 1e-5,
                "random_state": 42,
            },
            "regression": {
                "hidden_layer_sizes": (64, 64),
                "solver": "adam",
                "learning_rate_init": 1e-3,
                "batch_size": 32,
                "max_iter": 400,
                "early_stopping": True,
                "n_iter_no_change": 15,
                "tol": 1e-5,
                "random_state": 42,
            },
        },
        "mlp_pytorch": {
            "classification": {
                "n_layers": 2,
                "hidden_size": 32,
                "batch_size": 32,
                "learning_rate": 1e-3,
                "max_epochs": 400,
                "patience": 15,
                "min_delta": 1e-5,
                "validation_split": 0.2,
                "random_state": 42,
                "device": "cpu",
            },
            "regression": {
                "n_layers": 2,
                "hidden_size": 32,
                "batch_size": 32,
                "learning_rate": 1e-3,
                "max_epochs": 400,
                "patience": 15,
                "min_delta": 1e-5,
                "validation_split": 0.2,
                "random_state": 42,
                "device": "cpu",
            },
        },
        "xgboost": {
            "classification": {"n_estimators": 400, "learning_rate": 0.05, "max_depth": 6, "random_state": 42},
            "regression": {"n_estimators": 400, "learning_rate": 0.05, "max_depth": 6, "random_state": 42},
        },
        "lightgbm": {
            "classification": {"n_estimators": 400, "learning_rate": 0.05, "max_depth": -1, "random_state": 42},
            "regression": {"n_estimators": 400, "learning_rate": 0.05, "max_depth": -1, "random_state": 42},
        },
    }
    return dict(defaults.get(model_name, {}).get(task_type, {}))


def load_model_params(
    *,
    model_name: str,
    task_type: str,
    settings_repo_dir: Path,
    model_params_override: Dict[str, Any] | None,
) -> Dict[str, Any]:
    if model_params_override and model_name in model_params_override:
        return dict(model_params_override[model_name])

    settings_path = settings_repo_dir / f"{model_name}.json"
    if settings_path.exists():
        raw = json.loads(settings_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            scoped = raw.get(task_type)
            if isinstance(scoped, dict):
                return dict(scoped)
            return dict(raw)

    return _default_params(model_name=model_name, task_type=task_type)


def build_model(
    *,
    model_name: str,
    task_type: str,
    params: Dict[str, Any],
):
    key = str(model_name).strip().lower()
    task = str(task_type).strip().lower()
    if task not in {"classification", "regression"}:
        raise ValueError("task_type must be 'classification' or 'regression'.")

    sklearn_models = _import_sklearn_models()
    if key in sklearn_models:
        cls_cls, reg_cls = sklearn_models[key]
        cls = cls_cls if task == "classification" else reg_cls
        return cls(**params)

    if key == "xgboost":
        try:
            cls_cls, reg_cls = _import_xgboost_models()
        except Exception as exc:
            raise ImportError("xgboost is not installed but model 'xgboost' was requested.") from exc
        cls = cls_cls if task == "classification" else reg_cls
        return cls(**params)

    if key == "lightgbm":
        try:
            cls_cls, reg_cls = _import_lightgbm_models()
        except Exception as exc:
            raise ImportError("lightgbm is not installed but model 'lightgbm' was requested.") from exc
        cls = cls_cls if task == "classification" else reg_cls
        return cls(**params)

    if key == "mlp_pytorch":
        try:
            from tools.ml.torch_mlp import TorchMLPClassifier, TorchMLPRegressor
        except Exception as exc:
            raise ImportError("PyTorch MLP requested but torch is not installed.") from exc
        cls = TorchMLPClassifier if task == "classification" else TorchMLPRegressor
        return cls(**params)

    raise ValueError(
        "Unsupported model "
        f"'{model_name}'. Supported: rf, random_forest, ridge, mlp_sklearn, mlp_pytorch, xgboost, lightgbm"
    )
