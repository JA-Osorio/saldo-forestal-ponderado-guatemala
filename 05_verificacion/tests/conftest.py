from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from saldo_forestal.correspondencia import (
    construir_catalogo_proporciones,
    construir_correspondencia_territorial,
    reproducir_porcentajes_sitios,
)
from saldo_forestal.datos import leer_base_forestal, leer_evidencia_manglar
from saldo_forestal.indicadores import (
    calcular_resultados_recuperacion,
    completar_nacional_conservador,
)
from saldo_forestal.mangle import calcular_aproximacion_local
from saldo_forestal.reproduccion import ejecutar_reproduccion


ARTEFACTOS_DERIVADOS_EN_FUENTES = {
    "trazabilidad_municipio_region_guatemala_2016_2020.csv",
    "trazabilidad_region_sitio_recuperacion_biomasa_20_anios.csv",
}


@pytest.fixture(scope="session")
def repo_dir() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def base():
    return leer_base_forestal()


@pytest.fixture(scope="session")
def correspondencia(base):
    return construir_correspondencia_territorial(base)


@pytest.fixture(scope="session")
def catalogo():
    return construir_catalogo_proporciones()


@pytest.fixture(scope="session")
def reproduccion_sitios():
    return reproducir_porcentajes_sitios()


@pytest.fixture(scope="session")
def resultados_recuperacion(base, correspondencia, catalogo):
    return calcular_resultados_recuperacion(base, correspondencia, catalogo)


@pytest.fixture(scope="session")
def completacion(base, resultados_recuperacion):
    return completar_nacional_conservador(base, resultados_recuperacion)


@pytest.fixture(scope="session")
def evidencia():
    return leer_evidencia_manglar()


@pytest.fixture(scope="session")
def local(base, evidencia):
    return calcular_aproximacion_local(base, evidencia)


@pytest.fixture(scope="session")
def preparar_repo_limpio(repo_dir):
    """Copia solo fuentes y configuración; nunca tablas finales congeladas."""

    def preparar(destino: Path) -> Path:
        trazabilidad = destino / "00_trazabilidad_fuentes"
        metodologia = destino / "01_metodologia"

        def ignorar_derivados(_directorio: str, nombres: list[str]) -> set[str]:
            return ARTEFACTOS_DERIVADOS_EN_FUENTES.intersection(nombres)

        shutil.copytree(
            repo_dir / "00_trazabilidad_fuentes",
            trazabilidad,
            ignore=ignorar_derivados,
        )
        shutil.copytree(repo_dir / "01_metodologia", metodologia)
        shutil.copy2(repo_dir / "como_citar.txt", destino / "como_citar.txt")
        return destino

    return preparar


@pytest.fixture(scope="session")
def ejecucion_limpia(tmp_path_factory, preparar_repo_limpio):
    raiz = preparar_repo_limpio(tmp_path_factory.mktemp("reproduccion_sin_finales"))
    assert not (raiz / "02_resultados_y_diccionario").exists()
    assert not (raiz / "05_verificacion").exists()
    resultado = ejecutar_reproduccion(
        repo_dir=raiz,
        data_dir=raiz / "00_trazabilidad_fuentes",
    )
    return {"raiz": raiz, "resultado": resultado}
