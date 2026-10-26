"""Szenario: Bewertungen von Fahrern für Touren (additiv, ganze Zahlen von 1 bis 20)."""

import numpy as np

import ung_constants as C


def effective_m(n: int, m: int) -> int:
    """Die Tourenzahl, die bei n Fahrern tatsächlich gerechnet wird: höchstens M_LIMIT[n] (alle n^m Zuteilungen werden aufgezählt), mindestens n."""
    return max(n, min(m, C.M_LIMIT[n]))


def make_values(n: int, m: int, model: str, seed: int) -> np.ndarray:
    """Matrix (n, m) ganzer Zahlen von 1 bis 20: values[i, g] ist der Wert, den Fahrer i der Tour g beimisst.

    unabhaengig: gleichverteilt. aehnlich: gemeinsamer Wert je Tour (4 bis 17) plus Abweichung (−3 bis 3) je Fahrer, auf 1 bis 20 begrenzt.
    spezialisten: jede Tour hat einen Lieblingsfahrer (zufällig); er bewertet sie mit 13 bis 20, die anderen mit 1 bis 8."""
    if model not in C.MODELS:
        raise ValueError(model)
    rng = np.random.default_rng(seed)
    if model == "unabhaengig":
        return rng.integers(C.VALUE_MIN, C.VALUE_MAX + 1, size=(n, m))
    if model == "aehnlich":
        base = rng.integers(4, 18, size=m)
        noise = rng.integers(-3, 4, size=(n, m))
        return np.clip(base[None, :] + noise, C.VALUE_MIN, C.VALUE_MAX)
    favourite = rng.integers(0, n, size=m)
    high = rng.integers(13, C.VALUE_MAX + 1, size=(n, m))
    low = rng.integers(C.VALUE_MIN, 9, size=(n, m))
    return np.where(np.arange(n)[:, None] == favourite[None, :], high, low)
