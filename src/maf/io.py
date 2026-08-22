"""Configuration and provenance persistence helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_config(path: str | Path, config: dict[str, Any], provenance: dict[str, Any] | None = None) -> Path:
    """Atomically save a JSON configuration with optional provenance fields."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(config)
    if provenance is not None:
        payload["provenance"] = dict(provenance)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(target)
    return target


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON configuration and preserve its provenance fields unchanged."""
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("configuration root must be a JSON object")
    return value


__all__ = ["save_config", "load_config"]
