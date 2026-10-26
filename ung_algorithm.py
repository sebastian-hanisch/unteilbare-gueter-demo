"""Kern: Zuteilung unteilbarer Güter (hier: Touren auf Fahrer) bei additiven Bewertungen.

Bewertungen: Matrix `values` (n, m) ganzer Zahlen, values[i, g] = Wert der Tour g für Fahrer i. Eine Zuteilung ist ein Vektor `owner` der Länge m (owner[g] = Fahrer
der Tour g). Alle Rechnungen sind ganzzahlig, es gibt keine Rundungsfehler. Gleichstände entscheidet der kleinere Index (Fahrer, Tour, Zuteilung in der Reihenfolge von `all_allocations`).
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=None)
def all_allocations(n: int, m: int) -> np.ndarray:
    """Alle n^m Zuteilungen als Matrix (n^m, m) in der Reihenfolge von itertools.product(range(n), repeat=m): die erste Tour ist die höchstwertige Stelle."""
    index = np.arange(n**m)
    alloc = np.empty((n**m, m), dtype=np.int8)
    for g in range(m):
        alloc[:, g] = (index // n ** (m - 1 - g)) % n
    alloc.setflags(write=False)
    return alloc


def utilities(values, owner) -> np.ndarray:
    """Nutzen jedes Fahrers in einer Zuteilung (Länge n)."""
    owner = np.asarray(owner)
    return np.array([int(values[i][owner == i].sum()) for i in range(values.shape[0])])


def all_utilities(values) -> np.ndarray:
    """Nutzen aller Fahrer in allen Zuteilungen, Matrix (n^m, n)."""
    n, m = values.shape
    alloc = all_allocations(n, m)
    return np.stack([(alloc == i) @ values[i].astype(np.int64) for i in range(n)], axis=1)


# --- Regeln ----------------------------------------------------------------------------------------------------------------------------------

def round_robin(values) -> np.ndarray:
    """Fahrer 0, 1, …, n − 1, 0, 1, … wählen je eine freie Tour: die mit dem höchsten eigenen Wert (Gleichstand: kleinerer Index)."""
    n, m = values.shape
    owner = np.full(m, -1)
    free = list(range(m))
    turn = 0
    while free:
        i = turn % n
        g = max(free, key=lambda g: (values[i, g], -g))
        owner[g] = i
        free.remove(g)
        turn += 1
    return owner


def envy_cycle(values) -> np.ndarray:
    """Neidkreis-Verfahren (Lipton u. a.): Touren nach Gesamtwert fallend; jede Tour geht an einen Fahrer, den niemand beneidet.

    Beneidet jeder jemanden, folgt man den Neidern rückwärts, bis sich ein Fahrer wiederholt (ein Neidkreis), und jeder Neider im Kreis bekommt das Bündel dessen,
    den er beneidet; danach gibt es einen Fahrer ohne Neider. Neid heißt: Wert des fremden Bündels in den Augen des Neiders größer als der des eigenen."""
    n, m = values.shape
    bundles = [[] for _ in range(n)]
    order = sorted(range(m), key=lambda g: (-int(values[:, g].sum()), g))

    def value(i, bundle):
        return int(values[i, bundle].sum()) if bundle else 0

    for g in order:
        while True:
            enviers = [[j for j in range(n) if j != i and value(j, bundles[i]) > value(j, bundles[j])] for i in range(n)]
            free = [i for i in range(n) if not enviers[i]]
            if free:
                bundles[free[0]].append(g)
                break
            path = [0]
            while True:
                nxt = enviers[path[-1]][0]
                if nxt in path:
                    cycle = path[path.index(nxt):]
                    break
                path.append(nxt)
            old = [list(b) for b in bundles]
            for t in range(len(cycle)):
                bundles[cycle[(t + 1) % len(cycle)]] = old[cycle[t]]
    owner = np.full(m, -1)
    for i, bundle in enumerate(bundles):
        for g in bundle:
            owner[g] = i
    return owner


def max_nash(values, U=None) -> np.ndarray:
    """Zuteilung mit dem größten Produkt der Nutzen (bei Gleichstand die erste in der Aufzählung). Wert 1 bis 20, mindestens so viele Touren wie Fahrer: das Produkt ist positiv."""
    U = all_utilities(values) if U is None else U
    return all_allocations(*values.shape)[int(np.argmax(np.prod(U, axis=1)))].astype(int)


def leximin(values, U=None) -> np.ndarray:
    """Zuteilung mit dem größten Mindestnutzen; bei Gleichstand entscheidet der zweitkleinste Nutzen, dann der drittkleinste usw. (dann die erste in der Aufzählung)."""
    U = all_utilities(values) if U is None else U
    ordered = np.sort(U, axis=1)
    keep = np.ones(len(U), dtype=bool)
    for k in range(U.shape[1]):
        best = ordered[keep, k].max()
        keep &= ordered[:, k] == best
    return all_allocations(*values.shape)[int(np.flatnonzero(keep)[0])].astype(int)


def max_sum(values) -> np.ndarray:
    """Jede Tour geht an den Fahrer mit dem höchsten Wert (Gleichstand: kleinerer Index); Fairness spielt keine Rolle."""
    return np.argmax(values, axis=0).astype(int)


RULE_NAMES = ("reihum", "neidkreis", "nash", "leximin", "summe")


def allocate(rule, values, U=None) -> np.ndarray:
    if rule == "reihum":
        return round_robin(values)
    if rule == "neidkreis":
        return envy_cycle(values)
    if rule == "nash":
        return max_nash(values, U)
    if rule == "leximin":
        return leximin(values, U)
    if rule == "summe":
        return max_sum(values)
    raise ValueError(rule)


# --- Neid ------------------------------------------------------------------------------------------------------------------------------------

def envy_witnesses(values, owner) -> dict:
    """Prüft Neidfreiheit (ef), EF1 und EFX für eine Zuteilung und nennt je Eigenschaft den ersten Verstoß.

    Fahrer i beneidet Fahrer j, wenn er j's Bündel höher bewertet als sein eigenes. EF1: nach Entfernen EINER Tour aus j's Bündel (der wertvollsten für i) ist der Neid weg.
    EFX: nach Entfernen JEDER Tour (also auch der am wenigsten wertvollen für i) ist der Neid weg. Ein leeres Bündel wird nie beneidet.
    Rückgabe je Eigenschaft: None (erfüllt) oder (i, j, g) mit g = die entfernte Tour, nach der der Neid bleibt (bei Neid selbst: g = None)."""
    n, m = values.shape
    owner = np.asarray(owner)
    found = {"ef": None, "ef1": None, "efx": None}
    for i in range(n):
        mine = int(values[i][owner == i].sum())
        for j in range(n):
            if i == j:
                continue
            items = [int(g) for g in np.flatnonzero(owner == j)]
            theirs = sum(int(values[i, g]) for g in items)
            if mine >= theirs:
                continue
            if found["ef"] is None:
                found["ef"] = (i, j, None)
            best = max(items, key=lambda g: (int(values[i, g]), -g))           # die für i wertvollste Tour: Entfernen hilft am meisten
            if found["ef1"] is None and mine < theirs - int(values[i, best]):
                found["ef1"] = (i, j, best)
            worst = min(items, key=lambda g: (int(values[i, g]), g))           # die für i am wenigsten wertvolle Tour: Entfernen hilft am wenigsten
            if found["efx"] is None and mine < theirs - int(values[i, worst]):
                found["efx"] = (i, j, worst)
    return found


def fair_shares(values) -> dict:
    """Anteil ALLER n^m Zuteilungen, die neidfrei, EF1 beziehungsweise EFX sind (vektorisiert über alle Zuteilungen)."""
    n, m = values.shape
    alloc = all_allocations(n, m)
    val = values.astype(np.int64)
    ef = np.ones(len(alloc), dtype=bool)
    ef1 = np.ones(len(alloc), dtype=bool)
    efx = np.ones(len(alloc), dtype=bool)
    for i in range(n):
        mine = (alloc == i) @ val[i]
        for j in range(n):
            if i == j:
                continue
            has = alloc == j
            theirs = has @ val[i]
            biggest = np.where(has, val[i][None, :], 0).max(axis=1)
            smallest = np.where(has, val[i][None, :], 1 << 30).min(axis=1)
            smallest = np.where(has.any(axis=1), smallest, 0)
            ef &= mine >= theirs
            ef1 &= mine >= theirs - biggest
            efx &= mine >= theirs - smallest
    return {"ef": float(ef.mean()), "ef1": float(ef1.mean()), "efx": float(efx.mean())}


# --- Kennzahlen ------------------------------------------------------------------------------------------------------------------------------

@dataclass
class Table:
    """Einmal je Instanz gerechnet: Nutzen aller Zuteilungen und die besten Werte der drei Maße."""

    U: np.ndarray
    best_nash: int
    best_min: int
    best_sum: int


def make_table(values) -> Table:
    U = all_utilities(values)
    return Table(U=U, best_nash=int(np.prod(U, axis=1).max()), best_min=int(U.min(axis=1).max()), best_sum=int(U.sum(axis=1).max()))


def is_pareto_optimal(table: Table, u) -> bool:
    """Keine Zuteilung ist für alle Fahrer mindestens so gut und für einen echt besser."""
    u = np.asarray(u)
    return not bool(((table.U >= u).all(axis=1) & (table.U > u).any(axis=1)).any())


@dataclass(frozen=True)
class Outcome:
    owner: tuple
    utilities: tuple
    shares: tuple            # Nutzen im Verhältnis zum Gesamtwert aller Touren für den Fahrer
    witnesses: dict
    pareto: bool
    nash_ratio: float        # Produkt der Nutzen im Verhältnis zum größten Produkt
    min_ratio: float         # kleinster Nutzen im Verhältnis zum größten erreichbaren kleinsten Nutzen
    sum_ratio: float         # Summe der Nutzen im Verhältnis zur größten Summe


def evaluate(values, owner, table: Table) -> Outcome:
    u = utilities(values, owner)
    return Outcome(
        owner=tuple(int(x) for x in owner), utilities=tuple(int(x) for x in u),
        shares=tuple(float(u[i] / values[i].sum()) for i in range(values.shape[0])),
        witnesses=envy_witnesses(values, owner), pareto=is_pareto_optimal(table, u),
        nash_ratio=float(np.prod(u.astype(np.int64)) / table.best_nash), min_ratio=float(u.min() / table.best_min), sum_ratio=float(u.sum() / table.best_sum),
    )


def pareto_improvement(table: Table, u):
    """Eine Zuteilung, die alle mindestens so gut und einen echt besser stellt (die mit der größten Nutzensumme, dann die erste in der Aufzählung); None, wenn es keine gibt."""
    u = np.asarray(u)
    better = (table.U >= u).all(axis=1) & (table.U > u).any(axis=1)
    if not better.any():
        return None
    candidates = np.flatnonzero(better)
    return int(candidates[np.argmax(table.U[candidates].sum(axis=1))])
