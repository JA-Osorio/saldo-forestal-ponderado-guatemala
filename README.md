# Deforestación bruta, recuperación y saldo forestal ponderado en Guatemala

[![Datos: CC BY 4.0](https://img.shields.io/badge/datos-CC%20BY%204.0-1682FC.svg)](LICENSE)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-2EA44F.svg)](LICENSE_CODE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22119074.svg)](https://doi.org/10.5281/zenodo.22119074)
[![Validación automática](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml/badge.svg?branch=main)](https://github.com/JA-Osorio/saldo-forestal-ponderado-guatemala/actions/workflows/validar.yml)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/main/04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb)

¿Qué cambia si la recuperación de cobertura registrada entre 2016 y 2020 no
se descuenta como si hubiera restablecido inmediatamente la biomasa del bosque
perdido? Este repositorio parte de la información oficial de Guatemala y
compara la pérdida bruta, la recuperación reportada y la pérdida neta con un
saldo que pondera la recuperación mediante proporciones publicadas a veinte
años.

La pérdida neta oficial del período es 52,736.43 ha. El saldo nacional
ponderado, sin extender las proporciones a municipios que no tienen una
correspondencia territorial documentada, se sitúa entre 116,473.23 y
123,988.03 ha.

> [!WARNING]
> La dinámica de cobertura 2016–2020 procede de fuentes oficiales. La
> ponderación, la completación nacional, la valoración y las trayectorias son
> cálculos analíticos y no constituyen estadísticas oficiales.

> [!NOTE]
> La aplicación de manglar es una aproximación local separada. No se suma al
> saldo forestal ponderado nacional.

## Autor

| Autor | Afiliación | ORCID |
|---|---|---|
| [Juan Alejandro Osorio](https://github.com/JA-Osorio) | IARNA, Universidad Rafael Landívar | [0009-0001-4260-772X](https://orcid.org/0009-0001-4260-772X) |

## Comience aquí

| Si desea… | Recurso recomendado | Qué encontrará |
|---|---|---|
| Comprender el análisis paso a paso | [Cuaderno en Google Colab](https://colab.research.google.com/github/JA-Osorio/saldo-forestal-ponderado-guatemala/blob/main/04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb) | Conceptos, ejemplos, resultados nacionales y municipales, figuras y descargas |
| Consultar el resultado nacional | [`resultados_forestales_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_forestales_guatemala_2016_2020.csv) | Pérdida bruta, recuperación, pérdida neta y saldo ponderado |
| Explorar los 340 municipios | [`resultados_institucionales_municipios_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_institucionales_municipios_guatemala_2016_2020.csv) | Resultados oficiales con código, municipio y departamento |
| Examinar los 172 municipios ponderados | [`resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv`](02_resultados_y_diccionario/resultados_recuperacion_ponderada_municipios_guatemala_2016_2020.csv) | Grupo territorial, proporción aplicada y saldo municipal |
| Conocer el significado de cada variable | [`diccionario_variables.csv`](02_resultados_y_diccionario/diccionario_variables.csv) | Definición, unidad y dominio de uso |
| Revisar las reglas municipio por municipio | [`trazabilidad_municipio_region_guatemala_2016_2020.csv`](00_trazabilidad_fuentes/trazabilidad_municipio_region_guatemala_2016_2020.csv) | Las 342 unidades, la regla aplicada, el criterio y la fuente |

## Qué contiene

| Componente | Contenido | Acceso |
|---|---|---|
| Fuentes y trazabilidad | Procedencia de datos, sitios científicos y decisiones territoriales | [`00_trazabilidad_fuentes/`](00_trazabilidad_fuentes/) |
| Metodología | Conceptos, reglas, parámetros, fórmulas y limitaciones | [`01_metodologia/`](01_metodologia/) |
| Resultados | Tablas nacionales, departamentales y municipales, más el diccionario | [`02_resultados_y_diccionario/`](02_resultados_y_diccionario/) |
| Cuaderno y código | Recorrido didáctico, paquete Python y script maestro | [`04_reproduccion_python/`](04_reproduccion_python/) |
| Verificación | Pruebas, controles de calidad, manifiestos y huellas | [`05_verificacion/`](05_verificacion/) |

## Resultados principales

La base oficial contiene 340 municipios y dos unidades lacustres no
municipales. Las cifras son acumuladas para 2016–2020 y conservan los
decimales de la fuente.

| Resultado | Hectáreas | Lectura |
|---|---:|---|
| Pérdida bruta | 244,394.57 | Cobertura registrada como pérdida antes de cualquier resta |
| Recuperación reportada | 191,658.14 | Cobertura registrada como ganancia durante el período |
| Pérdida neta oficial | 52,736.43 | Diferencia entre pérdida bruta y recuperación |
| Saldo nacional ponderado | 116,473.23–123,988.03 | Recuperación reconocida de manera gradual dentro del dominio documentado |

En los 172 municipios donde se aplican proporciones a veinte años, la
pérdida neta oficial es 35,856.61 ha y el saldo ponderado se sitúa entre
99,593.41 y 107,108.21 ha. En los otros 168 municipios se conserva el cálculo
oficial: no se les asigna una proporción por semejanza supuesta.

La pérdida bruta de 244,394.57 ha corresponde al período acumulado completo;
no es una cifra exclusiva de 2020.

## Del balance oficial al saldo ponderado

El análisis utiliza cinco cantidades. Los símbolos facilitan la reproducción,
pero los nombres completos son la referencia principal.

| Símbolo | Significado | Unidad |
|---|---|---|
| $B$ | Pérdida bruta reportada | ha |
| $R$ | Recuperación o ganancia de cobertura reportada | ha |
| $N$ | Pérdida neta oficial: pérdida bruta menos recuperación | ha |
| $\rho_{20}$ | Proporción de biomasa recuperada a veinte años en los sitios de referencia | proporción o % |
| $H$ | Saldo forestal ponderado por recuperación | ha |

La secuencia puede leerse sin notación:

```text
Pérdida neta = pérdida bruta − recuperación reportada

Saldo ponderado = pérdida bruta
                  − (proporción a veinte años × recuperación reportada)
```

Por ejemplo, si se reportan 100 ha de recuperación y la proporción de
referencia es 60 %, el cálculo descuenta 60 ha de la pérdida bruta. Esto no
significa que 60 % de las hectáreas municipales haya recuperado su biomasa ni
que la proporción sea una probabilidad. Significa que los sitios científicos
de referencia alcanzaron aproximadamente 60 % de la biomasa aérea del bosque
de referencia a los veinte años.

Las expresiones formales, los límites de los intervalos, la completación
nacional, la valoración y el módulo de manglar se explican en el
[cuaderno](04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb)
y en la [metodología](01_metodologia/metodologia_saldo_forestal_guatemala_2016_2020.md).

## Cómo se agruparon los municipios

La agrupación se conserva como *correspondencia territorial experta
codificada*. Deben distinguirse dos asuntos:

1. La decisión computacional se toma con el código municipal. El código debe
   aparecer en una de cinco listas explícitas y disjuntas.
2. El fundamento territorial explica qué busca representar cada lista. Es una
   justificación operativa documentada, no una verificación automática de
   altitud, precipitación o tipo de bosque para cada hectárea recuperada.

La regla se ejecuta en este orden:

1. Un registro sin código municipal se identifica como unidad lacustre no
   municipal.
2. Un código presente en una de las cinco listas se asigna al grupo
   correspondiente y recibe su intervalo regional.
3. Cualquier otro código queda fuera del dominio de ponderación. Para esos 168
   municipios se conserva la pérdida neta oficial.

### Los cinco grupos incluidos

| Grupo territorial | Identificador | Fundamento territorial documentado | Municipios | Sitios y recuperación a 20 años |
|---|---|---|---:|---|
| Norte y centro de Petén | `REG-PET-N` | Plataforma kárstica, estacionalidad y bosque tropical estacional sobre calizas | 9 | Yucatán y Quintana Roo: 66.4–66.7 % |
| Sur de Petén y vertiente norte | `REG-PET-FTN` | Región analítica ampliada de la vertiente norte, asociada con bosques húmedos de tierras bajas de la Selva Maya | 32 | Chajul, México: 59.4 % |
| Tierras bajas húmedas del Caribe y del Pacífico | `REG-TB-HUM` | Caribe, Izabal, costa y bocacosta húmeda del Pacífico y Costa Cuca | 62 | Sarapiquí y Barro Colorado: 59.3–76.6 % |
| Bosques estacionales de Oriente | `REG-ORI-EST` | Chiquimula, Jalapa y Jutiapa tratados como bloque de bosque tropical estacional | 35 | El Ocote y Santa Rosa: 33.6–84.9 % |
| Valles secos interiores, Motagua y Salamá–Chixoy | `REG-SEC-MOT` | Mayor déficit hídrico y recuperación generalmente más lenta | 34 | Cinco sitios secos: 25.0–65.0 % |

Los 168 códigos restantes forman un grupo residual denominado en los
archivos *fuera del dominio por regla residual*. No constituyen una sexta
región ecológica y no se afirma que compartan una misma condición ambiental.
Los lagos de Amatitlán y Atitlán son los dos registros sin código municipal.

Tres ejemplos muestran la regla:

| Registro | Decisión |
|---|---|
| San José del Golfo (`0104`) | Su código aparece en la lista de valles secos; recibe el intervalo de ese grupo |
| Guatemala (`0101`) | Su código no aparece en las cinco listas; queda fuera del dominio y conserva el cálculo oficial |
| Lago de Amatitlán | No tiene código municipal; se conserva como unidad no municipal |

Las listas completas, los 342 registros y las fuentes están en el
[procedimiento reconstruido](01_metodologia/procedimiento_correspondencia_territorial_experta_codificada.md)
y en la [tabla de trazabilidad](00_trazabilidad_fuentes/trazabilidad_municipio_region_guatemala_2016_2020.csv).

## Ruta didáctica del cuaderno

El cuaderno está pensado para responder seis preguntas en orden:

1. ¿Qué registran la pérdida bruta, la recuperación y la pérdida neta?
2. ¿Por qué una ganancia de cobertura no equivale de inmediato a la biomasa
   del bosque perdido?
3. ¿Cómo se decide qué municipios reciben una proporción a veinte años?
4. ¿Cómo se construyen esas proporciones a partir de sitios científicos?
5. ¿Cuánto cambia la lectura municipal y nacional?
6. ¿Qué añaden la valoración, las trayectorias y la aplicación local de
   manglar?

El código está oculto de inicio para facilitar la lectura, pero puede
desplegarse. Cada tabla ofrece su CSV completo y cada resultado conserva nota,
fuente e interpretación.

## Datos utilizados

Las fuentes principales son INAB y CONAP para la dinámica de cobertura
forestal 2016–2020; Poorter et al. (2016) y el conjunto asociado en Dryad para
las proporciones de recuperación de biomasa; INAB, ICC y CONAP para la
evidencia estructural de manglar; y fuentes oficiales y académicas para la
valoración y las trayectorias.

El
[`registro_fuentes_saldo_forestal_guatemala.csv`](00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv)
documenta procedencia, acceso, uso analítico, archivos relacionados,
limitaciones y condiciones de reutilización.

## Reproducir y verificar

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

En Windows, active el entorno con `.venv\Scripts\activate`. La ejecución
reconstruye las tablas, el cuaderno y el paquete determinista en
`build/resultados_saldo_forestal_guatemala.zip`.

La verificación confirma la partición de 172 municipios incluidos, 168 fuera
del dominio y dos unidades no municipales; reproduce los cinco intervalos y
comprueba las identidades fila por fila. Estas comprobaciones garantizan que
el procedimiento documentado puede repetirse. No sustituyen la validación
ecológica pendiente de la correspondencia entre las hectáreas recuperadas y
los sitios de referencia.

## Estructura del repositorio

```text
.
├── 00_trazabilidad_fuentes/       # fuentes, insumos y bitácoras
├── 01_metodologia/                # conceptos, reglas y parámetros
├── 02_resultados_y_diccionario/   # tablas publicadas y diccionario
├── 04_reproduccion_python/        # cuaderno y cadena reproducible
├── 05_verificacion/               # pruebas, controles y manifiestos
├── CITATION.cff
├── codemeta.json
└── como_citar.txt
```

Los nombres de los archivos describen el contenido, el territorio y el
período. Los prefijos numéricos indican un orden de consulta, no una jerarquía
de importancia.

## Qué no puede concluirse

- Las proporciones a veinte años no indican la edad de la recuperación
  registrada entre 2016 y 2020.
- Las listas territoriales no son una regionalización oficial ni demuestran
  homogeneidad ecológica dentro de cada municipio.
- La evidencia publicada sustenta las proporciones de los sitios científicos,
  pero no valida por sí sola su transferencia a cada hectárea municipal.
- Los flujos municipales de la aproximación de manglar no son cambios
  exclusivos de cobertura de manglar.
- La recuperación ponderada y la aproximación local de manglar se comparan,
  pero no se suman.
- La transferencia monetaria es indicativa y no constituye una cuenta de
  ecosistemas completa.
- Los costos de Eta e Iota se presentan como contexto no aditivo y no se
  atribuyen causalmente a la deforestación.

Las brechas y los cruces espaciales necesarios para una validación posterior
se documentan en
[`brechas_validacion_ecologica.md`](01_metodologia/brechas_validacion_ecologica.md).

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
la versión más reciente.

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
