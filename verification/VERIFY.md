# MAF Release 1.1.1 Verification Report

## Overall status

**Local acceptance PASS; GitHub CI and final publication PENDING — MAF Release 1.1.1 support-boundary patch under SPEC-M3-R1.**

This patch retains every exact runtime dependency pin and narrows the supported Python version to `>=3.12`, the environment in which the package was originally certified. The previous `v1.1.0` tag remains unchanged as the historical hardening marker. No model code, scientific artifact, acceptance anchor, threshold, or dependency pin is changed by this patch.

## R1-003 acceptance checklist

| Criterion | Status | Evidence |
|---|---|---|
| A. Fresh Python 3.12 installation/import | PASS | Fresh `/tmp/maf_spec_m3_r1_venv`; `pip install .` exit 0; import returned `1.1.1` |
| B. Full nine-test suite and D4 anchors | PASS | Nine tests passed; RMSE `0.1118193525252465`, M-PSI `0.9082706766917292`, M-DAUROC `0.8` |
| C. Main push and GitHub Actions | PENDING | Requires push to main and a green actual single Python 3.12 Actions job |
| D. Manifest and prior-tree checks | PASS locally | Three prior-tree spot checks matched; final manifest regeneration remains after final report edits |
| E. v1.1.1 tag | PENDING | Tag may be created and pushed only after actual GitHub CI is green |

## Local acceptance evidence

```text
install_status=0
import_status=0
import_version=1.1.1
pytest_install_status=0
pytest_status=0
.........                                                                [100%]
```

The local run used a fresh Python 3.12 virtual environment and installed the package from the `maf_release/` package root. The exact pinned runtime dependencies remain:

```text
numpy==2.5.1
pandas==3.0.5
scipy==1.18.0
torch==2.13.0
```

## Numerical and determinism evidence

```text
fit_steps=6000
rmse_holdout=0.1118193525252465
m_psi=0.9082706766917292
m_dauroc=0.8
determinism=PASS
```

These values are unchanged from the accepted v1.1.0 hardening evidence and remain within the bound tolerances. The patch changes only support metadata, documentation, version metadata, and CI matrix scope.

## Authorized metadata changes

```text
pyproject.toml: requires-python >=3.12; version 1.1.1
.github/workflows/tests.yml: python-version ["3.12"]
README.md: Python 3.12-or-newer installation requirement
CHANGELOG.md: new 1.1.1 entry
CITATION.cff: version 1.1.1
src/maf/__init__.py: __version__ = "1.1.1"
```

## CI requirement

The actual GitHub Actions job is the decisive R1-003 acceptance criterion for the defect that triggered this patch. The package must be pushed to `main`, and the single Python 3.12 `install-and-test` job must finish green. No `v1.1.1` tag may be created before that checkmark.

## Provenance and deviations

SPEC-M3-R1 is preserved verbatim at `spec/SPEC-M3-R1-authored.md`. DEVIATION-056 records the original Python 3.10 wheel-availability failure; DEVIATION-057 records the initial local wrong-directory invocation. Both are closed under the recorded resolutions. D-054 and D-055 remain acknowledged as local publish-preparation tooling errors.

The previous `v1.1.0` tag is not moved. Main remains at its already pushed v1.1.0 state until the actual GitHub CI job passes. An initial ci-fix push occurred with the package nested below the GitHub repository root, so no valid R1-003 workflow run was created; this is recorded as DEVIATION-059. Main, the existing v1.1.0 tag, and the package’s scientific contents remain unchanged. A corrected repository-root ci-fix push is still pending. DEVIATION-060 records that the package now contains 42 total files: 41 manifest-covered files plus the manifest itself. DEVIATION-061 records that GitHub’s existing ci-fix branch has no common history with main; the branch will be rebuilt with main as its parent before retrying the merge.

## Final certification

Local R1-003 criteria A, B, and D pass. Criteria C and E remain pending until the corrected branch is pushed, the real GitHub Actions job is green, and tag `v1.1.1` is created and pushed afterward.
