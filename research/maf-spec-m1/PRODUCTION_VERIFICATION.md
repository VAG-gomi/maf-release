# SPEC-M1 MAF Production Verification Certificate

## Verification result

**`MAF_PRODUCTION_VERIFY=PASS`**

The verifier was run against the expanded `maf_v1/` tree with:

```bash
python3 -B maf_v1/verify_maf_bundle.py
```

The verifier is read-only with respect to scientific outputs. It does not retrain or alter the MAF models.

## Checks passed

| Check | Result |
|---|---:|
| T2 row count | 240 |
| T2 schema | exact five authored columns |
| Seed × method coverage | 30 seeds × 8 methods, one row per pair |
| World/config artifacts | 30 / 30 |
| Per-method metric JSON artifacts | 240 |
| MAF loss artifacts | 120 |
| R7 V-SOFT refit rows | 30, all marked `refit` |
| T2-to-metric numeric consistency | passed |
| Channel-column rule | passed: V-FULL/V-SOFT/V-ORAC populated; others blank |
| Frozen gate constants | `b_scale=1.0`, `lambda1=0.001` |
| Gate outcomes | G0a and G0b passed |
| Summary arithmetic | independently recomputed and matched |
| Verdict consistency | `PASS` in T3 and `results/verdict.json` |
| Artifact manifest | all listed files present and hash-matched |

## Artifact cardinality

The verifier reports the manifest entry count at runtime. This count includes the expanded production documentation, canonical R7 relay copy, verifier, raw evidence, specifications, logs, and all transmitted T2–T5 files.

## Provenance limitations disclosed

The inherited files named `spec/SPEC-M1-R7-authored.md` and `spec/SPEC-M1-R7-relay-attachment.txt` contain R6 text despite their R7 filenames. They are preserved unchanged. The exact R7 binding supplied in the relayed instruction is preserved separately as `spec/SPEC-M1-R7-canonical-relay.txt`, and D-041 records the mismatch.

The runner retained only one rolling `STATUS.md`; no original standalone start or midpoint snapshots were committed. `STATUS_PROVENANCE.md` reports this limitation and distinguishes the observed full-run log from any reconstructed description. No synthetic snapshot is presented as an original runtime artifact.

These are **package/provenance disclosures**, not changes to the scientific design or result. The scientific verdict remains the computed SPEC-M1 result: **PASS**.

## Release identity

The production bundle must be generated only after the verifier passes and the repository working tree is clean. The release ZIP is kept outside `maf_v1/` so the manifest remains non-self-referential.
