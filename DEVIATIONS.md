
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
