# Changelog

All notable changes to this project are documented here in Keep a Changelog format.

## [1.1.1] - 2026-08-22

### Changed

- Restricted supported Python to `>=3.12`: pinned runtime dependencies lack Python 3.10 distributions; certification was performed on Python 3.12. No behavioral change.

## [1.1.0] - 2026-08-22

### Added

- Added `CHANGELOG.md`, `CITATION.cff`, `.gitignore`, and a two-version CI test workflow.
- Added README and API documentation of the V-SOFT limitation and the importance of the do-mask.
- Added explicit misuse guards for unfitted models and out-of-range treatment values.
- Added a runtime warning for refitting an already fitted model.

### Changed

- `fit()` now sorts input environments by ascending `env_id`, using one-based positional indices when an ID is absent.
- Expanded API documentation with misuse behavior and bound method semantics.
- Bumped the package version to `1.1.0`.

### Preserved

- SPEC-M1 model mechanics, do-mask behavior, zero-init quarantine, training schedule, numerical anchors, and deterministic behavior remain unchanged within the authorized tolerance.

## [1.0.0] - 2026-08-22

### Added

- Initial certified MAF Release 1.0 package.
- SPEC-M1 mechanism–artifact factorization model with a global mechanism channel and quarantined environment artifact channel.
- Deterministic world generator, model API, metrics, tests, documentation, authored specifications, verification report, deviations ledger, and SHA-256 manifest.
- SPEC-M1 scientific result: computed verdict `PASS`.
- SPEC-M2 production packaging and verification: D4–D6 and F1–F7 acceptance battery passed.
