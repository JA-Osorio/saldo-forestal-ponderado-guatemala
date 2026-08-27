import numpy as np

from saldo_forestal.indicadores import construir_comparacion_nacional
from saldo_forestal.valoracion import (
    factor_anualidad,
    valorar_comparacion_nacional,
    valor_presente_trayectoria,
)


def test_factores_anualidad():
    assert np.isclose(factor_anualidad(0, 25), 25)
    assert np.isclose(factor_anualidad(0.04, 25), 15.622080605)
    assert np.isclose(factor_anualidad(0.04, 10), 8.110895779)


def test_resultado_reportado_reproduce_fuente(base, completacion):
    comparacion = construir_comparacion_nacional(base, completacion)
    valoracion = valorar_comparacion_nacional(comparacion)
    neta = valoracion.loc[valoracion["regla"].eq("Pérdida neta reportada")].iloc[0]
    assert np.isclose(neta["flujo_anual_inferior_gtq"] / 1e6, 395.345451, atol=1e-6)
    assert np.isclose(neta["vp_cohorte_inferior_gtq"] / 1e6, 6_176.118244, atol=1e-6)
    assert np.isclose(neta["vp_diez_cohortes_inferior_gtq"] / 1e6, 50_093.851399, atol=1e-6)


def test_valoracion_nacional_ponderada(base, completacion):
    comparacion = construir_comparacion_nacional(base, completacion)
    valoracion = valorar_comparacion_nacional(comparacion)
    ponderada = valoracion.loc[
        valoracion["regla"].eq("Saldo ponderado por recuperación")
    ].iloc[0]
    assert np.isclose(ponderada["flujo_anual_inferior_gtq"] / 1e6, 873.156665, atol=1e-6)
    assert np.isclose(ponderada["flujo_anual_superior_gtq"] / 1e6, 929.492308, atol=1e-6)


def test_cohortes_constantes_equivalen_a_producto_de_factores():
    ha = 100
    unitario = 30_000
    observado = valor_presente_trayectoria([ha] * 10, unitario, 0.04, 25)
    esperado = ha * unitario * factor_anualidad(0.04, 25) * factor_anualidad(0.04, 10)
    assert np.isclose(observado, esperado)
