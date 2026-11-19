import streamlit as st

from payments_bi import charts as C
from payments_bi import data as D
from payments_bi.theme import callout, fmt, fmt_pct, setup_page

ds = D.load()
setup_page("02 · EVOLUCIÓN DE PAGOS", "Qué crece rápido y qué pesa más",
           "Comparación interanual por medio de pago · Fuente: BCRA")

anios = [a for a in D.anios_disponibles(ds) if a >= 2021][::-1]
c1, c2, c3 = st.columns([1, 3, 1])
anio = c1.selectbox("Año a comparar", anios, index=0)
todos = list(D.ETIQUETAS[i] for i in D.MEDIOS_PAGO_IDS)
medios = c2.multiselect("Medios de pago", todos, default=todos)
log = c3.toggle("Escala log", value=False, help="Útil para ver los medios chicos junto a las transferencias.")

tabla = D.tabla_interanual(ds, anio)
sel = tabla[tabla["Medio de pago"].isin(medios)]
ids = sel["ID"].tolist()

izq, der = st.columns(2)
with izq:
    st.plotly_chart(C.linea_trimestral(D.serie_trimestral(ds, ids), log,
                                       "Evolución trimestral de operaciones por medio de pago"),
                    width="stretch")
with der:
    st.plotly_chart(C.barras_yoy(sel, titulo=f"Crecimiento interanual {anio} vs {anio - 1} (%)"),
                    width="stretch")
st.caption("2020-T3 es parcial: la serie de medios de pago empieza en septiembre de 2020.")

prev, curr = f"{anio - 1} (M)", f"{anio} (M)"
st.dataframe(
    sel.drop(columns="ID"), hide_index=True, width="stretch",
    column_config={
        prev: st.column_config.NumberColumn(format="%.1f"),
        curr: st.column_config.NumberColumn(format="%.1f"),
        "Variación %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Operaciones sumadas (M)": st.column_config.NumberColumn(format="%+.1f"),
    })

full = tabla
rapido, suma = full.iloc[0], full.sort_values("Operaciones sumadas (M)", ascending=False).iloc[0]
pos, net = full[full.ID == D.ID_POS].iloc[0], full[full.ID == D.ID_INTERNET].iloc[0]
callout(f"<b>El que más rápido crece:</b> {rapido['Medio de pago']} ({fmt_pct(rapido['Variación %'], signo=True)}). "
        f"<b>El que más suma:</b> {suma['Medio de pago']}, con {fmt(suma['Operaciones sumadas (M)'])} M de "
        f"operaciones nuevas en un año.")
callout(f"<b>Dos débitos, dos caminos:</b> el débito en terminales POS cae {fmt_pct(abs(pos['Variación %']))} mientras "
        f"el débito por Internet crece {fmt_pct(net['Variación %'])}: corrimiento hacia el e-commerce y el checkout digital.")
