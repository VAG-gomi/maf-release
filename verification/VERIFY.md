# MAF Release 1.1.0 Verification Report

## Overall status

**Acceptance battery: PASS — MAF Release 1.1.0 hardening completed under SPEC-M3 and AC-001.**

The hardening work was performed only on branch `hardening`, branched from certified commit `70e60a3805f3444706493713a986094a6072c7f3`. Main remained untouched during acceptance. The authored AC-001 and SPEC-M3 documents are preserved verbatim under `spec/`.

The hardening changes are limited to the seven audit findings bound by SPEC-M3: the four missing release files and documentation, not-fitted guards, treatment validation, refit warning, environment-order enforcement, version `1.1.0`, and the two-version test workflow. Branch protection, GitHub Release publication, and `torch.nn.Module` inheritance remain explicitly out of scope.

## F acceptance checklist

| Criterion | Status | Evidence |
|---|---|---|
| F1. Fresh install/import | PASS | Fresh `/tmp/maf_spec_m3_venv`; `pip install .` exit 0; `import maf` returned `1.1.0` from the installed environment |
| F2. D4 regression anchors | PASS | RMSE `0.1118193525252465` within `1e-6`; M-PSI `0.9082706766917292` exact within `1e-9`; M-DAUROC `0.8` |
| F3. D5 determinism | PASS | Bitwise-identical interventional prediction arrays under repeated world/model generation |
| F4. Full pytest | PASS | Nine tests passed; zero skips and zero xfails |
| F5. Required files/content | PASS | `CHANGELOG.md`, `CITATION.cff`, `.gitignore`, V-SOFT note, API misuse table, empirical-card K1–K4 sentence, and CI workflow present and non-empty |
| F6. Misuse probes | PASS | Pre-fit calls raise the required RuntimeError; `tau=1.5` raises ValueError naming the value; second fit emits the required RuntimeWarning |
| F7. SHA-256 manifest | PASS | Manifest regenerated over all non-manifest files under `maf_release/`, including `spec/` and `.github/`; only the manifest self-entry is excluded as non-recursive |
| F8. Prior-tree immutability | PASS | Three recorded prior-tree spot checks match exactly; main and earlier experiment trees remain unchanged |

## F2 exact evidence

```text
package_version= 1.1.0
fit_steps= 6000
rmse_holdout= 0.1118193525252465
m_psi= 0.9082706766917292
m_dauroc= 0.8
```

The release-code RMSE equals the AC-001/SPEC-M3 re-based anchor and remains within the bound `1e-6` tolerance. The M-PSI value remains exactly unchanged at the displayed precision. The D4 anchor did not move after adding the guards.

## F3 exact evidence

```text
determinism= PASS
```

The repeated fits produced bitwise-identical interventional prediction arrays, and the original D5 test passed in the nine-test suite.

## F4 exact evidence

```text
.........                                                                [100%]
9 passed
```

The original six tests and the three new SPEC-M3 tests all passed with no skips or expected failures.

## F5 exact evidence

The following required paths are present and non-empty:

```text
CHANGELOG.md
CITATION.cff
.gitignore
.github/workflows/tests.yml
docs/API.md
docs/EMPIRICAL_CARD.md
tests/test_not_fitted_error.py
tests/test_tau_validation.py
tests/test_refit_warning.py
```

The exact bound V-SOFT wording is present in both `README.md` and `docs/API.md`. The empirical card contains the required K1–K4 sentence. `pyproject.toml`, `src/maf/__init__.py`, and `CITATION.cff` all carry version `1.1.0`.

## F6 misuse evidence

```text
pre_fit_predict_interventional=RuntimeError: model not fitted: call fit() first
pre_fit_predict_observational=RuntimeError: model not fitted: call fit() first
pre_fit_psi_norms=RuntimeError: model not fitted: call fit() first
pre_fit_artifact_score=RuntimeError: model not fitted: call fit() first
pre_fit_adapt=RuntimeError: model not fitted: call fit() first
tau_1.5_predict_interventional=ValueError: tau value 1.5 outside [0, 1]
tau_1.5_predict_observational=ValueError: tau value 1.5 outside [0, 1]
tau_1.5_adapt=ValueError: tau value 1.5 outside [0, 1]
double_fit=RuntimeWarning: refitting over previously fitted model
tau_bounds=0_and_1 accepted
```

Boundary values `tau=0` and `tau=1` remain accepted. The permissive second-fit behavior is preserved, now made explicit by the required warning.

## F7 manifest evidence

The final manifest is `ARTIFACT_MANIFEST.sha256`. It covers every other file under `maf_release/`, including all authored specifications, the `.github/` workflow, source, tests, documentation, verification, status, and deviation artifacts. The only excluded path is the manifest itself because a file cannot contain a stable hash of its own changing contents.

## F8 prior-tree evidence

The three recorded prior-manifest spot checks remain unchanged:

```text
f1_v2_autopsy/SUMMARY.csv: match=True
lhe_v1/SUMMARY.csv: match=True
maf_v1/SUMMARY.csv: match=True
```

The hardening branch is the only branch changed by this cycle. Main remains at its certified v1.0.0 state until the separate merge/tag/push decision.

## Sequencing disclosure

DEVIATION-053 records that the required start status file was created after registration and bound edits rather than before the first hardening edit. This was an execution-order issue only; no scientific result was read to choose a change, and no acceptance threshold was altered.

## Certification

All SPEC-M3 F1–F8 acceptance criteria pass. The hardening branch is eligible for author/relay review as **MAF Release 1.1.0**. Per SPEC-M3 §G, merging `hardening` into `main`, creating tag `v1.1.0`, and pushing to GitHub require separate relay confirmation. GitHub Release page publication remains a separate human decision.
