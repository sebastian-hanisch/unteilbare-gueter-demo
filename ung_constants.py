"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

RULES = {
    "reihum": "Reihum wählen (Round Robin)",
    "neidkreis": "Neidkreis beseitigen",
    "nash": "Größte Nash-Wohlfahrt",
    "leximin": "Größter Mindestnutzen (Leximin)",
    "summe": "Größte Summe der Nutzen",
}
RULE_SHORT = {"reihum": "Reihum", "neidkreis": "Neidkreis", "nash": "Nash-Wohlfahrt", "leximin": "Leximin", "summe": "Größte Summe"}
RULE_TEXT = {
    "reihum": "Die Fahrer wählen reihum je eine noch freie Tour, jeder nimmt die ihm wertvollste.",
    "neidkreis": "Die Touren kommen der Reihe nach (wertvollste zuerst) zu einem Fahrer, den niemand beneidet; gibt es keinen, wird ein Neidkreis durch Weitergeben der Bündel aufgelöst.",
    "nash": "Von allen Zuteilungen wird die mit dem größten Produkt der Nutzen gewählt (Aufzählung aller Zuteilungen).",
    "leximin": "Von allen Zuteilungen wird die gewählt, deren kleinster Nutzen am größten ist; bei Gleichstand entscheidet der zweitkleinste und so weiter.",
    "summe": "Jede Tour geht an den Fahrer, der sie am höchsten bewertet; um Fairness kümmert sich diese Regel nicht.",
}
DEFAULT_RULE = "nash"

MODELS = {
    "unabhaengig": "Unabhängige Geschmäcker (jeder bewertet jede Tour für sich zufällig)",
    "aehnlich": "Ähnliche Geschmäcker (alle finden dieselben Touren gut)",
    "spezialisten": "Spezialisten (jede Tour hat einen Fahrer, dem sie besonders liegt)",
}
MODEL_SHORT = {"unabhaengig": "Unabhängig", "aehnlich": "Ähnlich", "spezialisten": "Spezialisten"}
DEFAULT_MODEL = "unabhaengig"

N_MIN, N_MAX, DEFAULT_N = 2, 6, 3             # Fahrer
M_MIN, M_MAX, DEFAULT_M = 5, 10, 9            # Touren
M_LIMIT = {2: 10, 3: 10, 4: 8, 5: 7, 6: 6}          # größte Tourenzahl je Fahrerzahl: alle n^m Zuteilungen werden aufgezählt
VALUE_MIN, VALUE_MAX = 1, 20                  # Bewertungen sind ganze Zahlen von 1 bis 20
SEED_MAX, DEFAULT_SEED = 9999, 5

# Feste Messreihen (unabhängig von den Reglern): nie ein einzelner Zufalls-Seed als Befund
SERIES_SEED = 100000
SERIES_RUNS = 150
SERIES_N, SERIES_M = 3, 9
SERIES_MS = (4, 5, 6, 7, 8, 9)                # Reihe 2: Tourenzahl bei 3 Fahrern, unabhängige Geschmäcker
SERIES_NS = (2, 3, 4, 5)                      # Reihe 3: Fahrerzahl bei 7 Touren, unabhängige Geschmäcker
SERIES_M_FOR_NS = 7

COLOR_DRIVERS = ["#4c78a8", "#e8a838", "#2F6B65", "#b04a3a", "#7b6fa8", "#8c8c8c"]
COLOR_ALERT = "#c0392b"
RULE_COLORS = {"reihum": "#4c78a8", "neidkreis": "#9aa5b1", "nash": "#2F6B65", "leximin": "#7fb8a6", "summe": "#b04a3a"}

PRESETS = {
    "Drei Fahrer, neun Touren": {"n": 3, "m": 9, "model": "unabhaengig", "seed": 5},
    "Fünf Fahrer: Nash-Wohlfahrt ohne EFX": {"n": 5, "m": 7, "model": "unabhaengig", "seed": 2},
    "Ähnliche Geschmäcker": {"n": 3, "m": 9, "model": "aehnlich", "seed": 14},
    "Spezialisten: Leximin ohne EF1": {"n": 3, "m": 9, "model": "spezialisten", "seed": 3},
    "Vier Fahrer, acht Touren": {"n": 4, "m": 8, "model": "unabhaengig", "seed": 25},
}
PRESET_HELP = {
    "Drei Fahrer, neun Touren": "Voreinstellung: drei Fahrer, neun Touren, unabhängige Geschmäcker. Reihum und die größte Nash-Wohlfahrt sind neidfrei; Neidkreis und Leximin erfüllen EF1, aber nicht EFX, und der Neidkreis ist nicht einmal Pareto-optimal.",
    "Fünf Fahrer: Nash-Wohlfahrt ohne EFX": "Bei fünf Fahrern und sieben Touren ist niemand neidfrei, und selbst die größte Nash-Wohlfahrt verletzt EFX, obwohl sie EF1 erfüllt und Pareto-optimal ist.",
    "Ähnliche Geschmäcker": "Wenn alle dieselben Touren gut finden, konkurrieren sie um dieselben: Reihum verletzt hier EFX und ist nicht Pareto-optimal, die größte Nash-Wohlfahrt ist neidfrei.",
    "Spezialisten: Leximin ohne EF1": "Jeder Fahrer hat Touren, die ihm besonders liegen. Der größte Mindestnutzen (Leximin) verletzt hier schon EF1, die größte Nash-Wohlfahrt nicht.",
    "Vier Fahrer, acht Touren": "Vier Fahrer, acht Touren: Reihum und Leximin sind neidfrei, der Neidkreis verletzt EFX, die größte Nash-Wohlfahrt ist nicht neidfrei, aber EFX und Pareto-optimal.",
}
