# Procedimiento de correspondencia territorial experta codificada

## 1. Objeto

El procedimiento vincula municipios guatemaltecos con grupos de sitios publicados por Poorter et al. (2016) para aplicar proporciones de recuperación relativa de biomasa aérea a veinte años. La denominación metodológica es **correspondencia territorial experta codificada**. No convierte esos sitios en estimaciones nacionales ni afirma equivalencia ecológica o integral de servicios ecosistémicos.

La cadena separa dos operaciones:

1. municipio de Guatemala → región analítica;
2. región analítica → sitios y proporción de recuperación.

## 2. Universo y llave

El universo de entrada contiene 342 registros de la fuente INAB 2016–2020:

- 340 municipios con código;
- Lago de Amatitlán y Lago de Atitlán, sin código municipal.

Todas las uniones se realizan mediante el código municipal canónico de cuatro dígitos. Los nombres se conservan solo como etiquetas, porque existen municipios homónimos.

## 3. Reglas municipales exactas

### `REG-PET-N`

```text
1701–1707, 1711, 1713
```

### `REG-PET-FTN`

```text
1305, 1307, 1318, 1322, 1324–1326, 1331–1333,
1405, 1411, 1413, 1415, 1419–1420,
1607–1617,
1708–1710, 1712, 1714
```

### `REG-TB-HUM`

```text
0408, 0412,
0501–0510, 0513–0514,
0607–0611,
0917, 0919–0922,
1001–1002, 1004–1007, 1010, 1012–1014, 1020–1021,
1101–1109,
1212–1222, 1230,
1801–1805
```

### `REG-ORI-EST`

```text
2001–2011, 2101–2107, 2201–2217
```

### `REG-SEC-MOT`

```text
0104–0105, 0107, 0112,
0201–0208,
1416–1418, 1421,
1501–1507,
1901–1911
```

La función determinista es:

1. código nulo → `UNIDAD-NO-MUN`;
2. código presente en una lista → región correspondiente y `elegible_recuperacion_20_anios`;
3. cualquier otro código municipal → `REG-ALT-MON` y `fuera_dominio_altiplano_montano`.

Las listas son disjuntas. El resultado contiene 172 códigos y la regla residual contiene 168.

## 4. Interpretación territorial operativa

| Región | Interpretación operativa | Municipios |
|---|---|---:|
| `REG-PET-N` | Norte y centro de Petén; plataforma kárstica y bosque estacional | 9 |
| `REG-PET-FTN` | Sur de Petén y vertiente norte; región analítica FTN ampliada | 32 |
| `REG-TB-HUM` | Caribe, costa y bocacosta húmeda del Pacífico y Costa Cuca | 62 |
| `REG-ORI-EST` | Bloque de Chiquimula, Jalapa y Jutiapa tratado como bosque estacional | 35 |
| `REG-SEC-MOT` | Valles secos interiores, Motagua y Salamá–Chixoy | 34 |

La clasificación no debe describirse como aplicación automática del umbral de 1,000 m. Incluye municipios con gradientes amplios y corresponde a listas territoriales expertas codificadas. La comparación empírica de las hectáreas recuperadas con los sitios de referencia sigue pendiente.

## 5. Derivación de las proporciones

La *Extended Data Table 1* informa `relative biomass recovery after 20 years (%AGB)`. Para cada región se seleccionan sitios explícitos y se calcula el mínimo y máximo.

Cuando el sitio está presente en el CSV de Dryad, el porcentaje se reproduce mediante:

\[
AGB_{20,s}=\widehat\alpha_s+\widehat\beta_s\ln(20),
\qquad
\rho_{20,s}=100\frac{AGB_{20,s}}{\operatorname{mediana}(AGB_{OG,s})}.
\]

Antes del ajuste se excluyen las observaciones con biomasa superior a 500 Mg/ha y el sitio Marqués de Comillas, conforme al README del dataset; las edades iguales a cero no entran en el logaritmo. Trece porcentajes seleccionados coinciden con la tabla publicada al redondear a una decimal. Quintana Roo no está presente en el CSV público y se verifica directamente en la tabla ampliada.

Para `REG-SEC-MOT`, los valores numéricos son 25.4, 29.5, 35.7, 49.9 y 64.5%. El intervalo bruto es:

\[
[0.254,\;0.645].
\]

Se aplica redondeo exterior en incrementos de 0.05:

\[
\left[
0.05\left\lfloor\frac{0.254}{0.05}\right\rfloor,
0.05\left\lceil\frac{0.645}{0.05}\right\rceil
\right]
=
[0.25,\;0.65].
\]

Los demás intervalos no se redondean más allá de convertir porcentajes a proporciones.

| Región | Intervalo $[\rho_{20}^{\min},\rho_{20}^{\max}]$ | Derivación |
|---|---:|---|
| `REG-PET-N` | [0.664, 0.667] | Mínimo y máximo publicados |
| `REG-PET-FTN` | [0.594, 0.594] | Valor único publicado |
| `REG-TB-HUM` | [0.593, 0.766] | Mínimo y máximo publicados |
| `REG-ORI-EST` | [0.336, 0.849] | Mínimo y máximo publicados |
| `REG-SEC-MOT` | [0.250, 0.650] | Mínimo y máximo con redondeo exterior |

## 6. Propagación municipal

Para cada municipio elegible:

\[
N_i=B_i-R_i,
\]

\[
H_i^{\mathrm{inf}}=B_i-\rho_i^{\mathrm{sup}}R_i,
\qquad
H_i^{\mathrm{sup}}=B_i-\rho_i^{\mathrm{inf}}R_i.
\]

La cadena reproduce estas identidades con los decimales originales y redondea solo en productos de comunicación posteriores.

## 7. Trazabilidad y archivos

La bitácora municipal registra, por fila:

- código original y canónico;
- departamento y municipio;
- estado del dominio, región e identificador `proporcion_region_id`;
- identificador de regla;
- tipo y origen de decisión;
- criterio operativo;
- estado de evidencia y revisión ecológica;
- fuente del universo y fuente del intervalo;
- versión metodológica `1.0.0`.

La bitácora de sitios registra sitio, país, precipitación, porcentaje original, uso numérico o contextual, operación de agregación, redondeo y localización en la fuente.

| Función | Archivo |
|---|---|
| Reglas municipales | `01_metodologia/reglas_correspondencia_territorial_experta_codificada.json` |
| Correspondencia entre regiones, sitios e intervalos | `01_metodologia/correspondencia_regiones_sitios_referencia.json` |
| Trazabilidad de 342 unidades | `00_trazabilidad_fuentes/trazabilidad_municipio_region_guatemala_2016_2020.csv` |
| Trazabilidad de regiones y sitios | `00_trazabilidad_fuentes/trazabilidad_region_sitio_recuperacion_biomasa_20_anios.csv` |
| Reproducción de porcentajes por sitio | `05_verificacion/reproduccion_por_sitio_recuperacion_biomasa_20_anios.csv` |

## 8. Pruebas automatizadas

Diez pruebas automatizadas comprueban:

- integridad de los insumos mediante huellas y ejecución determinista;
- igualdad fila a fila de 342 unidades;
- partición 172/168/2;
- conteos regionales 9/32/62/35/34;
- trazabilidad sin campos esenciales vacíos;
- cinco intervalos iguales a los de referencia de la versión 1.0.0;
- reproducción desde Dryad de trece porcentajes publicados;
- igualdad de los 172 resultados municipales;
- identidades matemáticas por municipio;
- independencia entre la cadena de cálculo y los archivos usados como referencia de regresión.

Estas pruebas resuelven la reproducibilidad computacional. No sustituyen la validación ecológica, que requiere cruces espaciales de las hectáreas recuperadas con elevación, tipo de bosque, estacionalidad y otras variables ambientales.
