# Fuentes para una validación ecológica complementaria

Estas fuentes no son necesarias para repetir la *asignación documentada de municipios a grupos territoriales de referencia*. Se registran para evaluar las superficies reportadas como ganancia de cobertura mediante variables ambientales observables.

| Insumo | Fuente | Variable o uso |
|---|---|---|
| Códigos municipales | [INE](https://www.ine.gob.gt/sistema/uploads/2016/10/28/0NiM1ouoHaN67SRO2IzXZ5RNI7FeyHpn.xls) | Padrón y códigos administrativos |
| Polígonos municipales | [IGN–INAB](https://sig.inab.gob.gt/server/rest/services/Hosted/Municipios_DAD_2016_GTM_vista/FeatureServer/0) | Código, municipio, departamento y geometría |
| Ecosistemas forestales | [INAB](https://sig.inab.gob.gt/server/rest/services/Hosted/TipoEcosistemasGuatemala2/FeatureServer/0) | Latifoliado, coníferas, nuboso, seco, manglar y otras clases |
| Bosque nuboso | [INAB](https://sig.inab.gob.gt/server/rest/services/Hosted/Ecosistema_Bosque_Nuboso/FeatureServer/0) | Exclusión o estratificación específica |
| Ganancia forestal 2016–2020 | [INAB](https://sig.inab.gob.gt/server/rest/services/Din%C3%A1mica_de_la_cobertura_forestal_RASTER/MapServer) | Píxeles de pérdida, ganancia, bosque, no bosque y agua |
| Reserva de Biosfera Maya | [SIGAP–INAB](https://sig.inab.gob.gt/server/rest/services/Hosted/SIGAP_12_2021/FeatureServer/1) | Regla espacial verificable para Petén norte |
| Plantaciones registradas | [INAB 2020](https://sig.inab.gob.gt/server/rest/services/Hosted/Plantaciones_Forestales_2020/FeatureServer/0) y [plantaciones voluntarias](https://sig.inab.gob.gt/server/rest/services/Hosted/Plantaciones_Voluntarias/FeatureServer/1) | Exclusión o identificación parcial de plantaciones |
| Corredor Seco y FTN | [Biblioteca MAGA](https://apps.maga.gob.gt/sieagro/Normativas?categoriaId=18&clasificacionId=3&sortOrder=Descripcion_desc&tipoId=1) | Delimitaciones documentadas de 2010 |
| Elevación | [Copernicus DEM GLO-30](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM) o [NASA SRTMGL1 v003](https://www.earthdata.nasa.gov/data/catalog/lpcloud-srtmgl1-003) | Proporción de ganancia forestal por debajo de 1,000 m |

La variable territorial recomendable no es la elevación de la cabecera ni el promedio de todo el municipio. Para cada municipio (m) y clase ecológica (k), debe calcularse:

\[
p_{mk}
=
\frac{\operatorname{área}(R_m\cap E_k)}
{\operatorname{área}(R_m)},
\]

donde $R_m$ son las hectáreas de ganancia forestal 2016–2020 dentro del municipio y $E_k$ representa elevación, tipo de bosque u otra clase ambiental.

Antes de ejecutar esa validación debe fijarse una regla de asignación: mayoría absoluta, pluralidad, mezcla ponderada o exclusión de municipios sin una clase dominante. Los umbrales no deben calibrarse para reproducir artificialmente el conteo actual de 172 municipios.
