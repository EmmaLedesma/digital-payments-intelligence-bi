"""Verifica que la réplica en Python reproduce las cifras publicadas en el informe del Grupo 8."""
import pytest

from payments_bi import data as D

ds = D.load()


# ── Pestaña 01: panorama ──
def test_totales_2025():
    assert D.total_registros(ds, 2025) == pytest.approx(21283.1, abs=0.05)
    assert D.total_registros(ds) == pytest.approx(69614.3, abs=0.05)


@pytest.mark.parametrize("cid,esperado", [(D.ID_TI, 7478.5), (D.ID_TC, 1866.1), (D.ID_ECHEQ, 34.3), (D.ID_INTEROP, 841.2)])
def test_operaciones_2025(cid, esperado):
    assert D.operaciones(ds, cid, 2025) == pytest.approx(esperado, abs=0.05)


# ── Pestaña 02: evolución ──
@pytest.mark.parametrize("cid,var", [
    (D.ID_INTEROP, 40.7), (D.ID_TI, 25.6), (8, 22.4), (D.ID_TC, 6.7), (D.ID_INTERNET, 5.4), (D.ID_POS, -19.4)])
def test_variacion_interanual(cid, var):
    assert D.variacion_anual(ds, cid, 2025) == pytest.approx(var, abs=0.05)


def test_transferencias_suman_1523_millones():
    t = D.tabla_interanual(ds, 2025).set_index("ID")
    assert t.loc[D.ID_TI, "Operaciones sumadas (M)"] == pytest.approx(1523.4, abs=0.05)


# ── Pestaña 03: adopción ──
def test_tenencia_total_y_composicion():
    r = D.resumen_tenencia(ds)
    assert r["total"] == 37_571_380
    assert (r["ambas"], r["solo_bancaria"], r["solo_pago"]) == (28_034_637, 7_513_296, 2_023_447)
    assert r["ambas_%"] == pytest.approx(74.6, abs=0.05)
    assert r["solo_bancaria_%"] == pytest.approx(20.0, abs=0.05)
    assert r["solo_pago_%"] == pytest.approx(5.4, abs=0.05)


def test_brecha_etaria():
    e = D.tenencia_por_edad(ds).set_index("Rango etario")
    assert e.loc["20 - 24", "Ambas cuentas"] == pytest.approx(90.4, abs=0.05)
    assert e.loc["70 - 74", "Ambas cuentas"] == pytest.approx(41.1, abs=0.05)


def test_participacion_debito_internet():
    d = D.participacion_debito(ds).set_index("Anio")
    assert d.loc[2024, "Débito por Internet"] == pytest.approx(19.6, abs=0.05)
    assert d.loc[2025, "Débito por Internet"] == pytest.approx(24.2, abs=0.05)


# ── Pestaña 05: mapa ──
def test_puntos_de_acceso():
    dens = D.densidad_provincia(ds).set_index("Nombre")
    assert dens["Puntos"].sum() == 42_381
    assert len(dens) == 24
    for prov, esperado in [("San Juan", 7.26), ("Formosa", 7.70), ("Tucuman", 8.70),
                           ("Buenos Aires", 9.36), ("La Pampa", 16.24)]:
        assert dens.loc[prov, "Cada_10000"] == pytest.approx(esperado, abs=0.005)
    assert dens.index[0] == "San Juan"  # menor densidad del país
    assert dens.loc["Buenos Aires", "Puntos"] / dens.loc["La Pampa", "Puntos"] == pytest.approx(26, abs=0.1)


# ── Integridad del modelo estrella ──
def test_integridad_referencial():
    assert set(ds.tx.ID_Categoria) <= set(ds.categorias.ID_Categoria)
    assert set(ds.pda_provincia.ID_Provincia) <= set(ds.provincias.ID_Provincia)
    assert set(ds.pda_tasas.ID_Provincia) <= set(ds.provincias.ID_Provincia)
    assert set(ds.tenencia.ID_Etario) <= set(ds.rangos.ID_Etario)
    assert set(ds.tenencia.ID_Tipo_Cuenta) <= set(ds.tipos_cuenta.ID_Tipo_Cuenta)
