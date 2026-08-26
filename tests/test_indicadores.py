import numpy as np

from saldo_forestal.indicadores import (
    clasificar_intervalo,
    clasificar_saldo,
    intervalo_saldo_ponderado,
    proporcion_critica,
    saldo_neto,
    saldo_ponderado,
)


def test_saldos_elementales():
    assert saldo_neto(10, 4) == 6
    assert saldo_ponderado(10, 4, 0) == 10
    assert saldo_ponderado(10, 4, 1) == 6


def test_orientacion_del_intervalo():
    inferior, superior = intervalo_saldo_ponderado(100, 80, 0.25, 0.75)
    assert inferior == 40
    assert superior == 80
    assert inferior <= superior


def test_clasificaciones():
    assert clasificar_saldo(1) == "Pérdida"
    assert clasificar_saldo(-1) == "Ganancia"
    assert clasificar_saldo(0) == "Equilibrio"
    assert clasificar_intervalo(1, 2) == "Pérdida"
    assert clasificar_intervalo(-2, -1) == "Ganancia"
    assert clasificar_intervalo(-1, 1) == "Indeterminado"


def test_proporcion_critica():
    assert np.isclose(proporcion_critica(30, 60), 0.5)
    assert np.isnan(proporcion_critica(30, 0))
