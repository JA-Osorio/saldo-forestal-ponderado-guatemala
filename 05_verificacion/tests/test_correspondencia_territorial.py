"""Diez controles agrupados de reconstrucción y trazabilidad territorial."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import tomllib

import numpy as np
import pandas as pd

import saldo_forestal
from saldo_forestal.indicadores import agregar_recuperacion
from saldo_forestal.reproduccion import ejecutar_reproduccion


CONTEOS_REGIONALES = {
    "REG-PET-N": 9,
    "REG-PET-FTN": 32,
    "REG-TB-HUM": 62,
    "REG-ORI-EST": 35,
    "REG-SEC-MOT": 34,
}

INTERVALOS_ESPERADOS = {
    "REG-PET-N": (0.664, 0.6655, 0.667),
    "REG-PET-FTN": (0.594, 0.594, 0.594),
    "REG-TB-HUM": (0.593, 0.6795, 0.766),
    "REG-ORI-EST": (0.336, 0.5925, 0.849),
    "REG-SEC-MOT": (0.25, 0.45, 0.65),
}


def _codigo_canonico(valor: object) -> str:
    return f"{int(valor):04d}"


def _expandir_codigos(especificaciones: list[str]) -> set[str]:
    codigos: set[str] = set()
    for especificacion in especificaciones:
        if "-" not in especificacion:
            nuevos = {_codigo_canonico(especificacion)}
        else:
            inicio, fin = map(int, especificacion.split("-", 1))
            assert fin >= inicio, f"Rango invertido: {especificacion}"
            nuevos = {_codigo_canonico(valor) for valor in range(inicio, fin + 1)}
        assert codigos.isdisjoint(nuevos), f"Código repetido en {especificacion}"
        codigos.update(nuevos)
    return codigos


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _huellas_productos(raiz: Path) -> dict[str, str]:
    archivos: list[Path] = []
    for directorio in (
        "00_trazabilidad_fuentes",
        "02_resultados_y_diccionario",
        "05_verificacion",
        "build",
    ):
        base = raiz / directorio
        if base.exists():
            archivos.extend(
                ruta
                for ruta in base.rglob("*")
                if ruta.is_file() and "cuadernos" not in ruta.parts
            )
    return {
        ruta.relative_to(raiz).as_posix(): _sha256(ruta)
        for ruta in sorted(archivos)
    }


def test_01_listas_explicitas_validas_y_disjuntas(repo_dir, base):
    configuracion = json.loads(
        (
            repo_dir
            / "01_metodologia"
            / "reglas_correspondencia_territorial_experta_codificada.json"
        ).read_text(encoding="utf-8")
    )
    regiones = configuracion["regiones"]
    assert len(regiones) == 5

    conjuntos: dict[str, set[str]] = {}
    for region in regiones:
        region_id = region["region_id"]
        assert region["proporcion_region_id"] == region_id
        assert "canasta_id" not in region
        conjuntos[region_id] = _expandir_codigos(region["codigos"])

    assert set(conjuntos) == set(CONTEOS_REGIONALES)
    assert {clave: len(valor) for clave, valor in conjuntos.items()} == CONTEOS_REGIONALES
    items = list(conjuntos.items())
    for indice, (region_id, codigos) in enumerate(items):
        for otra_region, otros in items[indice + 1 :]:
            assert codigos.isdisjoint(otros), f"{region_id} se superpone con {otra_region}"

    universo = {
        _codigo_canonico(codigo)
        for codigo in base.loc[base["codigo"].notna(), "codigo"]
    }
    union = set().union(*conjuntos.values())
    assert len(union) == 172
    assert union <= universo


def test_02_particion_172_168_2_y_conteos_regionales(correspondencia):
    es_municipio = correspondencia["codigo"].notna()
    esta_incluido = correspondencia["proporcion_region_id"].notna()
    assert len(correspondencia) == 342
    assert int((es_municipio & esta_incluido).sum()) == 172
    assert int((es_municipio & ~esta_incluido).sum()) == 168
    assert int((~es_municipio).sum()) == 2
    assert (
        correspondencia.loc[esta_incluido, "proporcion_region_id"]
        .value_counts()
        .to_dict()
        == CONTEOS_REGIONALES
    )


def test_03_esquema_y_completitud_de_las_tres_bitacoras(
    correspondencia,
    ejecucion_limpia,
):
    municipal_requeridas = {
        "cod_dep", "depto", "codigo", "codigo_canonico", "municipio",
        "region_id", "region_nombre", "estado_dominio", "proporcion_region_id",
        "regla_id", "tipo_decision", "criterio_operativo",
        "decision_manual_codificada", "origen_decision", "estado_evidencia",
        "revision_ecologica", "fuente_universo", "fuente_intervalo",
        "version_metodo",
    }
    assert municipal_requeridas <= set(correspondencia.columns)
    assert correspondencia[
        [
            "regla_id", "tipo_decision", "criterio_operativo", "origen_decision",
            "estado_evidencia", "revision_ecologica", "fuente_universo",
            "version_metodo",
        ]
    ].notna().all().all()

    resultado = ejecucion_limpia["resultado"]
    region_sitio = resultado["trazabilidad_region_sitio"]
    reproduccion = resultado["reproduccion_por_sitio"]
    assert {
        "proporcion_region_id", "region_nombre", "site_id", "site_name", "country",
        "relative_recovery_pct_20y", "uso_sitio", "regla_intervalo", "redondeo",
        "source_locator", "version_metodo",
    } <= set(region_sitio.columns)
    assert {
        "site_id", "site_name", "agb20_reproducida_mg_ha",
        "agb_bosque_maduro_mediana_mg_ha", "porcentaje_publicado",
        "porcentaje_reproducido", "porcentaje_reproducido_redondeado",
        "diferencia_puntos_porcentuales", "cumple_redondeo_una_decimal",
    } <= set(reproduccion.columns)
    assert region_sitio[["proporcion_region_id", "site_id", "uso_sitio"]].notna().all().all()
    assert reproduccion[["site_id", "site_name"]].notna().all().all()


def test_04_fuentes_enlazadas_y_localizables(repo_dir, correspondencia, ejecucion_limpia):
    fuentes = pd.read_csv(
        repo_dir
        / "00_trazabilidad_fuentes"
        / "registro_fuentes_saldo_forestal_guatemala.csv"
    )
    assert {
        "INAB_DINAMICA_2016_2020", "POORTER_ET_AL_2016", "POORTER_DRYAD_2017",
    } <= set(fuentes["fuente_id"])
    dryad = fuentes.set_index("fuente_id").loc["POORTER_DRYAD_2017"]
    assert dryad["doi"] == "10.5061/dryad.82vr4"
    assert str(dryad["url"]).startswith("https://doi.org/")

    incluidos = correspondencia["proporcion_region_id"].notna()
    assert correspondencia["fuente_universo"].notna().all()
    assert correspondencia.loc[incluidos, "fuente_intervalo"].notna().all()
    ids_fuentes = set(fuentes["fuente_id"])
    assert set(correspondencia["fuente_universo"]) <= ids_fuentes
    assert set(correspondencia.loc[incluidos, "fuente_intervalo"]) <= ids_fuentes

    region_sitio = ejecucion_limpia["resultado"]["trazabilidad_region_sitio"]
    assert region_sitio["source_locator"].notna().all()
    assert (
        repo_dir
        / "00_trazabilidad_fuentes"
        / "fuentes_originales"
        / "base_biomasa_bosques_secundarios_neotropicales_dryad.csv"
    ).is_file()


def test_05_cinco_intervalos_reconstruidos_exactamente(catalogo):
    observado = catalogo.set_index("proporcion_region_id")
    assert set(observado.index) == set(INTERVALOS_ESPERADOS)
    for region_id, esperado in INTERVALOS_ESPERADOS.items():
        fila = observado.loc[region_id]
        np.testing.assert_allclose(
            [fila["rho20_min"], fila["rho20_central"], fila["rho20_max"]],
            esperado,
            atol=1e-12,
            rtol=0,
        )
    assert observado.loc["REG-SEC-MOT", "rho20_min"] == 0.25
    assert observado.loc["REG-SEC-MOT", "rho20_max"] == 0.65


def test_06_dryad_13_reproducidos_4_contextuales_y_1_tabla_ampliada(
    reproduccion_sitios,
    ejecucion_limpia,
):
    assert len(reproduccion_sitios) == 13
    assert reproduccion_sitios["site_id"].is_unique
    assert reproduccion_sitios["cumple_redondeo_una_decimal"].all()
    np.testing.assert_allclose(
        reproduccion_sitios["porcentaje_reproducido_redondeado"],
        reproduccion_sitios["porcentaje_publicado"],
        atol=1e-12,
        rtol=0,
    )

    relaciones = ejecucion_limpia["resultado"]["trazabilidad_region_sitio"]
    contextuales = relaciones.loc[
        relaciones["uso_sitio"].eq("contextual_sin_porcentaje"), "site_id"
    ]
    assert contextuales.nunique() == 4
    numericos = relaciones.loc[
        relaciones["relative_recovery_pct_20y"].notna(), ["site_id", "site_name"]
    ].drop_duplicates()
    no_reproducidos = numericos.loc[
        ~numericos["site_id"].isin(reproduccion_sitios["site_id"])
    ]
    assert no_reproducidos["site_name"].tolist() == ["Quintana Roo"]


def test_07_identidades_fila_a_fila_de_los_172_resultados(
    resultados_recuperacion,
):
    assert len(resultados_recuperacion) == 172
    assert resultados_recuperacion["codigo"].is_unique
    perdida = resultados_recuperacion["perdida_bruta_ha"]
    recuperacion = resultados_recuperacion["recuperacion_bruta_ha"]
    np.testing.assert_allclose(
        resultados_recuperacion["perdida_neta_ha"],
        perdida - recuperacion,
        atol=1e-8,
        rtol=0,
    )
    np.testing.assert_allclose(
        resultados_recuperacion["saldo_ponderado_inferior_ha"],
        perdida - resultados_recuperacion["rho20_max"] * recuperacion,
        atol=1e-8,
        rtol=0,
    )
    np.testing.assert_allclose(
        resultados_recuperacion["saldo_ponderado_superior_ha"],
        perdida - resultados_recuperacion["rho20_min"] * recuperacion,
        atol=1e-8,
        rtol=0,
    )


def test_08_agregados_reconcilian_con_los_resultados_municipales(
    resultados_recuperacion,
):
    columnas = [
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "saldo_ponderado_inferior_ha",
        "saldo_ponderado_superior_ha",
    ]
    nacional = agregar_recuperacion(resultados_recuperacion).iloc[0]
    regional = agregar_recuperacion(
        resultados_recuperacion,
        ["proporcion_region_id", "region_nombre"],
    )
    departamental = agregar_recuperacion(
        resultados_recuperacion,
        ["cod_dep", "depto"],
    )
    assert regional["municipios"].sum() == 172
    assert departamental["municipios"].sum() == 172
    for columna in columnas:
        assert math.isclose(
            nacional[columna],
            resultados_recuperacion[columna].sum(),
            abs_tol=1e-8,
            rel_tol=0,
        )
        assert math.isclose(
            regional[columna].sum(),
            resultados_recuperacion[columna].sum(),
            abs_tol=1e-8,
            rel_tol=0,
        )
        assert math.isclose(
            departamental[columna].sum(),
            resultados_recuperacion[columna].sum(),
            abs_tol=1e-8,
            rel_tol=0,
        )


def test_09_ejecucion_completa_sin_resultados_finales_congelados(ejecucion_limpia):
    raiz = ejecucion_limpia["raiz"]
    resultado = ejecucion_limpia["resultado"]
    assert len(resultado["resultados_recuperacion_municipios"]) == 172
    assert resultado["controles_calidad"]["estado"].eq("Cumple").all()
    assert (
        raiz
        / "00_trazabilidad_fuentes"
        / "trazabilidad_municipio_region_guatemala_2016_2020.csv"
    ).is_file()
    assert (
        raiz
        / "02_resultados_y_diccionario"
        / "resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv"
    ).is_file()
    assert (
        raiz
        / "05_verificacion"
        / "reproduccion_por_sitio_recuperacion_biomasa_20_anios.csv"
    ).is_file()


def test_10_determinismo_version_unica_y_nombres_publicos_normalizados(
    repo_dir,
    ejecucion_limpia,
    tmp_path,
    preparar_repo_limpio,
):
    segunda_raiz = preparar_repo_limpio(tmp_path / "segunda_ejecucion")
    segunda = ejecutar_reproduccion(
        repo_dir=segunda_raiz,
        data_dir=segunda_raiz / "00_trazabilidad_fuentes",
    )
    assert _huellas_productos(ejecucion_limpia["raiz"]) == _huellas_productos(
        segunda_raiz
    )

    configuracion = tomllib.loads((repo_dir / "pyproject.toml").read_text(encoding="utf-8"))
    assert configuracion["project"]["version"] == "1.0.0"
    assert saldo_forestal.__version__ == "1.0.0"
    resultado_primero = ejecucion_limpia["resultado"]
    versiones = set(resultado_primero["trazabilidad_municipio_region"]["version_metodo"])
    versiones.update(resultado_primero["trazabilidad_region_sitio"]["version_metodo"])
    assert versiones == {"1.0.0"}
    metadatos = json.loads(
        (
            ejecucion_limpia["raiz"]
            / "05_verificacion"
            / "metadatos_ejecucion.json"
        ).read_text(encoding="utf-8")
    )
    assert metadatos["version"] == metadatos["version_metodo_correspondencia"] == "1.0.0"

    nombres_productos = set(resultado_primero) | set(segunda)
    rutas_publicas = {
        ruta.relative_to(ejecucion_limpia["raiz"]).as_posix()
        for directorio in (
            "00_trazabilidad_fuentes",
            "02_resultados_y_diccionario",
            "05_verificacion",
            "build",
        )
        for ruta in (ejecucion_limpia["raiz"] / directorio).glob("*")
        if ruta.is_file()
    }
    nombres_api = set(getattr(saldo_forestal, "__all__", ()))
    nombres = nombres_productos | rutas_publicas | nombres_api
    prohibido = re.compile(
        r"poorter|canast|(?:^|_)reglas(?:_|$)",
        flags=re.IGNORECASE,
    )
    encontrados = sorted(nombre for nombre in nombres if prohibido.search(nombre))
    assert not encontrados, f"Persisten nombres descartados: {encontrados}"
