import pytest

from maf import MAFModel, generate_world


def test_second_fit_emits_refit_warning():
    world = generate_world(2000)
    model = MAFModel(seed=world["keys"]["world"] + 7000)
    model.fit(world["environments"])
    with pytest.warns(RuntimeWarning, match=r"refitting over previously fitted model"):
        report = model.fit(world["environments"])
    assert report.steps == 6000
