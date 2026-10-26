"""Verdikte und Tabellen als reine Funktionen: Schwellen und jede Zahl im Text an handgesetzten Werten."""

import pytest

import ung_algorithm as A
import ung_constants as C
import ung_evaluation as ev
from conftest import vals


@pytest.fixture
def a_zwei(zwei):
    return ev.analyse_values(ev.Settings(n=2, m=3), zwei)


def test_number_formats():
    assert ev.num(3.0) == "3,0" and ev.num(1234.567, 2) == "1234,57"
    assert ev.pct(0.333) == "33 %" and ev.pct(0.0) == "0 %" and ev.pct(0.1234, 1) == "12,3 %"
    assert ev.driver(0) == "Fahrer 1" and ev.tour(2) == "T3"


def test_analysis_of_the_hand_instance(a_zwei):
    assert a_zwei.m_eff == 3
    owners = {rule: o.owner for rule, o in a_zwei.outcomes.items()}
    assert owners == {"reihum": (0, 1, 0), "neidkreis": (0, 1, 1), "nash": (0, 1, 1), "leximin": (0, 1, 1), "summe": (0, 1, 1)}
    assert a_zwei.shares == {"ef": 0.125, "ef1": 0.5, "efx": 0.25}                     # von 8 Zuteilungen: [0,1,1] neidfrei; EF1: [0,1,1], [1,0,1], [0,1,0], [1,0,0]; EFX: [0,1,1], [1,0,0]
    assert ev.holds(a_zwei, "nash", "ef") and not ev.holds(a_zwei, "reihum", "efx") and ev.holds(a_zwei, "reihum", "ef1")


def test_analyse_uses_the_effective_tour_count():
    a = ev.analyse(ev.Settings(n=5, m=10, seed=1))
    assert a.m_eff == 7 and a.values.shape == (5, 7)
    assert ev.analyse(ev.Settings(n=6, m=5, seed=1)).m_eff == 6                                     # mindestens so viele Touren wie Fahrer


def test_rule_rows_by_hand(a_zwei):
    rows = {r["Regel"]: r for r in ev.rule_rows(a_zwei)}
    assert list(rows) == list(C.RULES.values())
    r = rows[C.RULES["reihum"]]
    assert r["Nutzen je Fahrer"] == "14 / 7" and r["Kleinster Anteil am Gesamtwert"] == "35 %"
    assert (r["Neidfrei"], r["EF1"], r["EFX"], r["Pareto-optimal"]) == ("verletzt", "erfüllt", "verletzt", "ja")
    assert r["Nash-Wohlfahrt"] == "82 %" and r["Summe der Nutzen"] == "95 %"
    n = rows[C.RULES["nash"]]
    assert n["Nutzen je Fahrer"] == "10 / 12" and (n["Neidfrei"], n["EF1"], n["EFX"]) == ("erfüllt", "erfüllt", "erfüllt") and n["Nash-Wohlfahrt"] == "100 %"


def test_witness_lines_by_hand(a_zwei):
    lines = ev.witness_lines(a_zwei)
    assert lines == ["**Reihum, EFX:** Fahrer 2 bewertet sein Bündel mit 7, das von Fahrer 1 mit 13; auch nach Entfernen der Tour T3 (Wert 5 für Fahrer 2) bleibt der Neid (8 gegen 7)."]


def test_witness_lines_name_ef1_before_efx_and_non_pareto_rules():
    v = vals([5, 5, 1], [1, 1, 9])
    a = ev.analyse_values(ev.Settings(n=2, m=3), v)
    table = a.table
    a.outcomes["summe"] = A.evaluate(v, [1, 1, 1], table)                         # F1 hat nichts: EF1 verletzt (wertvollste Tour T1 weg: 6 > 0)
    a.outcomes["reihum"] = A.evaluate(v, [1, 0, 0], table)                        # (6, 1) lässt sich zu (10, 9) verbessern, F2 bekommt nur 1
    lines = ev.witness_lines(a)
    assert any(line.startswith("**Größte Summe, EF1:** Fahrer 1 bewertet sein Bündel mit 0, das von Fahrer 2 mit 11;") and "Entfernen der Tour T1 (Wert 5 für Fahrer 1) bleibt der Neid (6 gegen 0)" in line for line in lines)
    assert any(line.startswith("**Reihum, nicht Pareto-optimal:** die Nutzen 6 / 1 lassen sich auf 10 / 9 verbessern") for line in lines)


def test_verdict_state_by_hand(a_zwei):
    kind, text = ev.verdict_state(a_zwei)
    assert kind == "warning"
    assert text.startswith("2 Fahrer, 3 Touren: Von allen 8 Zuteilungen erfüllen 50 % EF1 und 25 % EFX, 12,5 % sind neidfrei. ")
    assert "EF1 erfüllen: Reihum, Neidkreis, Nash-Wohlfahrt, Leximin, Größte Summe. EFX erfüllen: Neidkreis, Nash-Wohlfahrt, Leximin, Größte Summe. Pareto-optimal sind: Reihum, Neidkreis, Nash-Wohlfahrt, Leximin, Größte Summe. " in text
    assert text.endswith("Die Nash-Wohlfahrt erreicht der Neidkreis zu 100 %, Reihum zu 82 %, Leximin zu 100 % des Größtmöglichen.")


def test_verdict_state_formats_thousands_with_a_dot_and_keeps_decimal_commas():
    kind, text = ev.verdict_state(ev.analyse(ev.Settings()))
    assert "Von allen 19.683 Zuteilungen" in text and "0,6 % sind neidfrei" in text and "3 Fahrer, 9 Touren:" in text


def test_verdict_state_is_info_when_the_four_fair_rules_satisfy_efx():
    v = vals([5, 1], [1, 5])
    kind, text = ev.verdict_state(ev.analyse_values(ev.Settings(n=2, m=2), v))
    assert kind == "info" and "EFX erfüllen: Reihum, Neidkreis, Nash-Wohlfahrt, Leximin, Größte Summe." in text


def _rows(param, xs, **by_rule):
    rows = []
    for i, x in enumerate(xs):
        for rule in C.RULES:
            base = {"ef": 0.5, "ef1": 1.0, "efx": 0.9, "po": 0.8, "nash": 0.9, "min": 0.9, "sum": 0.9, "share": 0.4}
            base.update({k: v[i] for k, v in by_rule.get(rule, {}).items()})
            rows.append({"param": param, "x": x, "rule": rule, "runs": 150, **base})
    return rows


def test_series_rows_and_labels():
    rows = _rows("model", tuple(C.MODELS), nash={"efx": [0.99, 0.93, 1.0]})
    table = ev.series_rows(rows, "efx")
    assert [r["Geschmacksmodell"] for r in table] == ["Unabhängig", "Ähnlich", "Spezialisten"]
    assert table[0]["Nash-Wohlfahrt"] == "99 %" and table[1]["Nash-Wohlfahrt"] == "93 %" and table[2]["Reihum"] == "90 %"
    assert list(ev.series_rows(_rows("m", (4, 5)), "efx")[0])[0] == "Touren" and list(ev.series_rows(_rows("n", (2,)), "efx")[0])[0] == "Fahrer"
    assert ev.cell_of(rows, "aehnlich", "nash")["efx"] == 0.93
    assert ev.x_label("m", 7) == "7" and ev.x_label("model", "aehnlich") == "Ähnlich"


def test_verdict_models_by_hand():
    rows = _rows("model", tuple(C.MODELS), nash={"efx": [0.99, 0.93, 1.0]}, reihum={"po": [0.69, 0.41, 0.83]}, leximin={"ef1": [0.99, 1.0, 0.85]})
    kind, text = ev.verdict_models(rows)
    assert kind == "info"
    assert text.startswith("Mittel über 150 Instanzen (3 Fahrer, 9 Touren). Unabhängig: Nash-Wohlfahrt EFX 99 %, Reihum Pareto-optimal 69 %, Leximin EF1 99 %;")
    assert "Spezialisten: Nash-Wohlfahrt EFX 100 %, Reihum Pareto-optimal 83 %, Leximin EF1 85 %." in text


def test_verdict_goods_by_hand():
    rows = _rows("m", (4, 9), nash={"efx": [0.89, 0.99], "ef": [0.35, 0.87]}, reihum={"efx": [0.55, 0.95]}, neidkreis={"efx": [0.83, 0.57]})
    kind, text = ev.verdict_goods(rows)
    assert kind == "info"
    assert text == ("Bei 4 bzw. 9 Touren erfüllen EFX: Nash-Wohlfahrt 89 % bzw. 99 %, Reihum 55 % bzw. 95 %, Neidkreis 83 % bzw. 57 %. Neidfrei ist die Nash-Wohlfahrt bei 35 % bzw. 87 % der Instanzen.")


def test_verdict_drivers_by_hand():
    rows = _rows("n", (2, 5), nash={"efx": [0.99, 0.81], "ef": [0.95, 0.03]})
    kind, text = ev.verdict_drivers(rows)
    assert kind == "info" and text.startswith("Bei 5 Fahrern (7 Touren, 150 Instanzen): Reihum EFX 90 %, neidfrei 50 %;")
    assert "Nash-Wohlfahrt EFX 81 %, neidfrei 3 %" in text


def test_cells_are_reproducible_and_bounded():
    a = ev._cell(3, 6, "unabhaengig", runs=5, seed=7)
    assert a == ev._cell(3, 6, "unabhaengig", runs=5, seed=7) and set(a) == set(C.RULES)
    assert a["nash"]["ef1"] == 1.0 and a["nash"]["po"] == 1.0 and a["nash"]["nash"] == 1.0
    assert all(0.0 <= v <= 1.0 for d in a.values() for v in d.values())
