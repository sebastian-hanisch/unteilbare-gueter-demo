"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import ung_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_allocation(a):
    """Welcher Fahrer welche Tour bekommt, je Regel eine Zeile; in der Zelle der Wert der Tour für ihren Besitzer."""
    rules = list(C.RULES)
    n, m = a.values.shape
    z = [[a.outcomes[r].owner[g] for g in range(m)] for r in rules]
    text = [[str(int(a.values[a.outcomes[r].owner[g], g])) for g in range(m)] for r in rules]
    colors = C.COLOR_DRIVERS[:n]
    scale = []
    for i, color in enumerate(colors):
        scale += [[i / n, color], [(i + 1) / n, color]]
    fig = go.Figure(go.Heatmap(z=z, x=[f"T{g + 1}" for g in range(m)], y=[C.RULE_SHORT[r] for r in rules], text=text, texttemplate="%{text}", colorscale=scale, zmin=-0.5, zmax=n - 0.5,
                               showscale=False, xgap=2, ygap=2, textfont=dict(color="white"), customdata=[[o + 1 for o in row] for row in z], hovertemplate="%{y}: %{x} geht an Fahrer %{customdata} (Wert %{text})<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(side="top")
    return _base(fig, height=300)


def build_shares(a):
    """Nutzen jedes Fahrers im Verhältnis zum Gesamtwert aller Touren für ihn, je Regel eine Gruppe von Balken (Fahrer als Serien)."""
    rules = list(C.RULES)
    n = a.values.shape[0]
    fig = go.Figure()
    for i in range(n):
        ys = [a.outcomes[r].shares[i] for r in rules]
        fig.add_trace(go.Bar(x=[C.RULE_SHORT[r] for r in rules], y=ys, name=f"Fahrer {i + 1}", marker_color=C.COLOR_DRIVERS[i], hovertemplate="%{x}: %{y:.0%}<extra>Fahrer " + str(i + 1) + "</extra>"))
    fig.add_hline(y=1 / n, line_dash="dash", line_color=C.COLOR_ALERT, annotation_text=f"gleicher Anteil 1/{n}", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Anteil am Gesamtwert aller Touren", range=[0, 1.05], tickformat=".0%")
    fig.update_xaxes(tickangle=-20)
    return _base(fig, height=380)


AXIS_TITLES = {"model": "Geschmacksmodell", "m": "Zahl der Touren", "n": "Zahl der Fahrer"}


def build_series(rows, key, ytitle, ymax=1.05):
    """Eine Linie je Regel; key: ef, ef1, efx, po, nash, min, sum, share."""
    fig = go.Figure()
    param = rows[0]["param"]
    for rule in C.RULES:
        pts = [r for r in rows if r["rule"] == rule]
        xs = [C.MODEL_SHORT[r["x"]] if param == "model" else r["x"] for r in pts]
        fig.add_trace(go.Scatter(x=xs, y=[r[key] for r in pts], mode="lines+markers", name=C.RULE_SHORT[rule], line=dict(color=C.RULE_COLORS[rule], width=2),
                                 hovertemplate="%{x}: %{y:.1%}<extra>" + C.RULE_SHORT[rule] + "</extra>"))
    fig.update_xaxes(title_text=AXIS_TITLES[param], type="category")
    fig.update_yaxes(title_text=ytitle, range=[0, ymax], tickformat=".0%")
    return _base(fig, height=340)
