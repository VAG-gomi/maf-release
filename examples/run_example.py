from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

# Permit running this file directly from an unpacked source tree.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from maf import MAFModel, generate_world
from maf.metrics import dauroc, psi_spearman, rmse_holdout


def main() -> None:
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    fit_report = model.fit(world["environments"])
    holdout = world["environments"][20]
    adapt_report = model.adapt(holdout["x_obs"], holdout["tau_obs"], holdout["y_obs"], steps=200, lr=1e-2)
    x = world["eval_grids"][21][:5]
    tau = np.asarray([0.0, 0.0, 0.5, 1.0, 1.0], dtype=float)
    result = {
        "seed": world["seed"],
        "fit_steps": fit_report.steps,
        "fit_epochs": fit_report.epochs,
        "adapt_env_id": adapt_report.env_id,
        "adapt_steps": adapt_report.steps,
        "interventional_prediction_first5": model.predict_interventional(x, tau).tolist(),
        "observational_before_first5": model.predict_interventional(x, tau).tolist(),
        "observational_after_first5": model.predict_observational(x, tau, adapt_report.env_id).tolist(),
        "rmse_holdout": rmse_holdout(model, world),
        "m_psi": psi_spearman(model, world),
        "m_dauroc": dauroc(model, world),
        "config": {
            "hidden": model.hidden,
            "r": model.r,
            "lambda1": model.lambda1,
            "weight_decay": model.weight_decay,
            "torch_seed": world["keys"]["world"] + 7000,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
