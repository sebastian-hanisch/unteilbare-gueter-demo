"""Unteilbare Güter fair verteilen: wer beneidet wen? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Abstimmen und Fair Teilen“: Touren (unteilbare Güter) werden auf Fahrer verteilt, jeder Fahrer bewertet jede Tour additiv. Fünf Regeln (Reihum, Neidkreis,
größte Nash-Wohlfahrt, Leximin, größte Summe) werden an allen n^m Zuteilungen gemessen: Neidfreiheit, EF1, EFX, Pareto-Optimalität. Der Kern liegt in ung_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import ung_constants as C
import ung_evaluation as ev
from ung_evaluation import Settings, analyse, num, pct, rule_rows, series_rows, verdict_drivers, verdict_goods, verdict_models, verdict_state, witness_lines
from ung_layout import dunkles_design, kopf_css
from ung_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from ung_visualization import build_allocation, build_series, build_shares

st.set_page_config(page_title="Unteilbare Güter – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _series_models():
    return ev.series_models()


@st.cache_data(show_spinner=False)
def _series_goods():
    return ev.series_goods()


@st.cache_data(show_spinner=False)
def _series_drivers():
    return ev.series_drivers()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in ung_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🚚 Touren fair verteilen: wer beneidet wen?")
st.markdown(
    """
Ein Betrieb verteilt **Touren** auf **Fahrer**. Jede Tour geht an genau einen Fahrer (sie ist **unteilbar**), und jeder Fahrer bewertet jede Tour für sich (ein Wert von 1 bis 20, die Werte eines Bündels addieren sich).
**Neidfrei** ist eine Zuteilung, wenn kein Fahrer das Bündel eines anderen höher bewertet als sein eigenes. Bei unteilbaren Gütern gibt es das oft nicht: zwei Fahrer, eine begehrte Tour. Deshalb gibt es abgeschwächte Maße: **EF1** (der Neid verschwindet, wenn man dem Beneideten **eine** Tour wegnimmt) und **EFX** (der Neid verschwindet nach Wegnahme **jeder** Tour, auch der unwichtigsten).
Die Demo vergleicht **fünf Regeln** auf denselben Bewertungen und prüft nach, was sie halten: Neidfreiheit, EF1, EFX und **Pareto-Optimalität** (niemand kann besser gestellt werden, ohne dass ein anderer verliert). Zum Vergleich werden **alle** n<sup>m</sup> Zuteilungen aufgezählt.
Verwandt: `shapley-demo` und `moulin-demo` (Kosten teilen statt Güter), `kreuzschulung-demo` und `shift-demo` (Zuordnung ohne Fairnessmaß), `wahlregeln-demo` (Abstimmen statt Verteilen).

Weiter unten: der Abschnitt **🔬 Messreihen**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
""",
    unsafe_allow_html=True,
)

with st.expander("So wird gerechnet", expanded=True):
    st.markdown(
        """
1. **Bewertungen:** ganze Zahlen von 1 bis 20 je Fahrer und Tour, nach einem von drei Modellen (unabhängig, ähnlich, mit Spezialisten) und dem Zufalls-Seed.
2. **Reihum:** die Fahrer wählen der Reihe nach je eine freie Tour. **Neidkreis:** die Touren kommen nach Gesamtwert fallend zu einem Fahrer, den niemand beneidet; gibt es keinen, werden die Bündel entlang eines Neidkreises weitergegeben. **Größte Nash-Wohlfahrt:** das größte Produkt der Nutzen über alle Zuteilungen. **Leximin:** der größte Mindestnutzen, bei Gleichstand der zweitkleinste und so weiter. **Größte Summe:** jede Tour an den, der sie am höchsten bewertet.
3. **Prüfung:** Neid, EF1 und EFX werden an jeder Zuteilung geprüft (jedes Paar von Fahrern, jede Tour im fremden Bündel); Pareto-Optimalität durch Vergleich mit **allen** Zuteilungen.
4. **Gleichstände** entscheidet der kleinere Index (Fahrer, Tour, Zuteilung in der Aufzählung).
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    n = st.slider("Fahrer", *bounds("n_slider"), key="n_slider", help="Zahl der Fahrer, unter denen die Touren verteilt werden.")
    m = st.slider("Touren", *bounds("m_slider"), key="m_slider", help="Zahl der Touren. Weil alle Zuteilungen aufgezählt werden, gilt eine Obergrenze je Fahrerzahl (siehe unten im Ergebnis).")
    model = st.selectbox("Geschmäcker", list(C.MODELS), format_func=C.MODELS.get, key="model_select", help="Wie die Bewertungen entstehen.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Bewertungen ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"n_slider": int(n), "m_slider": int(m), "model_select": model, "seed_input": int(seed)})

settings = Settings(n=int(n), m=int(m), model=model, seed=int(seed))
with st.spinner("Zähle alle Zuteilungen auf …"):
    a = _analysis(settings)
m_eff = a.m_eff

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
if m_eff != settings.m:
    st.caption(f"Bei {settings.n} Fahrern werden höchstens {C.M_LIMIT[settings.n]} Touren gerechnet (alle {settings.n}^{C.M_LIMIT[settings.n]} Zuteilungen werden aufgezählt) und mindestens so viele wie Fahrer; gerechnet wird mit {m_eff} Touren.")
m1, m2, m3 = st.columns(3)
m1.metric("Fahrer · Touren", f"{settings.n} · {m_eff}", delta=f"{settings.n ** m_eff:,} Zuteilungen".replace(",", "."), delta_color="off")
m2.metric("Zuteilungen mit EF1", pct(a.shares["ef1"]), delta=f"EFX: {pct(a.shares['efx'])}", delta_color="off")
m3.metric("Neidfreie Zuteilungen", pct(a.shares["ef"], 1), delta="aller Zuteilungen", delta_color="off")
st.table(rule_rows(a))
st.markdown("**Wer welche Tour bekommt** (Farbe = Fahrer, Zahl = Wert der Tour für ihn)")
st.plotly_chart(build_allocation(a), width="stretch", key="allocation_chart")
st.markdown("**Wie viel vom Möglichen jeder Fahrer bekommt**")
st.plotly_chart(build_shares(a), width="stretch", key="shares_chart")
lines = witness_lines(a)
if lines:
    st.markdown("**Beispiele für verletzte Eigenschaften**")
    for line in lines:
        st.markdown("- " + line)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was ist fair, was effizient, und was bekommt man zugleich?")
kind, text = verdict_state(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Messreihen")
st.caption(f"Feste Programme, unabhängig von den Reglern. Jede Reihe rechnet auf Klick in einigen Sekunden; je Zelle {C.SERIES_RUNS} Instanzen mit den Zufalls-Seeds {C.SERIES_SEED} bis {C.SERIES_SEED + C.SERIES_RUNS - 1}.")
tab1, tab2, tab3 = st.tabs(["Welche Geschmäcker?", "Wie viele Touren?", "Wie viele Fahrer?"])
with tab1:
    st.markdown(f"**Anteil der Instanzen** mit EFX und mit Pareto-Optimalität je Regel, für die drei Geschmacksmodelle ({C.SERIES_N} Fahrer, {C.SERIES_M} Touren).")
    if st.button("Reihe rechnen", key="models_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_models()
        st.session_state["models_done"] = time.perf_counter() - t0
    if "models_done" in st.session_state:
        rows = _series_models()
        st.plotly_chart(build_series(rows, "efx", "Anteil der Instanzen mit EFX"), width="stretch", key="models_efx_chart")
        st.plotly_chart(build_series(rows, "po", "Anteil der Instanzen, die Pareto-optimal sind"), width="stretch", key="models_po_chart")
        st.table(series_rows(rows, "efx"))
        kind, text = verdict_models(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['models_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown(f"**Wie hängt es von der Tourenzahl ab?** Anteil der Instanzen mit EFX ({C.SERIES_N} Fahrer, unabhängige Geschmäcker).")
    if st.button("Reihe rechnen", key="goods_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_goods()
        st.session_state["goods_done"] = time.perf_counter() - t0
    if "goods_done" in st.session_state:
        rows = _series_goods()
        st.plotly_chart(build_series(rows, "efx", "Anteil der Instanzen mit EFX"), width="stretch", key="goods_efx_chart")
        st.plotly_chart(build_series(rows, "ef", "Anteil neidfreier Instanzen"), width="stretch", key="goods_ef_chart")
        st.table(series_rows(rows, "efx"))
        kind, text = verdict_goods(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['goods_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab3:
    st.markdown(f"**Wie hängt es von der Fahrerzahl ab?** Anteil der Instanzen mit EFX und Nash-Wohlfahrt im Verhältnis zum Größtmöglichen ({C.SERIES_M_FOR_NS} Touren, unabhängige Geschmäcker).")
    if st.button("Reihe rechnen", key="drivers_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_drivers()
        st.session_state["drivers_done"] = time.perf_counter() - t0
    if "drivers_done" in st.session_state:
        rows = _series_drivers()
        st.plotly_chart(build_series(rows, "efx", "Anteil der Instanzen mit EFX"), width="stretch", key="drivers_efx_chart")
        st.plotly_chart(build_series(rows, "nash", "Nash-Wohlfahrt im Verhältnis zum Größtmöglichen"), width="stretch", key="drivers_nash_chart")
        st.table(series_rows(rows, "nash"))
        kind, text = verdict_drivers(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['drivers_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Additive Bewertungen** | Gehören zwei Touren zusammen (eine Rundtour in zwei Teilen), ist der Wert eines Bündels nicht die Summe; EF1 und EFX sind dann anders zu fassen. | diese Demo |
| **Wenige Fahrer und Touren** | Alle Zuteilungen werden aufgezählt (bei 3 Fahrern höchstens 10 Touren). Die Anteile gelten für diese Größen; bei mehr Fahrern wird EFX seltener erfüllt. | diese Demo (Reglerobergrenze) |
| **Ganze Zahlen von 1 bis 20, drei Modelle** | Echte Bewertungen sind weniger glatt; die Anteile hängen vom Modell ab (Messreihe 1). | diese Demo |
| **Ehrliche Bewertungen** | Wer weiß, nach welcher Regel verteilt wird, kann seine Bewertungen verschieben; hier sind sie echt. | – |
| **Eine Stichprobe von 150 Instanzen je Zelle** | Kleine Unterschiede sind kein Befund; Aussagen wie „nie“ gelten für die gemessenen Instanzen, nicht als Beweis. | diese Demo (Messreihen) |
| **Fairness ist nicht Effizienz** | Eine neidfreie Zuteilung kann für alle schlechter sein als eine andere; Pareto-Optimalität prüft nur, ob jemand besser gestellt werden kann, ohne dass ein anderer verliert. | diese Demo (Tabelle) |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Instanz.** $n$ Fahrer, $m$ Touren, Werte $v_{ig} \in \{1, \dots, 20\}$. Eine Zuteilung ist eine Abbildung $o : \{1,\dots,m\} \to \{1,\dots,n\}$, das Bündel von Fahrer $j$ ist $A_j = o^{-1}(j)$, und der Nutzen von Fahrer $i$ für ein Bündel $S$ ist $v_i(S) = \sum_{g \in S} v_{ig}$.

**Neid.** Fahrer $i$ beneidet $j$, wenn $v_i(A_j) > v_i(A_i)$. **Neidfrei:** niemand beneidet jemanden. **EF1:** für alle $i, j$ gilt $v_i(A_i) \ge v_i(A_j)$ oder es gibt $g \in A_j$ mit $v_i(A_i) \ge v_i(A_j \setminus \{g\})$. **EFX:** für alle $i, j$ und **alle** $g \in A_j$ gilt $v_i(A_i) \ge v_i(A_j \setminus \{g\})$. Neidfrei $\Rightarrow$ EFX $\Rightarrow$ EF1.

**Pareto-Optimalität.** Eine Zuteilung $o$ ist Pareto-optimal, wenn es keine Zuteilung $o'$ mit $v_i(A'_i) \ge v_i(A_i)$ für alle $i$ und $>$ für mindestens ein $i$ gibt (hier durch Vergleich mit allen $n^m$ Zuteilungen geprüft).

**Regeln.** Nash-Wohlfahrt: $\max_o \prod_i v_i(A_i)$. Leximin: sortiere die Nutzen aufsteigend und maximiere lexikographisch. Größte Summe: $\max_o \sum_i v_i(A_i)$, jede Tour an einen Fahrer mit dem größten $v_{ig}$.

**Literatur** (aus Abstracts, nicht im Original geprüft): Caragiannis, Kurokawa, Moulin, Procaccia, Shah, Wang, *The Unreasonable Fairness of Maximum Nash Welfare*, ACM TEAC 2019: die größte Nash-Wohlfahrt ist EF1 und Pareto-optimal. Neidkreis-Verfahren: Lipton u. a. 2004 (nicht nachgelesen). Dass EFX immer existiert, ist für drei Fahrer bekannt und für mehr offen (laut Sekundärquelle).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
