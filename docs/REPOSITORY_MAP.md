# MAF Repository Map

This repository is the **canonical home of the MAF model software**. The other repositories are navigational mirrors and evidence views; they do not replace the canonical implementation here.

## Canonical model and package

| Item | Actual location in this repository | Direct purpose |
|---|---|---|
| Core model | [`src/maf/model.py`](../src/maf/model.py) | Executable `MAFModel` implementation |
| World generator | [`src/maf/worlds.py`](../src/maf/worlds.py) | Deterministic package world generation |
| Metrics | [`src/maf/metrics.py`](../src/maf/metrics.py) | Package metric functions |
| I/O helpers | [`src/maf/io.py`](../src/maf/io.py) | Configuration and provenance persistence |
| Public exports | [`src/maf/__init__.py`](../src/maf/__init__.py) | Exposes `MAFModel`, `generate_world`, and version `1.1.1` |
| Tests | [`tests/`](../tests) | Nine executable package tests |
| API documentation | [`docs/API.md`](API.md) | Public API reference |
| Worked example | [`examples/run_example.py`](../examples/run_example.py) | Executable package usage example |
| Package verification | [`verification/VERIFY.md`](../verification/VERIFY.md) | Release verification report |

## Original experiment and evidence

| Item | Actual location in this repository | Direct purpose |
|---|---|---|
| Experiment runner | [`research/maf-spec-m1/run_maf.py`](../research/maf-spec-m1/run_maf.py) | Generates worlds, fits experimental variants and baselines, computes metrics, and writes evidence |
| T2 rows | [`research/maf-spec-m1/M1_ROWS.csv`](../research/maf-spec-m1/M1_ROWS.csv) | 240 actual result rows |
| T3 summary | [`research/maf-spec-m1/SUMMARY.csv`](../research/maf-spec-m1/SUMMARY.csv) | 13 actual summary statistics |
| Verdict | [`research/maf-spec-m1/results/verdict.json`](../research/maf-spec-m1/results/verdict.json) | Structured computed verdict |
| Gate report | [`research/maf-spec-m1/GATE_REPORT.md`](../research/maf-spec-m1/GATE_REPORT.md) | Gate outcomes and selected constants |
| Raw worlds | [`research/maf-spec-m1/worlds/`](../research/maf-spec-m1/worlds) | 30 binary NumPy world artifacts |
| Configurations | [`research/maf-spec-m1/configs/`](../research/maf-spec-m1/configs) | 30 recorded world configurations |
| Metric artifacts | [`research/maf-spec-m1/metrics/`](../research/maf-spec-m1/metrics) | Per-method metric files and refit table |
| Raw evidence manifest | [`research/maf-spec-m1/ARTIFACT_MANIFEST.sha256`](../research/maf-spec-m1/ARTIFACT_MANIFEST.sha256) | Hash index for the original evidence subset |
| Bank manifest | [`research/maf-spec-m1/BANK_MANIFEST.sha256`](../research/maf-spec-m1/BANK_MANIFEST.sha256) | Hash index for the expanded bank folder |

## Three separate repositories

| Repository | Role |
|---|---|
| [`maf-release`](https://github.com/VAG-gomi/maf-release) | Canonical model software, package release, and historical v1.1.1 Release marker |
| [`maf-software`](https://github.com/VAG-gomi/maf-software) | Human-readable software mirror with actual source and tests |
| [`maf-spec-m1-evidence`](https://github.com/VAG-gomi/maf-spec-m1-evidence) | Original SPEC-M1 evidence product with raw files under `evidence/` and readable result pages |
| [`maf-evidence-bank`](https://github.com/VAG-gomi/maf-evidence-bank) | Expanded evidence bank with raw files, release specifications, manifests, and readable result pages |

## Frozen release identity

The immutable [`v1.1.1` tag](https://github.com/VAG-gomi/maf-release/tree/v1.1.1) points to the hardened package commit. The evidence-bank commit was intentionally added later on `main`, so the tag remains a clean software-release identity and is not moved.

## Reading order

Start with [`README.md`](../README.md), then open [`docs/MODEL_OVERVIEW.md`](MODEL_OVERVIEW.md) for the implementation map. For the original experiment, read [`research/maf-spec-m1/HANDOFF.md`](../research/maf-spec-m1/HANDOFF.md), [`research/maf-spec-m1/PRODUCTION_VERIFICATION.md`](../research/maf-spec-m1/PRODUCTION_VERIFICATION.md), and the human-readable files in one of the separate evidence repositories.
