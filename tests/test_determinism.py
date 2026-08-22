import numpy as np

from maf import MAFModel, generate_world


def test_same_seed_double_fit_is_bitwise_identical():
    world_a = generate_world(2000)
    world_b = generate_world(2000)
    model_a = MAFModel(seed=world_a["keys"]["world"] + 7000)
    model_b = MAFModel(seed=world_b["keys"]["world"] + 7000)
    model_a.fit(world_a["environments"])
    model_b.fit(world_b["environments"])
    x = world_a["eval_grids"][21][:256]
    tau = np.linspace(0.0, 1.0, len(x))
    assert np.array_equal(model_a.predict_interventional(x, tau), model_b.predict_interventional(x, tau))
    assert model_a.psi_norms() == model_b.psi_norms()
