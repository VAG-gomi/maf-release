import numpy as np
import torch

from maf import MAFModel, generate_world


def test_interventional_prediction_is_bitwise_independent_of_artifact_channel():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    model.fit(world["environments"])
    x = world["eval_grids"][21][:128]
    tau = np.linspace(0.0, 1.0, len(x))
    before = model.predict_interventional(x, tau)
    with torch.no_grad():
        model.U.fill_(1.0e6)
        for parameter in model.psi:
            parameter.fill_(-1.0e6)
    after = model.predict_interventional(x, tau)
    assert np.array_equal(before, after)
