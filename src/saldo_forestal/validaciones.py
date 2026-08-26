"""Controles numéricos y de alcance que acompañan cada ejecución."""

from __future__ import annotations

import numpy as np
import pandas as pd


def ejecutar_controles(
    base: pd.DataFrame,
    catalogo: pd.DataFrame,
    poorter: pd.DataFrame,
    completacion: pd.DataFrame,
    evidencia_ppm: pd.DataFrame,
    local: pd.DataFrame,
    comparacion_local: pd.DataFrame,
) -> pd.DataFrame:
    filas: list[dict[str, object]] = []

    def registrar(control: str, condicion: bool, detalle: str) -> None:
        filas.append(
            {
                "control": control,
                "estado": "Cumple" if bool(condicion) else "Revisar",
                "detalle": detalle,
            }
        )

    registrar("Unidades en la base", len(base) == 342, f"{len(base)} unidades")
    registrar(
        "Municipios en la base",
        int(base["tipo_unidad"].eq("Municipio").sum()) == 340,
        f"{int(base['tipo_unidad'].eq('Municipio').sum())} municipios",
    )
    registrar(
        "Unidades lacustres documentadas",
        int(base["tipo_unidad"].ne("Municipio").sum()) == 2,
        "Lago de Amatitlán y lago de Atitlán",
    )
    registrar(
        "Identidad N = B - R",
        np.allclose(
            base["perdida_neta_ha"],
            base["perdida_bruta_ha"] - base["recuperacion_bruta_ha"],
            atol=1e-8,
            rtol=0,
        ),
        "Verificación por fila",
    )
    registrar(
        "Pérdida bruta nacional",
        np.isclose(base["perdida_bruta_ha"].sum(), 244_394.56984238, atol=1e-6),
        f"{base['perdida_bruta_ha'].sum():,.8f} ha",
    )
    registrar(
        "Recuperación nacional",
        np.isclose(base["recuperacion_bruta_ha"].sum(), 191_658.14331302, atol=1e-6),
        f"{base['recuperacion_bruta_ha'].sum():,.8f} ha",
    )
    registrar(
        "Regiones de referencia de rho20",
        len(catalogo) == 5,
        f"{len(catalogo)} regiones",
    )
    registrar(
        "Municipios con proporción a veinte años",
        len(poorter) == 172,
        f"{len(poorter)} municipios",
    )
    registrar(
        "Intervalo de recuperación ponderada ordenado",
        (poorter["saldo_ponderado_inferior_ha"] <= poorter["saldo_ponderado_superior_ha"]).all(),
        "Límite inferior ≤ límite superior",
    )
    registrar(
        "Completación nacional",
        len(completacion) == len(base),
        f"{len(completacion)} unidades conservadas",
    )
    registrar(
        "Saldo ponderado nacional inferior",
        np.isclose(completacion["saldo_ponderado_inferior_ha"].sum(), 116_473.23156616, atol=1e-6),
        f"{completacion['saldo_ponderado_inferior_ha'].sum():,.8f} ha",
    )
    registrar(
        "Saldo ponderado nacional superior",
        np.isclose(completacion["saldo_ponderado_superior_ha"].sum(), 123_988.02784436, atol=1e-6),
        f"{completacion['saldo_ponderado_superior_ha'].sum():,.8f} ha",
    )
    registrar(
        "Series estructurales PPM",
        int(evidencia_ppm["series_multitemporales"].sum()) == 55,
        f"{int(evidencia_ppm['series_multitemporales'].sum())} series",
    )
    registrar("Municipios de la aplicación local", len(local) == 13, f"{len(local)} municipios")
    registrar(
        "Soporte común de recuperación ponderada y manglar",
        comparacion_local["rho20_min"].notna().all() and len(comparacion_local) == 13,
        "Los trece municipios locales pertenecen al dominio de aplicación",
    )
    registrar(
        "No aditividad de los métodos",
        set(local["codigo"]) <= set(poorter["codigo"]),
        "La aplicación local está contenida en el dominio de recuperación y solo se compara",
    )
    controles = pd.DataFrame(filas)
    if controles["estado"].eq("Revisar").any():
        fallidos = controles.loc[controles["estado"].eq("Revisar"), "control"].tolist()
        raise AssertionError(f"Fallaron controles de calidad: {fallidos}")
    return controles
