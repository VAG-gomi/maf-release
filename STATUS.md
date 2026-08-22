# SPEC-M3 Status — Completion

**Stage:** MAF Release 1.1.0 hardening cycle completed on branch `hardening`.

**Acceptance:** F1–F8 PASS. Fresh installation/import returned version `1.1.0`; all nine tests passed with zero skips/xfails; D4 RMSE, M-PSI, and M-DAUROC anchors passed; D5 determinism passed; required files/content passed; misuse probes now produce the specified RuntimeError, ValueError, and RuntimeWarning; the final SHA-256 manifest passed; and three prior-tree spot checks matched exactly.

**Scientific preservation:** RMSE remained `0.1118193525252465`, M-PSI remained `0.9082706766917292`, and the do-mask and deterministic tests passed. No acceptance tolerance was loosened.

**Provenance:** AC-001 and SPEC-M3 are preserved verbatim under `spec/`. DEVIATION-053 records the start-ping sequencing issue and its closure. Main remains at certified v1.0.0 commit `70e60a3805f3444706493713a986094a6072c7f3`; no GitHub action was performed.

**Release status:** The `hardening` branch is eligible for separate relay review. Per SPEC-M3 §G, merging into `main`, tagging `v1.1.0`, and pushing to GitHub require separate confirmation. GitHub Release publication remains a separate human decision.
