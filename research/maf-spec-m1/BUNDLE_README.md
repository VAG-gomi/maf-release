# SPEC-M1 MAF Evidence Product

## Purpose

This directory is the **complete, hash-verifiable evidence product** for the authored SPEC-M1 MAF experiment. It is an evidence and reproducibility bundle, not a silently redesigned model implementation. The scientific artifacts remain those produced by the authored run and the author-authorized SPEC-M1-R7 deterministic V-SOFT refit.

## Scientific result

The final computed label is **PASS**. The binding gates passed before the full run: G0a selected `b_scale=1.0`, and G0b selected `lambda1=0.001` with best pooled correlation `0.9998984945969449`. The transmitted T2 contains 240 rows, the T3 summary contains 13 rows, and the result is reproduced in `results/verdict.json`.

## Product contents

| Area | Contents |
|---|---|
| Authored contract | `spec/` contains SPEC-M1 and all received amendment/relay files, plus the canonical relayed R7 copy |
| Source | `run_maf.py`, `refit_vsoft.py`, and `verify_maf_bundle.py` |
| Gates | `GATE_REPORT.csv`, `GATE_REPORT.md` |
| T2/T3/T4/T5 | `M1_ROWS.csv`, `SUMMARY.csv`, `DEVIATIONS.md`, `ARTIFACT_MANIFEST.sha256` |
| Raw evidence | 30 world files, 30 configs, 240 method metric files, 120 loss records, and the V-SOFT refit table |
| Provenance | `HANDOFF.md`, `STATUS.md`, `STATUS_PROVENANCE.md`, logs, and Git history |

## Verification

Run the read-only verifier from the repository root:

```bash
python3 -B maf_v1/verify_maf_bundle.py
```

The verifier does not retrain models and does not rewrite scientific outputs. It checks the exact T2/T3 schemas and cardinalities, seed-by-method coverage, metric/T2 consistency, world/config completeness, loss schedules, frozen gate constants, R7 V-SOFT refit provenance, summary arithmetic, verdict consistency, and every file hash in the manifest.

## Reproduction modes

The authored runner remains available for a clean execution in a new output root only. The current `maf_v1/` tree is the completed evidence product and must not be reset in place when inspecting it. The gate and full modes are:

```bash
python3 maf_v1/run_maf.py --mode gates
python3 maf_v1/run_maf.py --mode full
```

A clean reproduction should first copy the source and `spec/` contract into a separate working directory, retain the recorded environment/dependency information, and compare the resulting artifacts against the transmitted contract. The R7 channel correction is separately reproducible with:

```bash
python3 maf_v1/refit_vsoft.py
```

## Provenance cautions

The inherited files named `spec/SPEC-M1-R7-authored.md` and `spec/SPEC-M1-R7-relay-attachment.txt` are retained byte-for-byte, but their contents are R6 text despite their R7 filenames. This is recorded as D-041. The exact R7 binding relayed by the user is preserved in `spec/SPEC-M1-R7-canonical-relay.txt`; no inherited file was overwritten.

The original rolling status file was retained as `STATUS.md`. Because the runner overwrote that file at each stage and no historical start/midpoint snapshots were committed, `STATUS_PROVENANCE.md` explicitly distinguishes the observed full-run log and final status from reconstructed checkpoint descriptions. No synthetic snapshot is presented as an original runtime artifact.

## Release identity

The authoritative source identity is the Git history of `/home/ubuntu/cfhm_f1`. The release ZIP is created outside this directory so that packaging does not create a self-referential manifest. Before distribution, run the verifier and ensure the repository working tree is clean.
