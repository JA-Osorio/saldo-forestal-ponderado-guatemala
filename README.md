# Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala

[![Datos: CC BY 4.0](https://img.shields.io/badge/datos-CC%20BY%204.0-1682FC.svg)](LICENSE)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-2EA44F.svg)](LICENSE_CODE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22119074.svg)](https://doi.org/10.5281/zenodo.22119074)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/v1.0.0/notebooks/saldo_forestal_ponderado_guatemala.ipynb)

Este repositorio publica un compendio reproducible sobre pérdida bruta,
recuperación reportada y pérdida neta de cobertura forestal en Guatemala para
2016–2020. Reconstruye los resultados institucionales y examina cuánto cambia
el diagnóstico cuando la recuperación se pondera mediante proporciones de
biomasa a veinte años.

El paquete reúne datos documentados, resultados nacionales, departamentales y
municipales, una nota metodológica en cuaderno, valoración económica
indicativa, trayectorias 2026–2035 y una aplicación local para municipios con
evidencia estructural de manglar.

> [!WARNING]
> Los datos de cobertura proceden de fuentes oficiales, pero la ponderación de
> la recuperación, la completación nacional, la valoración y las trayectorias
> son resultados analíticos. No constituyen estadísticas oficiales.

> [!NOTE]
> La aplicación de manglar es una aproximación local y no se suma al saldo
> ponderado nacional. Cada tabla y figura identifica sus fuentes primarias.

## Autor

| Autor | Afiliación | ORCID |
|---|---|---|
| [Juan Alejandro Osorio](https://github.com/JA-Osorio) | IARNA, Universidad Rafael Landívar | [0009-0001-4260-772X](https://orcid.org/0009-0001-4260-772X) |

## Qué contiene

| Componente | Contenido | Acceso directo |
|---|---|---|
| Cuaderno metodológico | Fórmulas, resultados, figuras, tablas e interpretación | [`notebooks/saldo_forestal_ponderado_guatemala.ipynb`](notebooks/saldo_forestal_ponderado_guatemala.ipynb) |
| Datos de entrada | Insumos preservados para reconstruir el análisis | [`data/raw/`](data/raw/) |
| Resultados y diccionario | Tablas derivadas, variables y registro de fuentes | [`data/processed/`](data/processed/) y [`data/metadata/`](data/metadata/) |
| Metodología | Definiciones, secuencia de cálculo, alcance y limitaciones | [`docs/metodologia.md`](docs/metodologia.md) |
| Reproducción | Script maestro y módulos de lectura, cálculo y validación | [`scripts/run_pipeline.py`](scripts/run_pipeline.py) y [`src/saldo_forestal/`](src/saldo_forestal/) |
| Verificación | Pruebas automatizadas, controles y manifiesto SHA-256 | [`tests/`](tests/) y [`manifiesto_archivos.txt`](manifiesto_archivos.txt) |
| Paquete integral | Tablas, metadatos, fuentes y guía de citación en un ZIP | [`resultados_saldo_forestal_guatemala.zip`](outputs/downloads/resultados_saldo_forestal_guatemala.zip) |

## Accesos rápidos

| Objetivo | Recurso recomendado | Uso |
|---|---|---|
| Explorar sin instalar software | [Cuaderno en Google Colab](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/v1.0.0/notebooks/saldo_forestal_ponderado_guatemala.ipynb) | Recorrer la nota metodológica y consultar 33 resultados ejecutados |
| Consultar el balance nacional | [`resultados_forestales_nacionales.csv`](outputs/tables/resultados_forestales_nacionales.csv) | Comparar pérdida bruta, recuperación, pérdida neta y saldo ponderado |
| Analizar los 340 municipios | [`resultados_institucionales_municipales.csv`](outputs/tables/resultados_institucionales_municipales.csv) | Examinar la desagregación institucional completa |
| Consultar el dominio de ponderación | [`resultados_recuperacion_municipales.csv`](outputs/tables/resultados_recuperacion_municipales.csv) | Revisar los 172 municipios elegibles y sus intervalos |
| Revisar la aplicación de manglar | [`resumen_mangle_local.csv`](outputs/tables/resumen_mangle_local.csv) | Consultar la evidencia estructural local sin agregarla al resultado nacional |
| Entender variables y unidades | [`diccionario_variables.csv`](data/metadata/diccionario_variables.csv) | Identificar definiciones, dominios y convenciones |
| Auditar las fuentes | [`registro_fuentes.csv`](data/metadata/registro_fuentes.csv) | Revisar procedencia, uso, acceso y limitaciones |
| Descargar todos los resultados | [`resultados_saldo_forestal_guatemala.zip`](outputs/downloads/resultados_saldo_forestal_guatemala.zip) | Obtener 35 archivos con manifiesto interno |

## Resultados principales

La base 2016–2020 contiene 340 municipios y dos unidades lacustres no
municipales. Los resultados acumulados, conservando los decimales de la
fuente, son los siguientes:

| Resultado acumulado 2016–2020 | Hectáreas |
|---|---:|
| Pérdida bruta | 244,394.57 |
| Recuperación reportada | 191,658.14 |
| Pérdida neta institucional | 52,736.43 |
| Saldo ponderado nacional conservador | 116,473.23–123,988.03 |

El dominio construido para aplicar las proporciones regionales comprende 172
municipios. Dentro de ese dominio, el saldo ponderado es
99,593.41–107,108.21 ha, frente a una pérdida neta de 35,856.61 ha. Fuera del
dominio se mantiene el cálculo institucional para evitar extrapolar las
proporciones a ecosistemas incompatibles.

La pérdida bruta de 244,394.57 ha corresponde al acumulado 2016–2020; no debe
describirse como deforestación ocurrida únicamente en 2020.

## Método y alcance

El cálculo comienza con el balance institucional de cobertura forestal:

$$
N_i = B_i - R_i
$$

Se lee como: *la pérdida neta es igual a la pérdida bruta menos la recuperación
reportada*.

| Símbolo | Significado | Unidad |
|:---:|---|---:|
| $i$ | Municipio o unidad territorial analizada | — |
| $B_i$ | Pérdida bruta de cobertura forestal | ha |
| $R_i$ | Recuperación reportada como ganancia de cobertura forestal | ha |
| $N_i$ | Pérdida neta institucional | ha |
| $\rho_i$ | Proporción utilizada para ponderar la recuperación | Adimensional, entre 0 y 1 |
| $\rho_{20,i}$ | Proporción de biomasa recuperada a veinte años | Adimensional, entre 0 y 1 |
| $H_i(\rho_i)$ | Saldo forestal ponderado | ha |

Esta identidad expresa un balance de cobertura. Por sí sola no implica que una
hectárea recuperada tenga de inmediato la misma biomasa que una hectárea de
bosque perdida.

Para incorporar esa diferencia, la recuperación se multiplica por una
proporción antes de restarla:

$$
H_i(\rho_i) = B_i - \rho_i R_i
$$

El término $\rho_i R_i$ es la parte de la recuperación que se descuenta de la
pérdida bruta. La operación puede leerse como: *pérdida bruta menos
recuperación ponderada*. Como $\rho_i$ no tiene unidad, el resultado continúa
expresándose en hectáreas.

Los tres casos usados en el cuaderno son:

| Caso | Sustitución en la fórmula | Interpretación |
|---|---:|---|
| Sin descontar la recuperación | $H_i(0)=B_i$ | El saldo coincide con la pérdida bruta. |
| Balance institucional | $H_i(1)=B_i-R_i=N_i$ | La recuperación se descuenta por completo. |
| Recuperación ponderada a veinte años | $H_i(\rho_{20,i})=B_i-\rho_{20,i}R_i$ | Solo se descuenta la proporción de biomasa recuperada a veinte años. |

Las proporciones $\rho_{20,i}$ se derivan de Poorter et al. (2016) y se aplican
únicamente dentro del dominio documentado.

La [nota metodológica](docs/metodologia.md) presenta las fórmulas de
completación nacional, valoración, trayectorias y aplicación local de manglar.
El [alcance y las limitaciones](docs/alcance_y_limitaciones.md) explican los
supuestos y las fronteras de interpretación.

## Estado de calidad

[![Validación automática](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml/badge.svg?branch=main)](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml)
[![Python 3.11–3.13](https://img.shields.io/badge/Python-3.11%E2%80%933.13-3776AB.svg)](https://www.python.org/)

| Componente verificado | Evidencia | Estado |
|---|---:|---|
| Tablas listas para reutilización | 28 | Reconstruidas por el pipeline |
| Cuaderno público | 82 celdas y 33 resultados | Ejecutado sin errores |
| Pruebas automatizadas | 58 | Aprobadas |
| Inventario público | 112 huellas SHA-256 | Verificadas |
| Paquete integral | 35 archivos | Manifiesto interno conforme |

La integración continua instala un entorno limpio, reconstruye los resultados,
ejecuta el cuaderno con Jupyter y conserva la evidencia de la validación.

## Cuaderno en Google Colab

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/v1.0.0/notebooks/saldo_forestal_ponderado_guatemala.ipynb)

El cuaderno es simultáneamente una nota metodológica y una entrada didáctica a
los resultados. Presenta las fórmulas utilizadas, 16 figuras, 16 tablas y un
recuadro. El código permanece oculto en la lectura normal, pero está disponible
para auditoría y reproducción.

El enlace de Colab está fijado a la etiqueta inmutable `v1.0.0`, de modo que la
ejecución corresponde a la versión archivada en Zenodo.

## Reproducir el análisis

Requiere Python 3.11, 3.12 o 3.13.

### Linux, macOS o Git Bash

```bash
git clone https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git
cd saldo-forestal-ponderado-guatemala
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
python -m pytest -q
```

### Windows

```bat
git clone https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git
cd saldo-forestal-ponderado-guatemala
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts\run_pipeline.py
python -m pytest -q
```

La ejecución genera las tablas de `data/processed/` y `outputs/tables/`,
registra los parámetros monetarios aplicados y reconstruye el ZIP integral.
Las instrucciones ampliadas están en [`docs/reproduccion.md`](docs/reproduccion.md).

## Estructura del repositorio

```text
.
├── data/
│   ├── raw/                   # insumos preservados
│   ├── processed/             # productos derivados
│   └── metadata/              # fuentes y diccionario
├── docs/                      # método, alcance y reproducción
├── notebooks/                 # cuaderno público ejecutado
├── outputs/
│   ├── tables/                # tablas listas para reutilización
│   └── downloads/             # paquete integral y manifiesto
├── scripts/                   # puntos de ejecución y construcción
├── src/saldo_forestal/        # módulos analíticos
└── tests/                     # controles automatizados
```

Los productos de `data/processed/` y `outputs/` se reconstruyen a partir de
`data/raw/`. El [`manifiesto_archivos.txt`](manifiesto_archivos.txt) registra
el tamaño y la huella SHA-256 de cada artefacto público.

## Fuentes y trazabilidad

Las fuentes principales son el INAB y el CONAP para la dinámica de cobertura
forestal 2016–2020; Poorter et al. (2016) y el depósito asociado en Dryad para
las proporciones de recuperación de biomasa; el INAB para la evidencia de
parcelas permanentes de manglar; y fuentes oficiales y académicas para la
valoración y los escenarios.

El [`registro_fuentes.csv`](data/metadata/registro_fuentes.csv) documenta URL,
fecha de acceso, uso analítico, archivos relacionados y limitaciones. La guía
de [`fuentes`](docs/fuentes.md) desarrolla la atribución y las condiciones de
reutilización.

## Limitaciones

- Las proporciones a veinte años no describen la edad de la recuperación
  reportada para 2016–2020.
- La completación nacional aplica $\rho_{20}$ solo dentro de 172 municipios
  elegibles y mantiene $\rho=1$ fuera del dominio.
- Los flujos municipales usados en la aplicación de manglar no son cambios
  exclusivos de cobertura de manglar.
- La recuperación ponderada y la aproximación local de manglar se comparan,
  pero no se suman.
- La transferencia de valores monetarios es indicativa y no constituye una
  cuenta de ecosistemas completa.
- Los costos de Eta e Iota se presentan como contexto no aditivo y no se
  atribuyen causalmente a la deforestación.

## Citación

Use la opción *Cite this repository* de GitHub o consulte
[`CITATION.cff`](CITATION.cff). La referencia de la versión archivada es:

> Osorio, J. A. (2026). *Deforestación bruta, recuperación y saldo forestal
> ponderado en Guatemala* (Versión 1.0.0) [Cuaderno reproducible]. Instituto de
> Investigación en Ciencias Naturales y Tecnología, Universidad Rafael
> Landívar. https://doi.org/10.5281/zenodo.22119075

El DOI [`10.5281/zenodo.22119075`](https://doi.org/10.5281/zenodo.22119075)
identifica la versión 1.0.0. El DOI conceptual
[`10.5281/zenodo.22119074`](https://doi.org/10.5281/zenodo.22119074) dirige a
la versión más reciente. La cita dentro del texto es *(Osorio, 2026)*.

Al reutilizar una tabla, figura o conjunto de resultados, conserve esta
referencia y la atribución a las fuentes primarias indicada en la salida.

## Licencias

| Material | Licencia |
|---|---|
| Datos derivados, documentación, tablas, figuras y contenido del cuaderno | [CC BY 4.0](LICENSE) |
| Código Python y celdas ejecutables originales | [MIT](LICENSE_CODE) |

Las fuentes primarias y los materiales de terceros conservan sus derechos y
condiciones de uso de origen; este repositorio no los relicencia.

---

*Versión 1.0.0 · Guatemala · cobertura forestal 2016–2020*
