"""Lectura, normalización y validación de las fuentes tabulares.

Los archivos derivados que venían embebidos en el cuaderno original se
conservan como referencias de regresión, pero el pipeline reconstruye los
resultados desde cuatro insumos: base forestal, dominio territorial, catálogo
de proporciones de recuperación y evidencia estructural PPM.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from .constantes import TIPO_MUNICIPIO, TOLERANCIA


RENOMBRES_BASE = {
    "ganancia_bruta_ha": "recuperacion_bruta_ha",
    "balance_neto_cobertura_ha": "perdida_neta_ha",
}


def raiz_repositorio() -> Path:
    """Devuelve la raíz del repositorio instalado en modo editable."""

    return Path(__file__).resolve().parents[2]


def directorio_datos() -> Path:
    """Resuelve el directorio de insumos, con opción de anulación por entorno."""

    configurado = os.environ.get("SALDO_FORESTAL_DATA_DIR")
    return Path(configurado).resolve() if configurado else raiz_repositorio() / "data" / "raw"


def _leer_csv(nombre: str, data_dir: Path | None = None) -> pd.DataFrame:
    ruta = (data_dir or directorio_datos()) / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el insumo requerido: {ruta}")
    df = pd.read_csv(ruta)
    for columna in ("codigo", "codigo_municipio", "cod_dep"):
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna], errors="coerce").astype("Int64")
    return df


def leer_base_forestal(data_dir: Path | None = None) -> pd.DataFrame:
    """Lee la base 2016–2020 y adopta nombres analíticos no ambiguos."""

    base = _leer_csv("base_forestal_2016_2020.csv", data_dir).rename(columns=RENOMBRES_BASE)
    validar_base_forestal(base)
    return base


def leer_dominio_poorter(data_dir: Path | None = None) -> pd.DataFrame:
    return _leer_csv("dominio_aplicacion_recuperacion.csv", data_dir)


def leer_catalogo_poorter(data_dir: Path | None = None) -> pd.DataFrame:
    catalogo = _leer_csv("catalogo_proporciones_recuperacion.csv", data_dir)
    requeridas = {"proporcion_region_id", "rho20_min", "rho20_central", "rho20_max"}
    if faltan := requeridas.difference(catalogo.columns):
        raise ValueError(f"Faltan columnas en el catálogo de proporciones: {sorted(faltan)}")
    proporciones = catalogo[["rho20_min", "rho20_central", "rho20_max"]]
    if not ((proporciones >= 0) & (proporciones <= 1)).all().all():
        raise ValueError("Las proporciones de recuperación deben estar en el intervalo [0, 1].")
    if not (
        (catalogo["rho20_min"] <= catalogo["rho20_central"])
        & (catalogo["rho20_central"] <= catalogo["rho20_max"])
    ).all():
        raise ValueError("Los límites de recuperación no están ordenados.")
    return catalogo


def leer_evidencia_ppm(data_dir: Path | None = None) -> pd.DataFrame:
    evidencia = _leer_csv("evidencia_ppm_estructural.csv", data_dir)
    validar_evidencia_ppm(evidencia)
    return evidencia


def leer_serie_historica(data_dir: Path | None = None) -> pd.DataFrame:
    return _leer_csv("serie_historica_bosques_2022.csv", data_dir)


def leer_escenarios(data_dir: Path | None = None) -> pd.DataFrame:
    escenarios = _leer_csv("escenarios_2026_2035.csv", data_dir)
    for columna in ("multiplicador_perdida_bruta", "multiplicador_recuperacion"):
        if (escenarios[columna] < 0).any():
            raise ValueError(f"{columna} no puede contener valores negativos.")
    return escenarios


def leer_costos_contextuales(data_dir: Path | None = None) -> pd.DataFrame:
    return _leer_csv("costos_contextuales.csv", data_dir)


def leer_parametros_valoracion(data_dir: Path | None = None) -> pd.DataFrame:
    """Lee y valida los parámetros monetarios que gobiernan el pipeline."""

    parametros = _leer_csv("parametros_valoracion.csv", data_dir)
    requeridas_columnas = {"parametro", "valor", "unidad", "fuente", "nota"}
    if faltan := requeridas_columnas.difference(parametros.columns):
        raise ValueError(f"Faltan columnas de parámetros de valoración: {sorted(faltan)}")
    if parametros["parametro"].duplicated().any():
        raise ValueError("Cada parámetro de valoración debe aparecer una sola vez.")

    requeridos = {
        "valor_unitario",
        "factor_homologacion",
        "valor_unitario_homologado",
        "tasa_descuento_central",
        "horizonte_servicios",
        "horizonte_escenario",
    }
    disponibles = set(parametros["parametro"])
    if faltan := requeridos.difference(disponibles):
        raise ValueError(f"Faltan parámetros de valoración: {sorted(faltan)}")

    valores = parametros.set_index("parametro")["valor"].astype(float)
    if (valores[list(requeridos)] <= 0).any():
        raise ValueError("Los parámetros monetarios y horizontes deben ser positivos.")
    if not 0 < valores["tasa_descuento_central"] < 1:
        raise ValueError("La tasa de descuento central debe estar entre cero y uno.")
    for nombre in ("horizonte_servicios", "horizonte_escenario"):
        if not float(valores[nombre]).is_integer():
            raise ValueError(f"{nombre} debe ser un número entero de años.")

    esperado = valores["valor_unitario"] * valores["factor_homologacion"]
    if not np.isclose(valores["valor_unitario_homologado"], esperado, atol=1e-8, rtol=1e-10):
        raise ValueError(
            "valor_unitario_homologado no coincide con valor_unitario × factor_homologacion."
        )
    return parametros


def extraer_parametros_valoracion(parametros: pd.DataFrame) -> dict[str, float]:
    """Convierte el registro largo validado en un diccionario numérico."""

    return parametros.set_index("parametro")["valor"].astype(float).to_dict()


def validar_base_forestal(base: pd.DataFrame) -> None:
    requeridas = {
        "cod_dep",
        "depto",
        "codigo",
        "municipio",
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "tipo_unidad",
    }
    if faltan := requeridas.difference(base.columns):
        raise ValueError(f"Faltan columnas en la base forestal: {sorted(faltan)}")
    if len(base) != 342:
        raise ValueError(f"Se esperaban 342 unidades; se encontraron {len(base)}.")
    if int(base["tipo_unidad"].eq(TIPO_MUNICIPIO).sum()) != 340:
        raise ValueError("La base debe contener 340 municipios.")
    if base.loc[base["tipo_unidad"].eq(TIPO_MUNICIPIO), "codigo"].duplicated().any():
        raise ValueError("Los códigos municipales deben ser únicos.")
    if (base[["perdida_bruta_ha", "recuperacion_bruta_ha"]].fillna(0) < 0).any().any():
        raise ValueError("Los flujos brutos no pueden ser negativos.")
    error = base["perdida_neta_ha"] - (
        base["perdida_bruta_ha"] - base["recuperacion_bruta_ha"]
    )
    if not np.allclose(error, 0, atol=TOLERANCIA, rtol=0):
        raise ValueError("No se cumple la identidad N = B - R por unidad.")


def validar_evidencia_ppm(evidencia: pd.DataFrame) -> None:
    componentes = evidencia[
        [
            "suben_carbono_y_area_basal",
            "bajan_carbono_y_area_basal",
            "trayectoria_mixta",
        ]
    ].sum(axis=1)
    series = evidencia["series_multitemporales"]
    # Los municipios sin una serie multitemporal comparable pueden registrar
    # parcelas adultas, pero no aportan a los tres componentes de trayectoria.
    mascara = series.gt(0)
    if not (componentes[mascara] == series[mascara]).all():
        raise ValueError("La composición PPM no reconcilia con las series multitemporales.")
    if evidencia["codigo_municipio"].duplicated().any():
        raise ValueError("La evidencia PPM debe contener un registro por municipio.")


def verificar_manifiesto(manifest_path: Path, base_dir: Path) -> pd.DataFrame:
    """Comprueba las huellas SHA-256 registradas para los archivos extraídos."""

    registros = json.loads(manifest_path.read_text(encoding="utf-8"))
    filas: list[dict[str, object]] = []
    for registro in registros:
        ruta_relativa = registro.get("ruta", registro["archivo"])
        ruta = base_dir / ruta_relativa
        observado = hashlib.sha256(ruta.read_bytes()).hexdigest() if ruta.exists() else None
        filas.append(
            {
                "archivo": registro["archivo"],
                "sha256_esperado": registro["sha256"],
                "sha256_observado": observado,
                "cumple": observado == registro["sha256"],
            }
        )
    return pd.DataFrame(filas)
