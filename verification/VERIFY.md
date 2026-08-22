# MAF Release 1.0 Verification Report

## Overall status

**PASS — MAF Release 1.0 acceptance battery completed under SPEC-M2-R1.**

The package was constructed only under `maf_release/`. Existing `maf_v1/`, `f1_v2/`, `f1_v2_autopsy/`, `lhe_v1/`, and the `F1-v1-baseline` tag were not modified. D-047 was resolved by the binding R1 re-anchor; D-048 was resolved by shipping only `verification/VERIFY.md` and treating `VERIFY_REPORT.md` as the external H2 transmission copy.

## F acceptance checklist

| Criterion | Status | Evidence |
|---|---|---|
| F1. Fresh venv: `pip install .` and `import maf` | PASS | Fresh `/tmp/maf_spec_m2_venv`; install exit 0; import exit 0; version `1.0.0`; exports `MAFModel`, `generate_world` |
| F2. Full pytest: six files, zero skips/xfails | PASS | `/tmp/maf_spec_m2_venv/bin/python -m pytest -ra`: `6 passed in 99.26s (0:01:39)` |
| F3. Determinism D5 | PASS | `tests/test_determinism.py`: passed; bitwise-identical prediction arrays |
| F4. Regression anchors D4/D6 | PASS | D4 new RMSE anchor and D6 M-DAUROC both passed within bound tolerances |
| F5. §B files and documentation bindings | PASS | All enumerated paths non-empty; six test files; exact scope and R1 disclosure sentences present |
| F6. SHA-256 manifest over `maf_release/` | PASS | Manifest path set and every listed hash verified; all specification subtrees included; only self-entry excluded as technically non-recursive |
| F7. Three prior-tree hash spot-checks | PASS | Three recorded earlier-manifest hashes matched current files exactly |

## D4 exact evidence

The initial pre-R1 measurement was preserved in D-047. Under R1-001, the new release-code anchor is `0.1118193525252465` with absolute tolerance `1e-6`; the old anchor remains in the test as a commented historical reference.

```text
measured_rmse_holdout=0.1118193525252465
new_expected_rmse_holdout=0.1118193525252465
absolute_tolerance=1e-6
measured_m_psi=0.9082706766917292
expected_m_psi=0.9082706766917292
```

The original pre-refactor anchor was `0.111819155629592`; its measured signed delta was `+1.968956545e-7`. The author explicitly classified this as reassociation-scale drift and authorized the scoped re-anchor.

## D5 and D6 evidence

```text
D5: tests/test_determinism.py -> PASS
D6: tests/test_metrics.py -> PASS
D6 measured m_dauroc=0.8
D6 expected m_dauroc=0.80
```

## F7 exact evidence

```text
f1_v2_autopsy/SUMMARY.csv: recorded=ddaab71c417d0be34895459d2a28d89dcbaf3c034a160e6d4a0a9d41c4c20621 current=ddaab71c417d0be34895459d2a28d89dcbaf3c034a160e6d4a0a9d41c4c20621 match=True
lhe_v1/SUMMARY.csv: recorded=098db284e19677a51dedc5f09e4dda02d414d5cead6c069e5bda0c317ca86cdf current=098db284e19677a51dedc5f09e4dda02d414d5cead6c069e5bda0c317ca86cdf match=True
maf_v1/SUMMARY.csv: recorded=a0ac5382d41b902b7452b3c332640bca1b34794f77e903edc150fedef40468eb current=a0ac5382d41b902b7452b3c332640bca1b34794f77e903edc150fedef40468eb match=True
```

## Release certification

All F criteria pass under the binding R1 ruling. The package is certified as **MAF v1.0.0**. The external transmission file `VERIFY_REPORT.md` is a byte-identical copy of this report and is not a second shipped package path.
