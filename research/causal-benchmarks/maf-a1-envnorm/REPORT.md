## 2. MAF bounded investigation

The MAF-A1 investigation tested only feature standardization, computed from training features, before the published generalized MAF factorization. The do-mask, hidden width 16, rank 2, training schedule, penalties, benchmark inputs, and baseline definitions were preserved. The isolated MAF regression suite passed 9 tests.

| Benchmark | MAF-ENVNORM | Best pooled baseline | Result |
|---|---:|---:|---|
| LaLonde mean absolute ATE error | 1,776.877845 | 954.982596, direct pilot difference | No improvement |
| IHDP mean sqrt-PEHE | 13.050908 | 12.858283, pooled regression | No improvement |

`campaign_pass = FALSE`. MAF-ENVNORM therefore did not meet the mandate’s requirement to beat a pooled baseline on at least one real causal benchmark. The complete 20-pilot LaLonde records, 3 IHDP holdout rows, and per-run normalization statistics are preserved in `MAF_A1_RESULTS.json`.
