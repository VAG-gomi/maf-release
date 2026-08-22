# MAF Release 1.0

MAF is the **Mechanism–Artifact Factorization** model from SPEC-M1. It separates a global mechanism channel from an environment artifact channel and masks the artifact channel from interventional prediction.

> Validated in synthetic confound-heavy environments with analytic ground truth (30 worlds, pre-registered criteria, independent execution). NOT validated on real-world data.

Release code reproduces pre-release results to within 2e-7 RMSE (float reassociation); behavioral equivalence verified by exact M-PSI match and do-mask bitwise test (D2).

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

`MAFModel.fit` uses the SPEC-M1 loop: 300 epochs, ascending training environments, one optimizer step per environment, equal row weighting, and the frozen `lambda1` argument. `predict_interventional` reads the beta mechanism channel only. `predict_observational` includes the environment artifact channel. `adapt` creates a zero-initialized new-environment artifact vector and trains only that vector.

## Verification

Run the six-file test suite with:

```bash
python -m pytest
```

The package also includes a read-only release verification battery under `verification/VERIFY.md`. The tests and release battery are designed to fail loudly on a do-mask leak, a deterministic regression mismatch, a metric mismatch, or missing package content. Tolerances are not loosened by the executor.

## Reproduction example

The end-to-end example is in `examples/run_example.py`; its measured output is documented in `docs/EXAMPLE.md`. The empirical card in `docs/EMPIRICAL_CARD.md` reports the exact thirteen-row SPEC-M1 T3 table and computed verdict.

## License

MIT. See `LICENSE`.
