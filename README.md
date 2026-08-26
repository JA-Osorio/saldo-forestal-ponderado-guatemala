# Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala

[![Validar publicación](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml/badge.svg)](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml)
[![DOI](https://zenodo.org/badge/1347880444.svg)](https://doi.org/10.5281/zenodo.22119074)
[![Datos: CC BY 4.0](https://img.shields.io/badge/datos-CC%20BY%204.0-1682FC.svg)](LICENSE)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-2EA44F.svg)](LICENSE_CODE)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/v1.0.0/notebooks/saldo_forestal_ponderado_guatemala.ipynb)

Repositorio reproducible de una investigación sobre deforestación bruta, recuperación reportada y pérdida neta en Guatemala. El proyecto examina cuánto cambia el diagnóstico forestal cuando la ganancia de cobertura deja de tratarse como sustituto completo e inmediato de la pérdida.

## Qué hace este repositorio

El punto de partida es la identidad institucional:

\[
N_i=B_i-R_i,
\]

donde \(B_i\) es la pérdida bruta, \(R_i\) la recuperación reportada —medida como ganancia de cobertura forestal— y \(N_i\) la pérdida neta. La resta expresa un balance de cobertura; el análisis distingue ese balance de una equivalencia ecológica inmediata.

El repositorio reproduce primero ese resultado y luego calcula:

\[
H_i(\rho)=B_i-\rho_iR_i,
\]

donde \(\rho\) representa la proporción de recuperación reconocida en cada caso de cálculo:

- `0`: deforestación bruta;
- `1`: pérdida neta institucional;
- `rho20`: proporciones de recuperación de biomasa a veinte años derivadas de Poorter et al. (2016), aplicadas únicamente dentro del dominio analítico definido.

La pregunta central no es si \(B-R\) está bien restado, sino cuánto cambia el diagnóstico cuando la ganancia de cobertura no se considera equivalente, desde el primer momento, al bosque perdido.

## Resultados de referencia

La base 2016–2020 contiene 340 municipios y dos unidades lacustres no municipales. Con los valores decimales de la fuente:

| Resultado acumulado 2016–2020 | Hectáreas |
|---|---:|
| Pérdida bruta | 244,394.57 |
| Recuperación reportada (ganancia de cobertura) | 191,658.14 |
| Pérdida neta institucional | 52,736.43 |
| Saldo ponderado nacional conservador | 116,473.23–123,988.03 |

El dominio construido para aplicar las proporciones regionales comprende 172 municipios. Dentro de ese dominio, el saldo ponderado es 99,593.41–107,108.21 ha, frente a una pérdida neta de 35,856.61 ha. Para completar el resultado nacional sin extrapolar esas proporciones a ecosistemas incompatibles, fuera del dominio se mantiene el cálculo institucional \(\rho=1\).

La cifra de 244,394.57 ha corresponde al acumulado del periodo 2016–2020; no debe describirse como deforestación ocurrida únicamente en 2020.

## Alcance y límites

- Las proporciones de recuperación de biomasa a veinte años proceden de Poorter et al. (2016); no describen la edad de la ganancia de cobertura reportada para 2016–2020.
- La completación nacional es deliberadamente conservadora: aplica `rho20` dentro de 172 municipios elegibles y \(\rho=1\) fuera del dominio.
- El módulo de manglar es una aproximación local para trece municipios con evidencia estructural del portal del INAB. Los flujos \(B\) y \(R\) siguen siendo cambios forestales municipales totales, no pérdidas o ganancias específicas de cobertura de manglar.
- La recuperación ponderada y la aproximación local de manglar se comparan sobre un soporte territorial superpuesto; nunca se suman.
- La transferencia de valores monetarios es indicativa y permite contrastar los resultados físicos y los escenarios. No constituye una cuenta de ecosistemas completa ni una valoración compatible por sí sola con el SCAE-CE.
- Los costos de Eta e Iota y otros costos ambientales se presentan como contexto no aditivo; no se atribuyen causalmente a la deforestación.

Una explicación completa está en [alcance y limitaciones](docs/alcance_y_limitaciones.md).

## Organización

```text
.
├── notebooks/                 # cuaderno público reproducible
├── src/saldo_forestal/        # módulos de lectura, cálculo, valoración y gráficos
├── data/
│   ├── raw/                   # insumos preservados
│   ├── processed/             # productos reconstruidos por el pipeline
│   └── metadata/              # registro de fuentes y diccionario de variables
├── outputs/
│   ├── tables/                # tablas listas para reutilización
│   └── downloads/             # manifiesto y paquete integral
├── docs/                      # metodología, fuentes y guía de reproducción
├── scripts/run_pipeline.py    # punto único de ejecución
└── tests/                     # controles automáticos
```

Los archivos de `data/processed/` y `outputs/` son productos derivados. La cadena analítica se inicia en `data/raw/` y se reconstruye con el script maestro.

## Reproducción local

Requiere Python 3.11, 3.12 o 3.13. Desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
pytest -q
```

La ejecución genera tablas en `data/processed/` y `outputs/tables/`, registra los parámetros monetarios efectivamente aplicados y crea un ZIP autocontenido cuyo manifiesto verifica cada miembro salvo el propio manifiesto.

Consulte [reproducción](docs/reproduccion.md) para el procedimiento completo y [diccionario](docs/diccionario.md) para la semántica de las variables.

## Cuaderno

El cuaderno principal se ubica en `notebooks/saldo_forestal_ponderado_guatemala.ipynb`. Su diseño editorial sigue un criterio estricto: cada celda de resultado presenta un solo objeto semántico —tabla, figura, mapa o panel— con título y unidad; la celda Markdown contigua reúne la nota, la interpretación y la atribución de fuentes.

[Abrir la versión 1.0.0 en Google Colab](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/v1.0.0/notebooks/saldo_forestal_ponderado_guatemala.ipynb)

## Fuentes principales

- INAB, dinámica de cobertura forestal 2016–2020 y tabla municipal del portal SIG-INAB.
- Poorter et al. (2016), *Biomass resilience of Neotropical secondary forests*, y sus datos en Dryad.
- INAB, evidencia de parcelas permanentes del ecosistema manglar.
- Sandoval García, Gálvez Ruano y Pinillos Cifuentes (2022), *Bosques*.
- Banco Mundial et al. (2021), *Cuenta de ecosistemas de Guatemala* (2.ª ed.).
- CEPAL, evaluación de los efectos e impactos de Eta e Iota en Guatemala.

El [registro de fuentes](data/metadata/registro_fuentes.csv) identifica URL, uso, archivos relacionados y limitaciones. La discusión metodológica está en [fuentes](docs/fuentes.md).

## Referencia general

La referencia general del cuaderno es:

> Osorio, J. A. (2026). *Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala* (Versión 1.0.0) [Cuaderno reproducible]. Instituto de Investigación en Ciencias Naturales y Tecnología, Universidad Rafael Landívar. https://doi.org/10.5281/zenodo.22119075

Al reutilizar una tabla, figura o conjunto de resultados, conserve esta referencia y la atribución a las fuentes primarias indicada en la salida correspondiente.

## Licencias

- Datos, documentación, tablas y figuras: [Creative Commons Atribución 4.0 Internacional](LICENSE) (`CC BY 4.0`). Debe mantenerse la atribución a las fuentes originales; esta licencia no amplía derechos sobre materiales de terceros.
- Código fuente, scripts y pruebas: [MIT](LICENSE_CODE).

## Autoría institucional

[Juan Alejandro Osorio](https://github.com/JA-Osorio) — IARNA, Universidad Rafael Landívar — [ORCID 0009-0001-4260-772X](https://orcid.org/0009-0001-4260-772X)
