# MAF Empirical Card

## Scope

Validated in synthetic confound-heavy environments with analytic ground truth (30 worlds, pre-registered criteria, independent execution). NOT validated on real-world data.

## SPEC-M1 T3 summary

| statistic | value |
|---|---:|
| g0a_pass_scale | 1.0 |
| g0b_lambda1_chosen | 0.001 |
| g0b_best_correlation | 0.9998984945969449 |
| p1_vfull_rmse_median | 0.14646940341878317 |
| p1_best_baseline_name | B-MIXED |
| p1_best_baseline_rmse_median | 0.3399518624815555 |
| p1_relative_reduction | 0.5691466363808199 |
| p2_mpsi_median | 0.7842105263157895 |
| p3_mdauroc_median | 0.895 |
| k1_gap_percent | 161.05665741791586 |
| k2_gap_percent | 250.77287923221172 |
| k4_vorac_mpsi_median | 0.9969924812030074 |
| verdict_label | PASS |

The computed verdict is **PASS** under the pre-registered SPEC-M1 criteria. The K1/K2 gaps mean removal or rewiring of the quarantined channel degrades holdout interventional accuracy by 161% / 251% relative.

Release code reproduces pre-release results to within 2e-7 RMSE (float reassociation); behavioral equivalence verified by exact M-PSI match and do-mask bitwise test (D2).

## Interpretation boundaries

This card reports the authored synthetic experiment only. It is not evidence of real-world performance, clinical validity, operational reliability, or deployment safety.

Kill conditions that would have falsified this result (K1-K4) are enumerated in spec/SPEC-M1-authored.md §G2.
