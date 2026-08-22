from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import run_maf  # noqa: E402


def main() -> None:
    rows_path = HERE / "M1_ROWS.csv"
    rows = pd.read_csv(rows_path)
    config_paths = sorted((HERE / "configs").glob("seed_*.json"))
    if len(config_paths) != 30:
        raise RuntimeError(f"expected 30 configs, found {len(config_paths)}")
    refit_rows = []
    for idx, config_path in enumerate(config_paths, start=1):
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        seed = int(cfg["seed"])
        b_scale = float(cfg["b_scale"])
        lambda1 = float(cfg["lambda1"])
        world = run_maf.generate_world(seed, b_scale)
        if world.keys != {k: int(v) for k, v in cfg["seed_keys"].items()}:
            raise RuntimeError(f"seed-key mismatch for {seed}")
        model, duration = run_maf.train_maf(world, "V-SOFT", lambda1)
        mpsi, mdauroc = run_maf.maf_psi_metrics(world, model)
        if not (np.isfinite(mpsi) and np.isfinite(mdauroc)):
            raise RuntimeError(f"non-finite V-SOFT channel metric for {seed}: {mpsi}, {mdauroc}")
        mask = (rows["seed"].astype(int) == seed) & (rows["variant_or_baseline"] == "V-SOFT")
        if int(mask.sum()) != 1:
            raise RuntimeError(f"expected one V-SOFT row for {seed}, found {int(mask.sum())}")
        rows.loc[mask, "m_psi"] = mpsi
        rows.loc[mask, "m_dauroc"] = mdauroc
        cfg["vsoft_channel_metrics_provenance"] = "refit"
        cfg["vsoft_channel_metrics_refit_duration_seconds"] = float(duration)
        cfg["vsoft_channel_metrics_refit_runner"] = "maf_v1/refit_vsoft.py"
        config_path.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        refit_rows.append({"seed": seed, "m_psi": mpsi, "m_dauroc": mdauroc, "fit_seconds": duration, "provenance": "refit"})
        print(f"completed V-SOFT refit seed={seed} index={idx}/30 m_psi={mpsi:.12f} m_dauroc={mdauroc:.12f}", flush=True)
    rows.to_csv(rows_path, index=False)
    pd.DataFrame(refit_rows).to_csv(HERE / "metrics" / "vsoft_channel_refit.csv", index=False)
    print("refit_rows", len(refit_rows))
    print("vsoft_nonnull", int(rows.loc[rows.variant_or_baseline == "V-SOFT", ["m_psi", "m_dauroc"]].notna().all(axis=1).sum()))


if __name__ == "__main__":
    main()
