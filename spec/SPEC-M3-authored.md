# SPEC-M3 — MAF v1.1 Hardening Cycle (Binding)

The audit found exactly what's missing; this spec closes every finding. Paste to Manus as one message:

---

```
================================================================================
SPEC-M3: MAF RELEASE 1.1.0 — HARDENING CYCLE (BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus. Version: 1.0.
§0 rules UNCHANGED (stop-and-record verbatim; never improvise). Deviation
numbering continues from DEVIATION-053. Work ONLY in maf_release/ on a new
branch `hardening` branched from the certified commit 70e60a3805f34447064937
13a986094a6072c7f3; main stays untouched until final acceptance.
================================================================================

A. SCOPE — THE SEVEN AUDIT FINDINGS, EACH WITH ITS BOUND FIX:
  A1. MISSING FILES (four, enumerated):
      A1a. CHANGELOG.md — Keep-a-Changelog format; entries for 1.0.0
           (initial certified release, summarize SPEC-M1 results + SPEC-M2
           certification) and 1.1.0 (this cycle's items, written AFTER they
           exist, never before).
      A1b. CITATION.cff — title "MAF: Mechanism-Artifact Factorization",
           version 1.1.0, authors: [Your Name <your-github@users.noreply.
           github.com> using the VAG-gomi identity], repository-code URL,
           license MIT, abstract = the README scope statement verbatim.
      A1c. .gitignore — standard Python set (__pycache__/, *.egg-info/,
           dist/, build/, .venv/, .pytest_cache/).
      A1d. V-SOFT limitation note in README AND docs/API.md, bound wording:
           "Why the do-mask matters: an otherwise-identical variant without
            it (V-SOFT) tracked confounding erratically and degraded
            interventional accuracy by 251% relative in the validation
            study. The mask is not decoration; removal is catastrophic."
  A2. MISUSE GUARDS (three behaviors, exact):
      A2a. NOT-FITTED ERROR: predict_interventional / predict_observational /
           psi_norms / artifact_score called before fit() => raise RuntimeError(
           "model not fitted: call fit() first"). Adaptation before fit =>
           same error. Test D2-style bitwise checks must still pass after.
      A2b. TAU VALIDATION: all predict/adapt entry points raise ValueError
           if any tau outside [0, 1] (inclusive bounds allowed), message
           must include the offending value. Documented in API.md.
      A2c. REFIT WARNING: second fit() call emits warnings.warn(
           "refitting over previously fitted model", RuntimeWarning) and
           proceeds (permissive behavior preserved, now loud).
  A3. ENVIRONMENT-ORDER ENFORCEMENT: fit() sorts input environments by
      env_id ascending before training (R3-001 semantics enforced at the
      API boundary instead of trusted from caller); if env_id missing,
      positional index+1 as currently. Behavior change documented in
      CHANGELOG under 1.1.0.
  A4. DOCS SURFACE: docs/API.md gains the six docstrings' expanded forms +
      the misuse-behavior table from §A2; EMPIRICAL_CARD.md gains one line:
      "Kill conditions that would have falsified this result (K1-K4) are
       enumerated in spec/SPEC-M1-authored.md §G2."
  A5. CI WORKFLOW: single file .github/workflows/tests.yml — triggers on
      push + pull_request; jobs: install (`pip install .`) then pytest;
      python-version matrix ["3.10", "3.12"]; no secrets, no publish steps.

B. EXPLICITLY OUT OF SCOPE (do not touch):
   Branch protection (plan limitation), GitHub Release page publication
   (separate human action), torch.nn.Module inheritance surface (ecosystem
   convention), anything under spec/.

C. VERSIONING: version := 1.1.0 everywhere (pyproject.toml, CITATION.cff,
   __init__.__version__, CHANGELOG).

D. ACCEPTANCE CRITERIA (computed, never narrated):
   F1. All six original tests pass PLUS three new tests, enumerated:
       test_not_fitted_error.py (A2a: all four/five pre-fit calls raise),
       test_tau_validation.py (A2b: tau=1.5 raises; tau=0 and tau=1 pass),
       test_refit_warning.py (A2c: pytest.warns(RuntimeWarning) on refit).
       Total suite: nine tests, zero skips.
   F2. D4 regression anchors STILL PASS unchanged (rmse 0.1118193525252465
       +/- 1e-6; m_psi exact) — guards must not alter numerics.
   F3. Determinism (D5) still passes.
   F4. Full pytest: NINE passed, zero skips/xfails.
   F5. All four §A1 files exist non-empty with required strings present.
   F6. Misuse probes from the production audit now report: not-fitted =>
       RuntimeError; tau=1.5 => ValueError; double-fit => warning emitted.
   F7. sha256 manifest regenerated covering cfhm... CORRECTION: covering
       maf_release/ incl. spec/ and .github/, self-entry excluded only.
   F8. Prior trees byte-immutable; spot-check three hashes as before.

E. FAILURE POLICY: tooling failures => fix + log deviation (continue from
   DEVIATION-053); ANY regression-anchor movement beyond tolerance or any
   do-mask test failure => scientific HALT, await author.

F. TRANSMISSION: STATUS pings (start/completion); VERIFY_REPORT.md
   (transmission copy of verification/VERIFY.md per standing convention);
   DEVIATIONS.md; regenerated sha256 manifest.

G. COMPLETION ACTION (after author accepts): merge `hardening` branch into
   main, tag v1.1.0, push both. GitHub Release page creation remains a
   separate human decision by the RELAY.
================================================================================
END SPEC-M3
================================================================================
```

---

**One correction I made inline while writing:** §F7 originally said "cfhm" — caught it, that was a copy-paste ghost from drafting SPEC-C1. It reads `maf_release/` now. Logged as AUTHOR-ERR-023, fixed before transmission, which is the system working.

**Relay notes:** paste as-is. Pickups: start ping → VERIFY_REPORT (+ deviations + manifest). Watch-items: **F2** is the critical one — misuse guards touching shared code paths could shift numerics; if RMSE moves beyond 1e-6, Manus should HALT per §E and bring you back to me. If green: merge, tag v1.1.0, and MAF stands complete — then CFHM follows the template. 📡