# Alcance y limitaciones

## Alcance analítico

Este suplemento en línea reproduce la pérdida neta reportada por INAB y CONAP para 2016–2020, presenta resultados nacionales y desagregados y documenta el cálculo del saldo forestal ponderado.

La ponderación utiliza una *proporción de regeneración equivalente*. En esta aplicación, el parámetro procede de la recuperación relativa de biomasa aérea observada a los veinte años en los sitios de Poorter et al. (2016). No mide la edad ni la biomasa de la ganancia de cobertura registrada en Guatemala y no establece una equivalencia ecológica definitiva.

## Lo que sí puede sostenerse

- La igualdad $N=B-R$ se reproduce exactamente con la base municipal publicada por INAB y CONAP.
- La deforestación bruta, la ganancia de cobertura y la pérdida neta reportada se pueden comparar nacional, departamental y municipalmente.
- La proporción de regeneración equivalente puede aplicarse de forma transparente dentro de un dominio explícito.
- La *asignación documentada de municipios a grupos territoriales de referencia* permite repetir exactamente la partición 172/168/2 y los conteos por grupo 9/32/62/35/34.
- La completación conservadora permite construir un intervalo nacional sin extrapolar los parámetros regionales a los municipios excluidos.
- La deforestación bruta, la pérdida neta y el saldo ponderado se pueden valorar bajo un mismo valor unitario para mostrar diferencias de orden de magnitud.
- La evidencia estructural de manglar permite una comparación local, siempre que se mantenga separada de una estimación específica de cambios de cobertura de manglar.

## Lo que no puede sostenerse

### Equivalencia ecológica observada

La ganancia de cobertura reportada para 2016–2020 no contiene edad, origen, biomasa, composición, permanencia ni condición sucesional. Por ello, la proporción de regeneración equivalente no mide la condición actual de cada superficie clasificada como ganancia.

### Cobertura nacional homogénea de la proporción

Los intervalos se aplican a 172 municipios. Los otros 168 municipios no se imputan con una media nacional y las dos unidades lacustres se mantienen como registros no municipales. En ambos casos se conserva $B-R$ dentro de la suma nacional, sin interpretar el valor unitario como una proporción municipal asignada a los lagos. Esta decisión limita la aplicación de la proporción de regeneración equivalente y evita presentar una extrapolación como evidencia.

Las listas territoriales y la regla residual aseguran reproducibilidad computacional, pero no prueban que las hectáreas recuperadas de cada municipio sean empíricamente comparables con los sitios de referencia. Esa afirmación requiere la validación ecológica descrita en `01_metodologia/brechas_validacion_ecologica.md`.

### Cuenta de manglar

La aplicación local utiliza cambios forestales municipales totales y evidencia estructural de parcelas de manglar. No estima pérdida o ganancia específica de cobertura de manglar. El archivo reúne 75 registros de parcela para trece municipios, aunque el portal reporta 76 para el universo del servicio; únicamente 55 series multitemporales sostienen el intervalo 30/55–34/55. La discrepancia no se resuelve mediante una corrección manual.

### Valor nacional exhaustivo

El valor unitario se deriva de 21 estudios que cubrían cerca de 8 % del territorio y combinaban servicios y métodos. La valoración es una transferencia indicativa y no una cuenta nacional completa compatible, por sí sola, con el SCAE-CE. Los resultados monetarios no deben citarse sin su contraparte física ni sin el intervalo correspondiente.

### Atribución causal y distribución

La base no identifica agentes responsables, tenencia, cadenas productivas ni destinatarios de los servicios. Las clasificaciones territoriales no miden desempeño causal de gobiernos municipales ni bienestar. Los costos de Eta e Iota no se atribuyen a la deforestación y no se suman a la valoración forestal.

## Dominios que no deben sumarse

| Componente | Soporte | Uso correcto |
|---|---|---|
| Pérdida neta reportada por INAB y CONAP | 340 municipios y dos unidades lacustres | Reproducción nacional del balance de cobertura |
| Proporción de regeneración equivalente | 172 municipios mediante asignación documentada a grupos territoriales de referencia | Ponderación de la ganancia de cobertura |
| Completación conservadora | 342 unidades | Resultado nacional con el cálculo reportado fuera del dominio de aplicación |
| Aproximación local de manglar | 13 municipios, superpuestos con el dominio de aplicación | Contraste local de resultados |
| Costos de desastres | Agregados documentales | Contexto no aditivo |

Sumar la recuperación ponderada y la aproximación local de manglar duplicaría los trece municipios. Sumar costos de desastre a pérdidas forestales mezclaría conceptos, soportes y métodos incompatibles.

## Uso del suplemento en línea

El cuaderno reúne datos, métodos, resultados, controles y descargas reproducibles que permiten profundizar en los detalles del análisis. Sus tablas y figuras deben interpretarse junto con los supuestos, dominios y fuentes documentados; los resultados aislados no sustituyen una evaluación ecológica longitudinal ni una cuenta nacional de ecosistemas.
