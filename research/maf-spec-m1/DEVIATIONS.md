# SPEC-M1 Deviation Ledger

## DEVIATION-018 — G0b references an undefined evaluation direction vector

**Stage:** SPEC-M1 pre-implementation audit.

Section E2 requires the bias-only identifiability probe to compare recovered bias predictions with true bias `rho_e * v_dir.evaluation`, but SPEC-M1 does not define `v_dir`, its dimensionality, its values, its normalization, or how it is generated from the declared RNG streams. The symbol is not defined elsewhere in the received specification, and the input F1-v2 artifacts do not provide an MAF evaluation direction vector.

This is material because G0b’s Pearson correlation and the selected frozen `lambda1` depend on the reference bias target. Choosing a direction would create an un-authored evaluation target and could change whether the gate passes. Implementation is paused; no world generation, gate fit, or full model fit has been run.

**Classification:** Specification ambiguity; no scientific or implementation choice has been made.

## DEVIATION-018 closure — resolved by SPEC-M1-R1-001/-002

R1-001 binds the G0b reference target numerically using the eval-key `h_j` sample and defines the pooled 80,000-pair Pearson correlation. The undefined `v_dir.evaluation` target is retired.

## DEVIATION-019 — R1 G0b input width and trainable-map wiring remain unspecified

**Stage:** SPEC-M1-R1 pre-implementation audit.

R1-001 changes G0b inputs to `[z(x), tau]` of width 9 and says only `U` and `psi_e` are trainable, while C3 defines `U` as an `8x2` matrix and C4 defines the artifact contribution through `phi(x_full)^T U psi_e`, where C1’s encoder maps a width-6 `[x1..x5,tau]` input to width 8. The binding text does not specify whether G0b should use the C1 encoder, a direct oracle-feature map, how the width-9 design row connects to the 8-dimensional U, or whether the appended tau is consumed by a trainable/non-trainable transformation. These alternatives produce different recovered bias predictions and therefore different G0b correlations and lambda1 selection.

This ambiguity was not resolved by the numerical reference-target repair. Implementation is paused; no MAF gate fit or world generation has run. An author binding is requested for the exact G0b prediction function and which parameters are frozen or initialized.

## DEVIATION-019 closure — resolved by SPEC-M1-R2-001/-002/-003

R2-001 binds the G0b probe to the fixed non-trainable `g9(x,tau)=[z(x);tau]` map, a separate `U_G` in R^{9x2}, zero-initialized psi values, the exact trainable set `{U_G, psi_1,...,psi_20}`, 2000 Adam steps at 1e-3, and world_int+7000 torch seed. The C1 encoder is excluded from G0b. R2-002 binds the rank-2 identifiability rationale and R2-003 confirms all other MAF specification sections remain unchanged.

## DEVIATION-019 closure — resolved by SPEC-M1-R2-001/-002/-003

R2-001 binds G0b to the fixed non-trainable `g9(x,tau)=[z(x);tau]` map, separate `U_G` in R^{9x2}, zero-initialized psi values, the exact trainable set `{U_G, psi_1,...,psi_20}`, 2000 Adam steps at 1e-3, and world_int+7000 torch seed. The C1 encoder is excluded from G0b. R2-002 binds the rank-2 identifiability rationale and R2-003 confirms all other MAF sections remain unchanged.

## DEVIATION-020 — Full-model environment-batch training loop is undefined

**Stage:** SPEC-M1 pre-implementation audit after R2.

C6 binds “Adam lr 1e-3, 300 epochs full-batch per environment-batch loop as implemented,” but no implementation is supplied and the specification does not define whether an epoch means one pooled optimizer step over environments 1..20, one optimizer step per environment, an environment-batch size/order, loss weighting between 400 observational and 100 interventional rows, or the sequence of environment batches. These choices change V-FULL/V-A0/V-SOFT/V-ORAC parameters and all downstream metrics.

Implementation is paused; no MAF gate fit or world generation has run.

## DEVIATION-021 — V-ORAC encoder state is unspecified

**Stage:** SPEC-M1 pre-implementation audit after R2.

D defines V-ORAC as beta replaced by frozen true theta, with only U and psi_e trainable. C4 still consumes `phi(x_full)` from the C1 encoder, but the spec does not bind whether the encoder is trained before beta replacement, initialized from V-FULL, freshly initialized and frozen, replaced by an oracle feature map, or otherwise fixed. The resulting interventional predictions and M-RMSE are not determined by the stated text.

Implementation is paused pending the exact encoder initialization/freeze rule for V-ORAC.

## DEVIATION-022 — B-MIXED estimator is not executable as written

**Stage:** SPEC-M1 pre-implementation audit after R2.

B-MIXED is specified only as “mixed-effects linear regression on z(x) with per-env random intercept and random tau-coefficient; unseen envs use population means.” The estimator, fitting objective, treatment of the quadratic/interactions in z(x), random-effect covariance/estimation method, and whether trial interventional rows enter the fit are not defined. Different standard mixed-effects implementations produce different holdout predictions and M-RMSE.

Implementation is paused; no substitute estimator will be chosen.

## DEVIATION-023 — G0a scale propagation is unspecified

**Stage:** SPEC-M1 pre-implementation audit after R2.

E1 says that if world 2000 fails, the generator is rerun with the `b_e` scale multiplied by 2, then 4, and the first passing scale is recorded. The full-run sections do not state whether the selected scale is a global generator constant for worlds 2000..2029, whether only world 2000 is replaced while other worlds remain at scale 1, or whether each world independently repeats the scale ladder. These alternatives change the confounding regime and every subsequent result.

Implementation is paused pending the binding scale-propagation rule.

## DEVIATION-024 — G0b regularization relative to lambda1 is not fully bound

**Stage:** SPEC-M1 pre-implementation audit after R2.

R2-001 binds G0b’s training objective as mean squared error and binds the lambda1 ladder/freeze rule, while C5 defines Gaussian NLL plus lambda1 times the psi norm plus 1e-4 weight decay for the main model. The text does not state whether G0b adds the lambda1 psi penalty and weight decay to its MSE, or whether lambda1 is merely recorded/selected externally. This changes the G0b correlations and chosen frozen lambda1.

Implementation is paused pending the exact G0b loss formula.

## DEVIATIONS-020 through -024 closure — resolved by SPEC-M1-R3-001 through -006

R3-001 binds the full-model loop to 20 ascending environment steps per epoch, 300 epochs, all rows equally weighted, 6000 optimizer steps per fit, and per-variant world+7000 torch reseeding. R3-002 binds V-ORAC to the G0b g9/U_G/psi wiring, observational train rows only, analytic interventional truth, and the new M-PSI-based K4. R3-003 binds B-MIXED to pooled OLS plus per-environment ridge/shrinkage deviations. R3-004 makes the G0a scale a single global constant for all worlds and stages. R3-005 binds the G0b MSE plus lambda1 psi penalty and U_G weight decay. R3-006 supersedes the T3 summary with the exact thirteen-row enumeration.

## DEVIATION-025 — Baseline training procedures remain under-specified

**Stage:** SPEC-M1 post-R3 pre-implementation audit.

R3-001 specifies the 6000-step environment-batch loop for “each variant fit,” but D lists B-POOL, B-ENVNN, B-MIXED, and B-IRML as baselines without fully binding the optimizer, epoch count, batch construction, initialization, loss weighting, or early stopping for B-POOL, B-ENVNN, and B-IRML. B-IRML additionally gives `lambda_iv in {0.1, 1.0}` selected on trial-env interventional error but does not specify the fit loop or whether its pooled MLP follows C6’s loop. B-MIXED is now executable by R3-003. Different baseline training choices change the “best baseline” and P1.

Implementation is paused pending an author binding for B-POOL, B-ENVNN, and B-IRML training procedures. No MAF gate fit or world generation has run.

## DEVIATION-026 — V-FULL/V-A0/V-SOFT artifact-channel parameter initialization is not fully bound for R3 loop

**Stage:** SPEC-M1 post-R3 pre-implementation audit.

C3 binds U initialization N(0,0.01) and psi exact zero, while C2 binds beta initialization N(0,0.01), but R3-001 says each variant reseeds immediately before construction and notes different architectures consume the stream differently. V-A0 structurally removes Gamma and V-SOFT changes branch wiring, yet the text does not explicitly bind whether beta/U/psi/corresponding encoder tensors use the same initialization draws and parameter registration order as V-FULL before the variant-specific change. This affects deterministic comparisons. An explicit variant initialization order is requested; no assumption will be made.

## DEVIATION-027 — Holdout adaptation and evaluation-environment treatment is not fully enumerated

**Stage:** SPEC-M1 post-R3 pre-implementation audit.

D binds adaptation for MAF variants as 200 Adam steps on each holdout environment’s observational NLL with psi_new trainable, while F1 evaluates over holdout environments and interventional queries. It does not explicitly state whether each holdout environment’s 400 observational rows are used for adaptation before scoring, whether the 200 adaptation steps use the same bound batch/mean-loss convention as C6, or how V-ORAC’s analytic interventional branch interacts with the adaptation instruction. These choices affect M-RMSE. An author binding is requested.

## DEVIATIONS-025 through -027 closure — resolved by SPEC-M1-R4-001 through -003

R4-001 binds B-POOL, B-ENVNN, B-IRML, and B-MIXED training procedures, including the B-IRML candidate selection. R4-002 binds per-variant torch reseeding and natural parameter-registration order, with intentionally unaligned initialization draws. R4-003 binds holdout adaptation to V-FULL/V-A0/V-SOFT only, using 400 observational rows, 200 Adam steps at 1e-2, and per-environment seeds; V-ORAC and baselines do not adapt.

## DEVIATION-028 — World-generator RNG draw order and eval-stream partition are not bound

**Stage:** SPEC-M1 post-R4 pre-implementation audit.

B7 names seven child streams (`world`, `assign`, `outcome`, `sampling`, `model_init`, `adapt`, `eval`) but does not specify which stream generates each declared random object or the draw order within a stream: theta/kappa, per-environment a_e/rho_e, covariates, latent h, treatment assignments, outcome noise, the G0b auxiliary h_j sample, and the 2000-point evaluation grid. The eval key is reused by G0b and F1 evaluation, but no partition/order is stated. These alternatives produce different worlds and gate outcomes. No random draw convention will be invented.

## DEVIATION-029 — V-ORAC RMSE target conflicts between F1 and R3/R4 wording

**Stage:** SPEC-M1 post-R4 pre-implementation audit.

F1 defines M-RMSE against analytic interventional truth `mu*(x,tau)`. R3-002 defines V-ORAC’s interventional branch as exactly analytic truth and calls its M-RMSE a “noise floor,” while R4-003 describes V-ORAC evaluation grid rows as “analytic truth + noise floor.” If the F1 target remains analytic `mu*`, V-ORAC’s M-RMSE is identically zero; if noisy outcomes/noise-floor variance are included in the target, it is nonzero. This changes the diagnostic value and the reported T2/P1 quantities even though V-ORAC is excluded from P1 arithmetic. An author binding is required for the V-ORAC RMSE reference target and whether any noise is added to predictions or targets.

## DEVIATION-030 — B-IRML candidate tie handling is not bound

**Stage:** SPEC-M1 post-R4 pre-implementation audit.

R4-001 requires selecting the better lambda_iv candidate by trial-env interventional RMSE after both candidates are trained, but does not specify a deterministic tie rule. The tie is unlikely but the executor cannot silently choose a candidate under an exact reproducibility specification. An author binding is requested; no candidate has been fit.

## DEVIATIONS-028 through -030 closure — resolved by SPEC-M1-R5-001 through -003

R5-001 binds the complete RNG allocation and draw order, including the global b_scale transform and the reserved unused streams. R5-002 retires the contradictory noise-floor wording and binds the V-ORAC RMSE reference to analytic mu*, hence exactly 0.0. R5-003 binds exact-equality B-IRML candidate ties to lambda_iv=1.0.

## DEVIATION-031 — R4 requires holdout adaptation for V-A0, which has no psi channel

**Stage:** SPEC-M1 post-R5 pre-implementation audit.

D defines V-A0 as “Gamma STRUCTURALLY REMOVED (beta-only),” so V-A0 contains no U or psi_e parameters. R4-003 nevertheless says holdout adaptation applies to V-FULL, V-A0, and V-SOFT, and requires constructing a zero-initialized trainable psi_e while freezing all other parameters. The two bindings cannot both be implemented literally: V-A0 has no psi_e to construct or train. Treating V-A0 as if it retained an unconnected psi would change the structural ablation; skipping adaptation would contradict R4-003 and alter its holdout M-RMSE.

This is material because V-A0 is used in K1 and channel-gap arithmetic. Implementation is paused; no gate, world, or MAF fit has run. An author binding is requested for V-A0 holdout handling: either no adaptation for V-A0, or an explicitly defined residual adaptation parameterization that preserves the structural removal.

## DEVIATION-031 closure — resolved by SPEC-M1-R6-001/-002/-003

R6-001 binds V-A0 to receive no holdout adaptation and amends the adaptation set to {V-FULL, V-SOFT}. R6-002 records the metric no-op of V-FULL adaptation, the non-inert V-SOFT adaptation, and the K1 interpretation. R6-003 leaves all other thresholds and schemas unchanged.

## DEVIATION-036 — Unhandled runtime failure

ValueError: all the input array dimensions except for the concatenation axis must match exactly, but along dimension 0, the array at index 0 has size 2000 and the array at index 4 has size 1


## DEVIATION-036 — G0b evaluation-grid scalar tau shape failure

**Stage:** G0b gate execution after G0a passed at b_scale=1.

The first gate run failed while evaluating the bound G0b prediction on a 2000-point grid with scalar `tau=0.0`. The exact traceback was:

```text
Traceback (most recent call last):
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 948, in <module>
    raise SystemExit(main())
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 938, in main
    return run(args.mode)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 883, in run
    gate = run_gates()
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 335, in run_gates
    corr = g0b_fit(selected_world, lam)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 305, in g0b_fit
    gg = torch.as_tensor(z_map(x, tau).astype(np.float32))
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 197, in z_map
    return np.column_stack([np.ones(x.shape[0]), x, x[:, 2] ** 2, x[:, 3] * x[:, 4], tau_arr.reshape(-1)])
ValueError: all the input array dimensions except for the concatenation axis must match exactly, but along dimension 0, the array at index 0 has size 2000 and the array at index 4 has size 1
```

This is an implementation shape-handling failure, not a scientific design change. No G0b fit completed and no full-run artifact was generated. The required minimal fix is to broadcast scalar tau to the number of rows in `x` when constructing the fixed g9 map.

## DEVIATION-037 — Full-mode output reset would delete the required gate report

**Stage:** Pre-full-run implementation audit after successful G0a/G0b.

The initial runner reset unconditionally deleted `GATE_REPORT.csv` and `GATE_REPORT.md` before checking for the gate report in `--mode full`, making a full run self-blocking after a successful gate stage. This is an implementation lifecycle error, not an authored design choice. The minimal correction is to remove gate-report files only when running `--mode gates`, and preserve them when running `--mode full`. No full-run fit was started.

## DEVIATION-036 — Unhandled runtime failure

AttributeError: 'MAFModel' object has no attribute 'psi'


## DEVIATION-038 — V-A0 metric collector accessed an absent psi channel

**Stage:** Full MAF run, first world fit after G0a/G0b passed.

The full run completed the V-A0 fit but failed while collecting channel metrics because V-A0 is correctly constructed without a `psi` attribute. The exact traceback was:

```text
Traceback (most recent call last):
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 953, in <module>
    raise SystemExit(main())
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 943, in main
    return run(args.mode)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 913, in run
    results, _ = fit_world(world, gate.g0b_lambda1)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 746, in fit_world
    mpsi, md = maf_psi_metrics(world, model)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 455, in maf_psi_metrics
    psi_norm = [float(torch.linalg.vector_norm(p).detach().cpu()) for p in model.psi]
AttributeError: 'MAFModel' object has no attribute 'psi'. Did you mean: 'phi'?
```

This is an implementation metric-dispatch error exposed by the structural V-A0 binding, not a scientific redesign. The minimal correction is to emit blank channel metrics for V-A0 and continue the fit/reporting path. No result-driven change was made.

## DEVIATION-036 — Unhandled runtime failure

TypeError: maf_psi_metrics() missing 1 required positional argument: 'model'


## DEVIATION-039 — V-ORAC metric collector called with missing model argument

**Stage:** Full MAF run, after V-FULL/V-A0/V-SOFT processing of the first world.

The run failed when dispatching V-ORAC channel metrics because `maf_psi_metrics` requires `(world, model, oracle=True)` but the caller supplied only `(orac, oracle=True)`. The exact traceback was:

```text
Traceback (most recent call last):
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 956, in <module>
    raise SystemExit(main())
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 946, in main
    return run(args.mode)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 916, in run
    results, _ = fit_world(world, gate.g0b_lambda1)
  File "/home/ubuntu/cfhm_f1/maf_v1/run_maf.py", line 754, in fit_world
    orac_mpsi, orac_md = maf_psi_metrics(orac, oracle=True)
TypeError: maf_psi_metrics() missing 1 required positional argument: 'model'
```

This is an implementation call-site error, not a scientific design change. No full-run result was emitted. The minimal correction is to call `maf_psi_metrics(world, orac, oracle=True)`.

## DEVIATION-040 — T2 channel-column rule names undefined V-SOVT rather than V-SOFT

**Stage:** Post-run T2 schema audit, after all 30 worlds completed.

R3-006 states that “V-A0/V-SOVT/B-* rows leave channel columns blank,” but SPEC-M1 defines the variant `V-SOFT`, not `V-SOVT`. F2/F3 define M-PSI and M-DAUROC for the MAF channel, and V-SOFT has an active U/psi channel, so the executor cannot determine whether V-SOFT’s channel metrics should be transmitted or blanked. The current provisional T2 rows leave V-SOFT channel fields blank because the implementation populated only V-FULL and V-ORAC; no correction is being made pending author binding.

This ambiguity affects the required T2 evidence schema and may affect interpretation of K2, though it does not change the already computed RMSE values. The completed run and raw artifacts are preserved provisionally; no final handoff or classification is issued.

## DEVIATION-040 closure — resolved by SPEC-M1-R7-001/-002/-003

R7-001 binds channel-column population for exactly {V-FULL, V-SOFT, V-ORAC}; R7-002 authorizes deterministic refit of missing V-SOFT channel metrics from recorded per-world configurations and requires stored/refit provenance flags; R7-003 records the pre-result scientific interpretation of V-SOFT as diagnostic gold. The earlier `V-SOVT` spelling is retired.

## DEVIATION-041 — R7 amendment filename/content mismatch in inherited MAF tree

**Stage:** Production-bundle audit after the completed R7-corrected run.

The inherited file `maf_v1/spec/SPEC-M1-R7-authored.md` is named as the R7 amendment, but its contents begin with `SPEC-M1-R6` and contain the R6-001 through R6-003 resolution. The paired `SPEC-M1-R7-relay-attachment.txt` likewise contains the R6 relay text. This conflicts with the final handoff statement that the R7 amendment is preserved verbatim. The existing files are retained unchanged for historical provenance. The exact R7 binding relayed by the user is added separately as `SPEC-M1-R7-canonical-relay.txt`, explicitly labeled as a canonical relay copy; no scientific artifact, threshold, result, or prior file is changed. This is a provenance/package defect, not a scientific rerun authorization.
