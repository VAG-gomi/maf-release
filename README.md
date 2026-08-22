# MAF Release 1.1

MAF is the **Mechanism–Artifact Factorization** model from SPEC-M1. It separates a global mechanism channel from an environment artifact channel and masks the artifact channel from interventional prediction.

> Validated in synthetic confound-heavy environments with analytic ground truth (30 worlds, pre-registered criteria, independent execution). NOT validated on real-world data.

Release code reproduces pre-release results to within 2e-7 RMSE (float reassociation); behavioral equivalence verified by exact M-PSI match and do-mask bitwise test (D2).

Why the do-mask matters: an otherwise-identical variant without it (V-SOFT) tracked confounding erratically and degraded interventional accuracy by 251% relative in the validation study. The mask is not decoration; removal is catastrophic.

## Installation

From a clean Python 3.10-or-newer environment:

```bash
python -m pip install .
```

The release pins NumPy, pandas, SciPy, and PyTorch. The package exposes only the bound public surface:

```python
import maf

world = maf.generate_world(2000)
model = maf.MAFModel(seed=world["keys"]["world"] + 7000)
model.fit(world["environments"])
```

## Core behavior

All prediction, adaptation, artifact-norm, and artifact-score entry points require a fitted model and raise `RuntimeError("model not fitted: call fit() first")` otherwise. All treatment values must lie in the inclusive interval `[0, 1]`; invalid values raise `ValueError` naming the offending value. Calling `fit()` again is permitted but emits `RuntimeWarning("refitting over previously fitted model")`. Input environments are sorted by ascending `env_id` before training.

`MAFModel.fit` uses the SPEC-M1 loop: 300 epochs, ascending training environments, one optimizer step per environment, equal row weighting, and the frozen `lambda1` argument. `predict_interventional` reads the beta mechanism channel only. `predict_observational` includes the environment artifact channel. `adapt` creates a zero-initialized new-environment artifact vector and trains only that vector.

## Verification

Run the nine-test suite with:

```bash
python -m pytest
```

The package also includes a read-only release verification battery under `verification/VERIFY.md`. The tests and release battery are designed to fail loudly on a do-mask leak, a deterministic regression mismatch, a metric mismatch, misuse of an unfitted model, invalid treatment values, a silent refit, or missing package content. Tolerances are not loosened by the executor.

## Reproduction example

The end-to-end example is in `examples/run_example.py`; its measured output is documented in `docs/EXAMPLE.md`. The empirical card in `docs/EMPIRICAL_CARD.md` reports the exact thirteen-row SPEC-M1 T3 table and computed verdict.

## License

MIT. See `LICENSE`.
