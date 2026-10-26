"""Orakel-Test unteilbare-gueter-demo: jede Regel und jede Prüfung gegen einen ANDEREN Rechenweg.

* Aufzählung: itertools.product statt Stellenwertrechnung.
* Größte Nash-Wohlfahrt, Leximin, größte Summe: reine Python-Schleifen über alle Zuteilungen (Listen, Produkte aus ganzen Zahlen, sortierte Tupel).
* Neid, EF1, EFX: die Definition wörtlich, mit Listen von Touren und der Wegnahme jeder einzelnen Tour.
* Pareto-Optimalität: paarweiser Vergleich aller Zuteilungen in Python.
* Anteil der neidfreien, EF1- und EFX-Zuteilungen: Zählen über alle Zuteilungen mit den wörtlichen Definitionen.
* Reihum und Neidkreis: die bekannten Sätze (beide liefern EF1) als Eigenschaftstests; die Größte Nash-Wohlfahrt liefert EF1 und ist Pareto-optimal (Caragiannis u. a. 2019).
"""

import itertools

import numpy as np
import pytest

import ung_algorithm as A
import ung_constants as C
import ung_scenario as S


def random_values(seed, n_range=(2, 4), m_range=(2, 6)):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(*n_range, endpoint=True))
    m = int(rng.integers(max(n, m_range[0]), m_range[1], endpoint=True))
    return rng.integers(1, 21, size=(n, m))


# --- Aufzählung und Wahl über alle Zuteilungen -----------------------------------------------------------------------------------------------

def naive_utilities(values, owner):
    n, m = values.shape
    return [sum(int(values[i][g]) for g in range(m) if owner[g] == i) for i in range(n)]


def naive_rules(values):
    n, m = values.shape
    allocs = list(itertools.product(range(n), repeat=m))
    nash = max(allocs, key=lambda o: np.prod([int(x) for x in naive_utilities(values, o)]))
    leximin = max(allocs, key=lambda o: tuple(sorted(naive_utilities(values, o))))
    total = tuple(max(range(n), key=lambda i: (int(values[i][g]), -i)) for g in range(m))
    return {"nash": nash, "leximin": leximin, "summe": total}, allocs


@pytest.mark.parametrize("seed", range(120))
def test_enumeration_rules_match_plain_python(seed):
    values = random_values(seed)
    want, allocs = naive_rules(values)
    assert [tuple(a) for a in A.all_allocations(*values.shape).tolist()] == allocs
    for rule, owner in want.items():
        assert tuple(A.allocate(rule, values).tolist()) == owner, (seed, rule)
    U = A.all_utilities(values)
    assert [naive_utilities(values, o) for o in allocs] == U.tolist()


# --- Neid nach der Definition ----------------------------------------------------------------------------------------------------------------

def naive_envy(values, owner):
    """Neidfrei, EF1, EFX wörtlich: Bündel als Listen, jede Tour einzeln weggenommen."""
    n, m = values.shape
    bundles = [[g for g in range(m) if owner[g] == j] for j in range(n)]
    ef = ef1 = efx = True
    for i in range(n):
        mine = sum(int(values[i][g]) for g in bundles[i])
        for j in range(n):
            if i == j:
                continue
            theirs = sum(int(values[i][g]) for g in bundles[j])
            if mine >= theirs:
                continue
            ef = False
            if not any(mine >= theirs - int(values[i][g]) for g in bundles[j]):
                ef1 = False
            if not all(mine >= theirs - int(values[i][g]) for g in bundles[j]):
                efx = False
    return {"ef": ef, "ef1": ef1, "efx": efx}


@pytest.mark.parametrize("seed", range(120))
def test_envy_checks_match_the_definition_on_random_allocations(seed):
    values = random_values(seed, n_range=(2, 5), m_range=(2, 8))
    n, m = values.shape
    rng = np.random.default_rng(500 + seed)
    owners = [rng.integers(0, n, size=m) for _ in range(8)] + [A.allocate(rule, values) for rule in C.RULES]
    for owner in owners:
        got = A.envy_witnesses(values, owner)
        assert {k: v is None for k, v in got.items()} == naive_envy(values, owner), (seed, owner.tolist())


def test_the_envy_oracle_is_not_vacuous():
    """Von jeder Eigenschaft gibt es unter den geprüften Zuteilungen erfüllte und verletzte Fälle (sonst wäre die Gleichheit mit der Demo leer)."""
    held = {"ef": 0, "ef1": 0, "efx": 0}
    total = 0
    for seed in range(120):
        values = random_values(seed, n_range=(2, 5), m_range=(2, 8))
        n, m = values.shape
        rng = np.random.default_rng(500 + seed)
        for owner in [rng.integers(0, n, size=m) for _ in range(8)] + [A.allocate(rule, values) for rule in C.RULES]:
            found = naive_envy(values, owner)
            for k in held:
                held[k] += found[k]
            total += 1
    assert all(0.05 * total < c < 0.95 * total for c in held.values()), (held, total)


@pytest.mark.parametrize("seed", range(60))
def test_witness_details_are_correct(seed):
    values = random_values(seed, n_range=(2, 4), m_range=(3, 7))
    n, m = values.shape
    rng = np.random.default_rng(900 + seed)
    for owner in [rng.integers(0, n, size=m) for _ in range(6)]:
        w = A.envy_witnesses(values, owner)
        for key, hit in w.items():
            if hit is None:
                continue
            i, j, g = hit
            mine = int(values[i][owner == i].sum())
            theirs = int(values[i][owner == j].sum())
            assert theirs > mine
            if key != "ef":
                assert owner[g] == j and mine < theirs - int(values[i, g])


# --- Pareto-Optimalität und Anteile aller Zuteilungen ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("seed", range(60))
def test_pareto_matches_pairwise_comparison(seed):
    values = random_values(seed, n_range=(2, 4), m_range=(2, 5))
    table = A.make_table(values)
    allocs = list(itertools.product(range(values.shape[0]), repeat=values.shape[1]))
    utils = [naive_utilities(values, o) for o in allocs]
    rng = np.random.default_rng(300 + seed)
    for _ in range(8):
        k = int(rng.integers(0, len(allocs)))
        u = utils[k]
        dominated = any(all(x >= y for x, y in zip(w, u)) and any(x > y for x, y in zip(w, u)) for w in utils)
        assert A.is_pareto_optimal(table, u) == (not dominated)
        better = A.pareto_improvement(table, u)
        assert (better is None) == (not dominated)
        if better is not None:
            w = table.U[better].tolist()
            assert all(x >= y for x, y in zip(w, u)) and any(x > y for x, y in zip(w, u))


@pytest.mark.parametrize("seed", range(40))
def test_fair_shares_match_counting_all_allocations(seed):
    values = random_values(seed, n_range=(2, 4), m_range=(2, 5))
    allocs = list(itertools.product(range(values.shape[0]), repeat=values.shape[1]))
    found = [naive_envy(values, o) for o in allocs]
    got = A.fair_shares(values)
    for key in ("ef", "ef1", "efx"):
        assert got[key] == pytest.approx(sum(f[key] for f in found) / len(allocs)), (seed, key)


# --- Sätze aus der Literatur als Eigenschaftstests -------------------------------------------------------------------------------------------

def is_complete(owner, n, m):
    return len(owner) == m and all(0 <= int(o) < n for o in owner)


@pytest.mark.parametrize("seed", range(200))
def test_round_robin_envy_cycle_and_nash_satisfy_ef1_and_every_rule_assigns_each_tour_once(seed):
    values = random_values(seed, n_range=(2, 5), m_range=(2, 8))
    n, m = values.shape
    for rule in C.RULES:
        assert is_complete(A.allocate(rule, values), n, m), (seed, rule)
    for rule in ("reihum", "neidkreis", "nash"):
        assert A.envy_witnesses(values, A.allocate(rule, values))["ef1"] is None, (seed, rule)


@pytest.mark.parametrize("seed", range(120))
def test_max_nash_is_pareto_optimal_and_leximin_and_sum_too(seed):
    values = random_values(seed, n_range=(2, 4), m_range=(2, 6))
    table = A.make_table(values)
    for rule in ("nash", "leximin", "summe"):
        assert A.is_pareto_optimal(table, A.utilities(values, A.allocate(rule, values, table.U))), (seed, rule)


def test_the_property_tests_are_not_vacuous():
    """Es gibt Instanzen, in denen Reihum und Neidkreis nicht Pareto-optimal sind, Reihum EFX verletzt und Leximin EF1 verletzt: sonst prüften die Sätze oben nichts Unterscheidendes."""
    seen = {"reihum_not_po": 0, "neid_not_po": 0, "reihum_not_efx": 0, "leximin_not_ef1": 0}
    for seed in range(300):
        values = random_values(seed, n_range=(3, 4), m_range=(6, 8))
        table = A.make_table(values)
        out = {rule: A.evaluate(values, A.allocate(rule, values, table.U), table) for rule in ("reihum", "neidkreis", "leximin")}
        seen["reihum_not_po"] += not out["reihum"].pareto
        seen["neid_not_po"] += not out["neidkreis"].pareto
        seen["reihum_not_efx"] += out["reihum"].witnesses["efx"] is not None
        seen["leximin_not_ef1"] += out["leximin"].witnesses["ef1"] is not None
    assert all(v >= 3 for v in seen.values()), seen


@pytest.mark.parametrize("model", list(C.MODELS))
def test_models_produce_values_in_range_and_fixed_by_the_seed(model):
    a = S.make_values(4, 8, model, 3)
    assert a.shape == (4, 8) and a.min() >= C.VALUE_MIN and a.max() <= C.VALUE_MAX
    assert (a == S.make_values(4, 8, model, 3)).all() and not (a == S.make_values(4, 8, model, 4)).all()
