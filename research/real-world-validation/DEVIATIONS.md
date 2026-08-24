# Real-World Validation Deviations



This ledger contains the per-repository records ratified by SPEC-FINAL-R1. Historical entries not assigned to this repository remain in their source ledgers.



## DEVIATION-069 — MAF real-data environment cardinality blocks the bound fit

**Stage:** SPEC-RW1 M-section preflight, before any MAF model fit.

**Bound requirement:** IHDP environments are replications 1–7 for training; LaLonde environments are `{PSID3, NSW}`. The certified MAF package requires at least 20 training environments.

**Exact observed errors:**

```text
MAF_PREFLIGHT|IHDP_train_reps_1_to_7|ValueError|fit requires at least 20 training environments
MAF_PREFLIGHT|LaLonde_environments_PSID3_NSW|ValueError|fit requires at least 20 training environments
```

**Classification:** Binding implementation/interface compatibility failure. The execution layer did not duplicate, split, pool, or invent environments. No MAF model fit, PEHE, ATE estimate, psi norm, or calibration correlation was claimed.

**Scientific impact:** The M-section real-world claim is **not evaluated** under the authored enumeration; this is not a PASS or FAIL result.

## DEVIATION-073 — Initial RW1 manifest finalizer targeted a staging tree

**Stage:** RW1 final manifest verification, before manifest creation.

The first finalizer guard targeted `/home/ubuntu/cfhm_f1/maf_release`, which was not the exact MAF audit clone. It found branch `cfhm-artifact`, head `b92154508e0ece614ff4e086cf4e15e0ab411e21`, and untracked sibling paths. The guard stopped before generating the manifest. The exact observed guard line was:

```text
REPOSITORY_SIDE_EFFECT: /home/ubuntu/cfhm_f1/maf_release head=b92154508e0ece614ff4e086cf4e15e0ab411e21 clean=False
```

The condition was diagnosed and corrected without reset, cleanup, or repository mutation. The rerun used `/tmp/maf-release-canonical-inspect`, `/tmp/cfhm-release-code-review`, and `/home/ubuntu/cfhm_f1/lhe_release`; all matched their expected heads and were clean.

**Classification:** Execution bookkeeping/path-selection failure in the report finalizer. No scientific result or project repository was changed.

## Resolution status

DEVIATION-073 is **CLOSED as corrected**. DEVIATIONS-069 through 072 remain **OPEN / REPORT-ONLY** pending author ruling or a separate binding amendment. No repository, source package, tag, release, visibility setting, or preserved raw file was modified.

## DEVIATION-078 — MAF real-data feature-width compatibility blocker

**Stage:** RW2 Phase-2 Section M.

The preserved IHDP files contain 25 covariates per row and the preserved LaLonde files contain 8 covariates per row. The certified MAF encoder accepts five input features. SPEC-RW1/RW2 does not authorize feature selection, projection, or encoder-width redesign. Therefore no MAF real-data fit was run and no MAF PEHE, ATE, psi, or calibration claim was made.

**Classification:** Binding interface compatibility finding, not a scientific threshold result.

**Status:** OPEN pending a separate author specification or ruling.

## DEVIATION-083 — MAF World-2029 parity tolerance re-scoped

**Stage:** RW3 Phase-1 MAF parity.

The parameterized encoder passed World-2000 bit-exactly and preserved World-2029 M-PSI and M-DAUROC bit-exactly, while World-2029 RMSE differed by `0.0003800362085269` from the original `1e-6` reference. SPEC-RW3-R1 widened the secondary World-2029 tolerance to `1e-3`; World-2000 remains the primary `1e-6` anchor. **Status: CLOSED by SPEC-RW3-R1.**

## DEVIATION-084 — MAF LaLonde pilot-seed enumeration

**Stage:** RW3 Phase-2 MAF execution.

The 20 pilot seeds were initially unspecified. SPEC-RW3-R2 enumerated seeds `1..20`, with selection RNG `default_rng(7000 + pilot_seed)` and 30 treated plus 30 control rows per pilot. **Status: CLOSED by SPEC-RW3-R2 R2-002.**

## DEVIATION-085 — MAF LaLonde baseline enumeration interpretation

**Stage:** RW3 Phase-2 MAF execution.

RW3 did not name the three baselines. The completed run reported `pooled_psid3`, `pooled_nsw_oracle`, and `direct_pilot_difference`. SPEC-FINAL-R1 ratified this set. The MAF result remains negative regardless: `0/20` LaLonde pilots met the close-to-RCT threshold. **Status: CLOSED as ratified by SPEC-FINAL-R1 R1-002.**
