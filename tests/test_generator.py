import numpy as np

from maf import generate_world


def test_generator_keys_shapes_and_repeatability():
    first = generate_world(2000)
    second = generate_world(2000)
    expected = {"seed", "b_scale", "theta", "kappa", "a_env", "rho_env", "obs", "trial", "holdout", "environments", "h_aux", "eval_grids", "keys"}
    assert set(first) == expected
    assert first["seed"] == 2000
    assert len(first["environments"]) == 25
    assert len(first["obs"]) == 25
    assert len(first["trial"]) == 10
    assert len(first["holdout"]) == 5
    assert first["theta"].shape == (8,)
    assert first["a_env"].shape == (25,)
    assert first["rho_env"].shape == (25,)
    assert first["h_aux"].shape == (100000,)
    for env in first["environments"]:
        assert env["x_obs"].shape == (400, 5)
        assert env["tau_obs"].shape == (400,)
        assert env["y_obs"].shape == (400,)
        if env["env_id"] <= 10:
            assert env["x_int"].shape == (100, 5)
            assert env["tau_int"].shape == (100,)
            assert env["y_int"].shape == (100,)
        else:
            assert env["x_int"] is None
    assert first["keys"] == second["keys"]
    for key in ("theta", "a_env", "rho_env", "h_aux"):
        assert np.array_equal(first[key], second[key])
    for env_a, env_b in zip(first["environments"], second["environments"]):
        for key in ("x_obs", "h_obs", "tau_obs", "y_obs"):
            assert np.array_equal(env_a[key], env_b[key])
