import numpy as np
import pytest

from maf import MAFModel, generate_world


def test_tau_validation_rejects_out_of_range_and_accepts_bounds():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    model.fit(world["environments"])
    env = world["environments"][20]
    x = env["x_obs"][:2]
    y = env["y_obs"][:2]

    for call in [
        lambda: model.predict_interventional(x, np.array([1.5, 0.0])),
        lambda: model.predict_observational(x, np.array([0.0, -0.1]), 1),
        lambda: model.adapt(x, np.array([0.0, 1.5]), y, steps=1),
        lambda: model.artifact_score(x, np.array([2.0, 0.0]), 1),
    ]:
        with pytest.raises(ValueError, match=r"tau value"):
            call()

    model.predict_interventional(x, np.array([0.0, 1.0]))
    model.predict_observational(x, np.array([0.0, 1.0]), 1)
    model.artifact_score(x, np.array([0.0, 1.0]), 1)
    model.adapt(x, np.array([0.0, 1.0]), y, steps=1)
