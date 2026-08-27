"""Reproducción única de tablas, verificaciones y paquete determinista."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd

from . import __version__
from .correspondencia import (
    _reproducir_desde_marcos,
    construir_catalogo_proporciones,
    construir_correspondencia_territorial,
    construir_trazabilidad_region_sitio,
)
from .datos import (
    directorio_datos,
    directorio_metodologia,
    extraer_parametros_valoracion,
    leer_base_forestal,
    leer_configuracion_correspondencia,
    leer_configuracion_regiones_sitios,
    leer_costos_contextuales,
    leer_escenarios,
    leer_evidencia_manglar,
    leer_fuente_dryad,
    leer_parametros_valoracion,
    leer_serie_historica,
    leer_sitios_referencia,
    raiz_repositorio,
)
from .escenarios import (
    calcular_escenarios_nacionales,
    construir_trayectorias,
    construir_trayectorias_monetarias,
    valorar_escenarios,
)
from .indicadores import (
    agregar_institucional,
    agregar_recuperacion,
    calcular_resultados_institucionales,
    calcular_resultados_recuperacion,
    completar_nacional_conservador,
    construir_comparacion_nacional,
    resumir_nacional_conservador,
)
from .mangle import (
    calcular_aproximacion_local,
    comparar_metodos_locales,
    derivar_intervalo_estructural,
    resumir_aproximacion_local,
)
from .validaciones import ejecutar_controles
from .valoracion import sensibilidad_valor_presente, valorar_comparacion_nacional


RUTAS_RESULTADOS = {
    "resultados_institucionales_nacionales": (
        "02_resultados_y_diccionario/resultados_institucionales_guatemala_2016_2020.csv"
    ),
    "resultados_institucionales_departamentales": (
        "02_resultados_y_diccionario/"
        "resultados_institucionales_departamentos_guatemala_2016_2020.csv"
    ),
    "resultados_institucionales_municipales": (
        "02_resultados_y_diccionario/"
        "resultados_institucionales_municipios_guatemala_2016_2020.csv"
    ),
    "catalogo_proporciones_recuperacion": (
        "02_resultados_y_diccionario/"
        "catalogo_proporciones_recuperacion_biomasa_20_anios.csv"
    ),
    "resultados_recuperacion_dominio": (
        "02_resultados_y_diccionario/"
        "resultados_recuperacion_ponderada_dominio_guatemala_2016_2020.csv"
    ),
    "resultados_recuperacion_regiones": (
        "02_resultados_y_diccionario/"
        "resultados_recuperacion_ponderada_regiones_guatemala_2016_2020.csv"
    ),
    "resultados_recuperacion_departamentos": (
        "02_resultados_y_diccionario/"
        "resultados_recuperacion_ponderada_departamentos_guatemala_2016_2020.csv"
    ),
    "resultados_recuperacion_municipios": (
        "02_resultados_y_diccionario/"
        "resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv"
    ),
    "transiciones_clasificacion_ponderada": (
        "02_resultados_y_diccionario/"
        "transiciones_clasificacion_ponderada_municipios_guatemala_2016_2020.csv"
    ),
    "municipios_cambio_clasificacion_ponderada": (
        "02_resultados_y_diccionario/"
        "cambios_clasificacion_ponderada_municipios_guatemala_2016_2020.csv"
    ),
    "completacion_nacional_unidades": (
        "02_resultados_y_diccionario/"
        "completacion_conservadora_unidades_guatemala_2016_2020.csv"
    ),
    "completacion_nacional_resumen": (
        "02_resultados_y_diccionario/"
        "completacion_conservadora_resumen_guatemala_2016_2020.csv"
    ),
    "resultados_forestales_nacionales": (
        "02_resultados_y_diccionario/resultados_forestales_guatemala_2016_2020.csv"
    ),
    "valoracion_resultados_forestales_nacionales": (
        "02_resultados_y_diccionario/"
        "valoracion_resultados_forestales_guatemala_2016_2020_precios_2026.csv"
    ),
    "sensibilidad_valor_presente": (
        "02_resultados_y_diccionario/"
        "sensibilidad_valor_presente_guatemala_precios_2026.csv"
    ),
    "escenarios_nacionales": (
        "02_resultados_y_diccionario/escenarios_forestales_guatemala_2026_2035.csv"
    ),
    "escenarios_valorados": (
        "02_resultados_y_diccionario/"
        "escenarios_forestales_valorados_guatemala_2026_2035.csv"
    ),
    "trayectorias_fisicas": (
        "02_resultados_y_diccionario/"
        "trayectorias_forestales_fisicas_guatemala_2026_2035.csv"
    ),
    "trayectorias_monetarias": (
        "02_resultados_y_diccionario/"
        "trayectorias_forestales_monetarias_guatemala_2026_2035.csv"
    ),
    "intervalo_estructural_local": (
        "02_resultados_y_diccionario/intervalo_estructural_manglar_guatemala.csv"
    ),
    "resultados_mangle_locales": (
        "02_resultados_y_diccionario/"
        "resultados_manglar_municipios_guatemala_2016_2020.csv"
    ),
    "comparacion_recuperacion_ponderada_mangle": (
        "02_resultados_y_diccionario/"
        "comparacion_recuperacion_ponderada_y_manglar_municipios_guatemala_2016_2020.csv"
    ),
    "resumen_mangle_local": (
        "02_resultados_y_diccionario/resumen_manglar_guatemala_2016_2020.csv"
    ),
}

RUTA_TRAZABILIDAD_MUNICIPAL = (
    "00_trazabilidad_fuentes/trazabilidad_municipio_region_guatemala_2016_2020.csv"
)
RUTA_TRAZABILIDAD_SITIOS = (
    "00_trazabilidad_fuentes/"
    "trazabilidad_region_sitio_recuperacion_biomasa_20_anios.csv"
)
RUTA_REPRODUCCION_SITIOS = (
    "05_verificacion/reproduccion_por_sitio_recuperacion_biomasa_20_anios.csv"
)
RUTA_CONTROLES = (
    "05_verificacion/controles_calidad_saldo_forestal_guatemala_2016_2020.csv"
)
RUTA_METADATOS = "05_verificacion/metadatos_ejecucion.json"
RUTA_MANIFIESTO = "05_verificacion/manifiesto_resultados.csv"
RUTA_ZIP = "build/resultados_saldo_forestal_guatemala.zip"


def _escribir_csv(df: pd.DataFrame, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, float_format="%.10f", lineterminator="\n")
    return ruta


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _crear_zip_determinista(archivos: list[Path], destino: Path, raiz: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for ruta in sorted(archivos, key=lambda p: str(p.relative_to(raiz))):
            info = zipfile.ZipInfo(str(ruta.relative_to(raiz)).replace("\\", "/"))
            info.date_time = (2026, 8, 26, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, ruta.read_bytes())
    return destino


def _directorio_metodologia_entrada(datos: Path) -> Path | None:
    """Reconoce una raíz alternativa que también contenga la metodología."""

    candidatas = [datos, datos.parent, datos / "01_metodologia"]
    for candidata in candidatas:
        if (
            candidata / "reglas_correspondencia_territorial_experta_codificada.json"
        ).is_file():
            return candidata
        if (
            candidata
            / "01_metodologia"
            / "reglas_correspondencia_territorial_experta_codificada.json"
        ).is_file():
            return candidata / "01_metodologia"
    return None


def ejecutar_reproduccion(
    repo_dir: Path | None = None,
    data_dir: Path | None = None,
) -> dict[str, pd.DataFrame | Path]:
    """Reconstruye resultados desde fuentes y escribe una sola copia canónica."""

    repo = Path(repo_dir or raiz_repositorio()).resolve()
    datos = Path(data_dir or directorio_datos()).resolve()
    metodologia_alternativa = _directorio_metodologia_entrada(datos)

    base = leer_base_forestal(datos)
    sitios = leer_sitios_referencia(datos)
    configuracion_territorial = leer_configuracion_correspondencia(
        metodologia_alternativa or directorio_metodologia()
    )
    configuracion_sitios = leer_configuracion_regiones_sitios(
        metodologia_alternativa or directorio_metodologia()
    )
    correspondencia = construir_correspondencia_territorial(
        base,
        configuracion_territorial,
    )
    catalogo = construir_catalogo_proporciones(configuracion_sitios, sitios)
    trazabilidad_sitios = construir_trazabilidad_region_sitio(
        configuracion_sitios,
        sitios,
    )
    reproduccion_sitios = _reproducir_desde_marcos(
        leer_fuente_dryad(datos),
        sitios,
    )

    evidencia = leer_evidencia_manglar(datos)
    historica = leer_serie_historica(datos)
    costos = leer_costos_contextuales(datos)
    directorio_parametros = metodologia_alternativa or directorio_metodologia()
    escenarios_def = leer_escenarios(directorio_parametros)
    parametros_valoracion = leer_parametros_valoracion(directorio_parametros)
    parametros = extraer_parametros_valoracion(parametros_valoracion)
    valor_unitario = parametros["valor_unitario_homologado"]
    tasa_descuento = parametros["tasa_descuento_central"]
    horizonte_servicios = int(parametros["horizonte_servicios"])
    horizonte_escenarios = int(parametros["horizonte_escenario"])

    institucional = calcular_resultados_institucionales(base)
    institucional_nacional = agregar_institucional(institucional)
    institucional_departamental = agregar_institucional(institucional, ["cod_dep", "depto"])
    institucional_municipal = institucional.loc[
        institucional["tipo_unidad"].eq("Municipio")
    ].copy()

    recuperacion = calcular_resultados_recuperacion(base, correspondencia, catalogo)
    recuperacion_nacional = agregar_recuperacion(recuperacion)
    recuperacion_regiones = agregar_recuperacion(
        recuperacion,
        ["proporcion_region_id", "region_nombre"],
    )
    recuperacion_departamental = agregar_recuperacion(recuperacion, ["cod_dep", "depto"])

    orden_institucional = ["Ganancia", "Equilibrio", "Pérdida"]
    orden_ponderado = ["Ganancia", "Indeterminado", "Pérdida"]
    transiciones = (
        pd.crosstab(
            pd.Categorical(
                recuperacion["clasificacion_institucional"],
                categories=orden_institucional,
                ordered=True,
            ),
            pd.Categorical(
                recuperacion["clasificacion_ponderada"],
                categories=orden_ponderado,
                ordered=True,
            ),
            dropna=False,
        )
        .rename_axis(index="clasificacion_institucional", columns="clasificacion_ponderada")
        .stack(future_stack=True)
        .rename("municipios")
        .reset_index()
    )
    total_origen = transiciones.groupby("clasificacion_institucional", observed=False)[
        "municipios"
    ].transform("sum")
    transiciones["porcentaje_fila"] = (
        100 * transiciones["municipios"] / total_origen.replace(0, pd.NA)
    ).fillna(0.0)
    cambios = recuperacion.loc[
        recuperacion["clasificacion_institucional"].ne(
            recuperacion["clasificacion_ponderada"]
        )
    ].copy()
    cambios["cambio_clasificacion"] = (
        cambios["clasificacion_institucional"]
        + " → "
        + cambios["clasificacion_ponderada"]
    )

    completacion = completar_nacional_conservador(base, recuperacion)
    completacion_resumen = resumir_nacional_conservador(completacion)
    comparacion_nacional = construir_comparacion_nacional(base, completacion)

    local = calcular_aproximacion_local(base, evidencia)
    local_resumen = resumir_aproximacion_local(local)
    local_comparacion = comparar_metodos_locales(local, recuperacion)
    intervalo_local = pd.DataFrame([derivar_intervalo_estructural(evidencia)])

    valoracion = valorar_comparacion_nacional(
        comparacion_nacional,
        valor_unitario=valor_unitario,
        tasa=tasa_descuento,
        horizonte_servicios=horizonte_servicios,
        horizonte_escenarios=horizonte_escenarios,
    )
    sensibilidad = sensibilidad_valor_presente(
        comparacion_nacional,
        valor_unitario=valor_unitario,
        horizonte_servicios=horizonte_servicios,
    )
    escenarios = calcular_escenarios_nacionales(
        completacion,
        escenarios_def,
        horizonte_escenarios=horizonte_escenarios,
    )
    escenarios_valorados = valorar_escenarios(
        escenarios,
        valor_unitario=valor_unitario,
        tasa=tasa_descuento,
        horizonte_servicios=horizonte_servicios,
        numero_cohortes=horizonte_escenarios,
    )
    trayectorias = construir_trayectorias(
        escenarios,
        horizonte_escenarios=horizonte_escenarios,
    )
    trayectorias_monetarias = construir_trayectorias_monetarias(
        escenarios,
        valor_unitario=valor_unitario,
        tasa=tasa_descuento,
        horizonte_servicios=horizonte_servicios,
        horizonte_escenarios=horizonte_escenarios,
    )

    controles = ejecutar_controles(
        base,
        correspondencia,
        catalogo,
        recuperacion,
        completacion,
        evidencia,
        local,
        local_comparacion,
        reproduccion_sitios,
    )

    productos: dict[str, pd.DataFrame] = {
        "serie_historica": historica,
        "parametros_valoracion": parametros_valoracion,
        "evidencia_manglar": evidencia,
        "costos_contextuales": costos,
        "trazabilidad_municipio_region": correspondencia,
        "trazabilidad_region_sitio": trazabilidad_sitios,
        "reproduccion_por_sitio": reproduccion_sitios,
        "resultados_institucionales_nacionales": institucional_nacional,
        "resultados_institucionales_departamentales": institucional_departamental,
        "resultados_institucionales_municipales": institucional_municipal,
        "catalogo_proporciones_recuperacion": catalogo,
        "resultados_recuperacion_dominio": recuperacion_nacional,
        "resultados_recuperacion_regiones": recuperacion_regiones,
        "resultados_recuperacion_departamentos": recuperacion_departamental,
        "resultados_recuperacion_municipios": recuperacion,
        "transiciones_clasificacion_ponderada": transiciones,
        "municipios_cambio_clasificacion_ponderada": cambios,
        "completacion_nacional_unidades": completacion,
        "completacion_nacional_resumen": completacion_resumen,
        "resultados_forestales_nacionales": comparacion_nacional,
        "valoracion_resultados_forestales_nacionales": valoracion,
        "sensibilidad_valor_presente": sensibilidad,
        "escenarios_nacionales": escenarios,
        "escenarios_valorados": escenarios_valorados,
        "trayectorias_fisicas": trayectorias,
        "trayectorias_monetarias": trayectorias_monetarias,
        "intervalo_estructural_local": intervalo_local,
        "resultados_mangle_locales": local,
        "comparacion_recuperacion_ponderada_mangle": local_comparacion,
        "resumen_mangle_local": local_resumen,
        "controles_calidad": controles,
    }

    archivos_publicados: list[Path] = []
    for nombre, ruta_relativa in RUTAS_RESULTADOS.items():
        archivos_publicados.append(_escribir_csv(productos[nombre], repo / ruta_relativa))
    archivos_publicados.extend(
        [
            _escribir_csv(correspondencia, repo / RUTA_TRAZABILIDAD_MUNICIPAL),
            _escribir_csv(trazabilidad_sitios, repo / RUTA_TRAZABILIDAD_SITIOS),
            _escribir_csv(reproduccion_sitios, repo / RUTA_REPRODUCCION_SITIOS),
            _escribir_csv(controles, repo / RUTA_CONTROLES),
        ]
    )

    metadatos = {
        "version": __version__,
        "version_metodo_correspondencia": configuracion_territorial["version_metodo"],
        "fecha_corte": "2026-08-26",
        "periodo_forestal": "2016-2020",
        "unidades_base": len(base),
        "municipios": int(base["tipo_unidad"].eq("Municipio").sum()),
        "municipios_con_proporcion": len(recuperacion),
        "municipios_excluidos": int(
            base["tipo_unidad"].eq("Municipio").sum() - len(recuperacion)
        ),
        "unidades_lacustres": int(base["tipo_unidad"].ne("Municipio").sum()),
        "municipios_mangle": len(local),
        "porcentajes_reproducidos_dryad": len(reproduccion_sitios),
        "valor_unitario_2026_gtq_ha_anio": valor_unitario,
        "tasa_descuento_central": tasa_descuento,
        "horizonte_servicios_anios": horizonte_servicios,
        "horizonte_escenarios_anios": horizonte_escenarios,
        "nota": (
            "La recuperación ponderada y la aproximación local de manglar se "
            "comparan sobre dominios superpuestos; no se suman."
        ),
    }
    metadatos_ruta = repo / RUTA_METADATOS
    metadatos_ruta.parent.mkdir(parents=True, exist_ok=True)
    metadatos_ruta.write_text(
        json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    archivos_publicados.append(metadatos_ruta)

    extras_documentales = [
        repo / "como_citar.txt",
        repo / "02_resultados_y_diccionario" / "diccionario_variables.csv",
        repo / "02_resultados_y_diccionario" / "guia_diccionario_variables.md",
        repo
        / "00_trazabilidad_fuentes"
        / "registro_fuentes_saldo_forestal_guatemala.csv",
        repo
        / "01_metodologia"
        / "metodologia_saldo_forestal_guatemala_2016_2020.md",
        repo / "04_reproduccion_python" / "instrucciones_reproduccion_python.md",
    ]
    archivos_sin_manifiesto = archivos_publicados + [
        ruta for ruta in extras_documentales if ruta.is_file()
    ]
    manifiesto = pd.DataFrame(
        [
            {
                "ruta": str(ruta.relative_to(repo)).replace("\\", "/"),
                "bytes": ruta.stat().st_size,
                "sha256": _sha256(ruta),
            }
            for ruta in archivos_sin_manifiesto
        ]
    ).sort_values("ruta").reset_index(drop=True)
    manifiesto_ruta = _escribir_csv(manifiesto, repo / RUTA_MANIFIESTO)
    zip_ruta = _crear_zip_determinista(
        archivos_sin_manifiesto + [manifiesto_ruta],
        repo / RUTA_ZIP,
        repo,
    )
    return {
        **productos,
        "manifiesto": manifiesto,
        "zip": zip_ruta,
    }
