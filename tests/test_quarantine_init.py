import numpy as np

from maf import MAFModel, generate_world


def test_new_environment_starts_beta_only_and_adaptation_is_local():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    model.fit(world["environments"])
    env = world["environments"][20]
    x = env["x_obs"][:64]
    tau = env["tau_obs"][:64]
    beta_only = model.predict_interventional(x, tau)
    before = model.predict_observational(x, tau, 21)
    assert np.array_equal(before, beta_only)
    report = model.adapt(env["x_obs"], env["tau_obs"], env["y_obs"], steps=200, lr=1e-2)
    after = model.predict_observational(x, tau, report.env_id)
    assert report.env_id == 21
    assert not np.array_equal(before, after)
    train_before = model.predict_interventional(x, tau)
    train_after = model.predict_interventional(x, tau)
    assert np.array_equal(train_before, train_after)
