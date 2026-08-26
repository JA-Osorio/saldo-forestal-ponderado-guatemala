# Alcance y limitaciones

## Alcance analítico

Este repositorio reproduce el cálculo institucional de pérdida neta, presenta resultados nacionales y desagregados y hace explícita la proporción de recuperación restada.

El objetivo es cuantificar cuánto depende el diagnóstico de una decisión de contabilización con la información disponible y sus limitaciones documentadas. El ejercicio permite formular preguntas y orientar investigación futura; no establece una equivalencia ecológica definitiva.

## Lo que sí puede sostenerse

- La identidad \(N=B-R\) se reproduce exactamente con la base municipal disponible.
- La deforestación bruta, la recuperación y la pérdida neta se pueden comparar nacional, departamental y municipalmente.
- Las proporciones de recuperación de biomasa a veinte años pueden usarse de forma transparente para ponderar la recuperación dentro de un dominio explícito (Poorter et al., 2016).
- La completación conservadora permite construir un intervalo nacional sin extrapolar las proporciones regionales a los municipios excluidos.
- La deforestación bruta, la pérdida neta y el saldo ponderado se pueden valorar bajo un mismo valor unitario para mostrar diferencias de orden de magnitud.
- La evidencia estructural de manglar permite una comparación local, siempre que se mantenga separada de una estimación específica de cambios de cobertura de manglar.

## Lo que no puede sostenerse

### Equivalencia ecológica observada

La recuperación reportada para 2016–2020, medida como ganancia de cobertura forestal, no contiene edad, origen, biomasa, composición, permanencia ni condición sucesional. Por ello, `rho20` no mide la condición actual de cada superficie clasificada como ganancia. Es una proporción de recuperación de biomasa a veinte años.

### Cobertura nacional homogénea de las proporciones regionales

Las proporciones regionales se aplican a 172 municipios. Los demás municipios no se imputan con una media nacional; se mantienen bajo \(\rho=1\) en la completación conservadora. Esta decisión limita la aplicación del ponderador al dominio sustentado y evita presentar una extrapolación como evidencia.

### Cuenta de manglar

La aplicación local utiliza cambios forestales municipales totales y evidencia estructural de parcelas de manglar. No estima pérdida o ganancia específica de cobertura de manglar. El archivo reúne 75 registros de parcela para trece municipios, aunque el portal reporta 76 para el universo del servicio; únicamente 55 series multitemporales sostienen el intervalo 30/55–34/55. La discrepancia no se resuelve mediante una corrección manual.

### Valor nacional exhaustivo

El valor unitario se deriva de 21 estudios que cubrían cerca de 8 % del territorio y combinaban servicios y métodos. La valoración es una transferencia indicativa y no una cuenta nacional completa compatible, por sí sola, con el SCAE-CE. Los resultados monetarios no deben citarse sin su contraparte física ni sin el intervalo correspondiente.

### Atribución causal y distribución

La base no identifica agentes responsables, tenencia, cadenas productivas ni destinatarios de los servicios. Las clasificaciones territoriales no miden desempeño causal de gobiernos municipales ni bienestar. Los costos de Eta e Iota no se atribuyen a la deforestación y no se suman a la valoración forestal.

## Dominios que no deben sumarse

| Componente | Soporte | Uso correcto |
|---|---|---|
| Resultado institucional | 340 municipios y dos unidades lacustres | Reproducción nacional de cobertura |
| Proporciones de recuperación a veinte años | 172 municipios | Ponderación de la recuperación |
| Completación conservadora | 342 unidades | Resultado nacional con \(\rho=1\) fuera del dominio de aplicación |
| Aproximación local de manglar | 13 municipios, superpuestos con el dominio de aplicación | Contraste local de resultados |
| Costos de desastres | Agregados documentales | Contexto no aditivo |

Sumar la recuperación ponderada y la aproximación local de manglar duplicaría los trece municipios. Sumar costos de desastre a pérdidas forestales mezclaría conceptos, soportes y métodos incompatibles.

## Uso académico

El cuaderno reúne datos, métodos, resultados, controles y descargas reproducibles. Sus tablas y figuras deben interpretarse junto con los supuestos, dominios y fuentes documentados; los resultados aislados no sustituyen una evaluación ecológica longitudinal ni una cuenta nacional de ecosistemas.
