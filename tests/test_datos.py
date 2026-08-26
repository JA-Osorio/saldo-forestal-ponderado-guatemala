import numpy as np


def test_universo_nacional(base):
    assert len(base) == 342
    assert base["tipo_unidad"].eq("Municipio").sum() == 340
    assert base["tipo_unidad"].ne("Municipio").sum() == 2


def test_codigos_municipales_unicos_y_enteros(base):
    municipios = base.loc[base["tipo_unidad"].eq("Municipio")]
    assert str(base["codigo"].dtype) == "Int64"
    assert municipios["codigo"].notna().all()
    assert not municipios["codigo"].duplicated().any()


def test_identidad_por_unidad(base):
    observado = base["perdida_bruta_ha"] - base["recuperacion_bruta_ha"]
    assert np.allclose(base["perdida_neta_ha"], observado, atol=1e-8, rtol=0)


def test_totales_nacionales(base):
    assert np.isclose(base["perdida_bruta_ha"].sum(), 244_394.56984238)
    assert np.isclose(base["recuperacion_bruta_ha"].sum(), 191_658.14331302)
    assert np.isclose(base["perdida_neta_ha"].sum(), 52_736.42652936)


def test_catalogo_poorter(catalogo):
    assert len(catalogo) == 5
    assert catalogo["proporcion_region_id"].is_unique
    assert (catalogo["rho20_min"] <= catalogo["rho20_central"]).all()
    assert (catalogo["rho20_central"] <= catalogo["rho20_max"]).all()
    assert catalogo[["rho20_min", "rho20_central", "rho20_max"]].ge(0).all().all()
    assert catalogo[["rho20_min", "rho20_central", "rho20_max"]].le(1).all().all()
