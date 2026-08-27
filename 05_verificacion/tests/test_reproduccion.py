from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

from saldo_forestal.reproduccion import ejecutar_reproduccion


def test_reproduccion_completa_en_directorio_limpio(ejecucion_limpia):
    resultado = ejecucion_limpia["resultado"]
    assert len(resultado["resultados_recuperacion_municipios"]) == 172
    assert resultado["controles_calidad"]["estado"].eq("Cumple").all()
    zip_ruta = resultado["zip"]
    assert zip_ruta == (
        ejecucion_limpia["raiz"]
        / "build"
        / "resultados_saldo_forestal_guatemala.zip"
    )
    assert zip_ruta.exists()

    with zipfile.ZipFile(zip_ruta) as comprimido:
        nombres = comprimido.namelist()
        ruta_manifiesto = "05_verificacion/manifiesto_resultados.csv"
        manifiesto = pd.read_csv(comprimido.open(ruta_manifiesto))
        assert set(manifiesto["ruta"]) == set(nombres) - {ruta_manifiesto}
        for fila in manifiesto.itertuples(index=False):
            contenido = comprimido.read(fila.ruta)
            assert len(contenido) == fila.bytes
            assert hashlib.sha256(contenido).hexdigest() == fila.sha256

    assert (
        "02_resultados_y_diccionario/resultados_forestales_guatemala_2016_2020.csv"
        in nombres
    )
    assert (
        "02_resultados_y_diccionario/"
        "transiciones_clasificacion_ponderada_municipios_guatemala_2016_2020.csv"
        in nombres
    )
    assert (
        "02_resultados_y_diccionario/"
        "cambios_clasificacion_ponderada_municipios_guatemala_2016_2020.csv"
        in nombres
    )
    assert "como_citar.txt" in nombres

    ruta_metadatos = (
        ejecucion_limpia["raiz"] / "05_verificacion" / "metadatos_ejecucion.json"
    )
    metadatos = json.loads(ruta_metadatos.read_text(encoding="utf-8"))
    assert metadatos["unidades_base"] == 342
    assert metadatos["municipios"] == 340
    assert metadatos["municipios_con_proporcion"] == 172
    assert metadatos["municipios_excluidos"] == 168
    assert metadatos["unidades_lacustres"] == 2


def test_transiciones_de_clasificacion_recuperacion(ejecucion_limpia):
    resultado = ejecucion_limpia["resultado"]
    transiciones = resultado["transiciones_clasificacion_ponderada"]
    conteos = {
        (fila.clasificacion_institucional, fila.clasificacion_ponderada): fila.municipios
        for fila in transiciones.itertuples(index=False)
    }
    assert conteos[("Ganancia", "Ganancia")] == 42
    assert conteos[("Ganancia", "Indeterminado")] == 9
    assert conteos[("Ganancia", "Pérdida")] == 15
    assert conteos[("Equilibrio", "Indeterminado")] == 2
    assert conteos[("Pérdida", "Pérdida")] == 104
    assert len(resultado["municipios_cambio_clasificacion_ponderada"]) == 26


def test_reproduccion_lee_parametros_monetarios_del_csv(
    tmp_path: Path,
    preparar_repo_limpio,
):
    raiz = preparar_repo_limpio(tmp_path / "parametros_alternativos")
    ruta_parametros = (
        raiz
        / "01_metodologia"
        / "parametros"
        / "parametros_valoracion_servicios_ecosistemicos_guatemala_2019_2026.csv"
    )
    parametros = pd.read_csv(ruta_parametros)
    mascara_factor = parametros["parametro"].eq("factor_homologacion")
    mascara_homologado = parametros["parametro"].eq("valor_unitario_homologado")
    parametros.loc[mascara_factor, "valor"] *= 2
    unitario = parametros.loc[
        parametros["parametro"].eq("valor_unitario"), "valor"
    ].iloc[0]
    factor = parametros.loc[mascara_factor, "valor"].iloc[0]
    parametros.loc[mascara_homologado, "valor"] = unitario * factor
    parametros.to_csv(ruta_parametros, index=False)

    resultado = ejecutar_reproduccion(
        repo_dir=raiz,
        data_dir=raiz / "00_trazabilidad_fuentes",
    )
    neta = resultado["valoracion_resultados_forestales_nacionales"].loc[
        lambda datos: datos["regla"].eq("Pérdida neta institucional")
    ].iloc[0]
    assert np.isclose(
        neta["flujo_anual_inferior_gtq"] / 1e6,
        2 * 395.345451,
        atol=1e-6,
    )
