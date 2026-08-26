import hashlib
from pathlib import Path
import shutil
import zipfile

import numpy as np
import pandas as pd

from saldo_forestal.datos import directorio_datos
from saldo_forestal.pipeline import ejecutar_pipeline


def test_pipeline_completo_en_directorio_limpio(tmp_path: Path):
    resultado = ejecutar_pipeline(repo_dir=tmp_path, data_dir=directorio_datos())
    assert len(resultado["resultados_poorter_municipales"]) == 172
    assert resultado["controles_calidad"]["estado"].eq("Cumple").all()
    zip_ruta = resultado["zip"]
    assert zip_ruta.exists()
    with zipfile.ZipFile(zip_ruta) as zf:
        nombres = zf.namelist()
        manifiesto = pd.read_csv(zf.open("outputs/downloads/manifiesto_resultados.csv"))
        assert set(manifiesto["ruta"]) == set(nombres) - {
            "outputs/downloads/manifiesto_resultados.csv"
        }
        for fila in manifiesto.itertuples(index=False):
            contenido = zf.read(fila.ruta)
            assert len(contenido) == fila.bytes
            assert hashlib.sha256(contenido).hexdigest() == fila.sha256
    assert "outputs/tables/resultados_forestales_nacionales.csv" in nombres
    assert "outputs/tables/transiciones_clasificacion_ponderada.csv" in nombres
    assert "outputs/tables/municipios_cambio_clasificacion_ponderada.csv" in nombres
    assert "outputs/downloads/COMO_CITAR.txt" in nombres
    assert "outputs/downloads/manifiesto_resultados.csv" in nombres


def test_transiciones_de_clasificacion_poorter(tmp_path: Path):
    resultado = ejecutar_pipeline(repo_dir=tmp_path, data_dir=directorio_datos())
    transiciones = resultado["transiciones_clasificacion_poorter"]
    conteos = {
        (fila.clasificacion_institucional, fila.clasificacion_ponderada): fila.municipios
        for fila in transiciones.itertuples(index=False)
    }
    assert conteos[("Ganancia", "Ganancia")] == 42
    assert conteos[("Ganancia", "Indeterminado")] == 9
    assert conteos[("Ganancia", "Pérdida")] == 15
    assert conteos[("Equilibrio", "Indeterminado")] == 2
    assert conteos[("Pérdida", "Pérdida")] == 104
    assert len(resultado["municipios_cambio_clasificacion_poorter"]) == 26


def test_pipeline_lee_parametros_monetarios_del_csv(tmp_path: Path):
    datos_alternativos = tmp_path / "insumos"
    shutil.copytree(directorio_datos(), datos_alternativos)
    ruta_parametros = datos_alternativos / "parametros_valoracion.csv"
    parametros = pd.read_csv(ruta_parametros)
    mascara_factor = parametros["parametro"].eq("factor_homologacion")
    mascara_homologado = parametros["parametro"].eq("valor_unitario_homologado")
    parametros.loc[mascara_factor, "valor"] *= 2
    unitario = parametros.loc[parametros["parametro"].eq("valor_unitario"), "valor"].iloc[0]
    factor = parametros.loc[mascara_factor, "valor"].iloc[0]
    parametros.loc[mascara_homologado, "valor"] = unitario * factor
    parametros.to_csv(ruta_parametros, index=False)

    resultado = ejecutar_pipeline(repo_dir=tmp_path / "salida", data_dir=datos_alternativos)
    neta = resultado["valoracion_reglas_nacional"].loc[
        lambda d: d["regla"].eq("Pérdida neta institucional")
    ].iloc[0]
    assert np.isclose(neta["flujo_anual_inferior_gtq"] / 1e6, 2 * 395.345451, atol=1e-6)
