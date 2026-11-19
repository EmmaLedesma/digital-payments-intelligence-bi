import streamlit as st

from payments_bi import charts as C
from payments_bi import data as D
from payments_bi.theme import callout, fmt, fmt_pct, setup_page

ds = D.load()
setup_page("01 · EXECUTIVE OVERVIEW", "Panorama del mercado de pagos digitales en Argentina",
           "Tamaño de cada medio de pago antes de ver cómo crece · Fuente: BCRA, corte a diciembre de 2025")

anios = D.anios_disponibles(ds)[::-1]
anio = st.selectbox("Año de análisis", anios, index=0)


def delta(cid: int) -> str | None:
    v = D.variacion_anual(ds, cid, anio)
    return None if v is None else f"{fmt_pct(v, signo=True)} vs {anio - 1}"


k = st.columns(5)
k[0].metric(f"Operaciones registradas {anio}", f"{fmt(D.total_registros(ds, anio))} M",
            help="Suma de todos los canales del modelo. Hay solapamiento entre canales (ver página 06).")
k[1].metric("Acumulado de la serie", f"{fmt(D.total_registros(ds))} M")
k[2].metric("Transferencias inmediatas", f"{fmt(D.operaciones(ds, D.ID_TI, anio))} M", delta(D.ID_TI))
k[3].metric("Tarjetas de crédito", f"{fmt(D.operaciones(ds, D.ID_TC, anio))} M", delta(D.ID_TC))
k[4].metric("Cheques electrónicos (Echeq)", f"{fmt(D.operaciones(ds, D.ID_ECHEQ, anio))} M", delta(D.ID_ECHEQ))

izq, der = st.columns([3, 2])
with izq:
    st.plotly_chart(C.linea_mensual(D.serie_mensual(ds, D.ID_TI), anio,
                                    "Evolución mensual de transferencias inmediatas (millones de operaciones)"),
                    width="stretch")
with der:
    st.plotly_chart(C.donut_medios(D.operaciones_por_medio(ds, anio),
                                   "Distribución de operaciones por medio de pago"),
                    width="stretch")

ti, tc = D.operaciones(ds, D.ID_TI, anio), D.operaciones(ds, D.ID_TC, anio)
callout(f"<b>Cómo leerlo:</b> en {anio} las transferencias inmediatas movieron {fmt(ti)} M de operaciones, "
        f"unas <b>{fmt(ti / tc)} veces</b> las de tarjeta de crédito ({fmt(tc)} M). Los cheques electrónicos "
        f"tienen pocas operaciones pero de montos altos: es un uso mayorista y corporativo.")
callout("<b>Ojo con el total:</b> el número de operaciones registradas no sirve para estimar el tamaño real del "
        "mercado ni el consumo: algunos canales se superponen y los registros no son del todo homogéneos.", warn=True)
