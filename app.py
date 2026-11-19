"""Entrada de la app Streamlit — Digital Payments Intelligence (Grupo 8).

Ejecutar:  streamlit run app.py
"""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

st.set_page_config(page_title="Digital Payments Intelligence · BI", page_icon="💳", layout="wide")

paginas = [
    st.Page("views/overview.py", title="01 · Executive Overview", icon="📊", default=True),
    st.Page("views/evolucion.py", title="02 · Evolución de Pagos", icon="📈"),
    st.Page("views/adopcion.py", title="03 · Adopción Digital", icon="👥"),
    st.Page("views/insights.py", title="04 · Insights & Strategy", icon="💡"),
    st.Page("views/mapa.py", title="05 · Mapa de Oportunidades", icon="🗺️"),
    st.Page("views/limites.py", title="06 · Datos, límites y ética", icon="⚖️"),
]
st.navigation(paginas).run()

with st.sidebar:
    st.caption("Fuente: BCRA · corte diciembre 2025")
    st.caption("Proyecto Integrador de Business Intelligence 2026 · Grupo 8")
