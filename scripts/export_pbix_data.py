"""Exporta el modelo de datos del .pbix (Grupo 8) a CSV + las medidas DAX a texto.

Uso:
    python scripts/export_pbix_data.py dashboard/TP_BI_Grupo8_final.pbix

Requiere: pip install pbixray
Genera:
    data/processed/*.csv      -> dimensiones y hechos del modelo estrella
    queries/measures.dax      -> todas las medidas DAX del reporte
    queries/calendario.dax    -> tabla calculada Calendario
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from pbixray import PBIXRay

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
QUERIES = ROOT / "queries"

# Coordenadas aproximadas (centroides) de las 24 jurisdicciones, para el mapa.
# El .pbix usa geocodificación de Azure Maps; acá las fijamos para no depender de un servicio externo.
CENTROIDES = {
    "Buenos Aires": (-36.6, -60.0), "CABA": (-34.61, -58.44), "Catamarca": (-27.33, -66.95),
    "Chaco": (-26.35, -60.75), "Chubut": (-43.8, -68.8), "Cordoba": (-32.1, -63.8),
    "Corrientes": (-28.8, -57.8), "Entre Rios": (-32.0, -59.2), "Formosa": (-24.9, -60.0),
    "Jujuy": (-23.3, -65.7), "La Pampa": (-37.1, -65.4), "La Rioja": (-29.7, -67.2),
    "Mendoza": (-34.6, -68.6), "Misiones": (-26.9, -54.6), "Neuquen": (-38.6, -70.0),
    "Rio Negro": (-40.4, -67.2), "Salta": (-24.6, -64.0), "San Juan": (-30.9, -68.9),
    "San Luis": (-33.7, -66.0), "Santa Cruz": (-48.8, -70.0), "Santa Fe": (-30.9, -60.9),
    "Santiago del Estero": (-27.8, -63.3),
    "Tierra del Fuego, Antartida e Islas del Atlantico": (-54.3, -67.7),
    "Tucuman": (-26.9, -65.3),
}


def _num(s: pd.Series) -> pd.Series:
    """Convierte texto con coma decimal ('4,11E+11', '2,0999') a float."""
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def main(pbix_path: str) -> None:
    m = PBIXRay(pbix_path)
    OUT.mkdir(parents=True, exist_ok=True)
    QUERIES.mkdir(parents=True, exist_ok=True)

    # --- Dimensiones ---
    prov = m.get_table("Dim_Provincia").copy()
    prov["Nombre_Corto"] = prov["Nombre"].replace(
        {"Tierra del Fuego, Antartida e Islas del Atlantico": "Tierra del Fuego"}
    )
    prov["lat"] = prov["Nombre"].map(lambda n: CENTROIDES[n][0])
    prov["lon"] = prov["Nombre"].map(lambda n: CENTROIDES[n][1])
    prov.drop(columns=["Ubicacion_Mapa"]).to_csv(OUT / "dim_provincia.csv", index=False)

    m.get_table("Dim_Conformada").to_csv(OUT / "dim_categoria.csv", index=False)
    m.get_table("Dim_Puntos_Acceso").to_csv(OUT / "dim_puntos_acceso.csv", index=False)
    m.get_table("Dim_Rango_Etario").to_csv(OUT / "dim_rango_etario.csv", index=False)
    m.get_table("Dim_Tipo_Cuenta").to_csv(OUT / "dim_tipo_cuenta.csv", index=False)
    m.get_table("Dim_Entidades").to_csv(OUT / "dim_entidades.csv", index=False)

    # --- Hechos ---
    tx = m.get_table("Fact_Transacciones").copy()
    tx["Fecha"] = pd.to_datetime(tx["Fecha"]).dt.date
    tx["Cantidades"] = tx["Cantidades"].astype("int64")
    tx["Monto"] = _num(tx["Monto"])
    tx[["ID_Categoria", "Fecha", "Cantidades", "Monto"]].to_csv(
        OUT / "fact_transacciones.csv", index=False)

    pa = m.get_table("Fact_Puntos_Acceso_Provincia").copy()
    pa["Cantidades"] = pa["Cantidades"].astype("int64")
    pa.to_csv(OUT / "fact_puntos_acceso_provincia.csv", index=False)

    tasas = m.get_table("Fact_Puntos_Acceso_Tasas").copy()
    tasas["Tasa_cada_10000"] = _num(tasas["Tasa_cada_10000"])
    tasas.to_csv(OUT / "fact_puntos_acceso_tasas.csv", index=False)

    ten = m.get_table("Fact_Tenencia_Cuentas").copy()
    ten["Cantidades"] = ten["Cantidades"].astype("int64")
    ten.to_csv(OUT / "fact_tenencia_cuentas.csv", index=False)

    fpa = m.get_table("Fact_Puntos_Acceso").copy()
    fpa["Cantidades"] = pd.to_numeric(fpa["Cantidades"], errors="coerce").astype("int64")
    fpa.rename(columns={"Tipo_Punto_Acceso": "ID_Punto_Acceso", "Entidad": "ID_Entidad",
                        "Provincia": "ID_Provincia"}).to_csv(
        OUT / "fact_puntos_acceso_entidad.csv", index=False)

    # --- DAX ---
    lines = ["// Medidas DAX del reporte (extraídas del .pbix con scripts/export_pbix_data.py)\n"]
    for _, r in m.dax_measures.iterrows():
        expr = r["Expression"]
        if not isinstance(expr, str) or not expr.strip():
            continue
        expr = expr.replace("\\n", "\n").strip()
        lines.append(f"// Tabla: {r['TableName']}\n{r['Name']} =\n{expr}\n")
    (QUERIES / "measures.dax").write_text("\n".join(lines), encoding="utf-8")

    cal = m.dax_tables[m.dax_tables["TableName"] == "Calendario"]["Expression"].iloc[0]
    (QUERIES / "calendario.dax").write_text(
        "// Tabla calculada Calendario\nCalendario =" + cal.replace("\\n", "\n"), encoding="utf-8")
    print("OK -> data/processed/*.csv, queries/measures.dax, queries/calendario.dax")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/export_pbix_data.py <ruta al .pbix>")
    main(sys.argv[1])
