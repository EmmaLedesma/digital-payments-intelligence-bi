"""Gráficos Plotly (sin dependencia de Streamlit)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .theme import BLUE, GOLD, NAVY, PALETTE, RED, SLATE, TEAL, fmt


def _base(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=10, r=10, t=40, b=10),
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=NAVY),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, x=0),
        title=dict(font=dict(size=15), x=0),
    )
    return fig


def linea_mensual(df: pd.DataFrame, anio_resaltado: int | None = None, titulo: str = "") -> go.Figure:
    fig = px.line(df, x="Fecha", y="Operaciones_M", title=titulo,
                  labels={"Operaciones_M": "Millones de operaciones", "Fecha": ""},
                  color_discrete_sequence=[TEAL])
    fig.update_traces(line=dict(width=3))
    if anio_resaltado:
        fig.add_vrect(x0=f"{anio_resaltado}-01-01", x1=f"{anio_resaltado}-12-31",
                      fillcolor=GOLD, opacity=0.15, line_width=0)
    return _base(fig)


def donut_medios(df: pd.DataFrame, titulo: str = "") -> go.Figure:
    fig = px.pie(df, names="Medio", values="Operaciones_M", hole=0.55, title=titulo,
                 color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="inside", textinfo="percent", sort=False,
                      hovertemplate="%{label}<br>%{value:,.1f} M ops<br>%{percent}<extra></extra>")
    fig.update_layout(legend=dict(orientation="v", x=1.02, y=0.5))
    return _base(fig, 400)


def linea_trimestral(df: pd.DataFrame, log: bool = False, titulo: str = "") -> go.Figure:
    fig = px.line(df, x="Trimestre", y="Operaciones_M", color="Medio", markers=True, title=titulo,
                  labels={"Operaciones_M": "Millones de operaciones", "Trimestre": ""},
                  color_discrete_sequence=PALETTE)
    if log:
        fig.update_yaxes(type="log")
    fig.update_xaxes(tickangle=-45)
    return _base(fig, 440)


def barras_yoy(df: pd.DataFrame, col: str = "Variación %", titulo: str = "") -> go.Figure:
    d = df.sort_values(col)
    colores = [TEAL if v >= 0 else RED for v in d[col]]
    fig = go.Figure(go.Bar(
        x=d[col], y=d["Medio de pago"], orientation="h", marker_color=colores,
        text=[f"{v:+.1f}%".replace(".", ",") for v in d[col]], textposition="outside",
        hovertemplate="%{y}<br>%{x:+.1f}%<extra></extra>"))
    fig.update_layout(title=titulo, xaxis_title="Variación interanual (%)", yaxis_title="")
    return _base(fig, 440)


def apiladas_edad(df: pd.DataFrame, titulo: str = "") -> go.Figure:
    cols = ["Solo cuenta bancaria", "Solo cuenta de pago", "Ambas cuentas"]
    fig = go.Figure()
    for c, color in zip(cols, [BLUE, GOLD, TEAL]):
        fig.add_bar(x=df["Rango etario"], y=df[c], name=c, marker_color=color,
                    hovertemplate="%{x}<br>" + c + ": %{y:.1f}%<extra></extra>")
    fig.update_layout(barmode="stack", title=titulo, yaxis_title="% de personas con alguna cuenta",
                      xaxis_title="Rango etario", yaxis_range=[0, 100])
    return _base(fig, 420)


def apiladas_debito(df: pd.DataFrame, titulo: str = "") -> go.Figure:
    fig = go.Figure()
    for c, color in zip(["Débito POS", "Débito por Internet"], [SLATE, TEAL]):
        fig.add_bar(x=df["Anio"].astype(str), y=df[c], name=c, marker_color=color,
                    text=[f"{v:.1f}%".replace(".", ",") for v in df[c]], textposition="inside")
    fig.update_layout(barmode="stack", title=titulo, yaxis_title="% de operaciones de débito",
                      xaxis_title="", yaxis_range=[0, 100])
    return _base(fig, 420)


def barras_densidad(df: pd.DataFrame, titulo: str = "") -> go.Figure:
    d = df.sort_values("Cada_10000")
    colores = [GOLD if p else TEAL for p in d["Prioritaria"]]
    fig = go.Figure(go.Bar(
        x=d["Cada_10000"], y=d["Nombre_Corto"], orientation="h", marker_color=colores,
        text=[fmt(v, 2) for v in d["Cada_10000"]], textposition="outside",
        customdata=d["Puntos"],
        hovertemplate="%{y}<br>%{x:.2f} cada 10.000 adultos<br>%{customdata:,} puntos<extra></extra>"))
    fig.update_layout(title=titulo, xaxis_title="Puntos de acceso cada 10.000 adultos", yaxis_title="")
    return _base(fig, 680)


def mapa_puntos(df: pd.DataFrame, titulo: str = "") -> go.Figure:
    d = df.copy()
    d["Cada_10000_txt"] = d["Cada_10000"].map(lambda v: fmt(v, 2))
    fig = px.scatter_map(
        d, lat="lat", lon="lon", size="Puntos", color="Cada_10000",
        hover_name="Nombre_Corto", hover_data={"Puntos": ":,", "Cada_10000": ":.2f", "lat": False, "lon": False},
        color_continuous_scale=["#E5484D", "#F5B700", "#14B8A6"], size_max=45, zoom=3.0,
        center=dict(lat=-38.5, lon=-65), map_style="carto-positron", title=titulo,
        labels={"Cada_10000": "cada 10.000 adultos"})
    fig.update_layout(coloraxis_colorbar=dict(title="cada 10.000<br>adultos"))
    return _base(fig, 640)
