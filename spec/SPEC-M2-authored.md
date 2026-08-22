
```
================================================================================
SPEC-M2: MAF RELEASE 1.0 — PRODUCTION PACKAGING AND VERIFICATION (BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus. Version: 1.0.
Target user: RESEARCHERS (declared). §0 rules apply UNCHANGED. Standing rule
R2-002: every count is an explicit enumeration; prose counts void.
Standing rule R2-003: stream-usage table required wherever randomness exists
(the library inherits SPEC-M1's bound RNG map verbatim; no new randomness
is introduced anywhere in this packaging task).
================================================================================

A. SCOPE AND SOURCE OF TRUTH
  A1. Task: convert the verified SPEC-M1 implementation into an installable,
      documented, tested research package named `maf`, version 1.0.0.
  A2. Source of truth: maf_v1/run_maf.py (behavior) + SPEC-M1 authored chain
      (semantics). The refactor MUST NOT change any bound behavior; where
      refactoring and bindings conflict, THE BINDINGS GOVERN.
  A3. Work happens ONLY in new root maf_release/. Trees maf_v1/, f1_v2/,
      f1_v2_autopsy/, lhe_v1/, and tag F1-v1-baseline remain byte-immutable.
  A4. Copy ALL of {SPEC-M1-authored.md, SPEC-M1-R1..R7-authored.md,
      SPEC-M2-authored.md} into maf_release/spec/ before any execution
      (AUTHOR-ERR-010 lesson).

B. PACKAGE LAYOUT (closed-world enumeration; nothing else ships):
   1.  pyproject.toml            (name=maf, version=1.0.0, deps pinned:
                                 numpy, pandas, scipy, torch; python>=3.10)
   2.  LICENSE                   (MIT)
   3.  README.md                 (contents bound in §E)
   4.  docs/API.md               (every public signature from §C, documented)
   5.  docs/EMPIRICAL_CARD.md    (the thirteen-row T3 table VERBATIM + the
                                 verdict PASS + the scope sentence from §E2)
   6.  docs/EXAMPLE.md           (worked example: fit world 2000, adapt one
                                 holdout env, predict; show real numbers)
   7.  src/maf/__init__.py       (exports MAFModel, generate_world)
   8.  src/maf/model.py          (MAFModel per §C)
   9.  src/maf/worlds.py         (generate_world(seed) implementing SPEC-M1
                                 B-section + R5-001 RNG map EXACTLY, returning
                                 dict with enumerated keys: theta, kappa,
                                 a_env[25], rho_env[25], obs data per env,
                                 trial data per trial env, holdout data)
   10. src/maf/metrics.py        (rmse_holdout, psi_spearman, dauroc —
                                 formulas verbatim from SPEC-M1 F-section)
   11. src/maf/io.py             (config save/load incl. provenance flags)
   12. tests/                    (six files, enumerated in §D)
   13. examples/run_example.py   (runs §E3 example end-to-end)
   14. verification/VERIFY.md    (battery results, filled in)
   15. spec/                     (per A4)

C. PUBLIC API (bound signatures; no other public surface):
   C1. maf.generate_world(seed:int) -> WorldDict
   C2. class MAFModel:
       __init__(self, hidden:int=16, r:int=2, lambda1:float=1e-3,
                weight_decay:float=1e-4, seed:int|None=None)
       fit(self, environments:list[EnvData]) -> FitReport
             # EnvData: dict(x_obs[n,5], tau_obs[n], y_obs[n],
             #              x_int?[m,5], tau_int?[m], y_int?[m])
             # loop semantics = R3-001: ascending envs, one optimizer step
             # per environment, 300 epochs, equal row weights.
       adapt(self, x_obs:numpy, tau_obs:numpy, y_obs:numpy,
             steps:int=200, lr:float=1e-2) -> AdaptReport
             # creates psi_new zero-init; trains psi_new ONLY (R4-003).
       predict_interventional(self, x:numpy, tau:numpy) -> numpy
             # beta channel ONLY; architecturally independent of all psi/U.
       predict_observational(self, x:numpy, tau:numpy, env_id:int) -> numpy
       psi_norms(self) -> dict[int, float]
       artifact_score(self, x:numpy, tau:numpy, env_id:int) -> float
             # mean |phi(x_full,tau)^T (U psi_e)| — the designed D observable.

D. TEST SUITE (six files, exact contents):
   D1. test_generator.py: generate_world(2000) returns all enumerated keys;
       shapes correct (25 envs, 20 train, 10 trial, 5 holdout, 400/100/400
       rows); calling twice yields identical arrays.
   D2. test_do_mask.py (THE core invariant): fit world 2000 normally; then
       overwrite U and every psi_e with large random values; assert
       predict_interventional outputs are BITWISE UNCHANGED.
   D3. test_quarantine_init.py: fresh psi_new is exactly zero => first
       predict_observational on a new env equals beta-only prediction;
       and adaptation moves ONLY that env's predictions.
   D4. test_regression_seed2000.py: full pipeline (generate 2000 -> fit
       V-FULL config -> score) reproduces the stored SPEC-M1 value
       rmse_holdout = 0.111819155629592 within absolute tolerance 1e-9;
       likewise m_psi = 0.9082706766917292 within 1e-9.
       IF EITHER FAILS: DO NOT loosen tolerances, DO NOT patch the test —
       record verbatim deltas in DEVIATIONS.md and HALT for author ruling.
       (Refactors may legitimately change float op-order; that is an author
       decision, never an executor one.)
   D5. test_determinism.py: same-seed double fit produces bitwise-identical
       prediction arrays.
   D6. test_metrics.py: metric functions reproduce, on stored world-2000
       channel data, m_dauroc = 0.80 within 1e-9.

E. DOCUMENTATION BINDINGS:
   E1. README must contain, VERBATIM, this scope statement:
       "Validated in synthetic confound-heavy environments with analytic
        ground truth (30 worlds, pre-registered criteria, independent
        execution). NOT validated on real-world data."
   E2. EMPIRICAL_CARD.md contains the thirteen-row T3 table verbatim
       (g0a_pass_scale 1.0 ... verdict_label PASS) plus one paragraph:
       K1/K2 gaps mean removal or rewiring of the quarantined channel
       degrades holdout interventional accuracy by 161% / 251% relative.
   E3. EXAMPLE.md numbers come from an actual executed example, pasted
       with its config, not invented.

F. ACCEPTANCE CRITERIA (all must hold; computed, not narrated):
   F1. Fresh venv: `pip install .` succeeds; `import maf` succeeds.
   F2. Full pytest run: all six files pass, zero skips, zero xfails.
   F3. Determinism check (D5) passes.
   F4. Regression anchors (D4/D6) pass within bound tolerances.
   F5. Every §B file exists with non-empty content; docs contain §E strings.
   F6. sha256 manifest covers EVERY file under maf_release/ including spec/
       (MANIFEST-GAP-001 lesson; no subtree omitted).
   F7. Hash spot-check: prior trees unchanged (compare 3 recorded hashes
       of your choice from earlier manifests against current files).

G. FAILURE POLICY:
   G1. Packaging/tooling failures (paths, imports, metadata): fix allowed,
       EACH logged as a numbered deviation with the verbatim error.
   G2. Scientific-content failures (D2/D4/D5/D6 mismatches, do-mask leak,
       regression drift): NO fix authorized — record and HALT for author.
   G3. Report-don't-repair applies everywhere else (V-battery lesson).

H. TRANSMISSION TO AUTHOR:
   H1. STATUS.md ping at start and completion (<= 40 lines each).
   H2. VERIFY_REPORT.md verbatim: the §F checklist, each item PASS/FAIL
       with its evidence (test names, measured deltas, hashes).
   H3. DEVIATIONS.md verbatim (numbered from DEVIATION-047 onward,
       continuing the project ledger convention).
   H4. sha256 manifest verbatim.
================================================================================
END SPEC-M2
================================================================================
```
