================================================================================
SPEC-M1-R1: AUTHOR RESOLUTION TO DEVIATION-018 (BINDING)
================================================================================

AUTHOR-ERR-011: Section E2 referenced "rho_e * v_dir.evaluation" without
defining v_dir, AND the original probe design was unpassable by construction:
h is drawn independently of x, so the residual target is unpredictable from
z(x) alone; the identifiable signal is the TAU-CONDITIONAL selection shift,
which enters only when tau is available as an input. Both defects repaired
below. The 0.5 correlation threshold and the lambda1 ladder are UNCHANGED;
this is probe repair, not criterion weakening.

R1-001 — G0b REDEFINED (supersedes E2 wherever they conflict):

  Inputs to the bias-only fit: design rows [z(x), tau] — the oracle feature
  vector z(x) in R^8 APPENDED with the scalar treatment indicator tau
  (total width 9). Trainable parameters: U and psi_e ONLY (envs 1..20),
  on the 400 observational rows per environment. Target: y - theta.z(x)
  - kappa*tau (as before).

  TRUE-BIAS REFERENCE TARGET, bound numerically (no closed form required):
    Using the EVAL KEY stream, draw M = 100000 auxiliary values
    h_j ~ N(0,1), j = 1..M (fixed once per world, reused for all envs).
    For each train environment e with recorded (a_e, b_e):
      m1_e = SUM_j sigma(a_e + b_e*h_j) * h_j  /  SUM_j sigma(a_e + b_e*h_j)
      m0_e = SUM_j (1 - sigma(a_e + b_e*h_j)) * h_j
                     /  SUM_j (1 - sigma(a_e + b_e*h_j))
    True bias target: bias*(e, x, tau) = eta * m_{tau}_e   (constant in x;
    this constancy is a property of the generator, declared openly).

  EVALUATION SET (explicit enumeration):
    environments {1,...,20}  x  tau in {0, 1}  x  the 2000-point x-grid
    (eval key, shared across all methods) = 80000 prediction/target pairs.

  METRIC AND THRESHOLD: Pearson correlation between model bias predictions
  and bias* over ALL 80000 pairs, pooled. PASS iff r > 0.5.

  LAMBDA1 SELECTION: unchanged — test {1e-2, 1e-3, 1e-4} in that order;
  frozen lambda1 := largest candidate whose G0b run passes; none passing
  => HALT and transmit, as originally bound.

R1-002 — DECLARED CONSEQUENCE OF THE REPAIR:
  Under the corrected probe, a passing G0b certifies that the quarantined
  channel can recover the per-environment tau-conditional shift at scale
  rho_e * 1.5 — the quantity the artifact channel exists to absorb in
  V-FULL. A failing G0b now means genuine non-identifiability, not a
  broken probe. Gate semantics strengthened, not loosened.

R1-003 — EVERYTHING ELSE STANDS: sections A-D, F, G, H, I unchanged except
  as superseded by R1-001. The spec-copy rule (B8/I3) extends to THIS file:
  maf_v1/spec/ must contain SPEC-M1-authored.md AND SPEC-M1-R1-authored.md
  before any execution begins.

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as maf_v1/spec/SPEC-M1-R1-authored.md; provenance commit.
  2. Close DEVIATION-018 as resolved-by-R1-001/-002.
  3. Implementation UNBLOCKED. Run gates G0a then G0b per E1/R1-001;
     transmit gate outcomes before full-run artifacts per E3/H-T1.
================================================================================
END SPEC-M1-R1
================================================================================
