import streamlit as st

from payments_bi.theme import callout, setup_page

setup_page("06 · DATOS, LÍMITES Y ÉTICA", "Qué podemos y qué no podemos afirmar",
           "Calidad de los datos, riesgos de interpretación y gobernanza")

st.subheader("Qué no podemos afirmar")
c = st.columns(3)
with c[0], st.container(border=True):
    st.markdown("**1 · No hay cruce entre personas y transacciones**")
    st.write("Los datos del BCRA no permiten vincular las operaciones con la edad ni con la provincia de quien las hace.")
with c[1], st.container(border=True):
    st.markdown("**2 · Poca infraestructura ≠ poca adopción**")
    st.write("Una baja densidad de puntos de acceso no asegura alta demanda digital ni rentabilidad: falta mirar conectividad y bancarización previa.")
with c[2], st.container(border=True):
    st.markdown("**3 · El análisis es descriptivo**")
    st.write("Muestra patrones del pasado; no garantiza retornos ni anticipa el comportamiento futuro.")

st.subheader("Sesgos y calidad de la información")
st.markdown(
    "- **Superposición de canales:** las transferencias inmediatas (7.478,5 M en 2025) se solapan con las interoperables "
    "(841,2 M) y además figuran como canal *Push*; sumar volúmenes entre canales dobla la contabilización.\n"
    "- **Ausencia de cruce microanalítico:** no se puede saber la edad ni la provincia de quien ejecuta una transferencia o un pago QR.\n"
    "- **Subrepresentación de la economía informal:** la densidad de puntos refleja solo infraestructura formal.")

st.subheader("Riesgos de interpretación")
st.table({
    "Riesgo": ["Falacia de causalidad territorial", "Sesgo de métricas vanidosas", "Extrapolación prescriptiva no validada"],
    "Diagnóstico erróneo": ["Asumir que baja densidad implica falta de demanda digital",
                            "Evaluar volumen bruto sin margen ni recurrencia por usuario",
                            "Tratar hipótesis de acción como certezas de mercado"],
    "Impacto negativo": ["Invertir en fuerza de ventas sin diagnosticar conectividad",
                         "Priorizar canales masivos de bajo valor transaccional",
                         "Asignar presupuesto sin pilotos ni grupos de control"],
})

st.subheader("Gobernanza y uso responsable")
st.markdown(
    "- **Minimización y anonimización** si se integran datos primarios de la fintech.\n"
    "- **No discriminación:** la segmentación territorial no debe derivar en exclusión de jurisdicciones desatendidas.\n"
    "- **Trazabilidad:** cada indicador con ficha técnica (fuente, periodicidad, fórmula).")

st.subheader("Modelo de datos (esquema estrella)")
st.graphviz_chart("""
digraph G {
  rankdir=LR; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];
  node [fillcolor="#14B8A6", fontcolor=white];
  Fact_Transacciones; Fact_Puntos_Acceso_Provincia; Fact_Puntos_Acceso_Tasas; Fact_Tenencia_Cuentas;
  node [fillcolor="#0B1B3A", fontcolor=white];
  Dim_Conformada; Dim_Provincia; Dim_Puntos_Acceso; Dim_Rango_Etario; Dim_Tipo_Cuenta; Calendario;
  Fact_Transacciones -> Dim_Conformada [label="ID_Categoria"];
  Fact_Puntos_Acceso_Provincia -> Dim_Provincia; Fact_Puntos_Acceso_Provincia -> Dim_Puntos_Acceso;
  Fact_Puntos_Acceso_Tasas -> Dim_Provincia; Fact_Puntos_Acceso_Tasas -> Dim_Puntos_Acceso;
  Fact_Tenencia_Cuentas -> Dim_Rango_Etario; Fact_Tenencia_Cuentas -> Dim_Tipo_Cuenta;
}
""")
callout("Detalle completo del modelo, medidas DAX y diccionario de datos en <code>docs/data-model.md</code> y <code>queries/</code>.")
