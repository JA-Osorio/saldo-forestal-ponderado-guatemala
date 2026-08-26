"""Indicadores físicos y ponderación de la recuperación."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .constantes import (
    ESTADO_RECUPERACION_ELEGIBLE,
    PERIODO_BASE_ANIOS,
    TIPO_MUNICIPIO,
    TOLERANCIA,
)


def saldo_neto(perdida_bruta, recuperacion):
    """Identidad institucional de cambio de cobertura: N = B - R."""

    return perdida_bruta - recuperacion


def saldo_ponderado(perdida_bruta, recuperacion, proporcion):
    """Saldo con recuperación ponderada: H(rho) = B - rho R."""

    return perdida_bruta - proporcion * recuperacion


def intervalo_saldo_ponderado(
    perdida_bruta,
    recuperacion,
    proporcion_min,
    proporcion_max,
):
    """Devuelve límites inferior y superior correctamente orientados.

    Una proporción mayor reconoce más recuperación y, por tanto, produce el
    límite inferior de pérdida ponderada.
    """

    inferior = saldo_ponderado(perdida_bruta, recuperacion, proporcion_max)
    superior = saldo_ponderado(perdida_bruta, recuperacion, proporcion_min)
    return inferior, superior


def clasificar_saldo(valor: float, tolerancia: float = TOLERANCIA) -> str:
    if valor > tolerancia:
        return "Pérdida"
    if valor < -tolerancia:
        return "Ganancia"
    return "Equilibrio"


def clasificar_intervalo(
    inferior: float,
    superior: float,
    tolerancia: float = TOLERANCIA,
) -> str:
    if inferior > tolerancia:
        return "Pérdida"
    if superior < -tolerancia:
        return "Ganancia"
    return "Indeterminado"


def proporcion_critica(perdida_bruta, recuperacion):
    """Proporción B/R necesaria para que el saldo ponderado sea cero."""

    b = np.asarray(perdida_bruta, dtype=float)
    r = np.asarray(recuperacion, dtype=float)
    resultado = np.full(np.broadcast_shapes(b.shape, r.shape), np.nan, dtype=float)
    np.divide(b, r, out=resultado, where=r > 0)
    return float(resultado) if resultado.ndim == 0 else resultado


def calcular_resultados_institucionales(base: pd.DataFrame) -> pd.DataFrame:
    resultado = base.copy()
    resultado["perdida_neta_calculada_ha"] = saldo_neto(
        resultado["perdida_bruta_ha"], resultado["recuperacion_bruta_ha"]
    )
    if not np.allclose(
        resultado["perdida_neta_ha"],
        resultado["perdida_neta_calculada_ha"],
        atol=TOLERANCIA,
        rtol=0,
    ):
        raise ValueError("La base no reproduce la identidad institucional.")
    for columna in ("perdida_bruta_ha", "recuperacion_bruta_ha", "perdida_neta_ha"):
        resultado[f"{columna.removesuffix('_ha')}_anual_ha"] = (
            resultado[columna] / PERIODO_BASE_ANIOS
        )
    resultado["clasificacion_institucional"] = resultado["perdida_neta_ha"].map(
        clasificar_saldo
    )
    return resultado


def agregar_institucional(
    resultados: pd.DataFrame,
    grupos: str | Iterable[str] | None = None,
) -> pd.DataFrame:
    columnas = ["perdida_bruta_ha", "recuperacion_bruta_ha", "perdida_neta_ha"]
    if grupos is None:
        agregado = resultados[columnas].sum().to_frame().T
        agregado.insert(0, "ambito", "Guatemala")
    else:
        llaves = [grupos] if isinstance(grupos, str) else list(grupos)
        agregado = resultados.groupby(llaves, dropna=False, as_index=False)[columnas].sum()
        agregado.insert(len(llaves), "unidades", resultados.groupby(llaves, dropna=False).size().values)
    for columna in columnas:
        agregado[f"{columna.removesuffix('_ha')}_anual_ha"] = agregado[columna] / PERIODO_BASE_ANIOS
    return agregado


def calcular_resultados_poorter(
    base: pd.DataFrame,
    dominio: pd.DataFrame,
    catalogo: pd.DataFrame,
) -> pd.DataFrame:
    """Reconstruye los 172 resultados municipales sin usar tablas derivadas."""

    elegibles = dominio.loc[
        dominio["estado_dominio"].eq(ESTADO_RECUPERACION_ELEGIBLE),
        ["codigo", "region_id", "proporcion_region_id"],
    ].copy()
    if len(elegibles) != 172 or elegibles["codigo"].duplicated().any():
        raise ValueError("El dominio de aplicación debe contener 172 códigos municipales únicos.")
    asignacion = elegibles.merge(
        catalogo,
        on="proporcion_region_id",
        how="left",
        validate="many_to_one",
    )
    if asignacion[["rho20_min", "rho20_max"]].isna().any().any():
        raise ValueError("Hay municipios elegibles sin proporciones de recuperación.")

    columnas_base = [
        "cod_dep",
        "depto",
        "codigo",
        "municipio",
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "tipo_unidad",
    ]
    resultado = base.loc[base["tipo_unidad"].eq(TIPO_MUNICIPIO), columnas_base].merge(
        asignacion,
        on="codigo",
        how="inner",
        validate="one_to_one",
    )
    if len(resultado) != 172:
        raise ValueError("El cruce del dominio no conservó los 172 municipios elegibles.")

    inferior, superior = intervalo_saldo_ponderado(
        resultado["perdida_bruta_ha"],
        resultado["recuperacion_bruta_ha"],
        resultado["rho20_min"],
        resultado["rho20_max"],
    )
    resultado["saldo_ponderado_inferior_ha"] = inferior
    resultado["saldo_ponderado_superior_ha"] = superior
    resultado["saldo_ponderado_central_ha"] = saldo_ponderado(
        resultado["perdida_bruta_ha"],
        resultado["recuperacion_bruta_ha"],
        resultado["rho20_central"],
    )
    resultado["clasificacion_institucional"] = resultado["perdida_neta_ha"].map(
        clasificar_saldo
    )
    resultado["clasificacion_ponderada"] = resultado.apply(
        lambda fila: clasificar_intervalo(
            fila["saldo_ponderado_inferior_ha"],
            fila["saldo_ponderado_superior_ha"],
        ),
        axis=1,
    )
    resultado["brecha_ponderacion_inferior_ha"] = (
        resultado["saldo_ponderado_inferior_ha"] - resultado["perdida_neta_ha"]
    )
    resultado["brecha_ponderacion_superior_ha"] = (
        resultado["saldo_ponderado_superior_ha"] - resultado["perdida_neta_ha"]
    )
    resultado["rho_critica"] = proporcion_critica(
        resultado["perdida_bruta_ha"], resultado["recuperacion_bruta_ha"]
    )
    return resultado.sort_values(["cod_dep", "codigo"]).reset_index(drop=True)


def agregar_poorter(
    resultados: pd.DataFrame,
    grupos: str | Iterable[str] | None = None,
) -> pd.DataFrame:
    columnas = [
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "saldo_ponderado_inferior_ha",
        "saldo_ponderado_superior_ha",
    ]
    if grupos is None:
        agregado = resultados[columnas].sum().to_frame().T
        agregado.insert(0, "ambito", "Dominio de aplicación")
        agregado.insert(1, "municipios", len(resultados))
        return agregado
    llaves = [grupos] if isinstance(grupos, str) else list(grupos)
    agregado = resultados.groupby(llaves, dropna=False, as_index=False)[columnas].sum()
    tamanos = resultados.groupby(llaves, dropna=False).size().rename("municipios").reset_index()
    return agregado.merge(tamanos, on=llaves, validate="one_to_one")


def completar_nacional_conservador(
    base: pd.DataFrame,
    resultados_poorter: pd.DataFrame,
) -> pd.DataFrame:
    """Aplica rho20 dentro del dominio de recuperación y rho=1 fuera de él.

    El resultado conserva las 342 unidades de la base. No extrapola las
    proporciones al altiplano, bosques montanos ni unidades lacustres.
    """

    por_codigo = resultados_poorter.set_index("codigo")
    resultado = base.copy()
    resultado["rho_aplicada_min"] = resultado["codigo"].map(por_codigo["rho20_min"])
    resultado["rho_aplicada_max"] = resultado["codigo"].map(por_codigo["rho20_max"])
    resultado["en_dominio_recuperacion"] = resultado["rho_aplicada_min"].notna()
    resultado[["rho_aplicada_min", "rho_aplicada_max"]] = resultado[
        ["rho_aplicada_min", "rho_aplicada_max"]
    ].fillna(1.0)
    inferior, superior = intervalo_saldo_ponderado(
        resultado["perdida_bruta_ha"],
        resultado["recuperacion_bruta_ha"],
        resultado["rho_aplicada_min"],
        resultado["rho_aplicada_max"],
    )
    resultado["saldo_ponderado_inferior_ha"] = inferior
    resultado["saldo_ponderado_superior_ha"] = superior
    if len(resultado) != 342:
        raise ValueError("La completación nacional debe conservar 342 unidades.")
    if not (
        resultado["saldo_ponderado_inferior_ha"]
        <= resultado["saldo_ponderado_superior_ha"] + TOLERANCIA
    ).all():
        raise ValueError("Los límites de la completación nacional están invertidos.")
    return resultado


def resumir_nacional_conservador(completacion: pd.DataFrame) -> pd.DataFrame:
    columnas = [
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "saldo_ponderado_inferior_ha",
        "saldo_ponderado_superior_ha",
    ]
    resumen = completacion[columnas].sum().to_frame().T
    resumen.insert(0, "ambito", "Guatemala, completación conservadora")
    resumen.insert(1, "unidades", len(completacion))
    resumen.insert(
        2,
        "municipios_con_proporcion",
        int(completacion["en_dominio_recuperacion"].sum()),
    )
    for columna in columnas:
        resumen[f"{columna.removesuffix('_ha')}_anual_ha"] = resumen[columna] / PERIODO_BASE_ANIOS
    return resumen


def construir_comparacion_nacional(
    base: pd.DataFrame,
    completacion: pd.DataFrame,
) -> pd.DataFrame:
    """Tabla larga de los tres resultados forestales nacionales."""

    bruto = float(base["perdida_bruta_ha"].sum())
    neto = float(base["perdida_neta_ha"].sum())
    ponderado_inf = float(completacion["saldo_ponderado_inferior_ha"].sum())
    ponderado_sup = float(completacion["saldo_ponderado_superior_ha"].sum())
    filas = [
        {
            "regla": "Deforestación bruta",
            "proporcion_recuperacion": "0",
            "resultado_inferior_ha": bruto,
            "resultado_superior_ha": bruto,
        },
        {
            "regla": "Saldo ponderado por recuperación",
            "proporcion_recuperacion": "rho20 dentro del dominio; 1 fuera",
            "resultado_inferior_ha": ponderado_inf,
            "resultado_superior_ha": ponderado_sup,
        },
        {
            "regla": "Pérdida neta institucional",
            "proporcion_recuperacion": "1",
            "resultado_inferior_ha": neto,
            "resultado_superior_ha": neto,
        },
    ]
    resultado = pd.DataFrame(filas)
    resultado["resultado_inferior_anual_ha"] = resultado["resultado_inferior_ha"] / PERIODO_BASE_ANIOS
    resultado["resultado_superior_anual_ha"] = resultado["resultado_superior_ha"] / PERIODO_BASE_ANIOS
    return resultado
