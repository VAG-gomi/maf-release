"""Deterministic SPEC-M1 world generation."""
from __future__ import annotations

import math
from typing import Any

import numpy as np

N_ENVS = 25
N_TRAIN_ENVS = 20
N_TRIAL_ENVS = 10
N_HOLDOUT_ENVS = 5
N_OBS = 400
N_INT = 100
EVAL_N = 2000
SIGMA = 0.5
ETA = 1.0


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def _z_without_tau(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    return np.column_stack([np.ones(x.shape[0]), x, x[:, 2] ** 2, x[:, 3] * x[:, 4]])


def _seed_streams(seed: int) -> tuple[dict[str, int], dict[str, np.random.Generator]]:
    children = np.random.SeedSequence(int(seed)).spawn(7)
    names = ("world", "assign", "outcome", "sampling", "model_init", "adapt", "eval")
    keys = {name: int(child.generate_state(1, dtype=np.uint32)[0]) for name, child in zip(names, children)}
    rngs = {name: np.random.default_rng(keys[name]) for name in names}
    return keys, rngs


def generate_world(seed: int) -> dict[str, Any]:
    """Generate the deterministic SPEC-M1 world for ``seed``.

    The returned dictionary contains the bound mechanism parameters, per-environment
    observational/trial/holdout records, evaluation grids, auxiliary evaluation
    sample, and the seven integer stream keys. The generator is fixed at the
    selected SPEC-M1 gate scale ``b_scale=1.0``.
    """
    seed = int(seed)
    b_scale = 1.0
    keys, rng = _seed_streams(seed)
    r_world = rng["world"]
    theta = r_world.normal(0.0, 1.0, size=8) / math.sqrt(8.0)
    kappa = float(r_world.uniform(0.5, 1.5))
    a_env = np.empty(N_ENVS, dtype=float)
    rho_env = np.empty(N_ENVS, dtype=float)
    for e in range(N_ENVS):
        a_env[e] = float(r_world.uniform(-1.0, 1.0))
        rho_env[e] = float(r_world.uniform(0.0, 2.0))

    obs: list[dict[str, Any]] = []
    trial: list[dict[str, Any]] = []
    holdout: list[dict[str, Any]] = []
    environments: list[dict[str, Any]] = []
    for e0 in range(N_ENVS):
        env_id = e0 + 1
        x_obs = rng["sampling"].normal(0.0, 1.0, size=(N_OBS, 5))
        x_int = None
        tau_int = None
        y_int = None
        if env_id <= N_TRIAL_ENVS:
            x_int = rng["sampling"].normal(0.0, 1.0, size=(N_INT, 5))
            tau_int = rng["sampling"].integers(0, 2, size=N_INT).astype(float)
        h_obs = np.empty(N_OBS, dtype=float)
        tau_obs = np.empty(N_OBS, dtype=float)
        for i in range(N_OBS):
            h_obs[i] = float(rng["assign"].normal())
            u = float(rng["assign"].random())
            tau_obs[i] = float(u < float(_sigmoid(a_env[e0] + b_scale * 1.5 * rho_env[e0] * h_obs[i])))
        eps_obs = rng["outcome"].normal(0.0, SIGMA, size=N_OBS)
        y_obs = _z_without_tau(x_obs) @ theta + kappa * tau_obs + ETA * h_obs + eps_obs
        if x_int is not None and tau_int is not None:
            eps_int = rng["outcome"].normal(0.0, SIGMA, size=N_INT)
            y_int = _z_without_tau(x_int) @ theta + kappa * tau_int + eps_int
        env = {
            "env_id": env_id,
            "x_obs": x_obs,
            "h_obs": h_obs,
            "tau_obs": tau_obs,
            "y_obs": y_obs,
            "x_int": x_int,
            "tau_int": tau_int,
            "y_int": y_int,
            "a": a_env[e0],
            "rho": rho_env[e0],
        }
        environments.append(env)
        obs.append({"env_id": env_id, "x": x_obs, "h": h_obs, "tau": tau_obs, "y": y_obs})
        if x_int is not None and tau_int is not None and y_int is not None:
            trial.append({"env_id": env_id, "x": x_int, "tau": tau_int, "y": y_int})
        if env_id > N_TRAIN_ENVS:
            holdout.append({"env_id": env_id, "x": x_obs, "h": h_obs, "tau": tau_obs, "y": y_obs})

    h_aux = rng["eval"].normal(0.0, 1.0, size=100000)
    eval_grids = {env_id: rng["eval"].normal(0.0, 1.0, size=(EVAL_N, 5)) for env_id in range(21, 26)}
    return {
        "seed": seed,
        "b_scale": b_scale,
        "theta": theta,
        "kappa": kappa,
        "a_env": a_env,
        "rho_env": rho_env,
        "obs": obs,
        "trial": trial,
        "holdout": holdout,
        "environments": environments,
        "h_aux": h_aux,
        "eval_grids": eval_grids,
        "keys": keys,
    }


__all__ = ["generate_world"]
