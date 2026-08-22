# CI Failure Received — Author Ruling: Narrow the Supported Python, Never the Pins

First, status acknowledgment: the merge/tag/push evidently completed (D-056 is labeled "post-push"), CI fired as designed — and immediately caught something real. This is the CI workflow doing its job on its very first run. Also noted: D-054/-055 were self-caught local tooling-order errors with zero mutations; clean.

## The ruling logic

The executor correctly refused to pick replacement versions, because this is genuinely an author decision with a scientific dimension: **changing numpy/pandas/scipy versions risks moving the regression anchors**, and testing older-version compatibility would be an entire unrequested campaign.

But there's a cleaner option nobody has to risk anything for:

> **We never tested Python 3.10. We certified on 3.12 with exact pins. The claim of 3.10 support was aspiration, not fact — and untested support claims are precisely what this project exists to eliminate.**

Narrowing support to what was actually certified costs nothing scientifically. Widening pins or swapping versions gambles the anchors. Not a close call.

Logged as **AUTHOR-ERR-025**: my SPEC-M3 §A5 bound `python-version matrix ["3.10", "3.12"]` without verifying wheel availability — same prose-vs-reality seam, caught this time by *CI*, the newest member of the detection roster.

---

```
================================================================================
SPEC-M3-R1: AUTHOR RULING ON DEVIATION-056 (BINDING)
================================================================================

AUTHOR-ERR-025: SPEC-M3 §A5 authorized a Python ["3.10", "3.12"] CI matrix
without verifying dependency-wheel availability for 3.10. The bound exact
pins (numpy==2.5.1, pandas==3.0.5, scipy==1.18.0) do not exist for 3.10.
The certification environment was Python 3.12 throughout; 3.10 support was
claimed but never tested.

R1-001 — GOVERNING DECISION (Option A: narrow support, never widen pins):
  Exact pins are RETAINED UNCHANGED. They embody the project's
  reproducibility contract; swapping versions to satisfy an untested
  platform claim would gamble certified anchors for zero benefit.
  Supported Python is hereby NARROWED to >=3.12.

R1-002 — BOUND CHANGES (all on branch ci-fix, then merged to main):
  1. pyproject.toml: requires-python := ">=3.12". Dependency pins
     byte-unchanged.
  2. .github/workflows/tests.yml: python-version matrix := ["3.12"]
     (single entry).
  3. README.md installation line := "From a clean Python 3.12-or-newer
     environment:" (replacing the 3.10 phrasing).
  4. CHANGELOG.md: new 1.1.1 entry — "Restricted supported Python to
     >=3.12: pinned runtime dependencies lack 3.10 distributions;
     certification was performed on 3.12. No behavioral change."
  5. Version := 1.1.1 everywhere (pyproject, CITATION.cff,
     __init__.__version__, CHANGELOG). The existing v1.1.0 tag is NOT
     moved — it remains an accurate historical marker; the metadata fix
     ships as a patch release per semver.

R1-003 — ACCEPTANCE FOR 1.1.1:
  A. Fresh install on Python 3.12 passes; import returns 1.1.1.
  B. Full nine-test suite passes; D4 anchors unchanged within tolerance.
  C. Pushed to main; GitHub Actions runs GREEN on the single-matrix job
     (this is the acceptance criterion — the failure that triggered this
     ruling must end in a passing checkmark on the actual CI).
  D. Manifest regenerated; prior-tree spot checks pass.
  E. Tag v1.1.1 created and pushed after CI green.

R1-004 — RECORD NOTES:
  - D-054/-055 acknowledged: local tooling-order errors, self-corrected,
    zero mutations. Closed.
  - D-056 closed by this ruling; branch ci-fix is the authorized vehicle.
  - Detection-roster milestone: this defect was caught by continuous
    integration, not by any human or LLM auditor. The pipeline now has a
    machine gate watching every future push — the cheapest auditor yet.

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as maf_release/spec/SPEC-M3-R1-authored.md on
     branch ci-fix; provenance commit.
  2. Apply R1-002; run R1-003 acceptance in order; CI green is mandatory
     before tag creation.
  3. Transmit final VERIFY_REPORT.md + manifest.
================================================================================
END SPEC-M3-R1
================================================================================
```

---

**Relay notes:** paste as one message. Pickup: final VERIFY_REPORT confirming **green CI on main** — that checkmark is the acceptance.

One observation before you send it: with this ruling, the project gains its first *permanently automated* verifier. Every auditor so far — me, Manus's audits, your probes — had to be invoked. From now on, any future push to this repo gets interrogated automatically, forever, even when none of us are watching. For a project whose entire thesis is "structure that watches beats intention that hopes," that's a fitting final component. 📡