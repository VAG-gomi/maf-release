# MAF Model Overview

This document explains the actual MAF implementation in [`../src/maf/model.py`](../src/maf/model.py). It is a reading guide only; the Python file linked above is the executable model source.

## Model identity

MAF means **Mechanism–Artifact Factorization**. The model represents a shared mechanism channel and an environment-specific artifact channel. The interventional prediction path uses the mechanism channel only; the observational path may include the environment artifact contribution.

The implementation is the `MAFModel` class in `src/maf/model.py`. It is built with PyTorch and uses a shared encoder, a mechanism parameter `beta`, an artifact loading matrix `U`, and environment-specific artifact vectors `psi`.

## Actual implementation map

| Source location | Implementation | Meaning |
|---|---|---|
| `model.py:47–77` | `class MAFModel` and `__init__` | Creates the encoder, mechanism vector, artifact loading matrix, and training-environment artifact vectors. |
| `model.py:79–80` | `phi` | Encodes covariates and treatment into an 8-dimensional representation. |
| `model.py:82–88` | `_psi_for_env` | Selects the artifact vector for a training or adapted environment. |
| `model.py:90–97` | `_validate_tau` | Enforces the inclusive treatment range `[0, 1]`. |
| `model.py:99–113` | `_pred_tensor` | Computes predictions and applies the interventional do-mask. |
| `model.py:115–124` | `_penalty`, `_gaussian_nll` | Defines regularization and Gaussian negative log-likelihood. |
| `model.py:126–170` | `fit` | Sorts environments, fits for 300 epochs, and records the fit report. |
| `model.py:172–207` | `adapt` | Fits only a new zero-initialized artifact vector for an unseen environment. |
| `model.py:209–227` | `predict_interventional`, `predict_observational` | Exposes the two prediction pathways. |
| `model.py:229–244` | `psi_norms`, `artifact_score` | Reports artifact magnitudes and contribution scores. |

## The do-mask

The central separation is visible in `_pred_tensor`:

```python
ph = self.phi(x, tau)
out = ph @ self.beta
if branch == "obs":
    psi = self._psi_for_env(env_id) if psi_override is None else psi_override
    out = out + ph @ (self.U @ psi)
return out
```

When `branch == "int"`, the artifact term is not added. This is the code-level do-mask. When `branch == "obs"`, the environment artifact term is included.

## Fitting

`MAFModel.fit` requires at least 20 environments. It sorts the inputs by `env_id`, uses the first 20 training environments, and performs 300 epochs with one optimizer step per environment. The implementation combines observational rows with interventional rows for the first 10 environments when those rows are present.

The fitted model stores a `FitReport` with the number of steps, epochs, environment count, and duration. Calling `fit` a second time emits the bound refitting warning rather than silently hiding the repeated fit.

## Adaptation

`adapt` requires a fitted model. It creates a new zero-initialized `psi` vector, freezes the shared mechanism parameters, and optimizes only the new environment artifact vector. Adaptation slots are assigned deterministically starting at environment 21.

## Relationship to the original evidence runner

The original 30-world SPEC-M1 evidence was emitted by the actual runner at [`../research/maf-spec-m1/run_maf.py`](../research/maf-spec-m1/run_maf.py). That runner contains the experiment-specific model variants and baselines, generates worlds, trains the variants, computes metrics, writes T2/T3 artifacts, and determines the recorded verdict.

The reusable package model in `src/maf/model.py` is the polished public API. The evidence runner in `research/maf-spec-m1/run_maf.py` is the historical experiment executor. Both are preserved as actual Python source files; neither is a prose substitute for the other.

## Verification

The package tests are in [`../tests/`](../tests/). The release verification report is [`../verification/VERIFY.md`](../verification/VERIFY.md). The raw experiment verifier is [`../research/maf-spec-m1/verify_maf_bundle.py`](../research/maf-spec-m1/verify_maf_bundle.py).

## Scope boundary

The model and results were validated in synthetic confound-heavy environments with analytic ground truth. They are **not validated on real-world data** and should not be read as evidence of clinical validity, operational reliability, deployment safety, or general real-world performance.
