"""Befunde der README als feste Werte und Bänder: jede Zahl, die dort steht, ist hier an den festen Plänen der App geprüft.

Die Presets sind einzelne Instanzen und deshalb exakt. Die Messreihen sind Anteile von 150 Instanzen mit festen Zufalls-Seeds (die Standardabweichung eines Anteils liegt bei höchstens 4 Prozentpunkten):
Bänder von ±10 Punkten, Nullen, Hundert-Prozent-Aussagen und „nie“-Sätze exakt (die Läufe sind deterministisch).
"""

import pytest

import ung_constants as C
import ung_evaluation as ev

BAND = 0.10


def at(preset):
    return ev.analyse(ev.Settings(**C.PRESETS[preset]))


def flags(a, rule):
    """Kurzform je Regel: E = neidfrei, 1 = EF1, X = EFX, P = Pareto-optimal; fehlt der Buchstabe, ist die Eigenschaft verletzt."""
    return "".join(c if ev.holds(a, rule, k) else "-" for c, k in (("E", "ef"), ("1", "ef1"), ("X", "efx"))) + ("P" if a.outcomes[rule].pareto else "-")


def all_flags(a):
    return {r: flags(a, r) for r in C.RULES}


# --- Presets: einzelne Instanzen -------------------------------------------------------------------------------------------------------------

def test_default_preset():
    a = at("Drei Fahrer, neun Touren")
    assert all_flags(a) == {"reihum": "E1XP", "neidkreis": "-1--", "nash": "E1XP", "leximin": "-1-P", "summe": "-1-P"}
    assert (ev.pct(a.shares["ef1"]), ev.pct(a.shares["efx"]), ev.pct(a.shares["ef"], 1)) == ("17 %", "2 %", "0,6 %")
    assert {r: ev.pct(a.outcomes[r].nash_ratio) for r in C.RULES} == {"reihum": "89 %", "neidkreis": "40 %", "nash": "100 %", "leximin": "73 %", "summe": "52 %"}
    assert a.outcomes["neidkreis"].utilities == (37, 21, 27) and a.outcomes["nash"].utilities == (58, 20, 45)
    assert a.outcomes["summe"].utilities == (75, 8, 45) and int(a.values[1].sum()) == 43 and ev.pct(a.outcomes["summe"].shares[1]) == "19 %"


def test_five_drivers_preset_where_even_the_nash_rule_violates_efx():
    a = at("Fünf Fahrer: Nash-Wohlfahrt ohne EFX")
    assert all_flags(a) == {"reihum": "-1-P", "neidkreis": "-1XP", "nash": "-1-P", "leximin": "-1XP", "summe": "---P"}
    assert not any(ev.holds(a, r, "ef") for r in C.RULES) and (ev.pct(a.shares["ef1"]), ev.pct(a.shares["efx"])) == ("3 %", "0 %")
    assert a.outcomes["summe"].utilities == (0, 50, 0, 0, 65)


def test_similar_tastes_preset():
    a = at("Ähnliche Geschmäcker")
    assert all_flags(a) == {"reihum": "-1--", "neidkreis": "-1X-", "nash": "E1XP", "leximin": "E1XP", "summe": "---P"}
    assert ev.pct(a.outcomes["reihum"].nash_ratio) == "74 %" and ev.pct(a.outcomes["neidkreis"].nash_ratio) == "84 %"


def test_specialists_preset_where_leximin_violates_ef1():
    a = at("Spezialisten: Leximin ohne EF1")
    assert all_flags(a) == {"reihum": "E1XP", "neidkreis": "-1--", "nash": "E1XP", "leximin": "---P", "summe": "-1-P"}
    assert ev.pct(a.outcomes["neidkreis"].nash_ratio) == "25 %" and ev.pct(a.outcomes["leximin"].nash_ratio) == "53 %"


def test_four_drivers_preset():
    a = at("Vier Fahrer, acht Touren")
    assert all_flags(a) == {"reihum": "E1XP", "neidkreis": "-1--", "nash": "-1XP", "leximin": "E1XP", "summe": "-1-P"}
    assert (ev.pct(a.shares["ef1"]), ev.pct(a.shares["efx"])) == ("7 %", "0 %")


# --- Reihen ----------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def models():
    return ev.series_models()


@pytest.fixture(scope="module")
def goods():
    return ev.series_goods()


@pytest.fixture(scope="module")
def drivers():
    return ev.series_drivers()


def cell(rows, x, rule, key):
    return ev.cell_of(rows, x, rule)[key]


def test_ef1_holds_for_round_robin_envy_cycle_and_nash_in_every_cell(models, goods, drivers):
    for rows in (models, goods, drivers):
        for r in rows:
            if r["rule"] in ("reihum", "neidkreis", "nash"):
                assert r["ef1"] == 1.0, (r["param"], r["x"], r["rule"])


def test_the_rules_without_a_fairness_aim_or_with_the_nash_product_are_always_pareto_optimal(models, goods, drivers):
    for rows in (models, goods, drivers):
        for r in rows:
            if r["rule"] in ("nash", "leximin", "summe"):
                assert r["po"] == 1.0, (r["param"], r["x"], r["rule"])


def test_nash_and_leximin_and_sum_reach_their_own_optimum(models, goods, drivers):
    for rows in (models, goods, drivers):
        for r in rows:
            assert {"nash": r["nash"], "leximin": r["min"], "summe": r["sum"]}[r["rule"]] == 1.0 if r["rule"] in ("nash", "leximin", "summe") else True


def test_models_efx_and_ef1(models):
    f = lambda model, rule, key: cell(models, model, rule, key)
    assert f("unabhaengig", "reihum", "efx") == pytest.approx(0.95, abs=BAND) and f("unabhaengig", "neidkreis", "efx") == pytest.approx(0.57, abs=BAND)
    assert f("unabhaengig", "nash", "efx") == pytest.approx(0.99, abs=BAND) and f("unabhaengig", "leximin", "efx") == pytest.approx(0.91, abs=BAND) and f("unabhaengig", "summe", "efx") == pytest.approx(0.25, abs=BAND)
    assert f("aehnlich", "reihum", "efx") == pytest.approx(0.63, abs=BAND) and f("aehnlich", "neidkreis", "efx") == pytest.approx(0.95, abs=BAND) and f("aehnlich", "nash", "efx") == pytest.approx(0.93, abs=BAND)
    assert f("spezialisten", "neidkreis", "efx") == pytest.approx(0.33, abs=BAND) and f("spezialisten", "leximin", "efx") == pytest.approx(0.69, abs=BAND) and f("spezialisten", "nash", "efx") >= 0.95
    assert f("spezialisten", "leximin", "ef1") == pytest.approx(0.85, abs=BAND) and f("unabhaengig", "leximin", "ef1") >= 0.95 and f("unabhaengig", "summe", "ef1") == pytest.approx(0.50, abs=BAND)


def test_models_pareto_optimality_of_round_robin_and_envy_cycle(models):
    assert cell(models, "unabhaengig", "reihum", "po") == pytest.approx(0.69, abs=BAND) and cell(models, "aehnlich", "reihum", "po") == pytest.approx(0.41, abs=BAND)
    assert cell(models, "spezialisten", "reihum", "po") == pytest.approx(0.83, abs=BAND)
    assert all(cell(models, m, "neidkreis", "po") <= 0.15 for m in C.MODELS)


def test_models_nash_welfare_of_the_other_rules(models):
    assert cell(models, "unabhaengig", "neidkreis", "nash") == pytest.approx(0.51, abs=0.08) and cell(models, "spezialisten", "neidkreis", "nash") == pytest.approx(0.36, abs=0.08)
    assert cell(models, "unabhaengig", "reihum", "nash") == pytest.approx(0.90, abs=0.08) and cell(models, "unabhaengig", "summe", "nash") == pytest.approx(0.73, abs=0.08)
    assert cell(models, "unabhaengig", "leximin", "nash") == pytest.approx(0.92, abs=0.08)


def test_models_sum_of_utilities_and_ef1_of_the_greedy_sum(models):
    assert cell(models, "unabhaengig", "nash", "sum") == pytest.approx(0.97, abs=0.08) and cell(models, "unabhaengig", "reihum", "sum") == pytest.approx(0.94, abs=0.08)
    assert cell(models, "unabhaengig", "neidkreis", "sum") == pytest.approx(0.78, abs=0.08)
    assert cell(models, "aehnlich", "summe", "ef1") == pytest.approx(0.25, abs=BAND) and cell(models, "spezialisten", "summe", "ef1") == pytest.approx(0.80, abs=BAND)


def test_models_envy_freeness(models):
    assert cell(models, "unabhaengig", "nash", "ef") == pytest.approx(0.87, abs=BAND) and cell(models, "aehnlich", "nash", "ef") == pytest.approx(0.41, abs=BAND)
    assert cell(models, "aehnlich", "leximin", "ef") == pytest.approx(0.59, abs=BAND) and cell(models, "aehnlich", "reihum", "ef") == pytest.approx(0.12, abs=BAND)


def test_goods_series(goods):
    assert [cell(goods, m, "nash", "efx") for m in C.SERIES_MS] == pytest.approx([0.89, 0.90, 0.98, 0.99, 0.99, 0.99], abs=BAND)
    assert [cell(goods, m, "nash", "ef") for m in C.SERIES_MS] == pytest.approx([0.35, 0.37, 0.68, 0.76, 0.90, 0.87], abs=BAND)
    assert [cell(goods, m, "reihum", "efx") for m in C.SERIES_MS] == pytest.approx([0.55, 0.61, 0.93, 0.71, 0.80, 0.95], abs=BAND)
    assert [cell(goods, m, "neidkreis", "po") for m in C.SERIES_MS] == pytest.approx([0.59, 0.41, 0.25, 0.10, 0.09, 0.03], abs=BAND)
    assert cell(goods, 4, "leximin", "ef1") == pytest.approx(0.97, abs=BAND)


def test_drivers_series(drivers):
    assert [cell(drivers, n, "nash", "efx") for n in C.SERIES_NS] == pytest.approx([0.99, 0.99, 0.94, 0.81], abs=BAND)
    assert [cell(drivers, n, "leximin", "efx") for n in C.SERIES_NS] == pytest.approx([0.95, 0.94, 0.96, 0.84], abs=BAND)
    assert [cell(drivers, n, "reihum", "efx") for n in C.SERIES_NS] == pytest.approx([0.94, 0.71, 0.52, 0.29], abs=BAND)
    assert [cell(drivers, n, "nash", "ef") for n in C.SERIES_NS] == pytest.approx([0.95, 0.76, 0.19, 0.03], abs=BAND)
    assert [cell(drivers, n, "reihum", "nash") for n in C.SERIES_NS] == pytest.approx([0.94, 0.84, 0.73, 0.63], abs=0.08)
    assert [cell(drivers, n, "summe", "ef1") for n in C.SERIES_NS] == pytest.approx([0.81, 0.53, 0.32, 0.18], abs=BAND)


def test_the_series_use_the_documented_seeds():
    assert C.SERIES_SEED == 100000 and C.SERIES_RUNS == 150 and (C.SERIES_N, C.SERIES_M) == (3, 9) and C.SERIES_M_FOR_NS == 7
    assert C.SERIES_MS == (4, 5, 6, 7, 8, 9) and C.SERIES_NS == (2, 3, 4, 5)
