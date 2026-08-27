# Guía de reproducción

## Requisitos

- Python 3.11, 3.12 o 3.13;
- un entorno capaz de instalar las dependencias declaradas por el proyecto;
- aproximadamente 100 MB libres para entorno, resultados y exportaciones;
- no se requiere acceso de red para reconstruir los resultados a partir de `data/raw/`.

## Ejecución completa

Desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/run_pipeline.py
pytest -q
```

En Windows PowerShell, la activación equivalente es:

```powershell
.venv\Scripts\Activate.ps1
```

## Productos esperados

El script maestro reconstruye, entre otros:

- resultados institucionales nacionales, departamentales y municipales;
- resultados de recuperación ponderada por municipio, departamento y región de referencia;
- transiciones de clasificación y municipios cuyo diagnóstico cambia con la ponderación;
- completación nacional conservadora;
- comparación entre deforestación bruta, saldo ponderado y pérdida neta;
- valoración y sensibilidad de tasa de descuento;
- parámetros de valoración efectivamente aplicados;
- escenarios nacionales y trayectorias 2026–2035;
- aproximación local de manglar y comparación con la recuperación ponderada;
- controles de calidad;
- un ZIP determinista con tablas y metadatos de ejecución.

Los CSV se escriben en `data/processed/` y `outputs/tables/`. El manifiesto de resultados, los metadatos de ejecución y la descarga integral se escriben en `outputs/downloads/`. El manifiesto enumera todos los miembros del ZIP salvo a sí mismo, con tamaño y SHA-256 verificables.

## Comprobaciones rápidas

Después de ejecutar, deben cumplirse como mínimo:

| Comprobación | Valor esperado |
|---|---:|
| Unidades de la base | 342 |
| Municipios | 340 |
| Municipios con proporción de recuperación a veinte años | 172 |
| Municipios de la aproximación local | 13 |
| Series multitemporales PPM | 55 |
| Pérdida bruta nacional 2016–2020 | 244,394.56984238 ha |
| Recuperación nacional 2016–2020 | 191,658.14331302 ha |
| Pérdida neta nacional 2016–2020 | 52,736.42652936 ha |
| Saldo ponderado nacional conservador | 116,473.231566156–123,988.027844361 ha |

La tabla `data/processed/controles_calidad.csv` debe marcar todos los controles como `Cumple`.

## Ejecución del cuaderno

El cuaderno principal es `notebooks/saldo_forestal_ponderado_guatemala.ipynb`. Debe ejecutarse desde el inicio con el repositorio disponible. Para una revisión reproducible:

1. reinicie el entorno;
2. ejecute todas las celdas en orden;
3. confirme que cada celda de resultado emite un solo objeto;
4. compare las cifras de control con las tablas del pipeline;
5. pruebe las descargas individuales y la descarga integral;
6. revise que cada tabla o figura tenga título y unidad en la salida, y nota, interpretación y atribución de fuentes en la celda Markdown contigua;
7. confirme que las trayectorias se distingan por color, trazo y marcador;
8. pruebe la descarga PNG de una figura y el CSV completo de una tabla.

## Uso de otra ubicación de datos

El lector admite un directorio alternativo mediante la variable `SALDO_FORESTAL_DATA_DIR`:

```bash
export SALDO_FORESTAL_DATA_DIR=/ruta/explicita/a/insumos
python scripts/run_pipeline.py
```

El directorio debe contener los archivos esperados con los mismos nombres y esquemas. Esta opción no evita las validaciones de número de unidades, dominios e identidades.

## Verificación para publicación

Antes de distribuir los resultados:

1. ejecute el pipeline en un entorno limpio;
2. ejecute todas las pruebas;
3. ejecute el cuaderno de principio a fin;
4. revise visualmente tablas y figuras;
5. regenere manifiestos y descargas;
6. revise los metadatos bibliográficos en `CITATION.cff` y `codemeta.json`;
7. confirme que la referencia general y la atribución de fuentes sean consistentes en la documentación y las descargas.

## Diagnóstico de errores comunes

### `ModuleNotFoundError: saldo_forestal`

Instale el proyecto en modo editable con `python -m pip install -e ".[dev]"` y ejecute el script desde la raíz.

### No se cumple $N=B-R$

No corrija el archivo procesado. Verifique la fuente, separador decimal, encabezados y huella del insumo. Documente cualquier sustitución de archivo.

### El intervalo aparece invertido

Recuerde que una proporción de recuperación mayor reduce $H=B-\rho R$. El límite inferior usa `rho20_max`; el superior usa `rho20_min`.

### La recuperación ponderada y manglar no reconcilian al sumarlos

Es el comportamiento esperado: los trece municipios de la aplicación local están dentro del dominio de aplicación. Son aproximaciones que se comparan, no módulos aditivos.
