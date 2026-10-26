"""Auswertung: Einstellungen, Analyse einer Instanz, Tabellen, Verdikte als reine Funktionen (ohne Streamlit) und die festen Messreihen."""

from dataclasses import dataclass

import numpy as np

import ung_algorithm as A
import ung_constants as C
from ung_scenario import effective_m, make_values

PROPERTIES = {"ef": "Neidfrei", "ef1": "EF1", "efx": "EFX"}


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 0) -> str:
    return f"{100 * x:.{digits}f} %".replace(".", ",")


def short_rule(rule: str) -> str:
    return C.RULE_SHORT[rule]


def driver(i: int) -> str:
    return f"Fahrer {i + 1}"


def tour(g: int) -> str:
    return f"T{g + 1}"


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    m: int = C.DEFAULT_M
    model: str = C.DEFAULT_MODEL
    seed: int = C.DEFAULT_SEED


@dataclass
class Analysis:
    settings: Settings
    m_eff: int
    values: np.ndarray
    table: A.Table
    outcomes: dict      # Regel -> Outcome
    shares: dict        # Anteil aller Zuteilungen mit Neidfreiheit, EF1, EFX


def analyse(settings: Settings) -> Analysis:
    m_eff = effective_m(settings.n, settings.m)
    return analyse_values(settings, make_values(settings.n, m_eff, settings.model, settings.seed))


def analyse_values(settings: Settings, values: np.ndarray) -> Analysis:
    """Alle Regeln und Kennzahlen auf gegebenen Bewertungen (die Tests reichen handgebaute Werte herein)."""
    table = A.make_table(values)
    outcomes = {rule: A.evaluate(values, A.allocate(rule, values, table.U), table) for rule in C.RULES}
    return Analysis(settings=settings, m_eff=values.shape[1], values=values, table=table, outcomes=outcomes, shares=A.fair_shares(values))


def holds(a: Analysis, rule: str, key: str) -> bool:
    return a.outcomes[rule].witnesses[key] is None


def rule_rows(a: Analysis) -> list[dict]:
    """Zeilen für st.table: je Regel eine Zeile."""
    rows = []
    for rule in C.RULES:
        o = a.outcomes[rule]
        row = {"Regel": C.RULES[rule], "Nutzen je Fahrer": " / ".join(str(u) for u in o.utilities), "Kleinster Anteil am Gesamtwert": pct(min(o.shares))}
        for key, name in PROPERTIES.items():
            row[name] = "erfüllt" if holds(a, rule, key) else "verletzt"
        row["Pareto-optimal"] = "ja" if o.pareto else "nein"
        row["Nash-Wohlfahrt"] = pct(o.nash_ratio)
        row["Summe der Nutzen"] = pct(o.sum_ratio)
        rows.append(row)
    return rows


def witness_lines(a: Analysis) -> list[str]:
    """Je Regel mit verletztem EFX (oder EF1) ein Beispiel in Worten, dazu je Regel ohne Pareto-Optimalität eine Verbesserung für alle."""
    lines = []
    v = a.values
    for rule in C.RULES:
        o = a.outcomes[rule]
        for key in ("ef1", "efx"):
            w = o.witnesses[key]
            if w is None:
                continue
            i, j, g = w
            mine = int(v[i][np.array(o.owner) == i].sum())
            theirs = int(v[i][np.array(o.owner) == j].sum())
            lines.append(
                f"**{short_rule(rule)}, {PROPERTIES[key]}:** {driver(i)} bewertet sein Bündel mit {mine}, das von {driver(j)} mit {theirs}; auch nach Entfernen der Tour {tour(g)} "
                f"(Wert {int(v[i, g])} für {driver(i)}) bleibt der Neid ({theirs - int(v[i, g])} gegen {mine})."
            )
            break
        if not o.pareto:
            idx = A.pareto_improvement(a.table, o.utilities)
            better = tuple(int(x) for x in a.table.U[idx])
            lines.append(f"**{short_rule(rule)}, nicht Pareto-optimal:** die Nutzen {' / '.join(map(str, o.utilities))} lassen sich auf {' / '.join(map(str, better))} verbessern, ohne dass ein Fahrer verliert.")
    return lines


def verdict_state(a: Analysis) -> tuple[str, str]:
    """Verdikt für die Einstellungen: welche Regeln EF1 und EFX erfüllen, welche Pareto-optimal sind, und wie weit Neidkreis und Reihum von der größten Nash-Wohlfahrt entfernt sind."""
    names = lambda ok: [short_rule(r) for r in C.RULES if ok(r)]
    ef1 = names(lambda r: holds(a, r, "ef1"))
    efx = names(lambda r: holds(a, r, "efx"))
    po = names(lambda r: a.outcomes[r].pareto)
    total = f"{a.settings.n ** a.m_eff:,}".replace(",", ".")
    text = (f"{a.settings.n} Fahrer, {a.m_eff} Touren: Von allen {total} Zuteilungen erfüllen {pct(a.shares['ef1'])} EF1 und {pct(a.shares['efx'])} EFX, {pct(a.shares['ef'], 1)} sind neidfrei. "
            + f"EF1 erfüllen: {', '.join(ef1) or 'keine Regel'}. EFX erfüllen: {', '.join(efx) or 'keine Regel'}. Pareto-optimal sind: {', '.join(po) or 'keine Regel'}. "
            + f"Die Nash-Wohlfahrt erreicht der Neidkreis zu {pct(a.outcomes['neidkreis'].nash_ratio)}, Reihum zu {pct(a.outcomes['reihum'].nash_ratio)}, Leximin zu {pct(a.outcomes['leximin'].nash_ratio)} des Größtmöglichen.")
    fair = ("reihum", "neidkreis", "nash", "leximin")
    return ("warning" if any(not holds(a, r, "efx") for r in fair) else "info"), text


# --- feste Messreihen -------------------------------------------------------------------------------------------------------------------------

def _cell(n: int, m: int, model: str, runs: int, seed: int) -> dict:
    """Anteil der Instanzen mit Neidfreiheit, EF1, EFX und Pareto-Optimalität sowie Mittelwerte der drei Verhältnisse je Regel."""
    acc = {rule: {"ef": 0, "ef1": 0, "efx": 0, "po": 0, "nash": [], "min": [], "sum": [], "share": []} for rule in C.RULES}
    for s in range(runs):
        values = make_values(n, m, model, seed + s)
        table = A.make_table(values)
        for rule in C.RULES:
            o = A.evaluate(values, A.allocate(rule, values, table.U), table)
            d = acc[rule]
            for key in ("ef", "ef1", "efx"):
                d[key] += o.witnesses[key] is None
            d["po"] += o.pareto
            d["nash"].append(o.nash_ratio)
            d["min"].append(o.min_ratio)
            d["sum"].append(o.sum_ratio)
            d["share"].append(min(o.shares))
    return {rule: {"ef": d["ef"] / runs, "ef1": d["ef1"] / runs, "efx": d["efx"] / runs, "po": d["po"] / runs,
                   "nash": float(np.mean(d["nash"])), "min": float(np.mean(d["min"])), "sum": float(np.mean(d["sum"])), "share": float(np.mean(d["share"]))} for rule, d in acc.items()}


def _sweep(param: str, values, runs: int, seed: int) -> list[dict]:
    rows = []
    for x in values:
        args = {"n": C.SERIES_N, "m": C.SERIES_M, "model": C.DEFAULT_MODEL}
        if param == "n":
            args["m"] = C.SERIES_M_FOR_NS
        args[param] = x
        cell = _cell(args["n"], args["m"], args["model"], runs, seed)
        for rule in C.RULES:
            rows.append({"param": param, "x": x, "rule": rule, "runs": runs, **cell[rule]})
    return rows


def series_models(runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Reihe 1: die drei Geschmacksmodelle (3 Fahrer, 9 Touren)."""
    return _sweep("model", tuple(C.MODELS), runs, seed)


def series_goods(runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Reihe 2: Zahl der Touren bei 3 Fahrern und unabhängigen Geschmäckern."""
    return _sweep("m", C.SERIES_MS, runs, seed)


def series_drivers(runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Reihe 3: Zahl der Fahrer bei 7 Touren und unabhängigen Geschmäckern."""
    return _sweep("n", C.SERIES_NS, runs, seed)


def cell_of(rows: list[dict], x, rule: str) -> dict:
    return next(r for r in rows if r["x"] == x and r["rule"] == rule)


AXIS_LABELS = {"model": "Geschmacksmodell", "m": "Touren", "n": "Fahrer"}


def x_label(param: str, x) -> str:
    return C.MODEL_SHORT[x] if param == "model" else str(x)


def series_rows(rows: list[dict], key: str, formatter=pct) -> list[dict]:
    """Zeilen für st.table: je Wert des Reglers eine Zeile, je Regel eine Spalte."""
    out = []
    for x in dict.fromkeys(r["x"] for r in rows):
        row = {AXIS_LABELS[rows[0]["param"]]: x_label(rows[0]["param"], x)}
        for rule in C.RULES:
            row[short_rule(rule)] = formatter(cell_of(rows, x, rule)[key])
        out.append(row)
    return out


def verdict_models(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 1: je Geschmacksmodell, wie oft die Nash-Wohlfahrt EFX erfüllt und wie oft Reihum Pareto-optimal ist; EF1-Anteile."""
    parts = []
    for x in dict.fromkeys(r["x"] for r in rows):
        parts.append(f"{C.MODEL_SHORT[x]}: Nash-Wohlfahrt EFX {pct(cell_of(rows, x, 'nash')['efx'])}, Reihum Pareto-optimal {pct(cell_of(rows, x, 'reihum')['po'])}, Leximin EF1 {pct(cell_of(rows, x, 'leximin')['ef1'])}")
    return "info", f"Mittel über {rows[0]['runs']} Instanzen (3 Fahrer, 9 Touren). " + "; ".join(parts) + "."


def verdict_goods(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 2: bei der kleinsten und größten Tourenzahl EFX und Neidfreiheit der Nash-Wohlfahrt und von Reihum."""
    lo, hi = min(r["x"] for r in rows), max(r["x"] for r in rows)
    f = lambda x, rule, key: pct(cell_of(rows, x, rule)[key])
    return "info", (f"Bei {lo} bzw. {hi} Touren erfüllen EFX: Nash-Wohlfahrt {f(lo, 'nash', 'efx')} bzw. {f(hi, 'nash', 'efx')}, Reihum {f(lo, 'reihum', 'efx')} bzw. {f(hi, 'reihum', 'efx')}, Neidkreis {f(lo, 'neidkreis', 'efx')} bzw. {f(hi, 'neidkreis', 'efx')}. "
                    f"Neidfrei ist die Nash-Wohlfahrt bei {f(lo, 'nash', 'ef')} bzw. {f(hi, 'nash', 'ef')} der Instanzen.")


def verdict_drivers(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 3: bei der größten Fahrerzahl EFX, Neidfreiheit und Nash-Wohlfahrt je Regel."""
    x = max(r["x"] for r in rows)
    parts = [f"{short_rule(rule)} EFX {pct(cell_of(rows, x, rule)['efx'])}, neidfrei {pct(cell_of(rows, x, rule)['ef'])}" for rule in C.RULES]
    return "info", f"Bei {x} Fahrern (7 Touren, {rows[0]['runs']} Instanzen): " + "; ".join(parts) + "."
