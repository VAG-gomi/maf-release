# SPEC-M3-R1 Status — 1.1.1 Local Acceptance

**Stage:** Support-boundary correction on isolated branch `ci-fix`.

**Authorization:** SPEC-M3-R1 retained the exact runtime dependency pins and narrowed supported Python to `>=3.12` after the first GitHub Actions install failure on Python 3.10.

**Local acceptance:** PASS. A fresh Python 3.12 environment installed the package successfully, import returned `1.1.1`, and the complete nine-test suite passed with zero skips or expected failures. D4 anchors and prior-tree spot checks passed unchanged.

**Exact pins:** NumPy 2.5.1, pandas 3.0.5, SciPy 1.18.0, and PyTorch 2.13.0 remain unchanged.

**Remaining R1-003 gate:** Push `ci-fix` to GitHub and require the actual single Python 3.12 Actions job to finish green. Only after that check may the patch be merged to `main` and tag `v1.1.1` be created and pushed. The existing `v1.1.0` tag remains unchanged.

**External status:** An initial ci-fix push occurred with the package nested below the GitHub repository root, so no valid workflow run was created; this is recorded as DEVIATION-059. Main and the existing `v1.1.0` tag remain unchanged. A corrected repository-root ci-fix push is required before the R1-003 CI gate can be evaluated. The corrected package contains 42 total files: 41 manifest-covered files plus the manifest itself, as recorded in DEVIATION-060. GitHub rejected the first merge attempt because ci-fix had no common history with main; DEVIATION-061 records that the branch will be rebuilt with main as its parent before retrying the merge.
