"""Trayectorias 2026–2035 con pérdida y recuperación modeladas por separado."""

from __future__ import annotations

import pandas as pd

from .constantes import (
    HORIZONTE_ESCENARIOS_ANIOS,
    HORIZONTE_SERVICIOS_ANIOS,
    PERIODO_BASE_ANIOS,
    TASA_DESCUENTO_CENTRAL,
    VALOR_UNITARIO_2026_GTQ_HA_ANIO,
)
from .valoracion import valorar_flujo, valor_presente_trayectoria


def aplicar_escenario(
    perdida_bruta,
    recuperacion,
    proporcion,
    multiplicador_perdida_bruta: float,
    multiplicador_recuperacion: float,
):
    if multiplicador_perdida_bruta < 0 or multiplicador_recuperacion < 0:
        raise ValueError("Los multiplicadores de escenario no pueden ser negativos.")
    return (
        multiplicador_perdida_bruta * perdida_bruta
        - proporcion * multiplicador_recuperacion * recuperacion
    )


def validar_escenarios(escenarios: pd.DataFrame) -> None:
    requeridas = {
        "escenario",
        "multiplicador_perdida_bruta",
        "multiplicador_recuperacion",
    }
    if faltan := requeridas.difference(escenarios.columns):
        raise ValueError(f"Faltan columnas de escenarios: {sorted(faltan)}")
    if (
        escenarios[["multiplicador_perdida_bruta", "multiplicador_recuperacion"]]
        .lt(0)
        .any()
        .any()
    ):
        raise ValueError("Los multiplicadores de escenario no pueden ser negativos.")
    restauracion = escenarios["escenario"].str.contains("restaur", case=False, na=False)
    if (restauracion & escenarios["multiplicador_recuperacion"].le(1)).any():
        raise ValueError(
            "Un escenario llamado restauración debe modificar positivamente la recuperación."
        )


def calcular_escenarios_nacionales(
    completacion_nacional: pd.DataFrame,
    escenarios: pd.DataFrame,
    horizonte_escenarios: int = HORIZONTE_ESCENARIOS_ANIOS,
) -> pd.DataFrame:
    """Cruza tres reglas de reporte con trayectorias físicas explícitas."""

    validar_escenarios(escenarios)
    b = completacion_nacional["perdida_bruta_ha"]
    r = completacion_nacional["recuperacion_bruta_ha"]
    rho_min = completacion_nacional["proporcion_regeneracion_equivalente_aplicada_min"]
    rho_max = completacion_nacional["proporcion_regeneracion_equivalente_aplicada_max"]
    filas: list[dict[str, float | str]] = []
    for _, escenario in escenarios.iterrows():
        mb = float(escenario["multiplicador_perdida_bruta"])
        mr = float(escenario["multiplicador_recuperacion"])
        valores = {
            "Deforestación bruta": ((mb * b).sum(), (mb * b).sum()),
            "Saldo ponderado por recuperación": (
                aplicar_escenario(b, r, rho_max, mb, mr).sum(),
                aplicar_escenario(b, r, rho_min, mb, mr).sum(),
            ),
            "Pérdida neta reportada": (
                aplicar_escenario(b, r, 1.0, mb, mr).sum(),
                aplicar_escenario(b, r, 1.0, mb, mr).sum(),
            ),
        }
        for regla, (inferior, superior) in valores.items():
            filas.append(
                {
                    "escenario": escenario["escenario"],
                    "regla": regla,
                    "multiplicador_perdida_bruta": mb,
                    "multiplicador_recuperacion": mr,
                    "resultado_inferior_ha_periodo_base": float(inferior),
                    "resultado_superior_ha_periodo_base": float(superior),
                    "resultado_inferior_anual_ha": float(inferior) / PERIODO_BASE_ANIOS,
                    "resultado_superior_anual_ha": float(superior) / PERIODO_BASE_ANIOS,
                }
            )
    resultado = pd.DataFrame(filas)
    if horizonte_escenarios <= 0:
        raise ValueError("El horizonte de escenarios debe ser positivo.")
    resultado["resultado_inferior_decada_ha"] = (
        resultado["resultado_inferior_anual_ha"] * horizonte_escenarios
    )
    resultado["resultado_superior_decada_ha"] = (
        resultado["resultado_superior_anual_ha"] * horizonte_escenarios
    )
    return resultado


def valorar_escenarios(
    resultados: pd.DataFrame,
    valor_unitario: float = VALOR_UNITARIO_2026_GTQ_HA_ANIO,
    tasa: float = TASA_DESCUENTO_CENTRAL,
    horizonte_servicios: int = HORIZONTE_SERVICIOS_ANIOS,
    numero_cohortes: int = HORIZONTE_ESCENARIOS_ANIOS,
) -> pd.DataFrame:
    valorados = resultados.copy()
    for limite in ("inferior", "superior"):
        ha = valorados[f"resultado_{limite}_anual_ha"]
        valorados[f"flujo_anual_{limite}_gtq"] = valorar_flujo(ha, valor_unitario)
        valorados[f"vp_decada_{limite}_gtq"] = [
            valor_presente_trayectoria(
                [max(float(x), 0.0)] * numero_cohortes,
                valor_unitario=valor_unitario,
                tasa=tasa,
                horizonte_servicios=horizonte_servicios,
            )
            for x in ha
        ]
    return valorados


def construir_trayectorias(
    resultados: pd.DataFrame,
    anio_inicial: int = 2026,
    horizonte_escenarios: int = HORIZONTE_ESCENARIOS_ANIOS,
) -> pd.DataFrame:
    if horizonte_escenarios <= 0:
        raise ValueError("El horizonte de escenarios debe ser positivo.")
    filas: list[dict[str, float | int | str]] = []
    for _, resultado in resultados.iterrows():
        for paso in range(1, horizonte_escenarios + 1):
            filas.append(
                {
                    "anio": anio_inicial + paso - 1,
                    "escenario": resultado["escenario"],
                    "regla": resultado["regla"],
                    "acumulado_inferior_ha": resultado["resultado_inferior_anual_ha"] * paso,
                    "acumulado_superior_ha": resultado["resultado_superior_anual_ha"] * paso,
                }
            )
    return pd.DataFrame(filas)


def construir_trayectorias_monetarias(
    resultados: pd.DataFrame,
    anio_inicial: int = 2026,
    valor_unitario: float = VALOR_UNITARIO_2026_GTQ_HA_ANIO,
    tasa: float = TASA_DESCUENTO_CENTRAL,
    horizonte_servicios: int = HORIZONTE_SERVICIOS_ANIOS,
    horizonte_escenarios: int = HORIZONTE_ESCENARIOS_ANIOS,
) -> pd.DataFrame:
    """Valor presente acumulado al inicio de 2026 para cohortes sucesivas."""

    if horizonte_escenarios <= 0:
        raise ValueError("El horizonte de escenarios debe ser positivo.")
    filas: list[dict[str, float | int | str]] = []
    for _, resultado in resultados.iterrows():
        inferior = max(float(resultado["resultado_inferior_anual_ha"]), 0.0)
        superior = max(float(resultado["resultado_superior_anual_ha"]), 0.0)
        for paso in range(1, horizonte_escenarios + 1):
            filas.append(
                {
                    "anio": anio_inicial + paso - 1,
                    "escenario": resultado["escenario"],
                    "regla": resultado["regla"],
                    "vp_acumulado_inferior_gtq": valor_presente_trayectoria(
                        [inferior] * paso,
                        valor_unitario=valor_unitario,
                        tasa=tasa,
                        horizonte_servicios=horizonte_servicios,
                    ),
                    "vp_acumulado_superior_gtq": valor_presente_trayectoria(
                        [superior] * paso,
                        valor_unitario=valor_unitario,
                        tasa=tasa,
                        horizonte_servicios=horizonte_servicios,
                    ),
                }
            )
    return pd.DataFrame(filas)
