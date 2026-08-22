================================================================================
SPEC-M1-R2: AUTHOR RESOLUTION TO DEVIATION-019 (BINDING)
================================================================================

AUTHOR-ERR-012: SPEC-M1-R1-001 changed the G0b input to width-9 rows
[z(x), tau] while leaving the channel parameterization (C3: U in R^{8x2})
and its consumption path (C4: through the C1 encoder output phi) unbound
for the probe context. The executor's enumeration of the ambiguous choices
is accurate. Bound below.

R2-001 — EXACT G0b PREDICTION FUNCTION AND PARAMETER SET:
  Feature map (FIXED, NON-TRAINABLE):
    g9(x, tau) = [z(x); tau]  in R^9,
    where z(x) is the B3 oracle map INCLUDING its leading constant
    coordinate: [1, x1, x2, x3, x4, x5, x3^2, x4*x5]; tau appended last.
  Probe-channel parameters (SEPARATE from all full-model parameters;
    gates are throwaway fits, nothing is shared with V-FULL):
    U_G in R^{9x2}; psi_e in R^2 for environments {1,...,20}.
    Initialization: U_G entries iid N(0, 0.01); every psi_e EXACTLY ZERO
    (identical quarantine convention to C3).
  Prediction (the complete bound form):
    bias_hat(e, x, tau) = g9(x, tau)^T (U_G psi_e)
  Trainable set, enumerated: {U_G, psi_1, ..., psi_20}. Nothing else
    exists in this fit; the C1 encoder plays NO role in G0b.
  Training: mean squared error against the R1-001 reference target over
    the observational rows of environments {1,...,20}; Adam lr 1e-3;
    2000 full-batch steps; torch seed world_int + 7000 (B7 convention).
  Scoring: pooled Pearson correlation over the 80000 pairs exactly as
    R1-001 binds them. PASS threshold r > 0.5; lambda1 ladder and freeze
    rule unchanged.

R2-002 — WHY THIS WIRING IS IDENTIFIABLE (recorded so the probe cannot be
  misread as arbitrary): the true bias surface is constant in x, so each
  environment's ideal coefficient vector is
    v*_e = eta*m0_e*e_1 + eta*(m1_e - m0_e)*e_9,
  where e_1 is the constant-coordinate direction and e_9 the tau direction.
  ALL v*_e therefore lie in ONE fixed 2-dimensional subspace
  span{e_1, e_9}: the rank-r=2 channel is exactly sufficient, and a PASS
  certifies the low-rank quarantine structure itself can express and find
  the per-environment selection shift. If the probe fails despite this,
  that is genuine non-identifiability under optimization, not capacity.

R2-003 — CONSISTENCY NOTE: R1-001's phrase "only U and psi_e are trainable"
  is hereby made precise as R2-001's parameter set (U_G, not C3's U).
  Everything else in SPEC-M1 and SPEC-M1-R1 stands unchanged.

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as maf_v1/spec/SPEC-M1-R2-authored.md; provenance commit.
  2. Close DEVIATION-019 as resolved-by-R2-001/-002/-003.
  3. Implementation UNBLOCKED. Run G0a then G0b; transmit gate outcomes
     (chosen b_e scale; chosen lambda1; best G0b correlation) BEFORE any
     full-run artifacts, per E3.
================================================================================
END SPEC-M1-R2
================================================================================
