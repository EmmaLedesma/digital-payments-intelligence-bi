"""Capa de datos: carga el modelo estrella (CSV) y expone las métricas del dashboard.

Todas las funciones son puras (sin Streamlit) para poder testearlas y reutilizarlas.
Las métricas replican las medidas DAX del .pbix (ver queries/measures.dax).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

# Categorías que son "medios de pago" (excluye canales Push y extracciones).
MEDIOS_PAGO_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]

ETIQUETAS = {
    1: "Cheques físicos",
    2: "Cheques electrónicos (Echeq)",
    3: "Transferencias inmediatas",
    4: "Transferencias interoperables",
    5: "Débitos directos",
    6: "Débitos inmediatos",
    7: "Tarjetas de crédito",
    8: "Tarjetas prepagas",
    9: "TI Push · cajeros automáticos",
    10: "TI Push · canales digitales",
    11: "Extracciones · cajeros automáticos",
    12: "Extracciones · extrabancarias (débito)",
    13: "Extracciones · extrabancarias (transferencia)",
    14: "Extracciones · cajeros automáticos (otros)",
    15: "Débito POS",
    16: "Débito por Internet",
}

ID_TI, ID_INTEROP, ID_TC, ID_ECHEQ = 3, 4, 7, 2
ID_POS, ID_INTERNET = 15, 16
ID_SOLO_BANCARIA, ID_SOLO_PAGO, ID_AMBAS, ID_ALGUNA = 1, 2, 3, 6

# Provincias que el informe prioriza para diagnóstico de campo.
PROVINCIAS_PRIORITARIAS = ["San Juan", "Formosa", "Tucuman"]


@dataclass(frozen=True)
class Datasets:
    tx: pd.DataFrame            # fact_transacciones + etiqueta
    categorias: pd.DataFrame
    provincias: pd.DataFrame
    puntos_acceso: pd.DataFrame
    pda_provincia: pd.DataFrame  # cantidad de puntos por provincia y tipo
    pda_tasas: pd.DataFrame      # puntos cada 10.000 adultos por provincia y tipo
    tenencia: pd.DataFrame       # tenencia de cuentas por edad y tipo
    rangos: pd.DataFrame
    tipos_cuenta: pd.DataFrame


@lru_cache(maxsize=1)
def load(data_dir: Path | None = None) -> Datasets:
    d = Path(data_dir) if data_dir else DATA_DIR
    categorias = pd.read_csv(d / "dim_categoria.csv")
    tx = pd.read_csv(d / "fact_transacciones.csv", parse_dates=["Fecha"])
    tx["Anio"] = tx["Fecha"].dt.year
    tx["Medio"] = tx["ID_Categoria"].map(ETIQUETAS)
    return Datasets(
        tx=tx,
        categorias=categorias,
        provincias=pd.read_csv(d / "dim_provincia.csv"),
        puntos_acceso=pd.read_csv(d / "dim_puntos_acceso.csv"),
        pda_provincia=pd.read_csv(d / "fact_puntos_acceso_provincia.csv"),
        pda_tasas=pd.read_csv(d / "fact_puntos_acceso_tasas.csv"),
        tenencia=pd.read_csv(d / "fact_tenencia_cuentas.csv"),
        rangos=pd.read_csv(d / "dim_rango_etario.csv"),
        tipos_cuenta=pd.read_csv(d / "dim_tipo_cuenta.csv"),
    )


# ───────────────────────── Transacciones ─────────────────────────
def _millones(s):
    return s / 1e6


def anios_disponibles(ds: Datasets) -> list[int]:
    """Años con medios de pago completos (los canales Push arrancan antes, en 2017)."""
    return sorted(ds.tx[ds.tx.ID_Categoria.isin(MEDIOS_PAGO_IDS)]["Anio"].unique().tolist())


def total_registros(ds: Datasets, anio: int | None = None) -> float:
    """Total de operaciones registradas (millones). Replica Total_Transacciones sin filtro de medio.

    OJO: suma todos los canales del modelo; las transferencias inmediatas aparecen también
    como canal 'Push', por lo que hay solapamiento (ver docs/data-model.md y sección de límites).
    """
    tx = ds.tx if anio is None else ds.tx[ds.tx.Anio == anio]
    return _millones(tx["Cantidades"].sum())


def operaciones(ds: Datasets, id_categoria: int, anio: int) -> float:
    tx = ds.tx[(ds.tx.ID_Categoria == id_categoria) & (ds.tx.Anio == anio)]
    return _millones(tx["Cantidades"].sum())


def variacion_anual(ds: Datasets, id_categoria: int, anio: int) -> float | None:
    """Crecimiento interanual en % (replica Crecimiento_YoY_%)."""
    prev, curr = operaciones(ds, id_categoria, anio - 1), operaciones(ds, id_categoria, anio)
    return None if prev == 0 else (curr - prev) / prev * 100


def operaciones_por_medio(ds: Datasets, anio: int) -> pd.DataFrame:
    tx = ds.tx[ds.tx.ID_Categoria.isin(MEDIOS_PAGO_IDS) & (ds.tx.Anio == anio)]
    out = tx.groupby("Medio", as_index=False)["Cantidades"].sum()
    out["Operaciones_M"] = _millones(out["Cantidades"])
    out["Share_%"] = out["Operaciones_M"] / out["Operaciones_M"].sum() * 100
    return out.sort_values("Operaciones_M", ascending=False).drop(columns="Cantidades")


def tabla_interanual(ds: Datasets, anio: int) -> pd.DataFrame:
    """Tabla del informe: operaciones del año previo vs. actual, variación % y absoluta."""
    rows = []
    for cid in MEDIOS_PAGO_IDS:
        prev, curr = operaciones(ds, cid, anio - 1), operaciones(ds, cid, anio)
        rows.append({
            "Medio de pago": ETIQUETAS[cid], "ID": cid,
            f"{anio - 1} (M)": prev, f"{anio} (M)": curr,
            "Variación %": (curr - prev) / prev * 100 if prev else float("nan"),
            "Operaciones sumadas (M)": curr - prev,
        })
    return pd.DataFrame(rows).sort_values("Variación %", ascending=False).reset_index(drop=True)


def serie_mensual(ds: Datasets, id_categoria: int) -> pd.DataFrame:
    tx = ds.tx[ds.tx.ID_Categoria == id_categoria].sort_values("Fecha")
    return pd.DataFrame({"Fecha": tx["Fecha"], "Operaciones_M": _millones(tx["Cantidades"])})


def serie_trimestral(ds: Datasets, ids: list[int]) -> pd.DataFrame:
    tx = ds.tx[ds.tx.ID_Categoria.isin(ids)].copy()
    tx["Trimestre"] = tx["Fecha"].dt.year.astype(str) + "-T" + tx["Fecha"].dt.quarter.astype(str)
    out = tx.groupby(["Trimestre", "Medio"], as_index=False)["Cantidades"].sum()
    out["Operaciones_M"] = _millones(out["Cantidades"])
    return out.sort_values("Trimestre")


def participacion_debito(ds: Datasets) -> pd.DataFrame:
    """% de débito por POS vs. Internet por año (replica Participacion_Debito_Internet_%)."""
    d = ds.tx[ds.tx.ID_Categoria.isin([ID_POS, ID_INTERNET])]
    p = d.pivot_table(index="Anio", columns="ID_Categoria", values="Cantidades", aggfunc="sum")
    p["Total"] = p[ID_POS] + p[ID_INTERNET]
    out = pd.DataFrame({
        "Anio": p.index,
        "Débito POS": (p[ID_POS] / p["Total"] * 100).values,
        "Débito por Internet": (p[ID_INTERNET] / p["Total"] * 100).values,
    })
    return out


# ───────────────────────── Cuentas ─────────────────────────
def resumen_tenencia(ds: Datasets) -> dict:
    t = ds.tenencia.groupby("ID_Tipo_Cuenta")["Cantidades"].sum()
    total = int(t[ID_ALGUNA])
    return {
        "total": total,
        "ambas": int(t[ID_AMBAS]), "solo_bancaria": int(t[ID_SOLO_BANCARIA]),
        "solo_pago": int(t[ID_SOLO_PAGO]),
        "ambas_%": t[ID_AMBAS] / total * 100,
        "solo_bancaria_%": t[ID_SOLO_BANCARIA] / total * 100,
        "solo_pago_%": t[ID_SOLO_PAGO] / total * 100,
    }


def tenencia_por_edad(ds: Datasets) -> pd.DataFrame:
    """Composición del tipo de cuenta por rango etario (% de quienes tienen alguna cuenta)."""
    t = ds.tenencia.merge(ds.rangos, on="ID_Etario")
    p = t.pivot_table(index=["ID_Etario", "Rango_Etario"], columns="ID_Tipo_Cuenta",
                      values="Cantidades", aggfunc="sum").reset_index()
    out = pd.DataFrame({
        "ID_Etario": p["ID_Etario"], "Rango etario": p["Rango_Etario"],
        "Solo cuenta bancaria": p[ID_SOLO_BANCARIA] / p[ID_ALGUNA] * 100,
        "Solo cuenta de pago": p[ID_SOLO_PAGO] / p[ID_ALGUNA] * 100,
        "Ambas cuentas": p[ID_AMBAS] / p[ID_ALGUNA] * 100,
        "Personas": p[ID_ALGUNA], "Personas solo pago": p[ID_SOLO_PAGO],
    })
    return out.sort_values("ID_Etario").reset_index(drop=True)


# ───────────────────────── Puntos de acceso ─────────────────────────
def puntos_por_provincia(ds: Datasets, id_tipo: int | None = None) -> pd.DataFrame:
    pa = ds.pda_provincia if id_tipo is None else ds.pda_provincia[ds.pda_provincia.ID_Punto_Acceso == id_tipo]
    return pa.groupby("ID_Provincia", as_index=False)["Cantidades"].sum().rename(columns={"Cantidades": "Puntos"})


def densidad_provincia(ds: Datasets, id_tipo: int | None = None) -> pd.DataFrame:
    """Puntos de acceso cada 10.000 adultos. Sin filtro = suma de los 5 tipos (como el .pbix)."""
    t = ds.pda_tasas if id_tipo is None else ds.pda_tasas[ds.pda_tasas.ID_Punto_Acceso == id_tipo]
    dens = t.groupby("ID_Provincia", as_index=False)["Tasa_cada_10000"].sum().rename(
        columns={"Tasa_cada_10000": "Cada_10000"})
    out = ds.provincias.merge(dens, on="ID_Provincia", how="left").merge(
        puntos_por_provincia(ds, id_tipo), on="ID_Provincia", how="left")
    out["Cada_10000"] = out["Cada_10000"].fillna(0.0)
    out["Puntos"] = out["Puntos"].fillna(0).astype(int)
    out["Prioritaria"] = out["Nombre"].isin(PROVINCIAS_PRIORITARIAS)
    return out.sort_values("Cada_10000").reset_index(drop=True)
