"""Presentación académica de resultados reproducibles.

Las figuras conservan en el lienzo únicamente el título y la representación
estadística. Las notas, fuentes e interpretaciones se escriben en celdas
Markdown contiguas para que sean legibles y no formen parte del PNG. Las tablas
se representan como HTML semántico, con encabezados flexibles y descarga CSV.
"""

from __future__ import annotations

import base64
import html
import re
import unicodedata
from pathlib import Path
from textwrap import fill
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display


# Paleta apta para diferenciación cromática frecuente. Las trayectorias deben
# reforzarse con marcadores y/o trazos discontinuos desde el gráfico llamador.
TINTA = "#24363D"
MUTED = "#5C6F77"
TEAL = "#146C7A"
TEAL_CLARO = "#EEF4F6"
PERDIDA = "#D55E00"
GANANCIA = "#0072B2"
INCIERTO = "#E69F00"
GRILLA = "#D9E3E6"
TRAYECTORIA_BRUTA = "#C65300"
TRAYECTORIA_PONDERADA = "#6B3FA0"
TRAYECTORIA_NETA = "#0072B2"

CSS_TABLAS = """
<style>
.sf-bloque{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#24363D;margin:8px 0 18px;max-width:100%}
.sf-lienzo{margin:0;max-width:100%}.sf-subtitulo{font-size:16px;font-weight:400;line-height:1.4;margin:18px 0 10px;padding:0 4px 7px;border-bottom:1px solid #E1E7E9;color:#26353B}
.sf-rotulo{font-weight:700}
.sf-descargas{display:flex;flex-wrap:wrap;gap:7px;margin:8px 0 0}
.sf-descarga{display:inline-block;padding:6px 10px;border:1px solid #6F919C;border-radius:4px;
 color:#294E5B!important;background:#FFF;text-decoration:none;font-size:11px;font-weight:600}
.sf-descarga:hover{background:#EEF4F6}
.sf-tabla-contenedor{max-width:100%;overflow-x:auto;border-top:1px solid #AFC0C5}
.sf-tabla{width:100%;border-collapse:collapse;table-layout:auto;font-size:11.5px;line-height:1.35;font-variant-numeric:tabular-nums lining-nums}
.sf-tabla th{background:#EEF4F6;color:#24363D;font-weight:700;text-align:left;vertical-align:bottom;
 white-space:normal;overflow-wrap:anywhere;padding:10px 12px;border-bottom:1px solid #AFC0C5}
.sf-tabla td{padding:8px 12px;border-bottom:1px solid #D9E3E6;vertical-align:top;white-space:normal}
.sf-tabla tbody tr:nth-child(even){background:#F7FAFA}.sf-tabla .sf-num{text-align:right;white-space:nowrap}
.sf-tarjetas{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.sf-tarjeta{border:1px solid #D9E3E6;border-top:4px solid #146C7A;border-radius:5px;padding:13px;background:#FFF}
.sf-etiqueta{font-size:11px;color:#5C6F77;text-transform:uppercase;letter-spacing:.04em}
.sf-valor{font-size:24px;font-weight:700;margin:6px 0}.sf-detalle{font-size:11px;color:#5C6F77}
.sf-hallazgo{border-left:5px solid #146C7A;background:#EEF4F6;padding:14px 16px;border-radius:4px;line-height:1.45}
</style>
"""


def nombre_archivo(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", normalizado).strip("_").lower()[:90] or "resultado"


def descomponer_titulo(titulo: str) -> tuple[str, str]:
    coincidencia = re.fullmatch(r"(Figura|Tabla|Recuadro)\s+(\d+)\.\s*(.+)", str(titulo).strip())
    if not coincidencia:
        return "", str(titulo).strip()
    return f"{coincidencia.group(1)} {coincidencia.group(2)}", coincidencia.group(3).rstrip(".")


def titulo_apa_html(titulo: str) -> str:
    rotulo, texto = descomponer_titulo(titulo)
    texto_seguro = html.escape(texto)
    return f"<span class='sf-rotulo'>{rotulo}</span><br><em>{texto_seguro}</em>" if rotulo else f"<em>{texto_seguro}</em>"


def titulo_apa_plotly(titulo: str) -> str:
    rotulo, texto = descomponer_titulo(titulo)
    envuelto = "<br>".join(fill(html.escape(texto), width=68).splitlines())
    return f"<b>{rotulo}</b><br><i>{envuelto}</i>" if rotulo else f"<i>{envuelto}</i>"


def _formatear(valor: Any, decimales: int) -> str:
    if pd.isna(valor):
        return "—"
    if isinstance(valor, (bool, np.bool_)):
        return "Sí" if valor else "No"
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return f"{float(valor):,.{decimales}f}"
    return html.escape(str(valor))


def _enlace_descarga(contenido: bytes, nombre: str, mime: str, etiqueta: str) -> str:
    codificado = base64.b64encode(contenido).decode("ascii")
    return (
        f"<a class='sf-descarga' download='{html.escape(nombre)}' "
        f"href='data:{mime};base64,{codificado}'>{html.escape(etiqueta)}</a>"
    )


def _anchos_columnas(marco: pd.DataFrame) -> list[int]:
    """Anchos moderados: texto identificador respira, cifras permanecen compactas."""

    anchos: list[int] = []
    for columna in marco.columns:
        serie = marco[columna]
        if pd.api.types.is_numeric_dtype(serie):
            anchos.append(92)
        else:
            caracteres = max([len(str(columna)), *(len(str(x)) for x in serie.head(25))], default=12)
            anchos.append(min(220, max(105, caracteres * 6)))
    return anchos


def _ancho_tabla(marco: pd.DataFrame) -> int:
    """Ancho editorial del lienzo; evita tablas cortas extendidas a toda la pantalla."""

    return min(980, max(560, sum(_anchos_columnas(marco)) + 58))


def _encabezado_envuelto(texto: str, ancho: int = 21) -> str:
    seguro = html.escape(str(texto))
    return "<br>".join(fill(seguro, width=ancho).splitlines())


def _tabla_html(marco: pd.DataFrame, *, decimales: int) -> str:
    """Convierte un marco en una tabla compacta sin recortar encabezados."""

    encabezados = "".join(f"<th>{html.escape(str(columna))}</th>" for columna in marco.columns)
    filas: list[str] = []
    for _, fila in marco.iterrows():
        celdas: list[str] = []
        for columna in marco.columns:
            numerica = pd.api.types.is_numeric_dtype(marco[columna])
            clase = " class='sf-num'" if numerica else ""
            celdas.append(f"<td{clase}>{_formatear(fila[columna], decimales)}</td>")
        filas.append("<tr>" + "".join(celdas) + "</tr>")
    return (
        "<div class='sf-tabla-contenedor'><table class='sf-tabla'>"
        f"<thead><tr>{encabezados}</tr></thead><tbody>{''.join(filas)}</tbody></table></div>"
    )


def mostrar_tabla(
    marco: pd.DataFrame,
    titulo: str,
    nota: str,
    fuente: str,
    *,
    decimales: int = 2,
    max_filas: int | None = 20,
    archivo: str | None = None,
    descarga: pd.DataFrame | None = None,
) -> None:
    """Muestra una tabla HTML compacta y entrega su CSV en la misma salida.

    ``marco`` controla la vista y ``descarga`` (si se facilita) el CSV íntegro.
    Esto permite condensar una tabla municipal sin sacrificar su trazabilidad.
    """

    datos_descarga = descarga.copy() if descarga is not None else marco.copy()
    visible = marco.copy() if max_filas is None else marco.head(max_filas).copy()
    nombre = archivo or f"{nombre_archivo(titulo)}.csv"
    ancho = _ancho_tabla(visible)
    fragmento = _tabla_html(visible, decimales=decimales)
    enlaces = _enlace_descarga(
        datos_descarga.to_csv(index=False, lineterminator="\n").encode("utf-8-sig"),
        nombre,
        "text/csv;charset=utf-8",
        "Descargar CSV completo",
    )
    display(HTML(
        f"{CSS_TABLAS}<div class='sf-bloque' style='max-width:{ancho}px'>"
        f"<div class='sf-subtitulo'>{titulo_apa_html(titulo)}</div>{fragmento}"
        f"<div class='sf-descargas'>{enlaces}</div></div>"
    ))


def _contenido_descargable(datos: Any, archivo: str) -> tuple[bytes, str]:
    if isinstance(datos, pd.DataFrame):
        return datos.to_csv(index=False, lineterminator="\n").encode("utf-8-sig"), "text/csv;charset=utf-8"
    if isinstance(datos, Path):
        return datos.read_bytes(), _mime_para(datos)
    if isinstance(datos, bytes):
        return datos, _mime_para(Path(archivo))
    return str(datos).encode("utf-8"), _mime_para(Path(archivo))


def mostrar_tarjetas(
    items: list[tuple[str, str, str]],
    titulo: str,
    nota: str,
    fuente: str,
    *,
    archivo: str | None = None,
    datos_descargables: pd.DataFrame | str | bytes | Path | None = None,
) -> None:
    """Muestra tarjetas y descarga; el aparato académico se compone en Markdown."""

    tarjetas = "".join(
        f"<div class='sf-tarjeta'><div class='sf-etiqueta'>{html.escape(e)}</div>"
        f"<div class='sf-valor'>{html.escape(v)}</div><div class='sf-detalle'>{html.escape(d)}</div></div>"
        for e, v, d in items
    )
    enlaces: list[str] = []
    if datos_descargables is not None:
        nombre = archivo or f"{nombre_archivo(titulo)}.csv"
        contenido, mime = _contenido_descargable(datos_descargables, nombre)
        enlaces.insert(0, _enlace_descarga(contenido, nombre, mime, "Descargar datos"))
    contenido = (
        f"{CSS_TABLAS}<div class='sf-bloque'><div class='sf-subtitulo'>{titulo_apa_html(titulo)}</div>"
        f"<div class='sf-tarjetas'>{tarjetas}</div><div class='sf-descargas'>{''.join(enlaces)}</div></div>"
    )
    display(HTML(contenido))


def mostrar_hallazgo(texto: str, etiqueta: str = "Hallazgo") -> None:
    contenido = f"{CSS_TABLAS}<div class='sf-bloque'><div class='sf-hallazgo'><em>{html.escape(etiqueta)}.</em> {html.escape(texto)}</div></div>"
    display(HTML(contenido))


def config_plotly(titulo: str, alto: int = 700, ancho_descarga: int = 1400) -> dict:
    return {
        "displaylogo": False,
        "displayModeBar": True,
        "responsive": True,
        "scrollZoom": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": f"osorio_2026_{nombre_archivo(titulo)}",
            "height": int(max(360, alto)),
            "width": int(ancho_descarga),
            "scale": 2,
        },
    }


def estilo_plotly(
    fig: go.Figure,
    titulo: str,
    nota: str,
    fuente: str,
    *,
    alto: int = 700,
    es_tabla: bool = False,
) -> go.Figure:
    """Aplica una composición limpia; notas y fuentes quedan fuera del lienzo."""

    altura = max(390, alto)
    es_faceta = "xaxis2" in fig.layout
    titulo_renderizado = titulo_apa_plotly(titulo)
    lineas_titulo = titulo_renderizado.count("<br>") + 1
    hay_leyenda = any(getattr(traza, "showlegend", True) is not False for traza in fig.data)
    margen_superior = 26 + 22 * lineas_titulo + (72 if es_faceta and hay_leyenda else 34 if hay_leyenda else 10)
    if hay_leyenda:
        margen_superior = max(margen_superior, 170 if es_faceta else 128)
    margen_inferior = 92 if es_faceta else 74
    margen_actual = fig.layout.margin
    margen_izquierdo = max(76, int(margen_actual.l or 0))
    margen_derecho = max(48, int(margen_actual.r or 0))
    fig.update_layout(
        template="plotly_white",
        height=altura,
        font=dict(family="Arial", size=12, color=TINTA),
        title=dict(
            text=titulo_renderizado, x=0.01, xanchor="left",
            y=0.965, yanchor="top", font=dict(size=16),
            pad=dict(t=4, b=8, l=2, r=2),
        ),
        margin=dict(
            l=margen_izquierdo if not es_tabla else 24,
            r=margen_derecho if not es_tabla else 24,
            t=margen_superior,
            b=margen_inferior,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12 if es_faceta else 1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            font=dict(size=11),
            title_font=dict(size=11),
        ),
        hoverlabel=dict(font_family="Arial"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    if not es_tabla:
        fig.update_xaxes(
            gridcolor=GRILLA, gridwidth=0.7, zerolinecolor=GRILLA,
            showline=True, linecolor="#AFC0C5", linewidth=0.8,
            automargin=True, title_standoff=14,
        )
        fig.update_yaxes(
            gridcolor=GRILLA, gridwidth=0.7, zerolinecolor=GRILLA,
            showline=False, automargin=True, title_standoff=12,
        )
    for traza in fig.data:
        if "cliponaxis" in getattr(traza, "_valid_props", set()):
            traza.update(cliponaxis=False)
    return fig


def mostrar_plotly(
    fig: go.Figure,
    titulo: str,
    nota: str,
    fuente: str,
    *,
    alto: int = 700,
) -> None:
    estilo_plotly(fig, titulo, nota, fuente, alto=alto)
    fig.show(config=config_plotly(titulo, alto=int(fig.layout.height or alto)))


def guardar_plotly_html(fig: go.Figure, ruta: Path, titulo: str, nota: str, fuente: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    estilo_plotly(fig, titulo, nota, fuente)
    fig.write_html(ruta, include_plotlyjs="cdn", config=config_plotly(titulo))


def _mime_para(ruta: Path) -> str:
    return {
        ".zip": "application/zip",
        ".csv": "text/csv;charset=utf-8",
        ".txt": "text/plain;charset=utf-8",
        ".json": "application/json",
        ".html": "text/html;charset=utf-8",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".ipynb": "application/x-ipynb+json",
    }.get(ruta.suffix.lower(), "application/octet-stream")


def panel_descargas(archivos: list[Path], titulo: str = "Descargas reproducibles") -> None:
    enlaces = []
    for ruta in archivos:
        contenido = ruta.read_bytes()
        enlaces.append(
            _enlace_descarga(contenido, ruta.name, _mime_para(ruta), ruta.name)
        )
    salida = (
        f"{CSS_TABLAS}<div class='sf-bloque'><div class='sf-subtitulo'><em>{html.escape(titulo)}</em></div>"
        f"<div class='sf-descargas'>{''.join(enlaces)}</div></div>"
    )
    display(HTML(salida))
