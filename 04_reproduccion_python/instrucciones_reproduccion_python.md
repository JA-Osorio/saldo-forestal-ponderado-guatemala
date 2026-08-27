# Guía de reproducción

## Requisitos

El proyecto requiere Python 3.11, 3.12 o 3.13 y aproximadamente 100 MB
libres para el entorno y los artefactos temporales. La reproducción no
requiere acceso de red: los insumos preservados se encuentran en
`00_trazabilidad_fuentes/` y los parámetros en `01_metodologia/`.

## Ejecución completa

Desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python 04_reproduccion_python/reproducir_saldo_forestal_guatemala.py
python -m pytest -q
```

En Windows PowerShell, active el entorno con:

```powershell
.venv\Scripts\Activate.ps1
```

La cadena reconstruye la correspondencia territorial, las proporciones de
recuperación, los resultados físicos y monetarios, las trayectorias y la
aplicación local de manglar. Escribe una sola copia canónica de cada producto:

- bitácoras de procedencia en `00_trazabilidad_fuentes/`;
- tablas publicadas en `02_resultados_y_diccionario/`;
- controles y manifiestos en `05_verificacion/`;
- paquete temporal en `build/resultados_saldo_forestal_guatemala.zip`.

## Comprobaciones mínimas

| Comprobación | Valor esperado |
|---|---:|
| Unidades de la base | 342 |
| Municipios | 340 |
| Unidades lacustres | 2 |
| Municipios incluidos | 172 |
| Municipios excluidos por la regla residual | 168 |
| Conteos regionales | 9 / 32 / 62 / 35 / 34 |
| Municipios de la aproximación local | 13 |
| Series multitemporales de manglar | 55 |
| Pérdida bruta nacional 2016–2020 | 244,394.56984238 ha |
| Recuperación nacional 2016–2020 | 191,658.14331302 ha |
| Pérdida neta nacional 2016–2020 | 52,736.42652936 ha |
| Saldo ponderado nacional conservador | 116,473.231566156–123,988.027844361 ha |

La tabla
`05_verificacion/controles_calidad_saldo_forestal_guatemala_2016_2020.csv`
debe marcar todos los controles como `Cumple`. Las pruebas verifican además
la disjunción de las cinco listas territoriales, la regla residual, la
reproducción de trece porcentajes desde Dryad y las identidades por municipio.

## Ejecución del cuaderno

El cuaderno público es
`04_reproduccion_python/cuaderno_saldo_forestal_ponderado_guatemala_2016_2020.ipynb`.
Puede reconstruirse con:

```bash
python 04_reproduccion_python/generar_cuaderno_saldo_forestal_guatemala.py
```

Para una revisión editorial, ejecute todas las celdas en orden y compruebe que
cada resultado emite una sola salida; que las notas, fuentes e interpretaciones
están en la celda Markdown contigua; y que las descargas PNG y CSV funcionan.

## Uso de otra raíz de insumos

El lector admite una raíz alternativa mediante `SALDO_FORESTAL_DATA_DIR`:

```bash
export SALDO_FORESTAL_DATA_DIR=/ruta/explicita/al/paquete
python 04_reproduccion_python/reproducir_saldo_forestal_guatemala.py
```

La ruta debe conservar la estructura relativa `00_trazabilidad_fuentes/` y
`01_metodologia/`. Esta opción no omite ninguna validación.

## Verificación para publicación

Antes de publicar:

1. ejecute la reproducción completa en un entorno limpio;
2. regenere el cuaderno y los manifiestos;
3. ejecute las pruebas;
4. verifique que el ZIP sea determinista;
5. revise `CITATION.cff`, `codemeta.json` y `como_citar.txt`;
6. confirme que no existan rutas antiguas ni copias duplicadas de resultados.

El inventario general se regenera con:

```bash
python 04_reproduccion_python/generar_manifiestos.py
```

## Diagnóstico de errores frecuentes

### `ModuleNotFoundError: saldo_forestal`

Instale el proyecto en modo editable con `python -m pip install -e ".[dev]"`
y ejecute los comandos desde la raíz.

### No se cumple $N=B-R$

No edite un resultado publicado. Verifique el insumo, los encabezados y la
huella registrada; corrija la fuente o el código y reconstruya toda la cadena.

### El intervalo aparece invertido

Una proporción mayor reduce $H=B-\rho R$. Por eso el límite inferior usa
`rho20_max` y el superior usa `rho20_min`.

### Los resultados de manglar no se suman al saldo nacional

Es el comportamiento previsto. Los trece municipios de la aproximación local
están dentro del dominio de recuperación ponderada; ambas lecturas se comparan
en soporte común, pero no son módulos aditivos.
