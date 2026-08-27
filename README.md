# Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala

[![Datos: CC BY 4.0](https://img.shields.io/badge/datos-CC%20BY%204.0-1682FC.svg)](LICENSE)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-2EA44F.svg)](LICENSE_CODE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22119074.svg)](https://doi.org/10.5281/zenodo.22119074)
[![Validación automática](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml/badge.svg?branch=main)](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/main/04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb)

Este repositorio publica un compendio reproducible sobre pérdida bruta,
recuperación reportada y pérdida neta de cobertura forestal en Guatemala para
el periodo acumulado 2016–2020. También muestra cuánto cambia el diagnóstico
cuando la recuperación se pondera mediante proporciones de biomasa aérea
recuperada a veinte años.

La correspondencia entre municipios y regiones de referencia se documenta
como **correspondencia territorial experta codificada**. Es una clasificación
analítica reproducible, no una regionalización oficial ni una validación
ecológica de las hectáreas recuperadas.

> [!WARNING]
> Los datos de cobertura proceden de fuentes oficiales, pero la ponderación de
> la recuperación, la completación nacional, la valoración y las trayectorias
> son resultados analíticos. No constituyen estadísticas oficiales.

> [!NOTE]
> La aplicación de manglar es una aproximación local y no se suma al saldo
> ponderado nacional. Cada producto identifica sus fuentes primarias.

## Autor

| Autor | Afiliación | ORCID |
|---|---|---|
| [Juan Alejandro Osorio](https://github.com/JA-Osorio) | IARNA, Universidad Rafael Landívar | [0009-0001-4260-772X](https://orcid.org/0009-0001-4260-772X) |

## Resultado verificado de la correspondencia territorial

El universo contiene 342 unidades. Las listas explícitas de códigos asignan
172 municipios a cinco regiones; una regla residual mantiene fuera del dominio
los 168 municipios restantes y una regla independiente identifica las dos
unidades lacustres.

| Resultado | Unidades |
|---|---:|
| Municipios incluidos | 172 |
| Municipios excluidos | 168 |
| Unidades lacustres no municipales | 2 |
| `REG-PET-N` | 9 |
| `REG-PET-FTN` | 32 |
| `REG-TB-HUM` | 62 |
| `REG-ORI-EST` | 35 |
| `REG-SEC-MOT` | 34 |

Cada una de las 342 filas conserva el código territorial, la región, la regla
aplicada, el criterio operativo, las fuentes y el estado de revisión. La
clasificación y los intervalos se pueden regenerar sin leer los resultados
finales congelados.

## Accesos rápidos

| Objetivo | Recurso |
|---|---|
| Explorar el análisis | [Cuaderno en Google Colab](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/main/04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb) |
| Consultar el balance nacional | [`02_resultados_y_diccionario/resultados_forestales_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_forestales_guatemala_2016_2020.csv) |
| Examinar los 340 municipios | [`02_resultados_y_diccionario/resultados_institucionales_municipios_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_institucionales_municipios_guatemala_2016_2020.csv) |
| Revisar los 172 municipios incluidos | [`02_resultados_y_diccionario/resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv) |
| Auditar la asignación territorial | [`00_trazabilidad_fuentes/trazabilidad_municipio_region_guatemala_2016_2020.csv`](00_trazabilidad_fuentes/trazabilidad_municipio_region_guatemala_2016_2020.csv) |
| Auditar regiones, sitios e intervalos | [`00_trazabilidad_fuentes/trazabilidad_region_sitio_recuperacion_biomasa_20_anios.csv`](00_trazabilidad_fuentes/trazabilidad_region_sitio_recuperacion_biomasa_20_anios.csv) |
| Leer el procedimiento | [`01_metodologia/procedimiento_correspondencia_territorial_experta_codificada.md`](01_metodologia/procedimiento_correspondencia_territorial_experta_codificada.md) |
| Revisar la brecha ecológica | [`01_metodologia/brechas_validacion_ecologica.md`](01_metodologia/brechas_validacion_ecologica.md) |
| Entender las variables | [`02_resultados_y_diccionario/diccionario_variables.csv`](02_resultados_y_diccionario/diccionario_variables.csv) |
| Auditar las fuentes | [`00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv`](00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv) |

## Resultados principales

La base 2016–2020 contiene 340 municipios y dos unidades lacustres no
municipales. Los acumulados, conservando los decimales de la fuente, son:

| Resultado acumulado 2016–2020 | Hectáreas |
|---|---:|
| Pérdida bruta | 244,394.57 |
| Recuperación reportada | 191,658.14 |
| Pérdida neta institucional | 52,736.43 |
| Saldo ponderado nacional conservador | 116,473.23–123,988.03 |

Dentro del dominio de 172 municipios, el saldo ponderado es
99,593.41–107,108.21 ha, frente a una pérdida neta de 35,856.61 ha. Fuera del
dominio se mantiene el cálculo institucional para evitar extrapolar las
proporciones a condiciones sin correspondencia documentada.

La pérdida bruta de 244,394.57 ha corresponde al acumulado 2016–2020; no debe
describirse como deforestación ocurrida únicamente en 2020.

## Método y fórmulas

Para cada unidad territorial $i$, la identidad institucional es:

$$
N_i=B_i-R_i,
$$

donde $B_i$ es la pérdida bruta, $R_i$ la recuperación reportada y $N_i$ la
pérdida neta institucional, todas en hectáreas. Un valor positivo representa
pérdida.

La recuperación ponderada se calcula como:

$$
H_i(\rho_i)=B_i-\rho_iR_i,
$$

donde $\rho_i$ es adimensional. Los tres casos publicados son
$H_i(0)=B_i$, $H_i(1)=N_i$ y
$H_i(\rho_{20,i})=B_i-\rho_{20,i}R_i$.

Para un intervalo $[\rho_{20,i}^{\min},\rho_{20,i}^{\max}]$, los límites se
orientan por la monotonía de $H_i$:

$$
H_i^{\inf}=B_i-\rho_{20,i}^{\max}R_i,
\qquad
H_i^{\sup}=B_i-\rho_{20,i}^{\min}R_i.
$$

Los valores regionales provienen de sitios publicados por
Poorter et al. (2016) y del conjunto asociado en Dryad. Cuatro intervalos se
obtienen directamente de los valores publicados por sitio. En `REG-SEC-MOT`,
el mínimo y el máximo numéricos son 0.254 y 0.645; el redondeo exterior en
incrementos de 0.05 produce exactamente $[0.25,0.65]$.

La completación nacional conserva $\rho=1$ fuera del dominio:

$$
H_{GT}^{\inf}
=\sum_{i\in P}(B_i-\rho_{20,i}^{\max}R_i)
+\sum_{i\notin P}(B_i-R_i),
$$

$$
H_{GT}^{\sup}
=\sum_{i\in P}(B_i-\rho_{20,i}^{\min}R_i)
+\sum_{i\notin P}(B_i-R_i),
$$

donde $P$ contiene los 172 municipios incluidos. La metodología completa está
en
[`01_metodologia/metodologia_saldo_forestal_guatemala_2016_2020.md`](01_metodologia/metodologia_saldo_forestal_guatemala_2016_2020.md)
y sus límites de interpretación en
[`01_metodologia/alcance_y_limitaciones.md`](01_metodologia/alcance_y_limitaciones.md).

## Estado de trazabilidad

La reproducibilidad computacional está resuelta para la clasificación y los
intervalos:

- las listas de códigos y la regla residual están versionadas como `1.0.0`;
- la partición es 172 municipios incluidos, 168 excluidos y dos unidades
  lacustres;
- los conteos regionales son 9/32/62/35/34;
- trece porcentajes se reproducen desde el CSV público de Dryad a una decimal;
- Quintana Roo se verifica en la tabla ampliada del artículo porque no aparece
  en ese CSV;
- las reglas y las fuentes regeneran la clasificación sin depender de los
  archivos finales usados como referencia de regresión.

La brecha pendiente es ecológica: todavía se requiere contrastar las hectáreas
de recuperación 2016–2020 con elevación, tipo de bosque, estacionalidad y otras
variables espaciales antes de afirmar comparabilidad empírica con los sitios de
referencia. Los insumos y cruces propuestos están documentados en
[`00_trazabilidad_fuentes/fuentes_validacion_ecologica.md`](00_trazabilidad_fuentes/fuentes_validacion_ecologica.md).

## Reproducir el análisis

Requiere Python 3.11, 3.12 o 3.13.

```bash
git clone https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala.git
cd saldo-forestal-ponderado-guatemala
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python 04_reproduccion_python/reproducir_saldo_forestal_guatemala.py
python -m pytest -q
```

En Windows, active el entorno con `.venv\Scripts\activate`. Las instrucciones
ampliadas están en
[`04_reproduccion_python/instrucciones_reproduccion_python.md`](04_reproduccion_python/instrucciones_reproduccion_python.md).
La ejecución genera el paquete determinista en
`build/resultados_saldo_forestal_guatemala.zip`.

## Estructura del repositorio

```text
.
├── 00_trazabilidad_fuentes/       # insumos, fuentes y bitácoras
├── 01_metodologia/                # método, reglas y parámetros
├── 02_resultados_y_diccionario/   # tablas publicadas y diccionario
├── 04_reproduccion_python/        # cuaderno y cadena reproducible
├── 05_verificacion/               # pruebas, controles y manifiestos
├── CITATION.cff
├── codemeta.json
└── como_citar.txt
```

Los nombres de los archivos describen contenido, territorio y periodo; los
prefijos numéricos expresan el orden de lectura y auditoría. Los manifiestos de
`05_verificacion/` registran tamaño y huella SHA-256 de los artefactos públicos.

## Fuentes y límites de uso

Las fuentes principales son INAB y CONAP para la dinámica de cobertura
forestal 2016–2020; Poorter et al. (2016) y Dryad para las proporciones de
recuperación de biomasa; INAB, ICC y CONAP para la evidencia de parcelas de
manglar; y fuentes oficiales y académicas para valoración y escenarios.

El
[`00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv`](00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv)
documenta procedencia, acceso, uso analítico, archivos relacionados,
limitaciones y condiciones de reutilización.

- Las proporciones a veinte años no describen la edad de la recuperación
  reportada para 2016–2020.
- Las cinco regiones son construcciones analíticas y no divisiones
  administrativas u oficiales.
- Los flujos municipales usados en la aproximación de manglar no son cambios
  exclusivos de cobertura de manglar.
- La recuperación ponderada y la aproximación local de manglar se comparan,
  pero no se suman.
- La transferencia de valores monetarios es indicativa y no constituye una
  cuenta de ecosistemas completa.
- Los costos de Eta e Iota se presentan como contexto no aditivo y no se
  atribuyen causalmente a la deforestación.

## Citación

Use la opción *Cite this repository* de GitHub o consulte
[`CITATION.cff`](CITATION.cff). La referencia de la publicación archivada es:

> Osorio, J. A. (2026). *Deforestación bruta, recuperación y saldo forestal
> ponderado en Guatemala* (Versión 1.0.0) [Compendio reproducible]. Instituto
> de Investigación en Ciencias Naturales y Tecnología, Universidad Rafael
> Landívar. https://doi.org/10.5281/zenodo.22119075

El DOI [`10.5281/zenodo.22119075`](https://doi.org/10.5281/zenodo.22119075)
identifica la versión 1.0.0. El DOI conceptual
[`10.5281/zenodo.22119074`](https://doi.org/10.5281/zenodo.22119074) dirige a
la versión más reciente. El botón de Colab abre la organización vigente de la
rama `main`; la cita identifica la publicación archivada.

Al reutilizar una tabla, figura o conjunto de resultados, conserve la
referencia del compendio y la atribución a las fuentes primarias indicada en el
producto correspondiente.

## Licencias

| Material | Licencia |
|---|---|
| Datos derivados, documentación, tablas, figuras y contenido del cuaderno | [CC BY 4.0](LICENSE) |
| Código Python y celdas ejecutables originales | [MIT](LICENSE_CODE) |

Las fuentes primarias y los materiales de terceros conservan sus derechos y
condiciones de uso de origen; este repositorio no los relicencia.

---

*Versión 1.0.0 · Guatemala · cobertura forestal 2016–2020*
