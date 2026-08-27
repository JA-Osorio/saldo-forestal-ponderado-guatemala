"""Lectura, normalización y validación de las fuentes canónicas."""

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
    """Devuelve la raíz que contiene los directorios numerados del proyecto."""

    ruta = Path(__file__).resolve()
    for candidata in ruta.parents:
        if (candidata / "00_trazabilidad_fuentes").is_dir() and (
            candidata / "01_metodologia"
        ).is_dir():
            return candidata
    return ruta.parents[3]


def directorio_datos() -> Path:
    """Resuelve el directorio de fuentes, con anulación opcional por entorno."""

    configurado = os.environ.get("SALDO_FORESTAL_DATA_DIR")
    return (
        Path(configurado).expanduser().resolve()
        if configurado
        else raiz_repositorio() / "00_trazabilidad_fuentes"
    )


def directorio_metodologia() -> Path:
    """Resuelve el directorio de configuración metodológica versionada."""

    configurado = os.environ.get("SALDO_FORESTAL_METODOLOGIA_DIR")
    return (
        Path(configurado).expanduser().resolve()
        if configurado
        else raiz_repositorio() / "01_metodologia"
    )


def _resolver_archivo(
    nombre: str,
    directorio: Path | None,
    predeterminado: Path,
    subdirectorio: str | None = None,
) -> Path:
    base = Path(directorio).resolve() if directorio is not None else predeterminado
    candidatas = [base / nombre]
    if subdirectorio:
        candidatas.insert(0, base / subdirectorio / nombre)
    candidatas.extend(
        [
            base / "00_trazabilidad_fuentes" / nombre,
            base / "01_metodologia" / nombre,
            base / "01_metodologia" / "parametros" / nombre,
        ]
    )
    for ruta in candidatas:
        if ruta.is_file():
            return ruta
    raise FileNotFoundError(
        "No se encontró el insumo requerido; se revisaron: "
        + ", ".join(str(ruta) for ruta in candidatas)
    )


def _leer_csv(
    nombre: str,
    data_dir: Path | None = None,
    *,
    predeterminado: Path | None = None,
    subdirectorio: str | None = None,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    ruta = _resolver_archivo(
        nombre,
        data_dir,
        predeterminado or directorio_datos(),
        subdirectorio,
    )
    df = pd.read_csv(ruta, encoding=encoding)
    for columna in ("codigo", "codigo_municipio", "cod_dep"):
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna], errors="coerce").astype("Int64")
    return df


def leer_base_forestal(data_dir: Path | None = None) -> pd.DataFrame:
    """Lee la base 2016–2020 y adopta nombres analíticos no ambiguos."""

    base = _leer_csv(
        "base_forestal_municipios_guatemala_2016_2020.csv",
        data_dir,
    ).rename(columns=RENOMBRES_BASE)
    validar_base_forestal(base)
    return base


def leer_configuracion_asignacion_territorial(
    metodologia_dir: Path | None = None,
) -> dict[str, object]:
    ruta = _resolver_archivo(
        "reglas_asignacion_grupos_territoriales.json",
        metodologia_dir,
        directorio_metodologia(),
    )
    return json.loads(ruta.read_text(encoding="utf-8"))


def leer_configuracion_grupos_sitios(
    metodologia_dir: Path | None = None,
) -> dict[str, object]:
    ruta = _resolver_archivo(
        "asignacion_grupos_sitios_referencia.json",
        metodologia_dir,
        directorio_metodologia(),
    )
    return json.loads(ruta.read_text(encoding="utf-8"))


def leer_sitios_referencia(data_dir: Path | None = None) -> pd.DataFrame:
    sitios = _leer_csv(
        "sitios_referencia_proporcion_regeneracion_equivalente.csv",
        data_dir,
    )
    requeridas = {
        "site_id",
        "site_name",
        "country",
        "relative_recovery_pct_20y",
        "source_locator",
    }
    if faltan := requeridas.difference(sitios.columns):
        raise ValueError(f"Faltan columnas en la fuente de sitios: {sorted(faltan)}")
    if sitios["site_id"].duplicated().any() or sitios["site_name"].duplicated().any():
        raise ValueError("Cada sitio de referencia debe tener identificadores únicos.")
    return sitios


def leer_fuente_dryad(data_dir: Path | None = None) -> pd.DataFrame:
    """Lee el CSV original de Dryad conservando su codificación ISO-8859-1."""

    return _leer_csv(
        "base_biomasa_bosques_secundarios_neotropicales_dryad.csv",
        data_dir,
        subdirectorio="fuentes_originales",
        encoding="latin-1",
    )


def leer_asignacion_territorial(
    data_dir: Path | None = None,
    configuracion: dict[str, object] | str | Path | None = None,
) -> pd.DataFrame:
    """Reconstruye el dominio territorial desde la fuente y su configuración."""

    from .asignacion_territorial import construir_asignacion_territorial

    configuracion_efectiva = configuracion or leer_configuracion_asignacion_territorial()
    return construir_asignacion_territorial(
        leer_base_forestal(data_dir),
        configuracion_efectiva,
    )


def leer_catalogo_proporcion_regeneracion_equivalente(
    data_dir: Path | None = None,
    configuracion: dict[str, object] | str | Path | None = None,
) -> pd.DataFrame:
    """Construye el catálogo por grupo desde sitios y configuración versionada."""

    from .asignacion_territorial import construir_catalogo_proporcion_regeneracion_equivalente

    configuracion_efectiva = configuracion or leer_configuracion_grupos_sitios()
    catalogo = construir_catalogo_proporcion_regeneracion_equivalente(
        configuracion_efectiva,
        leer_sitios_referencia(data_dir),
    )
    validar_catalogo_proporciones(catalogo)
    return catalogo


def leer_evidencia_manglar(data_dir: Path | None = None) -> pd.DataFrame:
    evidencia = _leer_csv(
        "evidencia_parcelas_permanentes_manglar_guatemala.csv",
        data_dir,
    )
    validar_evidencia_manglar(evidencia)
    return evidencia


def leer_serie_historica(data_dir: Path | None = None) -> pd.DataFrame:
    return _leer_csv(
        "serie_historica_cobertura_forestal_guatemala_1991_2016.csv",
        data_dir,
    )


def leer_escenarios(data_dir: Path | None = None) -> pd.DataFrame:
    escenarios = _leer_csv(
        "supuestos_escenarios_forestales_guatemala_2026_2035.csv",
        data_dir,
        predeterminado=directorio_metodologia(),
        subdirectorio="parametros",
    )
    for columna in ("multiplicador_perdida_bruta", "multiplicador_recuperacion"):
        if (escenarios[columna] < 0).any():
            raise ValueError(f"{columna} no puede contener valores negativos.")
    return escenarios


def leer_costos_contextuales(data_dir: Path | None = None) -> pd.DataFrame:
    return _leer_csv(
        "costos_contextuales_no_aditivos_guatemala_2026.csv",
        data_dir,
    )


def leer_parametros_valoracion(data_dir: Path | None = None) -> pd.DataFrame:
    """Lee y valida los parámetros monetarios que gobiernan la reproducción."""

    parametros = _leer_csv(
        "parametros_valoracion_servicios_ecosistemicos_guatemala_2019_2026.csv",
        data_dir,
        predeterminado=directorio_metodologia(),
        subdirectorio="parametros",
    )
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


def validar_catalogo_proporciones(catalogo: pd.DataFrame) -> None:
    requeridas = {"proporcion_grupo_id", "proporcion_regeneracion_equivalente_min", "proporcion_regeneracion_equivalente_central", "proporcion_regeneracion_equivalente_max"}
    if faltan := requeridas.difference(catalogo.columns):
        raise ValueError(f"Faltan columnas en el catálogo de proporciones: {sorted(faltan)}")
    proporciones = catalogo[["proporcion_regeneracion_equivalente_min", "proporcion_regeneracion_equivalente_central", "proporcion_regeneracion_equivalente_max"]]
    if not ((proporciones >= 0) & (proporciones <= 1)).all().all():
        raise ValueError("Las proporciones de recuperación deben estar en el intervalo [0, 1].")
    if not (
        (catalogo["proporcion_regeneracion_equivalente_min"] <= catalogo["proporcion_regeneracion_equivalente_central"])
        & (catalogo["proporcion_regeneracion_equivalente_central"] <= catalogo["proporcion_regeneracion_equivalente_max"])
    ).all():
        raise ValueError("Los límites de recuperación no están ordenados.")


def validar_evidencia_manglar(evidencia: pd.DataFrame) -> None:
    componentes = evidencia[
        [
            "suben_carbono_y_area_basal",
            "bajan_carbono_y_area_basal",
            "trayectoria_mixta",
        ]
    ].sum(axis=1)
    series = evidencia["series_multitemporales"]
    mascara = series.gt(0)
    if not (componentes[mascara] == series[mascara]).all():
        raise ValueError("La composición de parcelas no reconcilia con las series multitemporales.")
    if evidencia["codigo_municipio"].duplicated().any():
        raise ValueError("La evidencia debe contener un registro por municipio.")


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
