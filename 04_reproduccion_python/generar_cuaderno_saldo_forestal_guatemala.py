"""Construye el cuaderno público y reproducible del saldo forestal.

Después de la configuración, cada celda de código reúne cálculo y presentación
de un único resultado. Así se conserva la trazabilidad sin duplicar espacios de
código en Colab o Jupyter.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
from textwrap import dedent

import nbformat as nbf


REPO = Path(__file__).resolve().parents[1]
DESTINO = (
    REPO
    / "04_reproduccion_python"
    / "cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb"
)


FUENTES_APARATO = {
    "FUENTE_INAB": "INAB y CONAP (2023) e INAB (2023b); cálculos del autor.",
    "FUENTE_RECUPERACION": (
        "INAB y CONAP (2023), INAB (2023b) y Poorter et al. (2016, 2017); cálculos del autor."
    ),
    "FUENTE_VALORACION": (
        "Banco Mundial et al. (2021) y Banco de Guatemala (s. f.); cálculos del autor."
    ),
    "FUENTE_MANGLAR": (
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
        "mientras la pérdida neta disminuye. Las dos series describen magnitudes distintas y "
        "se presentan por separado."
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
        "Las cinco listas reúnen 172 municipios y vinculan cada grupo con sitios científicos de "
        "referencia y un intervalo de regeneración equivalente. Los otros 168 municipios no "
        "reciben una proporción y conservan la pérdida neta reportada por INAB y CONAP."
    ),
    "Figura 5": (
        "La figura distingue los límites aplicados, su punto medio aritmético y los valores "
        "publicados por sitio. La amplitud de cada segmento se traslada al intervalo del saldo "
        "ponderado y no representa error muestral."
    ),
    "Tabla 5": (
        "Dentro de los 172 municipios elegibles, el saldo ponderado asciende a "
        "99,593–107,108 ha, frente a 35,857 ha bajo el cálculo neto reportado."
    ),
    "Tabla 6": (
        "El efecto de la ponderación difiere por departamento porque cambian tanto la recuperación "
        "observada como la proporción de cada grupo territorial asignada a sus municipios."
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
        "El 15.1 % de los municipios del dominio cambia de clasificación. La transición se concentra "
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
        "a 2.35 veces la pérdida neta reportada. El total reúne 172 municipios ponderados, "
        "168 municipios sin proporción asignada y dos unidades lacustres no municipales."
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
        "aplicación local e indeterminado con la proporción de regeneración equivalente."
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
    """Resuelve la fuente de una llamada sin autocitar el producto reproducible."""

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
            """
            <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;max-width:960px;padding:28px 0 34px;border-top:4px solid #146c7a;border-bottom:1px solid #dfe6e9">
              <div style="color:#146c7a;font-size:12px;font-weight:700;letter-spacing:.09em;text-transform:uppercase">Material suplementario en línea</div>
              <h1 style="color:#18242a;font-size:36px;line-height:1.16;letter-spacing:-.025em;font-weight:650;margin:15px 0 17px">Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala</h1>
              <div style="color:#58666d;font-size:16px;line-height:1.55;max-width:850px">Reproducción de los datos, parámetros, operaciones y resultados nacionales y municipales para 2016–2020.</div>
              <div style="margin-top:26px;color:#334148;font-size:14px"><em>Autor:</em> Juan Alejandro Osorio · IARNA, Universidad Rafael Landívar</div>
            </div>
            """,
            etiquetas=("remove-input",),
        ),
        _texto(
            """
            Este cuaderno es el material suplementario en línea del análisis forestal. Su función
            es reproducir la secuencia de datos, parámetros, operaciones y resultados a partir de
            la dinámica de cobertura forestal 2016–2020 reportada por INAB y CONAP (2023).

            El contenido se organiza en ocho componentes: antecedente nacional, reproducción del
            balance reportado, asignación territorial de la proporción de regeneración equivalente,
            completación nacional, valoración indicativa, trayectorias, aplicación local de manglar
            y contexto económico no aditivo. El anexo reúne las fórmulas completas.

            Salvo indicación expresa, las cifras son acumuladas para 2016–2020. Un resultado
            positivo representa pérdida y uno negativo, ganancia de cobertura. El código está
            oculto de inicio, pero puede desplegarse. Cada tabla ofrece el CSV completo y cada
            salida está acompañada por su nota, fuente y lectura numérica.

            > *Alcance.* La cobertura de origen es reportada por INAB y CONAP. La ponderación, la completación
            > nacional, la valoración y las trayectorias son cálculos analíticos. La aplicación
            > de manglar es local y no se suma al resultado nacional.
            """
        ),
        _codigo(
            r"""
            from pathlib import Path
            import subprocess
            import sys
            from textwrap import wrap

            candidatos = [Path.cwd(), Path.cwd().parent, Path.cwd() / "saldo-forestal-ponderado-guatemala"]
            repo = next((
                p.resolve()
                for p in candidatos
                if (p / "04_reproduccion_python" / "src" / "saldo_forestal").is_dir()
            ), None)
            if repo is None:
                destino_repo = Path.cwd() / "saldo-forestal-ponderado-guatemala"
                subprocess.run(
                    [
                        "git", "clone", "--depth", "1", "--branch", "main",
                        "https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git",
                        str(destino_repo),
                    ],
                    check=True,
                )
                repo = destino_repo.resolve()
            sys.path.insert(0, str(repo / "04_reproduccion_python" / "src"))

            import numpy as np
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            from IPython.display import HTML, display

            from saldo_forestal.reproduccion import ejecutar_reproduccion
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

            productos = ejecutar_reproduccion(repo_dir=repo)
            FUENTE_INAB = "INAB y CONAP (2023) e INAB (2023b); cálculos del autor."
            FUENTE_RECUPERACION = "INAB y CONAP (2023), INAB (2023b) y Poorter et al. (2016, 2017); cálculos del autor."
            FUENTE_VALORACION = "Banco Mundial et al. (2021) y Banco de Guatemala (s. f.); cálculos del autor."
            FUENTE_MANGLAR = "INAB (2023a), INAB et al. (2016), e INAB y CONAP (2023); cálculos del autor."
            FUENTE_ESCENARIOS = "INAB y CONAP (2023) e INAB (2023b); supuestos y cálculos del autor."
            """,
            titulo_colab="Preparar entorno y reconstruir resultados",
        ),
        _texto(
            r"""
            ## 1. Antecedente nacional de pérdida bruta y pérdida neta

            La publicación *Bosques* reúne las estimaciones nacionales disponibles desde 1991.
            Entre los intervalos 1991–2001 y 2010–2016, la pérdida bruta anual aumentó
            aproximadamente 32 %, mientras
            la pérdida neta anual disminuyó cerca de 75 % (Sandoval García et al., 2022).

            *El año 1991 aparece porque inicia el primer intervalo recopilado por esa fuente.* No
            amplía el período municipal ni entra en los cálculos de 2016–2020. Los intervalos
            tienen duraciones y métodos de medición propios; la figura es un antecedente
            comparativo y no una serie anual continua.
            """
        ),
        _codigo(
            """
            historica = productos["serie_historica"].copy()
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
            ## 2. Reproducción del balance reportado por INAB y CONAP, 2016–2020

            Guatemala tenía 340 municipios durante el período analizado. La tabla territorial de
            INAB y CONAP (2023), con detalle municipal en INAB (2023b), contiene 342 registros
            porque añade el Lago de Amatitlán y el Lago de Atitlán como unidades de reporte sin
            código municipal. Para cada registro se distinguen tres magnitudes:

            | Símbolo | Nombre | Qué representa | Unidad |
            |---|---|---|---|
            | $B_i$ | Pérdida bruta | Cobertura registrada como pérdida en la unidad $i$ | ha |
            | $R_i$ | Ganancia de cobertura | Cobertura registrada como recuperación en la fuente | ha |
            | $N_i$ | Pérdida neta reportada | Diferencia entre las dos magnitudes anteriores | ha |

            INAB y CONAP obtienen la pérdida neta al restar toda la ganancia de cobertura de la
            pérdida bruta:

            $$N_i=B_i-R_i.$$

            Si una unidad registra 100 ha de pérdida y 60 ha de ganancia, su pérdida neta es
            40 ha. Si la ganancia supera la pérdida, el resultado es negativo y se lee como
            ganancia neta. La variable $R_i$ no informa la edad, la biomasa, el origen ni la
            permanencia de la nueva cobertura.

            El total nacional acumulado del período es 244,395 ha de pérdida bruta, 191,658 ha
            de recuperación y 52,736 ha de pérdida neta. Esta sección muestra primero el
            resultado reportado en sus propios términos y establece el punto de comparación
            para la ponderación de la recuperación.
            """
        ),
        _codigo(
            """
            nacional = productos["resultados_reportados_inab_conap_nacionales"].iloc[0]
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
            titulo_colab="Preparar resultado nacional reportado por INAB y CONAP",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_nacional,
                "Tabla 1. Balance nacional reportado por INAB y CONAP",
                "La recuperación se descuenta en proporción uno a uno; las cifras acumuladas corresponden a 2016–2020.",
                FUENTE_INAB,
                decimales=1,
                max_filas=None,
                archivo="resultados_reportados_inab_conap_guatemala_2016_2020.csv",
                descarga=productos["resultados_reportados_inab_conap_nacionales"],
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
                "Figura 2. Componentes del balance nacional reportado por INAB y CONAP, 2016–2020",
                "La recuperación se muestra como una sustracción contable. La operación reproduce el cálculo reportado por INAB y CONAP, pero no demuestra equivalencia ecológica inmediata.",
                FUENTE_INAB,
                alto=620,
            )
            """,
            titulo_colab="Mostrar Figura 2",
            resultado=True,
        ),
        _codigo(
            """
            departamentales = productos["resultados_reportados_inab_conap_departamentales"].copy()
            tabla_departamental = departamentales[[
                "depto", "perdida_bruta_ha", "recuperacion_bruta_ha", "perdida_neta_ha"
            ]].rename(columns={
                "depto": "Departamento",
                "perdida_bruta_ha": "Pérdida bruta (ha)",
                "recuperacion_bruta_ha": "Recuperación bruta (ha)",
                "perdida_neta_ha": "Pérdida neta (ha)",
            }).sort_values("Pérdida neta (ha)", ascending=False)
            """,
            titulo_colab="Preparar resultados departamentales reportados por INAB y CONAP",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_departamental,
                "Tabla 2. Balance reportado por INAB y CONAP por departamento",
                "Orden descendente por pérdida neta acumulada. Las dos unidades lacustres permanecen en los agregados departamentales y se identifican en completacion_nacional_unidades.csv dentro de la descarga integral.",
                FUENTE_INAB,
                decimales=1,
                max_filas=None,
                archivo="resultados_reportados_inab_conap_departamentos_guatemala_2016_2020.csv",
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
                "Figura 3. Pérdida neta reportada por INAB y CONAP por departamento, 2016–2020",
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
            municipales = productos["resultados_reportados_inab_conap_municipales"].copy()
            extremos_municipales = pd.concat([
                municipales.nsmallest(10, "perdida_neta_ha"),
                municipales.nlargest(10, "perdida_neta_ha"),
            ]).drop_duplicates("codigo").sort_values("perdida_neta_ha", ascending=False)
            tabla_municipal = extremos_municipales[[
                "depto", "municipio", "perdida_neta_ha", "clasificacion_perdida_neta_reportada"
            ]].rename(columns={
                "depto": "Departamento", "municipio": "Municipio",
                "perdida_neta_ha": "Pérdida neta (ha)",
                "clasificacion_perdida_neta_reportada": "Clasificación",
            })
            mostrar_tabla(
                tabla_municipal,
                "Tabla 3. Municipios con mayores pérdidas y ganancias netas reportadas",
                "Se muestran los diez valores más altos y los diez más bajos; el CSV contiene los 340 municipios.",
                FUENTE_INAB,
                decimales=1,
                max_filas=None,
                archivo="resultados_reportados_inab_conap_municipios_guatemala_2016_2020.csv",
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
                color="clasificacion_perdida_neta_reportada", symbol="clasificacion_perdida_neta_reportada",
                hover_name="municipio",
                custom_data=["depto", "recuperacion_bruta_ha", "perdida_bruta_ha", "perdida_neta_ha"],
                labels={
                    "recuperacion_log1p": "Ganancia de cobertura (ha; escala log₁₀[1+x])",
                    "perdida_log1p": "Pérdida bruta (ha; escala log₁₀[1+x])",
                    "clasificacion_perdida_neta_reportada": "Clasificación",
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
                "La transformación log₁₀(1+x) conserva los 340 municipios, incluidos los valores cero. Sobre B = R hay pérdida neta reportada; debajo hay ganancia neta reportada.",
                FUENTE_INAB,
                alto=720,
            )
            """,
            titulo_colab="Mostrar Figura 3",
            resultado=True,
        ),
        _texto(
            r"""
            ## 3. Asignación territorial de la proporción de regeneración equivalente

            ### 3.1 Definición del factor

            La *proporción de regeneración equivalente*, $\rho_i$, es el factor aplicado a la
            recuperación de cobertura antes de restarla de la pérdida bruta. En este ejercicio se
            parametriza con la recuperación relativa de biomasa aérea que los sitios de referencia
            de Poorter et al. (2016) alcanzan después de veinte años respecto de la biomasa de su
            bosque maduro de referencia.

            El horizonte de veinte años pertenece al parámetro científico utilizado. No indica la
            edad de la ganancia de cobertura reportada por INAB y CONAP ni implica que las hectáreas
            municipales hayan recuperado la misma composición, estructura o permanencia.

            $$H_i=B_i-\rho_iR_i.$$

            | Resultado reproducido | Valor de la proporción $\rho_i$ | Aplicación |
            |---|---:|---|
            | Pérdida bruta | 0 % | No se resta recuperación |
            | Pérdida neta reportada por INAB y CONAP | 100 % | Se resta toda la recuperación y se reproduce $N_i=B_i-R_i$ |
            | Saldo forestal ponderado | Intervalo del grupo territorial | Se resta únicamente la fracción parametrizada con los sitios de referencia |

            ### 3.2 Universo territorial y regla de asignación

            Guatemala tenía 340 municipios durante el período analizado. La tabla de INAB y CONAP
            contiene 342 registros porque incorpora además el Lago de Amatitlán y el Lago de
            Atitlán como unidades de reporte sin código municipal.

            La asignación municipal reproduce cinco listas explícitas y disjuntas de códigos. Los
            172 municipios incluidos reciben el intervalo de su grupo territorial; los otros 168
            municipios conservan la pérdida neta reportada por INAB y CONAP. Los dos lagos no se
            clasifican como municipios ni reciben una proporción.

            Las listas se formaron con criterios territoriales de posición geográfica, humedad,
            estacionalidad y déficit hídrico. Estos criterios explican la agrupación utilizada en
            el cálculo, pero no constituyen una medición ambiental individual de cada municipio.
            """
        ),
        _codigo(
            """
            catalogo = productos["catalogo_proporcion_regeneracion_equivalente"].copy()
            trazabilidad_sitios = productos["trazabilidad_grupo_sitio"].copy()
            resumen_grupos = productos["resumen_grupos_territoriales"].copy()
            catalogo_tabla = resumen_grupos.loc[
                resumen_grupos["tipo_unidad_analitica"].eq("municipios_con_proporcion")
            ].sort_values("orden").copy()
            orden_grupos = catalogo_tabla["grupo_territorial_id"].tolist()
            nombres_publicos = dict(zip(
                catalogo_tabla["grupo_territorial_id"],
                catalogo_tabla["grupo_territorial_nombre"],
            ))

            def etiqueta_intervalo(fila):
                if pd.isna(fila["proporcion_regeneracion_equivalente_min"]):
                    return "No aplica"
                minimo = 100 * fila["proporcion_regeneracion_equivalente_min"]
                medio = 100 * fila["proporcion_regeneracion_equivalente_central"]
                maximo = 100 * fila["proporcion_regeneracion_equivalente_max"]
                if np.isclose(minimo, maximo):
                    return f"{medio + 1e-9:.1f} % (valor único)"
                return (
                    f"{minimo + 1e-9:.1f}–{maximo + 1e-9:.1f} %; "
                    f"punto medio {medio + 1e-9:.1f} %"
                )

            tabla_trazabilidad = pd.DataFrame({
                "Grupo territorial en Guatemala": resumen_grupos["grupo_territorial_nombre"],
                "Criterio de agrupación": resumen_grupos["criterio_agrupacion"],
                "Territorios o sitios utilizados como referencia": resumen_grupos.apply(
                    lambda fila: fila["territorios_sitios_referencia"]
                    if fila["fundamento_vinculacion_sitios"] == "No aplica"
                    else (
                        f"{fila['territorios_sitios_referencia']}; "
                        f"{fila['fundamento_vinculacion_sitios']}"
                    ),
                    axis=1,
                ),
                "Proporción de regeneración equivalente": resumen_grupos.apply(
                    etiqueta_intervalo, axis=1
                ),
                "Aplicación en el cálculo": resumen_grupos["aplicacion_calculo"],
                "Unidades": resumen_grupos["unidades"].astype(int),
            })
            """,
            titulo_colab="Preparar asignación territorial y proporciones",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_trazabilidad,
                "Tabla 4. Asignación territorial y proporciones de regeneración equivalente utilizadas en el cálculo",
                "Los criterios describen las características compartidas que formaron cada lista. La vinculación con los sitios fundamenta el parámetro aplicado, pero no demuestra equivalencia ecológica de cada hectárea municipal. Para el grupo seco, 25.0–65.0 % es el redondeo exterior del intervalo observado de 25.4–64.5 %.",
                "INAB y CONAP (2023), INAB (2023b) y Poorter et al. (2016, 2017); asignación territorial y cálculos del autor.",
                decimales=0,
                max_filas=None,
                archivo="asignacion_grupos_territoriales_proporcion_regeneracion_equivalente.csv",
                descarga=resumen_grupos,
            )
            """,
            titulo_colab="Mostrar Tabla 4",
            resultado=True,
        ),
        _texto(
            r"""
            La descarga de la Tabla 4 contiene, para cada grupo, la lista exacta de códigos,
            los límites inferior y superior, el punto medio, los sitios de referencia y el
            tratamiento aplicado. La trazabilidad individual de los 342 registros se conserva
            por separado en `00_trazabilidad_fuentes/trazabilidad_municipio_grupo_territorial_guatemala_2016_2020.csv`.

            Tres registros ilustran la aplicación de la regla de pertenencia:

            | Registro | Aplicación |
            |---|---|
            | San José del Golfo (`0104`) | El código pertenece a la lista de valles secos; recibe el intervalo de ese grupo |
            | Guatemala (`0101`) | El código no pertenece a las cinco listas; conserva $N_i=B_i-R_i$ |
            | Lago de Amatitlán | No tiene código municipal; permanece fuera de la clasificación municipal |

            ### 3.3 Ejemplo de aplicación municipal

            | Paso en San Andrés Villa Seca (`1106`) | Resultado |
            |---|---:|
            | Pérdida bruta | 793.8 ha |
            | Ganancia de cobertura reportada | 1,072.2 ha |
            | Pérdida neta reportada por INAB y CONAP | −278.4 ha |
            | Grupo territorial | Tierras bajas húmedas |
            | Proporción de regeneración equivalente | 59.3–76.6 % |
            | Recuperación equivalente aplicada | 635.8–821.3 ha |
            | Saldo ponderado | −27.5 a 158.0 ha |

            Con 76.6 % se descuenta más recuperación y se obtiene el extremo menor del saldo;
            con 59.3 % se descuenta menos y se obtiene el extremo mayor. Como el intervalo cruza
            cero, el resultado se clasifica como indeterminado.

            Para los sitios secos, los valores observados de 25.4–64.5 % se redondean hacia
            afuera a 25.0–65.0 %. La operación exacta permanece en el anexo metodológico y en los
            archivos descargables.
            """
        ),
        _codigo(
            """
            posiciones = {
                grupo_territorial_id: len(orden_grupos) - 1 - indice
                for indice, grupo_territorial_id in enumerate(orden_grupos)
            }
            nombres_figura = {
                grupo_territorial_id: "<br>".join(wrap(nombre, width=28))
                for grupo_territorial_id, nombre in nombres_publicos.items()
            }
            catalogo_fig = catalogo_tabla.copy()
            catalogo_fig["posicion"] = catalogo_fig["grupo_territorial_id"].map(posiciones)
            catalogo_fig["etiqueta_publica"] = catalogo_fig["grupo_territorial_id"].map(
                nombres_publicos
            )

            fig_proporciones = go.Figure()
            for indice, fila in catalogo_fig.iterrows():
                fig_proporciones.add_trace(go.Scatter(
                    x=[fila["proporcion_regeneracion_equivalente_min"], fila["proporcion_regeneracion_equivalente_max"]],
                    y=[fila["posicion"], fila["posicion"]],
                    mode="lines",
                    line=dict(color="#146C7A", width=6),
                    hoverinfo="skip",
                    name="Intervalo aplicado",
                    legendgroup="intervalo",
                    showlegend=indice == 0,
                ))

            extremos = []
            for _, fila in catalogo_fig.iterrows():
                limites = (
                    [(fila["proporcion_regeneracion_equivalente_min"], "Valor único")]
                    if np.isclose(fila["proporcion_regeneracion_equivalente_min"], fila["proporcion_regeneracion_equivalente_max"])
                    else [
                        (fila["proporcion_regeneracion_equivalente_min"], "Mínimo"),
                        (fila["proporcion_regeneracion_equivalente_max"], "Máximo"),
                    ]
                )
                for valor, tipo in limites:
                    extremos.append({
                        "valor": valor,
                        "posicion": fila["posicion"],
                        "grupo": fila["etiqueta_publica"],
                        "tipo": tipo,
                    })
            extremos = pd.DataFrame(extremos)
            fig_proporciones.add_trace(go.Scatter(
                x=extremos["valor"],
                y=extremos["posicion"],
                mode="markers",
                marker=dict(
                    color="#146C7A", size=8, symbol="circle",
                    line=dict(color="white", width=1),
                ),
                customdata=extremos[["grupo", "tipo"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>%{customdata[1]}: %{x:.1%}<extra></extra>"
                ),
                name="Límite del intervalo",
                showlegend=False,
            ))

            fig_proporciones.add_trace(go.Scatter(
                x=catalogo_fig["proporcion_regeneracion_equivalente_central"],
                y=catalogo_fig["posicion"],
                mode="markers+text",
                marker=dict(color="#24363D", size=12, symbol="diamond"),
                text=catalogo_fig["proporcion_regeneracion_equivalente_central"].map(
                    lambda valor: f"{100 * valor + 1e-9:.1f}%"
                ),
                textposition="bottom center",
                textfont=dict(size=10, color="#24363D"),
                customdata=catalogo_fig[[
                    "etiqueta_publica", "proporcion_regeneracion_equivalente_min", "proporcion_regeneracion_equivalente_max", "territorios_sitios_referencia"
                ]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b>"
                    "<br>Intervalo aplicado: %{customdata[1]:.1%}–%{customdata[2]:.1%}"
                    "<br>Punto medio de los límites: %{x:.1%}"
                    "<br>Referencias: %{customdata[3]}<extra></extra>"
                ),
                name="Punto medio del intervalo",
            ))

            sitios_fig = trazabilidad_sitios.loc[
                trazabilidad_sitios["uso_sitio"].eq("numerico")
                & trazabilidad_sitios["proporcion_grupo_id"].isin(orden_grupos)
            ].copy()
            sitios_fig["proporcion"] = sitios_fig["relative_recovery_pct_20y"] / 100
            sitios_fig["pais_publico"] = sitios_fig["country"].replace({
                "Mexico": "México", "Panama": "Panamá", "Brazil": "Brasil",
                "Bolivia": "Bolivia", "Costa Rica": "Costa Rica",
            })
            sitios_fig["posicion"] = (
                sitios_fig["proporcion_grupo_id"].map(posiciones) + 0.16
            )
            fig_proporciones.add_trace(go.Scatter(
                x=sitios_fig["proporcion"],
                y=sitios_fig["posicion"],
                mode="markers",
                marker=dict(
                    color="#687980", size=9, symbol="circle-open",
                    line=dict(color="#687980", width=1.5),
                ),
                customdata=sitios_fig[["site_name", "pais_publico"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b>, %{customdata[1]}"
                    "<br>Valor publicado: %{x:.1%}<extra></extra>"
                ),
                name="Valor publicado por sitio",
            ))
            fig_proporciones.update_xaxes(
                title="Proporción de regeneración equivalente (%)",
                range=[0, 1], dtick=0.2, tickformat=".0%"
            )
            fig_proporciones.update_yaxes(
                title=None,
                tickmode="array",
                tickvals=[posiciones[grupo_territorial_id] for grupo_territorial_id in orden_grupos],
                ticktext=[nombres_figura[grupo_territorial_id] for grupo_territorial_id in orden_grupos],
                range=[-0.45, len(orden_grupos) - 0.45],
                showgrid=False,
            )
            fig_proporciones.update_layout(margin=dict(l=285, r=55), hovermode="closest")
            mostrar_figura(
                fig_proporciones,
                "Figura 5. Intervalos y puntos medios de la proporción de regeneración equivalente por grupo territorial",
                "Las líneas muestran los intervalos aplicados; los círculos delimitan sus extremos; los diamantes son el punto medio aritmético de los límites, no el promedio de los sitios; y los círculos abiertos son los valores publicados para los sitios seleccionados. Los intervalos no son intervalos de confianza.",
                FUENTE_RECUPERACION,
                alto=690,
            )
            """,
            titulo_colab="Construir Figura 5",
            resultado=True,
        ),
        _codigo(
            """
            dominio = productos["resultados_recuperacion_dominio"].iloc[0]
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
                "El dominio cubre los municipios incluidos en las cinco listas territoriales documentadas; estas cifras no se presentan como total nacional.",
                FUENTE_RECUPERACION,
                decimales=1,
                max_filas=None,
                archivo="resultados_recuperacion_ponderada_dominio_guatemala_2016_2020.csv",
                descarga=productos["resultados_recuperacion_dominio"],
            )
            """,
            titulo_colab="Mostrar Tabla 6",
            resultado=True,
        ),
        _codigo(
            """
            recuperacion_departamentos = productos["resultados_recuperacion_departamentos"].copy()
            recuperacion_departamentos["Saldo ponderado (ha)"] = recuperacion_departamentos.apply(
                lambda f: f"{f.saldo_ponderado_inferior_ha:,.0f}–{f.saldo_ponderado_superior_ha:,.0f}",
                axis=1,
            )
            tabla_recuperacion_departamentos = recuperacion_departamentos[[
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
                tabla_recuperacion_departamentos,
                "Tabla 6. Resultados departamentales dentro del dominio de aplicación",
                "Cada agregado incluye únicamente municipios con una proporción de su grupo territorial; por ello no equivale necesariamente al total departamental.",
                FUENTE_RECUPERACION,
                decimales=1,
                max_filas=None,
                archivo="resultados_recuperacion_ponderada_departamentos_guatemala_2016_2020.csv",
                descarga=recuperacion_departamentos,
            )
            """,
            titulo_colab="Mostrar Tabla 7",
            resultado=True,
        ),
        _codigo(
            """
            recuperacion_municipios = productos["resultados_recuperacion_municipios"].copy()
            recuperacion_municipios["recuperacion_reconocida_central_ha"] = (
                recuperacion_municipios["proporcion_regeneracion_equivalente_central"] * recuperacion_municipios["recuperacion_bruta_ha"]
            )
            recuperacion_municipios["clasificacion_central"] = np.select(
                [
                    recuperacion_municipios["saldo_ponderado_central_ha"].gt(0),
                    recuperacion_municipios["saldo_ponderado_central_ha"].lt(0),
                ],
                ["Pérdida", "Ganancia"],
                default="Equilibrio",
            )
            panel_reportado = recuperacion_municipios.assign(
                Tratamiento="Cálculo reportado: R completa",
                recuperacion_reconocida_ha=recuperacion_municipios["recuperacion_bruta_ha"],
                Clasificación=recuperacion_municipios["clasificacion_perdida_neta_reportada"],
            )
            panel_ponderado = recuperacion_municipios.assign(
                Tratamiento="Ponderación: punto medio de ρ × R",
                recuperacion_reconocida_ha=recuperacion_municipios["recuperacion_reconocida_central_ha"],
                Clasificación=recuperacion_municipios["clasificacion_central"],
            )
            dispersion_paneles = pd.concat([panel_reportado, panel_ponderado], ignore_index=True)
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
                category_orders={"Tratamiento": ["Cálculo reportado: R completa", "Ponderación: punto medio de ρ × R"]},
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
                FUENTE_RECUPERACION,
                alto=770,
            )
            """,
            titulo_colab="Construir Figura 6",
            resultado=True,
        ),
        _codigo(
            """
            escala_simetica = lambda s: np.sign(s) * np.log10(1 + np.abs(s) / 100)
            recuperacion_municipios["N_transformado"] = escala_simetica(recuperacion_municipios["perdida_neta_ha"])
            recuperacion_municipios["H_transformado"] = escala_simetica(recuperacion_municipios["saldo_ponderado_central_ha"])
            recuperacion_municipios["Estado del cambio"] = np.select(
                [
                    recuperacion_municipios["clasificacion_perdida_neta_reportada"].eq("Ganancia")
                    & recuperacion_municipios["clasificacion_ponderada"].eq("Pérdida"),
                    recuperacion_municipios["clasificacion_ponderada"].eq("Indeterminado"),
                ],
                ["Ganancia → pérdida", "Hacia indeterminado"],
                default="Sin cambio de clase",
            )
            fig_cambio = px.scatter(
                recuperacion_municipios,
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
                recuperacion_municipios["N_transformado"].abs().max(),
                recuperacion_municipios["H_transformado"].abs().max(),
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
                title="Pérdida neta reportada, N (ha; escala simétrica)",
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
                    "<br>N reportada: %{customdata[1]:,.1f} ha"
                    "<br>H central: %{customdata[2]:,.1f} ha"
                    "<br>Intervalo H: %{customdata[3]:,.1f}–%{customdata[4]:,.1f} ha<extra></extra>"
                ),
            )
            mostrar_figura(
                fig_cambio,
                "Figura 7. Cambio municipal entre la pérdida neta y el saldo ponderado",
                "La misma transformación simétrica se aplica a ambos ejes y conserva negativos y ceros. Quince municipios pasan de ganancia a pérdida y once quedan indeterminados o cambian desde equilibrio.",
                FUENTE_RECUPERACION,
                alto=760,
            )
            """,
            titulo_colab="Construir Figura 7",
            resultado=True,
        ),
        _codigo(
            """
            transiciones = productos["transiciones_clasificacion_ponderada"].copy()
            orden_i = ["Ganancia", "Equilibrio", "Pérdida"]
            orden_p = ["Ganancia", "Indeterminado", "Pérdida"]
            matriz_n = transiciones.pivot(
                index="clasificacion_perdida_neta_reportada", columns="clasificacion_ponderada", values="municipios"
            ).reindex(index=orden_i, columns=orden_p).fillna(0)
            matriz_pct = transiciones.pivot(
                index="clasificacion_perdida_neta_reportada", columns="clasificacion_ponderada", values="porcentaje_fila"
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
                hovertemplate="Pérdida neta reportada: %{y}<br>Ponderada: %{x}<br>Municipios: %{z}<extra></extra>",
            ))
            fig_transiciones.update_xaxes(title="Clasificación con intervalo ponderado", side="bottom")
            fig_transiciones.update_yaxes(title="Clasificación según la pérdida neta reportada", autorange="reversed")
            mostrar_figura(
                fig_transiciones,
                "Figura 8. Transición de clasificaciones municipales al aplicar el ponderador",
                "Cada celda muestra municipios y porcentaje dentro de la clasificación según la pérdida neta reportada. Cambian 26 de las 172 clasificaciones.",
                FUENTE_RECUPERACION,
                alto=650,
            )
            """,
            titulo_colab="Construir Figura 8",
            resultado=True,
        ),
        _codigo(
            """
            tabla_transiciones = matriz_n.reset_index().rename(columns={
                "clasificacion_perdida_neta_reportada": "Clasificación según pérdida neta reportada",
                "Ganancia": "Ponderada: ganancia",
                "Indeterminado": "Ponderada: indeterminado",
                "Pérdida": "Ponderada: pérdida",
            })
            mostrar_tabla(
                tabla_transiciones,
                "Tabla 7. Matriz de transición de clasificaciones municipales",
                "Los conteos corresponden al dominio de 172 municipios; la clasificación ponderada usa el intervalo completo, no solo el punto central.",
                FUENTE_RECUPERACION,
                decimales=0,
                max_filas=None,
                archivo="transiciones_clasificacion_ponderada_municipios_guatemala_2016_2020.csv",
                descarga=transiciones,
            )
            """,
            titulo_colab="Mostrar Tabla 7",
            resultado=True,
        ),
        _codigo(
            """
            cambios = productos["municipios_cambio_clasificacion_ponderada"].copy()
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
                "Tabla 8. Municipios con mayor cambio de clasificación al ponderar la recuperación",
                "Se muestran los veinte mayores aumentos del saldo; el CSV contiene los 26 municipios cuya clasificación cambia con el intervalo ponderado.",
                FUENTE_RECUPERACION,
                decimales=1,
                max_filas=None,
                archivo="cambios_clasificacion_ponderada_municipios_guatemala_2016_2020.csv",
                descarga=cambios,
            )
            """,
            titulo_colab="Mostrar Tabla 8",
            resultado=True,
        ),
        _codigo(
            """
            forestal_dep = recuperacion_departamentos.copy()
            forestal_dep["centro"] = (
                forestal_dep["saldo_ponderado_inferior_ha"] + forestal_dep["saldo_ponderado_superior_ha"]
            ) / 2
            forestal_dep = forestal_dep.sort_values("centro")
            fig_departamentos_recuperacion = go.Figure()
            for fila in forestal_dep.itertuples(index=False):
                fig_departamentos_recuperacion.add_trace(go.Scatter(
                    x=[fila.perdida_neta_ha, fila.centro], y=[fila.depto, fila.depto],
                    mode="lines", line=dict(color="#CBD5D8", width=2),
                    showlegend=False, hoverinfo="skip",
                ))
            fig_departamentos_recuperacion.add_trace(go.Scatter(
                x=forestal_dep["perdida_neta_ha"], y=forestal_dep["depto"],
                mode="markers", name="Pérdida neta reportada",
                marker=dict(color="#0072B2", symbol="square", size=8),
                hovertemplate="%{y}<br>N: %{x:,.1f} ha<extra></extra>",
            ))
            fig_departamentos_recuperacion.add_trace(go.Scatter(
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
            fig_departamentos_recuperacion.add_vline(x=0, line_color="#5C6F77", line_width=1)
            fig_departamentos_recuperacion.update_xaxes(title="Resultado (ha); la pérdida es positiva", tickformat=",")
            fig_departamentos_recuperacion.update_yaxes(title=None)
            mostrar_figura(
                fig_departamentos_recuperacion,
                "Figura 9. Cambio departamental entre pérdida neta y saldo ponderado",
                "Solo incluye municipios del dominio de aplicación. El cuadrado es N; el diamante y su intervalo representan H. Las líneas grises unen lecturas alternativas.",
                FUENTE_RECUPERACION,
                alto=820,
            )
            """,
            titulo_colab="Construir Figura 9",
            resultado=True,
        ),
        _texto(
            r"""
            ## 4. Completación del saldo forestal nacional

            La proporción de regeneración equivalente se aplica únicamente a los municipios de
            las cinco listas territoriales. El total nacional combina dos componentes:

            | Componente | Unidades | Aplicación en el cálculo | Resultado |
            |---|---:|---|---:|
            | Municipios dentro del dominio | 172 municipios | Saldo ponderado con proporciones de regeneración equivalente | 99,593–107,108 ha |
            | Otros municipios | 168 municipios | Pérdida neta reportada, sin asignar una proporción | 16,862 ha |
            | Unidades lacustres | 2 lagos | Pérdida neta reportada; no reciben una proporción municipal | 18 ha |
            | Total de la fuente | 342 registros | Suma de 340 municipios y 2 lagos | 116,473–123,988 ha |

            Las dos unidades lacustres se conservan en la suma nacional de la fuente, pero no se
            tratan como municipios ni forman un grupo territorial. Esta completación es conservadora respecto del alcance: evita
            asignar un valor a municipios sin sitios de referencia documentados. El resultado queda
            entre la pérdida bruta y la pérdida neta reportada. La expresión formal se presenta en
            el anexo metodológico.
            """
        ),
        _codigo(
            """
            completacion = productos["completacion_nacional_resumen"].copy()
            fila_completacion = completacion.iloc[0]
            tabla_completacion = pd.DataFrame({
                "Magnitud": [
                    "Registros de la fuente (340 municipios y 2 lagos)", "Municipios con proporción de regeneración equivalente",
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
                "Método": ["Universo reportado", "Asignación territorial", "B", "R", "N = B − R", "Completación conservadora"],
            })
            """,
            titulo_colab="Preparar completación nacional",
        ),
        _codigo(
            """
            mostrar_tabla(
                tabla_completacion,
                "Tabla 9. Completación conservadora del saldo forestal nacional",
                "Dentro del dominio se aplica el intervalo de la proporción de regeneración equivalente. En los otros 168 municipios y en las dos unidades lacustres se conserva B − R; los lagos no reciben una proporción municipal. El intervalo refleja únicamente los valores transferidos desde los sitios de referencia.",
                FUENTE_RECUPERACION,
                decimales=1,
                max_filas=None,
                archivo="completacion_conservadora_resumen_guatemala_2016_2020.csv",
                descarga=completacion,
            )
            """,
            titulo_colab="Mostrar Tabla 9",
            resultado=True,
        ),
        _codigo(
            """
            resultados_nacionales = productos["resultados_forestales_nacionales"].copy()
            resultados_nacionales["central"] = (
                resultados_nacionales["resultado_inferior_ha"]
                + resultados_nacionales["resultado_superior_ha"]
            ) / 2
            resultados_nacionales["err_mas"] = (
                resultados_nacionales["resultado_superior_ha"] - resultados_nacionales["central"]
            )
            resultados_nacionales["err_menos"] = (
                resultados_nacionales["central"] - resultados_nacionales["resultado_inferior_ha"]
            )
            orden_resultados = ["Deforestación bruta", "Saldo ponderado por recuperación", "Pérdida neta reportada"]
            resultados_nacionales["regla"] = pd.Categorical(
                resultados_nacionales["regla"], categories=orden_resultados, ordered=True
            )
            resultados_nacionales = resultados_nacionales.sort_values("regla")
            fig_resultados_nacionales = go.Figure(go.Scatter(
                x=resultados_nacionales["central"], y=resultados_nacionales["regla"].astype(str), mode="markers+text",
                marker=dict(
                    color=["#D55E00", "#6A3D9A", "#0072B2"],
                    symbol=["circle", "diamond", "square"], size=12,
                ),
                error_x=dict(
                    type="data",
                    array=resultados_nacionales["err_mas"],
                    arrayminus=resultados_nacionales["err_menos"],
                ),
                text=[f"  {v:,.0f}" for v in resultados_nacionales["central"]], textposition="middle right",
                hovertemplate="%{y}<br>%{x:,.0f} ha<extra></extra>",
            ))
            maximo_resultados = resultados_nacionales["resultado_superior_ha"].max()
            fig_resultados_nacionales.update_xaxes(
                title="ha acumuladas, 2016–2020", range=[0, maximo_resultados * 1.20], tickformat=","
            )
            fig_resultados_nacionales.update_yaxes(title=None)
            """,
            titulo_colab="Construir Figura 5",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_resultados_nacionales,
                "Figura 10. Deforestación bruta, saldo ponderado y pérdida neta nacional",
                "La línea del saldo ponderado muestra el intervalo nacional conservador. Los tres resultados parten de la misma base y no son categorías aditivas.",
                FUENTE_RECUPERACION,
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

            La cadena de cálculo tiene cuatro pasos:

            | Paso | Operación | Resultado que representa |
            |---:|---|---|
            | 1 | Dividir el resultado acumulado de cuatro años entre cuatro | Superficie anual media |
            | 2 | Multiplicar esa superficie por Q29,986 por ha y año | Flujo monetario anual indicativo |
            | 3 | Descontar 25 años de ese flujo | Valor presente de una cohorte anual |
            | 4 | Incorporar diez cohortes anuales consecutivas | Valor presente de la década |

            Son objetos distintos y no deben intercambiarse. La tabla siguiente los muestra en
            columnas separadas; las expresiones de descuento permanecen en el anexo metodológico.
            """
        ),
        _codigo(
            """
            valoracion = productos["valoracion_resultados_forestales_nacionales"].copy()
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
                archivo="valoracion_resultados_forestales_guatemala_2016_2020_precios_2026.csv",
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
                archivo="sensibilidad_valor_presente_guatemala_precios_2026.csv",
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
                "Pérdida neta reportada": "#0072B2",
            }
            trazos_regla = {
                "Deforestación bruta": "solid",
                "Saldo ponderado por recuperación": "dash",
                "Pérdida neta reportada": "dot",
            }
            simbolos_regla = {
                "Deforestación bruta": "circle",
                "Saldo ponderado por recuperación": "diamond",
                "Pérdida neta reportada": "square",
            }
            fig_sensibilidad = go.Figure()
            for regla_nombre in [
                "Deforestación bruta", "Saldo ponderado por recuperación", "Pérdida neta reportada"
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

            Esta sección no pronostica el futuro. Compara qué ocurriría si los flujos anuales
            observados entre 2016 y 2020 se redujeran, continuaran o aumentaran durante una
            década. Cada supuesto se aplica por separado a la pérdida bruta y a la ganancia de
            cobertura.

            La *contención proporcional* usa una cuarta parte de ambos flujos; la *continuidad*
            conserva los flujos observados; y el *deterioro proporcional acelerado* los duplica.
            La contención no se denomina restauración porque no añade una trayectoria nueva de
            recuperación. La formulación general queda en el anexo metodológico.
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
                archivo="escenarios_forestales_guatemala_2026_2035.csv",
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
                    "Pérdida neta reportada": "#0072B2",
                },
                line_dash_map={
                    "Deforestación bruta": "solid",
                    "Saldo ponderado por recuperación": "dash",
                    "Pérdida neta reportada": "dot",
                },
                symbol_map={
                    "Deforestación bruta": "circle",
                    "Saldo ponderado por recuperación": "diamond",
                    "Pérdida neta reportada": "square",
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
                    "Pérdida neta reportada": "#0072B2",
                },
                line_dash_map={
                    "Deforestación bruta": "solid",
                    "Saldo ponderado por recuperación": "dash",
                    "Pérdida neta reportada": "dot",
                },
                symbol_map={
                    "Deforestación bruta": "circle",
                    "Saldo ponderado por recuperación": "diamond",
                    "Pérdida neta reportada": "square",
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
                archivo="escenarios_forestales_valorados_guatemala_2026_2035.csv",
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
            disponibles en el portal de INAB: 30 muestran aumento conjunto de carbono y área
            basal, 21 muestran disminución conjunta y 4 son mixtas.

            El límite inferior cuenta solo las 30 trayectorias favorables: 30 de 55, o 54.5 %.
            El superior incorpora también las cuatro mixtas: 34 de 55, o 61.8 %. Este rango no es
            un intervalo de confianza; resume dos formas explícitas de contar la evidencia local.
            Las 55 series representan 73.3 % de los 75 registros de parcela del archivo analítico,
            pero esa cobertura se documenta y no se usa como multiplicador.

            El cálculo sigue la misma intuición que el saldo ponderado nacional:

            $$
            \text{saldo local}
            =\text{pérdida bruta}
            -(\text{proporción estructural local}\times\text{ganancia de cobertura}).
            $$

            Los dos extremos, la tolerancia de clasificación y la relación con la pérdida neta
            se detallan en el anexo metodológico.

            $B_i$ y $R_i$ siguen siendo la pérdida y la ganancia de cobertura forestal del
            municipio completo, no cambios exclusivos de manglar. La evidencia de campo informa
            únicamente el ponderador local. Los resultados se comparan con el cálculo neto y,
            donde existe soporte común, con el saldo basado en la proporción de regeneración
            equivalente; no se suman
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
                archivo="intervalo_estructural_manglar_guatemala.csv",
                descarga=productos["intervalo_estructural_local"],
            )
            """,
            titulo_colab="Mostrar Tabla 14",
            resultado=True,
        ),
        _codigo(
            """
            evidencia_manglar = productos["evidencia_manglar"].copy()
            evidencia_manglar["Total"] = evidencia_manglar["series_multitemporales"]
            orden_manglar = evidencia_manglar.sort_values(["Total", "municipio"])["municipio"].tolist()
            categorias_manglar = [
                ("Aumento conjunto", "suben_carbono_y_area_basal", "#009E73"),
                ("Disminución conjunta", "bajan_carbono_y_area_basal", "#D55E00"),
                ("Mixta", "trayectoria_mixta", "#6A3D9A"),
            ]
            fig_evidencia_manglar = go.Figure()
            for etiqueta, columna, color in categorias_manglar:
                valores = evidencia_manglar[columna]
                fig_evidencia_manglar.add_trace(go.Bar(
                    x=valores,
                    y=evidencia_manglar["municipio"],
                    orientation="h",
                    name=etiqueta,
                    marker_color=color,
                    text=[str(int(v)) if v > 0 else "" for v in valores],
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate="%{y}<br>%{fullData.name}: %{x:.0f}<extra></extra>",
                ))
            fig_evidencia_manglar.update_layout(
                barmode="stack", legend_title_text="Trayectoria estructural",
                margin=dict(l=210, r=60),
            )
            fig_evidencia_manglar.update_xaxes(
                title="Número de series multitemporales", range=[0, 17.5], dtick=2
            )
            fig_evidencia_manglar.update_yaxes(
                title=None, categoryorder="array", categoryarray=orden_manglar
            )
            fig_evidencia_manglar.add_annotation(
                x=0.25, y="Nueva Concepción", text="0", showarrow=False,
                xanchor="left", font=dict(color="#5C6F77", size=11),
            )
            """,
            titulo_colab="Construir Figura 15",
        ),
        _codigo(
            """
            mostrar_figura(
                fig_evidencia_manglar,
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
            resumen_local = productos["resumen_manglar_local"].iloc[0]
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
                FUENTE_MANGLAR,
                decimales=1,
                max_filas=None,
                archivo="resumen_manglar_guatemala_2016_2020.csv",
                descarga=productos["resumen_manglar_local"],
            )
            """,
            titulo_colab="Mostrar Tabla 15",
            resultado=True,
        ),
        _codigo(
            """
            local_comp = productos["comparacion_recuperacion_ponderada_manglar"].copy()
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
                ("Saldo con regeneración equivalente", "saldo_ponderado_inferior_ha", "saldo_ponderado_superior_ha", "#E69F00", "circle"),
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
                "Los puntos e intervalos son resultados alternativos de la misma pérdida y ganancia de cobertura municipal. La aplicación estructural local y el saldo basado en la proporción de regeneración equivalente no se agregan entre sí.",
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
            tabla_local["Saldo con regeneración equivalente (ha)"] = local_comp.apply(
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
                archivo="comparacion_recuperacion_ponderada_y_manglar_municipios_guatemala_2016_2020.csv",
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
            costos = productos["costos_contextuales"].copy().rename(columns={
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
                archivo="costos_contextuales_no_aditivos_guatemala_2026.csv",
                descarga=costos,
            )
            """,
            titulo_colab="Mostrar Recuadro 1",
            resultado=True,
        ),
        _texto(
            r"""
            ## Anexo metodológico. Fórmulas de reproducción

            La ruta principal explicó cada operación con palabras y ejemplos. Este anexo reúne
            la notación formal para quien necesite reproducir o adaptar los cálculos. Puede
            omitirse sin perder la lectura de los resultados.

            <details>
            <summary><em>Mostrar las fórmulas y la definición de sus símbolos</em></summary>

            ### A.1 Balance reportado y saldo ponderado

            | Símbolo | Significado | Unidad |
            |---|---|---|
            | $B_i$ | Pérdida bruta de la unidad $i$ | ha |
            | $R_i$ | Ganancia de cobertura reportada | ha |
            | $N_i$ | Pérdida neta reportada por INAB y CONAP | ha |
            | $\rho_i$ | Proporción de regeneración equivalente asignada | proporción |
            | $H_i$ | Saldo ponderado por recuperación | ha |

            El balance reportado por INAB y CONAP se reproduce como:

            $$N_i=B_i-R_i.$$

            El saldo ponderado descuenta solo la fracción indicada por la proporción:

            $$H_i(\rho)=B_i-\rho_iR_i.$$

            Si la proporción tiene un límite inferior y otro superior, se calculan dos saldos.
            Como una proporción mayor descuenta más recuperación, produce el saldo menor:

            $$H_i^{\mathrm{inf}}=B_i-\rho_i^{\mathrm{sup}}R_i,$$

            $$H_i^{\mathrm{sup}}=B_i-\rho_i^{\mathrm{inf}}R_i.$$

            Para los sitios secos, el intervalo observado $[0.254,0.645]$ se amplía al múltiplo
            de 0.05 inmediatamente inferior y superior:

            $$
            \left[0.05\left\lfloor\frac{0.254}{0.05}\right\rfloor,
            0.05\left\lceil\frac{0.645}{0.05}\right\rceil\right]=[0.25,0.65].
            $$

            ### A.2 Completación nacional

            Sea $U$ el conjunto de 342 registros de la fuente: 340 municipios y dos unidades
            lacustres. Sea $P\subset U$ el conjunto de 172 municipios ponderados. El primer
            término aplica la proporción dentro de $P$; el segundo conserva la pérdida neta
            reportada por INAB y CONAP en los otros 168 municipios y en los dos lagos:

            $$
            H_{GT}=\sum_{i\in P}(B_i-\rho_iR_i)
            +\sum_{i\in U\setminus P}(B_i-R_i).
            $$

            ### A.3 Valoración indicativa

            Si $H_i$ es una superficie acumulada durante cuatro años, su media anual es
            $h_i=H_i/4$. Con un valor anual por hectárea $v$, el flujo monetario es $F_i=v h_i$.
            El valor presente de ese flujo durante $T$ años, a una tasa $r$, es:

            $$VP_i=F_i\left[\frac{1-(1+r)^{-T}}{r}\right].$$

            Para diez cohortes que comienzan en años consecutivos:

            $$VP_{i,10}=\sum_{k=1}^{10}\frac{VP_i}{(1+r)^k}.$$

            ### A.4 Trayectorias comparativas

            Los multiplicadores $m_s^B$ y $m_s^R$ cambian por separado la pérdida y la
            recuperación del supuesto $s$:

            $$H_{i,s}=m_s^B B_i-\rho_i m_s^R R_i.$$

            ### A.5 Aplicación local de manglar

            Con $n_F=30$ trayectorias favorables, $n_M=4$ mixtas y $n=55$ series, los dos
            límites del ponderador estructural local son:

            $$\underline{\omega}_M=\frac{n_F}{n}=\frac{30}{55}=0.5455,$$

            $$\overline{\omega}_M=\frac{n_F+n_M}{n}=\frac{34}{55}=0.6182.$$

            El saldo local y sus extremos se calculan así:

            $$H_{i,M}(\omega_M)=B_i-\omega_MR_i,$$

            $$\underline H_{i,M}=B_i-\overline{\omega}_MR_i,\qquad
            \overline H_{i,M}=B_i-\underline{\omega}_MR_i.$$

            Una proporción mayor produce un saldo menor porque
            $\partial H_{i,M}/\partial\omega_M=-R_i$. El código usa
            $\varepsilon=10^{-8}$ para distinguir pérdida, ganancia e intervalos que cruzan cero.
            La diferencia respecto de la pérdida neta es:

            $$H_{i,M}(\omega_M)-N_i=(1-\omega_M)R_i.$$

            </details>
            """
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
                repo / "05_verificacion" / "manifiesto_resultados.csv",
                repo / "05_verificacion" / "metadatos_ejecucion.json",
                repo / "como_citar.txt",
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
            ## Resumen de resultados reproducidos

            INAB y CONAP reportan 244,394.57 ha de pérdida bruta, 191,658.14 ha de ganancia de
            cobertura y 52,736.43 ha de pérdida neta acumulada para 2016–2020. Al aplicar las
            proporciones de regeneración equivalente en los 172 municipios incluidos, el saldo
            ponderado es de 99,593.41–107,108.21 ha. La completación conserva la pérdida neta
            reportada en los otros 168 municipios y en las dos unidades lacustres, y produce un intervalo nacional de
            116,473.23–123,988.03 ha.

            Estos resultados reproducen las operaciones documentadas en el cuaderno. La
            ponderación utiliza referencias de recuperación relativa de biomasa aérea a los veinte
            años y no convierte la ganancia de cobertura reportada en una medición contemporánea
            de biomasa, composición o madurez forestal.
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
            > ponderado en Guatemala* (Versión 1.0.0) [Material suplementario en línea]. Instituto de
            > Investigación en Ciencias Naturales y Tecnología, Universidad Rafael Landívar.
            > https://doi.org/10.5281/zenodo.22119075

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
    # El formato compacto conserva todas las celdas y salidas, reduce el peso
    # de transferencia y mantiene una serialización determinista.
    DESTINO.write_text(
        json.dumps(
            cuaderno,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    resultados = sum("result" in c.metadata.get("tags", []) for c in cuaderno.cells)
    print(
        f"Cuaderno construido y ejecutado: {DESTINO.relative_to(REPO)} "
        f"({len(cuaderno.cells)} celdas; {resultados} resultados)"
    )


if __name__ == "__main__":
    main()
