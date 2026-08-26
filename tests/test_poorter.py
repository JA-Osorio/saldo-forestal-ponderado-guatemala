import numpy as np

from saldo_forestal.indicadores import agregar_poorter, construir_comparacion_nacional


def test_dominio_y_agregados_poorter(poorter):
    assert len(poorter) == 172
    assert poorter["proporcion_region_id"].nunique() == 5
    assert poorter["depto"].nunique() == 19
    assert np.isclose(poorter["perdida_bruta_ha"].sum(), 220_307.71209084)
    assert np.isclose(poorter["recuperacion_bruta_ha"].sum(), 184_451.10275683)
    assert np.isclose(poorter["saldo_ponderado_inferior_ha"].sum(), 99_593.41437081)
    assert np.isclose(poorter["saldo_ponderado_superior_ha"].sum(), 107_108.21064901)


def test_agregacion_departamental_reconcilia(poorter):
    dep = agregar_poorter(poorter, ["cod_dep", "depto"])
    assert len(dep) == 19
    for columna in [
        "perdida_bruta_ha",
        "recuperacion_bruta_ha",
        "perdida_neta_ha",
        "saldo_ponderado_inferior_ha",
        "saldo_ponderado_superior_ha",
    ]:
        assert np.isclose(dep[columna].sum(), poorter[columna].sum())


def test_clasificaciones_poorter(poorter):
    assert poorter["clasificacion_institucional"].value_counts().to_dict() == {
        "Pérdida": 104,
        "Ganancia": 66,
        "Equilibrio": 2,
    }
    assert poorter["clasificacion_ponderada"].value_counts().to_dict() == {
        "Pérdida": 119,
        "Ganancia": 42,
        "Indeterminado": 11,
    }


def test_completacion_nacional(completacion):
    assert len(completacion) == 342
    assert completacion["en_dominio_recuperacion"].sum() == 172
    assert np.isclose(completacion["saldo_ponderado_inferior_ha"].sum(), 116_473.23156616)
    assert np.isclose(completacion["saldo_ponderado_superior_ha"].sum(), 123_988.02784436)


def test_comparacion_nacional_tres_reglas(base, completacion):
    comparacion = construir_comparacion_nacional(base, completacion)
    assert comparacion["regla"].tolist() == [
        "Deforestación bruta",
        "Saldo ponderado por recuperación",
        "Pérdida neta institucional",
    ]
    assert len(comparacion) == 3
