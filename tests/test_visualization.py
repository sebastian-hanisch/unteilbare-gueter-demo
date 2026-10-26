"""Abbildungen: Aufbau, gesperrte Achsen, Werte an der Hand-Instanz."""

import numpy as np
import pytest

import ung_constants as C
import ung_evaluation as ev
import ung_visualization as V


@pytest.fixture
def a_zwei(zwei):
    return ev.analyse_values(ev.Settings(n=2, m=3), zwei)


def locked(fig):
    return all(ax.fixedrange for ax in fig.select_xaxes()) and all(ax.fixedrange for ax in fig.select_yaxes())


def test_allocation_figure_by_hand(a_zwei):
    fig = V.build_allocation(a_zwei)
    heat = fig.data[0]
    assert list(heat.y) == [C.RULE_SHORT[r] for r in C.RULES] and list(heat.x) == ["T1", "T2", "T3"]
    assert np.array(heat.z).tolist() == [[0, 1, 0], [0, 1, 1], [0, 1, 1], [0, 1, 1], [0, 1, 1]]
    assert np.array(heat.text).tolist() == [["10", "7", "4"], ["10", "7", "5"], ["10", "7", "5"], ["10", "7", "5"], ["10", "7", "5"]]       # der Wert der Tour für ihren Besitzer
    assert np.array(heat.customdata).tolist()[0] == [1, 2, 1]
    assert heat.zmin == -0.5 and heat.zmax == 1.5 and locked(fig)


def test_allocation_scale_has_one_flat_block_per_driver(a_zwei):
    scale = V.build_allocation(a_zwei).data[0].colorscale
    assert [c[1] for c in scale] == [C.COLOR_DRIVERS[0]] * 2 + [C.COLOR_DRIVERS[1]] * 2 and scale[0][0] == 0.0 and scale[-1][0] == 1.0


def test_shares_figure_by_hand(a_zwei):
    fig = V.build_shares(a_zwei)
    bars = [t for t in fig.data if t.type == "bar"]
    assert [b.name for b in bars] == ["Fahrer 1", "Fahrer 2"]
    assert [round(float(v), 3) for v in bars[0].y] == [0.7, 0.5, 0.5, 0.5, 0.5]            # 14 / 20, 10 / 20
    assert [round(float(v), 3) for v in bars[1].y] == [0.35, 0.6, 0.6, 0.6, 0.6]           # 7 / 20, 12 / 20
    lines = [s for s in fig.layout.shapes if s.type == "line"]
    assert len(lines) == 1 and lines[0].y0 == pytest.approx(0.5) and locked(fig)


def test_shares_figure_has_a_color_for_every_possible_driver():
    assert len(C.COLOR_DRIVERS) >= C.N_MAX
    a = ev.analyse(ev.Settings(n=C.N_MAX, m=C.M_MIN, seed=3))
    assert len([t for t in V.build_shares(a).data if t.type == "bar"]) == C.N_MAX


def rows(param, xs):
    return [{"param": param, "x": x, "rule": rule, "runs": 10, "efx": 0.5, "po": 0.7} for x in xs for rule in C.RULES]


def test_series_figure_has_one_line_per_rule():
    fig = V.build_series(rows("m", (4, 5)), "efx", "EFX")
    assert [t.name for t in fig.data] == [C.RULE_SHORT[r] for r in C.RULES] and list(fig.data[0].x) == [4, 5]
    assert fig.layout.xaxis.title.text == V.AXIS_TITLES["m"] and locked(fig)
    models = V.build_series(rows("model", tuple(C.MODELS)), "po", "PO")
    assert list(models.data[0].x) == ["Unabhängig", "Ähnlich", "Spezialisten"]
    assert V.build_series(rows("n", (2, 3)), "efx", "EFX").layout.xaxis.title.text == V.AXIS_TITLES["n"]


def test_series_axis_range_follows_ymax():
    assert tuple(V.build_series(rows("n", (2, 3)), "efx", "EFX", ymax=1.2).layout.yaxis.range) == (0, 1.2)
