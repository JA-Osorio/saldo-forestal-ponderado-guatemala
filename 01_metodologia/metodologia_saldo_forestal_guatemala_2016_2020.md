# Metodología

## 1. Unidad, periodo y convención de signo

La base forestal cubre el periodo acumulado 2016–2020 y contiene 342 unidades: 340 municipios y dos unidades lacustres no municipales. Los cálculos preservan los decimales originales; el redondeo se reserva para las tablas de comunicación.

Para una unidad territorial $i$:

- $B_i$: pérdida o deforestación bruta de cobertura forestal, en hectáreas;
- $R_i$: recuperación reportada, medida como ganancia de cobertura forestal, en hectáreas;
- $N_i$: pérdida neta institucional, en hectáreas.

Un saldo positivo representa pérdida; uno negativo representa ganancia. La identidad de la fuente es:

$$
N_i=B_i-R_i.
$$

La reproducción institucional verifica esta igualdad para cada unidad y reconcilia los agregados municipales, departamentales y nacionales.

Las magnitudes anuales 2016–2020 se obtienen dividiendo el acumulado entre cuatro:

$$
X_{i,\text{anual}}=\frac{X_{i,2016-2020}}{4}.
$$

Esta anualización es una tasa media del periodo, no una observación para cada año.

## 2. Problema de contabilización

El saldo neto es una identidad válida de cambio de cobertura. Su límite aparece cuando $R_i$ se interpreta como sustituto completo e inmediato de $B_i$, aunque la base de cobertura no identifica edad, biomasa, origen, composición, permanencia, manejo ni equivalencia de servicios ecosistémicos.

Para hacer visible esa decisión se utiliza:

$$
H_i(\rho)=B_i-\rho_iR_i,
$$

donde $\rho_i\in[0,1]$ es la proporción de recuperación reconocida en cada caso.

| Caso de cálculo | Proporción | Interpretación |
|---|---:|---|
| Deforestación bruta | $\rho=0$ | No resta la recuperación |
| Pérdida neta institucional | $\rho=1$ | Resta toda la recuperación |
| Saldo ponderado | $\rho=\rho_{20}$ | Resta una proporción de recuperación de biomasa a veinte años |

El ejercicio no afirma que la superficie reportada como ganancia de cobertura tenga veinte años. Usa deliberadamente ese horizonte generoso para preguntar si, incluso bajo una recuperación prolongada, la resta completa está respaldada por la evidencia de biomasa.

## 3. Proporciones regionales de recuperación de biomasa a veinte años

Poorter et al. (2016) estiman la recuperación de biomasa aérea de bosques secundarios neotropicales veinte años después del abandono. El repositorio utiliza esos valores como fuente de intervalos regionales para ponderar la recuperación, no como medición directa de las ganancias de cobertura reportadas en Guatemala.

Los municipios se asignan a cinco regiones de referencia mediante **correspondencia territorial experta codificada**: listas explícitas de códigos y una regla residual, documentadas en `01_metodologia/reglas_correspondencia_territorial_experta_codificada.json`. El dominio contiene 172 municipios; quedan fuera 168 municipios del altiplano, bosques montanos, coníferas u otras condiciones sin correspondencia defendible, además de las dos unidades lacustres. Los conteos son 9, 32, 62, 35 y 34 para `REG-PET-N`, `REG-PET-FTN`, `REG-TB-HUM`, `REG-ORI-EST` y `REG-SEC-MOT`, respectivamente.

La asignación es reproducible, pero no constituye todavía una validación ecológica de las hectáreas recuperadas. Esa validación requiere cruces espaciales con elevación, tipo de bosque, estacionalidad y otras variables ambientales.

Para cada municipio elegible se conservan $\rho_{20}^{\min}$, $\rho_{20}^{\text{central}}$ y $\rho_{20}^{\max}$. Como $H$ disminuye cuando $\rho$ aumenta, los límites del saldo se orientan así:

$$
H_i^{\inf}=B_i-\rho_{20,i}^{\max}R_i,
\qquad
H_i^{\sup}=B_i-\rho_{20,i}^{\min}R_i.
$$

Por tanto, “inferior” y “superior” se refieren a la magnitud de pérdida ponderada, no al valor de la proporción.

La clasificación municipal utiliza el intervalo completo:

- **Pérdida:** $H_i^{\inf}>0$;
- **Ganancia:** $H_i^{\sup}<0$;
- **Indeterminado:** el intervalo contiene cero.

La proporción crítica, disponible para análisis posterior, es:

$$
\rho_i^*=\frac{B_i}{R_i},\qquad R_i>0.
$$

Indica qué proporción de recuperación sería necesaria para neutralizar la pérdida. No identifica causas ni desempeño institucional.

## 4. Dominio de aplicación y completación nacional conservadora

Los resultados se publican en tres niveles separados:

1. dominio de aplicación de 172 municipios;
2. resultados municipales dentro del dominio;
3. completación nacional conservadora.

La completación evita extrapolar las proporciones a ecosistemas incompatibles:

$$
H_{GT}^{\inf}
=
\sum_{i\in P}\left(B_i-\rho_{20,i}^{\max}R_i\right)
+
\sum_{i\notin P}(B_i-R_i),
$$

$$
H_{GT}^{\sup}
=
\sum_{i\in P}\left(B_i-\rho_{20,i}^{\min}R_i\right)
+
\sum_{i\notin P}(B_i-R_i),
$$

donde $P$ es el dominio elegible. Fuera de $P$ se conserva $\rho=1$, el supuesto institucional más favorable a la compensación.

Esta operación produce un resultado nacional sin llamar “nacional” al subtotal de 172 municipios. No resuelve la falta de evidencia específica para los ecosistemas excluidos; la hace explícita.

## 5. Aproximación local para municipios con evidencia estructural de manglar

La evidencia del portal del INAB se resume en trece municipios. El archivo analítico registra 75 observaciones de parcela, mientras el portal menciona 76 para el universo del servicio. Esa diferencia se conserva y no se corrige manualmente. Solo 55 series multitemporales comparables sustentan el intervalo utilizado:

- 30 aumentan conjuntamente carbono y área basal;
- 21 disminuyen ambas variables;
- cuatro tienen trayectoria mixta.

El intervalo estructural local se representa con $\omega_m$. Las 55 series
comparables equivalen al 73.3 % de las 75 observaciones contenidas en el archivo
analítico:

$$
\omega_m^{\min}=\frac{30}{55}=0.5455,
\qquad
\omega_m^{\max}=\frac{30+4}{55}=0.6182.
$$

Los saldos se calculan como:

$$
H_{i,m}^{\inf}=B_i-\omega_m^{\max}R_i,
\qquad
H_{i,m}^{\sup}=B_i-\omega_m^{\min}R_i.
$$

La orientación de los límites se debe a que
$\partial H_{i,m}/\partial\omega_m=-R_i\leq0$. La clasificación utiliza una
tolerancia numérica $\varepsilon=10^{-8}$: hay pérdida cuando
$H_{i,m}^{\inf}>\varepsilon$, ganancia cuando
$H_{i,m}^{\sup}<-\varepsilon$ e indeterminación cuando el intervalo contiene
cero dentro de esa tolerancia.

Esta es una aproximación local para municipios con evidencia estructural de manglar. $B_i$ y $R_i$ siguen siendo cambios forestales municipales totales de la base general; no son cambios exclusivos de cobertura de manglar. La proporción estructural local y la proporción de recuperación de biomasa a veinte años (Poorter et al., 2016) miden fenómenos distintos. Los resultados se comparan sobre los mismos trece municipios, pero no se promedian ni se suman.

## 6. Síntesis de resultados físicos

La comparación nacional mantiene visibles tres magnitudes:

1. deforestación bruta, $B$;
2. saldo ponderado por recuperación, $H(\rho_{20})$;
3. pérdida neta institucional, $N$.

Las brechas no se interpretan como nueva superficie observada. Expresan el efecto aritmético de cambiar la proporción de recuperación reconocida.

En el dominio de aplicación también se calculan, para usos de investigación posteriores:

$$
G_i(\rho)=H_i(\rho)-N_i=(1-\rho_i)R_i.
$$

El cuaderno público conserva las variables necesarias, pero no presenta una narrativa política de “ganadores y perdedores”. Esa interpretación requiere datos de tenencia, agentes causales, uso de la tierra y distribución de servicios que no están en la base.

## 7. Valoración económica indicativa

La cadena de cálculo lee el valor unitario, el factor de homologación, la tasa
central y los horizontes directamente de
`01_metodologia/parametros/parametros_valoracion_servicios_ecosistemicos_guatemala_2019_2026.csv`.
La misma tabla conserva los valores de la versión 1.0.0. Las constantes del
código son valores predeterminados para funciones aisladas y no sustituyen el
archivo de entrada en la cadena principal.

La valoración parte de un valor medio documentado de Q22,553 por ha/año a precios de 2019, derivado de 21 estudios sobre aproximadamente 9,403 km². Se homologa a 2026 mediante un factor de 1.32960218275:

$$
v_{2026}=22{,}553\times1.32960218275
=29{,}986.52\ \text{Q/ha/año}.
$$

Para una pérdida física anual $L$, el flujo anual indicativo no generado es:

$$
F=L\,v_{2026}.
$$

El valor presente de una cohorte anual, con tasa $r$ y horizonte $T$, es:

$$
VP_{\text{cohorte}}=F\left(\frac{1-(1+r)^{-T}}{r}\right).
$$

El caso central usa $r=4\%$ y $T=25$ años; la sensibilidad utiliza 2 %, 4 % y 5 %. Para diez cohortes 2026–2035, cada cohorte se descuenta al inicio del horizonte:

$$
VP_{10}=\sum_{t=1}^{10}
\frac{L_t\,v_{2026}}{(1+r)^t}
\left(\frac{1-(1+r)^{-T}}{r}\right).
$$

El flujo anual, el valor presente de una cohorte y el valor presente de diez cohortes son conceptos diferentes y no se suman. La transferencia uniforme replica la distribución física; no identifica variación espacial del valor por hectárea.

## 8. Escenarios 2026–2035

Los escenarios distinguen la proporción de recuperación reconocida de la trayectoria futura. Para cada escenario $s$:

$$
H_{i,s}=m_s^B B_i-\rho_i m_s^R R_i,
$$

donde $m_s^B$ y $m_s^R$ modifican por separado la pérdida bruta y la recuperación. Esta formulación evita llamar “restauración” a un escenario que solo reduce $B$. En la cadena de cálculo, cualquier escenario denominado restauración debe aumentar explícitamente el multiplicador de recuperación.

Los flujos base se anualizan y se mantienen constantes dentro de cada trayectoria de diez años. Son ejercicios comparativos, no pronósticos probabilísticos.

## 9. Costos contextuales y desastres

Los costos de degradación, contaminación, Eta e Iota se conservan en una tabla separada con `uso_analitico = Contexto no aditivo`. No se suman a la valoración forestal ni se presentan como daños causados por la deforestación. Su función es mostrar la relevancia económica de la vulnerabilidad ecosistémica sin formular una atribución causal que las fuentes no permiten.

## 10. Controles

La cadena de cálculo verifica, como mínimo:

- 342 unidades y 340 municipios;
- unicidad de los códigos municipales;
- identidad $N=B-R$ por unidad;
- 172 municipios elegibles en el dominio de aplicación;
- proporciones dentro de $[0,1]$ y límites ordenados;
- orientación correcta de los intervalos;
- 55 series multitemporales PPM y reconciliación 30 + 21 + 4;
- trece municipios en la aproximación local;
- superposición y no aditividad entre la recuperación ponderada y la aproximación local de manglar;
- coherencia de agregados y parámetros de valoración.

Los resultados de cada ejecución se registran en `05_verificacion/controles_calidad_saldo_forestal_guatemala_2016_2020.csv`. El manifiesto incluido en el paquete integral enumera tamaño y SHA-256 de cada miembro, salvo el propio manifiesto para evitar una referencia circular.
