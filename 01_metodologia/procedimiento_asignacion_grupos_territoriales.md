# Asignación de municipios a grupos territoriales de referencia

## 1. Finalidad del procedimiento

Este documento explica cómo el suplemento reproducible asigna una proporción
de regeneración equivalente a una parte de los municipios de Guatemala. La
operación tiene dos etapas:

1. asignar cada municipio incluido a uno de cinco grupos territoriales;
2. vincular cada grupo con sitios científicos de referencia y con el intervalo
   que se aplica a la ganancia de cobertura forestal.

La asignación se ejecuta mediante listas explícitas de códigos municipales. Es
reproducible, pero no constituye una regionalización oficial ni una validación
ecológica individual de las hectáreas reportadas como ganancia de cobertura.

## 2. Universo territorial

Guatemala tenía 340 municipios durante el período analizado. La tabla de INAB
y CONAP contiene 342 registros porque incorpora, además, el Lago de Amatitlán y
el Lago de Atitlán como unidades de reporte sin código municipal.

| Tratamiento | Unidades | Aplicación |
|---|---:|---|
| Municipios incluidos en cinco listas | 172 | Reciben el intervalo asignado a su grupo territorial |
| Otros municipios | 168 | Conservan la pérdida neta reportada por INAB y CONAP |
| Lagos de Amatitlán y Atitlán | 2 | Permanecen fuera de la asignación municipal |
| Total de registros de la fuente | 342 | 340 municipios y 2 unidades lacustres |

La llave de unión es el código municipal canónico de cuatro dígitos. Los
nombres se conservan como etiquetas y no se utilizan para decidir la
pertenencia, porque existen municipios homónimos.

## 3. Proporción aplicada

La *proporción de regeneración equivalente*, \(\rho_i\), es el factor por el
que se multiplica la ganancia de cobertura \(R_i\) antes de restarla de la
pérdida bruta \(B_i\):

\[
H_i=B_i-\rho_iR_i.
\]

Los valores de \(\rho_i\) se parametrizan con la recuperación relativa de
biomasa aérea observada a los veinte años en los sitios de Poorter et al.
(2016). El horizonte de veinte años pertenece a esa evidencia científica; no
indica la edad de la ganancia de cobertura registrada en cada municipio.

## 4. Grupos territoriales, criterios y sitios de referencia

La tabla separa tres decisiones que no deben confundirse: la regla
computacional que determina la pertenencia, el criterio territorial usado para
tratar esos municipios como un grupo y los sitios científicos utilizados para
parametrizar el intervalo.

| Grupo territorial en Guatemala | Regla computacional y criterio compartido | Territorios o sitios utilizados como referencia | Valores publicados | Intervalo aplicado | Punto medio | Municipios |
|---|---|---|---:|---:|---:|---:|
| Norte y centro de Petén | Nueve códigos de Petén; plataforma kárstica, estacionalidad y bosque tropical estacional | Quintana Roo y Yucatán, México | 66.4 y 66.7 % | 66.4–66.7 % | 66.6 % | 9 |
| Sur de Petén y vertiente norte | Diez municipios de Huehuetenango, seis de Quiché, once de Alta Verapaz y cinco de Petén; continuidad territorial con la Franja Transversal del Norte | Chajul, México; bosques húmedos de tierras bajas del ámbito de la Selva Maya | 59.4 % | 59.4 % | 59.4 % | 32 |
| Tierras bajas húmedas del Caribe y del Pacífico | Municipios seleccionados de Izabal, la costa y bocacosta húmeda del Pacífico y Costa Cuca; baja altitud y alta disponibilidad de agua | Barro Colorado, Panamá, y dos series de Sarapiquí, Costa Rica | 59.3, 59.6 y 76.6 % | 59.3–76.6 % | 68.0 % | 62 |
| Oriente de Guatemala | Los 11 municipios de Chiquimula, siete de Jalapa y 17 de Jutiapa; bloque territorial de bosque tropical estacional | Dos series de El Ocote, México, y Santa Rosa, Costa Rica | 33.6, 62.3 y 84.9 % | 33.6–84.9 % | 59.3 % | 35 |
| Valles secos interiores, Motagua y Salamá–Chixoy | Municipios seleccionados de Guatemala, El Progreso, Quiché, Baja Verapaz y Zacapa; valles interiores con mayor déficit hídrico | Nizanda y Chamela, México; Salvatierra y San Lorenzo, Bolivia; São Paulo, Brasil | 25.4, 29.5, 35.7, 49.9 y 64.5 % | 25.0–65.0 % | 45.0 % | 34 |

Los territorios o sitios de referencia sustentan el valor aplicado en el
cálculo. La tabla no afirma que cada municipio sea ecológicamente equivalente
a esos sitios. Esa afirmación requeriría validar las hectáreas recuperadas con
variables espaciales de elevación, precipitación, tipo de bosque,
estacionalidad y uso del suelo.

En el grupo de valles secos, el intervalo observado de 25.4–64.5 % se amplía
mediante redondeo exterior a incrementos de 0.05:

\[
\left[
0.05\left\lfloor\frac{0.254}{0.05}\right\rfloor,
0.05\left\lceil\frac{0.645}{0.05}\right\rceil
\right]
=
[0.25,\,0.65].
\]

## 5. Reglas exactas de pertenencia

Los identificadores `REG-*` se conservan como llaves técnicas en los archivos
descargables. En la lectura pública se utilizan los nombres geográficos.

### Norte y centro de Petén

`1701–1707, 1711, 1713`

### Sur de Petén y vertiente norte

`1305, 1307, 1318, 1322, 1324–1326, 1331–1333, 1405, 1411, 1413, 1415,
1419–1420, 1607–1617, 1708–1710, 1712, 1714`

### Tierras bajas húmedas del Caribe y del Pacífico

`0408, 0412, 0501–0510, 0513–0514, 0607–0611, 0917, 0919–0922,
1001–1002, 1004–1007, 1010, 1012–1014, 1020–1021, 1101–1109,
1212–1222, 1230, 1801–1805`

### Oriente de Guatemala

`2001–2011, 2101–2107, 2201–2217`

### Valles secos interiores, Motagua y Salamá–Chixoy

`0104–0105, 0107, 0112, 0201–0208, 1416–1418, 1421, 1501–1507,
1901–1911`

Las cinco listas son disjuntas. Un código municipal que no aparece en ellas
queda fuera del dominio de aplicación. Los 168 municipios residuales no se
interpretan como un sexto grupo ecológico y no reciben sitio ni proporción de
referencia.

## 6. Construcción y propagación de los intervalos

Para cada grupo se toma el mínimo y el máximo de los valores numéricos
seleccionados. El punto medio que se presenta en la figura es el promedio
aritmético de esos dos límites; no es el promedio de los sitios ni una nueva
estimación estadística.

Para un municipio incluido, el límite superior de la proporción produce el
saldo menor y el límite inferior produce el saldo mayor:

\[
H_i^{\mathrm{inf}}=B_i-\rho_i^{\mathrm{sup}}R_i,
\qquad
H_i^{\mathrm{sup}}=B_i-\rho_i^{\mathrm{inf}}R_i.
\]

Para los otros 168 municipios y para las dos unidades lacustres se conserva:

\[
N_i=B_i-R_i.
\]

## 7. Trazabilidad de la decisión

Cada uno de los 342 registros conserva código, departamento, municipio,
grupo, regla aplicada, criterio de agrupación, fuente y estado de revisión. La
segunda tabla de trazabilidad conserva los sitios, los valores publicados, su
uso numérico o contextual y la operación con la que se forma cada intervalo.

| Función | Archivo |
|---|---|
| Reglas municipales | `01_metodologia/reglas_asignacion_grupos_territoriales.json` |
| Relación entre grupos, sitios e intervalos | `01_metodologia/asignacion_grupos_sitios_referencia.json` |
| Trazabilidad de 342 unidades | `00_trazabilidad_fuentes/trazabilidad_municipio_grupo_territorial_guatemala_2016_2020.csv` |
| Trazabilidad de grupos y sitios | `00_trazabilidad_fuentes/trazabilidad_grupo_sitio_proporcion_regeneracion_equivalente.csv` |
| Reproducción de valores por sitio | `05_verificacion/reproduccion_proporcion_regeneracion_equivalente_por_sitio.csv` |

Las pruebas automatizadas verifican la partición 172/168/2, los conteos
9/32/62/35/34, los cinco intervalos y la aplicación fila por fila. Estas
comprobaciones resuelven la reproducibilidad computacional del procedimiento;
no sustituyen la validación ecológica pendiente.
