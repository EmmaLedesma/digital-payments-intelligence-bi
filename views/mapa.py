import streamlit as st

from payments_bi import charts as C
from payments_bi import data as D
from payments_bi.theme import callout, fmt, setup_page

ds = D.load()
setup_page("05 · MAPA DE OPORTUNIDADES", "Cobertura territorial y dónde mirar primero",
           "Puntos de acceso (cajeros, sucursales, agentes, sucursales móviles y terminales de autoservicio) · BCRA, 1/12/2025")

opciones = {"Todos los tipos": None} | {n.split(" / ")[0]: int(i) for i, n in
                                         zip(ds.puntos_acceso["ID_Punto_Acceso"], ds.puntos_acceso["Nombre"])}
tipo = st.selectbox("Tipo de punto de acceso", list(opciones))
dens = D.densidad_provincia(ds, opciones[tipo])
con_datos = dens[dens.Puntos > 0]

menor, mayor = dens.iloc[0], dens.iloc[-1]
k = st.columns(4)
k[0].metric("Puntos de acceso", f"{fmt(dens['Puntos'].sum(), 0)}")
k[1].metric("Jurisdicciones con datos", f"{len(con_datos)} de {len(dens)}")
k[2].metric("Menor densidad", f"{fmt(menor['Cada_10000'], 2)}", menor["Nombre_Corto"], delta_color="off")
k[3].metric("Mayor densidad", f"{fmt(mayor['Cada_10000'], 2)}", mayor["Nombre_Corto"], delta_color="off")

izq, der = st.columns([3, 2])
with izq:
    st.plotly_chart(C.mapa_puntos(dens, "Distribución geográfica de puntos de acceso"), width="stretch")
with der:
    st.plotly_chart(C.barras_densidad(dens, "Puntos de acceso cada 10.000 adultos"), width="stretch")

if opciones[tipo] is None:
    prio = dens[dens.Prioritaria].sort_values("Cada_10000")
    txt = ", ".join(f"<b>{r.Nombre_Corto}</b> ({fmt(r.Cada_10000, 2)})" for r in prio.itertuples())
    callout(f"<b>Provincias prioritarias para diagnóstico de campo:</b> {txt}. Son las de menor densidad del país "
            f"junto con Santiago del Estero y Corrientes.")
    ba = dens[dens.Nombre == "Buenos Aires"].iloc[0]
    lp = dens[dens.Nombre == "La Pampa"].iloc[0]
    callout(f"<b>Mirar solo el total engaña:</b> Buenos Aires tiene {fmt(ba.Puntos / lp.Puntos, 0)} veces más puntos que "
            f"La Pampa ({fmt(ba.Puntos, 0)} vs {fmt(lp.Puntos, 0)}), pero La Pampa ofrece casi el doble de cobertura por "
            f"adulto ({fmt(lp.Cada_10000, 2)} vs {fmt(ba.Cada_10000, 2)}).")
    top = dens.sort_values("Cada_10000", ascending=False).head(3)
    callout("<b>Ranking de mayor densidad:</b> " + ", ".join(
        f"{r.Nombre_Corto} ({fmt(r.Cada_10000, 2)})" for r in top.itertuples()) +
        ". Chaco se explica sobre todo por sus agentes bancarios (ACSF); conviene validarlo antes de tomarlo como referencia.",
        warn=True)
callout("<b>Poca infraestructura no es lo mismo que poca adopción.</b> La densidad refleja solo infraestructura formal: "
        "no dice nada sobre la demanda digital ni sobre la conectividad local.", warn=True)
