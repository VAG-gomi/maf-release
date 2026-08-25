================================================================================
SPEC-MAF-A1: AUTONOMOUS MAF ENVIRONMENT NORMALIZATION
Author: Ox-alpha mandate; Executor: Manus
================================================================================

STATUS
This is a new executor-authored pre-registration under the autonomous campaign.
It is written before the A1 MAF runs. The published MAF source, RW3 evidence,
tags, and all historical records are immutable.

1. OBJECTIVE
Test one bounded engineering change within the MAF concept: pooled training
feature standardization before the existing MAF neural factorization. The
question is whether numerical environment normalization improves causal
interventional prediction without altering the do-mask, hidden width, rank,
training epochs, causal targets, or baseline definitions.

2. VARIANT
The variant is MAF-ENVNORM. For each benchmark, compute one feature mean and
standard deviation from the concatenated training observational and trial
features only; replace zero standard deviations with 1.0; standardize every
training and evaluation feature with those fixed training statistics. Fit the
published generalized `MAFModel(hidden=16, r=2)` with the same 300 epochs,
learning rate, penalties, and seeded initialization. No evaluation labels or
holdout features are used to estimate normalization statistics. The published
MAF is the unchanged comparator implementation; MAF-ENVNORM changes only input
scaling in the isolated workspace.

3. LALONDE PROTOCOL
Use DS-A `psid3_controls.txt`, `nswre74_control.txt`, and
`nswre74_treated.txt`. Preserve the exact 20 pilot seeds 7001..7020 and the
same 30-control/30-treated pilot sampling per seed. The RCT ATE is the NSW
full-sample treated-minus-control mean. Fit two MAF environments: env 1 is the
full PSID3 observational record; env 2 contains empty observational arrays and
the sampled NSW pilot as trial records. Evaluate the interventional effect on
the remaining NSW rows. Compare absolute ATE error against the existing
pooled-PSID3, pooled-NSW-pilot, and direct-pilot-difference baselines. Primary
LaLonde improvement is MAF-ENVNORM mean absolute error strictly below the best
of those three baseline mean errors across the 20 pilots.

4. IHDP PROTOCOL
Use DS-B `ihdp_npci_1.csv` through `_10.csv`, shape (747,30), with x columns
5:30, observed treatment column 0, observed outcome column 1, and truth effect
column 4 minus column 3. Train on replications 1..7 and evaluate holdouts 8..10.
Use the pooled training-feature normalization statistics, `input_dim=25`, and
one seeded model per holdout replication. Compare sqrt-PEHE to the unchanged
pooled linear regression and per-environment linear baselines. Primary IHDP
improvement is mean MAF-ENVNORM sqrt-PEHE strictly below mean pooled sqrt-PEHE.

5. VERDICT AND REPORTING
MAF-ENVNORM is a campaign success only if it beats a pooled baseline on at
least one primary benchmark. Otherwise report MAF-ENVNORM as FAIL/NOT-ACHIEVED;
no tuning, threshold relaxation, or narrative substitute is allowed. Record
all 20 LaLonde rows, all 3 IHDP rows, normalization statistics hashes, model
configuration, tests, deviations, and a SHA-256 manifest. Keep the work
isolated and transmit the complete campaign record to the author for audit.
================================================================================
END SPEC-MAF-A1
================================================================================
