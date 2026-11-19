# Datos

Todos los datos son **públicos** y provienen del **Banco Central de la República Argentina (BCRA)**, con corte a diciembre de 2025.

| Archivo fuente (BCRA) | Se usa en |
|---|---|
| `MAIN_series_informe_anual_pagos_minoristas_2025.xlsx` — Pagos minoristas (tabla de hechos principal) | `fact_transacciones.csv` |
| Puntos de acceso a servicios financieros por tipo y provincia | `fact_puntos_acceso_provincia.csv` |
| Puntos de acceso por entidad, tipo y provincia | `fact_puntos_acceso_entidad.csv` |
| Puntos de acceso cada 10.000 adultos por tipo y provincia | `fact_puntos_acceso_tasas.csv` |
| Tenencia de cuentas bancarias y de pago por grupo etario | `fact_tenencia_cuentas.csv` |

## `data/processed/`
CSV del **modelo estrella** que quedó en Power BI tras la limpieza en Power Query. Se regeneran desde el `.pbix` con:

```bash
python scripts/export_pbix_data.py dashboard/TP_BI_Grupo8_final.pbix
```

Las coordenadas de `dim_provincia.csv` (`lat`, `lon`) son centroides aproximados, usados solo para ubicar las burbujas del mapa.
