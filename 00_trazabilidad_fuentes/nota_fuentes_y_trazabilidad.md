# Fuentes y trazabilidad

## Principio de procedencia

El repositorio organiza el suplemento en cinco capas:

1. **Fuentes y trazabilidad (`00_trazabilidad_fuentes/`):** insumos preservados, referencias y bitácoras.
2. **Metodología (`01_metodologia/`):** reglas, fórmulas y parámetros.
3. **Resultados y diccionario (`02_resultados_y_diccionario/`):** tablas listas para reutilización y definiciones de variables.
4. **Reproducción (`04_reproduccion_python/`):** cuaderno y cadena de cálculo.
5. **Verificación (`05_verificacion/`):** pruebas, controles y manifiestos.

`00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv` registra para cada fuente su URL o DOI, fecha de consulta, uso analítico, archivos relacionados, limitaciones y estado de las condiciones de reutilización.

La existencia de una copia en `00_trazabilidad_fuentes/` no convierte al repositorio en fuente primaria. Toda reutilización debe atribuir la institución o publicación original y revisar sus condiciones de uso. Las licencias que todavía no están identificadas se marcan como pendientes; la licencia CC BY 4.0 del repositorio no amplía derechos sobre materiales de terceros.

## Cobertura forestal 2016–2020

La base principal procede del portal SIG-INAB y de *Estudio de la cobertura forestal para el año 2020 y dinámica de la cobertura forestal en el período 2016–2020: República de Guatemala*, publicado por INAB y CONAP en 2023. El repositorio utiliza la tabla preservada en `00_trazabilidad_fuentes/base_forestal_municipios_guatemala_2016_2020.csv`.

En el archivo de origen:

- `ganancia_bruta_ha` se normaliza como `recuperacion_bruta_ha`;
- `balance_neto_cobertura_ha` se normaliza como `perdida_neta_ha`;
- se mantienen dos unidades lacustres no municipales;
- la igualdad $N=B-R$ reportada por INAB y CONAP se verifica antes de cualquier cálculo complementario.

La cifra nacional de pérdida bruta, cerca de 245 mil ha, corresponde al acumulado 2016–2020. No es una observación exclusiva del año 2020.

Enlaces oficiales:

- [Narrativa de dinámica de cobertura 2016–2020](https://sig.inab.gob.gt/portal/apps/storymaps/stories/eac535d7b61a47f7b12a9b81eb9c15b6)
- [Tabla municipal en ArcGIS](https://sig.inab.gob.gt/portal/home/item.html?id=a15d600e7aed41d8b2afdcdcefad32db&sublayer=5)

## Antecedente histórico 1991–2016

La serie descriptiva procede de *Bosques* (Sandoval García, Gálvez Ruano y Pinillos Cifuentes, 2022) y del material de dinámica 2010–2016. Se usa para contrastar el comportamiento de la deforestación bruta y de la pérdida neta.

Los periodos históricos no forman un panel perfectamente encadenado: tienen intervalos efectivos distintos y cada ejercicio estimó coberturas iniciales y finales de manera independiente. La serie se usa como antecedente narrativo, no para interpolar una trayectoria anual exacta.

- [*Bosques* (IARNA-URL, 2022)](https://infoiarna.url.edu.gt/publicacion/bosques/)
- [Dinámica de cobertura forestal de Guatemala 2010–2016](https://infoiarna.url.edu.gt/publicacion/dinamica-de-cobertura-forestal-de-guatemala-2010-2016-folleto/)

## Proporción de regeneración equivalente

Los parámetros proceden de la publicación de Poorter et al. (2016) y del conjunto de datos publicado en Dryad en 2017:

- [Publicación en *Nature*](https://doi.org/10.1038/nature16512)
- [*Data from: Biomass resilience of Neotropical secondary forests* (Dryad, 2017; CC0)](https://doi.org/10.5061/dryad.82vr4)

Poorter et al. (2016) estiman la recuperación relativa de biomasa aérea de bosques secundarios neotropicales veinte años después del abandono. En este suplemento, esos valores parametrizan la *proporción de regeneración equivalente* aplicada a la ganancia de cobertura forestal. El horizonte corresponde a los sitios científicos de referencia: la base municipal guatemalteca no informa la edad, el origen ni la biomasa de la superficie registrada como ganancia.

La *asignación documentada de municipios a grupos territoriales de referencia* utiliza cinco listas explícitas y una regla residual. El procedimiento produce 172 municipios dentro del dominio de aplicación, 168 fuera de él y dos unidades lacustres separadas. Los cinco grupos contienen 9, 32, 62, 35 y 34 municipios. Es una construcción analítica del suplemento y no una regionalización publicada por Poorter et al. (2016).

La bitácora `00_trazabilidad_fuentes/trazabilidad_municipio_grupo_territorial_guatemala_2016_2020.csv` conserva la decisión para las 342 unidades. La relación entre grupos territoriales, sitios e intervalos está en `00_trazabilidad_fuentes/trazabilidad_grupo_sitio_proporcion_regeneracion_equivalente.csv`; el catálogo de aplicación está en `02_resultados_y_diccionario/catalogo_proporcion_regeneracion_equivalente.csv`. Los nombres técnicos de estos archivos se mantienen para conservar la compatibilidad de la cadena reproducible.

Cuatro intervalos se obtienen directamente de los valores publicados por sitio. Para `REG-SEC-MOT`, los sitios numéricos producen $[0.254,0.645]$ y el redondeo exterior en incrementos de 0.05 produce $[0.25,0.65]$. La reproducción desde Dryad verifica trece porcentajes a una decimal; Quintana Roo solo se verifica en la tabla ampliada porque no aparece en el CSV público.

## Evidencia estructural de manglar

La evidencia estructural se contextualiza con el portal oficial del INAB y sigue el diseño descrito en la metodología de parcelas permanentes publicada por INAB, ICC y CONAP en 2016:

- [Áreas potenciales de restauración de manglares](https://sig.inab.gob.gt/portal/apps/storymaps/stories/955793375059405ab4964bb40813b9fd)
- [Metodología para el establecimiento y mantenimiento de parcelas permanentes de medición forestal en bosque natural del ecosistema manglar](https://icc.org.gt/wp-content/uploads/2023/03/094.pdf)

La tabla analítica reúne trece municipios y suma 75 registros de parcela, aunque el portal menciona 76 para el universo del servicio. El repositorio no imputa ni altera un registro para forzar la coincidencia. El intervalo 30/55–34/55 se deriva únicamente de 55 series multitemporales comparables.

Los cambios de cobertura utilizados en el análisis siguen siendo municipales y forestales totales. El módulo no constituye una estimación de pérdida o ganancia específica de cobertura de manglar.

## Valoración de servicios ecosistémicos

El valor unitario se documenta a partir de la *Cuenta de ecosistemas de Guatemala*. Su homologación a precios de 2026 utiliza el cuadro oficial del producto interno bruto del Banco de Guatemala descrito más adelante.

- [Cuenta de ecosistemas de Guatemala, segunda edición](https://documents.worldbank.org/en/publication/documents-reports/documentdetail/451591561110110128)

El valor medio de Q22,553/ha/año a precios de 2019 resume 21 estudios sobre aproximadamente 9,403 km². Combina distintos servicios, ecosistemas y métodos. Su homologación a 2026 es una transferencia de valor indicativa, no una valoración espacialmente diferenciada ni una cuenta nacional exhaustiva.

El factor de homologación 2019–2026 se deriva del cuadro oficial *Producto interno bruto: año de referencia 2013; años 2013–2026* del Banco de Guatemala, consultado el 26 de agosto de 2026. Se calcula como el cociente entre los deflactores implícitos de ambos años:

$$
\frac{1{,}008{,}060.4/657{,}811.4}{593{,}972.0/515{,}350.3}
=1.32960218275.
$$

- [Cuadro del PIB, año de referencia 2013](https://banguat.gob.gt/sites/default/files/banguat/cuentasnac/PIB2013/resumidos/1.1_PIB_Tasa_de_Variacion_AR2013.pdf)

## Desastres y costos contextuales

La evaluación de Eta e Iota de la CEPAL se usa como contexto sobre vulnerabilidad y costos de desastres:

- [Evaluación de los efectos e impactos de Eta e Iota en Guatemala](https://www.cepal.org/es/publicaciones/46681-evaluacion-efectos-impactos-depresiones-tropicales-eta-iota-guatemala)

Estas cifras no se atribuyen causalmente a la deforestación, no se suman a la valoración forestal y se etiquetan como `Contexto no aditivo`.

El contexto de degradación de suelos procede de Castañeda Sánchez, Carrera y Rexhepi (2019), *Towards natural capital accounting in Guatemala: Synthesis report*, publicado por el Banco Mundial.

- [Informe de Castañeda Sánchez et al. (2019)](https://documents1.worldbank.org/curated/en/332151561104488571/pdf/Towards-Natural-Capital-Accounting-in-Guatemala-Synthesis-Report.pdf)

## Actualización y auditoría

Al actualizar una fuente se debe:

1. actualizar `00_trazabilidad_fuentes/registro_fuentes_saldo_forestal_guatemala.csv` y la fecha de acceso;
2. recalcular la huella SHA-256;
3. ejecutar la cadena de reproducción y las pruebas;
4. revisar si cambia el dominio, la interpretación o la citación.

No debe editarse manualmente un resultado para corregir el análisis. La corrección debe realizarse en el insumo, en las reglas o en el código y después reproducirse toda la cadena.
