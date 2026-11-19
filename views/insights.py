import pandas as pd
import streamlit as st

from payments_bi import data as D
from payments_bi.theme import callout, fmt, fmt_pct, setup_page

ds = D.load()
setup_page("04 · INSIGHTS & STRATEGY", "De los datos a las hipótesis de producto",
           "Cada hallazgo descriptivo se convierte en una hipótesis de acción para validar en una prueba piloto")

anio = 2025
ti = D.operaciones(ds, D.ID_TI, anio)
interop = D.operaciones(ds, D.ID_INTEROP, anio)
r = D.resumen_tenencia(ds)
deb = D.participacion_debito(ds)
i25 = deb[deb.Anio == anio]["Débito por Internet"].iloc[0]

callout("<b>Alcance:</b> es un diagnóstico <b>descriptivo</b>. Las propuestas son <b>hipótesis a poner a prueba</b>, "
        "no recetas cerradas, y que un patrón aparezca en los datos no significa que sepamos su causa.", warn=True)

st.subheader("Hipótesis de acción")
hip = pd.DataFrame([
    {"Qué vimos": f"Transferencias {fmt_pct(D.variacion_anual(ds, D.ID_TI, anio), signo=True)} ({fmt(ti)} M de op.)",
     "Qué significa para el negocio": "Ya son un medio de pago habitual",
     "Hipótesis de acción": "Simplificar el envío, el seguimiento y la confirmación",
     "Cómo la medimos": "Tasa de finalización, tiempo hasta la confirmación, consultas a soporte"},
    {"Qué vimos": f"Interoperables {fmt_pct(D.variacion_anual(ds, D.ID_INTEROP, anio), signo=True)} ({fmt(interop)} M de op.)",
     "Qué significa para el negocio": "Los comercios adoptan cobros digitales cada vez más rápido",
     "Hipótesis de acción": "Ofrecer cobro interoperable para comercios",
     "Cómo la medimos": "Tiempo al primer cobro, activación y repetición"},
    {"Qué vimos": f"{fmt_pct(r['ambas_%'])} con ambas cuentas ({fmt(r['ambas'] / 1e6, 2)} M de personas)",
     "Qué significa para el negocio": "La gente maneja su plata entre banco y billetera",
     "Hipótesis de acción": "Facilitar transferencias e interoperabilidad entre cuentas propias",
     "Cómo la medimos": "Operaciones exitosas, fricción y abandono"},
    {"Qué vimos": f"Débito por Internet: {fmt_pct(i25)} del débito",
     "Qué significa para el negocio": "El canal online se recupera mientras cae el POS físico",
     "Hipótesis de acción": "Mejorar la experiencia de checkout y la pasarela de pago",
     "Cómo la medimos": "Conversión online, rechazos y abandono"},
])
st.table(hip.set_index("Qué vimos"))

st.subheader("Hoja de ruta en tres etapas")
e = st.columns(3)
etapas = [
    ("1 · Actualización", "Sumar el próximo corte trimestral del BCRA y chequear que los datos sean consistentes.",
     "Mantener los datos vigentes y las series comparables."),
    ("2 · Prueba de producto", "Pilotos acotados de transferencias y de cobro interoperable.",
     "Medir finalización, activación de comercios y tiempo al primer cobro."),
    ("3 · Validación en territorio", "Relevar conectividad y demanda en San Juan, Formosa y Tucumán.",
     "Confirmar que sea viable y que haya demanda antes de expandir."),
]
for col, (t, que, para) in zip(e, etapas):
    with col, st.container(border=True):
        st.markdown(f"**{t}**")
        st.write(f"**Qué haríamos:** {que}")
        st.write(f"**Para qué:** {para}")

st.subheader("Dos narrativas con los mismos datos")
a, b = st.tabs(["A · Riesgos, saturación y brechas", "B · Oportunidades de captura de mercado"])
with a:
    st.markdown("**Ángulo:** defensivo, de mitigación de fricciones.")
    st.write("El POS físico cae y hay una brecha de acceso en el interior del país. En adultos mayores, "
             "la mayoría no combina cuenta bancaria y billetera.")
    st.info("**Mensaje clave:** blindar la operación actual, corregir las fallas de conversión en la pasarela "
            "online y no expandirse donde la falta de infraestructura afecte la usabilidad.")
with b:
    st.markdown("**Ángulo:** expansivo, de captura de nuevos segmentos.")
    st.write("Las transferencias viven una adopción masiva y la tenencia dual muestra que la población ya "
             "superó la barrera del aprendizaje digital.")
    st.success("**Mensaje clave:** hay una oportunidad para liderar el cobro digital en comercios pequeños y "
               "capturar mercado en provincias sub-atendidas como San Juan, Formosa y Tucumán.")

with st.expander("Adaptar la presentación según el público"):
    st.table(pd.DataFrame([
        {"Público": "Técnico (PMs, Tech Leads, UX)", "Énfasis": "Tasas de finalización, cuellos de botella de UX, pruebas piloto",
         "Formato": "Tablas de variación interanual, volumen relativo, flujos de usuario"},
        {"Público": "Directivo (C-Level, inversores)", "Énfasis": "Matriz de oportunidades, hoja de ruta de expansión, reducción de riesgos",
         "Formato": "Indicadores macro, densidad geográfica, comparativa de narrativas"},
    ]).set_index("Público"))
