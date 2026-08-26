"""Controles editoriales y estructurales del cuaderno público.

Estas pruebas operan sobre el cuaderno ejecutado cuando la variable
``CUADERNO_EJECUTADO`` está definida (como sucede en CI). En una ejecución
local revisan el único cuaderno situado directamente en ``notebooks/``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

import nbformat
import pytest


REPO = Path(__file__).resolve().parents[1]
DIRECTORIO_CUADERNOS = REPO / "notebooks"


def _cuadernos_activos() -> list[Path]:
    return sorted(DIRECTORIO_CUADERNOS.glob("*.ipynb"))


def _ruta_sometida_a_prueba() -> Path:
    configurada = os.environ.get("CUADERNO_EJECUTADO")
    if configurada:
        ruta = Path(configurada)
        if not ruta.is_absolute():
            ruta = REPO / ruta
        return ruta

    activos = _cuadernos_activos()
    assert len(activos) == 1, (
        "La publicación debe tener exactamente un cuaderno activo en notebooks/; "
        f"se encontraron {len(activos)}."
    )
    return activos[0]


@pytest.fixture(scope="module")
def cuaderno():
    ruta = _ruta_sometida_a_prueba()
    assert ruta.is_file(), f"No existe el cuaderno que debe validarse: {ruta}"
    return nbformat.read(ruta, as_version=4)


def _texto_salida(salida: Any) -> str:
    """Convierte una salida Jupyter en texto inspeccionable sin perder metadatos."""

    if salida.output_type == "stream":
        return str(salida.get("text", ""))
    if salida.output_type == "error":
        return "\n".join(
            [
                str(salida.get("ename", "")),
                str(salida.get("evalue", "")),
                *map(str, salida.get("traceback", [])),
            ]
        )
    if salida.output_type in {"display_data", "execute_result"}:
        return json.dumps(
            salida.get("data", {}), ensure_ascii=False, sort_keys=True, default=str
        )
    return json.dumps(salida, ensure_ascii=False, sort_keys=True, default=str)


def _texto_publico(cuaderno) -> str:
    partes: list[str] = []
    for celda in cuaderno.cells:
        if celda.cell_type == "markdown":
            partes.append(celda.source)
        if celda.cell_type == "code":
            partes.extend(_texto_salida(salida) for salida in celda.get("outputs", []))
    return "\n".join(partes)


def _html_salida(salida: Any) -> str:
    html = salida.get("data", {}).get("text/html", "")
    return "".join(html) if isinstance(html, list) else str(html)


def _datos_plotly(salida: Any) -> list[dict[str, Any]]:
    html = _html_salida(salida)
    inicio = html.find("Plotly.newPlot(")
    assert inicio >= 0, "La salida no contiene un lienzo Plotly inspeccionable."
    fragmento = html[inicio:]
    llamada = re.search(r'Plotly\.newPlot\(\s*"[^"]+"\s*,\s*', fragmento)
    assert llamada is not None
    datos, _ = json.JSONDecoder().raw_decode(fragmento[llamada.end():])
    return datos


def _layout_plotly(salida: Any) -> dict[str, Any]:
    html = _html_salida(salida)
    inicio = html.find("Plotly.newPlot(")
    assert inicio >= 0, "La salida no contiene un lienzo Plotly inspeccionable."
    fragmento = html[inicio:]
    llamada = re.search(r'Plotly\.newPlot\(\s*"[^"]+"\s*,\s*', fragmento)
    assert llamada is not None
    _, fin_datos = json.JSONDecoder().raw_decode(fragmento[llamada.end():])
    resto = fragmento[llamada.end() + fin_datos:].lstrip()
    assert resto.startswith(",")
    layout, _ = json.JSONDecoder().raw_decode(resto[1:].lstrip())
    return layout


def _resultado_numerado(cuaderno, rotulo: str):
    for celda in _celdas_resultado(cuaderno):
        plano = celda.outputs[0].get("data", {}).get("text/plain", "")
        plano = "".join(plano) if isinstance(plano, list) else str(plano)
        if plano.startswith(rotulo):
            return celda.outputs[0]
    raise AssertionError(f"No se encontró {rotulo}.")


def _celdas_resultado(cuaderno):
    return [
        celda
        for celda in cuaderno.cells
        if celda.cell_type == "code" and "result" in celda.metadata.get("tags", [])
    ]


def test_hay_un_unico_cuaderno_publico_activo():
    activos = _cuadernos_activos()
    assert len(activos) == 1, (
        "Debe existir exactamente un .ipynb publicable directamente en notebooks/."
    )


def test_metadatos_basicos_del_cuaderno(cuaderno):
    assert cuaderno.nbformat == 4
    assert cuaderno.metadata.get("kernelspec", {}).get("name") == "python3"
    assert _celdas_resultado(cuaderno), "No se encontraron celdas etiquetadas como result."


def test_todo_el_codigo_esta_oculto(cuaderno):
    visibles: list[int] = []
    for indice, celda in enumerate(cuaderno.cells, start=1):
        if celda.cell_type != "code":
            continue
        etiquetas = set(celda.metadata.get("tags", []))
        oculto_jupyter = celda.metadata.get("jupyter", {}).get("source_hidden") is True
        if (
            "hide-input" not in etiquetas
            or "remove_input" not in etiquetas
            or not oculto_jupyter
        ):
            visibles.append(indice)

    assert not visibles, (
        "Todas las celdas de código deben incluir hide-input, remove_input y "
        f"jupyter.source_hidden=true. Celdas pendientes: {visibles}"
    )


def test_no_hay_rotulos_de_preparacion_en_las_celdas(cuaderno):
    rotulos_invalidos: list[tuple[int, str]] = []
    for indice, celda in enumerate(cuaderno.cells, start=1):
        if celda.cell_type != "code":
            continue
        primera = celda.source.splitlines()[0] if celda.source.splitlines() else ""
        if primera != '#@title { display-mode: "form" }':
            rotulos_invalidos.append((indice, primera))

    assert not rotulos_invalidos, (
        "El rótulo Colab debe quedar vacío; los títulos pertenecen a las salidas: "
        f"{rotulos_invalidos}"
    )


def test_despues_de_configurar_cada_codigo_produce_una_salida(cuaderno):
    codigos = [celda for celda in cuaderno.cells if celda.cell_type == "code"]
    assert len(codigos[0].get("outputs", [])) == 0, "La configuración no debe producir salida."
    incompletas = [
        indice
        for indice, celda in enumerate(codigos[1:], start=2)
        if len(celda.get("outputs", [])) != 1
    ]
    assert not incompletas, (
        "Después de la configuración, cálculo y presentación deben compartir una sola celda: "
        f"{incompletas}"
    )


def test_una_salida_semantica_por_celda(cuaderno):
    demasiadas: list[tuple[int, int]] = []
    resultados_incompletos: list[tuple[int, int]] = []

    for indice, celda in enumerate(cuaderno.cells, start=1):
        if celda.cell_type != "code":
            continue
        cantidad = len(celda.get("outputs", []))
        if cantidad > 1:
            demasiadas.append((indice, cantidad))
        if "result" in celda.metadata.get("tags", []) and cantidad != 1:
            resultados_incompletos.append((indice, cantidad))

    assert not demasiadas, f"Hay celdas con más de una salida: {demasiadas}"
    assert not resultados_incompletos, (
        "Cada celda etiquetada result debe producir exactamente una salida: "
        f"{resultados_incompletos}"
    )


def test_el_cuaderno_ejecuta_sin_errores(cuaderno):
    errores: list[tuple[int, str]] = []
    for indice, celda in enumerate(cuaderno.cells, start=1):
        if celda.cell_type != "code":
            continue
        for salida in celda.get("outputs", []):
            if salida.output_type == "error":
                errores.append((indice, _texto_salida(salida)))

    assert not errores, f"El cuaderno contiene salidas de error: {errores}"


@pytest.mark.parametrize(
    ("patron", "explicacion"),
    [
        (r"\bFER[\s\-‑–—_]*20\b", "FER-20"),
        (r"\bcr[eé]dit(?:o|os|a|as)\b", "crédito/créditos"),
        (r"\bthetas?\s+de\s+Poorter\b", "thetas de Poorter"),
        (r"θ\s+de\s+Poorter\b", "θ de Poorter"),
        (r"\bcanast(?:a|as)\b", "canasta/canastas"),
        (
            r"\b(?:escenario|intervalo|m[eé]todo|aplicaci[oó]n)\s+(?:de\s+)?Poorter\b",
            "Poorter como nombre de escenario, intervalo, método o aplicación",
        ),
        (r"\bcr[ií]tica(?:s|mente)?\b", "crítica"),
        (r"per[ií]odo\s+cartogr[aá]fico", "período cartográfico"),
        (r"Perfil\s+Ambiental", "Perfil Ambiental"),
        (r"Manuscrito\s+en\s+preparaci[oó]n", "manuscrito en preparación"),
        (r"comparaci[oó]n\s+de\s+reglas", "comparación de reglas"),
    ],
)
def test_terminos_descartados_no_aparecen_en_el_texto_publico(
    cuaderno, patron: str, explicacion: str
):
    coincidencia = re.search(patron, _texto_publico(cuaderno), flags=re.IGNORECASE)
    assert coincidencia is None, f"Aparece el término descartado {explicacion!r}."


def test_resultados_numerados_con_nota_y_fuente(cuaderno):
    titulo = re.compile(
        r"(Tabla|Figura|Recuadro)\s+(\d+)\b(?:\s*[.:])?", re.IGNORECASE
    )
    secuencias: dict[str, list[int]] = {}
    faltantes: list[str] = []

    for posicion, celda in enumerate(cuaderno.cells):
        if celda.cell_type != "code" or "result" not in celda.metadata.get("tags", []):
            continue
        if len(celda.get("outputs", [])) != 1:
            faltantes.append(f"celda {posicion + 1}: no hay una única salida")
            continue
        texto = re.sub(
            r"\\u([0-9a-fA-F]{4})",
            lambda coincidencia: chr(int(coincidencia.group(1), 16)),
            _html_salida(celda.outputs[0]),
        )
        encontrados = {
            (tipo.casefold().capitalize(), int(numero))
            for tipo, numero in titulo.findall(texto)
        }
        if len(encontrados) != 1:
            faltantes.append(
                f"celda {posicion + 1}: se esperaba un único título numerado y hubo "
                f"{sorted(encontrados)}"
            )
            continue

        tipo, numero = encontrados.pop()
        secuencias.setdefault(tipo, []).append(numero)
        resultado_id = f"{tipo} {numero}"
        if celda.metadata.get("result_id") != resultado_id:
            faltantes.append(f"{resultado_id}: el resultado no conserva su identificador")
        if posicion + 1 >= len(cuaderno.cells):
            faltantes.append(f"{resultado_id}: falta comentario Markdown")
            continue
        comentario = cuaderno.cells[posicion + 1]
        if comentario.cell_type != "markdown" or "result-commentary" not in comentario.metadata.get("tags", []):
            faltantes.append(f"{resultado_id}: la celda siguiente no es el comentario académico")
            continue
        if comentario.metadata.get("result_id") != resultado_id:
            faltantes.append(f"{resultado_id}: el comentario no comparte el identificador")
        if not comentario.source.startswith("*Nota.* "):
            faltantes.append(f"{resultado_id}: falta Nota en Markdown")
        if "\n\n*Fuente.* " not in comentario.source:
            faltantes.append(f"{resultado_id}: falta Fuente en Markdown")
        if len([p for p in comentario.source.split("\n\n") if p.strip()]) < 3:
            faltantes.append(f"{resultado_id}: falta interpretación posterior")
        if re.search(r"Osorio\s*\(2026\)|Cita\s+sugerida", comentario.source, re.IGNORECASE):
            faltantes.append(f"{resultado_id}: contiene una autocita o una cita sugerida")
        if re.search(r"Nota\s*\.|Fuente\s*\.", texto, flags=re.IGNORECASE):
            faltantes.append(f"{resultado_id}: nota o fuente siguen dentro del lienzo")

    assert not faltantes, "\n".join(faltantes)

    for tipo, numeros in secuencias.items():
        esperada = list(range(1, len(numeros) + 1))
        assert numeros == esperada, (
            f"La numeración de {tipo.lower()} debe ser consecutiva, sin duplicados: "
            f"observada={numeros}, esperada={esperada}."
        )


def test_no_hay_doi_de_publicacion_ficticio(cuaderno):
    texto = _texto_publico(cuaderno)
    patrones_ficticios = [
        r"10\.5281/zenodo\.(?:0+|x+|pendiente)",
        r"10\.\d{4,9}/(?:x+|pendiente|tbd)\b",
        r"\bDOI\s*:\s*(?:pendiente|tbd|por asignar)\b",
    ]
    encontrados = [
        patron
        for patron in patrones_ficticios
        if re.search(patron, texto, flags=re.IGNORECASE)
    ]
    assert not encontrados, "No se debe publicar un DOI provisional o inventado."


def test_titulo_canonico_y_seccion_final_como_citar(cuaderno):
    titulo = "Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala"
    assert cuaderno.metadata.get("title") == titulo
    markdown = [celda.source for celda in cuaderno.cells if celda.cell_type == "markdown"]
    assert markdown[0].startswith(f"# {titulo}")
    assert markdown[-1].startswith("## Cómo citar")
    assert "Osorio, J. A. (2026)" in markdown[-1]


def test_comparacion_ponderada_y_trayectorias_distinguibles(cuaderno):
    fuentes_codigo = "\n".join(
        celda.source for celda in cuaderno.cells if celda.cell_type == "code"
    )
    assert "Dispersión municipal antes y después de aplicar la ponderación" in fuentes_codigo
    assert "Transición de clasificaciones municipales" in fuentes_codigo
    for patron in ('"solid"', '"dash"', '"dot"', '"circle"', '"diamond"', '"square"'):
        assert patron in fuentes_codigo, f"Falta codificación redundante {patron}."


def test_figura_historica_conecta_los_puntos(cuaderno):
    salida = _resultado_numerado(cuaderno, "Figura 1.")
    trazas = _datos_plotly(salida)
    assert trazas
    assert all("lines" in traza.get("mode", "") for traza in trazas)


@pytest.mark.parametrize("rotulo", ["Figura 6.", "Figura 13.", "Figura 14."])
def test_facetas_separan_leyenda_titulos_y_comentario(cuaderno, rotulo):
    salida = _resultado_numerado(cuaderno, rotulo)
    layout = _layout_plotly(salida)
    assert layout.get("legend", {}).get("y", 0) > 1.08
    titulos_y = [
        layout.get(clave, {}).get("title", {}).get("text")
        for clave in ("yaxis", "yaxis2", "yaxis3")
        if clave in layout
    ]
    assert sum(bool(titulo) for titulo in titulos_y) == 1
    pies_en_lienzo = [
        anotacion
        for anotacion in layout.get("annotations", [])
        if re.search(r"Nota\s*\.|Fuente\s*\.", anotacion.get("text", ""), re.IGNORECASE)
    ]
    assert not pies_en_lienzo
    assert 0.90 <= layout.get("title", {}).get("y", 0) <= 0.97
    assert layout.get("margin", {}).get("t", 0) >= 110


def test_tablas_compactas_y_descargas_atribuidas(cuaderno):
    excesos: list[tuple[str, int]] = []
    for celda in _celdas_resultado(cuaderno):
        salida = celda.outputs[0]
        plano = salida.get("data", {}).get("text/plain", "")
        plano = "".join(plano) if isinstance(plano, list) else str(plano)
        if not plano.startswith(("Tabla ", "Recuadro ")):
            continue
        html = _html_salida(salida)
        columnas = len(re.findall(r"<th>", html))
        if columnas > 5:
            excesos.append((plano, columnas))
        assert "class='sf-tabla'" in html
        assert "Plotly.newPlot(" not in html
        assert "Descargar CSV completo" in html
        assert "Descargar cita" not in html
        assert "max-width:" in html

    assert not excesos, f"Las tablas visibles no deben exceder cinco columnas: {excesos}"
    assert "osorio_2026_" in _texto_publico(cuaderno)


def test_nota_metodologica_incluye_formulas_clave_y_figura_de_manglar(cuaderno):
    markdown = "\n".join(
        celda.source for celda in cuaderno.cells if celda.cell_type == "markdown"
    )
    for expresion in (
        r"N_i=B_i-R_i",
        r"H_i^{\mathrm{inf}}",
        r"VP_i=F_i",
        r"\underline{\omega}_M",
        r"\underline H_{i,M}",
    ):
        assert expresion in markdown

    salida = _resultado_numerado(cuaderno, "Figura 15.")
    trazas = _datos_plotly(salida)
    assert len(trazas) == 3
    assert all(traza.get("type") == "bar" for traza in trazas)
    assert {traza.get("name") for traza in trazas} == {
        "Aumento conjunto", "Disminución conjunta", "Mixta"
    }


def test_sin_lenguaje_de_version_provisional(cuaderno):
    texto = _texto_publico(cuaderno)
    assert "0.1.0" not in texto
    assert re.search(r"versión\s+de\s+trabajo", texto, flags=re.IGNORECASE) is None
