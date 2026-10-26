"""Kern von Hand: jede Regel und jede Prüfung an Mini-Instanzen, mit der Rechnung im Kommentar."""

import itertools

import numpy as np
import pytest

import ung_algorithm as A
from conftest import vals


def test_all_allocations_in_product_order():
    alloc = A.all_allocations(3, 4)
    assert alloc.shape == (81, 4) and alloc.tolist() == [list(t) for t in itertools.product(range(3), repeat=4)]
    assert A.all_allocations(2, 3)[1].tolist() == [0, 0, 1] and A.all_allocations(2, 3)[6].tolist() == [1, 1, 0]
    assert not alloc.flags.writeable


def test_utilities_by_hand(zwei):
    assert A.utilities(zwei, [0, 1, 1]).tolist() == [10, 12]          # F1: T1 = 10; F2: T2 + T3 = 7 + 5
    assert A.utilities(zwei, [0, 1, 0]).tolist() == [14, 7]
    U = A.all_utilities(zwei)
    assert U.shape == (8, 2) and U[int("011", 2)].tolist() == [10, 12] and U[0].tolist() == [20, 0] and U[7].tolist() == [0, 20]


def test_round_robin_by_hand(zwei):
    # F1 wählt T1 (10), F2 wählt T2 (7: mehr als T3 mit 5), F1 bekommt T3
    assert A.round_robin(zwei).tolist() == [0, 1, 0]
    assert A.round_robin(vals([5, 5, 5], [5, 5, 5])).tolist() == [0, 1, 0]       # alles gleich: kleinerer Index zuerst
    # drei Fahrer, vier Touren: F1 nimmt T1 (9), F2 nimmt T2 (8), F3 nimmt T3 (7), F1 nimmt die letzte (T4)
    assert A.round_robin(vals([9, 1, 1, 1], [1, 8, 1, 1], [1, 1, 7, 1])).tolist() == [0, 1, 2, 0]


def test_max_sum_by_hand(zwei):
    assert A.max_sum(zwei).tolist() == [0, 1, 1]                 # T1: 10 > 8, T2: 7 > 6, T3: 5 > 4
    assert A.max_sum(vals([5, 5], [5, 5])).tolist() == [0, 0]    # Gleichstand: kleinerer Index


def test_max_nash_by_hand(zwei):
    # F1 bekommt S, F2 den Rest. Produkte: {} 0, {T1} 10 · 12 = 120, {T2} 6 · 13 = 78, {T3} 4 · 15 = 60, {T1,T2} 16 · 5 = 80, {T1,T3} 14 · 7 = 98, {T2,T3} 10 · 8 = 80, alle 0 -> 120
    assert A.max_nash(zwei).tolist() == [0, 1, 1]
    assert A.max_nash(vals([5, 5], [5, 5])).tolist() == [0, 1]   # [0, 1] und [1, 0] gleich gut: die erste in der Aufzählung


def test_leximin_by_hand(zwei):
    # kleinste Nutzen je Zuteilung: {T1} 10, {T1,T2} 5, {T1,T3} 7, {T2,T3} 8, {T2} 6, {T3} 4 -> {T1} mit (10, 12)
    assert A.leximin(zwei).tolist() == [0, 1, 1]
    assert A.leximin(vals([5, 5], [5, 5])).tolist() == [0, 1]


def test_leximin_breaks_ties_by_the_second_smallest():
    # [[1,1,1],[1,3,2]]: F1 bekommt {T1,T2}: (2, 2), {T1,T3}: (2, 3), {T2,T3}: (2, 1) mit Mindestnutzen 1. Mindestnutzen 2 haben (2, 2) und (2, 3);
    # die erste in der Aufzählung ist [0, 0, 1] mit (2, 2), Leximin wählt wegen des größeren zweitkleinsten Nutzens (2, 3): [0, 1, 0]
    assert A.leximin(vals([1, 1, 1], [1, 3, 2])).tolist() == [0, 1, 0]
    # vollständiger Gleichstand: die erste in der Aufzählung ([0, 0, 1] kommt vor [0, 1, 1]), beide haben (4, 8)
    assert A.leximin(vals([4, 4, 4], [4, 4, 4])).tolist() == [0, 0, 1]
    # F1 [6, 2, 2], F2 [3, 3, 9]: Zuteilung {T1, T2} / {T3} gibt (8, 9); alle anderen haben einen kleineren Mindestnutzen
    assert A.leximin(vals([6, 2, 2], [3, 3, 9])).tolist() == [0, 0, 1]


def test_allocate_dispatches_and_rejects_unknown_rules(zwei):
    for rule in A.RULE_NAMES:
        assert A.allocate(rule, zwei).tolist() == {"reihum": [0, 1, 0]}.get(rule, [0, 1, 1])
    with pytest.raises(ValueError):
        A.allocate("x", zwei)


def test_envy_cycle_by_hand():
    # [[1,1,2],[1,2,1]]: Gesamtwerte T1 2, T2 3, T3 3 -> Reihenfolge T2, T3, T1.
    # T2 -> F1; T3 -> F2 (F1 beneidet niemanden, F2 beneidet F1: F2 hat keinen Neider); T1: F1 beneidet F2 ({T3} = 2 > 1) und F2 beneidet F1 ({T2} = 2 > 1): Neidkreis (F1, F2).
    # F2 bekommt {T2}, F1 bekommt {T3}; jetzt beneidet keiner, T1 -> F1. Ergebnis: F1 {T1, T3}, F2 {T2}.
    assert A.envy_cycle(vals([1, 1, 2], [1, 2, 1])).tolist() == [0, 1, 0]


def test_envy_cycle_without_a_cycle(zwei):
    assert A.envy_cycle(zwei).tolist() == [0, 1, 1]              # T1 -> F1, T2 -> F2 (F1 beneidet F2 nicht), T3 -> F2 (niemand beneidet F2)


def test_envy_witnesses_by_hand_for_round_robin(zwei):
    w = A.envy_witnesses(zwei, [0, 1, 0])
    # F2 hat 7, bewertet F1s Bündel {T1, T3} mit 8 + 5 = 13: Neid. EF1: ohne T1 (8) bleiben 5 ≤ 7 -> erfüllt. EFX: ohne T3 (5) bleiben 8 > 7 -> verletzt.
    assert w == {"ef": (1, 0, None), "ef1": None, "efx": (1, 0, 2)}
    assert A.envy_witnesses(zwei, [0, 1, 1]) == {"ef": None, "ef1": None, "efx": None}


def test_ef1_violation_by_hand():
    # F1 hat nichts, F2 hat zwei Touren, die F1 je mit 5 bewertet: Entfernen einer Tour lässt 5 > 0 übrig
    v = vals([5, 5], [1, 1])
    assert A.envy_witnesses(v, [1, 1]) == {"ef": (0, 1, None), "ef1": (0, 1, 0), "efx": (0, 1, 0)}


def test_nobody_envies_an_empty_bundle():
    v = vals([5, 5], [1, 1])
    assert A.envy_witnesses(v, [0, 0]) == {"ef": (1, 0, None), "ef1": (1, 0, 0), "efx": (1, 0, 0)}      # F2 hat nichts und beneidet das Bündel von F1
    assert A.envy_witnesses(vals([5], [1]), [0]) == {"ef": (1, 0, None), "ef1": None, "efx": None}      # ein einzelnes Gut: Entfernen beseitigt jeden Neid


def test_fair_shares_by_hand():
    # [[3, 1], [1, 3]]: [0,0] (4, 0), [0,1] (3, 3) neidfrei, [1,0] (1, 1) EF1 und EFX (jedes Bündel hat eine Tour), [1,1] (0, 4): nur [0,1] neidfrei, [0,1] und [1,0] EF1 und EFX
    assert A.fair_shares(vals([3, 1], [1, 3])) == {"ef": 0.25, "ef1": 0.5, "efx": 0.5}


def test_pareto_by_hand():
    v = vals([10, 1], [1, 10])
    table = A.make_table(v)
    assert A.is_pareto_optimal(table, [10, 10]) and not A.is_pareto_optimal(table, [1, 1])
    assert A.pareto_improvement(table, [1, 1]) == 1                    # die Zuteilung [0, 1] mit (10, 10)
    assert A.pareto_improvement(table, [10, 10]) is None


def test_table_by_hand(zwei):
    t = A.make_table(zwei)
    assert t.best_nash == 120 and t.best_min == 10 and t.best_sum == 22


def test_evaluate_by_hand(zwei):
    t = A.make_table(zwei)
    o = A.evaluate(zwei, [0, 1, 0], t)
    assert o.owner == (0, 1, 0) and o.utilities == (14, 7) and o.pareto
    assert o.shares == (14 / 20, 7 / 20)
    assert o.nash_ratio == 98 / 120 and o.min_ratio == 7 / 10 and o.sum_ratio == 21 / 22
    assert o.witnesses["efx"] == (1, 0, 2)
