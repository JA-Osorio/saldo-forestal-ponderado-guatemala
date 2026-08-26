import numpy as np
import pytest

from saldo_forestal.errores import DominiosSuperpuestosError
from saldo_forestal.mangle import (
    comparar_metodos_locales,
    derivar_intervalo_estructural,
    validar_no_aditividad,
)


def test_intervalo_estructural(evidencia):
    intervalo = derivar_intervalo_estructural(evidencia)
    assert intervalo["series_multitemporales"] == 55
    assert intervalo["trayectorias_favorables"] == 30
    assert intervalo["trayectorias_desfavorables"] == 21
    assert intervalo["trayectorias_mixtas"] == 4
    assert np.isclose(intervalo["proporcion_estructural_min"], 30 / 55)
    assert np.isclose(intervalo["proporcion_estructural_max"], 34 / 55)


def test_resultado_local(local):
    assert len(local) == 13
    assert np.isclose(local["perdida_bruta_ha"].sum(), 12_990.36459838)
    assert np.isclose(local["recuperacion_bruta_ha"].sum(), 7_950.76021207)
    assert np.isclose(local["saldo_estructural_inferior_ha"].sum(), 8_075.34919455)
    assert np.isclose(local["saldo_estructural_superior_ha"].sum(), 8_653.58630089)


def test_soporte_comun_y_no_aditividad(poorter, local):
    comparacion = comparar_metodos_locales(local, poorter)
    assert len(comparacion) == 13
    assert comparacion["rho20_min"].notna().all()
    with pytest.raises(DominiosSuperpuestosError):
        validar_no_aditividad(poorter, local)
