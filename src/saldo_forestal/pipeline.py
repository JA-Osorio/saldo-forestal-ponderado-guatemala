"""Pipeline único para reconstruir tablas, manifiestos y descargas."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd

from . import __version__
from .datos import (
    directorio_datos,
    extraer_parametros_valoracion,
    leer_base_forestal,
    leer_catalogo_poorter,
    leer_costos_contextuales,
    leer_dominio_poorter,
    leer_escenarios,
    leer_evidencia_ppm,
    leer_parametros_valoracion,
    leer_serie_historica,
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
    agregar_poorter,
    calcular_resultados_institucionales,
    calcular_resultados_poorter,
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


CITA_CUADERNO = """CÓMO CITAR

Osorio, J. A. (2026). Deforestación bruta, recuperación y saldo forestal
ponderado en Guatemala (Versión 1.0.0) [Cuaderno reproducible]. Instituto de
Investigación en Ciencias Naturales y Tecnología, Universidad Rafael Landívar.
https://doi.org/10.5281/zenodo.22119075
"""


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


def ejecutar_pipeline(
    repo_dir: Path | None = None,
    data_dir: Path | None = None,
) -> dict[str, pd.DataFrame | Path]:
    repo = (repo_dir or raiz_repositorio()).resolve()
    datos = (data_dir or directorio_datos()).resolve()
    processed = repo / "data" / "processed"
    tablas = repo / "outputs" / "tables"
    descargas = repo / "outputs" / "downloads"

    base = leer_base_forestal(datos)
    dominio = leer_dominio_poorter(datos)
    catalogo = leer_catalogo_poorter(datos)
    evidencia = leer_evidencia_ppm(datos)
    historica = leer_serie_historica(datos)
    costos = leer_costos_contextuales(datos)
    escenarios_def = leer_escenarios(datos)
    parametros_valoracion = leer_parametros_valoracion(datos)
    parametros = extraer_parametros_valoracion(parametros_valoracion)
    valor_unitario = parametros["valor_unitario_homologado"]
    tasa_descuento = parametros["tasa_descuento_central"]
    horizonte_servicios = int(parametros["horizonte_servicios"])
    horizonte_escenarios = int(parametros["horizonte_escenario"])

    institucional = calcular_resultados_institucionales(base)
    institucional_nacional = agregar_institucional(institucional)
    institucional_departamental = agregar_institucional(institucional, ["cod_dep", "depto"])
    institucional_municipal = institucional.loc[institucional["tipo_unidad"].eq("Municipio")].copy()

    poorter = calcular_resultados_poorter(base, dominio, catalogo)
    poorter_nacional = agregar_poorter(poorter)
    poorter_regiones = agregar_poorter(poorter, ["proporcion_region_id", "region_nombre"])
    poorter_departamental = agregar_poorter(poorter, ["cod_dep", "depto"])

    orden_institucional = ["Ganancia", "Equilibrio", "Pérdida"]
    orden_ponderado = ["Ganancia", "Indeterminado", "Pérdida"]
    transiciones_poorter = (
        pd.crosstab(
            pd.Categorical(
                poorter["clasificacion_institucional"],
                categories=orden_institucional,
                ordered=True,
            ),
            pd.Categorical(
                poorter["clasificacion_ponderada"],
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
    total_origen = transiciones_poorter.groupby(
        "clasificacion_institucional", observed=False
    )[
        "municipios"
    ].transform("sum")
    transiciones_poorter["porcentaje_fila"] = (
        100 * transiciones_poorter["municipios"] / total_origen.replace(0, pd.NA)
    ).fillna(0.0)
    cambios_poorter = poorter.loc[
        poorter["clasificacion_institucional"].ne(poorter["clasificacion_ponderada"])
    ].copy()
    cambios_poorter["cambio_clasificacion"] = (
        cambios_poorter["clasificacion_institucional"]
        + " → "
        + cambios_poorter["clasificacion_ponderada"]
    )

    completacion = completar_nacional_conservador(base, poorter)
    completacion_resumen = resumir_nacional_conservador(completacion)
    comparacion_nacional = construir_comparacion_nacional(base, completacion)

    local = calcular_aproximacion_local(base, evidencia)
    local_resumen = resumir_aproximacion_local(local)
    local_comparacion = comparar_metodos_locales(local, poorter)
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
        catalogo,
        poorter,
        completacion,
        evidencia,
        local,
        local_comparacion,
    )

    productos: dict[str, pd.DataFrame] = {
        "serie_historica_1991_2016": historica,
        "parametros_valoracion_aplicados": parametros_valoracion,
        "resultados_institucionales_nacionales": institucional_nacional,
        "resultados_institucionales_departamentales": institucional_departamental,
        "resultados_institucionales_municipales": institucional_municipal,
        "catalogo_proporciones_poorter": catalogo,
        "resultados_poorter_dominio": poorter_nacional,
        "resultados_poorter_regiones": poorter_regiones,
        "resultados_poorter_departamentales": poorter_departamental,
        "resultados_poorter_municipales": poorter,
        "transiciones_clasificacion_poorter": transiciones_poorter,
        "municipios_cambio_clasificacion_poorter": cambios_poorter,
        "completacion_nacional_unidades": completacion,
        "completacion_nacional_resumen": completacion_resumen,
        "comparacion_reglas_nacional": comparacion_nacional,
        "valoracion_reglas_nacional": valoracion,
        "sensibilidad_valor_presente": sensibilidad,
        "escenarios_nacionales": escenarios,
        "escenarios_valorados": escenarios_valorados,
        "trayectorias_fisicas": trayectorias,
        "trayectorias_monetarias": trayectorias_monetarias,
        "evidencia_estructural_mangle": evidencia,
        "intervalo_estructural_local": intervalo_local,
        "resultados_mangle_locales": local,
        "comparacion_local_poorter_mangle": local_comparacion,
        "resumen_mangle_local": local_resumen,
        "costos_contextuales_no_aditivos": costos,
        "controles_calidad": controles,
    }

    nombres_publicacion = {
        "catalogo_proporciones_poorter": "catalogo_proporciones_recuperacion",
        "resultados_poorter_dominio": "resultados_dominio_recuperacion",
        "resultados_poorter_regiones": "resultados_regiones_recuperacion",
        "resultados_poorter_departamentales": "resultados_recuperacion_departamentales",
        "resultados_poorter_municipales": "resultados_recuperacion_municipales",
        "transiciones_clasificacion_poorter": "transiciones_clasificacion_ponderada",
        "municipios_cambio_clasificacion_poorter": "municipios_cambio_clasificacion_ponderada",
        "comparacion_local_poorter_mangle": "comparacion_local_recuperacion_mangle",
        "comparacion_reglas_nacional": "resultados_forestales_nacionales",
        "valoracion_reglas_nacional": "valoracion_resultados_forestales_nacionales",
    }
    archivos_publicados: list[Path] = []
    for nombre, marco in productos.items():
        nombre_publicado = nombres_publicacion.get(nombre, nombre)
        _escribir_csv(marco, processed / f"{nombre_publicado}.csv")
        publicado = _escribir_csv(marco, tablas / f"{nombre_publicado}.csv")
        archivos_publicados.append(publicado)

    metadatos = {
        "version": __version__,
        "fecha_corte": "2026-08-26",
        "periodo_forestal": "2016-2020",
        "unidades_base": len(base),
        "municipios": int(base["tipo_unidad"].eq("Municipio").sum()),
        "municipios_con_proporcion": len(poorter),
        "municipios_mangle": len(local),
        "valor_unitario_2026_gtq_ha_anio": valor_unitario,
        "tasa_descuento_central": tasa_descuento,
        "horizonte_servicios_anios": horizonte_servicios,
        "horizonte_escenarios_anios": horizonte_escenarios,
        "nota": "La recuperación ponderada y la aproximación local de manglar se comparan sobre dominios superpuestos; no se suman.",
    }
    metadatos_ruta = descargas / "metadatos_ejecucion.json"
    metadatos_ruta.parent.mkdir(parents=True, exist_ok=True)
    metadatos_ruta.write_text(json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cita_ruta = descargas / "COMO_CITAR.txt"
    cita_documental = repo / "docs" / "COMO_CITAR.txt"
    texto_cita = (
        cita_documental.read_text(encoding="utf-8")
        if cita_documental.exists()
        else CITA_CUADERNO
    )
    cita_ruta.write_text(texto_cita, encoding="utf-8")

    extras_documentales = [
        repo / "data" / "metadata" / "diccionario_variables.csv",
        repo / "data" / "metadata" / "registro_fuentes.csv",
        repo / "docs" / "metodologia.md",
        repo / "docs" / "reproduccion.md",
    ]
    archivos_zip_sin_manifiesto = archivos_publicados + [metadatos_ruta, cita_ruta] + [
        ruta for ruta in extras_documentales if ruta.exists()
    ]
    manifiesto = pd.DataFrame(
        [
            {
                "ruta": str(ruta.relative_to(repo)),
                "bytes": ruta.stat().st_size,
                "sha256": _sha256(ruta),
            }
            for ruta in archivos_zip_sin_manifiesto
        ]
    ).sort_values("ruta").reset_index(drop=True)
    manifiesto_ruta = _escribir_csv(manifiesto, descargas / "manifiesto_resultados.csv")
    archivos_zip = archivos_zip_sin_manifiesto + [manifiesto_ruta]
    zip_ruta = _crear_zip_determinista(
        archivos_zip,
        descargas / "resultados_saldo_forestal_guatemala.zip",
        repo,
    )
    return {
        **productos,
        "manifiesto": manifiesto,
        "como_citar": cita_ruta,
        "zip": zip_ruta,
    }
