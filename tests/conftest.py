from __future__ import annotations

from pathlib import Path

import pytest

from saldo_forestal.datos import (
    leer_base_forestal,
    leer_catalogo_poorter,
    leer_dominio_poorter,
    leer_evidencia_ppm,
)
from saldo_forestal.indicadores import (
    calcular_resultados_poorter,
    completar_nacional_conservador,
)
from saldo_forestal.mangle import calcular_aproximacion_local


@pytest.fixture(scope="session")
def repo_dir():
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def base():
    return leer_base_forestal()


@pytest.fixture(scope="session")
def dominio():
    return leer_dominio_poorter()


@pytest.fixture(scope="session")
def catalogo():
    return leer_catalogo_poorter()


@pytest.fixture(scope="session")
def evidencia():
    return leer_evidencia_ppm()


@pytest.fixture(scope="session")
def poorter(base, dominio, catalogo):
    return calcular_resultados_poorter(base, dominio, catalogo)


@pytest.fixture(scope="session")
def completacion(base, poorter):
    return completar_nacional_conservador(base, poorter)


@pytest.fixture(scope="session")
def local(base, evidencia):
    return calcular_aproximacion_local(base, evidencia)
