# MAF Release 1.1 Example

The following values were produced by executing `python3 examples/run_example.py` on seed 2000 under the release code. They are measured output, not illustrative or invented values.

## Configuration

| Parameter | Value |
|---|---:|
| seed | 2000 |
| hidden | 16 |
| rank `r` | 2 |
| lambda1 | 0.001 |
| weight decay | 0.0001 |
| torch seed | 4082789755 |
| fit epochs | 300 |
| fit steps | 6000 |
| adapted environment | 21 |
| adaptation steps | 200 |

## Measured metrics

| Metric | Measured value |
|---|---:|
| holdout RMSE | 0.1118193525252465 |
| M-PSI | 0.9082706766917292 |
| M-DAUROC | 0.8 |

The historical pre-refactor SPEC-M1 D4 regression anchor for holdout RMSE was `0.111819155629592`; the release-code measurement differs by `+1.968956545e-7`. SPEC-M2-R1 retires that pre-refactor anchor for release acceptance and binds `0.1118193525252465` with absolute tolerance `1e-6`. The M-PSI anchor remains `0.9082706766917292` and matched exactly. D-047 is closed by R1-001, and the complete D4–D6 and F1–F7 battery passed.

## Predictions

For five measured evaluation rows, the interventional predictions were:

```text
[-1.1797316074371338, 0.8059645295143127, 2.336653709411621,
  0.9596872925758362, 1.4244451522827148]
```

The first new-environment observational prediction was beta-only before adaptation. After the zero-initialized environment-21 adaptation, the measured observational predictions were:

```text
[-2.002743721008301, 0.28274255990982056, 2.2193045616149902,
  1.419898509979248, 1.9309678077697754]
```
