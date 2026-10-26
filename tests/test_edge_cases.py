"""Randfälle: Extremwerte der Regler, Invarianten jeder Zuteilung, entartete Bewertungen."""

import numpy as np
import pytest

import ung_algorithm as A
import ung_constants as C
import ung_evaluation as ev
import ung_scenario as S
from conftest import vals

EXTREMES = [(n, m, model) for n in (C.N_MIN, 4, C.N_MAX) for m in (C.M_MIN, C.M_MAX) for model in C.MODELS]


@pytest.mark.parametrize("n,m,model", EXTREMES)
def test_invariants_at_the_extremes(n, m, model):
    a = ev.analyse(ev.Settings(n=n, m=m, model=model, seed=2))
    m_eff = S.effective_m(n, m)
    assert a.m_eff == m_eff and a.values.shape == (n, m_eff) and m_eff >= n
    assert a.values.min() >= C.VALUE_MIN and a.values.max() <= C.VALUE_MAX
    for rule, o in a.outcomes.items():
        assert len(o.owner) == m_eff and all(0 <= x < n for x in o.owner), rule
        assert sum(o.utilities) == sum(int(a.values[o.owner[g], g]) for g in range(m_eff))
        assert 0.0 <= o.nash_ratio <= 1.0 and 0.0 <= o.min_ratio <= 1.0 and 0.0 <= o.sum_ratio <= 1.0 and all(0.0 <= s <= 1.0 for s in o.shares)
        ef, ef1, efx = (o.witnesses[k] is None for k in ("ef", "ef1", "efx"))
        assert (not ef) or efx and ef1                                   # neidfrei -> EFX -> EF1
        assert (not efx) or ef1
    assert a.outcomes["nash"].nash_ratio == 1.0 and a.outcomes["leximin"].min_ratio == 1.0 and a.outcomes["summe"].sum_ratio == 1.0
    assert a.outcomes["nash"].witnesses["ef1"] is None and a.outcomes["nash"].pareto
    assert 0.0 <= a.shares["ef"] <= a.shares["efx"] <= a.shares["ef1"] <= 1.0
    kind, text = ev.verdict_state(a)
    assert kind in ("warning", "info") and text
    assert len(ev.rule_rows(a)) == len(C.RULES)
    ev.witness_lines(a)


def test_effective_m_limits_and_floors():
    assert S.effective_m(3, 10) == 10 and S.effective_m(4, 10) == 8 and S.effective_m(5, 10) == 7 and S.effective_m(6, 10) == 6 and S.effective_m(2, 5) == 5
    assert S.effective_m(6, 5) == 6 and S.effective_m(5, 5) == 5


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        S.make_values(3, 5, "x", 1)


def test_models_have_their_signature():
    unabh = S.make_values(3, 10, "unabhaengig", 1)
    aehnl = S.make_values(3, 10, "aehnlich", 1)
    spez = S.make_values(4, 12, "spezialisten", 1)
    assert aehnl.std(axis=0).mean() < unabh.std(axis=0).mean()                       # ähnliche Geschmäcker: die Spalten (Touren) unterscheiden sich wenig zwischen Fahrern
    assert ((spez >= 13).sum(axis=0) == 1).all()                                      # genau ein Lieblingsfahrer je Tour
    assert (spez[spez < 13] <= 8).all()


def test_all_values_equal_every_rule_still_gives_a_complete_allocation():
    v = np.full((3, 6), 7)
    table = A.make_table(v)
    for rule in A.RULE_NAMES:
        o = A.evaluate(v, A.allocate(rule, v, table.U), table)
        assert sorted(o.owner) in ([0, 0, 1, 1, 2, 2], [0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 2], [0, 0, 0, 0, 1, 2]) or len(o.owner) == 6
    assert A.max_nash(v).tolist() == [0, 0, 1, 1, 2, 2] and A.leximin(v).tolist() == [0, 0, 1, 1, 2, 2]       # gleich viele Touren je Fahrer, die erste in der Aufzählung
    assert A.round_robin(v).tolist() == [0, 1, 2, 0, 1, 2]
    assert A.envy_witnesses(v, [0, 0, 1, 1, 2, 2]) == {"ef": None, "ef1": None, "efx": None}


def test_as_many_tours_as_drivers():
    v = vals([9, 1, 1], [1, 9, 1], [1, 1, 9])
    for rule in ("reihum", "nash", "leximin", "neidkreis"):
        assert A.allocate(rule, v).tolist() == [0, 1, 2], rule              # jeder bekommt „seine“ Tour
    assert A.max_sum(v).tolist() == [0, 1, 2]


def test_one_tour_cannot_be_split():
    v = vals([5], [5])
    w = A.envy_witnesses(v, [0])
    assert w["ef"] == (1, 0, None) and w["ef1"] is None and w["efx"] is None        # Neid bleibt, aber nach Wegnahme der einen Tour nicht mehr
    assert A.fair_shares(v) == {"ef": 0.0, "ef1": 1.0, "efx": 1.0}


def test_value_of_one_tour_dominates():
    v = vals([20, 1, 1], [20, 1, 1])
    o = A.evaluate(v, A.max_nash(v), A.make_table(v))
    assert o.owner[0] in (0, 1) and set(o.owner) == {0, 1}
    assert o.witnesses["ef1"] is None


def test_envy_cycle_terminates_with_many_equal_goods():
    v = np.full((4, 8), 5)
    assert A.envy_cycle(v).tolist().count(0) == 2                              # gleich verteilt
    v = np.tile(np.arange(1, 9), (4, 1))
    owner = A.envy_cycle(v)
    assert sorted(set(owner.tolist())) == [0, 1, 2, 3] and A.envy_witnesses(v, owner)["ef1"] is None
