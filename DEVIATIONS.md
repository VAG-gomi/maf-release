
## DEVIATION-047 — D4 world-2000 regression anchor mismatch; scientific halt

**Stage:** SPEC-M2 D4 regression-anchor execution.

The newly refactored package was executed on world 2000 using `examples/run_example.py`. The measured V-FULL holdout RMSE was `0.1118193525252465`; the SPEC-M2 stored anchor is `0.111819155629592`. The signed delta (measured minus anchor) is `+0.0000001968956545` (approximately `+1.968956545e-7`), which exceeds the bound absolute tolerance `1e-9`. The same execution measured `m_psi=0.9082706766917292`, matching its anchor exactly within the bound tolerance.

Verbatim execution output:

```text
rmse_holdout=0.1118193525252465
expected_rmse_holdout=0.111819155629592
m_psi=0.9082706766917292
expected_m_psi=0.9082706766917292
```

The package refactor may have changed floating-point operation order or another implementation detail. No tolerance was loosened, no test was patched, and no scientific behavior was silently changed. Under SPEC-M2 G2, this scientific-content regression requires HALT and author ruling. D5/D6 and the remaining acceptance execution are not treated as passed; no MAF v1.0.0 release claim is issued.

## DEVIATION-048 — Verification report path is inconsistent between §B and §H2

**Stage:** SPEC-M2 package layout audit after the D4 scientific halt.

Section B item 14 enumerates `verification/VERIFY.md` as the package file, while H2 requires transmission of `VERIFY_REPORT.md` without specifying the `verification/` directory. Section B also declares the package layout closed-world and says nothing else ships. Creating only one path would satisfy one binding and violate the other; creating both would violate the closed-world enumeration unless H2 is read as a transmission artifact outside the shipped package. No path interpretation is silently selected. The package remains HALTED pending author ruling; this does not alter any scientific result.

## DEVIATION-047 closure — resolved by SPEC-M2-R1-001

SPEC-M2-R1 retires the pre-refactor RMSE anchor for release acceptance, preserves it as the historical reference, and binds `rmse_holdout=0.1118193525252465` with absolute tolerance `1e-6`. The M-PSI anchor remains `0.9082706766917292` with tolerance `1e-9`. The release regression test is updated exactly as authorized; the old expected RMSE remains as a commented historical reference. No scientific criterion beyond the author-ratified acceptance anchor is changed by the executor.

## DEVIATION-048 closure — resolved by SPEC-M2-R1-002

The shipped package uses only `verification/VERIFY.md`, as required by the §B closed-world layout. `VERIFY_REPORT.md` is emitted outside `maf_release/` as the H2 transmission copy of `verification/VERIFY.md`. No duplicate verification file is shipped.

## DEVIATION-049 — D4 collection import failure before package installation

**Stage:** SPEC-M2-R1 resumption, D4 test invocation.

The first direct D4 invocation was:

```text
cd /home/ubuntu/cfhm_f1/maf_release
python3 -m pytest -q tests/test_regression_seed2000.py
```

It failed during test collection because the source-layout package had not yet been installed:

```text
==================================== ERRORS ====================================
______________ ERROR collecting tests/test_regression_seed2000.py ______________
ImportError while importing test module '/home/ubuntu/cfhm_f1/maf_release/tests/test_regression_seed2000.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
...
tests/test_regression_seed2000.py:1: in <module>
    from maf import MAFModel, generate_world
E   ModuleNotFoundError: No module named 'maf'
=========================== short test summary info ============================
ERROR tests/test_regression_seed2000.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
D4_exit=2
```

This is a packaging/invocation failure, not a scientific-content result. The authorized mechanical continuation is to run D4–D6 with `PYTHONPATH=src` until the required F1 installation is executed; no test or model code is changed. D-049 is resolved by that invocation-path correction.

## DEVIATION-050 — F2 fresh-environment test runner absent

**Stage:** SPEC-M2-R1 resumption, F2 full pytest acceptance.

F1 successfully installed `maf` into `/tmp/maf_spec_m2_venv` and `import maf` passed. The first F2 invocation was:

```text
cd /home/ubuntu/cfhm_f1/maf_release
/tmp/maf_spec_m2_venv/bin/python -m pytest -ra
```

The exact result was:

```text
/tmp/maf_spec_m2_venv/bin/python: No module named pytest
F2_exit=1
```

The closed SPEC-M2 dependency list does not include pytest, while F2 requires pytest execution. This is a tooling prerequisite, not a scientific result. Installing the test runner into the temporary verification environment is authorized as a mechanical continuation; package runtime dependencies are unchanged.

## DEVIATION-051 — Initial F7 spot-check executed before F6 manifest emission

**Stage:** SPEC-M2-R1 acceptance sequencing.

The executor initially ran the F7 three-file prior-tree spot-check before emitting the new `maf_release/` manifest required by F6. The spot-check passed for `f1_v2_autopsy/SUMMARY.csv`, `lhe_v1/SUMMARY.csv`, and `maf_v1/SUMMARY.csv`. This was an execution-order mistake; no scientific artifact was changed. F6 is now executed next, followed by a fresh F7 spot-check so the final acceptance sequence is corrected and both results are preserved in the final verification report.

## DEVIATION-052 — F6 manifest self-reference is non-recursive by necessity

**Stage:** SPEC-M2 F6 manifest emission.

The literal phrase “manifest covers EVERY file under maf_release/” includes `sha256 manifest` itself, but a manifest cannot contain a stable hash of its own changing contents. Following the established project manifest convention, the emitted manifest lists every other file under `maf_release/`, including the complete `spec/` subtree, and excludes only `ARTIFACT_MANIFEST.sha256` itself. The exclusion and the exact covered-file count are disclosed in `verification/VERIFY.md`; no subtree is omitted.

## DEVIATION-049 closure — resolved by source-layout invocation

D4 was rerun with `PYTHONPATH=src`, passed under the R1 anchor, and the package source was not modified to hide the initial import-path issue.

## DEVIATION-050 closure — resolved by temporary test-runner installation

F1 installed `maf` successfully. Pytest was then installed only into `/tmp/maf_spec_m2_venv` for F2, and the full suite passed: `6 passed in 99.26s (0:01:39)`. Pytest was not added to the package runtime dependency list.

## DEVIATION-051 closure — corrected acceptance ordering

After the initial out-of-order observation, F6 was executed and passed, followed by the fresh F7 spot-check. The final acceptance record reports the corrected F6-then-F7 sequence.

## DEVIATION-052 resolution status — manifest self-entry

The release manifest covers every other file under `maf_release/`, including all specification and evidence subtrees, and excludes only its own self-entry because a file cannot contain a stable hash of its own changing contents. This follows the existing project manifest convention. The exact covered-file count and self-exclusion are disclosed in `verification/VERIFY.md`.


## DEVIATION-053 — SPEC-M3 start status ping created after registration edits

**Stage:** SPEC-M3 hardening-cycle initialization.

SPEC-M3 F requires a start status ping. The executor registered AC-001 and SPEC-M3 and applied the bound hardening edits before creating the start status file. This is an execution-sequencing deviation: the required start ping was not the first hardening-work artifact. No scientific result was read or used to choose a code change, and no main-branch or GitHub artifact was modified. The start status will now be created before the formal acceptance battery; the omission is preserved here rather than silently backfilled.


## DEVIATION-053 closure — resolved by explicit disclosure and completion ping

The required start status is now present at `STATUS.md`, and the sequencing issue remains disclosed in the final verification report. The hardening acceptance battery was executed after that status checkpoint. No scientific code, threshold, anchor, or result was changed to resolve D-053.


## DEVIATION-054 — Initial GitHub publish archive source-path error

**Stage:** SPEC-M3 §G merge/tag/push preparation.

The first publish-preparation command attempted to archive the package with:

```text
git archive --format=tar /home/ubuntu/cfhm_f1 main:maf_release | tar -x
```

Git reported:

```text
fatal: not a valid object name: /home/ubuntu/cfhm_f1
tar: This does not look like a tar archive
tar: Exiting with failure status due to previous errors
```

No GitHub mutation occurred. The remote repository remained unchanged. This was a local command-construction error, corrected by invoking `git -C /home/ubuntu/cfhm_f1 archive --format=tar main:maf_release`.

## DEVIATION-055 — Publish staging count checked before staging

**Stage:** SPEC-M3 §G merge/tag/push preparation.

The corrected archive extraction succeeded, but the second preparation command measured `git ls-files` before running `git add -A`. It therefore reported `package_file_count=0` and stopped at the bound expected count check of 41. No commit, tag, or GitHub push occurred. The remote repository remained unchanged. This was a local staging-order tooling error, not a package or scientific result; the next attempt will count filesystem files before staging and then verify the committed tree after staging.


## DEVIATION-056 — Runtime dependency pins unavailable for bound Python 3.10 CI

**Stage:** Post-push SPEC-M3 CI audit, before any correction.

The GitHub Actions `install-and-test` job failed during `pip install .` for Python 3.10. The screenshot showed the first failure at the pinned NumPy requirement:

```text
ERROR: No matching distribution found for numpy==2.5.1
Error: Process completed with exit code 1.
```

A workflow-equivalent package-index audit for the bound Python 3.10 target found that all four exact runtime pins lack compatible Python 3.10 distributions, although the same versions are available for Python 3.12:

```text
numpy==2.5.1  -> unavailable for Python 3.10; numpy==2.2.6 available
pandas==3.0.5 -> unavailable for Python 3.10; pandas==2.3.2 available
scipy==1.18.0 -> unavailable for Python 3.10; scipy==1.15.3 available
torch==2.13.0 -> Python 3.10 wheel available in the index audit
```

The exact compatible replacement set for the first three packages is not authored by SPEC-M3, and changing pandas or SciPy versions could affect numerical behavior. No dependency pin has been changed. The issue is recorded on isolated branch `ci-fix`, and author/relay selection is required before applying any replacement version set.


## DEVIATION-054 closure — acknowledged by SPEC-M3-R1-004

The invalid archive source-path command was a local tooling error, produced no repository or GitHub mutation, and was corrected before the successful publish. Closed as acknowledged by the author ruling.

## DEVIATION-055 closure — acknowledged by SPEC-M3-R1-004

The pre-staging file-count check was a local tooling-order error, produced no repository or GitHub mutation, and was corrected before the successful publish. Closed as acknowledged by the author ruling.

## DEVIATION-056 closure — resolved by SPEC-M3-R1-001

The author retained the exact reproducibility pins and narrowed the supported Python version to `>=3.12`, because the 3.10 wheel-availability claim was untested and false for the pinned NumPy, pandas, and SciPy versions. The correction is authorized for branch `ci-fix`; no runtime dependency pin is changed.


## DEVIATION-057 — Local R1 installation invoked from outer repository root

**Stage:** SPEC-M3-R1 acceptance A, fresh-install check.

The first local acceptance command created the fresh virtual environment but invoked `pip install .` while the shell was in `/home/ubuntu/cfhm_f1` instead of `/home/ubuntu/cfhm_f1/maf_release`. The exact result was:

```text
ERROR: Directory '.' is not installable. Neither 'setup.py' nor 'pyproject.toml' found.
install_status=1
```

No package file, model code, scientific artifact, GitHub repository, or main branch was changed by this failed invocation. The prior-tree spot checks in the same command passed. This is a local command-directory error; the acceptance will be rerun from the package root as authorized.


## DEVIATION-057 closure — resolved by correct package-root invocation

The fresh Python 3.12 installation was rerun from `/home/ubuntu/cfhm_f1/maf_release`. Installation exited 0, import returned `1.1.1`, and the full nine-test suite passed with zero skips or expected failures. No dependency pin, model code, scientific artifact, or acceptance anchor was changed.


## DEVIATION-058 — Outer research repository has no configured origin

**Stage:** SPEC-M3-R1 R1-003 C, confirmed ci-fix push.

The confirmed push command was first attempted from the outer research repository with:

```text
git push origin ci-fix
```

The exact result was:

```text
fatal: 'origin' does not appear to be a git repository
fatal: Could not read from remote repository.
Please make sure you have the correct access rights
and the repository exists.
```

No GitHub mutation occurred. The outer repository intentionally has no configured `origin`; the next attempt will use the explicit approved URL `https://github.com/VAG-gomi/maf-release.git`. This is a local remote-configuration error, not a package or CI result.


## DEVIATION-059 — ci-fix first push placed workflow below repository root

**Stage:** SPEC-M3-R1 R1-003 C, actual GitHub Actions verification.

The confirmed `ci-fix` push was performed from the outer research repository. As a result, GitHub received the release package at `maf_release/` with the workflow at `maf_release/.github/workflows/tests.yml`, rather than with the package contents and workflow at the GitHub repository root. GitHub Actions registered the workflow on the repository but created no run for ci-fix commit `a07b750ddfc0b7f75c8f106f816fbd95dc1b590f`; the only recent runs remained the earlier v1.1.0 main/tag failures.

No `main` branch change or tag change occurred during this failed ci-fix verification. This is a repository-layout publishing error, not a package or scientific result. The correction is to rebuild ci-fix from the package-root tree and update that branch before evaluating the actual CI check.


## DEVIATION-060 — Corrected package total is 42 files including manifest

**Stage:** SPEC-M3-R1 R1-003 C, corrected repository-root ci-fix staging.

The corrected package-root extraction succeeded, but the preparation command stopped at a stale expected total of 41:

```text
filesystem_count=42
```

The current package contains 41 manifest-covered files plus `ARTIFACT_MANIFEST.sha256` itself, for 42 total files. The earlier count of 41 referred to the non-manifest entries before `SPEC-M3-R1-authored.md` was registered. No commit or GitHub mutation occurred in this attempt. The next attempt will require 41 manifest entries and 42 total files, consistent with the manifest’s non-recursive self-exclusion convention.


## DEVIATION-061 — ci-fix branch has no common Git history with GitHub main

**Stage:** SPEC-M3-R1 R1-003 C, merge after green ci-fix CI.

The authorized merge attempt created no pull request because GitHub returned:

```text
pull request create failed: GraphQL: The ci-fix branch has no history in common with main (createPullRequest)
```

The outer research repository’s `ci-fix` history and the GitHub package repository’s `main` history are unrelated, even though the ci-fix tree content was verified byte-for-byte. No GitHub main, tag, or release changed. The next correction will preserve the existing package-root ci-fix commit as a parent and create a common-history mergeable branch before retrying the authorized main merge.


## DEVIATION-099 — Autonomous MAF-A1 evidence banking

**Stage:** Ox-alpha-authorized autonomous campaign evidence banking.

The bounded MAF-A1 environment-normalization investigation was copied to `research/causal-benchmarks/maf-a1-envnorm/`. The bank contains the author pre-registration, complete MAF-A1 result JSON, and the campaign-report Section 2 as `REPORT.md`. This is an evidence-only addition; no package-root source code, historical RW3 evidence, existing tag, or GitHub Release page was changed. The banking commit hash is reported in the executor handoff.

**Status:** CLOSED — authorized banking record; historical and source artifacts preserved.
