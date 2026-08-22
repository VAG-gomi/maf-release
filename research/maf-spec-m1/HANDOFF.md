# SPEC-M1 MAF Final Evidence Handoff

## Final status

The binding SPEC-M1-R7 amendment has been applied to the completed 30-world run. The scientific run itself was not rerun and no criterion, threshold, parameter, or result was changed. The final computed label remains **PASS**.

The gate stage passed at `b_scale=1.0`. G0b selected the largest passing value, `lambda1=0.001`, with best pooled correlation `0.9998984945969449`.

## T2 — `M1_ROWS.csv`

`M1_ROWS.csv` contains exactly **240 rows**: 30 worlds × 8 methods. Channel columns are populated exactly for `V-FULL`, `V-SOFT`, and `V-ORAC`, and are blank for `V-A0`, `B-POOL`, `B-ENVNN`, `B-MIXED`, and `B-IRML`, as required by R7-001.

The 30 missing V-SOFT channel-metric rows were computed by deterministic refit from the recorded per-world configurations. Each corresponding configuration records `vsoft_channel_metrics_provenance: "refit"`; the raw refit table is `metrics/vsoft_channel_refit.csv`.

## T3 — `SUMMARY.csv`

`SUMMARY.csv` contains exactly the bound **13 summary rows**, unchanged from the completed scientific run:

| Statistic | Value |
|---|---:|
| `g0a_pass_scale` | 1.0 |
| `g0b_lambda1_chosen` | 0.001 |
| `g0b_best_correlation` | 0.9998984945969449 |
| `p1_vfull_rmse_median` | 0.14646940341878317 |
| `p1_best_baseline_name` | B-MIXED |
| `p1_best_baseline_rmse_median` | 0.3399518624815555 |
| `p1_relative_reduction` | 0.5691466363808199 |
| `p2_mpsi_median` | 0.7842105263157895 |
| `p3_mdauroc_median` | 0.895 |
| `k1_gap_percent` | 161.05665741791586 |
| `k2_gap_percent` | 250.77287923221172 |
| `k4_vorac_mpsi_median` | 0.9969924812030074 |
| `verdict_label` | PASS |

## T4 — `DEVIATIONS.md`

`DEVIATIONS.md` is transmitted as the complete ledger, including the recorded implementation failures D-036 through D-039, the closure of D-040 by R7-001 through R7-003, and the production-audit D-041 record. No previous deviation entry was deleted or rewritten.

## T5 — `ARTIFACT_MANIFEST.sha256`

`ARTIFACT_MANIFEST.sha256` covers every file under `maf_v1/`, including the `spec/` subtree, raw world/config/metric outputs, logs, status files, the corrected T2/T3 files, the R7 refit script and table, the deviation ledger, and this handoff.

## Provenance and immutability

The F1-v1, F1-v2, and SPEC-002 trees remain unchanged. The inherited files named `spec/SPEC-M1-R7-authored.md` and `spec/SPEC-M1-R7-relay-attachment.txt` are retained unchanged, but their contents are R6 text; this mismatch is recorded in D-041. The exact R7 binding relayed by the user is preserved separately at `spec/SPEC-M1-R7-canonical-relay.txt`. All R7 work is confined to the `maf_v1/` evidence tree and its provenance history.
