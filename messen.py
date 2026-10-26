"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout."""

import sys
import time

sys.path.insert(0, ".")
import ung_constants as C
import ung_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    print(name, "| Zuteilungen", p["n"] ** a.m_eff, "| EF1/EFX/neidfrei aller:", ev.pct(a.shares["ef1"]), ev.pct(a.shares["efx"]), ev.pct(a.shares["ef"], 1))
    for r in ev.rule_rows(a):
        print("   ", r)
    for line in ev.witness_lines(a):
        print("   -", line)
    print("   ", ev.verdict_state(a)[1])

for title, fn, key_list in (("REIHE 1 (Geschmäcker)", ev.series_models, ("ef", "ef1", "efx", "po", "nash", "min", "sum", "share")),
                            ("REIHE 2 (Touren)", ev.series_goods, ("ef", "ef1", "efx", "po", "nash", "min", "sum")),
                            ("REIHE 3 (Fahrer)", ev.series_drivers, ("ef", "ef1", "efx", "po", "nash", "min", "sum"))):
    rows = fn()
    print(title, rows[0]["runs"], "Instanzen je Zelle")
    for key in key_list:
        print(" ", key)
        for r in ev.series_rows(rows, key):
            print("    ", r)
print("sec", round(time.time() - t0, 1))
