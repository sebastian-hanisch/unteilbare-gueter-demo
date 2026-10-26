# Unteilbare Güter fair verteilen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-unteilbare-gueter-demo.streamlit.app/)** -->

Stück der Linie **Abstimmen und Fair Teilen** (Konzepte-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“). Verwandt: [gemeinsames-budget-demo](https://github.com/sebastian-hanisch/gemeinsames-budget-demo) (ein Budget auf Projekte verteilen, mit Garantien für Gruppen), [wahlregeln-demo](https://github.com/sebastian-hanisch/wahlregeln-demo) (ein Sieger statt einer Zuteilung) sowie `shapley-demo` und `moulin-demo` (Kosten teilen statt Güter) und `kreuzschulung-demo` und `shift-demo` (Zuordnung ohne Fairnessmaß).
Die Demo fragt: **Ein Betrieb verteilt unteilbare Touren auf Fahrer, jeder Fahrer bewertet jede Tour für sich – welche Regel verteilt „fair“, und was heißt das überhaupt?** Fünf Regeln auf denselben Bewertungen: **Reihum** wählen, **Neidkreis** beseitigen, die **größte Nash-Wohlfahrt** (größtes Produkt der Nutzen), **Leximin** (größter Mindestnutzen) und die **größte Summe** der Nutzen als Gegenprobe, die Fairness nicht kennt.
Nachgeprüft werden **Neidfreiheit**, die abgeschwächten Maße **EF1** (der Neid verschwindet, wenn man dem Beneideten eine Tour wegnimmt) und **EFX** (er verschwindet nach Wegnahme jeder Tour) sowie **Pareto-Optimalität**; zum Vergleich werden **alle** n<sup>m</sup> Zuteilungen aufgezählt (bis zu 78 125).

Der Kern ist eigener Code (`numpy`): die fünf Regeln, die Neid- und Pareto-Prüfung und die Aufzählung aller Zuteilungen. Ein unabhängiges Orakel in den Tests rechnet die Wahl über alle Zuteilungen und die Definitionen in reinem Python nach.

## Warum dieses Problem

Unteilbare Güter sind das Gegenstück zur Kostenteilung: eine Tour geht an genau einen Fahrer. **Neidfrei ist kaum eine Zuteilung** (bei 3 Fahrern und 9 Touren im Standardfall 0,6 % aller 19 683), also braucht man abgeschwächte Maße, und die Frage wird: welche Regel liefert sie, und was kostet das an Effizienz?
Die Demo zeigt vier Dinge, die in einer Lehrbuchdarstellung nebeneinander stehen und hier **gemessen** werden: (1) **EF1 liefern drei Regeln immer** (Reihum, Neidkreis, Nash-Wohlfahrt), Leximin nicht. (2) **EFX liefert keine** (die Nash-Wohlfahrt fast immer, bei fünf Fahrern in 81 %, Reihum bei fünf Fahrern nur in 29 %). (3) **Effizienz ist eine eigene Frage**: der Neidkreis ist EF1, aber fast nie Pareto-optimal (3 % der Instanzen bei 3 Fahrern und 9 Touren) und erreicht nur 51 % der größten Nash-Wohlfahrt. (4) **Nur die Nash-Wohlfahrt hat beides**, EF1 und Pareto-Optimalität, in jeder gemessenen Instanz.

## Modell

**Instanz.** n Fahrer, m Touren, Werte v<sub>ig</sub> ∈ {1, …, 20}. Das Bündel eines Fahrers hat als Wert die Summe der Werte seiner Touren (additiv). Drei Geschmacksmodelle: *unabhängig* (jeder bewertet jede Tour zufällig), *ähnlich* (gemeinsamer Wert je Tour plus Abweichung ±3) und *Spezialisten* (jede Tour hat einen Lieblingsfahrer mit 13 bis 20, die anderen 1 bis 8).
**Regeln.** *Reihum:* Fahrer 1, 2, …, n wählen reihum die ihnen wertvollste freie Tour. *Neidkreis:* Touren nach Gesamtwert fallend, jede an einen Fahrer, den niemand beneidet; gibt es keinen, geben die Fahrer eines Neidkreises ihre Bündel weiter. *Nash-Wohlfahrt:* das größte Produkt der Nutzen über alle Zuteilungen. *Leximin:* der größte Mindestnutzen, bei Gleichstand der zweitkleinste usw. *Größte Summe:* jede Tour an den, der sie am höchsten bewertet. Gleichstände entscheidet der kleinere Index.
**Maße.** Fahrer i **beneidet** j, wenn er j's Bündel höher bewertet als sein eigenes. **EF1:** nach Wegnahme *einer* Tour aus j's Bündel ist der Neid weg. **EFX:** nach Wegnahme *jeder* Tour. **Pareto-optimal:** keine Zuteilung stellt alle mindestens so gut und einen besser (geprüft gegen alle n<sup>m</sup> Zuteilungen). Neidfrei ⇒ EFX ⇒ EF1.
**Aufzählung.** Weil alle Zuteilungen durchgesehen werden, gilt eine Obergrenze der Tourenzahl je Fahrerzahl (2 und 3 Fahrer: 10 Touren, 4: 8, 5: 7, 6: 6).
Formeln und Lesehilfe stehen im 📐-Expander der App.

## Methodik

- **Kern** (`ung_algorithm.py`): Aufzählung aller Zuteilungen, die fünf Regeln, `envy_witnesses` (Neid, EF1, EFX mit dem ersten Verstoß), `fair_shares` (Anteil aller Zuteilungen), Pareto-Prüfung samt Verbesserung, Kennzahlen.
- **Szenario und Auswertung** (`ung_scenario.py`, `ung_evaluation.py`): Bewertungen aus Modell und Zufalls-Seed, Tabelle je Regel, Beispiele in Worten, drei Messreihen mit festem Programm (je Zelle 150 Instanzen, Zufalls-Seeds 100000 bis 100149), alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): fünf Schnellstart-Szenarien, Regler für Fahrer, Touren, Geschmäcker und Zufalls-Seed, Ergebnis (Tabelle, Zuteilung als Farbkarte, Anteil am Gesamtwert je Fahrer), Kernfrage mit Verdikt, drei Reiter mit Messreihen, Annahmen und Formeln.

## Befunde (gemessen, keine Behauptungen)

Die Presets sind einzelne Instanzen und deshalb exakt. Die Messreihen sind Anteile von 150 Instanzen mit festen Zufalls-Seeds (die Standardabweichung eines Anteils liegt bei höchstens 4 Prozentpunkten). **Die Zufallszahlen eines `numpy`-Generators sind nicht über Versionen stabil**: die Tests prüfen für die Reihen deshalb Bänder um diese Zahlen (±10 Prozentpunkte, bei Verhältnissen ±8); „immer“-Aussagen sind in den festen Läufen exakt.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Die Wahl von Nash-Wohlfahrt, Leximin und größter Summe gleich einer Schleife über alle Zuteilungen in reinem Python (120 Instanzen); Neid, EF1 und EFX gleich der Definition mit Listen und Wegnahme jeder Tour (120 Instanzen, je 13 Zuteilungen); Pareto-Optimalität gleich dem paarweisen Vergleich (60); der Anteil neidfreier, EF1- und EFX-Zuteilungen gleich dem Zählen aller Zuteilungen (40). Handrechnungen mit Rechnung im Kommentar, darunter ein Neidkreis. | `test_oracle_unteilbare_gueter.py`, `test_algorithm.py` |
| Wie selten ist Fairness (Standardfall, Zufalls-Seed 5)? | Von allen 19 683 Zuteilungen sind **17 %** EF1, **2 %** EFX und **0,6 %** neidfrei. Hier sind Reihum und die Nash-Wohlfahrt neidfrei; Neidkreis und Leximin erfüllen EF1, aber nicht EFX; die größte Summe gibt Fahrer 2 nur 8 von 43 Wertpunkten (19 % seines Gesamtwerts). | `test_claims.py::test_default_preset` |
| Welche Regel liefert EF1? | **Reihum, Neidkreis und Nash-Wohlfahrt in jeder der 13 Zellen** (je 150 Instanzen: drei Geschmäcker, 4 bis 9 Touren, 2 bis 5 Fahrer). **Leximin nicht immer:** 97 bis 100 % der Instanzen, bei Spezialisten **85 %**. Größte Summe: 18 bis 81 % je nach Fahrerzahl, 25 bis 80 % je nach Geschmack. | `test_claims.py::test_ef1_holds_for_round_robin_envy_cycle_and_nash_in_every_cell`, `…::test_models_efx_and_ef1` |
| Wer liefert EFX (3 Fahrer, 9 Touren, unabhängig)? | **Nash-Wohlfahrt 99 %**, Reihum 95 %, Leximin 91 %, **Neidkreis 57 %**, größte Summe 25 %. Bei **ähnlichen Geschmäckern** fällt Reihum auf **63 %**, der Neidkreis steigt auf 95 %. Bei Spezialisten: Nash-Wohlfahrt 100 %, Leximin 69 %, Neidkreis 33 %. | `test_claims.py::test_models_efx_and_ef1` |
| Wie hängt EFX von der Fahrerzahl ab (7 Touren)? | Mit 2, 3, 4, 5 Fahrern: Nash-Wohlfahrt **99, 99, 94, 81 %**, Leximin 95, 94, 96, 84 %, Reihum **94, 71, 52, 29 %**. **Selbst die Nash-Wohlfahrt verletzt EFX**, dazu ein Beispiel (5 Fahrer, 7 Touren, Zufalls-Seed 2). | `test_claims.py::test_drivers_series`, `…::test_five_drivers_preset_where_even_the_nash_rule_violates_efx` |
| Wie hängt EFX von der Tourenzahl ab (3 Fahrer)? | Die Nash-Wohlfahrt liefert EFX bei 4 bis 9 Touren in 89, 90, 98, 99, 99, 99 % der Instanzen und ist neidfrei in 35, 37, 68, 76, 90, 87 %: **mehr Touren machen Fairness leichter**. Reihum schwankt zwischen 55 und 95 %. | `test_claims.py::test_goods_series` |
| Ist EF1 schon effizient? | **Nein.** Pareto-optimal sind Nash-Wohlfahrt, Leximin und größte Summe in **allen** Instanzen. **Reihum** nur in 69 % (ähnliche Geschmäcker: 41 %, Spezialisten: 83 %). Der **Neidkreis** in 3 % (ähnlich 7 %, Spezialisten **0 %**); bei 4 bis 9 Touren fällt sein Anteil von 59 auf 3 %. | `test_claims.py::test_models_pareto_optimality_of_round_robin_and_envy_cycle`, `…::test_goods_series` |
| Was kostet Fairness an Wohlfahrt (Verhältnis zum Größtmöglichen)? | Nash-Wohlfahrt im Verhältnis zu ihrem Optimum: **Neidkreis 51 %** (Spezialisten 36 %), Reihum 90 %, Leximin 92 %, größte Summe 73 %. Summe der Nutzen: Nash-Wohlfahrt 97 %, Reihum 94 %, Neidkreis 78 %. | `test_claims.py::test_models_nash_welfare_of_the_other_rules` |
| Wie oft sind alle neidfrei? | Die Nash-Wohlfahrt ist neidfrei in 87 % (unabhängig), **41 %** (ähnlich) und 99 % (Spezialisten); Leximin in 59 % bei ähnlichen Geschmäckern. Mit der Fahrerzahl (2 bis 5): Nash-Wohlfahrt 95, 76, **19, 3 %**. | `test_claims.py::test_models_envy_freeness`, `…::test_drivers_series` |
| Schnellstart-Szenarien | Standardfall; fünf Fahrer, Nash-Wohlfahrt ohne EFX (Zufalls-Seed 2); ähnliche Geschmäcker (Reihum verletzt EFX, nicht Pareto-optimal, die Nash-Wohlfahrt neidfrei); Spezialisten, Leximin ohne EF1 (Zufalls-Seed 3); vier Fahrer, acht Touren. | `test_claims.py::test_five_drivers_preset_…`, `…::test_similar_tastes_preset`, `…::test_specialists_preset_…`, `…::test_four_drivers_preset` |

## Ehrliche Grenzen

- **Additive Bewertungen, ganze Zahlen von 1 bis 20.** Gehören zwei Touren zusammen, ist der Wert eines Bündels nicht die Summe, und EF1 und EFX müssen anders gefasst werden. Echte Bewertungen sind weniger glatt; die Anteile hängen vom Geschmacksmodell ab (Reihe 1).
- **Wenige Fahrer und Touren.** Alle n<sup>m</sup> Zuteilungen werden aufgezählt, deshalb höchstens 10 Touren (bei 6 Fahrern 6). Dass EFX bei der Nash-Wohlfahrt mit wachsender Fahrerzahl seltener erfüllt wird (99 → 81 %), ist ein Befund für diese Größen, kein Gesetz.
- **„Immer“ heißt: in allen gemessenen Instanzen.** EF1 der drei Regeln und die Pareto-Optimalität der Nash-Wohlfahrt sind aus der Literatur bekannt (Caragiannis, Kurokawa, Moulin, Procaccia, Shah, Wang, ACM TEAC 2019; nur der Abstract gelesen); hier sind sie **bestätigt**, nicht bewiesen. Ob EFX immer existiert, ist hier nicht entschieden (die Demo prüft nur, was die fünf Regeln liefern).
- **Der Neidkreis ist unsere Ausführung:** Touren in fester Reihenfolge nach Gesamtwert, Neidkreise werden über den ersten Neider gefunden. Andere Reihenfolgen und Auswahlen liefern andere Zuteilungen; dass der Neidkreis hier selten Pareto-optimal ist, gilt für diese Ausführung.
- **Leximin statt Maximin.** Bei gleichem Mindestnutzen entscheidet der zweitkleinste usw.; beim reinen Maximin wäre die Wahl unter den Gleichständen willkürlich.
- **Ehrliche Bewertungen.** Wer weiß, nach welcher Regel verteilt wird, kann seine Bewertungen verschieben.
- **Eine Stichprobe von 150 Instanzen je Zelle**; kleine Unterschiede sind kein Befund.

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9193 (9170 bis 9192 sind vergeben).
- **Leximin statt Maximin.** Der Plan nannte „Maximin“; die Demo rechnet Leximin, weil Maximin bei Gleichständen eine willkürliche Wahl träfe und nicht immer Pareto-optimal ist.
- **Die Vormessung „alle vier EF1“ stimmt für Leximin nicht.** Dort erfüllten alle vier Regeln EF1 in allen 150 Instanzen (Maximin); die App misst für Leximin 97 bis 100 % und **85 %** bei Spezialisten. Die Vormessung hatte nur das unabhängige Modell.
- **Vormessung und App im Vergleich** (150 Instanzen, 3 Fahrer, 9 Touren, unabhängig, andere Zufalls-Seeds): EFX bei Reihum 93 gegen 95 %, Neidkreis 61 gegen 57 %, Nash-Wohlfahrt 99 gegen 99 %; Nash-Wohlfahrt im Verhältnis zum Optimum beim Neidkreis 0,53 (Median) gegen 0,51 (Mittel). Abweichungen im Rahmen der Stichprobe.
- **Neu gegenüber dem Plan:** die Pareto-Prüfung (der Plan nannte nur EF1, EFX und die Nash-Wohlfahrt), die größte Summe als Gegenprobe, zwei weitere Geschmacksmodelle und der Anteil aller Zuteilungen, die EF1, EFX oder neidfrei sind.
- **Reglerspanne:** Fahrer 2 bis 6, Touren 5 bis 10 (je nach Fahrerzahl begrenzt), drei Geschmacksmodelle.

## Verifikation

- **Kern:** jede Einheit an Mini-Instanzen von Hand (Reihum, größte Summe, Nash-Wohlfahrt mit der Produkttabelle, Leximin mit Gleichstand auf dem zweitkleinsten Nutzen, der Neidkreis mit Rechnung, Neid, EF1 und EFX an der Schwelle, Anteile aller Zuteilungen, Pareto mit Verbesserung).
- **Orakel:** Wahl über alle Zuteilungen in reinem Python, Neid-Definition wörtlich, paarweise Pareto-Prüfung, Zählen aller Zuteilungen; die Sätze „Reihum, Neidkreis und Nash-Wohlfahrt sind EF1“ und „Nash-Wohlfahrt, Leximin, größte Summe sind Pareto-optimal“ als Eigenschaftstests auf zufälligen Instanzen, mit Prüfung, dass die Tests nicht leer laufen (es gibt Instanzen, in denen Reihum EFX und der Neidkreis die Pareto-Optimalität verletzen).
- **Verdikte:** reine Funktionen, jeder Zweig und jede Zahl im Text an handgesetzten Werten (`tests/test_verdicts.py`), Randfälle an den Reglergrenzen (`tests/test_edge_cases.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich, keines auf einem Reglerrand, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern, Footer, Laufzeit-Importe).
- **Mutationsprüfung** (`tools/mutate_demo.py`): 61 Stellen im Kern `ung_algorithm.py`, **56 gefangen** (5 davon über wortgleiche Zeilen in Nachbar-Demos), **3 als äquivalent festgehalten**, **2 Mutanten mit Zeitüberschreitung** (in `envy_cycle` führen sie zu einer Endlosschleife; sie zählen nicht als gefangen). Der Lauf ließ drei überleben, keine echte Lücke: der Füllwert `1 << 30` in `fair_shares` steht für „größer als jeder Wert“ und ist beliebig.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `ung_algorithm.py` | Kern: Aufzählung, Regeln, Neid, Pareto, Kennzahlen |
| `ung_constants.py` | Regler-Grenzen, feste Pläne, Farben, Presets |
| `ung_evaluation.py` | Analyse einer Instanz, Tabelle, Beispiele in Worten, Messreihen, Verdikte |
| `ung_layout.py` | Fester Kopf (Stylesheet) |
| `ung_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `ung_scenario.py` | Bewertungen nach drei Geschmacksmodellen |
| `ung_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen, Kern, Orakel, Verdikte, Randfälle, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe, Claims |

## Bewusst nicht umgesetzt

- **Teilbare Güter und Kuchen** (stetige Bewertungen, Schnittverfahren): ein anderes Problem mit anderen Mitteln.
- **Nicht additive Bewertungen** (Ergänzungen und Ersetzungen zwischen Touren) und **Kardinalitätsgrenzen** je Fahrer.
- **Größere Instanzen** mit Näherungsverfahren für die Nash-Wohlfahrt: hier genügt die Aufzählung.
- **Strategisches Bewerten:** die Bewertungen sind ehrlich.
- **Beweis, dass EFX existiert:** die Demo zeigt, was die Regeln liefern, nicht ob es immer eine Zuteilung gibt.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
