import numpy as np
import pytest

from maf import MAFModel, generate_world


def test_all_fitted_entry_points_raise_before_fit():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    x = np.zeros((2, 5), dtype=np.float32)
    tau = np.array([0.0, 1.0], dtype=np.float32)
    y = np.zeros(2, dtype=np.float32)

    calls = [
        lambda: model.predict_interventional(x, tau),
        lambda: model.predict_observational(x, tau, 1),
        model.psi_norms,
        lambda: model.artifact_score(x, tau, 1),
        lambda: model.adapt(x, tau, y, steps=1),
    ]
    for call in calls:
        with pytest.raises(RuntimeError, match=r"model not fitted: call fit\(\) first"):
            call()
