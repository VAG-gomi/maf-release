# SPEC-M1 Status Provenance

## Evidence status

The authored SPEC-M1 transmission contract requires start, approximately midpoint, and completion status pings. The inherited runner writes a single rolling `STATUS.md`; it does not create immutable per-stage status snapshots. The committed MAF tree therefore contains the final status file and the full-run log, but not original standalone start or midpoint status files.

This record is a **provenance disclosure**, not a replacement runtime artifact. It does not claim that reconstructed text was emitted at the original timestamps.

| Stage | Available evidence | Assessment |
|---|---|---|
| Start | Runner source establishes the start-stage write; the original rolling file was later overwritten and no committed snapshot was found | Not independently preserved as an original file |
| Gate completion | `GATE_REPORT.md`, `GATE_REPORT.csv`, and Git history | Preserved |
| Midpoint | `logs/full_run.log` proves world completion through `world=2014 index=15/30`; the original rolling midpoint file was later overwritten | Execution boundary is evidenced; original standalone status text is not preserved |
| Completion | `STATUS.md` states `30/30 worlds; 240 method rows; verdict=PASS`; `logs/full_run.log` contains all 30 completion lines | Preserved |

## Why this is not silently repaired

Creating a file that looked like an original start or midpoint ping would manufacture provenance. The correct production treatment is to preserve the limitation explicitly and keep the full-run log, final status, Git history, and result artifacts available for audit.

## Related files

`STATUS.md` is the final rolling status. `logs/full_run.log` is the per-world completion log. `DEVIATIONS.md` records implementation and provenance issues, including D-041. `BUNDLE_README.md` describes the release and verification procedure.
