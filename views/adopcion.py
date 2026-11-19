import streamlit as st

from payments_bi import charts as C
from payments_bi import data as D
from payments_bi.theme import callout, fmt, fmt_pct, setup_page

ds = D.load()
setup_page("03 · ADOPCIÓN DIGITAL", "Quiénes usan cuentas y dónde están las brechas por edad",
           "Personas con cuentas bancarias (CBU) y de pago / billeteras (CVU) al 1 de diciembre de 2025 · Fuente: BCRA")

r = D.resumen_tenencia(ds)
k = st.columns(4)
k[0].metric("Personas con alguna cuenta", f"{fmt(r['total'] / 1e6, 2)} M")
k[1].metric("Ambas cuentas (dual)", f"{fmt_pct(r['ambas_%'])}", f"{fmt(r['ambas'] / 1e6, 2)} M personas", delta_color="off")
k[2].metric("Solo cuenta bancaria (CBU)", f"{fmt_pct(r['solo_bancaria_%'])}", f"{fmt(r['solo_bancaria'] / 1e6, 2)} M", delta_color="off")
k[3].metric("Solo cuenta de pago (CVU)", f"{fmt_pct(r['solo_pago_%'])}", f"{fmt(r['solo_pago'] / 1e6, 2)} M", delta_color="off")

edad = D.tenencia_por_edad(ds)
deb = D.participacion_debito(ds)

izq, der = st.columns(2)
with izq:
    st.plotly_chart(C.apiladas_edad(edad, "Tipo de cuenta entre personas con alguna cuenta, por edad"),
                    width="stretch")
with der:
    st.plotly_chart(C.apiladas_debito(deb, "Participación de POS e Internet en operaciones de débito"),
                    width="stretch")

joven = edad[edad["Rango etario"] == "20 - 24"].iloc[0]
mayor = edad[edad["Rango etario"] == "70 - 74"].iloc[0]
teen = edad[edad["Rango etario"] == "15 - 19"].iloc[0]
brecha = joven["Ambas cuentas"] - mayor["Ambas cuentas"]
i24 = deb[deb.Anio == 2024]["Débito por Internet"].iloc[0]
i25 = deb[deb.Anio == 2025]["Débito por Internet"].iloc[0]
concentra = teen["Personas solo pago"] / r["solo_pago"] * 100

callout(f"<b>Brecha generacional:</b> los jóvenes de 20 a 24 años tienen la mayor tenencia dual del país "
        f"({fmt_pct(joven['Ambas cuentas'])}); en 70 a 74 años baja a {fmt_pct(mayor['Ambas cuentas'])}: "
        f"<b>{fmt(brecha)} puntos porcentuales</b> menos.")
callout(f"<b>Débito online:</b> dentro del total de débito (POS + Internet), Internet pasó de {fmt_pct(i24)} en 2024 "
        f"a {fmt_pct(i25)} en 2025.")
callout(f"<b>Hallazgo adicional:</b> el {fmt_pct(concentra, 0)} de las personas con <i>solo</i> cuenta de pago tiene entre "
        f"15 y 19 años: la billetera es la puerta de entrada financiera de la población más joven.")
