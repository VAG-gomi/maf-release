"""The public SPEC-M1 MAF model API."""
from __future__ import annotations

import math
import time
import warnings
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

SIGMA = 0.5
N_TRAIN_ENVS = 20
N_TRIAL_ENVS = 10


def _z_map(x: np.ndarray, tau: np.ndarray | float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    tau_arr = np.asarray(tau, dtype=float)
    if tau_arr.ndim == 0:
        tau_arr = np.full(x.shape[0], float(tau_arr), dtype=float)
    else:
        tau_arr = tau_arr.reshape(-1)
    return np.column_stack([np.ones(x.shape[0]), x, x[:, 2] ** 2, x[:, 3] * x[:, 4], tau_arr])


@dataclass(frozen=True)
class FitReport:
    steps: int
    epochs: int
    environments: int
    duration_seconds: float


@dataclass(frozen=True)
class AdaptReport:
    env_id: int
    steps: int
    lr: float
    duration_seconds: float
    psi_new: np.ndarray


class MAFModel(torch.nn.Module):
    """Mechanism–Artifact Factorization model with the SPEC-M1 do-mask."""

    def __init__(
        self,
        hidden: int = 16,
        r: int = 2,
        lambda1: float = 1e-3,
        weight_decay: float = 1e-4,
        seed: int | None = None,
        input_dim: int = 5,
    ) -> None:
        super().__init__()
        if hidden != 16 or r != 2:
            raise ValueError("SPEC-M2 binds hidden=16 and r=2")
        if int(input_dim) <= 0:
            raise ValueError("input_dim must be positive")
        self.hidden = int(hidden)
        self.r = int(r)
        self.input_dim = int(input_dim)
        self.lambda1 = float(lambda1)
        self.weight_decay = float(weight_decay)
        self.seed = None if seed is None else int(seed)
        if seed is not None:
            torch.manual_seed(int(seed))
        self.encoder = torch.nn.Sequential(torch.nn.Linear(self.input_dim + 1, 16), torch.nn.Tanh(), torch.nn.Linear(16, 8))
        self.beta = torch.nn.Parameter(torch.empty(8))
        torch.nn.init.normal_(self.beta, mean=0.0, std=0.01)
        self.U = torch.nn.Parameter(torch.empty((8, 2)))
        torch.nn.init.normal_(self.U, mean=0.0, std=0.01)
        # G1.1(b): sized at fit time from the supplied environment count.
        self.psi = torch.nn.ParameterList([])
        self._train_envs: list[dict[str, Any]] = []
        self._adapted_psi: dict[int, torch.Tensor] = {}
        self._next_adapt_env_id = 1
        self._fit_report: FitReport | None = None

    def phi(self, x: torch.Tensor, tau: torch.Tensor) -> torch.Tensor:
        if x.ndim != 2 or int(x.shape[1]) != self.input_dim:
            raise ValueError(f"x must have shape (n, {self.input_dim})")
        return self.encoder(torch.cat([x, tau.reshape(-1, 1)], dim=1))

    def _psi_for_env(self, env_id: int) -> torch.Tensor:
        env_id = int(env_id)
        if 1 <= env_id <= len(self._train_envs):
            return self.psi[env_id - 1]
        if env_id in self._adapted_psi:
            return self._adapted_psi[env_id]
        return torch.zeros(self.r, dtype=self.beta.dtype, device=self.beta.device)

    @staticmethod
    def _validate_tau(tau: np.ndarray | float) -> np.ndarray:
        tau_arr = np.asarray(tau, dtype=float)
        invalid = (tau_arr < 0.0) | (tau_arr > 1.0)
        if bool(np.any(invalid)):
            offending = float(tau_arr[invalid].reshape(-1)[0])
            raise ValueError(f"tau value {offending} outside [0, 1]")
        return tau_arr

    def _pred_tensor(
        self,
        x: torch.Tensor,
        tau: torch.Tensor,
        env_id: int,
        branch: str,
        psi_override: torch.Tensor | None = None,
    ) -> torch.Tensor:
        ph = self.phi(x, tau)
        out = ph @ self.beta
        # The do-mask: Gamma is excluded from interventional predictions.
        if branch == "obs":
            psi = self._psi_for_env(env_id) if psi_override is None else psi_override
            out = out + ph @ (self.U @ psi)
        return out

    def _penalty(self) -> torch.Tensor:
        reg = self.lambda1 * torch.linalg.vector_norm(torch.stack(list(self.psi)), dim=1).sum()
        wd = torch.tensor(0.0, dtype=torch.float32, device=self.beta.device)
        for parameter in self.parameters():
            wd = wd + torch.sum(parameter * parameter)
        return reg + self.weight_decay * wd

    @staticmethod
    def _gaussian_nll(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return 0.5 * torch.mean(((target - pred) / SIGMA) ** 2 + 2.0 * math.log(SIGMA))

    def fit(self, environments: list[dict[str, Any]]) -> FitReport:
        """Fit on ascending environments with 300 epochs and one optimizer step per environment.

        Input environments are sorted by ``env_id`` ascending; records without an
        ``env_id`` use their one-based positional index for sorting.
        """
        if self._fit_report is not None:
            warnings.warn("refitting over previously fitted model", RuntimeWarning)
        # G1.1(a): the generalized interface accepts the authored real-data
        # environment cardinalities; no other validation is relaxed.
        if len(environments) < 2:
            raise ValueError("fit requires at least 2 training environments")
        for env in environments:
            for field in ("x_obs", "x_int"):
                value = env.get(field)
                if value is not None:
                    array = np.asarray(value)
                    if array.ndim != 2 or int(array.shape[1]) != self.input_dim:
                        raise ValueError(f"{field} must have feature width {self.input_dim}")
        keyed = [(int(env.get("env_id", index + 1)), index, env) for index, env in enumerate(environments)]
        self._train_envs = [env for _, _, env in sorted(keyed, key=lambda item: (item[0], item[1]))[:N_TRAIN_ENVS]]
        # G1.1(b): ParameterList size is set from len(environments) at fit time.
        self.psi = torch.nn.ParameterList([torch.nn.Parameter(torch.zeros(2)) for _ in range(len(environments))])
        self._adapted_psi.clear()
        # G1.1(c): new environment IDs follow the actual trained set.
        self._next_adapt_env_id = len(self._train_envs) + 1
        started = time.monotonic()
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
        for _epoch in range(300):
            for env_index, env in enumerate(self._train_envs):
                x_parts = [np.asarray(env["x_obs"])]
                t_parts = [np.asarray(env["tau_obs"])]
                y_parts = [np.asarray(env["y_obs"])]
                branch_parts = ["obs"] * len(y_parts[0])
                env_id = int(env.get("env_id", env_index + 1))
                if env_id <= N_TRIAL_ENVS and env.get("x_int") is not None and env.get("tau_int") is not None and env.get("y_int") is not None:
                    x_parts.append(np.asarray(env["x_int"]))
                    t_parts.append(np.asarray(env["tau_int"]))
                    y_parts.append(np.asarray(env["y_int"]))
                    branch_parts.extend(["int"] * len(y_parts[-1]))
                x = torch.as_tensor(np.vstack(x_parts).astype(np.float32))
                tau = torch.as_tensor(np.concatenate(t_parts).astype(np.float32))
                y = torch.as_tensor(np.concatenate(y_parts).astype(np.float32))
                optimizer.zero_grad(set_to_none=True)
                obs_mask = torch.as_tensor(np.array([v == "obs" for v in branch_parts]))
                int_mask = ~obs_mask
                pred = torch.empty_like(y)
                if bool(obs_mask.any()):
                    pred[obs_mask] = self._pred_tensor(x[obs_mask], tau[obs_mask], env_id, "obs")
                if bool(int_mask.any()):
                    pred[int_mask] = self._pred_tensor(x[int_mask], tau[int_mask], env_id, "int")
                loss = self._gaussian_nll(pred, y) + self._penalty()
                loss.backward()
                optimizer.step()
        duration = time.monotonic() - started
        self._fit_report = FitReport(steps=300 * len(self._train_envs), epochs=300, environments=len(self._train_envs), duration_seconds=duration)
        return self._fit_report

    def adapt(self, x_obs: np.ndarray, tau_obs: np.ndarray, y_obs: np.ndarray, steps: int = 200, lr: float = 1e-2) -> AdaptReport:
        """Adapt one new environment by training only a fresh zero-initialized psi.

        The bound public signature does not carry an environment identifier. New
        environments are therefore assigned deterministic slots immediately after
        the trained environment set in adaptation-call order; the assigned slot is
        returned in ``AdaptReport``.
        """
        if self._fit_report is None:
            raise RuntimeError("model not fitted: call fit() first")
        tau_arr = self._validate_tau(tau_obs)
        env_id = self._next_adapt_env_id
        self._next_adapt_env_id += 1
        started = time.monotonic()
        if self.seed is not None:
            # This is the bound per-environment adaptation seed convention.
            torch.manual_seed(int(self.seed + env_id))
        psi_new = torch.nn.Parameter(torch.zeros(self.r, dtype=torch.float32))
        optimizer = torch.optim.Adam([psi_new], lr=float(lr))
        x = torch.as_tensor(np.asarray(x_obs, dtype=np.float32))
        tau = torch.as_tensor(np.asarray(tau_arr, dtype=np.float32))
        y = torch.as_tensor(np.asarray(y_obs, dtype=np.float32))
        frozen = [parameter.requires_grad for parameter in self.parameters()]
        try:
            for parameter in self.parameters():
                parameter.requires_grad_(False)
            for _ in range(int(steps)):
                optimizer.zero_grad(set_to_none=True)
                pred = self._pred_tensor(x, tau, env_id, "obs", psi_override=psi_new)
                loss = self._gaussian_nll(pred, y)
                loss.backward()
                optimizer.step()
        finally:
            for parameter, requires_grad in zip(self.parameters(), frozen):
                parameter.requires_grad_(requires_grad)
        self._adapted_psi[env_id] = psi_new.detach().clone()
        return AdaptReport(env_id=env_id, steps=int(steps), lr=float(lr), duration_seconds=time.monotonic() - started, psi_new=self._adapted_psi[env_id].numpy().copy())

    def predict_interventional(self, x: np.ndarray, tau: np.ndarray) -> np.ndarray:
        """Predict under intervention using the beta channel only."""
        if self._fit_report is None:
            raise RuntimeError("model not fitted: call fit() first")
        x_np = np.asarray(x, dtype=np.float32)
        tau_np = np.asarray(self._validate_tau(tau), dtype=np.float32).reshape(-1)
        x_tensor = torch.as_tensor(x_np)
        tau_tensor = torch.as_tensor(tau_np)
        with torch.no_grad():
            return self._pred_tensor(x_tensor, tau_tensor, 0, "int").cpu().numpy()

    def predict_observational(self, x: np.ndarray, tau: np.ndarray, env_id: int) -> np.ndarray:
        """Predict observationally, including the environment artifact channel."""
        if self._fit_report is None:
            raise RuntimeError("model not fitted: call fit() first")
        x_np = np.asarray(x, dtype=np.float32)
        tau_np = np.asarray(self._validate_tau(tau), dtype=np.float32).reshape(-1)
        with torch.no_grad():
            return self._pred_tensor(torch.as_tensor(x_np), torch.as_tensor(tau_np), int(env_id), "obs").cpu().numpy()

    def psi_norms(self) -> dict[int, float]:
        """Return train-environment artifact magnitudes."""
        if self._fit_report is None:
            raise RuntimeError("model not fitted: call fit() first")
        return {i + 1: float(torch.linalg.vector_norm(parameter).detach().cpu()) for i, parameter in enumerate(self.psi)}

    def artifact_score(self, x: np.ndarray, tau: np.ndarray, env_id: int) -> float:
        """Return mean absolute artifact contribution for one environment."""
        if self._fit_report is None:
            raise RuntimeError("model not fitted: call fit() first")
        x_tensor = torch.as_tensor(np.asarray(x, dtype=np.float32))
        tau_tensor = torch.as_tensor(np.asarray(self._validate_tau(tau), dtype=np.float32).reshape(-1))
        with torch.no_grad():
            ph = self.phi(x_tensor, tau_tensor)
            contribution = ph @ (self.U @ self._psi_for_env(int(env_id)))
            return float(torch.mean(torch.abs(contribution)).cpu())


__all__ = ["MAFModel", "FitReport", "AdaptReport"]
