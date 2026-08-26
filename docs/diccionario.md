# Diccionario de datos

El diccionario legible por máquina está en `data/metadata/diccionario_variables.csv`. Incluye nombre, definición, tipo, unidad, capa, archivos y procedimiento de construcción.

## Convenciones esenciales

| Prefijo o sufijo | Significado |
|---|---|
| `perdida_bruta` | Pérdida de cobertura forestal antes de restar la recuperación reportada |
| `recuperacion_bruta` | Recuperación reportada, medida como ganancia de cobertura; se llama `ganancia_bruta` en el archivo original |
| `perdida_neta` | \(B-R\); un valor positivo representa pérdida |
| `rho20` | Proporción de recuperación de biomasa a veinte años, con fuente en Poorter et al. (2016) |
| `ponderado` | Resultado de \(B-\rho R\) |
| `estructural` | Aproximación local basada en carbono y área basal de series PPM |
| `_inferior` | Menor magnitud de pérdida del intervalo, calculada con la mayor proporción |
| `_superior` | Mayor magnitud de pérdida del intervalo, calculada con la menor proporción |
| `_anual_ha` | Tasa media anual obtenida al dividir el acumulado 2016–2020 entre cuatro |
| `_gtq` | Quetzales corrientes del año indicado por el parámetro |

## Transformaciones de nombres

Al leer la base oficial de cobertura, el pipeline normaliza:

| Nombre en `data/raw/` | Nombre analítico |
|---|---|
| `ganancia_bruta_ha` | `recuperacion_bruta_ha` |
| `balance_neto_cobertura_ha` | `perdida_neta_ha` |

El catálogo analítico de proporciones utiliza directamente `rho20_min`, `rho20_central` y `rho20_max`, junto con la notación \(\rho_{20}\).

## Tipos de archivo

- `data/raw/`: valores de entrada preservados o transcritos con trazabilidad.
- `data/processed/`: tablas reconstruidas por el pipeline.
- `outputs/tables/`: copias de publicación de las tablas procesadas.
- `outputs/downloads/`: manifiesto, metadatos de ejecución y paquete integral.

## Identificadores territoriales

`codigo` es el código municipal utilizado para cruces. Es nulo en las dos unidades lacustres. `cod_dep` identifica el departamento y `tipo_unidad` separa municipios de unidades no municipales. Ninguna suma “municipal” debe incluir las unidades lacustres sin explicitarlo.

## Valores faltantes

- `codigo` puede faltar solo en unidades lacustres.
- `proporcion_region_id` falta fuera del dominio de aplicación.
- `rho_critica` falta cuando la recuperación es cero, porque \(B/R\) no está definida.
- Los vacíos no deben convertirse silenciosamente en cero.

## Precisión

El pipeline conserva diez decimales en los CSV derivados para permitir reconciliación. Las tablas narrativas pueden redondear, pero los agregados se calculan antes del redondeo.
