"""Aproximación local para municipios con evidencia estructural de manglar."""

from __future__ import annotations

import pandas as pd

from .constantes import TIPO_MUNICIPIO
from .errores import DominiosSuperpuestosError
from .indicadores import clasificar_intervalo, intervalo_saldo_ponderado


def derivar_intervalo_estructural(evidencia: pd.DataFrame) -> dict[str, float | int]:
    """Deriva 30/55–34/55 de las trayectorias PPM comparables."""

    total = int(evidencia["series_multitemporales"].sum())
    favorables = int(evidencia["suben_carbono_y_area_basal"].sum())
    desfavorables = int(evidencia["bajan_carbono_y_area_basal"].sum())
    mixtas = int(evidencia["trayectoria_mixta"].sum())
    if total <= 0 or favorables + desfavorables + mixtas != total:
        raise ValueError("Las trayectorias estructurales PPM no reconcilian.")
    return {
        "series_multitemporales": total,
        "trayectorias_favorables": favorables,
        "trayectorias_desfavorables": desfavorables,
        "trayectorias_mixtas": mixtas,
        "proporcion_estructural_min": favorables / total,
        "proporcion_estructural_max": (favorables + mixtas) / total,
    }


def calcular_aproximacion_local(
    base: pd.DataFrame,
    evidencia: pd.DataFrame,
) -> pd.DataFrame:
    """Calcula la aproximación sobre los trece municipios del portal INAB.

    B y R continúan siendo flujos forestales municipales totales. La evidencia
    de manglar informa únicamente el intervalo estructural local; el resultado
    no es un cambio específico de cobertura de manglar.
    """

    intervalo = derivar_intervalo_estructural(evidencia)
    codigos = evidencia[["codigo_municipio"]].rename(columns={"codigo_municipio": "codigo"})
    columnas = [
        "cod_dep",
        "depto",
        "codigo",
        "municipio",
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "tipo_unidad",
    ]
    local = base.loc[base["tipo_unidad"].eq(TIPO_MUNICIPIO), columnas].merge(
        codigos,
        on="codigo",
        how="inner",
        validate="one_to_one",
    )
    if len(local) != 13:
        raise ValueError("La aproximación local debe conservar trece municipios.")
    local["proporcion_estructural_min"] = intervalo["proporcion_estructural_min"]
    local["proporcion_estructural_max"] = intervalo["proporcion_estructural_max"]
    inferior, superior = intervalo_saldo_ponderado(
        local["perdida_bruta_ha"],
        local["recuperacion_bruta_ha"],
        local["proporcion_estructural_min"],
        local["proporcion_estructural_max"],
    )
    local["saldo_estructural_inferior_ha"] = inferior
    local["saldo_estructural_superior_ha"] = superior
    local["clasificacion_estructural"] = local.apply(
        lambda fila: clasificar_intervalo(
            fila["saldo_estructural_inferior_ha"],
            fila["saldo_estructural_superior_ha"],
        ),
        axis=1,
    )
    return local.sort_values(["cod_dep", "codigo"]).reset_index(drop=True)


def comparar_metodos_locales(
    resultados_locales: pd.DataFrame,
    resultados_recuperacion: pd.DataFrame,
) -> pd.DataFrame:
    """Compara ambas aproximaciones sobre el mismo soporte de 13 municipios."""

    columnas_recuperacion = [
        "codigo",
        "proporcion_regeneracion_equivalente_min",
        "proporcion_regeneracion_equivalente_max",
        "saldo_ponderado_inferior_ha",
        "saldo_ponderado_superior_ha",
        "clasificacion_ponderada",
    ]
    comparacion = resultados_locales.merge(
        resultados_recuperacion[columnas_recuperacion],
        on="codigo",
        how="left",
        validate="one_to_one",
    )
    if len(comparacion) != 13 or comparacion["proporcion_regeneracion_equivalente_min"].isna().any():
        raise ValueError("Los trece municipios locales deben pertenecer al dominio de aplicación.")
    return comparacion


def validar_no_aditividad(
    resultados_recuperacion: pd.DataFrame,
    resultados_locales: pd.DataFrame,
) -> None:
    """Impide sumar la aplicación local a la recuperación ponderada."""

    comunes = set(resultados_recuperacion["codigo"].dropna()).intersection(
        set(resultados_locales["codigo"].dropna())
    )
    if comunes:
        raise DominiosSuperpuestosError(
            "La recuperación ponderada y la aproximación local de manglar comparten "
            f"{len(comunes)} municipios; sus resultados se comparan y no se suman."
        )


def resumir_aproximacion_local(resultados_locales: pd.DataFrame) -> pd.DataFrame:
    columnas = [
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "saldo_estructural_inferior_ha",
        "saldo_estructural_superior_ha",
    ]
    resumen = resultados_locales[columnas].sum().to_frame().T
    resumen.insert(0, "ambito", "Trece municipios con evidencia estructural de manglar")
    resumen.insert(1, "municipios", len(resultados_locales))
    return resumen
