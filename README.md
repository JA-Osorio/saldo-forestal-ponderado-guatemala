# Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala

[![Datos: CC BY 4.0](https://img.shields.io/badge/datos-CC%20BY%204.0-1682FC.svg)](LICENSE)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-2EA44F.svg)](LICENSE_CODE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22119074.svg)](https://doi.org/10.5281/zenodo.22119074)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/main/04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb)

Este repositorio presenta el material suplementario en línea para reproducir y
examinar los cálculos de deforestación bruta, recuperación de cobertura,
pérdida neta y saldo forestal ponderado en Guatemala durante 2016–2020. La
dinámica de cobertura procede del [Instituto Nacional de Bosques (INAB) y del
Consejo Nacional de Áreas Protegidas (CONAP)](https://sig.inab.gob.gt/portal/apps/storymaps/stories/eac535d7b61a47f7b12a9b81eb9c15b6); el paquete documenta los datos,
los parámetros, las operaciones intermedias y los resultados nacionales,
departamentales y municipales.

El cuaderno ejecutado permite seguir la secuencia del cálculo sin instalar
software. El script maestro reconstruye las tablas, las figuras, el cuaderno y
el paquete de resultados a partir de los insumos documentados. El repositorio
funciona como suplemento metodológico y computacional del análisis realizado.

> [!WARNING]
> **La dinámica de cobertura forestal es reportada por INAB y CONAP. El saldo
> ponderado, la completación nacional, la valoración indicativa y las
> trayectorias son cálculos del autor y no constituyen estadísticas oficiales.**

> [!NOTE]
> La *proporción de regeneración equivalente* es el factor aplicado a la
> recuperación de cobertura. En este ejercicio se parametriza con la
> recuperación relativa de biomasa aérea observada a los veinte años en los
> sitios de referencia de Poorter et al. (2016); no representa la edad ni el
> porcentaje de hectáreas regeneradas en cada municipio.

## Autor

| Autor | Afiliación | ORCID |
|---|---|---|
| [Juan Alejandro Osorio](https://github.com/JA-Osorio) | IARNA, Universidad Rafael Landívar | [0009-0001-4260-772X](https://orcid.org/0009-0001-4260-772X) |

Los roles y responsabilidades se documentan en
[`creditos.txt`](creditos.txt).

## Qué contiene

| Componente | Contenido | Acceso directo |
|---|---|---|
| Fuentes y trazabilidad | Insumos preservados, registro de fuentes y asignación municipio–grupo–sitio | [`00_trazabilidad_fuentes/`](00_trazabilidad_fuentes/) |
| Metodología | Definiciones, parámetros, reglas de asignación, fórmulas y límites | [`01_metodologia/`](01_metodologia/) |
| Resultados y diccionario | Tablas nacionales, departamentales y municipales y definición de variables | [`02_resultados_y_diccionario/`](02_resultados_y_diccionario/) |
| Reproducción | Paquete Python, script maestro, generador y cuaderno ejecutado | [`04_reproduccion_python/`](04_reproduccion_python/) |
| Verificación | Pruebas, controles, manifiestos y huellas de los resultados | [`05_verificacion/`](05_verificacion/) |

## Accesos rápidos

| Objetivo | Archivo recomendado | Uso |
|---|---|---|
| Consultar el suplemento metodológico | [`cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb`](04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb) | Seguir datos, fórmulas, resultados, tablas y figuras con el código oculto de inicio |
| Consultar el resultado nacional | [`resultados_forestales_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_forestales_guatemala_2016_2020.csv) | Comparar pérdida bruta, recuperación, pérdida neta y saldo ponderado |
| Examinar los 340 municipios | [`resultados_reportados_inab_conap_municipios_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_reportados_inab_conap_municipios_guatemala_2016_2020.csv) | Revisar las magnitudes reportadas por INAB y CONAP por municipio |
| Examinar los 172 municipios ponderados | [`resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv) | Consultar grupo territorial, proporción aplicada y saldo municipal |
| Entender los grupos territoriales | [`asignacion_grupos_territoriales_proporcion_regeneracion_equivalente.csv`](02_resultados_y_diccionario/asignacion_grupos_territoriales_proporcion_regeneracion_equivalente.csv) | Consultar criterios, códigos, sitios equivalentes, límites, puntos medios y aplicación |
| Auditar los 342 registros | [`trazabilidad_municipio_grupo_territorial_guatemala_2016_2020.csv`](00_trazabilidad_fuentes/trazabilidad_municipio_grupo_territorial_guatemala_2016_2020.csv) | Buscar cada unidad, su regla de pertenencia, grupo y estado de aplicación |
| Consultar los sitios de referencia | [`trazabilidad_grupo_sitio_proporcion_regeneracion_equivalente.csv`](00_trazabilidad_fuentes/trazabilidad_grupo_sitio_proporcion_regeneracion_equivalente.csv) | Ver los sitios, valores publicados y reglas usadas para formar cada intervalo |
| Interpretar las variables | [`diccionario_variables.csv`](02_resultados_y_diccionario/diccionario_variables.csv) | Consultar definición, unidad, dominio y fórmula de cada campo |
| Reconstruir todos los resultados | [`reproducir_saldo_forestal_guatemala.py`](04_reproduccion_python/reproducir_saldo_forestal_guatemala.py) | Ejecutar la cadena completa y generar el paquete determinista |

## Resultados principales

INAB y CONAP reportan resultados para los 340 municipios de Guatemala y dos
unidades lacustres, los lagos de Amatitlán y Atitlán. Las cifras siguientes
son acumuladas para 2016–2020.

| Resultado | Hectáreas |
|---|---:|
| Pérdida bruta reportada | 244,394.57 |
| Recuperación de cobertura reportada | 191,658.14 |
| Pérdida neta reportada por INAB y CONAP | 52,736.43 |
| Saldo ponderado en los 172 municipios del dominio | 99,593.41–107,108.21 |
| Saldo ponderado nacional con completación conservadora | 116,473.23–123,988.03 |

La completación nacional aplica la proporción de regeneración equivalente a
los 172 municipios incluidos en las cinco listas territoriales y conserva el
cálculo reportado de pérdida neta en los otros 168 municipios. Las dos
unidades lacustres permanecen en los agregados de la fuente y no reciben una
proporción municipal.

### Estado de reproducción

[![Validación automática](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml/badge.svg?branch=main)](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml)
[![Python 3.11–3.13](https://img.shields.io/badge/Python-3.11%E2%80%933.13-3776AB.svg)](https://www.python.org/)

Las pruebas verifican los agregados reportados, la asignación de los 340
municipios, los cinco intervalos, la aplicación fila por fila, los resultados
publicados y la integridad de los manifiestos. La verificación computacional
garantiza que el procedimiento puede repetirse; no sustituye una validación
ecológica de las hectáreas recuperadas dentro de cada municipio.

## Cuaderno visor

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/main/04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb)

El [cuaderno visor](04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb)
es el suplemento metodológico ejecutado. Presenta la fuente, las operaciones,
la asignación territorial, las proporciones, los resultados y las descargas en
la misma secuencia en que se reproducen. El código está oculto de inicio, pero
puede desplegarse para auditar cada cálculo.

El cuaderno carga los productos del script maestro y permite volver a ejecutar
la cadena dentro de Google Colab. No reemplaza al reproductor: el punto de
entrada canónico para reconstruir el conjunto completo es
[`reproducir_saldo_forestal_guatemala.py`](04_reproduccion_python/reproducir_saldo_forestal_guatemala.py).

## Reproductor

Se requiere Python 3.11, 3.12 o 3.13.

### Linux, macOS o Git Bash

```bash
git clone https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git
cd saldo-forestal-ponderado-guatemala
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python 04_reproduccion_python/reproducir_saldo_forestal_guatemala.py
python -m pytest -q
```

### Windows (CMD)

```bat
git clone https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git
cd saldo-forestal-ponderado-guatemala
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python 04_reproduccion_python\reproducir_saldo_forestal_guatemala.py
python -m pytest -q
```

La ejecución reconstruye las tablas, el cuaderno y el paquete
`build/resultados_saldo_forestal_guatemala.zip`. Los parámetros del entorno se
encuentran en [`pyproject.toml`](pyproject.toml) y
[`requirements.txt`](04_reproduccion_python/requirements.txt).

## Estructura del repositorio

```text
.
├── 00_trazabilidad_fuentes/       # fuentes, insumos y tablas de asignación
├── 01_metodologia/                # método, parámetros, fórmulas y alcance
├── 02_resultados_y_diccionario/   # resultados publicados y diccionario
├── 04_reproduccion_python/        # reproductor, paquete Python y cuaderno
├── 05_verificacion/               # pruebas, controles y manifiestos
├── CITATION.cff                   # metadatos para citar el repositorio
├── LICENSE                        # datos y documentación: CC BY 4.0
├── LICENSE_CODE                   # código: MIT
├── .zenodo.json                   # metadatos del depósito archivado
├── codemeta.json                  # metadatos legibles por máquina
├── como_citar.txt                 # referencia bibliográfica de la versión
└── creditos.txt                   # autoría y responsabilidades
```

El [`manifiesto_archivos.txt`](05_verificacion/manifiesto_archivos.txt)
registra el tamaño y la huella SHA-256 de los archivos del paquete. Los
materiales de fuente primaria conservan sus condiciones de uso originales.

## Metodología y alcance

### Datos reportados por INAB y CONAP

Para cada unidad territorial, INAB y CONAP reportan pérdida bruta de cobertura
`B` y recuperación de cobertura `R`. La pérdida neta reportada se reproduce
como:

```text
Pérdida neta reportada = pérdida bruta − recuperación de cobertura
N = B − R
```

La operación descuenta una hectárea de recuperación por cada hectárea de
pérdida. Es un balance de cambios de cobertura y no una medición de biomasa,
composición o madurez del bosque recuperado.

### Proporción de regeneración equivalente

La *proporción de regeneración equivalente* `ρ` pondera la recuperación de
cobertura antes de restarla. En esta aplicación, sus valores proceden de la
recuperación relativa de biomasa aérea que los sitios de [Poorter et al.
(2016)](https://doi.org/10.1038/nature16512)
alcanzan después de veinte años respecto de su bosque maduro de referencia.

```text
Saldo forestal ponderado = pérdida bruta
                           − (proporción de regeneración equivalente
                              × recuperación de cobertura)
H = B − ρR
```

Una proporción de 60 % reconoce 60 ha equivalentes por cada 100 ha reportadas
como recuperación. No significa que 60 % de las hectáreas municipales tenga
veinte años ni que haya recuperado una condición ecológica integral.

### Asignación a grupos territoriales de referencia

Los municipios se asignan mediante cinco listas explícitas y disjuntas de
códigos. La pertenencia a una lista determina la asignación computacional; el
criterio territorial documenta por qué esos municipios se trataron como un
grupo. Después, cada grupo se vincula con territorios científicos de
referencia para obtener el intervalo de la proporción de regeneración
equivalente. Las dos decisiones se muestran por separado en la tabla.

| Grupo territorial en Guatemala | Criterio territorial de agrupación | Territorios de referencia y fundamento de la vinculación | Intervalo de la proporción | Municipios |
|---|---|---|---:|---:|
| Norte y centro de Petén | Municipios del norte y centro de Petén tratados como plataforma kárstica y bosque tropical estacional sobre calizas | Quintana Roo y Yucatán, México; plataforma kárstica, estacionalidad y bosques tropicales estacionales | 66.4–66.7 % | 9 |
| Sur de Petén y vertiente norte | Municipios del sur de Petén y de la vertiente norte agrupados por continuidad territorial con la Franja Transversal del Norte | Chajul, México; bosques húmedos de tierras bajas del ámbito de la Selva Maya | 59.4 % | 32 |
| Tierras bajas húmedas del Caribe y del Pacífico | Caribe, Izabal, costa y bocacosta húmeda del Pacífico y Costa Cuca | Barro Colorado, Panamá, y Sarapiquí, Costa Rica; bosques tropicales húmedos de baja altitud y alta disponibilidad de agua | 59.3–76.6 % | 62 |
| Oriente de Guatemala | Municipios de Chiquimula, Jalapa y Jutiapa tratados como un bloque de bosque tropical estacional | El Ocote, México, y Santa Rosa, Costa Rica; bosques tropicales estacionales | 33.6–84.9 % | 35 |
| Valles secos interiores, Motagua y Salamá–Chixoy | Municipios de los valles secos interiores, el valle del Motagua y el sistema Salamá–Chixoy | Sitios secos de Bolivia, Brasil y México; mayor déficit hídrico y recuperación generalmente más lenta | 25.0–65.0 % | 34 |

La vinculación documenta el parámetro aplicado; no demuestra equivalencia
ecológica de cada hectárea municipal. Los 168 municipios cuyos códigos no
pertenecen a estas listas quedan fuera del dominio de aplicación y conservan
la pérdida neta reportada por INAB y CONAP.

### Alcance y limitaciones

- La recuperación reportada no contiene edad, origen, biomasa, composición,
  permanencia ni condición sucesional.
- Las listas territoriales reproducen la asignación utilizada en el cálculo;
  no son una regionalización oficial de Guatemala.
- La completación nacional no extrapola proporciones a los 168 municipios
  situados fuera del dominio documentado.
- La valoración económica es una transferencia indicativa y no una cuenta de
  ecosistemas completa.
- La aplicación local de manglar utiliza evidencia estructural distinta; se
  compara con la ponderación nacional y no se suma a ella.

La [metodología completa](01_metodologia/metodologia_saldo_forestal_guatemala_2016_2020.md),
el [procedimiento didáctico de asignación](01_metodologia/procedimiento_asignacion_grupos_territoriales.md),
las [reglas legibles por máquina](01_metodologia/reglas_asignacion_grupos_territoriales.json)
y el [registro de fuentes](00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv)
documentan las decisiones, los parámetros y sus límites.

## Citación

Use la opción *Cite this repository* de GitHub o consulte
[`CITATION.cff`](CITATION.cff). La referencia de la publicación archivada es:

> Osorio, J. A. (2026). *Deforestación bruta, recuperación y saldo forestal
> ponderado en Guatemala* (Versión 1.0.0) [Material suplementario en línea]. Instituto
> de Investigación en Ciencias Naturales y Tecnología, Universidad Rafael
> Landívar. https://doi.org/10.5281/zenodo.22119075

El DOI [`10.5281/zenodo.22119075`](https://doi.org/10.5281/zenodo.22119075)
identifica la versión 1.0.0. El DOI conceptual
[`10.5281/zenodo.22119074`](https://doi.org/10.5281/zenodo.22119074) dirige a
la versión más reciente.

Al reutilizar una tabla, figura o conjunto de resultados, conserve la
referencia del suplemento y la atribución a las fuentes primarias indicada en
el producto correspondiente.

## Licencias

| Material | Licencia |
|---|---|
| Datos derivados, documentación, tablas, figuras y contenido del cuaderno | [CC BY 4.0](LICENSE) |
| Código Python y celdas ejecutables originales | [MIT](LICENSE_CODE) |

Las fuentes primarias y los materiales de terceros conservan sus derechos y
condiciones de uso de origen; este repositorio no los relicencia.

---

*Versión 1.0.0 · Guatemala · cobertura forestal 2016–2020*
