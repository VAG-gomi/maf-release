"""SPEC-M1 MAF first-run executor.

The scientific choices in this file are bindings from SPEC-M1 and R1-R6;
the executor only supplies implementation mechanics and artifact handling.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
AUTO = ROOT / "maf_v1"
SEEDS = list(range(2000, 2030))
N_ENVS = 25
N_TRAIN_ENVS = 20
N_TRIAL_ENVS = 10
N_HOLDOUT_ENVS = 5
N_OBS = 400
N_INT = 100
EVAL_N = 2000
SIGMA = 0.5
ETA = 1.0
LAMBDA_CANDIDATES = (1e-2, 1e-3, 1e-4)
METHODS = ("V-FULL", "V-A0", "V-SOFT", "V-ORAC", "B-POOL", "B-ENVNN", "B-MIXED", "B-IRML")
BASELINES = ("B-POOL", "B-ENVNN", "B-MIXED", "B-IRML")


@dataclass
class EnvData:
    env_id: int
    x_obs: np.ndarray
    h_obs: np.ndarray
    tau_obs: np.ndarray
    y_obs: np.ndarray
    x_int: np.ndarray | None
    tau_int: np.ndarray | None
    y_int: np.ndarray | None
    a: float
    rho: float


@dataclass
class World:
    seed: int
    b_scale: float
    theta: np.ndarray
    kappa: float
    a: np.ndarray
    rho: np.ndarray
    envs: list[EnvData]
    h_aux: np.ndarray
    eval_grids: dict[int, np.ndarray]
    keys: dict[str, int]


@dataclass
class MethodResult:
    rmse_holdout: float
    rmse_heavy: float
    m_psi: float | None = None
    m_dauroc: float | None = None
    lambda_iv: float | None = None
    fit_seconds: float = 0.0


@dataclass
class GateResult:
    b_scale: float
    g0a_rows: list[dict[str, Any]]
    g0a_pass: bool
    g0b_rows: list[dict[str, Any]]
    g0b_lambda1: float | None
    g0b_best_correlation: float | None
    g0b_pass: bool


@dataclass
class RuntimeState:
    deviations: list[str] = field(default_factory=list)
    log_lines: list[str] = field(default_factory=list)


STATE = RuntimeState()


def log(message: str) -> None:
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"[{stamp}] {message}"
    STATE.log_lines.append(line)
    print(line, flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_json(path: Path, payload: Any) -> None:
    atomic_text(path, json.dumps(payload, indent=2, sort_keys=True, allow_nan=True) + "\n")


def atomic_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def write_status(stage: str, detail: str) -> None:
    atomic_text(
        AUTO / "STATUS.md",
        "# SPEC-M1 STATUS\n\n"
        f"Stage: {stage}\n\n"
        f"Detail: {detail}\n",
    )


def record_deviation(title: str, detail: str) -> None:
    STATE.deviations.append(f"## {title}\n\n{detail}\n")


def write_deviations() -> None:
    path = AUTO / "DEVIATIONS.md"
    existing = path.read_text(encoding="utf-8").rstrip() if path.exists() else "# SPEC-M1 Deviation Ledger"
    if STATE.deviations:
        existing = existing + "\n\n" + "\n".join(STATE.deviations)
        STATE.deviations = []
        atomic_text(path, existing + "\n")


def reset_outputs(mode: str) -> None:
    AUTO.mkdir(parents=True, exist_ok=True)
    generated_files = [
        "M1_ROWS.csv", "SUMMARY.csv", "HANDOFF.md", "ARTIFACT_MANIFEST.sha256",
    ]
    if mode == "gates":
        generated_files.extend(["GATE_REPORT.csv", "GATE_REPORT.md"])
    for name in generated_files:
        path = AUTO / name
        if path.exists():
            path.unlink()
    for name in ("configs", "worlds", "losses", "metrics", "logs", "results"):
        path = AUTO / name
        if path.exists():
            shutil.rmtree(path)
    for name in ("configs", "worlds", "losses", "metrics", "logs", "results"):
        (AUTO / name).mkdir(parents=True, exist_ok=True)
    STATE.deviations = []
    STATE.log_lines = []
    write_status("start: " + mode, "No downstream fit artifacts have been emitted.")


def seed_streams(seed: int) -> tuple[dict[str, int], dict[str, np.random.Generator]]:
    children = np.random.SeedSequence(seed).spawn(7)
    names = ("world", "assign", "outcome", "sampling", "model_init", "adapt", "eval")
    keys = {name: int(child.generate_state(1, dtype=np.uint32)[0]) for name, child in zip(names, children)}
    rngs = {name: np.random.default_rng(keys[name]) for name in names}
    return keys, rngs


def z_map(x: np.ndarray, tau: np.ndarray | float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    tau_arr = np.asarray(tau, dtype=float)
    if tau_arr.ndim == 0:
        tau_arr = np.full(x.shape[0], float(tau_arr), dtype=float)
    else:
        tau_arr = tau_arr.reshape(-1)
    return np.column_stack([np.ones(x.shape[0]), x, x[:, 2] ** 2, x[:, 3] * x[:, 4], tau_arr])


def z_without_tau(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    return np.column_stack([np.ones(x.shape[0]), x, x[:, 2] ** 2, x[:, 3] * x[:, 4]])


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def generate_world(seed: int, b_scale: float) -> World:
    keys, rng = seed_streams(seed)
    r_world = rng["world"]
    theta = r_world.normal(0.0, 1.0, size=8) / math.sqrt(8.0)
    kappa = float(r_world.uniform(0.5, 1.5))
    a = np.empty(N_ENVS, dtype=float)
    rho = np.empty(N_ENVS, dtype=float)
    for e in range(N_ENVS):
        a[e] = float(r_world.uniform(-1.0, 1.0))
        rho[e] = float(r_world.uniform(0.0, 2.0))
    envs: list[EnvData] = []
    for e0 in range(N_ENVS):
        e = e0 + 1
        x_obs = rng["sampling"].normal(0.0, 1.0, size=(N_OBS, 5))
        x_int = None
        tau_int = None
        if e <= N_TRIAL_ENVS:
            x_int = rng["sampling"].normal(0.0, 1.0, size=(N_INT, 5))
            tau_int = rng["sampling"].integers(0, 2, size=N_INT).astype(float)
        h_obs = np.empty(N_OBS, dtype=float)
        tau_obs = np.empty(N_OBS, dtype=float)
        for i in range(N_OBS):
            h_obs[i] = float(rng["assign"].normal())
            u = float(rng["assign"].random())
            tau_obs[i] = float(u < float(sigmoid(a[e0] + b_scale * 1.5 * rho[e0] * h_obs[i])))
        eps_obs = rng["outcome"].normal(0.0, SIGMA, size=N_OBS)
        y_obs = z_without_tau(x_obs) @ theta + kappa * tau_obs + ETA * h_obs + eps_obs
        y_int = None
        if x_int is not None and tau_int is not None:
            eps_int = rng["outcome"].normal(0.0, SIGMA, size=N_INT)
            y_int = z_without_tau(x_int) @ theta + kappa * tau_int + eps_int
        envs.append(EnvData(e, x_obs, h_obs, tau_obs, y_obs, x_int, tau_int, y_int, a[e0], rho[e0]))
    h_aux = rng["eval"].normal(0.0, 1.0, size=100000)
    eval_grids = {e: rng["eval"].normal(0.0, 1.0, size=(EVAL_N, 5)) for e in range(21, 26)}
    return World(seed, b_scale, theta, kappa, a, rho, envs, h_aux, eval_grids, keys)


def g0a_probe(world: World, scale: float) -> tuple[bool, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    for env in world.envs:
        xmat = np.column_stack([z_without_tau(env.x_obs), env.tau_obs])
        coef, *_ = np.linalg.lstsq(xmat, env.y_obs, rcond=None)
        resid = env.y_obs - xmat @ coef
        dof = max(1, len(resid) - xmat.shape[1])
        sigma2 = float((resid @ resid) / dof)
        xtx_inv = np.linalg.pinv(xmat.T @ xmat)
        se_tau = float(math.sqrt(max(0.0, sigma2 * xtx_inv[-1, -1])))
        rows.append({"scale": scale, "env": env.env_id, "tau_hat": float(coef[-1]), "se_tau": se_tau, "rho": env.rho})
    median_abs = float(np.median([abs(r["tau_hat"] - world.kappa) for r in rows]))
    median_se = float(np.median([r["se_tau"] for r in rows]))
    passed = bool(median_abs >= 3.0 * median_se)
    for r in rows:
        r["median_abs_error"] = median_abs
        r["median_se"] = median_se
        r["pass"] = passed
    return passed, rows


def conditional_biases(world: World) -> tuple[np.ndarray, np.ndarray]:
    p1 = sigmoid(world.a + 1.5 * world.b_scale * world.rho * world.h_aux[:, None])
    p1_num = (p1 * world.h_aux[:, None]).sum(axis=0)
    p1_den = p1.sum(axis=0)
    p0 = 1.0 - p1
    p0_num = (p0 * world.h_aux[:, None]).sum(axis=0)
    p0_den = p0.sum(axis=0)
    return ETA * p0_num / p0_den, ETA * p1_num / p1_den


def g0b_fit(world: World, lambda_candidate: float) -> float:
    m0, m1 = conditional_biases(world)
    g_parts: list[np.ndarray] = []
    target_parts: list[np.ndarray] = []
    for env in world.envs[:20]:
        g_parts.append(z_map(env.x_obs, env.tau_obs))
        target_parts.append(np.where(env.tau_obs > 0.5, m1[env.env_id - 1], m0[env.env_id - 1]))
    g_np = np.vstack(g_parts).astype(np.float32)
    t_np = np.concatenate(target_parts).astype(np.float32)
    torch.manual_seed(int(world.keys["world"] + 7000))
    u = torch.nn.Parameter(torch.randn((9, 2), dtype=torch.float32) * 0.01)
    psi = torch.nn.Parameter(torch.zeros((20, 2), dtype=torch.float32))
    opt = torch.optim.Adam([u, psi], lr=1e-3)
    g = torch.as_tensor(g_np)
    target = torch.as_tensor(t_np)
    for _ in range(2000):
        opt.zero_grad(set_to_none=True)
        pred = torch.cat([g[i * N_OBS : (i + 1) * N_OBS] @ (u @ psi[i]) for i in range(20)])
        loss = torch.mean((pred - target) ** 2) + lambda_candidate * torch.linalg.vector_norm(psi, dim=1).sum() + 1e-4 * torch.sum(u * u)
        loss.backward()
        opt.step()
    eval_pred: list[np.ndarray] = []
    eval_true: list[np.ndarray] = []
    for e in range(20):
        x = world.eval_grids[21 + (e % 5)]
        for tau, target_value in ((0.0, m0[e]), (1.0, m1[e])):
            gg = torch.as_tensor(z_map(x, tau).astype(np.float32))
            with torch.no_grad():
                pp = (gg @ (u @ psi[e])).cpu().numpy()
            eval_pred.append(pp)
            eval_true.append(np.full(EVAL_N, target_value, dtype=float))
    pred_flat = np.concatenate(eval_pred)
    true_flat = np.concatenate(eval_true)
    if np.std(pred_flat) == 0 or np.std(true_flat) == 0:
        return float("nan")
    return float(pearsonr(pred_flat, true_flat).statistic)


def run_gates() -> GateResult:
    g0a_rows_all: list[dict[str, Any]] = []
    selected_scale: float | None = None
    selected_world: World | None = None
    for scale in (1.0, 2.0, 4.0):
        world = generate_world(2000, scale)
        passed, rows = g0a_probe(world, scale)
        g0a_rows_all.extend(rows)
        log(f"G0a scale={scale:g} pass={passed}")
        if passed and selected_scale is None:
            selected_scale = scale
            selected_world = world
            break
    if selected_scale is None or selected_world is None:
        return GateResult(4.0, g0a_rows_all, False, [], None, None, False)
    g0b_rows: list[dict[str, Any]] = []
    passing: list[tuple[float, float]] = []
    for lam in LAMBDA_CANDIDATES:
        corr = g0b_fit(selected_world, lam)
        passed = bool(np.isfinite(corr) and corr > 0.5)
        g0b_rows.append({"lambda1": lam, "correlation": corr, "pass": passed})
        log(f"G0b lambda1={lam:g} correlation={corr:.8f} pass={passed}")
        if passed:
            passing.append((lam, corr))
    chosen = max(passing, key=lambda x: x[0]) if passing else None
    return GateResult(selected_scale, g0a_rows_all, True, g0b_rows, None if chosen is None else chosen[0], None if chosen is None else chosen[1], bool(chosen))


class MAFModel(torch.nn.Module):
    def __init__(self, variant: str, torch_seed: int):
        super().__init__()
        torch.manual_seed(int(torch_seed))
        self.variant = variant
        self.encoder = torch.nn.Sequential(torch.nn.Linear(6, 16), torch.nn.Tanh(), torch.nn.Linear(16, 8))
        self.beta = torch.nn.Parameter(torch.empty(8))
        torch.nn.init.normal_(self.beta, mean=0.0, std=0.01)
        self.channel = variant in ("V-FULL", "V-SOFT")
        if self.channel:
            self.U = torch.nn.Parameter(torch.empty((8, 2)))
            torch.nn.init.normal_(self.U, mean=0.0, std=0.01)
            self.psi = torch.nn.ParameterList([torch.nn.Parameter(torch.zeros(2)) for _ in range(20)])

    def phi(self, x: torch.Tensor, tau: torch.Tensor) -> torch.Tensor:
        return self.encoder(torch.cat([x, tau.reshape(-1, 1)], dim=1))

    def pred(self, x: torch.Tensor, tau: torch.Tensor, env_index: int, branch: str, psi_override: torch.Tensor | None = None) -> torch.Tensor:
        ph = self.phi(x, tau)
        out = ph @ self.beta
        if self.channel and (branch == "obs" or self.variant == "V-SOFT"):
            psi = self.psi[env_index] if psi_override is None else psi_override
            out = out + ph @ (self.U @ psi)
        return out

    def penalty(self, lambda1: float) -> torch.Tensor:
        reg = lambda1 * torch.tensor(0.0, dtype=torch.float32)
        if self.channel:
            reg = reg + lambda1 * torch.linalg.vector_norm(torch.stack(list(self.psi)), dim=1).sum()
        wd = torch.tensor(0.0, dtype=torch.float32)
        for p in self.parameters():
            wd = wd + torch.sum(p * p)
        return reg + 1e-4 * wd


def gaussian_nll(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return 0.5 * torch.mean(((target - pred) / SIGMA) ** 2 + 2.0 * math.log(SIGMA))


def train_maf(world: World, variant: str, lambda1: float) -> tuple[MAFModel, float]:
    started = time.monotonic()
    model = MAFModel(variant, world.keys["world"] + 7000)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for _epoch in range(300):
        for env in world.envs[:20]:
            x_parts = [env.x_obs]
            t_parts = [env.tau_obs]
            y_parts = [env.y_obs]
            b_parts = ["obs"] * len(env.y_obs)
            if env.env_id <= 10 and env.x_int is not None and env.tau_int is not None and env.y_int is not None:
                x_parts.append(env.x_int)
                t_parts.append(env.tau_int)
                y_parts.append(env.y_int)
                b_parts.extend(["int"] * len(env.y_int))
            x = torch.as_tensor(np.vstack(x_parts).astype(np.float32))
            tau = torch.as_tensor(np.concatenate(t_parts).astype(np.float32))
            y = torch.as_tensor(np.concatenate(y_parts).astype(np.float32))
            opt.zero_grad(set_to_none=True)
            obs_mask = torch.as_tensor(np.array([v == "obs" for v in b_parts]))
            int_mask = ~obs_mask
            pred = torch.empty_like(y)
            if bool(obs_mask.any()):
                pred[obs_mask] = model.pred(x[obs_mask], tau[obs_mask], env.env_id - 1, "obs")
            if bool(int_mask.any()):
                pred[int_mask] = model.pred(x[int_mask], tau[int_mask], env.env_id - 1, "int")
            loss = gaussian_nll(pred, y) + model.penalty(lambda1)
            loss.backward()
            opt.step()
    duration = time.monotonic() - started
    if duration > 900:
        record_deviation("DEVIATION-032 — fit exceeded fifteen minutes", f"seed={world.seed} variant={variant} duration_seconds={duration:.3f}")
    return model, duration


def adapt_psi(world: World, model: MAFModel, env: EnvData) -> torch.Tensor | None:
    if getattr(model, "variant", None) not in ("V-FULL", "V-SOFT"):
        return None
    torch.manual_seed(int(world.keys["world"] + 7000 + env.env_id))
    psi_new = torch.nn.Parameter(torch.zeros(2, dtype=torch.float32))
    opt = torch.optim.Adam([psi_new], lr=1e-2)
    x = torch.as_tensor(env.x_obs.astype(np.float32))
    tau = torch.as_tensor(env.tau_obs.astype(np.float32))
    y = torch.as_tensor(env.y_obs.astype(np.float32))
    for _ in range(200):
        opt.zero_grad(set_to_none=True)
        pred = model.pred(x, tau, 0, "obs", psi_override=psi_new)
        loss = gaussian_nll(pred, y)
        loss.backward()
        opt.step()
    return psi_new.detach()


def maf_psi_metrics(world: World, model: MAFModel, oracle: bool = False) -> tuple[float, float]:
    if oracle:
        psi_norm = []
        d_scores = []
        for env in world.envs[:20]:
            # V-ORAC stores its channel psi in the attached attributes below.
            psi_norm.append(float(torch.linalg.vector_norm(model.psi_orac[env.env_id - 1]).cpu()))
            x = torch.as_tensor(env.x_obs.astype(np.float32))
            tau = torch.ones(len(x), dtype=torch.float32)
            gg = torch.as_tensor(z_map(env.x_obs, tau.numpy()).astype(np.float32))
            with torch.no_grad():
                d_scores.append(float(torch.mean(torch.abs(gg @ (model.U_orac @ model.psi_orac[env.env_id - 1]))).cpu()))
    else:
        psi_norm = [float(torch.linalg.vector_norm(p).detach().cpu()) for p in model.psi]
        d_scores = []
        for env in world.envs[:20]:
            x = torch.as_tensor(env.x_obs.astype(np.float32))
            tau = torch.ones(len(x), dtype=torch.float32)
            with torch.no_grad():
                ph = model.phi(x, tau)
                d_scores.append(float(torch.mean(torch.abs(ph @ (model.U @ model.psi[env.env_id - 1]))).cpu()))
    rhos = np.asarray([e.rho for e in world.envs[:20]], dtype=float)
    if np.std(psi_norm) == 0 or np.std(rhos) == 0:
        mpsi = float("nan")
    else:
        mpsi = float(spearmanr(psi_norm, rhos).statistic)
    labels = (rhos > np.median(rhos)).astype(int)
    md = float(roc_auc_score(labels, d_scores)) if np.unique(labels).size == 2 and np.std(d_scores) > 0 else float("nan")
    return mpsi, md


def score_maf_holdout(world: World, model: MAFModel, method: str) -> tuple[float, float]:
    preds: list[np.ndarray] = []
    truth: list[np.ndarray] = []
    heavy_preds: list[np.ndarray] = []
    heavy_truth: list[np.ndarray] = []
    for env in world.envs[20:]:
        psi_new = adapt_psi(world, model, env)
        grid = world.eval_grids[env.env_id]
        for tau_value in (0.0, 0.5, 1.0):
            tau = np.full(len(grid), tau_value, dtype=np.float32)
            x = torch.as_tensor(grid.astype(np.float32))
            t = torch.as_tensor(tau)
            with torch.no_grad():
                if method == "V-ORAC":
                    mu = z_without_tau(grid) @ world.theta + world.kappa * tau_value
                else:
                    mu = model.pred(x, t, 0, "int", psi_override=psi_new).cpu().numpy()
            target = z_without_tau(grid) @ world.theta + world.kappa * tau_value
            preds.append(np.asarray(mu, dtype=float))
            truth.append(target)
            if env.rho >= 1.0:
                heavy_preds.append(np.asarray(mu, dtype=float))
                heavy_truth.append(target)
    p = np.concatenate(preds)
    y = np.concatenate(truth)
    hp = np.concatenate(heavy_preds) if heavy_preds else np.asarray([], dtype=float)
    hy = np.concatenate(heavy_truth) if heavy_truth else np.asarray([], dtype=float)
    return float(np.sqrt(np.mean((p - y) ** 2))), float(np.sqrt(np.mean((hp - hy) ** 2))) if len(hp) else float("nan")


class OracleModel:
    def __init__(self, world: World):
        torch.manual_seed(int(world.keys["world"] + 7000))
        self.U_orac = torch.nn.Parameter(torch.randn((9, 2), dtype=torch.float32) * 0.01)
        self.psi_orac = torch.nn.ParameterList([torch.nn.Parameter(torch.zeros(2, dtype=torch.float32)) for _ in range(20)])
        self.world = world

    def train(self, lambda1: float) -> float:
        started = time.monotonic()
        opt = torch.optim.Adam([self.U_orac, *list(self.psi_orac)], lr=1e-3)
        m0, m1 = conditional_biases(self.world)
        x_parts: list[np.ndarray] = []
        t_parts: list[np.ndarray] = []
        y_parts: list[np.ndarray] = []
        for env in self.world.envs[:20]:
            x_parts.append(env.x_obs)
            t_parts.append(env.tau_obs)
            y_parts.append(np.where(env.tau_obs > 0.5, m1[env.env_id - 1], m0[env.env_id - 1]))
        g = torch.as_tensor(np.vstack([z_map(x, t) for x, t in zip(x_parts, t_parts)]).astype(np.float32))
        target = torch.as_tensor(np.concatenate(y_parts).astype(np.float32))
        for _ in range(2000):
            opt.zero_grad(set_to_none=True)
            pieces = []
            start = 0
            for i in range(20):
                n = len(x_parts[i])
                pieces.append(g[start : start + n] @ (self.U_orac @ self.psi_orac[i]))
                start += n
            pred = torch.cat(pieces)
            loss = torch.mean((pred - target) ** 2) + lambda1 * torch.linalg.vector_norm(torch.stack(list(self.psi_orac)), dim=1).sum() + 1e-4 * torch.sum(self.U_orac * self.U_orac)
            loss.backward()
            opt.step()
        return time.monotonic() - started


def train_mlp_model(world: World, kind: str, lambda_iv: float | None = None) -> tuple[torch.nn.Module, float, float | None]:
    started = time.monotonic()
    torch.manual_seed(int(world.keys["world"] + 7000))
    if kind == "B-ENVNN":
        net = torch.nn.Sequential(torch.nn.Linear(10, 16), torch.nn.Tanh(), torch.nn.Linear(16, 1))
        emb = torch.nn.Parameter(torch.randn((25, 4), dtype=torch.float32) * 0.01)
        params = list(net.parameters()) + [emb]
    else:
        net = torch.nn.Sequential(torch.nn.Linear(6, 16), torch.nn.Tanh(), torch.nn.Linear(16, 1))
        emb = None
        params = list(net.parameters())
    opt = torch.optim.Adam(params, lr=1e-3)
    for _epoch in range(300):
        for env in world.envs[:20]:
            x_parts = [env.x_obs]
            t_parts = [env.tau_obs]
            y_parts = [env.y_obs]
            if env.env_id <= 10 and env.x_int is not None and env.tau_int is not None and env.y_int is not None:
                x_parts.append(env.x_int)
                t_parts.append(env.tau_int)
                y_parts.append(env.y_int)
            x_np = np.vstack(x_parts).astype(np.float32)
            t_np = np.concatenate(t_parts).astype(np.float32)
            y_np = np.concatenate(y_parts).astype(np.float32)
            x = torch.as_tensor(np.column_stack([x_np, t_np]))
            y = torch.as_tensor(y_np)
            if kind == "B-ENVNN":
                eidx = torch.full((len(x),), env.env_id - 1, dtype=torch.long)
                inp = torch.cat([x, emb[eidx]], dim=1)
            else:
                inp = x
            opt.zero_grad(set_to_none=True)
            pred = net(inp).squeeze(-1)
            loss = gaussian_nll(pred, y)
            if kind == "B-IRML" and lambda_iv is not None:
                loss = loss + lambda_iv * torch.mean((y - pred)) ** 2
            wd = sum(torch.sum(p * p) for p in params)
            loss = loss + 1e-4 * wd
            loss.backward()
            opt.step()
    dur = time.monotonic() - started
    if dur > 900:
        record_deviation("DEVIATION-033 — baseline fit exceeded fifteen minutes", f"seed={world.seed} kind={kind} duration_seconds={dur:.3f}")
    if kind == "B-ENVNN":
        net.emb_maf = emb
    return net, dur, None


def baseline_predict(model: torch.nn.Module, world: World, x: np.ndarray, tau: float, env_id: int, kind: str) -> np.ndarray:
    xfull = torch.as_tensor(np.column_stack([x, np.full(len(x), tau)]).astype(np.float32))
    if kind == "B-ENVNN":
        # Unseen environments use the declared zero embedding.
        if env_id > 20:
            emb = torch.zeros((len(xfull), 4), dtype=torch.float32)
        else:
            emb = model.emb_maf[torch.full((len(xfull),), env_id - 1, dtype=torch.long)]
        inp = torch.cat([xfull, emb], dim=1)
    else:
        inp = xfull
    with torch.no_grad():
        return model(inp).squeeze(-1).cpu().numpy()


def train_birm(world: World) -> tuple[torch.nn.Module, float, float]:
    candidates: list[tuple[float, torch.nn.Module, float, float]] = []
    for lam in (0.1, 1.0):
        model, dur, _ = train_mlp_model(world, "B-IRML", lam)
        errs: list[float] = []
        for env in world.envs[:10]:
            assert env.x_int is not None and env.tau_int is not None and env.y_int is not None
            pred = baseline_predict(model, world, env.x_int, 0.0, env.env_id, "B-IRML")
            # Replace tau through a direct call for each intervention row.
            pred = baseline_predict(model, world, env.x_int, 0.0, env.env_id, "B-IRML")
            pred1 = baseline_predict(model, world, env.x_int, 1.0, env.env_id, "B-IRML")
            pred = np.where(env.tau_int > 0.5, pred1, pred)
            errs.append(float(np.sqrt(np.mean((pred - env.y_int) ** 2))))
        score = float(np.mean(errs))
        candidates.append((score, model, dur, lam))
    candidates.sort(key=lambda x: (x[0], -x[3]))
    best = candidates[0]
    return best[1], best[2], best[3]


@dataclass
class MixedModel:
    wg: np.ndarray
    deviations: dict[int, np.ndarray]


def train_mixed(world: World) -> MixedModel:
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for env in world.envs[:20]:
        xs.append(z_map(env.x_obs, env.tau_obs))
        ys.append(env.y_obs)
        if env.x_int is not None and env.tau_int is not None and env.y_int is not None:
            xs.append(z_map(env.x_int, env.tau_int))
            ys.append(env.y_int)
    X = np.vstack(xs)
    y = np.concatenate(ys)
    wg, *_ = np.linalg.lstsq(X, y, rcond=None)
    dev: dict[int, np.ndarray] = {}
    for env in world.envs[:20]:
        Xe = z_map(env.x_obs, env.tau_obs)
        ye = env.y_obs
        if env.x_int is not None and env.tau_int is not None and env.y_int is not None:
            Xe = np.vstack([Xe, z_map(env.x_int, env.tau_int)])
            ye = np.concatenate([ye, env.y_int])
        resid = ye - Xe @ wg
        D = np.column_stack([np.ones(len(Xe)), Xe[:, -1]])
        raw = np.linalg.solve(D.T @ D + np.eye(2), D.T @ resid)
        dev[env.env_id] = (len(ye) / (len(ye) + 100.0)) * raw
    return MixedModel(wg, dev)


def mixed_predict(model: MixedModel, x: np.ndarray, tau: float) -> np.ndarray:
    X = z_map(x, tau)
    return X @ model.wg


def score_baseline(world: World, model: Any, kind: str) -> tuple[float, float]:
    preds: list[np.ndarray] = []
    truth: list[np.ndarray] = []
    hp: list[np.ndarray] = []
    hy: list[np.ndarray] = []
    for env in world.envs[20:]:
        grid = world.eval_grids[env.env_id]
        for tau in (0.0, 0.5, 1.0):
            if kind == "B-MIXED":
                mu = mixed_predict(model, grid, tau)
            else:
                mu = baseline_predict(model, world, grid, tau, env.env_id, kind)
            target = z_without_tau(grid) @ world.theta + world.kappa * tau
            preds.append(mu)
            truth.append(target)
            if env.rho >= 1.0:
                hp.append(mu)
                hy.append(target)
    p = np.concatenate(preds)
    y = np.concatenate(truth)
    hpp = np.concatenate(hp) if hp else np.asarray([], dtype=float)
    hyy = np.concatenate(hy) if hy else np.asarray([], dtype=float)
    return float(np.sqrt(np.mean((p - y) ** 2))), float(np.sqrt(np.mean((hpp - hyy) ** 2))) if len(hpp) else float("nan")


def create_gate_artifacts(gate: GateResult) -> None:
    atomic_csv(AUTO / "GATE_REPORT.csv", gate.g0a_rows + gate.g0b_rows, ["scale", "env", "tau_hat", "se_tau", "rho", "median_abs_error", "median_se", "pass", "lambda1", "correlation"])
    lines = [
        "# SPEC-M1 Gate Report",
        "",
        f"g0a_pass_scale: {gate.b_scale}",
        f"g0a_pass: {gate.g0a_pass}",
        f"g0b_lambda1_chosen: {gate.g0b_lambda1}",
        f"g0b_best_correlation: {gate.g0b_best_correlation}",
        f"g0b_pass: {gate.g0b_pass}",
    ]
    atomic_text(AUTO / "GATE_REPORT.md", "\n".join(lines) + "\n")


def save_config(world: World, lambda1: float, gate: GateResult) -> None:
    atomic_json(AUTO / "configs" / f"seed_{world.seed}.json", {
        "spec": "SPEC-M1 + SPEC-M1-R1 + SPEC-M1-R2 + SPEC-M1-R3 + SPEC-M1-R4 + SPEC-M1-R5 + SPEC-M1-R6",
        "seed": world.seed,
        "b_scale": world.b_scale,
        "theta": world.theta.tolist(),
        "kappa": world.kappa,
        "a": world.a.tolist(),
        "rho": world.rho.tolist(),
        "lambda1": lambda1,
        "torch_seed": world.keys["world"] + 7000,
        "seed_keys": world.keys,
        "g0a_pass_scale": gate.b_scale,
        "g0b_lambda1_chosen": gate.g0b_lambda1,
        "g0b_best_correlation": gate.g0b_best_correlation,
        "rng_binding": "SPEC-M1-R5-001",
    })


def save_world(world: World) -> None:
    payload: dict[str, Any] = {
        "theta": world.theta,
        "kappa": np.asarray([world.kappa]),
        "a": world.a,
        "rho": world.rho,
        "h_aux": world.h_aux,
    }
    for env in world.envs:
        payload[f"env{env.env_id}_x_obs"] = env.x_obs
        payload[f"env{env.env_id}_h_obs"] = env.h_obs
        payload[f"env{env.env_id}_tau_obs"] = env.tau_obs
        payload[f"env{env.env_id}_y_obs"] = env.y_obs
        if env.x_int is not None:
            payload[f"env{env.env_id}_x_int"] = env.x_int
            payload[f"env{env.env_id}_tau_int"] = env.tau_int
            payload[f"env{env.env_id}_y_int"] = env.y_int
        payload[f"env{env.env_id}_x_eval"] = world.eval_grids.get(env.env_id, np.empty((0, 5)))
    tmp = AUTO / "worlds" / f"seed_{world.seed}.npz.tmp"
    with tmp.open("wb") as f:
        np.savez_compressed(f, **payload)
    os.replace(tmp, AUTO / "worlds" / f"seed_{world.seed}.npz")


def fit_world(world: World, lambda1: float) -> tuple[dict[str, MethodResult], list[dict[str, Any]]]:
    results: dict[str, MethodResult] = {}
    losses: list[dict[str, Any]] = []
    for variant in ("V-FULL", "V-A0", "V-SOFT"):
        model, duration = train_maf(world, variant, lambda1)
        rmse, heavy = score_maf_holdout(world, model, variant)
        if variant == "V-A0":
            mpsi, md = None, None
        else:
            mpsi, md = maf_psi_metrics(world, model)
        results[variant] = MethodResult(rmse, heavy, mpsi if variant == "V-FULL" else None, md if variant == "V-FULL" else None, fit_seconds=duration)
        atomic_json(AUTO / "losses" / f"seed_{world.seed}_{variant}.json", {"fit_seconds": duration, "epochs": 300, "steps": 6000, "lambda1": lambda1})
    orac = OracleModel(world)
    odur = orac.train(lambda1)
    orac_mpsi, orac_md = maf_psi_metrics(world, orac, oracle=True)
    ormse, oheavy = score_maf_holdout(world, orac, "V-ORAC")
    results["V-ORAC"] = MethodResult(ormse, oheavy, orac_mpsi, orac_md, fit_seconds=odur)
    atomic_json(AUTO / "losses" / f"seed_{world.seed}_V-ORAC.json", {"fit_seconds": odur, "steps": 2000, "lambda1": lambda1})
    pool, pdur, _ = train_mlp_model(world, "B-POOL")
    prmse, pheavy = score_baseline(world, pool, "B-POOL")
    results["B-POOL"] = MethodResult(prmse, pheavy, fit_seconds=pdur)
    envnn, edur, _ = train_mlp_model(world, "B-ENVNN")
    ermse, eheavy = score_baseline(world, envnn, "B-ENVNN")
    results["B-ENVNN"] = MethodResult(ermse, eheavy, fit_seconds=edur)
    mixed = train_mixed(world)
    mrmse, mheavy = score_baseline(world, mixed, "B-MIXED")
    results["B-MIXED"] = MethodResult(mrmse, mheavy)
    irmodel, irdur, irlambda = train_birm(world)
    irmse, irheavy = score_baseline(world, irmodel, "B-IRML")
    results["B-IRML"] = MethodResult(irmse, irheavy, lambda_iv=irlambda, fit_seconds=irdur)
    for method, result in results.items():
        atomic_json(AUTO / "metrics" / f"seed_{world.seed}_{method}.json", {
            "seed": world.seed, "method": method, "rmse_holdout": result.rmse_holdout,
            "rmse_heavy": result.rmse_heavy, "m_psi": result.m_psi,
            "m_dauroc": result.m_dauroc, "lambda_iv": result.lambda_iv,
            "fit_seconds": result.fit_seconds,
        })
    return results, losses


def summary_and_verdict(all_world_results: dict[int, dict[str, MethodResult]]) -> tuple[list[dict[str, Any]], str]:
    rows = []
    for seed in SEEDS:
        for method in METHODS:
            r = all_world_results[seed][method]
            rows.append({"seed": seed, "variant_or_baseline": method, "rmse_holdout": r.rmse_holdout, "m_psi": r.m_psi, "m_dauroc": r.m_dauroc})
    def med(method: str, attr: str = "rmse_holdout") -> float:
        return float(np.median([getattr(all_world_results[s][method], attr) for s in SEEDS]))
    vfull = med("V-FULL")
    baseline_meds = {b: med(b) for b in BASELINES}
    best_name = min(baseline_meds, key=baseline_meds.get)
    best_rmse = baseline_meds[best_name]
    p1_rel = float((best_rmse - vfull) / best_rmse) if best_rmse != 0 else float("nan")
    p2 = med("V-FULL", "m_psi")
    p3 = med("V-FULL", "m_dauroc")
    k1_gaps = []
    k2_gaps = []
    for s in SEEDS:
        full = all_world_results[s]["V-FULL"].rmse_heavy
        a0 = all_world_results[s]["V-A0"].rmse_heavy
        soft = all_world_results[s]["V-SOFT"].rmse_heavy
        if np.isfinite(full) and full != 0:
            k1_gaps.append(100.0 * (a0 - full) / abs(full))
            k2_gaps.append(100.0 * (soft - full) / abs(full))
    k1 = float(np.median(k1_gaps)) if k1_gaps else float("nan")
    k2 = float(np.median(k2_gaps)) if k2_gaps else float("nan")
    k4 = med("V-ORAC", "m_psi")
    p1 = bool(p1_rel >= 0.25)
    p2ok = bool(p2 >= 0.6)
    p3ok = bool(p3 >= 0.8)
    k1fire = bool(np.isfinite(k1) and abs(k1) <= 5.0)
    k2fire = bool(np.isfinite(k2) and abs(k2) <= 5.0)
    k3fire = bool(np.isfinite(p2) and p2 < 0.3)
    k4fire = bool(np.isfinite(k4) and k4 < 0.3)
    if p1 and p2ok and p3ok:
        verdict = "PASS"
    else:
        kill_codes = [code for code, fire in (("K1", k1fire), ("K2", k2fire), ("K3", k3fire), ("K4", k4fire)) if fire]
        verdict = "KILL-" + kill_codes[0] if kill_codes else "INCONCLUSIVE"
    summary = [
        ("g0a_pass_scale", None),
        ("g0b_lambda1_chosen", None),
        ("g0b_best_correlation", None),
        ("p1_vfull_rmse_median", vfull),
        ("p1_best_baseline_name", best_name),
        ("p1_best_baseline_rmse_median", best_rmse),
        ("p1_relative_reduction", p1_rel),
        ("p2_mpsi_median", p2),
        ("p3_mdauroc_median", p3),
        ("k1_gap_percent", k1),
        ("k2_gap_percent", k2),
        ("k4_vorac_mpsi_median", k4),
        ("verdict_label", verdict),
    ]
    return rows, verdict, summary


def write_manifest() -> None:
    lines: list[str] = []
    for path in sorted(AUTO.rglob("*")):
        if path.is_file() and path.name != "ARTIFACT_MANIFEST.sha256" and not path.name.endswith(".tmp"):
            lines.append(f"{sha256_file(path)}  {path.relative_to(AUTO).as_posix()}")
    atomic_text(AUTO / "ARTIFACT_MANIFEST.sha256", "\n".join(lines) + "\n")


def write_handoff(gate: GateResult, summary: list[tuple[str, Any]], verdict: str, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# SPEC-M1 MAF Evidence Handoff",
        "",
        "> Evidence ends at the computed T2 summary. No post-hoc scientific classification is applied by the executor.",
        "",
        "## T1 — M1_ROWS.csv",
        "",
        "The complete 240-row table is attached as `M1_ROWS.csv`.",
        "",
        "## T2 — Summary.csv",
        "",
        "| statistic | value |",
        "|---|---:|",
    ]
    for name, value in summary:
        if name == "g0a_pass_scale": value = gate.b_scale
        if name == "g0b_lambda1_chosen": value = gate.g0b_lambda1
        if name == "g0b_best_correlation": value = gate.g0b_best_correlation
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        "## T3 — DEVIATIONS.md",
        "",
        "The complete deviation ledger is attached as `DEVIATIONS.md`.",
        "",
        "## T4 — ARTIFACT_MANIFEST.sha256",
        "",
        "The complete SHA-256 manifest is attached as `ARTIFACT_MANIFEST.sha256`.",
        "",
        "## Provenance",
        "",
        f"Repository commit: `{subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()}`.",
        f"Gate-selected b_scale: `{gate.b_scale}`. Gate-selected lambda1: `{gate.g0b_lambda1}`. Best G0b correlation: `{gate.g0b_best_correlation}`.",
        "",
        "## Final computed label",
        "",
        f"`{verdict}`",
    ]
    atomic_text(AUTO / "HANDOFF.md", "\n".join(lines) + "\n")


def run(mode: str) -> int:
    reset_outputs(mode)
    write_deviations()
    if mode == "gates":
        gate = run_gates()
        create_gate_artifacts(gate)
        write_status("completion: gates", f"G0a pass scale={gate.b_scale}; G0b lambda1={gate.g0b_lambda1}; best correlation={gate.g0b_best_correlation}; G0a_pass={gate.g0a_pass}; G0b_pass={gate.g0b_pass}.")
        write_deviations()
        atomic_text(AUTO / "logs" / "gates.log", "\n".join(STATE.log_lines) + "\n")
        write_manifest()
        return 0 if gate.g0a_pass and gate.g0b_pass else 2
    gate_path = AUTO / "GATE_REPORT.md"
    if not gate_path.exists():
        record_deviation("DEVIATION-034 — Full mode requested without gate report", "The full runner requires a completed G0a/G0b gate report.")
        write_deviations()
        return 2
    gate_lines = gate_path.read_text(encoding="utf-8").splitlines()
    vals = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in gate_lines if ":" in line}
    gate = GateResult(float(vals["g0a_pass_scale"]), [], vals.get("g0a_pass", "False") == "True", [], float(vals["g0b_lambda1_chosen"]) if vals.get("g0b_lambda1_chosen") not in ("None", "null") else None, float(vals["g0b_best_correlation"]) if vals.get("g0b_best_correlation") not in ("None", "null") else None, vals.get("g0b_pass", "False") == "True")
    if not (gate.g0a_pass and gate.g0b_pass and gate.g0b_lambda1 is not None):
        record_deviation("DEVIATION-035 — Gate report does not authorize full run", "G0a/G0b did not both pass; full artifacts were not generated.")
        write_deviations()
        return 2
    all_results: dict[int, dict[str, MethodResult]] = {}
    all_rows: list[dict[str, Any]] = []
    for idx, seed in enumerate(SEEDS, start=1):
        world = generate_world(seed, gate.b_scale)
        save_config(world, gate.g0b_lambda1, gate)
        save_world(world)
        results, _ = fit_world(world, gate.g0b_lambda1)
        all_results[seed] = results
        log(f"completed world={seed} index={idx}/30")
        if idx == 15:
            write_status("midpoint: 15/30 worlds", "No parameter, gate, or criterion changes were made after observing partial results.")
    rows, verdict, summary = summary_and_verdict(all_results)
    atomic_csv(AUTO / "M1_ROWS.csv", rows, ["seed", "variant_or_baseline", "rmse_holdout", "m_psi", "m_dauroc"])
    summary_values = {
        "g0a_pass_scale": gate.b_scale,
        "g0b_lambda1_chosen": gate.g0b_lambda1,
        "g0b_best_correlation": gate.g0b_best_correlation,
    }
    summary_rows = [{"statistic": name, "value": summary_values.get(name, value)} for name, value in summary]
    atomic_csv(AUTO / "SUMMARY.csv", summary_rows, ["statistic", "value"])
    atomic_json(AUTO / "results" / "verdict.json", {"verdict_label": verdict, "summary": summary_rows, "n_worlds": 30, "n_methods": 8})
    write_status("completion: full run", f"30/30 worlds; 240 method rows; verdict={verdict}.")
    write_deviations()
    atomic_text(AUTO / "logs" / "full_run.log", "\n".join(STATE.log_lines) + "\n")
    write_handoff(gate, summary, verdict, rows)
    write_manifest()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("gates", "full"), required=True)
    args = parser.parse_args()
    try:
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        return run(args.mode)
    except Exception as exc:
        record_deviation("DEVIATION-036 — Unhandled runtime failure", f"{type(exc).__name__}: {exc}")
        write_deviations()
        write_status("failure", f"{type(exc).__name__}: {exc}")
        atomic_text(AUTO / "logs" / "failure.log", "\n".join(STATE.log_lines + [repr(exc)]) + "\n")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
