"""Paleta, formato de números (es-AR) y componentes de UI compartidos."""
from __future__ import annotations

import streamlit as st

NAVY = "#0B1B3A"
TEAL = "#14B8A6"
GOLD = "#F5B700"
RED = "#E5484D"
BLUE = "#3B82F6"
SLATE = "#64748B"
LIGHT = "#F4F6FA"

PALETTE = ["#14B8A6", "#3B82F6", "#F5B700", "#8B5CF6", "#E5484D",
           "#0EA5E9", "#F97316", "#10B981", "#EC4899", "#64748B"]


def fmt(x: float, dec: int = 1) -> str:
    """Formato es-AR: 7478.5 -> '7.478,5'."""
    return f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def fmt_pct(x: float, dec: int = 1, signo: bool = False) -> str:
    s = f"{x:+.{dec}f}" if signo else f"{x:.{dec}f}"
    return s.replace(".", ",") + "%"


CSS = f"""
<style>
.block-container {{ padding-top: 2rem; max-width: 1280px; }}
.page-eyebrow {{ color:{TEAL}; font-weight:700; letter-spacing:.08em; font-size:.8rem; margin-bottom:0; }}
.page-title {{ color:{NAVY}; font-size:2rem; font-weight:800; margin:0 0 .2rem 0; line-height:1.15; }}
.page-sub {{ color:{SLATE}; margin-bottom:1.2rem; font-size:1rem; }}
.callout {{ border-left:4px solid {TEAL}; background:{LIGHT}; padding:.8rem 1rem; border-radius:6px;
            margin:.5rem 0 1rem 0; color:{NAVY}; }}
.callout.warn {{ border-left-color:{GOLD}; }}
.callout b {{ color:{NAVY}; }}
div[data-testid="stMetric"] {{ background:{LIGHT}; padding:.8rem 1rem; border-radius:10px;
                               border:1px solid #E2E8F0; }}
</style>
"""


def setup_page(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f'<p class="page-eyebrow">{eyebrow}</p><p class="page-title">{title}</p>'
                f'<p class="page-sub">{subtitle}</p>', unsafe_allow_html=True)


def callout(texto: str, warn: bool = False) -> None:
    clase = "callout warn" if warn else "callout"
    st.markdown(f'<div class="{clase}">{texto}</div>', unsafe_allow_html=True)
