"""Construye el cuaderno público y reproducible del saldo forestal.

Después de la configuración, cada celda de código reúne cálculo y presentación
de un único resultado. Así se conserva la trazabilidad sin duplicar espacios de
código en Colab o Jupyter.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
import re
from textwrap import dedent

import nbformat as nbf


REPO = Path(__file__).resolve().parents[1]
DESTINO = REPO / "notebooks" / "saldo_forestal_ponderado_guatemala.ipynb"
DESTINO_ANTERIOR = REPO / "notebooks" / "saldo_forestal_ponderado_PAG2026.ipynb"


FUENTES_APARATO = {
    "FUENTE_INAB": "INAB y CONAP (2023) e INAB (2023b); cálculos del autor.",
    "FUENTE_POORTER": (
        "INAB y CONAP (2023), INAB (2023b) y Poorter et al. (2016, 2017); cálculos del autor."
    ),
    "FUENTE_VALORACION": (
        "Banco Mundial et al. (2021) y Banco de Guatemala (s. f.); cálculos del autor."
    ),
    "FUENTE_MANGLE": (
        "INAB (2023a), INAB et al. (2016), e INAB y CONAP (2023); "
        "cálculos del autor."
    ),
    "FUENTE_ESCENARIOS": (
        "INAB y CONAP (2023) e INAB (2023b); supuestos y cálculos del autor."
    ),
}


INTERPRETACIONES = {
    "Figura 1": (
        "La pérdida bruta anual aumenta entre el primer y el último intervalo disponible, "
        "mientras la pérdida neta disminuye. La divergencia muestra por qué ambos indicadores "
        "deben leerse juntos."
    ),
    "Tabla 1": (
        "La recuperación reportada equivale al 78.4 % de la pérdida bruta. En consecuencia, "
        "el resultado neto conserva 52,736 ha, o 21.6 % de la pérdida observada antes de la resta."
    ),
    "Figura 2": (
        "La recuperación reduce aritméticamente el resultado nacional de 244,395 a 52,736 ha. "
        "La magnitud de esa reducción no implica que la cobertura recuperada tenga la misma "
        "condición que la cobertura perdida."
    ),
    "Tabla 2": (
        "La composición del resultado nacional varía entre departamentos: un mismo saldo neto "
        "puede provenir de pérdidas y recuperaciones brutas de magnitudes muy distintas."
    ),
    "Figura 3": (
        "La agregación departamental oculta una geografía heterogénea: conviven departamentos "
        "con pérdida neta y otros con ganancia de cobertura durante 2016–2020."
    ),
    "Tabla 3": (
        "Los extremos municipales confirman que el resultado nacional no describe una tendencia "
        "uniforme. La tabla completa permite examinar los 340 municipios sin reducir el análisis "
        "a los casos más visibles."
    ),
    "Figura 4": (
        "La distancia respecto de la diagonal revela cuánto depende cada resultado municipal de "
        "la recuperación. Los municipios próximos a la diagonal son particularmente sensibles "
        "al ponderador aplicado."
    ),
    "Tabla 4": (
        "Las cinco regiones de referencia producen proporciones distintas de recuperación de biomasa a veinte "
        "años. Esa variación territorial se conserva en lugar de imponer un único valor a todos "
        "los municipios elegibles."
    ),
    "Figura 5": (
        "Los intervalos se superponen, pero no son idénticos. La amplitud mostrada se traslada al "
        "saldo ponderado y debe interpretarse como variación de las proporciones regionales, no como error muestral."
    ),
    "Tabla 5": (
        "Dentro de los 172 municipios elegibles, el saldo ponderado asciende a "
        "99,593–107,108 ha, frente a 35,857 ha bajo el cálculo neto reportado."
    ),
    "Tabla 6": (
        "El efecto de la ponderación difiere por departamento porque cambian tanto la recuperación "
        "observada como la proporción regional asignada a sus municipios elegibles."
    ),
    "Figura 6": (
        "Después de ponderar la recuperación, los puntos se desplazan hacia abajo respecto de la "
        "comparación original. El cambio permite verificar visualmente que el ajuste no es un "
        "multiplicador uniforme del resultado neto."
    ),
    "Figura 7": (
        "La ponderación eleva el saldo de pérdida en la mayor parte del dominio. Veintiséis "
        "municipios cambian de clasificación, incluidos quince que pasan de ganancia reportada a pérdida."
    ),
    "Figura 8": (
        "El 15.1 % de los municipios del dominio cambia de diagnóstico. La transición se concentra "
        "en resultados próximos a cero, donde la resta completa de la recuperación determina el signo."
    ),
    "Tabla 7": (
        "La matriz distingue permanencias y transiciones sin perder el denominador de cada grupo "
        "de origen. La mayoría conserva su clasificación, pero los cambios no son marginales."
    ),
    "Tabla 8": (
        "Los mayores cambios se concentran donde la recuperación reportada es alta. La tabla permite "
        "identificar los municipios que explican el cambio agregado y no solo su magnitud nacional."
    ),
    "Figura 9": (
        "Todos los departamentos del dominio se desplazan hacia un saldo de mayor pérdida al limitar "
        "la recuperación reconocida. La longitud de cada línea resume la magnitud territorial del ajuste."
    ),
    "Tabla 9": (
        "La completación conservadora sitúa el saldo nacional entre 116,473 y 123,988 ha: de 2.21 "
        "a 2.35 veces la pérdida neta reportada, sin extrapolar las proporciones fuera de su dominio de aplicación."
    ),
    "Figura 10": (
        "El saldo ponderado queda entre la pérdida bruta y la pérdida neta. La separación entre los "
        "tres resultados cuantifica cuánto cambia la lectura nacional según el reconocimiento otorgado "
        "a la recuperación."
    ),
    "Tabla 10": (
        "La valoración conserva el orden de los resultados físicos: la pérdida bruta produce el mayor "
        "monto, la pérdida neta el menor y el saldo ponderado un intervalo intermedio."
    ),
    "Figura 11": (
        "Como se aplica un valor unitario uniforme, las diferencias monetarias son proporcionales a "
        "las hectáreas anualizadas. La figura expresa órdenes de magnitud, no precios observados por municipio."
    ),
    "Tabla 11": (
        "Una tasa de descuento menor eleva el valor presente de todas las alternativas. La sensibilidad "
        "financiera modifica los montos, pero no revierte su orden relativo."
    ),
    "Figura 12": (
        "El intervalo ponderado permanece separado del resultado neto en las tres tasas. Por ello, la "
        "diferencia principal procede del tratamiento físico de la recuperación y no de una tasa particular."
    ),
    "Tabla 12": (
        "Los escenarios alteran por separado pérdida y recuperación. Esa simetría hace explícito qué "
        "supuesto impulsa cada trayectoria y evita presentar los resultados como pronósticos."
    ),
    "Figura 13": (
        "La contención proporcional desacelera la acumulación; la continuidad conserva el ritmo base "
        "y el deterioro acelerado amplía la brecha. En los tres casos el saldo ponderado permanece "
        "entre la pérdida bruta y la pérdida neta."
    ),
    "Figura 14": (
        "La incorporación sucesiva de cohortes hace crecer el valor presente acumulado. La distancia "
        "entre trayectorias combina los supuestos físicos con el mismo esquema de valoración."
    ),
    "Tabla 13": (
        "La tabla permite comparar, bajo supuestos comunes, el efecto conjunto del escenario físico "
        "y del resultado forestal utilizado como base de la valoración."
    ),
    "Tabla 14": (
        "Treinta de las 55 series muestran aumento conjunto de carbono y área basal; cuatro son mixtas. "
        "De esos conteos se deriva un ponderador estructural local de 0.545–0.618."
    ),
    "Figura 15": (
        "La Blanca y Retalhuleu reúnen 29 series, equivalentes al 52.7 % del total. Al sumar Sipacate "
        "y Pasaco, cuatro municipios concentran 43 de las 55 series, o 78.2 % de la evidencia clasificada."
    ),
    "Tabla 15": (
        "El saldo agregado aumenta de 5,039.6 ha bajo el cálculo neto a 8,075.3–8,653.6 ha con el "
        "ponderador estructural. La diferencia es de 3,035.7–3,614.0 ha, equivalente a un resultado "
        "60.2 %–71.7 % mayor que la pérdida neta."
    ),
    "Figura 16": (
        "El resultado neto clasifica seis municipios con pérdida y siete con ganancia. El ponderador "
        "local clasifica diez con pérdida y tres con ganancia; Tiquisate, Chiquimulilla, La Blanca y "
        "Pasaco cambian de signo."
    ),
    "Tabla 16": (
        "Los intervalos estructural y de recuperación ponderada se superponen en el agregado, pero responden a fundamentos "
        "distintos. En doce municipios conservan la misma clasificación; Pasaco es pérdida en la "
        "aplicación local e indeterminado con la proporción de recuperación a veinte años."
    ),
    "Recuadro 1": (
        "Las cifras muestran la escala económica del contexto ambiental y de desastres. Se mantienen "
        "fuera de la valoración forestal porque la información disponible no permite atribuirlas a la "
        "deforestación ni descartar doble conteo."
    ),
}


def _texto(contenido: str, *, etiquetas: tuple[str, ...] = ()):
    """Crea una celda Markdown con espacios normalizados."""

    return nbf.v4.new_markdown_cell(
        dedent(contenido).strip() + "\n",
        metadata={"tags": list(etiquetas)},
    )


def _codigo(
    contenido: str,
    *,
    titulo_colab: str | None = None,
    resultado: bool = False,
):
    """Crea una celda de código oculta en Jupyter y Colab."""

    etiquetas = ["hide-input", "remove_input"]
    if resultado:
        etiquetas.append("result")
    # El rótulo se deja deliberadamente vacío: el título editorial pertenece a
    # la tabla o figura, no a un segundo encabezado de código.
    fuente = "#@title { display-mode: \"form\" }\n" + dedent(contenido).strip() + "\n"
    return nbf.v4.new_code_cell(
        fuente,
        execution_count=None,
        outputs=[],
        metadata={
            "tags": etiquetas,
            "jupyter": {"source_hidden": True},
            "cellView": "form",
            "execution": {
                "iopub.status.busy": "show",
                "iopub.execute_input": "hide",
                "iopub.status.idle": "show",
            },
        },
    )


def _fusionar_calculo_y_resultado(celdas):
    """Fusiona cada par preparación/resultado en una sola celda ejecutable."""

    fusionadas = []
    indice = 0
    while indice < len(celdas):
        actual = celdas[indice]
        siguiente = celdas[indice + 1] if indice + 1 < len(celdas) else None
        actual_es_preparacion = (
            actual.cell_type == "code"
            and "result" not in actual.metadata.get("tags", [])
        )
        siguiente_es_resultado = (
            siguiente is not None
            and siguiente.cell_type == "code"
            and "result" in siguiente.metadata.get("tags", [])
        )
        if actual_es_preparacion and siguiente_es_resultado:
            fuentes = []
            for celda in (actual, siguiente):
                lineas = celda.source.splitlines()
                if lineas and lineas[0].startswith("#@title"):
                    lineas = lineas[1:]
                fuentes.append("\n".join(lineas).strip())
            siguiente.source = (
                "#@title { display-mode: \"form\" }\n"
                + "\n\n".join(fuentes)
                + "\n"
            )
            fusionadas.append(siguiente)
            indice += 2
            continue
        fusionadas.append(actual)
        indice += 1
    return fusionadas


def _fuente_publica(expresion: ast.expr) -> str:
    """Resuelve la fuente de una llamada sin autocitar el trabajo en construcción."""

    if isinstance(expresion, ast.Name):
        if expresion.id not in FUENTES_APARATO:
            raise KeyError(f"No hay fuente editorial para {expresion.id}.")
        return FUENTES_APARATO[expresion.id]
    fuente = ast.literal_eval(expresion)
    reemplazos = {
        "análisis reproducible de Osorio (2026)": "cálculos del autor",
        "cálculos de Osorio (2026)": "cálculos del autor",
        "compilación de Osorio (2026)": "cálculos del autor",
        "Supuestos y análisis reproducible de Osorio (2026)": "Supuestos y cálculos del autor",
    }
    for original, sustituto in reemplazos.items():
        fuente = fuente.replace(original, sustituto)
    return re.sub(r"^Fuente:\s*", "", fuente, flags=re.IGNORECASE)


def _extraer_aparato(celda) -> tuple[str, str, str]:
    """Extrae título, nota y fuente de la única presentación de una celda."""

    arbol = ast.parse(celda.source)
    llamadas = [
        nodo
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Call)
        and isinstance(nodo.func, ast.Name)
        and nodo.func.id in {"mostrar_figura", "mostrar_tabla"}
    ]
    if len(llamadas) != 1 or len(llamadas[0].args) < 4:
        raise ValueError("Cada resultado debe contener una sola llamada de presentación completa.")
    llamada = llamadas[0]
    titulo = ast.literal_eval(llamada.args[1])
    nota = ast.literal_eval(llamada.args[2])
    fuente = _fuente_publica(llamada.args[3])
    return titulo, nota, fuente


def _incorporar_comentarios(celdas):
    """Añade después de cada resultado su nota, fuente e interpretación en Markdown."""

    publicadas = []
    for celda in celdas:
        publicadas.append(celda)
        if celda.cell_type != "code" or "result" not in celda.metadata.get("tags", []):
            continue
        titulo, nota, fuente = _extraer_aparato(celda)
        coincidencia = re.match(r"(Figura|Tabla|Recuadro)\s+\d+", titulo)
        if coincidencia is None:
            raise ValueError(f"El resultado carece de rótulo numerado: {titulo}")
        resultado_id = coincidencia.group(0)
        if resultado_id not in INTERPRETACIONES:
            raise KeyError(f"Falta interpretación para {resultado_id}.")
        celda.metadata["result_id"] = resultado_id
        comentario = _texto(
            f"""
            *Nota.* {nota}

            *Fuente.* {fuente}

            {INTERPRETACIONES[resultado_id]}
            """,
            etiquetas=("result-commentary",),
        )
        comentario.metadata["result_id"] = resultado_id
        publicadas.append(comentario)
    return publicadas


def construir_cuaderno():
    """Devuelve el cuaderno completo como ``NotebookNode``."""

    celdas = [
        _texto(
            r"""
            # Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala

            *Resultados nacionales y municipales, 2016–2020*

            Juan Alejandro Osorio · IARNA, Universidad Rafael Landívar

            Este cuaderno examina qué cambia cuando la recuperación reportada deja de descontarse
            de inmediato y en proporción uno a uno de la pérdida bruta. El punto de partida es la
            información oficial de la dinámica de cobertura forestal 2016–2020 (INAB & CONAP, 2023).

            El recorrido reproduce primero el reporte institucional de pérdida bruta ($B$),
            recuperación bruta ($R$) y pérdida neta ($N=B-R$). Después introduce una
            *proporción de recuperación de biomasa a veinte años*, $\rho_{20}$, derivada de
            Poorter et al., y calcula el saldo forestal ponderado

            $$H_i(\rho)=B_i-\rho_iR_i.$$

            Los resultados son una aproximación cuantitativa bajo limitaciones explícitas de
            datos. No constituyen una cuenta SCAE-CE completa, una medición contemporánea de
            biomasa ni una equivalencia ecológica entre pérdida y recuperación.
            """,
            etiquetas=("remove-input",),
        ),
        _texto(
            """
            ## Cómo leer el cuaderno

            Salvo indicación expresa, las magnitudes corresponden al período de análisis
            2016–2020. Una cifra positiva representa pérdida y una negativa, ganancia de cobertura.
            El dominio de aplicación comprende 172 municipios; el total nacional se construye
            después mediante una completación conservadora.

            La aproximación de manglar es local y utiliza evidencia estructural de campo. No se
            suma a la recuperación ponderada. Los costos de desastres y degradación se mantienen
            como contexto no aditivo. El código puede desplegarse, aunque se oculta de inicio para
            privilegiar la lectura. Las fórmulas permiten seguir cada cálculo y, después de cada
            resultado, una celda Markdown reúne la nota, la fuente y su interpretación.
            """
        ),
        _codigo(
            r"""
            from pathlib import Path
            import subprocess
            import sys

            candidatos = [Path.cwd(), Path.cwd().parent, Path.cwd() / "saldo-forestal-ponderado-guatemala"]
            repo = next((p.resolve() for p in candidatos if (p / "src" / "saldo_forestal").is_dir()), None)
            if repo is None:
                destino_repo = Path.cwd() / "saldo-forestal-ponderado-guatemala"
                subprocess.run(
                    [
                        "git", "clone", "--depth", "1", "--branch", "v1.0.0",
                        "https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git",
                        str(destino_repo),
                    ],
                    check=True,
                )
                repo = destino_repo.resolve()
            sys.path.insert(0, str(repo / "src"))

            import numpy as np
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            from IPython.display import HTML, display

            from saldo_forestal.pipeline import ejecutar_pipeline
            from saldo_forestal.visualizacion import (
                config_plotly,
                estilo_plotly,
                mostrar_hallazgo,
                mostrar_tabla,
                mostrar_tarjetas,
                nombre_archivo,
                panel_descargas,
            )

            def mostrar_figura(fig, titulo, nota, fuente, *, alto=700):
                # Presenta una figura interactiva como una sola salida HTML.
                estilo_plotly(fig, titulo, nota, fuente, alto=alto)
                fragmento = fig.to_html(
                    full_html=False,
                    include_plotlyjs="cdn",
                    config=config_plotly(titulo, alto=int(fig.layout.height or alto)),
                    div_id=f"sf_{nombre_archivo(titulo)}",
                )
                display(HTML(fragmento))

            productos = ejecutar_pipeline(repo_dir=repo, data_dir=repo / "data" / "raw")
            FUENTE_INAB = "INAB y CONAP (2023) e INAB (2023b); cálculos del autor."
            FUENTE_POORTER = "INAB y CONAP (2023), INAB (2023b) y Poorter et al. (2016, 2017); cálculos del autor."
            FUENTE_VALORACION = "Banco Mundial et al. (2021) y Banco de Guatemala (s. f.); cálculos del autor."
            FUENTE_MANGLE = "INAB (2023a), INAB et al. (2016), e INAB y CONAP (2023); cálculos del autor."
            FUENTE_ESCENARIOS = "INAB y CONAP (2023) e INAB (2023b); supuestos y cálculos del autor."
            """,
            titulo_colab="Preparar entorno y reconstruir resultados",
        ),
        _texto(
            r"""
            ## 1. Antecedente descriptivo del problema de la deforestación neta

            La identidad institucional $N=B-R$ es aritméticamente correcta. Su interpretación
            como desempeño forestal descuenta toda recuperación de la pérdida en el mismo período.
            *Bosques* reúne las estimaciones disponibles desde 1991 y documenta que, entre
            1991–2001 y 2010–2016, la pérdida bruta anual aumentó aproximadamente 32 %, mientras
            la pérdida neta anual disminuyó cerca de 75 % (Sandoval García et al., 2022).

            *El año 1991 aparece porque inicia el primer intervalo recopilado por esa fuente.* No
            amplía el período municipal ni entra en los cálculos de 2016–2020. Los intervalos
            tienen duraciones y métodos de medición propios; la figura es un antecedente
            comparativo y no una serie anual continua.
            """
        ),
        _codigo(
            """
            historica = productos["serie_historica_1991_2016"].copy()
            larga_historica = historica.melt(
                id_vars="periodo",
                value_vars=["perdida_bruta_anual_reportada_ha", "perdida_neta_anual_reportada_ha"],
                var_name="Indicador",
                value_name="Hectáreas por año",
            )
            larga_historica["Indicador"] = larga_historica["Indicador"].map({
                "perdida_bruta_anual_reportada_ha": "Pérdida bruta",
                "perdida_neta_anual_reportada_ha": "Pérdida neta",
            })
            fig_historica = px.line(
                larga_historica,
                x="periodo", y="Hectáreas por año", color="Indicador", symbol="Indicador",
                markers=True,
                color_discrete_map={"Pérdida bruta": "#D55E00", "Pérdida neta": "#0072B2"},
                symbol_map={"Pérdida bruta": "circle", "Pérdida neta": "diamond"},
            )
            fig_historica.update_traces(marker_size=9, line_width=2.5)
            fig_historica.update_xaxes(title="Intervalo de referencia")
            fig_historica.update_yaxes(title="ha/año", rangemode="tozero", tickformat=",")
            """,
            titulo_colab="Construir Figura 1",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_historica,
                "Figura 1. Divergencia histórica entre pérdida bruta y pérdida neta reportadas",
                "Antecedente descriptivo fuera del análisis municipal 2016–2020. Cada punto corresponde a un intervalo de medición distinto; las líneas facilitan la comparación y no implican continuidad anual.",
                "Sandoval García et al. (2022); cálculos del autor.",
                alto=640,
            )
            """,
            titulo_colab="Mostrar Figura 1",
            resultado=True,
        ),
        _texto(
            r"""
            ## 2. Reproducción del resultado institucional 2016–2020

            Para las 342 unidades de la base oficial —340 municipios y dos unidades lacustres
            documentadas por el Instituto Nacional de Bosques (INAB) y el Consejo Nacional de
            Áreas Protegidas (CONAP) (2023), con detalle municipal en INAB (2023b)— se reproduce
            la identidad:

            $$N_i=B_i-R_i.$$

            $R_i$ es la recuperación reportada, denominada *ganancia de cobertura forestal* en
            la fuente. Se obtiene al comparar las coberturas de 2016 y 2020; no informa la edad,
            biomasa, origen o permanencia de esa ganancia.

            El total nacional acumulado del período es 244,395 ha de pérdida bruta, 191,658 ha
            de recuperación y 52,736 ha de pérdida neta. Esta sección muestra primero el
            resultado institucional en sus propios términos y establece el punto de comparación
            para la ponderación de la recuperación.
            """
        ),
        _codigo(
            """
            nacional = productos["resultados_institucionales_nacionales"].iloc[0]
            tabla_nacional = pd.DataFrame({
                "Magnitud": ["Pérdida bruta", "Ganancia de cobertura", "Pérdida neta reportada"],
                "Acumulado 2016–2020 (ha)": [
                    nacional.perdida_bruta_ha,
                    nacional.recuperacion_bruta_ha,
                    nacional.perdida_neta_ha,
                ],
                "Lectura": ["B", "R", "N = B − R"],
            })
            """,
            titulo_colab="Preparar resultado nacional institucional",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_nacional,
                "Tabla 1. Magnitudes nacionales del cálculo institucional",
                "La recuperación se descuenta en proporción uno a uno; las cifras acumuladas corresponden a 2016–2020.",
                FUENTE_INAB,
                decimales=1,
                max_filas=None,
                archivo="tabla_01_magnitudes_institucionales_nacionales.csv",
                descarga=productos["resultados_institucionales_nacionales"],
            )
            """,
            titulo_colab="Mostrar Tabla 2",
            resultado=True,
        ),
        _codigo(
            """
            fig_componentes = go.Figure(go.Waterfall(
                x=["Pérdida bruta", "Ganancia de cobertura", "Pérdida neta"],
                y=[nacional.perdida_bruta_ha, -nacional.recuperacion_bruta_ha, nacional.perdida_neta_ha],
                measure=["absolute", "relative", "total"],
                text=[
                    f"+{nacional.perdida_bruta_ha:,.0f}",
                    f"−{nacional.recuperacion_bruta_ha:,.0f}",
                    f"{nacional.perdida_neta_ha:,.0f}",
                ],
                textposition="outside",
                increasing=dict(marker_color="#D55E00"),
                decreasing=dict(marker_color="#0072B2"),
                totals=dict(marker_color="#009E73"),
                connector=dict(line=dict(color="#8B9AA0", dash="dot")),
                hovertemplate="%{x}<br>%{y:,.1f} ha<extra></extra>",
            ))
            fig_componentes.update_layout(showlegend=False)
            fig_componentes.update_yaxes(
                title="ha acumuladas", range=[0, nacional.perdida_bruta_ha * 1.13], tickformat=","
            )
            fig_componentes.update_xaxes(title=None)
            """,
            titulo_colab="Construir Figura 2",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_componentes,
                "Figura 2. Componentes del resultado institucional nacional, 2016–2020",
                "La recuperación se muestra como una sustracción contable. La operación reproduce el reporte institucional, pero no demuestra equivalencia ecológica inmediata.",
                FUENTE_INAB,
                alto=620,
            )
            """,
            titulo_colab="Mostrar Figura 2",
            resultado=True,
        ),
        _codigo(
            """
            departamentales = productos["resultados_institucionales_departamentales"].copy()
            tabla_departamental = departamentales[[
                "depto", "perdida_bruta_ha", "recuperacion_bruta_ha", "perdida_neta_ha"
            ]].rename(columns={
                "depto": "Departamento",
                "perdida_bruta_ha": "Pérdida bruta (ha)",
                "recuperacion_bruta_ha": "Recuperación bruta (ha)",
                "perdida_neta_ha": "Pérdida neta (ha)",
            }).sort_values("Pérdida neta (ha)", ascending=False)
            """,
            titulo_colab="Preparar resultados departamentales institucionales",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_departamental,
                "Tabla 2. Resultados departamentales del cálculo institucional",
                "Orden descendente por pérdida neta acumulada. Las dos unidades lacustres permanecen en los agregados departamentales y se identifican en completacion_nacional_unidades.csv dentro de la descarga integral.",
                FUENTE_INAB,
                decimales=1,
                max_filas=None,
                archivo="tabla_02_resultados_institucionales_departamentales.csv",
                descarga=departamentales,
            )
            """,
            titulo_colab="Mostrar Tabla 3",
            resultado=True,
        ),
        _codigo(
            """
            orden_departamental = departamentales.sort_values("perdida_neta_ha")
            fig_departamentos = go.Figure(go.Bar(
                x=orden_departamental["perdida_neta_ha"],
                y=orden_departamental["depto"],
                orientation="h",
                marker_color=np.where(
                    orden_departamental["perdida_neta_ha"].ge(0), "#D55E00", "#009E73"
                ),
                text=[f"{v:,.0f}" for v in orden_departamental["perdida_neta_ha"]],
                textposition="outside",
                hovertemplate="%{y}<br>Pérdida neta: %{x:,.1f} ha<extra></extra>",
                name="Pérdida neta",
            ))
            fig_departamentos.add_vline(x=0, line_color="#5C6F77", line_width=1)
            minimo_dep = orden_departamental["perdida_neta_ha"].min()
            maximo_dep = orden_departamental["perdida_neta_ha"].max()
            amplitud_dep = maximo_dep - minimo_dep
            fig_departamentos.update_xaxes(
                title="Pérdida neta (ha); la ganancia se muestra a la izquierda",
                range=[min(0, minimo_dep - 0.12 * amplitud_dep), maximo_dep + 0.18 * amplitud_dep],
                tickformat=",",
            )
            fig_departamentos.update_yaxes(title=None)
            mostrar_figura(
                fig_departamentos,
                "Figura 3. Pérdida neta institucional por departamento, 2016–2020",
                "Las barras positivas indican pérdida y las negativas ganancia de cobertura bajo N = B − R.",
                FUENTE_INAB,
                alto=820,
            )
            """,
            titulo_colab="Construir Figura 3",
            resultado=True,
        ),
        _codigo(
            """
            municipales = productos["resultados_institucionales_municipales"].copy()
            extremos_municipales = pd.concat([
                municipales.nsmallest(10, "perdida_neta_ha"),
                municipales.nlargest(10, "perdida_neta_ha"),
            ]).drop_duplicates("codigo").sort_values("perdida_neta_ha", ascending=False)
            tabla_municipal = extremos_municipales[[
                "depto", "municipio", "perdida_neta_ha", "clasificacion_institucional"
            ]].rename(columns={
                "depto": "Departamento", "municipio": "Municipio",
                "perdida_neta_ha": "Pérdida neta (ha)",
                "clasificacion_institucional": "Clasificación",
            })
            mostrar_tabla(
                tabla_municipal,
                "Tabla 3. Municipios con mayores pérdidas y ganancias institucionales",
                "Se muestran los diez valores más altos y los diez más bajos; el CSV contiene los 340 municipios.",
                FUENTE_INAB,
                decimales=1,
                max_filas=None,
                archivo="tabla_03_resultados_institucionales_municipales.csv",
                descarga=municipales,
            )
            """,
            titulo_colab="Mostrar Tabla 4",
            resultado=True,
        ),
        _codigo(
            """
            municipales["recuperacion_log1p"] = np.log10(1 + municipales["recuperacion_bruta_ha"])
            municipales["perdida_log1p"] = np.log10(1 + municipales["perdida_bruta_ha"])
            fig_municipios = px.scatter(
                municipales,
                x="recuperacion_log1p", y="perdida_log1p",
                color="clasificacion_institucional", symbol="clasificacion_institucional",
                hover_name="municipio",
                custom_data=["depto", "recuperacion_bruta_ha", "perdida_bruta_ha", "perdida_neta_ha"],
                labels={
                    "recuperacion_log1p": "Ganancia de cobertura (ha; escala log₁₀[1+x])",
                    "perdida_log1p": "Pérdida bruta (ha; escala log₁₀[1+x])",
                    "clasificacion_institucional": "Clasificación",
                },
                color_discrete_map={"Pérdida": "#D55E00", "Ganancia": "#0072B2", "Equilibrio": "#E69F00"},
                symbol_map={"Pérdida": "circle", "Ganancia": "diamond", "Equilibrio": "square"},
            )
            limite = max(municipales["recuperacion_bruta_ha"].max(), municipales["perdida_bruta_ha"].max())
            fig_municipios.add_trace(go.Scatter(
                x=[0, np.log10(1 + limite)], y=[0, np.log10(1 + limite)], mode="lines", name="B = R",
                line=dict(color="#66777E", dash="dash"), hoverinfo="skip"
            ))
            marcas = [0, 10, 100, 1000, 10000, 30000]
            fig_municipios.update_xaxes(tickvals=np.log10(1 + np.array(marcas)), ticktext=[f"{v:,}" for v in marcas])
            fig_municipios.update_yaxes(tickvals=np.log10(1 + np.array(marcas)), ticktext=[f"{v:,}" for v in marcas])
            fig_municipios.update_traces(
                selector=dict(mode="markers"),
                marker=dict(size=8, opacity=0.75, line=dict(width=0.5, color="white")),
                hovertemplate=(
                    "%{hovertext}<br>Departamento: %{customdata[0]}"
                    "<br>Recuperación: %{customdata[1]:,.1f} ha"
                    "<br>Pérdida bruta: %{customdata[2]:,.1f} ha"
                    "<br>Pérdida neta: %{customdata[3]:,.1f} ha<extra></extra>"
                ),
            )
            """,
            titulo_colab="Construir Figura 3",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_municipios,
                "Figura 4. Pérdida bruta y ganancia de cobertura por municipio",
                "La transformación log₁₀(1+x) conserva los 340 municipios, incluidos los valores cero. Sobre B = R hay pérdida institucional; debajo hay ganancia.",
                FUENTE_INAB,
                alto=720,
            )
            """,
            titulo_colab="Mostrar Figura 3",
            resultado=True,
        ),
        _texto(
            r"""
            ## 3. Proporciones regionales de recuperación de biomasa a veinte años

            Poorter et al. (2016) sintetizan la recuperación de biomasa aérea de bosques
            secundarios tropicales veinte años después del abandono. Sus datos abarcan 45 sitios
            neotropicales y muestran una variación sustantiva entre condiciones ambientales
            (Poorter et al., 2017). Aquí esos resultados se convierten en cinco intervalos regionales
            de $\rho_{20}$ para explorar cuánto de la recuperación reportada podría tratarse
            como recuperación de biomasa en ese horizonte:

            $$H_i(\rho_{20})=B_i-\rho_{20,i}R_i.$$

            Como cada intervalo regional contiene un límite mínimo y máximo, y $R_i\geq0$, los extremos del
            saldo se calculan en orden inverso:

            $$H_i^{\mathrm{inf}}=B_i-\rho_{20,i}^{\max}R_i,$$

            $$H_i^{\mathrm{sup}}=B_i-\rho_{20,i}^{\min}R_i.$$

            La vinculación es deliberadamente generosa con la recuperación institucional: no se
            observan edad, origen, permanencia ni regeneración natural en cada ganancia municipal.
            Por ello $H$ es un *saldo forestal ponderado por recuperación*, no una medición actual de
            biomasa ni una corrección oficial de cobertura.
            """
        ),
        _codigo(
            """
            catalogo = productos["catalogo_proporciones_poorter"].copy()
            regiones_resumen = productos["resultados_poorter_regiones"][[
                "proporcion_region_id", "municipios"
            ]].copy()
            catalogo = catalogo.merge(regiones_resumen, on="proporcion_region_id", how="left")
            catalogo["Intervalo de proporción"] = catalogo.apply(
                lambda f: f"{f.rho20_min:.3f}–{f.rho20_max:.3f}", axis=1
            )
            tabla_catalogo = catalogo[[
                "region_nombre", "sitios_referencia", "rho20_central",
                "Intervalo de proporción", "municipios"
            ]].rename(columns={
                "region_nombre": "Región de referencia",
                "sitios_referencia": "Sitios de referencia",
                "rho20_central": "Proporción central",
                "municipios": "Municipios",
            })
            """,
            titulo_colab="Preparar catálogo de proporciones",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_catalogo,
                "Tabla 4. Proporciones regionales de recuperación de biomasa a veinte años",
                "Las proporciones se transfieren desde evidencia biofísica regional. No identifican la edad, el origen ni la permanencia de la recuperación reportada en cada municipio.",
                "Poorter et al. (2016, 2017); cálculos del autor.",
                decimales=3,
                max_filas=None,
                archivo="tabla_04_proporciones_regionales_recuperacion.csv",
                descarga=catalogo,
            )
            """,
            titulo_colab="Mostrar Tabla 5",
            resultado=True,
        ),
        _codigo(
            """
            catalogo_fig = catalogo.sort_values("rho20_central")
            fig_proporciones = go.Figure(go.Scatter(
                x=catalogo_fig["rho20_central"],
                y=catalogo_fig["region_nombre"],
                mode="markers",
                marker=dict(color="#6A3D9A", size=11, symbol="diamond"),
                error_x=dict(
                    type="data",
                    array=catalogo_fig["rho20_max"] - catalogo_fig["rho20_central"],
                    arrayminus=catalogo_fig["rho20_central"] - catalogo_fig["rho20_min"],
                    color="#6A3D9A",
                    thickness=2,
                    width=7,
                ),
                customdata=catalogo_fig[["sitios_referencia", "municipios"]],
                hovertemplate=(
                    "%{y}<br>Proporción central: %{x:.3f}"
                    "<br>Sitios: %{customdata[0]}<br>Municipios: %{customdata[1]}<extra></extra>"
                ),
                name="Proporción e intervalo",
            ))
            fig_proporciones.update_xaxes(
                title="Proporción de recuperación de biomasa a veinte años",
                range=[0, 1], tickformat=".0%"
            )
            fig_proporciones.update_yaxes(title=None)
            mostrar_figura(
                fig_proporciones,
                "Figura 5. Intervalos de recuperación de biomasa a veinte años por región de referencia",
                "El punto es la proporción central y la línea su intervalo. Son ponderadores transferidos, no mediciones de edad o biomasa municipal.",
                FUENTE_POORTER,
                alto=650,
            )
            """,
            titulo_colab="Construir Figura 5",
            resultado=True,
        ),
        _codigo(
            """
            dominio = productos["resultados_poorter_dominio"].iloc[0]
            tabla_dominio = pd.DataFrame({
                "Magnitud": ["Municipios", "Pérdida bruta", "Pérdida neta", "Saldo ponderado"],
                "Resultado": [
                    f"{int(dominio.municipios)}",
                    f"{dominio.perdida_bruta_ha:,.0f} ha",
                    f"{dominio.perdida_neta_ha:,.0f} ha",
                    f"{dominio.saldo_ponderado_inferior_ha:,.0f}–{dominio.saldo_ponderado_superior_ha:,.0f} ha",
                ],
                "Lectura": ["Dominio analítico", "B", "N = B − R", "H, intervalo"],
            })
            """,
            titulo_colab="Preparar resumen del dominio de aplicación",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_dominio,
                "Tabla 5. Resultado agregado dentro del dominio de 172 municipios",
                "El dominio cubre municipios con una proporción regional defendible; estas cifras no se presentan como total nacional.",
                FUENTE_POORTER,
                decimales=1,
                max_filas=None,
                archivo="tabla_05_resultado_dominio_aplicacion.csv",
                descarga=productos["resultados_poorter_dominio"],
            )
            """,
            titulo_colab="Mostrar Tabla 6",
            resultado=True,
        ),
        _codigo(
            """
            poorter_departamentos = productos["resultados_poorter_departamentales"].copy()
            poorter_departamentos["Saldo ponderado (ha)"] = poorter_departamentos.apply(
                lambda f: f"{f.saldo_ponderado_inferior_ha:,.0f}–{f.saldo_ponderado_superior_ha:,.0f}",
                axis=1,
            )
            tabla_poorter_departamentos = poorter_departamentos[[
                "depto", "municipios", "perdida_neta_ha", "Saldo ponderado (ha)"
            ]].rename(columns={
                "depto": "Departamento", "municipios": "Municipios del dominio",
                "perdida_neta_ha": "Pérdida neta (ha)",
            }).sort_values("Pérdida neta (ha)", ascending=False)
            """,
            titulo_colab="Preparar resultados departamentales ponderados",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_poorter_departamentos,
                "Tabla 6. Resultados departamentales dentro del dominio de aplicación",
                "Cada agregado incluye únicamente municipios con proporción regional asignada; por ello no equivale necesariamente al total departamental.",
                FUENTE_POORTER,
                decimales=1,
                max_filas=None,
                archivo="tabla_06_resultados_recuperacion_departamentales.csv",
                descarga=poorter_departamentos,
            )
            """,
            titulo_colab="Mostrar Tabla 7",
            resultado=True,
        ),
        _codigo(
            """
            poorter_municipios = productos["resultados_poorter_municipales"].copy()
            poorter_municipios["recuperacion_reconocida_central_ha"] = (
                poorter_municipios["rho20_central"] * poorter_municipios["recuperacion_bruta_ha"]
            )
            poorter_municipios["clasificacion_central"] = np.select(
                [
                    poorter_municipios["saldo_ponderado_central_ha"].gt(0),
                    poorter_municipios["saldo_ponderado_central_ha"].lt(0),
                ],
                ["Pérdida", "Ganancia"],
                default="Equilibrio",
            )
            panel_institucional = poorter_municipios.assign(
                Tratamiento="Cálculo reportado: R completa",
                recuperacion_reconocida_ha=poorter_municipios["recuperacion_bruta_ha"],
                Clasificación=poorter_municipios["clasificacion_institucional"],
            )
            panel_ponderado = poorter_municipios.assign(
                Tratamiento="Ponderación: ρ central × R",
                recuperacion_reconocida_ha=poorter_municipios["recuperacion_reconocida_central_ha"],
                Clasificación=poorter_municipios["clasificacion_central"],
            )
            dispersion_paneles = pd.concat([panel_institucional, panel_ponderado], ignore_index=True)
            dispersion_paneles["x_log1p"] = np.log10(1 + dispersion_paneles["recuperacion_reconocida_ha"])
            dispersion_paneles["y_log1p"] = np.log10(1 + dispersion_paneles["perdida_bruta_ha"])
            fig_paneles = px.scatter(
                dispersion_paneles,
                x="x_log1p", y="y_log1p", facet_col="Tratamiento",
                facet_col_spacing=0.06,
                color="Clasificación", symbol="Clasificación", hover_name="municipio",
                custom_data=["depto", "recuperacion_reconocida_ha", "perdida_bruta_ha"],
                color_discrete_map={"Pérdida": "#D55E00", "Ganancia": "#0072B2", "Equilibrio": "#E69F00"},
                symbol_map={"Pérdida": "circle", "Ganancia": "diamond", "Equilibrio": "square"},
                category_orders={"Tratamiento": ["Cálculo reportado: R completa", "Ponderación: ρ central × R"]},
            )
            limite_panel = max(
                dispersion_paneles["recuperacion_reconocida_ha"].max(),
                dispersion_paneles["perdida_bruta_ha"].max(),
            )
            limite_panel_log = np.log10(1 + limite_panel)
            for columna in (1, 2):
                fig_paneles.add_shape(
                    type="line", x0=0, y0=0, x1=limite_panel_log, y1=limite_panel_log,
                    line=dict(color="#5C6F77", dash="dash"), row=1, col=columna,
                )
            marcas_panel = [0, 10, 100, 1000, 10000, 30000]
            fig_paneles.update_xaxes(
                title=None, matches="x",
                tickvals=np.log10(1 + np.array(marcas_panel)), ticktext=[f"{v:,}" for v in marcas_panel]
            )
            fig_paneles.update_yaxes(
                title=None, matches="y",
                tickvals=np.log10(1 + np.array(marcas_panel)), ticktext=[f"{v:,}" for v in marcas_panel]
            )
            fig_paneles.update_yaxes(
                title_text="Pérdida bruta (ha; log₁₀[1+x])", row=1, col=1
            )
            fig_paneles.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig_paneles.add_annotation(
                text="Recuperación reconocida (ha; log₁₀[1+x])",
                x=0.5, y=0, xref="paper", yref="paper", yshift=-44,
                showarrow=False, font=dict(size=12, color="#24363D"),
            )
            fig_paneles.update_traces(
                marker=dict(size=7, opacity=0.72, line=dict(width=0.4, color="white")),
                hovertemplate=(
                    "%{hovertext}<br>Departamento: %{customdata[0]}"
                    "<br>Recuperación reconocida: %{customdata[1]:,.1f} ha"
                    "<br>Pérdida bruta: %{customdata[2]:,.1f} ha<extra></extra>"
                ),
            )
            mostrar_figura(
                fig_paneles,
                "Figura 6. Dispersión municipal antes y después de aplicar la ponderación",
                "Los dos paneles usan los mismos 172 municipios y escalas. La diagonal compara B con la recuperación reconocida; el panel ponderado reduce R mediante la proporción central.",
                FUENTE_POORTER,
                alto=770,
            )
            """,
            titulo_colab="Construir Figura 6",
            resultado=True,
        ),
        _codigo(
            """
            escala_simetica = lambda s: np.sign(s) * np.log10(1 + np.abs(s) / 100)
            poorter_municipios["N_transformado"] = escala_simetica(poorter_municipios["perdida_neta_ha"])
            poorter_municipios["H_transformado"] = escala_simetica(poorter_municipios["saldo_ponderado_central_ha"])
            poorter_municipios["Estado del cambio"] = np.select(
                [
                    poorter_municipios["clasificacion_institucional"].eq("Ganancia")
                    & poorter_municipios["clasificacion_ponderada"].eq("Pérdida"),
                    poorter_municipios["clasificacion_ponderada"].eq("Indeterminado"),
                ],
                ["Ganancia → pérdida", "Hacia indeterminado"],
                default="Sin cambio de clase",
            )
            fig_cambio = px.scatter(
                poorter_municipios,
                x="N_transformado", y="H_transformado", color="Estado del cambio",
                symbol="Estado del cambio", hover_name="municipio",
                custom_data=[
                    "depto", "perdida_neta_ha", "saldo_ponderado_central_ha",
                    "saldo_ponderado_inferior_ha", "saldo_ponderado_superior_ha"
                ],
                color_discrete_map={
                    "Sin cambio de clase": "#8B9AA0",
                    "Ganancia → pérdida": "#D55E00",
                    "Hacia indeterminado": "#E69F00",
                },
                symbol_map={
                    "Sin cambio de clase": "circle-open",
                    "Ganancia → pérdida": "diamond",
                    "Hacia indeterminado": "square",
                },
            )
            limite_cambio = max(
                poorter_municipios["N_transformado"].abs().max(),
                poorter_municipios["H_transformado"].abs().max(),
            )
            fig_cambio.add_trace(go.Scatter(
                x=[-limite_cambio, limite_cambio], y=[-limite_cambio, limite_cambio],
                mode="lines", name="H = N", line=dict(color="#5C6F77", dash="dash"),
                hoverinfo="skip",
            ))
            fig_cambio.add_hline(y=0, line_color="#AAB7BC", line_width=1)
            fig_cambio.add_vline(x=0, line_color="#AAB7BC", line_width=1)
            marcas_simeticas = [-10000, -1000, -100, 0, 100, 1000, 10000]
            posiciones_simeticas = escala_simetica(np.array(marcas_simeticas))
            fig_cambio.update_xaxes(
                title="Pérdida neta institucional, N (ha; escala simétrica)",
                tickvals=posiciones_simeticas, ticktext=[f"{v:,}" for v in marcas_simeticas]
            )
            fig_cambio.update_yaxes(
                title="Saldo ponderado central, H (ha; escala simétrica)",
                tickvals=posiciones_simeticas, ticktext=[f"{v:,}" for v in marcas_simeticas]
            )
            fig_cambio.update_traces(
                selector=dict(mode="markers"),
                marker=dict(size=8, opacity=0.8),
                hovertemplate=(
                    "%{hovertext}<br>Departamento: %{customdata[0]}"
                    "<br>N institucional: %{customdata[1]:,.1f} ha"
                    "<br>H central: %{customdata[2]:,.1f} ha"
                    "<br>Intervalo H: %{customdata[3]:,.1f}–%{customdata[4]:,.1f} ha<extra></extra>"
                ),
            )
            mostrar_figura(
                fig_cambio,
                "Figura 7. Cambio municipal entre la pérdida neta y el saldo ponderado",
                "La misma transformación simétrica se aplica a ambos ejes y conserva negativos y ceros. Quince municipios pasan de ganancia a pérdida y once quedan indeterminados o cambian desde equilibrio.",
                FUENTE_POORTER,
                alto=760,
            )
            """,
            titulo_colab="Construir Figura 7",
            resultado=True,
        ),
        _codigo(
            """
            transiciones = productos["transiciones_clasificacion_poorter"].copy()
            orden_i = ["Ganancia", "Equilibrio", "Pérdida"]
            orden_p = ["Ganancia", "Indeterminado", "Pérdida"]
            matriz_n = transiciones.pivot(
                index="clasificacion_institucional", columns="clasificacion_ponderada", values="municipios"
            ).reindex(index=orden_i, columns=orden_p).fillna(0)
            matriz_pct = transiciones.pivot(
                index="clasificacion_institucional", columns="clasificacion_ponderada", values="porcentaje_fila"
            ).reindex(index=orden_i, columns=orden_p).fillna(0)
            texto_matriz = [
                [f"{int(matriz_n.iloc[i, j])}<br>{matriz_pct.iloc[i, j]:.1f}%" for j in range(len(orden_p))]
                for i in range(len(orden_i))
            ]
            fig_transiciones = go.Figure(go.Heatmap(
                z=matriz_n.values,
                x=orden_p,
                y=orden_i,
                text=texto_matriz,
                texttemplate="%{text}",
                colorscale=[[0, "#F7FAFA"], [1, "#6A3D9A"]],
                colorbar=dict(title="Municipios"),
                hovertemplate="Institucional: %{y}<br>Ponderada: %{x}<br>Municipios: %{z}<extra></extra>",
            ))
            fig_transiciones.update_xaxes(title="Clasificación con intervalo ponderado", side="bottom")
            fig_transiciones.update_yaxes(title="Clasificación institucional", autorange="reversed")
            mostrar_figura(
                fig_transiciones,
                "Figura 8. Transición de clasificaciones municipales al aplicar el ponderador",
                "Cada celda muestra municipios y porcentaje dentro de la clasificación institucional de origen. Cambian 26 de 172 diagnósticos.",
                FUENTE_POORTER,
                alto=650,
            )
            """,
            titulo_colab="Construir Figura 8",
            resultado=True,
        ),
        _codigo(
            """
            tabla_transiciones = matriz_n.reset_index().rename(columns={
                "clasificacion_institucional": "Clasificación institucional",
                "Ganancia": "Ponderada: ganancia",
                "Indeterminado": "Ponderada: indeterminado",
                "Pérdida": "Ponderada: pérdida",
            })
            mostrar_tabla(
                tabla_transiciones,
                "Tabla 7. Matriz de transición de clasificaciones municipales",
                "Los conteos corresponden al dominio de 172 municipios; la clasificación ponderada usa el intervalo completo, no solo el punto central.",
                FUENTE_POORTER,
                decimales=0,
                max_filas=None,
                archivo="tabla_07_transiciones_clasificacion_ponderada.csv",
                descarga=transiciones,
            )
            """,
            titulo_colab="Mostrar Tabla 7",
            resultado=True,
        ),
        _codigo(
            """
            cambios = productos["municipios_cambio_clasificacion_poorter"].copy()
            cambios["brecha_central_ha"] = (
                cambios["saldo_ponderado_central_ha"] - cambios["perdida_neta_ha"]
            )
            cambios_visibles = cambios.nlargest(20, "brecha_central_ha")
            tabla_cambios = cambios_visibles[[
                "depto", "municipio", "perdida_neta_ha", "saldo_ponderado_central_ha",
                "cambio_clasificacion"
            ]].rename(columns={
                "depto": "Departamento", "municipio": "Municipio",
                "perdida_neta_ha": "Pérdida neta (ha)",
                "saldo_ponderado_central_ha": "Saldo ponderado central (ha)",
                "cambio_clasificacion": "Cambio",
            })
            mostrar_tabla(
                tabla_cambios,
                "Tabla 8. Municipios con mayor cambio de diagnóstico al ponderar la recuperación",
                "Se muestran los veinte mayores aumentos del saldo; el CSV contiene los 26 municipios cuya clasificación cambia con el intervalo ponderado.",
                FUENTE_POORTER,
                decimales=1,
                max_filas=None,
                archivo="tabla_08_municipios_cambio_clasificacion.csv",
                descarga=cambios,
            )
            """,
            titulo_colab="Mostrar Tabla 8",
            resultado=True,
        ),
        _codigo(
            """
            forestal_dep = poorter_departamentos.copy()
            forestal_dep["centro"] = (
                forestal_dep["saldo_ponderado_inferior_ha"] + forestal_dep["saldo_ponderado_superior_ha"]
            ) / 2
            forestal_dep = forestal_dep.sort_values("centro")
            fig_departamentos_poorter = go.Figure()
            for fila in forestal_dep.itertuples(index=False):
                fig_departamentos_poorter.add_trace(go.Scatter(
                    x=[fila.perdida_neta_ha, fila.centro], y=[fila.depto, fila.depto],
                    mode="lines", line=dict(color="#CBD5D8", width=2),
                    showlegend=False, hoverinfo="skip",
                ))
            fig_departamentos_poorter.add_trace(go.Scatter(
                x=forestal_dep["perdida_neta_ha"], y=forestal_dep["depto"],
                mode="markers", name="Pérdida neta institucional",
                marker=dict(color="#0072B2", symbol="square", size=8),
                hovertemplate="%{y}<br>N: %{x:,.1f} ha<extra></extra>",
            ))
            fig_departamentos_poorter.add_trace(go.Scatter(
                x=forestal_dep["centro"], y=forestal_dep["depto"],
                mode="markers", name="Saldo ponderado",
                marker=dict(color="#6A3D9A", symbol="diamond", size=9),
                error_x=dict(
                    type="data",
                    array=forestal_dep["saldo_ponderado_superior_ha"] - forestal_dep["centro"],
                    arrayminus=forestal_dep["centro"] - forestal_dep["saldo_ponderado_inferior_ha"],
                    color="#6A3D9A",
                ),
                hovertemplate="%{y}<br>H central: %{x:,.1f} ha<extra></extra>",
            ))
            fig_departamentos_poorter.add_vline(x=0, line_color="#5C6F77", line_width=1)
            fig_departamentos_poorter.update_xaxes(title="Resultado (ha); la pérdida es positiva", tickformat=",")
            fig_departamentos_poorter.update_yaxes(title=None)
            mostrar_figura(
                fig_departamentos_poorter,
                "Figura 9. Cambio departamental entre pérdida neta y saldo ponderado",
                "Solo incluye municipios del dominio de aplicación. El cuadrado es N; el diamante y su intervalo representan H. Las líneas grises unen lecturas alternativas.",
                FUENTE_POORTER,
                alto=820,
            )
            """,
            titulo_colab="Construir Figura 9",
            resultado=True,
        ),
        _texto(
            r"""
            ## 4. Completación conservadora del resultado nacional

            Para no extrapolar las proporciones regionales a ecosistemas sin un puente defendible, la
            completación nacional aplica $\rho_{20}$ únicamente dentro del dominio de 172
            municipios. Fuera de él conserva el cálculo institucional $\rho=1$:

            $$H_{GT}=\sum_{i\in P}(B_i-\rho_{20,i}R_i)+\sum_{i\notin P}(B_i-R_i).$$

            Esta decisión conserva fuera del dominio la compensación completa de la recuperación.
            El resultado nacional ponderado (116,473–123,988 ha) permanece entre la pérdida
            bruta y la pérdida neta institucional (INAB & CONAP, 2023; Poorter et al., 2016, 2017).
            """
        ),
        _codigo(
            """
            completacion = productos["completacion_nacional_resumen"].copy()
            fila_completacion = completacion.iloc[0]
            tabla_completacion = pd.DataFrame({
                "Magnitud": [
                    "Unidades nacionales", "Municipios con proporción a veinte años",
                    "Pérdida bruta", "Ganancia de cobertura", "Pérdida neta",
                    "Saldo ponderado nacional",
                ],
                "Resultado": [
                    f"{int(fila_completacion.unidades)}",
                    f"{int(fila_completacion.municipios_con_proporcion)}",
                    f"{fila_completacion.perdida_bruta_ha:,.0f} ha",
                    f"{fila_completacion.recuperacion_bruta_ha:,.0f} ha",
                    f"{fila_completacion.perdida_neta_ha:,.0f} ha",
                    f"{fila_completacion.saldo_ponderado_inferior_ha:,.0f}–{fila_completacion.saldo_ponderado_superior_ha:,.0f} ha",
                ],
                "Método": ["Cobertura", "ρ₂₀", "B", "R", "N = B − R", "Completación conservadora"],
            })
            """,
            titulo_colab="Preparar completación nacional",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_completacion,
                "Tabla 9. Completación conservadora del saldo forestal nacional",
                "Dentro del dominio se aplica el intervalo de ρ₂₀; fuera se conserva ρ = 1. El intervalo refleja únicamente las proporciones transferidas.",
                FUENTE_POORTER,
                decimales=1,
                max_filas=None,
                archivo="tabla_09_completacion_nacional.csv",
                descarga=completacion,
            )
            """,
            titulo_colab="Mostrar Tabla 9",
            resultado=True,
        ),
        _codigo(
            """
            reglas = productos["comparacion_reglas_nacional"].copy()
            reglas["central"] = (reglas["resultado_inferior_ha"] + reglas["resultado_superior_ha"]) / 2
            reglas["err_mas"] = reglas["resultado_superior_ha"] - reglas["central"]
            reglas["err_menos"] = reglas["central"] - reglas["resultado_inferior_ha"]
            orden_reglas = ["Deforestación bruta", "Saldo ponderado por recuperación", "Pérdida neta institucional"]
            reglas["regla"] = pd.Categorical(reglas["regla"], categories=orden_reglas, ordered=True)
            reglas = reglas.sort_values("regla")
            fig_reglas = go.Figure(go.Scatter(
                x=reglas["central"], y=reglas["regla"].astype(str), mode="markers+text",
                marker=dict(
                    color=["#D55E00", "#6A3D9A", "#0072B2"],
                    symbol=["circle", "diamond", "square"], size=12,
                ),
                error_x=dict(type="data", array=reglas["err_mas"], arrayminus=reglas["err_menos"]),
                text=[f"  {v:,.0f}" for v in reglas["central"]], textposition="middle right",
                hovertemplate="%{y}<br>%{x:,.0f} ha<extra></extra>",
            ))
            maximo_resultados = reglas["resultado_superior_ha"].max()
            fig_reglas.update_xaxes(
                title="ha acumuladas, 2016–2020", range=[0, maximo_resultados * 1.20], tickformat=","
            )
            fig_reglas.update_yaxes(title=None)
            """,
            titulo_colab="Construir Figura 5",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_reglas,
                "Figura 10. Deforestación bruta, saldo ponderado y pérdida neta nacional",
                "La línea del saldo ponderado muestra el intervalo nacional conservador. Los tres resultados parten de la misma base y no son categorías aditivas.",
                FUENTE_POORTER,
                alto=660,
            )
            """,
            titulo_colab="Mostrar Figura 5",
            resultado=True,
        ),
        _texto(
            r"""
            ## 5. Valoración indicativa de los resultados forestales

            La transferencia utiliza Q29,986 por ha por año, valor homologado a 2026 a partir de
            Q22,553 por ha por año. La Cuenta de ecosistemas de Guatemala integra 21 estudios
            sobre 9,403 km², cerca de 8 % del territorio, y combina servicios y métodos distintos
            (Banco Mundial et al., 2021). En consecuencia, la monetización *no es una valoración
            primaria ni constituye por sí sola una cuenta de ecosistemas conforme al SCAE-CE*
            (Naciones Unidas et al., 2021).

            La homologación aplica el cociente entre los deflactores implícitos del PIB de 2026
            (escenario bajo) y 2019, calculados como PIB nominal dividido por PIB real. Con las
            series oficiales, el factor es 1.3296 (Banco de Guatemala, s. f.).

            Se distinguen tres objetos: (a) flujo anual asociado a una cohorte anual de pérdida;
            (b) valor presente de 25 años de servicios para esa cohorte; y (c) valor presente de
            diez cohortes anuales. No deben intercambiarse como si fueran la misma magnitud.

            Para un resultado acumulado $H_i$ de cuatro años, el flujo físico anual medio es

            $$h_i=\frac{H_i}{4}.$$

            Con valor unitario anual $v$, el flujo monetario es $F_i=v h_i$. Su valor presente
            durante $T$ años a una tasa $r$ se calcula como

            $$VP_i=F_i\left[\frac{1-(1+r)^{-T}}{r}\right].$$

            Para diez cohortes anuales consecutivas:

            $$VP_{i,10}=\sum_{k=1}^{10}\frac{VP_i}{(1+r)^k}.$$
            """
        ),
        _codigo(
            """
            valoracion = productos["valoracion_reglas_nacional"].copy()
            def intervalo_millones(fila, inferior, superior):
                bajo, alto = fila[inferior] / 1e6, fila[superior] / 1e6
                return f"{bajo:,.1f}" if np.isclose(bajo, alto) else f"{bajo:,.1f}–{alto:,.1f}"

            tabla_valoracion = pd.DataFrame({
                "Resultado forestal": valoracion["regla"],
                "Flujo anual (Q millones)": valoracion.apply(
                    intervalo_millones, axis=1,
                    args=("flujo_anual_inferior_gtq", "flujo_anual_superior_gtq")
                ),
                "VP de una cohorte (Q millones)": valoracion.apply(
                    intervalo_millones, axis=1,
                    args=("vp_cohorte_inferior_gtq", "vp_cohorte_superior_gtq")
                ),
                "VP de 10 cohortes (Q millones)": valoracion.apply(
                    intervalo_millones, axis=1,
                    args=("vp_diez_cohortes_inferior_gtq", "vp_diez_cohortes_superior_gtq")
                ),
            })
            """,
            titulo_colab="Preparar valoración nacional",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_valoracion,
                "Tabla 10. Valoración indicativa de los resultados forestales nacionales",
                "Q de 2026. Tasa central de 4%, horizonte de servicios de 25 años y diez cohortes anuales. Los intervalos solo difieren para el saldo ponderado.",
                FUENTE_VALORACION,
                decimales=1,
                max_filas=None,
                archivo="tabla_10_valoracion_resultados_forestales.csv",
                descarga=valoracion,
            )
            """,
            titulo_colab="Mostrar Tabla 10",
            resultado=True,
        ),
        _codigo(
            """
            flujo = valoracion.copy()
            flujo["central_millones"] = (
                flujo["flujo_anual_inferior_gtq"] + flujo["flujo_anual_superior_gtq"]
            ) / 2e6
            flujo["err_mas"] = flujo["flujo_anual_superior_gtq"] / 1e6 - flujo["central_millones"]
            flujo["err_menos"] = flujo["central_millones"] - flujo["flujo_anual_inferior_gtq"] / 1e6
            fig_flujo = go.Figure(go.Bar(
                x=flujo["regla"], y=flujo["central_millones"],
                marker_color=["#D55E00", "#6A3D9A", "#0072B2"],
                error_y=dict(type="data", array=flujo["err_mas"], arrayminus=flujo["err_menos"]),
                text=[f"Q{v:,.0f} M" for v in flujo["central_millones"]], textposition="outside",
                hovertemplate="%{x}<br>Q%{y:,.1f} millones/año<extra></extra>",
            ))
            maximo_flujo = (flujo["central_millones"] + flujo["err_mas"]).max()
            fig_flujo.update_yaxes(
                title="Q millones por año", range=[0, maximo_flujo * 1.18], tickformat=","
            )
            fig_flujo.update_xaxes(title=None)
            """,
            titulo_colab="Construir Figura 6",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_flujo,
                "Figura 11. Flujo anual indicativo por resultado forestal",
                "La transferencia uniforme compara resultados, pero no representa valores municipales observados ni sustituye una valoración primaria.",
                FUENTE_VALORACION,
                alto=670,
            )
            """,
            titulo_colab="Mostrar Figura 6",
            resultado=True,
        ),
        _codigo(
            """
            sensibilidad = productos["sensibilidad_valor_presente"].copy()
            sensibilidad["VP inferior (Q millones)"] = sensibilidad["vp_cohorte_inferior_gtq"] / 1e6
            sensibilidad["VP superior (Q millones)"] = sensibilidad["vp_cohorte_superior_gtq"] / 1e6
            sensibilidad["VP de una cohorte (Q millones)"] = sensibilidad.apply(
                lambda f: (
                    f"{f['VP inferior (Q millones)']:,.1f}"
                    if np.isclose(f['VP inferior (Q millones)'], f['VP superior (Q millones)'])
                    else f"{f['VP inferior (Q millones)']:,.1f}–{f['VP superior (Q millones)']:,.1f}"
                ), axis=1
            )
            tabla_sensibilidad = sensibilidad[["regla", "tasa", "VP de una cohorte (Q millones)"]].rename(columns={
                "regla": "Resultado forestal", "tasa": "Tasa de descuento"
            })
            tabla_sensibilidad["Tasa de descuento"] = tabla_sensibilidad["Tasa de descuento"].map(
                lambda x: f"{x:.0%}"
            )
            """,
            titulo_colab="Preparar sensibilidad del valor presente",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_sensibilidad,
                "Tabla 11. Sensibilidad del valor presente de una cohorte anual",
                "Horizonte de servicios de 25 años; tasas de 2%, 4% y 5%. El saldo ponderado conserva un intervalo.",
                FUENTE_VALORACION,
                decimales=2,
                max_filas=None,
                archivo="tabla_11_sensibilidad_valor_presente.csv",
                descarga=sensibilidad,
            )
            """,
            titulo_colab="Mostrar Tabla 11",
            resultado=True,
        ),
        _codigo(
            """
            sensibilidad["VP central (Q millones)"] = (
                sensibilidad["VP inferior (Q millones)"] + sensibilidad["VP superior (Q millones)"]
            ) / 2
            colores_regla = {
                "Deforestación bruta": "#D55E00",
                "Saldo ponderado por recuperación": "#6A3D9A",
                "Pérdida neta institucional": "#0072B2",
            }
            trazos_regla = {
                "Deforestación bruta": "solid",
                "Saldo ponderado por recuperación": "dash",
                "Pérdida neta institucional": "dot",
            }
            simbolos_regla = {
                "Deforestación bruta": "circle",
                "Saldo ponderado por recuperación": "diamond",
                "Pérdida neta institucional": "square",
            }
            fig_sensibilidad = go.Figure()
            for regla_nombre in [
                "Deforestación bruta", "Saldo ponderado por recuperación", "Pérdida neta institucional"
            ]:
                serie = sensibilidad.loc[sensibilidad["regla"].eq(regla_nombre)].sort_values("tasa")
                fig_sensibilidad.add_trace(go.Scatter(
                    x=100 * serie["tasa"], y=serie["VP central (Q millones)"],
                    mode="lines+markers", name=regla_nombre,
                    line=dict(color=colores_regla[regla_nombre], dash=trazos_regla[regla_nombre], width=3),
                    marker=dict(symbol=simbolos_regla[regla_nombre], size=9),
                    error_y=dict(
                        type="data",
                        array=serie["VP superior (Q millones)"] - serie["VP central (Q millones)"],
                        arrayminus=serie["VP central (Q millones)"] - serie["VP inferior (Q millones)"],
                    ),
                    hovertemplate="Tasa: %{x:.0f}%<br>VP: Q%{y:,.1f} millones<extra>%{fullData.name}</extra>",
                ))
            fig_sensibilidad.update_xaxes(title="Tasa de descuento (%)", tickvals=[2, 4, 5])
            fig_sensibilidad.update_yaxes(title="VP de una cohorte (Q millones de 2026)", tickformat=",")
            mostrar_figura(
                fig_sensibilidad,
                "Figura 12. Sensibilidad del valor presente a la tasa de descuento",
                "Las líneas combinan color, trazo y marcador. El intervalo solo es visible para el saldo ponderado y el orden de los resultados no cambia entre tasas.",
                FUENTE_VALORACION,
                alto=680,
            )
            """,
            titulo_colab="Construir Figura 12",
            resultado=True,
        ),
        _texto(
            r"""
            ## 6. Escenarios 2026–2035

            Los escenarios modifican por separado la pérdida bruta y la recuperación mediante
            $m_s^B$ y $m_s^R$:

            $$H_{i,s}=m_s^B B_i-\rho_i m_s^R R_i.$$

            Los tres escenarios son proporcionales: contención ($0.25,0.25$), continuidad
            ($1,1$) y deterioro acelerado ($2,2$). La contención *no se denomina restauración*,
            porque no incorpora una trayectoria adicional de recuperación. La
            formulación deja preparado el modelo para escenarios asimétricos futuros.
            """
        ),
        _codigo(
            """
            escenarios = productos["escenarios_nacionales"].copy()
            tabla_escenarios = escenarios[[
                "escenario", "multiplicador_perdida_bruta", "multiplicador_recuperacion"
            ]].drop_duplicates().rename(columns={
                "escenario": "Escenario",
                "multiplicador_perdida_bruta": "Multiplicador de pérdida bruta",
                "multiplicador_recuperacion": "Multiplicador de recuperación",
            }).sort_values("Escenario")
            """,
            titulo_colab="Preparar definición de escenarios",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_escenarios,
                "Tabla 12. Multiplicadores físicos de los escenarios 2026–2035",
                "Los multiplicadores se aplican a los flujos base observados. Son supuestos comparativos, no pronósticos probabilísticos.",
                "Supuestos y cálculos del autor.",
                decimales=2,
                max_filas=None,
                archivo="tabla_12_definicion_escenarios.csv",
            )
            """,
            titulo_colab="Mostrar Tabla 12",
            resultado=True,
        ),
        _codigo(
            """
            trayectorias = productos["trayectorias_fisicas"].copy()
            trayectorias["Acumulado central (ha)"] = (
                trayectorias["acumulado_inferior_ha"] + trayectorias["acumulado_superior_ha"]
            ) / 2
            fig_trayectorias = px.line(
                trayectorias,
                x="anio", y="Acumulado central (ha)", color="regla", line_dash="regla",
                symbol="regla", markers=True, facet_col="escenario",
                facet_col_spacing=0.045,
                labels={"anio": "Año", "regla": "Resultado forestal", "escenario": "Escenario"},
                color_discrete_map={
                    "Deforestación bruta": "#D55E00",
                    "Saldo ponderado por recuperación": "#6A3D9A",
                    "Pérdida neta institucional": "#0072B2",
                },
                line_dash_map={
                    "Deforestación bruta": "solid",
                    "Saldo ponderado por recuperación": "dash",
                    "Pérdida neta institucional": "dot",
                },
                symbol_map={
                    "Deforestación bruta": "circle",
                    "Saldo ponderado por recuperación": "diamond",
                    "Pérdida neta institucional": "square",
                },
            )
            fig_trayectorias.update_traces(line_width=3, marker_size=7)
            fig_trayectorias.update_xaxes(title=None)
            fig_trayectorias.update_yaxes(matches="y", title=None, tickformat=",")
            fig_trayectorias.update_yaxes(title_text="ha acumuladas", row=1, col=1)
            fig_trayectorias.update_layout(legend_title_text="Resultado forestal")
            fig_trayectorias.for_each_annotation(
                lambda a: a.update(text=a.text.split("=")[-1].replace(
                    "Deterioro proporcional acelerado", "Deterioro proporcional<br>acelerado"
                ))
            )
            fig_trayectorias.add_annotation(
                text="Año", x=0.5, y=0, xref="paper", yref="paper", yshift=-44,
                showarrow=False, font=dict(size=12, color="#24363D"),
            )
            """,
            titulo_colab="Construir Figura 7",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_trayectorias,
                "Figura 13. Trayectorias físicas acumuladas bajo tres escenarios proporcionales",
                "Se grafica el punto medio del intervalo ponderado. Los paneles comparten escala vertical y los resultados se distinguen por color, trazo y marcador.",
                FUENTE_ESCENARIOS,
                alto=740,
            )
            """,
            titulo_colab="Mostrar Figura 7",
            resultado=True,
        ),
        _codigo(
            """
            trayectorias_monetarias = productos["trayectorias_monetarias"].copy()
            trayectorias_monetarias["VP central (Q miles de millones)"] = (
                trayectorias_monetarias["vp_acumulado_inferior_gtq"]
                + trayectorias_monetarias["vp_acumulado_superior_gtq"]
            ) / 2e9
            fig_trayectorias_monetarias = px.line(
                trayectorias_monetarias,
                x="anio", y="VP central (Q miles de millones)", color="regla", line_dash="regla",
                symbol="regla", markers=True, facet_col="escenario",
                facet_col_spacing=0.045,
                labels={"anio": "Año", "regla": "Resultado forestal", "escenario": "Escenario"},
                color_discrete_map={
                    "Deforestación bruta": "#D55E00",
                    "Saldo ponderado por recuperación": "#6A3D9A",
                    "Pérdida neta institucional": "#0072B2",
                },
                line_dash_map={
                    "Deforestación bruta": "solid",
                    "Saldo ponderado por recuperación": "dash",
                    "Pérdida neta institucional": "dot",
                },
                symbol_map={
                    "Deforestación bruta": "circle",
                    "Saldo ponderado por recuperación": "diamond",
                    "Pérdida neta institucional": "square",
                },
            )
            fig_trayectorias_monetarias.update_traces(line_width=3, marker_size=7)
            fig_trayectorias_monetarias.update_xaxes(title=None)
            fig_trayectorias_monetarias.update_yaxes(
                matches="y", title=None, tickformat=",.1f"
            )
            fig_trayectorias_monetarias.update_yaxes(
                title_text="Q miles de millones, valor presente", row=1, col=1
            )
            fig_trayectorias_monetarias.update_layout(legend_title_text="Resultado forestal")
            fig_trayectorias_monetarias.for_each_annotation(
                lambda a: a.update(text=a.text.split("=")[-1].replace(
                    "Deterioro proporcional acelerado", "Deterioro proporcional<br>acelerado"
                ))
            )
            fig_trayectorias_monetarias.add_annotation(
                text="Año", x=0.5, y=0, xref="paper", yref="paper", yshift=-44,
                showarrow=False, font=dict(size=12, color="#24363D"),
            )
            """,
            titulo_colab="Construir Figura 8",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_trayectorias_monetarias,
                "Figura 14. Trayectorias del valor presente acumulado bajo tres escenarios",
                "Punto medio del intervalo, Q de 2026, tasa de 4% y 25 años de servicios por cohorte. Los paneles comparten escala y los resultados se distinguen por color, trazo y marcador.",
                FUENTE_VALORACION,
                alto=740,
            )
            """,
            titulo_colab="Mostrar Figura 8",
            resultado=True,
        ),
        _codigo(
            """
            escenarios_val = productos["escenarios_valorados"].copy()
            escenarios_val["Resultado físico, década (ha)"] = escenarios_val.apply(
                lambda f: (
                    f"{f.resultado_inferior_decada_ha:,.0f}"
                    if np.isclose(f.resultado_inferior_decada_ha, f.resultado_superior_decada_ha)
                    else f"{f.resultado_inferior_decada_ha:,.0f}–{f.resultado_superior_decada_ha:,.0f}"
                ), axis=1
            )
            escenarios_val["VP, década (Q millones)"] = escenarios_val.apply(
                lambda f: (
                    f"{f.vp_decada_inferior_gtq / 1e6:,.1f}"
                    if np.isclose(f.vp_decada_inferior_gtq, f.vp_decada_superior_gtq)
                    else f"{f.vp_decada_inferior_gtq / 1e6:,.1f}–{f.vp_decada_superior_gtq / 1e6:,.1f}"
                ), axis=1
            )
            tabla_escenarios_val = escenarios_val[[
                "escenario", "regla", "Resultado físico, década (ha)", "VP, década (Q millones)"
            ]].rename(columns={"escenario": "Escenario", "regla": "Resultado forestal"}).sort_values(["Escenario", "Resultado forestal"])
            """,
            titulo_colab="Preparar valoración de escenarios",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_escenarios_val,
                "Tabla 13. Resultados físicos y valoración indicativa de los escenarios",
                "Valor presente de diez cohortes anuales, Q de 2026, tasa de 4% y 25 años de servicios por cohorte. Los resultados son alternativos y no se suman.",
                FUENTE_VALORACION,
                decimales=1,
                max_filas=None,
                archivo="tabla_13_escenarios_valorados.csv",
                descarga=escenarios_val,
            )
            """,
            titulo_colab="Mostrar Tabla 13",
            resultado=True,
        ),
        _texto(
            r"""
            ## 7. Manglar: aproximación local con evidencia estructural

            El módulo local parte de 55 trayectorias multitemporales de estructura de manglar
            disponibles en el portal de INAB: 30 favorables, 21 desfavorables y 4 mixtas. De ahí
            se deriva $\omega_M$, el *ponderador estructural local de manglar*:

            $$\underline{\omega}_M=\frac{n_F}{n}=\frac{30}{55}=0.5455,$$

            $$\overline{\omega}_M=\frac{n_F+n_M}{n}=\frac{34}{55}=0.6182.$$

            El límite inferior cuenta solo trayectorias con aumento conjunto de carbono y área
            basal; el superior incorpora las cuatro trayectorias mixtas. No es un intervalo de
            confianza. Las 55 series representan 73.3 % de los 75 registros de parcela contenidos
            en el archivo analítico; esa cobertura se documenta y no se usa como multiplicador.

            Para cada municipio, la aplicación se define como

            $$H_{i,M}(\omega_M)=B_i-\omega_MR_i,$$

            $$\underline H_{i,M}=B_i-\overline{\omega}_MR_i,\qquad
            \overline H_{i,M}=B_i-\underline{\omega}_MR_i.$$

            La inversión de los extremos se debe a que $\partial H_{i,M}/\partial\omega_M=-R_i$.
            Con la tolerancia numérica $\varepsilon=10^{-8}$ utilizada por el código, la
            clasificación es pérdida si $\underline H_{i,M}>\varepsilon$, ganancia si
            $\overline H_{i,M}<-\varepsilon$ e indeterminada en otro caso. Además,

            $$H_{i,M}(\omega_M)-N_i=(1-\omega_M)R_i.$$

            $B_i$ y $R_i$ siguen siendo la pérdida y la ganancia de cobertura forestal del
            municipio completo, no cambios exclusivos de manglar. La evidencia de campo informa
            únicamente el ponderador local. Los resultados se comparan con el cálculo neto y,
            donde existe soporte común, con la recuperación ponderada a veinte años; no se suman
            entre sí (INAB et al., 2016; INAB, 2023; Poorter et al., 2016, 2017).
            """
        ),
        _codigo(
            """
            intervalo_local = productos["intervalo_estructural_local"].copy().rename(columns={
                "series_multitemporales": "Series multitemporales",
                "trayectorias_favorables": "Favorables",
                "trayectorias_desfavorables": "Desfavorables",
                "trayectorias_mixtas": "Mixtas",
                "proporcion_estructural_min": "Proporción estructural mínima",
                "proporcion_estructural_max": "Proporción estructural máxima",
            })
            intervalo_local_visible = pd.DataFrame({
                "Series": intervalo_local["Series multitemporales"],
                "Trayectorias (F/D/M)": intervalo_local.apply(
                    lambda f: f"{int(f.Favorables)} / {int(f.Desfavorables)} / {int(f.Mixtas)}", axis=1
                ),
                "Proporción mínima": intervalo_local["Proporción estructural mínima"],
                "Proporción máxima": intervalo_local["Proporción estructural máxima"],
            })
            """,
            titulo_colab="Preparar evidencia estructural local",
        ),
        _codigo(
            """
            mostrar_tabla(
                intervalo_local_visible,
                "Tabla 14. Derivación del intervalo estructural local de manglar",
                "El límite inferior cuenta solo trayectorias favorables; el superior incorpora las cuatro mixtas. No es una proporción nacional de recuperación de manglar.",
                "INAB (2023a) e INAB et al. (2016); cálculos del autor.",
                decimales=3,
                max_filas=None,
                archivo="tabla_14_intervalo_estructural_mangle.csv",
                descarga=productos["intervalo_estructural_local"],
            )
            """,
            titulo_colab="Mostrar Tabla 14",
            resultado=True,
        ),
        _codigo(
            """
            evidencia_mangle = productos["evidencia_estructural_mangle"].copy()
            evidencia_mangle["Total"] = evidencia_mangle["series_multitemporales"]
            orden_mangle = evidencia_mangle.sort_values(["Total", "municipio"])["municipio"].tolist()
            categorias_mangle = [
                ("Aumento conjunto", "suben_carbono_y_area_basal", "#009E73"),
                ("Disminución conjunta", "bajan_carbono_y_area_basal", "#D55E00"),
                ("Mixta", "trayectoria_mixta", "#6A3D9A"),
            ]
            fig_evidencia_mangle = go.Figure()
            for etiqueta, columna, color in categorias_mangle:
                valores = evidencia_mangle[columna]
                fig_evidencia_mangle.add_trace(go.Bar(
                    x=valores,
                    y=evidencia_mangle["municipio"],
                    orientation="h",
                    name=etiqueta,
                    marker_color=color,
                    text=[str(int(v)) if v > 0 else "" for v in valores],
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate="%{y}<br>%{fullData.name}: %{x:.0f}<extra></extra>",
                ))
            fig_evidencia_mangle.update_layout(
                barmode="stack", legend_title_text="Trayectoria estructural",
                margin=dict(l=210, r=60),
            )
            fig_evidencia_mangle.update_xaxes(
                title="Número de series multitemporales", range=[0, 17.5], dtick=2
            )
            fig_evidencia_mangle.update_yaxes(
                title=None, categoryorder="array", categoryarray=orden_mangle
            )
            fig_evidencia_mangle.add_annotation(
                x=0.25, y="Nueva Concepción", text="0", showarrow=False,
                xanchor="left", font=dict(color="#5C6F77", size=11),
            )
            """,
            titulo_colab="Construir Figura 15",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_evidencia_mangle,
                "Figura 15. Distribución municipal de las series estructurales de manglar",
                "Las categorías describen el cambio conjunto de carbono y área basal en las series multitemporales. Nueva Concepción tiene cinco registros de parcela, pero ninguna serie multitemporal disponible; el ponderador utiliza las 55 series clasificadas.",
                "INAB (2023a), Áreas potenciales de restauración de manglares; cálculos del autor.",
                alto=680,
            )
            """,
            titulo_colab="Mostrar Figura 15",
            resultado=True,
        ),
        _codigo(
            """
            resumen_local = productos["resumen_mangle_local"].iloc[0]
            tabla_resumen_local = pd.DataFrame({
                "Magnitud": [
                    "Municipios", "Pérdida bruta", "Ganancia de cobertura",
                    "Pérdida neta", "Saldo con ponderador estructural",
                ],
                "Resultado": [
                    f"{int(resumen_local.municipios)}",
                    f"{resumen_local.perdida_bruta_ha:,.1f} ha",
                    f"{resumen_local.recuperacion_bruta_ha:,.1f} ha",
                    f"{resumen_local.perdida_neta_ha:,.1f} ha",
                    f"{resumen_local.saldo_estructural_inferior_ha:,.1f}–{resumen_local.saldo_estructural_superior_ha:,.1f} ha",
                ],
                "Lectura": ["Ámbito local", "B", "R", "N = B − R", "H_M"],
            })
            """,
            titulo_colab="Preparar resumen local de manglar",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_resumen_local,
                "Tabla 15. Resultados agregados en trece municipios con evidencia de manglar",
                "La pérdida y recuperación proceden de la base municipal general; la evidencia de campo sustenta únicamente la ponderación estructural local.",
                FUENTE_MANGLE,
                decimales=1,
                max_filas=None,
                archivo="tabla_15_resumen_local_mangle.csv",
                descarga=productos["resumen_mangle_local"],
            )
            """,
            titulo_colab="Mostrar Tabla 15",
            resultado=True,
        ),
        _codigo(
            """
            local_comp = productos["comparacion_local_poorter_mangle"].copy()
            graf_local = local_comp[[
                "municipio", "perdida_neta_ha",
                "saldo_estructural_inferior_ha", "saldo_estructural_superior_ha",
                "saldo_ponderado_inferior_ha", "saldo_ponderado_superior_ha"
            ]].sort_values("saldo_estructural_superior_ha")
            fig_local = go.Figure()
            fig_local.add_trace(go.Scatter(
                x=graf_local["perdida_neta_ha"], y=graf_local["municipio"],
                mode="markers", name="Pérdida neta", marker=dict(color="#0072B2", size=9, symbol="square"),
                hovertemplate="%{y}<br>Pérdida neta: %{x:,.1f} ha<extra></extra>",
            ))
            for etiqueta, inferior, superior, color, simbolo in [
                ("Aproximación estructural local", "saldo_estructural_inferior_ha", "saldo_estructural_superior_ha", "#009E73", "diamond"),
                ("Saldo ponderado con ρ₂₀", "saldo_ponderado_inferior_ha", "saldo_ponderado_superior_ha", "#E69F00", "circle"),
            ]:
                centro = (graf_local[inferior] + graf_local[superior]) / 2
                fig_local.add_trace(go.Scatter(
                    x=centro, y=graf_local["municipio"], mode="markers", name=etiqueta,
                    marker=dict(color=color, size=9, symbol=simbolo),
                    error_x=dict(type="data", array=graf_local[superior]-centro, arrayminus=centro-graf_local[inferior]),
                    hovertemplate="%{y}<br>%{x:,.1f} ha<extra></extra>",
                ))
            fig_local.update_xaxes(title="Resultado (ha); pérdida positiva", zeroline=True, tickformat=",")
            fig_local.update_yaxes(title=None)
            """,
            titulo_colab="Construir Figura 9",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_local,
                "Figura 16. Resultados locales en municipios con evidencia de manglar",
                "Los puntos e intervalos son resultados alternativos de la misma pérdida y ganancia de cobertura municipal. La aplicación estructural local y la recuperación ponderada a veinte años no se agregan entre sí.",
                "INAB y CONAP (2023), INAB (2023a) y Poorter et al. (2016, 2017); cálculos del autor.",
                alto=760,
            )
            """,
            titulo_colab="Mostrar Figura 9",
            resultado=True,
        ),
        _codigo(
            """
            tabla_local = local_comp[[
                "depto", "municipio", "perdida_neta_ha"
            ]].copy()
            tabla_local["Intervalo estructural (ha)"] = local_comp.apply(
                lambda f: f"{f.saldo_estructural_inferior_ha:,.1f}–{f.saldo_estructural_superior_ha:,.1f}", axis=1
            )
            tabla_local["Saldo ponderado con ρ₂₀ (ha)"] = local_comp.apply(
                lambda f: f"{f.saldo_ponderado_inferior_ha:,.1f}–{f.saldo_ponderado_superior_ha:,.1f}", axis=1
            )
            tabla_local = tabla_local.rename(columns={
                "depto": "Departamento", "municipio": "Municipio",
                "perdida_neta_ha": "Pérdida neta (ha)",
            }).sort_values(["Departamento", "Municipio"])
            """,
            titulo_colab="Preparar resultados municipales de manglar",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_local,
                "Tabla 16. Comparación municipal de la aproximación estructural local",
                "Los trece municipios tienen soporte común para la comparación. Los intervalos estructural y de recuperación ponderada responden a fundamentos distintos y no son componentes aditivos.",
                "INAB y CONAP (2023), INAB (2023a) y Poorter et al. (2016, 2017); cálculos del autor.",
                decimales=1,
                max_filas=None,
                archivo="tabla_16_comparacion_local_mangle.csv",
                descarga=local_comp,
            )
            """,
            titulo_colab="Mostrar Tabla 16",
            resultado=True,
        ),
        _texto(
            """
            ## 8. Recuadro de desastres y degradación: contexto no aditivo

            Los costos reportados para degradación de suelos y para las tormentas Eta e Iota
            ayudan a dimensionar el entorno económico de la pérdida de capital natural. No se
            atribuyen causalmente a la deforestación de este ejercicio y no se suman a la
            valoración forestal: hacerlo produciría doble conteo y una precisión inexistente
            (Castañeda Sánchez et al., 2019; CEPAL, 2021).
            """
        ),
        _codigo(
            """
            costos = productos["costos_contextuales_no_aditivos"].copy().rename(columns={
                "dimension": "Dimensión",
                "indicador_fuente": "Indicador",
                "equivalencia_indicativa_2026_gtq_millones": "Equivalencia 2026 (Q millones)",
                "fuente": "Fuente original",
                "uso_analitico": "Uso analítico",
            })
            costos_visibles = costos[["Dimensión", "Indicador", "Equivalencia 2026 (Q millones)"]]
            """,
            titulo_colab="Preparar costos contextuales",
        ),
        _codigo(
            """
            mostrar_tabla(
                costos_visibles,
                "Recuadro 1. Costos ambientales y de desastres presentados como contexto",
                "Las equivalencias a 2026 son indicativas. No se establece causalidad con la pérdida forestal ni se agregan estos montos a la valoración de servicios ecosistémicos.",
                "Castañeda Sánchez et al. (2019), CEPAL (2021) y Banco de Guatemala (s. f.); cálculos del autor.",
                decimales=0,
                max_filas=None,
                archivo="recuadro_01_costos_contextuales_no_aditivos.csv",
                descarga=costos,
            )
            """,
            titulo_colab="Mostrar Recuadro 1",
            resultado=True,
        ),
        _texto(
            """
            ## Descargas

            El paquete integral reúne las tablas completas, el manifiesto de archivos, los
            metadatos de ejecución y las instrucciones de citación. Los controles de consistencia
            se ejecutan en el proceso reproducible y permanecen disponibles en el repositorio,
            sin ocupar un apartado de resultados en el cuaderno.
            """
        ),
        _codigo(
            """
            archivos_descarga = [
                productos["zip"],
                repo / "outputs" / "downloads" / "manifiesto_resultados.csv",
                repo / "outputs" / "downloads" / "metadatos_ejecucion.json",
                productos["como_citar"],
            ]
            panel_descargas(
                archivos_descarga,
                titulo="Descargas reproducibles: tablas, manifiesto y metadatos",
            )
            """,
            titulo_colab="Mostrar panel de descargas",
        ),
        _texto(
            """
            ## Conclusión

            La comparación muestra que la pérdida neta puede disminuir mientras la pérdida bruta
            permanece elevada, porque el cálculo institucional descuenta la recuperación de forma
            completa dentro del mismo período. Incluso al conceder un horizonte de veinte años,
            el saldo ponderado conserva una pérdida mayor que el resultado neto. La aproximación
            cuantitativa no sustituye una medición ecológica longitudinal; muestra qué puede
            establecerse al vincular fuentes disponibles y qué preguntas requieren investigación
            adicional.
            """
        ),
        _texto(
            """
            ## Referencias

            Banco de Guatemala. (s. f.). *Producto interno bruto total, año de referencia 2013:
            Años 2013–2026* [Cuadro estadístico]. Recuperado el 26 de agosto de 2026, de
            https://banguat.gob.gt/sites/default/files/banguat/cuentasnac/PIB2013/resumidos/1.1_PIB_Tasa_de_Variacion_AR2013.pdf

            Banco Mundial, Gobierno de Guatemala, Alianza Mundial para la Contabilidad de la
            Riqueza y la Valoración de los Servicios de los Ecosistemas, & Universidad Rafael
            Landívar, Vicerrectoría de Investigación y Proyección. (2021). *Cuenta de ecosistemas
            de Guatemala* (2.ª ed.). Universidad Rafael Landívar. https://documents.worldbank.org/en/publication/documents-reports/documentdetail/451591561110110128

            Castañeda Sánchez, J. P., Carrera, J., & Rexhepi, D. (2019). *Towards natural capital
            accounting in Guatemala: Synthesis report*. World Bank. https://documents1.worldbank.org/curated/en/332151561104488571/pdf/Towards-Natural-Capital-Accounting-in-Guatemala-Synthesis-Report.pdf

            Comisión Económica para América Latina y el Caribe. (2021). *Evaluación de los
            efectos e impactos de las depresiones tropicales Eta y Iota en Guatemala*
            (LC/TS.2021/21). https://www.cepal.org/es/publicaciones/46681-evaluacion-efectos-impactos-depresiones-tropicales-eta-iota-guatemala

            Instituto Nacional de Bosques. (2023a). *Áreas potenciales de restauración de
            manglares* [Portal de información de campo]. https://sig.inab.gob.gt/portal/apps/storymaps/stories/955793375059405ab4964bb40813b9fd

            Instituto Nacional de Bosques. (2023b). *Dinámica de la cobertura forestal
            2016–2020: Tabla municipal* [Capa ArcGIS]. https://sig.inab.gob.gt/portal/home/item.html?id=a15d600e7aed41d8b2afdcdcefad32db&sublayer=5

            Instituto Nacional de Bosques, & Consejo Nacional de Áreas Protegidas. (2023).
            *Estudio de la cobertura forestal para el año 2020 y dinámica de la cobertura
            forestal en el período 2016–2020: República de Guatemala* [Informe técnico].
            https://sig.inab.gob.gt/portal/apps/storymaps/stories/eac535d7b61a47f7b12a9b81eb9c15b6

            Instituto Nacional de Bosques, Instituto Privado de Investigación sobre Cambio
            Climático, & Consejo Nacional de Áreas Protegidas. (2016). *Metodología para el
            establecimiento y mantenimiento de parcelas permanentes de medición forestal (PPMF)
            en bosque natural del ecosistema manglar*. https://icc.org.gt/wp-content/uploads/2023/03/094.pdf

            Naciones Unidas, Comisión Europea, Organización de las Naciones Unidas para la
            Alimentación y la Agricultura, Fondo Monetario Internacional, Organización para la
            Cooperación y el Desarrollo Económicos, & Banco Mundial. (2021). *Sistema de
            Contabilidad Ambiental y Económica—Contabilidad de los Ecosistemas (SCAE-CE)*.
            https://seea.un.org/content/system-environmental-economic-accounting-ecosystem-accounting-white-cover-version

            Poorter, L., Bongers, F., Aide, T. M., Almeyda Zambrano, A. M., Balvanera, P.,
            Becknell, J. M., Boukili, V., Brancalion, P. H. S., Broadbent, E. N., Chazdon, R. L.,
            Craven, D., de Almeida-Cortez, J. S., Cabral, G. A. L., de Jong, B. H. J., Denslow,
            J. S., Dent, D. H., DeWalt, S. J., Dupuy, J. M., Durán, S. M., ... Rozendaal, D. M. A.
            (2016). Biomass resilience of Neotropical secondary forests. *Nature, 530*, 211–214.
            https://doi.org/10.1038/nature16512

            Poorter, L., Bongers, F., Aide, T. M., Almeyda Zambrano, A. M., Balvanera, P.,
            Becknell, J. M., Boukili, V., Brancalion, P. H. S., Broadbent, E. N., Chazdon, R. L.,
            Craven, D., de Almeida-Cortez, J. S., Cabral, G. A. L., de Jong, B. H. J., Denslow,
            J. S., Dent, D. H., DeWalt, S. J., Dupuy, J. M., Durán, S. M., ... Rozendaal, D. M. A.
            (2017). *Data from: Biomass resilience of Neotropical secondary forests* [Data set].
            Dryad. https://doi.org/10.5061/dryad.82vr4

            Sandoval García, C. A., Gálvez Ruano, J. J., & Pinillos Cifuentes, D. A. (2022).
            *Bosques*. Universidad Rafael Landívar, Editorial Cara Parens. https://biblior.url.edu.gt/wp-content/uploads/publichlg/IARNA/serie_ambi/978-9929-54-422-2.pdf
            """
        ),
        _texto(
            """
            ## Cómo citar

            > Osorio, J. A. (2026). *Deforestación bruta, recuperación y saldo forestal
            > ponderado en Guatemala* (Versión 1.0.0) [Cuaderno reproducible]. Instituto de
            > Investigación en Ciencias Naturales y Tecnología, Universidad Rafael Landívar.
            > https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/releases/tag/v1.0.0

            Esta referencia identifica la versión pública 1.0.0. Cada figura y tabla está
            acompañada por la atribución de sus fuentes primarias.
            """
        ),
    ]

    celdas = _fusionar_calculo_y_resultado(celdas)
    celdas = _incorporar_comentarios(celdas)

    for indice, celda in enumerate(celdas):
        celda["id"] = f"sf-{indice:03d}"

    cuaderno = nbf.v4.new_notebook(
        cells=celdas,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
                "mimetype": "text/x-python",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "pygments_lexer": "ipython3",
                "nbconvert_exporter": "python",
                "file_extension": ".py",
            },
            "colab": {
                "name": DESTINO.name,
                "provenance": [],
                "toc_visible": True,
            },
            "authors": [
                {
                    "name": "Juan Alejandro Osorio",
                    "affiliation": "IARNA, Universidad Rafael Landívar",
                },
            ],
            "title": "Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala",
        },
    )
    return cuaderno


def ejecutar_cuaderno(cuaderno):
    """Ejecuta las celdas en proceso y guarda una sola salida por resultado.

    El constructor evita depender de un servidor Jupyter para poder funcionar también
    en entornos de publicación restringidos. El cuaderno conserva código Python normal
    y puede volver a ejecutarse de forma convencional en Colab o Jupyter.
    """

    espacio = {"__name__": "__notebook__"}
    contador = 0
    directorio_original = Path.cwd()
    os.chdir(REPO)
    try:
        for indice, celda in enumerate(cuaderno.cells):
            if celda.cell_type != "code":
                continue

            contador += 1
            capturas = []

            def capturar(objeto=None, **_):
                capturas.append(objeto)

            if "productos" in espacio:
                espacio["display"] = capturar
                import saldo_forestal.visualizacion as visualizacion

                visualizacion.display = capturar

            try:
                exec(compile(celda.source, f"<celda {indice}>", "exec"), espacio)
            except Exception as exc:  # pragma: no cover - mensaje editorial para el constructor
                raise RuntimeError(f"Falló la ejecución de la celda {indice}: {exc}") from exc

            if "productos" in espacio:
                espacio["display"] = capturar
                import saldo_forestal.visualizacion as visualizacion

                visualizacion.display = capturar

            celda.execution_count = contador
            celda.outputs = []
            coincidencia_titulo = re.search(
                r'"((?:Tabla|Figura|Recuadro)\s+\d+\.[^"]+)"', celda.source
            )
            texto_plano = (
                coincidencia_titulo.group(1)
                if coincidencia_titulo
                else "Resultado HTML reproducible"
            )
            for objeto in capturas:
                html = getattr(objeto, "data", None)
                if html is None and hasattr(objeto, "_repr_html_"):
                    html = objeto._repr_html_()
                if html is None:
                    html = str(objeto)
                celda.outputs.append(
                    nbf.v4.new_output(
                        "display_data",
                        data={"text/html": str(html), "text/plain": texto_plano},
                        metadata={},
                    )
                )

            if "result" in celda.metadata.get("tags", []) and len(celda.outputs) != 1:
                raise RuntimeError(
                    f"La celda de resultado {indice} produjo {len(celda.outputs)} salidas; se esperaba una."
                )
    finally:
        os.chdir(directorio_original)

    return cuaderno


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    cuaderno = ejecutar_cuaderno(construir_cuaderno())
    nbf.write(cuaderno, DESTINO)
    if DESTINO_ANTERIOR.exists() and DESTINO_ANTERIOR != DESTINO:
        DESTINO_ANTERIOR.unlink()
    resultados = sum("result" in c.metadata.get("tags", []) for c in cuaderno.cells)
    print(
        f"Cuaderno construido y ejecutado: {DESTINO.relative_to(REPO)} "
        f"({len(cuaderno.cells)} celdas; {resultados} resultados)"
    )


if __name__ == "__main__":
    main()
