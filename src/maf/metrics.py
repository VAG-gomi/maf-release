"""SPEC-M1 metric definitions."""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.stats import rankdata, spearmanr



def rmse_holdout(model: Any, world: dict[str, Any]) -> float:
    """Compute M-RMSE over holdout environments, tau={0,0.5,1}, and fixed grids."""
    predictions: list[np.ndarray] = []
    truth: list[np.ndarray] = []
    for env in world["holdout"]:
        env_id = int(env["env_id"])
        grid = np.asarray(world["eval_grids"][env_id], dtype=float)
        for tau_value in (0.0, 0.5, 1.0):
            tau = np.full(len(grid), tau_value, dtype=float)
            predictions.append(np.asarray(model.predict_interventional(grid, tau), dtype=float))
            z = np.column_stack([np.ones(len(grid)), grid, grid[:, 2] ** 2, grid[:, 3] * grid[:, 4]])
            truth.append(z @ np.asarray(world["theta"], dtype=float) + float(world["kappa"]) * tau_value)
    p = np.concatenate(predictions)
    y = np.concatenate(truth)
    return float(math.sqrt(float(np.mean((p - y) ** 2))))


def psi_spearman(model: Any, world: dict[str, Any]) -> float:
    """Compute M-PSI: Spearman rho between train psi norms and planted rho."""
    psi = np.asarray([model.psi_norms()[i + 1] for i in range(20)], dtype=float)
    rho = np.asarray(world["rho_env"][:20], dtype=float)
    if np.std(psi) == 0 or np.std(rho) == 0:
        return float("nan")
    return float(spearmanr(psi, rho).statistic)


def _roc_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=int).reshape(-1)
    scores = np.asarray(scores, dtype=float).reshape(-1)
    positive = labels == 1
    negative = labels == 0
    n_pos = int(positive.sum())
    n_neg = int(negative.sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = rankdata(scores, method="average")
    u = float(ranks[positive].sum() - n_pos * (n_pos + 1) / 2.0)
    return u / float(n_pos * n_neg)


def dauroc(model: Any, world: dict[str, Any]) -> float:
    """Compute M-DAUROC from artifact scores and median-split rho labels."""
    scores = np.asarray(
        [model.artifact_score(env["x_obs"], np.ones(len(env["x_obs"])), int(env["env_id"])) for env in world["environments"][:20]],
        dtype=float,
    )
    rho = np.asarray(world["rho_env"][:20], dtype=float)
    labels = (rho > np.median(rho)).astype(int)
    if np.std(scores) == 0:
        return float("nan")
    return float(_roc_auc(labels, scores))


__all__ = ["rmse_holdout", "psi_spearman", "dauroc"]
