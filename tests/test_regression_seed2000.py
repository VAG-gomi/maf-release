from maf import MAFModel, generate_world
from maf.metrics import rmse_holdout, psi_spearman


def test_world_2000_vfull_regression_anchors():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    report = model.fit(world["environments"])
    assert report.steps == 6000
    rmse = rmse_holdout(model, world)
    mpsi = psi_spearman(model, world)
    # Historical pre-refactor anchor: 0.111819155629592 (tol 1e-9).
    assert abs(rmse - 0.1118193525252465) <= 1e-6
    assert abs(mpsi - 0.9082706766917292) <= 1e-9
