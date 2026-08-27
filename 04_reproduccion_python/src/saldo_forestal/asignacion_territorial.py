"""Reconstrucción trazable de la asignación territorial y sus proporciones.

Este módulo separa tres operaciones reproducibles: la asignación de las 342
unidades territoriales, la construcción del catálogo de proporciones de
regeneración equivalente y la verificación de los porcentajes publicados a
partir del CSV de Dryad. El horizonte de veinte años corresponde a la variable
de recuperación relativa de biomasa de la fuente, no al nombre del método.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .constantes import ESTADO_RECUPERACION_ELEGIBLE, TIPO_MUNICIPIO


FUENTE_UNIVERSO = "INAB_DINAMICA_2016_2020"
FUENTE_INTERVALO = "POORTER_ET_AL_2016"
SITIOS_REPRODUCIBLES_DRYAD = (
    "Salvatierra",
    "San Lorenzo",
    "Sao Paulo",
    "Chamela",
    "Nizanda",
    "Yucatán",
    "Chajul",
    "Barro Colorado Island",
    "Sarapiquí (Chazdon)",
    "Sarapiquí (Letcher)",
    "El Ocote 1",
    "El Ocote 2",
    "Santa Rosa",
)


def _cargar_json(configuracion: dict[str, Any] | str | Path | None, nombre: str) -> dict[str, Any]:
    if configuracion is None:
        from .datos import directorio_metodologia

        ruta = directorio_metodologia() / nombre
        return json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(configuracion, dict):
        return configuracion
    return json.loads(Path(configuracion).read_text(encoding="utf-8"))


def _expandir_codigos(expresiones: list[str]) -> set[int]:
    """Expande códigos individuales y rangos inclusivos de cuatro dígitos."""

    codigos: set[int] = set()
    for expresion in expresiones:
        texto = str(expresion).strip().replace("–", "-").replace("—", "-")
        if "-" in texto:
            inicio_texto, fin_texto = texto.split("-", maxsplit=1)
            inicio, fin = int(inicio_texto), int(fin_texto)
            if fin < inicio:
                raise ValueError(f"Rango municipal invertido: {expresion!r}.")
            nuevos = set(range(inicio, fin + 1))
        else:
            nuevos = {int(texto)}
        repetidos = codigos.intersection(nuevos)
        if repetidos:
            raise ValueError(f"Hay códigos repetidos dentro de una asignación: {sorted(repetidos)}")
        codigos.update(nuevos)
    return codigos


def construir_asignacion_territorial(
    base: pd.DataFrame,
    configuracion: dict[str, Any] | str | Path | None = None,
) -> pd.DataFrame:
    """Asigna las 342 unidades mediante listas explícitas y una regla residual."""

    especificacion = _cargar_json(
        configuracion,
        "reglas_asignacion_grupos_territoriales.json",
    )
    requeridas = {"cod_dep", "depto", "codigo", "municipio", "tipo_unidad"}
    if faltan := requeridas.difference(base.columns):
        raise ValueError(f"Faltan columnas en el universo territorial: {sorted(faltan)}")

    asignaciones: dict[int, dict[str, Any]] = {}
    for grupo in sorted(especificacion["grupos_territoriales"], key=lambda fila: fila["prioridad"]):
        codigos = _expandir_codigos(grupo["codigos"])
        superpuestos = set(asignaciones).intersection(codigos)
        if superpuestos:
            raise ValueError(
                "Las listas de asignación deben ser disjuntas; "
                f"códigos superpuestos: {sorted(superpuestos)}"
            )
        proporcion_grupo_id = grupo.get("proporcion_grupo_id")
        if not proporcion_grupo_id:
            raise ValueError(f"El grupo {grupo['grupo_territorial_id']} no identifica su proporción.")
        for codigo in codigos:
            asignaciones[codigo] = {
                **grupo,
                "proporcion_grupo_id": proporcion_grupo_id,
            }

    municipales = base.loc[base["tipo_unidad"].eq(TIPO_MUNICIPIO), "codigo"]
    if municipales.isna().any():
        raise ValueError("Todo municipio debe tener código.")
    universo_codigos = set(municipales.astype(int))
    desconocidos = set(asignaciones).difference(universo_codigos)
    if desconocidos:
        raise ValueError(f"La configuración contiene códigos ajenos al universo: {sorted(desconocidos)}")

    residual = especificacion["regla_residual"]
    no_municipal = especificacion["regla_no_municipal"]
    filas: list[dict[str, Any]] = []
    for fila in base.itertuples(index=False):
        codigo = getattr(fila, "codigo")
        es_municipio = getattr(fila, "tipo_unidad") == TIPO_MUNICIPIO
        if not es_municipio:
            decision = no_municipal
            ruta_asignacion = "unidad_no_municipal"
            origen_decision = "atributo_directo_de_la_fuente"
            decision_manual = "no_aplica"
            revision_ecologica = "no_aplica"
        else:
            codigo_entero = int(codigo)
            if codigo_entero in asignaciones:
                decision = asignaciones[codigo_entero]
                ruta_asignacion = "lista_explicita"
            else:
                decision = residual
                ruta_asignacion = "regla_residual"
            origen_decision = "procedimiento_reconstruido"
            decision_manual = "si"
            revision_ecologica = decision.get("revision_ecologica", "pendiente")

        proporcion_grupo_id = decision.get("proporcion_grupo_id")
        estado = decision["estado_dominio"]
        if es_municipio and proporcion_grupo_id:
            estado = ESTADO_RECUPERACION_ELEGIBLE
        codigo_entero = int(codigo) if pd.notna(codigo) else None
        filas.append(
            {
                "cod_dep": int(getattr(fila, "cod_dep")),
                "depto": getattr(fila, "depto"),
                "codigo": codigo_entero,
                "codigo_canonico": f"{codigo_entero:04d}" if codigo_entero is not None else None,
                "municipio": getattr(fila, "municipio"),
                "grupo_territorial_id": decision["grupo_territorial_id"],
                "grupo_territorial_nombre": decision["grupo_territorial_nombre"],
                "estado_dominio": estado,
                "proporcion_grupo_id": proporcion_grupo_id,
                "regla_id": decision["regla_id"],
                "ruta_asignacion": ruta_asignacion,
                "criterio_agrupacion": decision["criterio_agrupacion"],
                "asignacion_fijada_en_regla": decision_manual,
                "origen_decision": origen_decision,
                "estado_evidencia": decision["estado_evidencia"],
                "revision_ecologica": revision_ecologica,
                "fuente_universo": FUENTE_UNIVERSO,
                "fuente_intervalo": FUENTE_INTERVALO if proporcion_grupo_id else None,
                "version_metodo": especificacion["version_metodo"],
            }
        )

    resultado = pd.DataFrame(filas)
    resultado["codigo"] = pd.array(resultado["codigo"], dtype="Int64")
    conteos = resultado["estado_dominio"].value_counts()
    esperados = {
        ESTADO_RECUPERACION_ELEGIBLE: 172,
        "fuera_dominio_regla_residual": 168,
        "unidad_no_municipal": 2,
    }
    if any(int(conteos.get(estado, 0)) != cantidad for estado, cantidad in esperados.items()):
        raise ValueError(f"La partición territorial no coincide con 172/168/2: {conteos.to_dict()}")
    if resultado.loc[
        resultado["estado_dominio"].eq(ESTADO_RECUPERACION_ELEGIBLE), "codigo"
    ].duplicated().any():
        raise ValueError("La asignación territorial contiene municipios elegibles duplicados.")
    return resultado


def _leer_sitios_por_defecto() -> pd.DataFrame:
    from .datos import leer_sitios_referencia

    return leer_sitios_referencia()


def _formatear_intervalo(porcentaje_min: float, porcentaje_max: float) -> str:
    def formatear(valor: float) -> str:
        return f"{valor:.1f}".rstrip("0").rstrip(".")

    if np.isclose(porcentaje_min, porcentaje_max):
        return f"{formatear(porcentaje_min)}%"
    return f"{formatear(porcentaje_min)}-{formatear(porcentaje_max)}%"


def construir_catalogo_proporcion_regeneracion_equivalente(
    configuracion: dict[str, Any] | str | Path | None = None,
    sitios: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Construye las cinco proporciones por grupo desde los valores por sitio."""

    especificacion = _cargar_json(
        configuracion,
        "asignacion_grupos_sitios_referencia.json",
    )
    sitios_fuente = (sitios.copy() if sitios is not None else _leer_sitios_por_defecto())
    requeridas = {"site_name", "relative_recovery_pct_20y"}
    if faltan := requeridas.difference(sitios_fuente.columns):
        raise ValueError(f"Faltan columnas en los sitios de referencia: {sorted(faltan)}")
    if sitios_fuente["site_name"].duplicated().any():
        raise ValueError("Los nombres de sitio deben ser únicos.")
    sitios_indice = sitios_fuente.set_index("site_name")

    territorial = _cargar_json(
        None,
        "reglas_asignacion_grupos_territoriales.json",
    )
    nombres_grupos = {
        grupo["proporcion_grupo_id"]: grupo["grupo_territorial_nombre"]
        for grupo in territorial["grupos_territoriales"]
    }
    filas: list[dict[str, Any]] = []
    for grupo in especificacion["grupos_territoriales"]:
        proporcion_grupo_id = grupo["proporcion_grupo_id"]
        nombres = grupo["sitios_numericos"]
        faltantes = set(nombres).difference(sitios_indice.index)
        if faltantes:
            raise ValueError(
                f"Faltan sitios numéricos para {proporcion_grupo_id}: {sorted(faltantes)}"
            )
        valores = pd.to_numeric(
            sitios_indice.loc[nombres, "relative_recovery_pct_20y"],
            errors="coerce",
        )
        if valores.isna().any():
            raise ValueError(f"Hay sitios numéricos sin porcentaje en {proporcion_grupo_id}.")
        porcentaje_min = float(valores.min())
        porcentaje_max = float(valores.max())
        proporcion_regeneracion_equivalente_min_bruto = porcentaje_min / 100
        proporcion_regeneracion_equivalente_max_bruto = porcentaje_max / 100
        redondeo = grupo.get("redondeo", "ninguno")
        if redondeo == "minimo_hacia_abajo_y_maximo_hacia_arriba_a_incrementos_de_0.05":
            proporcion_regeneracion_equivalente_min = math.floor((proporcion_regeneracion_equivalente_min_bruto + 1e-12) / 0.05) * 0.05
            proporcion_regeneracion_equivalente_max = math.ceil((proporcion_regeneracion_equivalente_max_bruto - 1e-12) / 0.05) * 0.05
        elif redondeo == "ninguno":
            proporcion_regeneracion_equivalente_min, proporcion_regeneracion_equivalente_max = proporcion_regeneracion_equivalente_min_bruto, proporcion_regeneracion_equivalente_max_bruto
        else:
            raise ValueError(f"Operación de redondeo no reconocida: {redondeo!r}")

        filas.append(
            {
                "proporcion_grupo_id": proporcion_grupo_id,
                "grupo_territorial_nombre": grupo.get(
                    "grupo_territorial_nombre",
                    nombres_grupos.get(proporcion_grupo_id, proporcion_grupo_id),
                ),
                "sitios_referencia": grupo["etiqueta_sitios"],
                "intervalo_proporcion_regeneracion_equivalente": _formatear_intervalo(
                    100 * proporcion_regeneracion_equivalente_min,
                    100 * proporcion_regeneracion_equivalente_max,
                ),
                "proporcion_regeneracion_equivalente_min": proporcion_regeneracion_equivalente_min,
                "proporcion_regeneracion_equivalente_central": (proporcion_regeneracion_equivalente_min + proporcion_regeneracion_equivalente_max) / 2,
                "proporcion_regeneracion_equivalente_max": proporcion_regeneracion_equivalente_max,
                "tratamiento_intervalo": grupo["tratamiento_intervalo"],
                "fundamento_vinculacion_sitios": grupo["fundamento_vinculacion_sitios"],
            }
        )

    catalogo = pd.DataFrame(filas)
    if len(catalogo) != 5 or not catalogo["proporcion_grupo_id"].is_unique:
        raise ValueError("El catálogo debe contener cinco grupos territoriales únicos.")
    return catalogo


def construir_resumen_grupos_territoriales(
    catalogo: pd.DataFrame,
    configuracion: dict[str, Any] | str | Path | None = None,
) -> pd.DataFrame:
    """Integra criterios, referencias, intervalos y aplicación en una sola tabla."""

    especificacion = _cargar_json(
        configuracion,
        "reglas_asignacion_grupos_territoriales.json",
    )
    catalogo_indice = catalogo.set_index("proporcion_grupo_id")
    filas: list[dict[str, Any]] = []

    for orden, grupo in enumerate(
        sorted(especificacion["grupos_territoriales"], key=lambda fila: fila["prioridad"]),
        start=1,
    ):
        grupo_id = grupo["proporcion_grupo_id"]
        if grupo_id not in catalogo_indice.index:
            raise ValueError(f"Falta el intervalo del grupo territorial {grupo_id}.")
        intervalo = catalogo_indice.loc[grupo_id]
        filas.append(
            {
                "orden": orden,
                "grupo_territorial_id": grupo["grupo_territorial_id"],
                "grupo_territorial_nombre": grupo["grupo_territorial_nombre"],
                "tipo_unidad_analitica": "municipios_con_proporcion",
                "criterio_agrupacion": grupo["criterio_agrupacion"],
                "territorios_sitios_referencia": intervalo["sitios_referencia"],
                "fundamento_vinculacion_sitios": intervalo[
                    "fundamento_vinculacion_sitios"
                ],
                "intervalo_proporcion_regeneracion_equivalente": intervalo[
                    "intervalo_proporcion_regeneracion_equivalente"
                ],
                "proporcion_regeneracion_equivalente_min": intervalo[
                    "proporcion_regeneracion_equivalente_min"
                ],
                "proporcion_regeneracion_equivalente_central": intervalo[
                    "proporcion_regeneracion_equivalente_central"
                ],
                "proporcion_regeneracion_equivalente_max": intervalo[
                    "proporcion_regeneracion_equivalente_max"
                ],
                "tratamiento_intervalo": intervalo["tratamiento_intervalo"],
                "aplicacion_calculo": (
                    "Se aplica el intervalo a la recuperación reportada"
                ),
                "unidades": int(grupo["conteo_municipios"]),
                "codigos_municipales": ", ".join(grupo["codigos"]),
            }
        )

    residual = especificacion["regla_residual"]
    no_municipal = especificacion["regla_no_municipal"]
    filas.extend(
        [
            {
                "orden": 6,
                "grupo_territorial_id": residual["grupo_territorial_id"],
                "grupo_territorial_nombre": residual["grupo_territorial_nombre"],
                "tipo_unidad_analitica": "municipios_fuera_del_dominio",
                "criterio_agrupacion": residual["criterio_agrupacion"],
                "territorios_sitios_referencia": "No se asignan",
                "fundamento_vinculacion_sitios": "No aplica",
                "intervalo_proporcion_regeneracion_equivalente": "No aplica",
                "proporcion_regeneracion_equivalente_min": np.nan,
                "proporcion_regeneracion_equivalente_central": np.nan,
                "proporcion_regeneracion_equivalente_max": np.nan,
                "tratamiento_intervalo": "No se asigna un intervalo",
                "aplicacion_calculo": "Se conserva N = B − R reportado por INAB y CONAP",
                "unidades": int(
                    especificacion["conteos_esperados"]["municipios_excluidos"]
                ),
                "codigos_municipales": "Códigos no incluidos en las cinco listas",
            },
            {
                "orden": 7,
                "grupo_territorial_id": no_municipal["grupo_territorial_id"],
                "grupo_territorial_nombre": no_municipal["grupo_territorial_nombre"],
                "tipo_unidad_analitica": "unidades_lacustres_no_municipales",
                "criterio_agrupacion": no_municipal["criterio_agrupacion"],
                "territorios_sitios_referencia": "No aplica",
                "fundamento_vinculacion_sitios": "No aplica",
                "intervalo_proporcion_regeneracion_equivalente": "No aplica",
                "proporcion_regeneracion_equivalente_min": np.nan,
                "proporcion_regeneracion_equivalente_central": np.nan,
                "proporcion_regeneracion_equivalente_max": np.nan,
                "tratamiento_intervalo": "Fuera de la clasificación municipal",
                "aplicacion_calculo": "Se conserva N = B − R en la suma nacional",
                "unidades": int(
                    especificacion["conteos_esperados"]["unidades_lacustres"]
                ),
                "codigos_municipales": "No aplica",
            },
        ]
    )
    resumen = pd.DataFrame(filas).sort_values("orden").reset_index(drop=True)
    if len(resumen) != 7 or int(resumen["unidades"].sum()) != 342:
        raise ValueError("El resumen territorial debe reconciliar 172 + 168 + 2 unidades.")
    return resumen


def construir_trazabilidad_grupo_sitio(
    configuracion: dict[str, Any] | str | Path | None = None,
    sitios: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Registra el uso numérico o contextual de cada sitio por grupo territorial."""

    especificacion = _cargar_json(
        configuracion,
        "asignacion_grupos_sitios_referencia.json",
    )
    sitios_fuente = (sitios.copy() if sitios is not None else _leer_sitios_por_defecto())
    sitios_indice = sitios_fuente.set_index("site_name", drop=False)
    territorial = _cargar_json(
        None,
        "reglas_asignacion_grupos_territoriales.json",
    )
    nombres_grupos = {
        grupo["proporcion_grupo_id"]: grupo["grupo_territorial_nombre"]
        for grupo in territorial["grupos_territoriales"]
    }
    filas: list[dict[str, Any]] = []
    for grupo in especificacion["grupos_territoriales"]:
        proporcion_grupo_id = grupo["proporcion_grupo_id"]
        usos = [
            ("sitios_numericos", "numerico"),
            ("sitios_contextuales_sin_porcentaje", "contextual_sin_porcentaje"),
            ("sitios_secos_asignados_a_otro_grupo", "asignado_a_otro_grupo"),
        ]
        for campo, uso in usos:
            for nombre in grupo.get(campo, []):
                if nombre not in sitios_indice.index:
                    raise ValueError(f"El sitio {nombre!r} no existe en la fuente tabular.")
                sitio = sitios_indice.loc[nombre]
                if isinstance(sitio, pd.DataFrame):
                    raise ValueError(f"El sitio {nombre!r} aparece más de una vez.")
                filas.append(
                    {
                        "proporcion_grupo_id": proporcion_grupo_id,
                        "grupo_territorial_nombre": grupo.get(
                            "grupo_territorial_nombre",
                            nombres_grupos.get(proporcion_grupo_id, proporcion_grupo_id),
                        ),
                        "site_id": sitio["site_id"],
                        "site_name": sitio["site_name"],
                        "country": sitio["country"],
                        "rainfall_mm": sitio["rainfall_mm"],
                        "relative_recovery_pct_20y": sitio["relative_recovery_pct_20y"],
                        "uso_sitio": uso,
                        "regla_intervalo": grupo["regla_intervalo"],
                        "redondeo": grupo.get("redondeo", "ninguno"),
                        "fuente_verificacion": (
                            "tabla_ampliada"
                            if sitio["site_name"] == "Quintana Roo"
                            else "csv_dryad_y_tabla_ampliada"
                        ),
                        "source_locator": sitio["source_locator"],
                        "version_metodo": especificacion["version_metodo"],
                    }
                )
    return pd.DataFrame(filas)


def _reproducir_desde_marcos(
    dryad: pd.DataFrame,
    sitios: pd.DataFrame,
) -> pd.DataFrame:
    requeridas_dryad = {"Chronosequence", "Age", "AGB"}
    if faltan := requeridas_dryad.difference(dryad.columns):
        raise ValueError(f"Faltan columnas en el CSV de Dryad: {sorted(faltan)}")
    fuente = dryad.copy()
    fuente["AGB"] = pd.to_numeric(fuente["AGB"], errors="coerce")
    fuente = fuente.loc[
        fuente["AGB"].le(500) & fuente["Chronosequence"].ne("Marqués de Comillas")
    ].copy()
    publicados = sitios.set_index("site_name")

    filas: list[dict[str, Any]] = []
    for nombre in SITIOS_REPRODUCIBLES_DRYAD:
        if nombre not in publicados.index:
            raise ValueError(f"Falta el valor publicado del sitio {nombre!r}.")
        observaciones = fuente.loc[fuente["Chronosequence"].eq(nombre)].copy()
        bosque_maduro = observaciones.loc[observaciones["Age"].astype(str).eq("OG"), "AGB"]
        edades = pd.to_numeric(observaciones["Age"], errors="coerce")
        secundario = observaciones.loc[edades.gt(0) & observaciones["AGB"].notna()].copy()
        edad_secundaria = pd.to_numeric(secundario["Age"], errors="raise").to_numpy(float)
        if len(secundario) < 2 or bosque_maduro.empty:
            raise ValueError(f"El sitio {nombre!r} no permite reproducir el porcentaje.")

        pendiente, intercepto = np.polyfit(
            np.log(edad_secundaria),
            secundario["AGB"].to_numpy(float),
            1,
        )
        agb20 = float(intercepto + pendiente * np.log(20))
        mediana_bosque_maduro = float(bosque_maduro.median())
        porcentaje = 100 * agb20 / mediana_bosque_maduro
        porcentaje_publicado = float(publicados.loc[nombre, "relative_recovery_pct_20y"])
        porcentaje_redondeado = round(porcentaje, 1)
        filas.append(
            {
                "site_id": publicados.loc[nombre, "site_id"],
                "site_name": nombre,
                "observaciones_bosque_secundario": len(secundario),
                "observaciones_bosque_maduro": len(bosque_maduro),
                "agb20_reproducida_mg_ha": agb20,
                "agb_bosque_maduro_mediana_mg_ha": mediana_bosque_maduro,
                "porcentaje_publicado": porcentaje_publicado,
                "porcentaje_reproducido": porcentaje,
                "porcentaje_reproducido_redondeado": porcentaje_redondeado,
                "diferencia_puntos_porcentuales": porcentaje_redondeado - porcentaje_publicado,
                "cumple_redondeo_una_decimal": bool(
                    np.isclose(porcentaje_redondeado, porcentaje_publicado, atol=1e-12, rtol=0)
                ),
            }
        )
    resultado = pd.DataFrame(filas)
    if len(resultado) != 13 or not resultado["cumple_redondeo_una_decimal"].all():
        raise ValueError("No se reprodujeron los trece porcentajes publicados desde Dryad.")
    return resultado


def reproducir_porcentajes_sitios() -> pd.DataFrame:
    """Reproduce los trece porcentajes disponibles en el CSV público de Dryad."""

    from .datos import leer_fuente_dryad, leer_sitios_referencia

    return _reproducir_desde_marcos(leer_fuente_dryad(), leer_sitios_referencia())
