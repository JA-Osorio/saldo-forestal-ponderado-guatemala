"""Valoración indicativa con separación estricta entre flujo y activo."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .constantes import (
    HORIZONTE_ESCENARIOS_ANIOS,
    HORIZONTE_SERVICIOS_ANIOS,
    TASA_DESCUENTO_CENTRAL,
    VALOR_UNITARIO_2026_GTQ_HA_ANIO,
)


def factor_anualidad(tasa: float, horizonte: int) -> float:
    if horizonte < 0:
        raise ValueError("El horizonte no puede ser negativo.")
    if tasa < 0:
        raise ValueError("La tasa de descuento no puede ser negativa.")
    if np.isclose(tasa, 0):
        return float(horizonte)
    return float((1 - (1 + tasa) ** (-horizonte)) / tasa)


def anualizar(hectareas_periodo, duracion_anios: float = 4):
    if duracion_anios <= 0:
        raise ValueError("La duración del periodo debe ser positiva.")
    return hectareas_periodo / duracion_anios


def valorar_flujo(
    hectareas_anuales,
    valor_unitario: float = VALOR_UNITARIO_2026_GTQ_HA_ANIO,
):
    """Valor anual no generado; no es un valor presente."""

    return hectareas_anuales * valor_unitario


def valor_presente_cohorte(
    flujo_anual,
    tasa: float = TASA_DESCUENTO_CENTRAL,
    horizonte_servicios: int = HORIZONTE_SERVICIOS_ANIOS,
):
    """Valor del activo asociado con una cohorte anual de pérdida."""

    return flujo_anual * factor_anualidad(tasa, horizonte_servicios)


def valor_presente_trayectoria(
    hectareas_por_cohorte: Iterable[float],
    valor_unitario: float = VALOR_UNITARIO_2026_GTQ_HA_ANIO,
    tasa: float = TASA_DESCUENTO_CENTRAL,
    horizonte_servicios: int = HORIZONTE_SERVICIOS_ANIOS,
) -> float:
    """VP al inicio del horizonte para cohortes observadas en t=1,...,T."""

    cohortes = np.asarray(list(hectareas_por_cohorte), dtype=float)
    if (cohortes < 0).any():
        # Las ganancias físicas pueden valorarse en ejercicios separados, pero
        # el costo de pérdida patrimonial no debe cambiar silenciosamente de signo.
        raise ValueError("Las cohortes de pérdida valoradas no pueden ser negativas.")
    tiempos = np.arange(1, len(cohortes) + 1, dtype=float)
    vp_unitario = valor_unitario * factor_anualidad(tasa, horizonte_servicios)
    return float(np.sum(cohortes * vp_unitario / (1 + tasa) ** tiempos))


def valorar_comparacion_nacional(
    comparacion: pd.DataFrame,
    valor_unitario: float = VALOR_UNITARIO_2026_GTQ_HA_ANIO,
    tasa: float = TASA_DESCUENTO_CENTRAL,
    horizonte_servicios: int = HORIZONTE_SERVICIOS_ANIOS,
    horizonte_escenarios: int = HORIZONTE_ESCENARIOS_ANIOS,
) -> pd.DataFrame:
    """Valora bruta, neta y ponderada sin mezclar dominios ni conceptos."""

    resultado = comparacion.copy()
    for limite in ("inferior", "superior"):
        hectareas = resultado[f"resultado_{limite}_anual_ha"]
        flujo = valorar_flujo(hectareas, valor_unitario)
        resultado[f"flujo_anual_{limite}_gtq"] = flujo
        resultado[f"vp_cohorte_{limite}_gtq"] = valor_presente_cohorte(
            flujo, tasa, horizonte_servicios
        )
        resultado[f"vp_diez_cohortes_{limite}_gtq"] = [
            valor_presente_trayectoria(
                [ha] * horizonte_escenarios,
                valor_unitario=valor_unitario,
                tasa=tasa,
                horizonte_servicios=horizonte_servicios,
            )
            for ha in hectareas
        ]
    resultado["valor_unitario_gtq_ha_anio"] = valor_unitario
    resultado["tasa_descuento"] = tasa
    resultado["horizonte_servicios_anios"] = horizonte_servicios
    resultado["numero_cohortes"] = horizonte_escenarios
    return resultado


def sensibilidad_valor_presente(
    comparacion: pd.DataFrame,
    tasas: Iterable[float] = (0.02, 0.04, 0.05),
    valor_unitario: float = VALOR_UNITARIO_2026_GTQ_HA_ANIO,
    horizonte_servicios: int = HORIZONTE_SERVICIOS_ANIOS,
) -> pd.DataFrame:
    filas: list[dict[str, float | str]] = []
    for _, fila in comparacion.iterrows():
        for tasa in tasas:
            registro: dict[str, float | str] = {"regla": fila["regla"], "tasa": tasa}
            for limite in ("inferior", "superior"):
                flujo = valorar_flujo(fila[f"resultado_{limite}_anual_ha"], valor_unitario)
                registro[f"vp_cohorte_{limite}_gtq"] = valor_presente_cohorte(
                    flujo, tasa, horizonte_servicios
                )
            filas.append(registro)
    return pd.DataFrame(filas)
