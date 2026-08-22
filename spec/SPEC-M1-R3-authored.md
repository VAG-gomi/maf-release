================================================================================
SPEC-M1-R3: AUTHOR RESOLUTIONS TO DEVIATIONS 020-024 (BINDING)
================================================================================

AUTHOR-ERR-013: Five specification gaps confirmed (D-020..D-024). Root cause
class: deferred-to-implementation phrasing. Resolved individually below;
superseded text listed explicitly. No results exist yet; all pre-registration
thresholds remain as originally published except where K4 is re-derived
(R3-004) — re-derived BEFORE any execution, which is the only legitimate
moment for such a change.

R3-001 (D-020) — FULL-MODEL TRAINING LOOP, EXACT DEFINITION:
  One optimizer step per environment, environments processed in ASCENDING
  order e = 1..20; that ordered pass = ONE epoch; 300 epochs => exactly
  6000 optimizer steps per fit.
  Batch content for environment e: ALL of that environment's rows —
    train envs: 400 observational rows;
    trial envs: 400 observational + 100 interventional rows (500 total).
  Batch loss = MEAN over all rows in the batch of the row-appropriate
    branch NLL (observational rows -> mu_obs branch; interventional rows
    -> mu_int branch) + C5 penalties. Rows are equally weighted; no
    interventional upweighting anywhere.
  Each variant fit re-seeds torch.manual_seed(world_int + 7000)
    immediately before model construction (deterministic per world per
    variant; different architectures consume the stream differently,
    which is expected and recorded).

R3-002 (D-021) — V-ORAC, COMPLETE DEFINITION (supersedes the D-entry and
  the K4 wording in G2):
  Wiring: IDENTICAL to the G0b probe (R2-001) — fixed non-trainable map
    g9(x,tau) = [z(x); tau]; trainable set exactly {U_G in R^{9x2},
    psi_1..psi_20}; init N(0,0.01)/exact-zero; Adam lr 1e-3; 2000 steps;
    trained on the observational rows of environments {1..20} ONLY
    (trial interventional rows are unused by V-ORAC; recorded as such).
  Branches:
    observational: mu_obs = theta.z(x) + kappa*tau + g9^T(U_G psi_e);
    interventional: mu_int = theta.z(x) + kappa*tau   (analytic truth;
      zero learned content — DECLARED consequence: V-ORAC's M-RMSE equals
      the noise floor by construction and is DIAGNOSTIC-ONLY, excluded
      from P1 comparisons and from K1/K2 arithmetic).
  Scored outputs: M-PSI_VO and M-DAUROC_VO from its channel (psi norms /
    D_e computed exactly as F2/F3 define, using U_G psi_e).
  K4 RE-DERIVED (replaces the old K4 verbatim):
    K4 fires iff median-across-worlds M-PSI(V-ORAC) < 0.3.
    Rationale: with the mechanism analytically perfect, the only thing
    left to test is whether the quarantine channel itself identifies the
    planted confounding across all 30 worlds — the direct generalization
    of the G0b gate and the precise analogue of CFHM's fatal pattern.
    Old K4 ("V-ORAC beats V-A0 on RMSE") was degenerate under analytic
    branches and is retired.

R3-003 (D-022) — B-MIXED, EXACT ESTIMATOR (single path, no library
  dependence; a shrinkage estimator in the random-effects family):
  Design rows: [z(x); tau] (width 9) for ALL train-env rows (envs 1..20,
    observational and, for trial envs, interventional rows included
    plainly as (x, tau, y) — no flag column exists or is used).
  Step 1: pooled OLS -> global w_g in R^9 (numpy lstsq, rcond=None).
  Step 2: per environment e in 1..20: OLS on that environment's rows for
    deviation d_e in R^2 on coordinates [constant, tau] (i.e., regress
    residual y - X w_g on [1, tau] restricted to those two columns),
    with ridge toward zero: solve (X_e'^T X_e' + I) d_e = X_e'^T r_e.
  Step 3: shrink d~_e = (n_e / (n_e + 100)) * d_e, n_e = row count.
  Prediction for seen env e: X w_g + [1, tau].d~_e.
  Prediction for UNSEEN env: X w_g (population means — declared).
  Recorded in the project record as a shrinkage approximation to random
  effects, chosen for determinism and zero dependencies; the name B-MIXED
  is retained solely for T2-schema continuity.

R3-004 (D-023) — G0a SCALE PROPAGATION:
  The ladder outcome on world 2000 selects ONE GLOBAL generator constant
  b_scale in {1, 2, 4} applied IDENTICALLY to all worlds 2000..2029 and
  to every downstream stage. No per-world ladders; world 2000 is not
  special after the gate. Chosen scale transmitted as T3 row 1.

R3-005 (D-024) — G0b OBJECTIVE, EXACT FORMULA:
  loss_G0b = MSE(bias_hat, target)
             + lambda_candidate * SUM_{e=1..20} ||psi_e||_2
             + 1e-4 * ||U_G||_F^2
  i.e., G0b carries the SAME penalty structure as C5 (norm-type-matched),
  so lambda1 is selected under the regularization it will govern.
  Lambda candidates tested in the bound order {1e-2, 1e-3, 1e-4};
  freeze rule unchanged.

R3-006 — T3 SUMMARY TABLE SUPERSEDED IN FULL. New closed-world enumeration,
  THIRTEEN rows, exact names:
    1. g0a_pass_scale            2. g0b_lambda1_chosen
    3. g0b_best_correlation      4. p1_vfull_rmse_median
    5. p1_best_baseline_name     6. p1_best_baseline_rmse_median
    7. p1_relative_reduction     8. p2_mpsi_median
    9. p3_mdauroc_median        10. k1_gap_percent
   11. k2_gap_percent           12. k4_vorac_mpsi_median
   13. verdict_label (PASS / KILL-Kn / INCONCLUSIVE — computed)
  T2 schema unchanged; V-ORAC rows carry rmse (diagnostic) plus
  m_psi/m_dauroc; V-A0/V-SOVT/B-* rows leave channel columns blank.

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as maf_v1/spec/SPEC-M1-R3-authored.md; provenance commit.
  2. Close DEVIATION-020..024 as resolved-by-R3-001..006 respectively.
  3. Implementation UNBLOCKED. Run G0a then G0b; transmit gate outcomes
     before any full-run artifacts (E3).
================================================================================
END SPEC-M1-R3
================================================================================
