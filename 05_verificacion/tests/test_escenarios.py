import numpy as np
import pandas as pd
import pytest

from saldo_forestal.datos import leer_escenarios
from saldo_forestal.escenarios import (
    aplicar_escenario,
    calcular_escenarios_nacionales,
    construir_trayectorias_monetarias,
    valorar_escenarios,
    validar_escenarios,
)


def test_aplicacion_separada():
    assert aplicar_escenario(100, 60, 0.5, 0.25, 2.0) == -35


def test_continuidad_reproduce_base(completacion):
    resultados = calcular_escenarios_nacionales(completacion, leer_escenarios())
    continuidad = resultados.loc[resultados["escenario"].eq("Continuidad")]
    ponderada = continuidad.loc[
        continuidad["regla"].eq("Saldo ponderado por recuperación")
    ].iloc[0]
    assert np.isclose(ponderada["resultado_inferior_ha_periodo_base"], 116_473.23156616)
    assert np.isclose(ponderada["resultado_superior_ha_periodo_base"], 123_988.02784436)


def test_multiplicadores_iguales_escalan_saldo(completacion):
    escenario = pd.DataFrame(
        [{
            "escenario": "Escala de prueba",
            "multiplicador_perdida_bruta": 2.5,
            "multiplicador_recuperacion": 2.5,
        }]
    )
    resultado = calcular_escenarios_nacionales(completacion, escenario)
    ponderada = resultado.loc[resultado["regla"].eq("Saldo ponderado por recuperación")].iloc[0]
    assert np.isclose(ponderada["resultado_inferior_ha_periodo_base"], 2.5 * 116_473.23156616)


def test_restauracion_exige_cambio_en_recuperacion():
    invalido = pd.DataFrame(
        [{
            "escenario": "Conservación y restauración",
            "multiplicador_perdida_bruta": 0.25,
            "multiplicador_recuperacion": 1.0,
        }]
    )
    with pytest.raises(ValueError, match="restauración"):
        validar_escenarios(invalido)


def test_trayectoria_monetaria_reconcilia_con_resultado_final(completacion):
    resultados = calcular_escenarios_nacionales(completacion, leer_escenarios())
    valorados = valorar_escenarios(resultados)
    trayectorias = construir_trayectorias_monetarias(resultados)
    final = trayectorias.loc[trayectorias["anio"].eq(2035)]
    comparada = valorados.merge(final, on=["escenario", "regla"], validate="one_to_one")
    assert np.allclose(
        comparada["vp_decada_inferior_gtq"],
        comparada["vp_acumulado_inferior_gtq"],
    )
