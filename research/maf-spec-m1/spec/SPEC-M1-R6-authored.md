================================================================================
SPEC-M1-R6: AUTHOR RESOLUTION TO DEVIATION-031 (BINDING)
================================================================================

AUTHOR-ERR-016: R4-003 required holdout adaptation for V-A0 while D defines
V-A0 as having no psi channel — an unimplementable conjunction. Resolution
below, including a DECLARED ARCHITECTURAL CONSEQUENCE (R6-002) that the
contradiction's investigation surfaced and that must be on record before
any number exists.

R6-001 — V-A0 HOLDOUT HANDLING:
  V-A0 receives NO holdout adaptation. R4-003's adaptation set is amended
  to {V-FULL, V-SOFT} exactly; V-A0 is reclassified STRUCTURALLY
  INADAPTABLE.
  Declared non-handicap, with reasoning on the record: (i) V-A0 possesses
  no quarantine surface, so no safe adaptation parameterization exists
  for it — inventing one would break the structural ablation K1 depends
  on; (ii) per R6-002(a), V-FULL's own adaptation is provably inert for
  every scored metric, so V-A0 forfeits no scored advantage by skipping
  it. No asymmetry in any scored quantity arises from this ruling.

R6-002 — DECLARED ARCHITECTURAL CONSEQUENCES (recorded PRE-GATE):
  (a) V-FULL holdout adaptation is a METRIC NO-OP: psi_e enters only the
      observational branch (C4 do-mask), so 200 adaptation steps alter
      no quantity that F2/F3/M-RMSE read. Adaptation is retained solely
      to mirror deployment semantics; its scored effect is identically
      zero. This was implicit in the architecture and is now explicit.
  (b) V-SOFT's holdout adaptation is NOT inert: its Gamma participates in
      the interventional branch, so observational-row adaptation injects
      environment-specific bias directly into scored interventional
      predictions. The do-mask's protective value is therefore expressed
      THROUGH K2: if V-SOFT fails to match V-FULL, part of the gap is
      adaptation-path contamination by wiring, not merely training-time
      coupling. K2's wording is unchanged; this is its interpretation,
      fixed before results.
  (c) K1 interpretation, fixed before results: V-A0 and V-FULL possess
      IDENTICAL interventional machinery (beta-only readout); they differ
      only through main-training dynamics (Gamma gradients flowing
      through the shared encoder/beta). K1 therefore remains purely the
      decoration test — whether the channel's mere presence during
      training helps or hurts the mechanism — with no adaptation term
      entering either side.
  (d) No pre-registered threshold or criterion is altered by this
      resolution. G1/G2 arithmetic stands exactly as published.

R6-003 — EVERYTHING ELSE STANDS. SPEC-M1 + R1..R5 remain binding except
  as amended by R6-001/-002. T2 schema unchanged (V-A0 rows carry rmse;
  channel columns already blank per R3-006).

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as maf_v1/spec/SPEC-M1-R6-authored.md; provenance commit.
  2. Close DEVIATION-031 as resolved-by-R6-001/-002.
  3. Implementation UNBLOCKED. Run G0a then G0b; transmit gate outcomes
     (b-scale, lambda1, best G0b correlation) BEFORE any full-run artifacts.
================================================================================
END SPEC-M1-R6
================================================================================
