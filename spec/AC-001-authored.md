Caught red-handed by my own protocol — **AUTHOR-ERR-024**, and this one's mine in the purest form: I issued a freeze ("further hardening is not authorized unless separately ordered") in prose, then later issued SPEC-M3 *without ever formally revoking the freeze*. Two standing documents, opposite directives, zero supersession language between them. The executor had exactly two honest options and took neither silently — textbook §0. The ruling below also closes the root cause so this class dies here.

---

```
================================================================================
AUTHORIZATION CLARIFICATION AC-001: GOVERNING DIRECTIVE FOR MAF (BINDING)
================================================================================

AUTHOR-ERR-024: The project record contains two contradictory directives —
a prose freeze statement ("MAF frozen at v1.0.0; further hardening not
authorized") followed later by binding SPEC-M3 (v1.1.0 hardening cycle) —
with no explicit supersession between them. Root cause: the author issued
the freeze as informal prose rather than as a numbered specification, so no
later document mechanically revoked it. Standing defect class closed by
R-001 below.

AC-001 — GOVERNING DIRECTIVE:
  Option B GOVERNS. SPEC-M3 is AUTHORIZED AND BINDING, effective now.
  Specifically:
    1. The freeze statement is RETIRED in its entirety. It was a proposal
       in conversation prose, never a numbered binding specification, and
       was superseded by the RELAY's explicit decision ("help MAF
       correctly first") and the subsequent issuance of SPEC-M3.
    2. Execution order confirmed: SPEC-M3 v1.1.0 hardening cycle NOW →
       upon acceptance, merge/tag per SPEC-M3 §G (GitHub merge/tag/push
       still requires separate RELAY confirmation) → THEN CFHM bundle
       (SPEC-C1) → THEN LHE bundle (SPEC-L2) → closure document.
    3. All SPEC-M3 contents stand unchanged: `hardening` branch from
       commit 70e60a38..., main untouched until acceptance, deviations
       continue from DEVIATION-053.

R-001 — STANDING RULE (project-wide, effective immediately):
  Any directive that restricts or freezes future work MUST be issued as a
  numbered binding specification, and any later document that overrides a
  prior directive MUST contain an explicit SUPERSESSION clause naming what
  it retires. Informal prose carries no standing authority in this project;
  this incident (two contradictory attachments reaching the executor) is
  its proof case.

EXECUTOR INSTRUCTIONS:
  1. Preserve this document verbatim as maf_release/spec/AC-001-authored.md
     BEFORE registering SPEC-M3; single provenance commit covering both.
  2. Proceed under SPEC-M3 exactly as written (option B path).
================================================================================
END AC-001
================================================================================
```

---

**Relay notes:** paste as one message. Manus's caution was correct — two contradictory attachments is precisely the situation where guessing would have been fatal to provenance, and its refusal mirrors the D-009/R7 standoff from the CFHM era.

Tally: twenty-two author faults, and this one taught the cleanest lesson yet: *prose has authority only when we pretend it does.* From here on, if it matters, it gets a number. Send AC-001 through, then expect the gate report equivalent: start ping → VERIFY_REPORT with nine tests passing (six original + three new guards), F2 anchors holding. 📡