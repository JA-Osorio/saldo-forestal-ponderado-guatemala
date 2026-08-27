# Guía del diccionario de variables

El diccionario legible por máquina está en
`02_resultados_y_diccionario/diccionario_variables.csv`. Incluye nombre,
definición, tipo, unidad, capa, archivos relacionados y procedimiento de
construcción.

## Convenciones esenciales

| Prefijo, sufijo o campo | Significado |
|---|---|
| `perdida_bruta` | Pérdida de cobertura forestal antes de restar la recuperación reportada |
| `recuperacion_bruta` | Recuperación reportada, medida como ganancia de cobertura; se llama `ganancia_bruta` en la fuente |
| `perdida_neta` | $B-R$; un valor positivo representa pérdida |
| `proporcion_regeneracion_equivalente` | Prefijo de los campos que contienen el límite mínimo, el valor central o el límite máximo del factor aplicado |
| `proporcion_grupo_id` | Identificador del grupo territorial que aporta el intervalo de proporciones |
| `ponderado` | Resultado de $B-\rho R$ |
| `estructural` | Aproximación local basada en carbono y área basal de series de parcelas permanentes |
| `_inferior` | Menor magnitud de pérdida del intervalo, calculada con la mayor proporción |
| `_superior` | Mayor magnitud de pérdida del intervalo, calculada con la menor proporción |
| `_anual_ha` | Tasa media anual obtenida al dividir el acumulado 2016–2020 entre cuatro |
| `_gtq` | Quetzales corrientes del año indicado por el parámetro |

## Asignación territorial

La **asignación documentada de municipios a grupos territoriales de
referencia** utiliza cinco listas explícitas de códigos y una regla residual.
El procedimiento produce 172
municipios incluidos, 168 excluidos y dos unidades lacustres. Los conteos por
grupo son 9/32/62/35/34 para `REG-PET-N`, `REG-PET-FTN`, `REG-TB-HUM`,
`REG-ORI-EST` y `REG-SEC-MOT`.

| Campo de trazabilidad | Uso |
|---|---|
| `codigo_canonico` | Código municipal de cuatro dígitos usado en las reglas |
| `estado_dominio` | `elegible_regeneracion_equivalente`, `fuera_dominio_regla_residual` o `unidad_no_municipal` |
| `regla_id` | Regla determinista que produjo la asignación |
| `ruta_asignacion` | Lista explícita, regla residual o unidad no municipal |
| `criterio_agrupacion` | Explicación territorial de la asignación documentada |
| `estado_evidencia` | Soporte disponible para la asignación territorial |
| `revision_ecologica` | Estado de la validación ecológica, actualmente pendiente cuando corresponde |
| `version_metodo` | Versión de las reglas; en esta publicación, `1.0.0` |

La reproducibilidad computacional no equivale a validación ecológica. La
comparabilidad empírica de las hectáreas recuperadas con los sitios de
referencia requiere los cruces espaciales descritos en
`01_metodologia/brechas_validacion_ecologica.md`.

## Transformaciones de nombres

Al leer la base oficial de cobertura, la cadena normaliza:

| Nombre en la fuente | Nombre analítico |
|---|---|
| `ganancia_bruta_ha` | `recuperacion_bruta_ha` |
| `balance_neto_cobertura_ha` | `perdida_neta_ha` |

El catálogo conserva los nombres técnicos `proporcion_regeneracion_equivalente_min`, `proporcion_regeneracion_equivalente_central` y
`proporcion_regeneracion_equivalente_max`. En la documentación pública, los tres campos se representan con
$\rho$ y se denominan proporción de regeneración equivalente.

## Organización de archivos

- `00_trazabilidad_fuentes/`: insumos, fuentes y bitácoras de procedencia.
- `01_metodologia/`: fórmulas, reglas y parámetros de la versión 1.0.0.
- `02_resultados_y_diccionario/`: resultados publicados y diccionario.
- `04_reproduccion_python/`: cuaderno y cadena reproducible.
- `05_verificacion/`: pruebas, controles, reproducción por sitio y
  manifiestos.

Los nombres describen contenido, territorio y periodo. Los prefijos numéricos
indican el orden de lectura y auditoría.

## Identificadores territoriales y valores faltantes

`codigo` es el código municipal usado en los resultados. `codigo_canonico` lo
representa con cuatro dígitos en la bitácora de trazabilidad. Ambos son nulos en
las dos unidades lacustres. `cod_dep` identifica el departamento y
`tipo_unidad` separa municipios de unidades no municipales.

- `codigo` y `codigo_canonico` pueden faltar solo en unidades lacustres.
- `proporcion_grupo_id` falta fuera del dominio de aplicación.
- `proporcion_regeneracion_equivalente_critica` falta cuando la recuperación es cero, porque $B/R$ no está
  definida.
- Los vacíos no deben convertirse silenciosamente en cero.

## Precisión

La cadena conserva diez decimales en los CSV derivados para permitir la
reconciliación. Las tablas narrativas pueden redondear, pero los agregados se
calculan antes del redondeo. Para `REG-SEC-MOT`, el intervalo bruto
$[0.254,0.645]$ se redondea hacia afuera en incrementos de 0.05 y produce
$[0.25,0.65]$.
