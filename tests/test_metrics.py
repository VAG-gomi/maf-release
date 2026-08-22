from maf import MAFModel, generate_world
from maf.metrics import dauroc


def test_world_2000_dauroc_anchor():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    model.fit(world["environments"])
    value = dauroc(model, world)
    assert abs(value - 0.80) <= 1e-9
