# MAF Release 1.0 API

The public surface is intentionally limited to `maf.generate_world` and `maf.MAFModel`. Supporting metric and I/O modules are importable for research workflows but are not additional model surfaces.

## `maf.generate_world`

```python
maf.generate_world(seed: int) -> dict[str, Any]
```

Returns the deterministic SPEC-M1 world dictionary for the supplied integer seed. The dictionary contains `theta`, `kappa`, `a_env[25]`, `rho_env[25]`, `obs`, `trial`, `holdout`, `environments`, `h_aux`, `eval_grids`, `keys`, `b_scale`, and `seed`. Each environment record contains `x_obs[n,5]`, `tau_obs[n]`, `y_obs[n]`, optional `x_int[m,5]`, `tau_int[m]`, `y_int[m]`, `h_obs`, `a`, `rho`, and `env_id`.

## `maf.MAFModel`

```python
MAFModel(
    hidden: int = 16,
    r: int = 2,
    lambda1: float = 1e-3,
    weight_decay: float = 1e-4,
    seed: int | None = None,
)
```

The release binds `hidden=16` and `r=2`; passing other values raises `ValueError` rather than silently changing the architecture.

```python
model.fit(environments: list[EnvData]) -> FitReport
```

Fits 300 epochs with ascending environments and one optimizer step per environment per epoch. Observational rows and available trial interventional rows are included with equal row weighting. `FitReport` exposes `steps`, `epochs`, `environments`, and `duration_seconds`.

```python
model.adapt(
    x_obs: numpy.ndarray,
    tau_obs: numpy.ndarray,
    y_obs: numpy.ndarray,
    steps: int = 200,
    lr: float = 1e-2,
) -> AdaptReport
```

Creates a fresh zero-initialized `psi_new`, freezes the fitted model, and trains only the new artifact vector. `AdaptReport` exposes the assigned new environment ID, steps, learning rate, duration, and copied `psi_new` values.

```python
model.predict_interventional(x: numpy.ndarray, tau: numpy.ndarray) -> numpy.ndarray
```

Predicts using the beta mechanism channel only. Changing `U` or training-environment `psi` values cannot change these outputs.

```python
model.predict_observational(
    x: numpy.ndarray,
    tau: numpy.ndarray,
    env_id: int,
) -> numpy.ndarray
```

Predicts using the mechanism channel plus the artifact channel for the specified environment. For a new environment before adaptation, the artifact vector is exactly zero.

```python
model.psi_norms() -> dict[int, float]
```

Returns the L2 norm of each training-environment artifact vector, keyed by environment ID.

```python
model.artifact_score(
    x: numpy.ndarray,
    tau: numpy.ndarray,
    env_id: int,
) -> float
```

Returns the mean absolute artifact contribution `mean(abs(phi(x_full,tau)^T(U psi_e)))` for the specified environment.

## Supporting research helpers

`maf.metrics.rmse_holdout(model, world)`, `maf.metrics.psi_spearman(model, world)`, and `maf.metrics.dauroc(model, world)` implement the three SPEC-M1 metric definitions. `maf.io.save_config(path, config, provenance=None)` and `maf.io.load_config(path)` persist JSON configurations and provenance fields.
