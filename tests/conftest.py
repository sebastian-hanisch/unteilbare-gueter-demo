"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def vals(*rows) -> np.ndarray:
    """Bewertungen aus Zeilen (ein Fahrer je Zeile)."""
    return np.array(rows, dtype=int)


@pytest.fixture
def zwei():
    """2 Fahrer, 3 Touren. Fahrer 1 bewertet 10, 6, 4; Fahrer 2 bewertet 8, 7, 5.

    Handrechnung: Reihum: F1 wählt T1 (10), F2 wählt T2 (7), F1 wählt T3 (4): F1 {T1, T3} = 14, F2 {T2} = 7.
    Größte Nash-Wohlfahrt: alle 8 Zuteilungen durchgehen, das größte Produkt ist 14 · 7 = 98 ({T1, T3} / {T2}) gegen z. B. 10 · 12 = 120 ({T1} / {T2, T3}): 120."""
    return vals([10, 6, 4], [8, 7, 5])
