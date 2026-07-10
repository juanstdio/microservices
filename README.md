# microservices
Un lugar donde guardaré mis pequeños scripts para hacer cosas...

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Status](https://img.shields.io/badge/Status-stable-green)
![GitHub repo size](https://img.shields.io/github/repo-size/juanstdio/microservices)
![GitHub license](https://img.shields.io/github/license/juanstdio/microservices) 
![MySQL](https://shields.io/badge/MySQL-lightgrey?logo=mysql&style=plastic&logoColor=white&labelColor=blue)
![NumPy](https://img.shields.io/static/v1?label=+&logo=numpy&color=blue&message=NumPy)
## Contenido

- [Incidentes](#incidents)
- [Demanda](#demandita)
- [Generación por Región](#generación-por-región)
- [Programación Diaria RSF](#programación-diaria-rsf)
- [Cortes ENRE](#cortes-enre)
- [Observaciones SMN](#observaciones-smn)
- [UVA](#uva)
- [Radar](#radar)
- [References](#references)
- [Contributing](#contribuciones)
- [Author](#author)
- [Gratitudes](#gratitudes)
- [License](#license)

## Incidents

Extrae las perturbaciones (Incidentes) del SADI en las últimas 5 semanas via API Pública. Luego las carga en una base de Datos MySQL. Datos provistos amablemente por [CAMMESA](https://cammesaweb.cammesa.com/)
Ejemplo de visalización:
| tipo | fechaFalla | horaFalla | creado | modificado | causa | descripcion |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| 'Evento de Falla'	| '2024-05-26'|	 '00:00:00'	| '2024-05-26 00:00:00'	| NULL	| 'Se investigan.'	| '23:59:30 - Transnea: A las 23:21 h en E.T. Resistencia Norte desenganchó el TR1(132/33/13.2 kV) señalizando máxima corriente. Se produjeron 12.8 MW de cortes. Convocaron el técnico a la estación.'|

## Demandita
Genera una imagen PNG en tamaño 1920x1080 de la Demanda Actual del SADI y el Predespacho (Demanda estimada). Datos provistos amablemente por [CAMMESA](https://cammesaweb.cammesa.com/) y extraídos desde una base de datos MySQL.

![](https://raw.githubusercontent.com/juanstdio/microservices/refs/heads/main/grafico_demanda_predespacho.png)


### Salto Grande - Datos Operativos

Extrae los datos operativos de la Represa Hidroeléctrica de Salto Grande y las carga en una base de datos MySQL. 
Datos provistos amablemente por [CTM Salto Grande](https://saltogrande.org/)
| idsaltogrande_explotacion |  HORA_FECHA_REPORTE |  PotI |  ETotal |  CaudalTur |  CaudalVer |  MaquinasDisp |  MaquinasActivas |  PotRotante |  avgCotaEmbalse |  avgCotaRestitu |  Temperatura |  SGU_T1 |  SGU_T2 |  SGA_GP |  SGA_RSM |  CE_T1 |  CE_T2 |  CE_CAMP |  CE_MERC |  CE_BELG |  TOTAL_SIS_URG |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| '3792' |  '2024-11-01 23:22:05' |  '888 MW' |  '30.255 MWh' |  '4.214 m3/s' |  '0 m3/s' |  '14' |  '14' |  '1.890 MW' |  '34 | 56 m' |  '8 | 09 m' |  '25 | 01 ÂºC' |  '66 MW' |  '68 MW' |  '394 MW' |  '82 MW' |  '58 MW' |  '122 MW' |  '318 MW' |  '69 MW' |  '192 MW' |  '-520 MW' |

## Generación por Región

Extrae la generación de energía actual desglosada por tipo (térmica, hidráulica, nuclear, renovable e importación) para una región eléctrica específica. Realiza un swap atómico en la base de datos MySQL mediante tablas temporales para asegurar la disponibilidad. Datos provistos amablemente por [CAMMESA](https://cammesaweb.cammesa.com/).
| fecha | sumTotal | hidraulico | termico | nuclear | renovable | importacion |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| '2026-07-10 12:00:00' | 14500.2 | 3200.5 | 8500.1 | 1000.0 | 1200.3 | 599.3 |

## Programación Diaria RSF

Busca, selecciona la versión más reciente y descarga de forma automática los documentos adjuntos en formato ZIP de la Programación Diaria de CAMMESA. Se encarga de parsear dinámicamente el archivo plano `RF_GENERADORES.csv` (detectando codificación y delimitadores), filtra los registros de tipo **RSF** e inyecta masivamente las curvas horarias (H01 a H24) asociándolas a su respectiva central eléctrica en MySQL. Datos provistos amablemente por [CAMMESA](https://cammesaweb.cammesa.com/).

## Cortes ENRE

Scrapea en tiempo real los datos estructurados incrustados en los mapas del ENRE para consolidar el estado de cortes de suministro eléctrico de Edenor y Edesur. Genera de manera local un reporte en formato CSV (`cortes_enre.csv`) e impacta de manera optimizada los resúmenes y coordenadas geográficas de los detalles de baja, media y alta tensión en una base de datos MySQL. Datos provistos amablemente por el [ENRE](https://www.enre.gov.ar/).

## Observaciones SMN

Descarga diariamente los partes meteorológicos oficiales. Realiza el parseo regionalizado de las variables climáticas (temperatura, sensación térmica, humedad, presión y estado nuboso) para las diferentes ciudades argentinas y las almacena de forma segura en MySQL utilizando rotación de tablas temporales. Datos provistos amablemente por el [SMN](https://www.smn.gob.ar/).

## UVA

Script para obtener los últimos 195 días (histórica y futura) sobre el valor de la tasa UVA (Unidad de Valor Adquisitivo), el rango es configurable, pero a efectos demostrativos se dejó en 180 días para atrás y 14 días en adelante. Los datos son luego almacenados en una base de datos MySQL instalada localmente para luego ser convocadas por distintas APIs, de esta forma no se depende del BCRA para cada llamada y se logra verificar los datos.
Usando la versión 2.0 [Detalles de la API](https://www.bcra.gob.ar/Noticias/primera-api-BCRA.asp)

## Radar

Script para obtener las últimas 12 imágenes del Radar INTA localizado en Paraná, Entre ríos provisto por el [SMN](https://www.smn.gob.ar/radar). La _salida_ es un video en MP4 en resolución 804x802 a 2 FPS, resumiendo la última hora y 20 minutos de actividad. 
Las imágenes están disponibles cada 10 minutos, pero como el segundo es variable, el script se encarga de "encontrar" la imagen (recorre desde 1Z hasta 10Z)

![image](https://github.com/user-attachments/assets/f85f1031-0d99-43e4-b37d-16e9b51f9f04)

## Estado del Subte

Establece una conexión persistente a través del protocolo SignalR (Server-Sent Events) con los servidores de Metrovías/Emova para capturar flujos en streaming sobre el estado de la red de subtes de Buenos Aires. El script intercepta las cargas útiles, parsea los árboles HTML con BeautifulSoup y actualiza la base de datos MySQL **únicamente cuando se detectan variaciones reales** en el servicio de las líneas (A, B, C, D, E, H, Premetro).

## References

- [Servicio Meteorológico Nacional](https://www.smn.gob.ar/radar)
- [MariaDB MySQL](https://mariadb.org/)
- [MySQL Connector](https://www.mysql.com/products/connector/)
- [Requests](https://requests.readthedocs.io/en/latest/)
- [Curl CFFI (Advanced HTTP)](https://curl-cffi.readthedocs.io/)
- [Beautiful Soup 4](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [MatPlotLib](https://matplotlib.org/)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Python Dotenv](https://github.com/theofidry/pip-dotenv)

## Contribuciones

Las solicitudes de incorporación (_Pull Requests_) de cambios son bienvenidas. Para realizar cambios importantes, primero abra un problema (_issue_) para analizar lo que desea cambiar.
Asegúrese de actualizar las pruebas según corresponda.

## Author

- **Juan Blanc** - _Initial Development & Idea_ - [juanstdio](https://github.com/juanstdio)


## Gratitudes
- **Comision técnica Mixta de Salto Grande** - _Por Proveer los datos abiertamente_ - [CTM Salto Grande](https://saltogrande.org/)
- **Compañía Administradora del Mercado Mayorista Eléctrico S.A.** - _Por Proveer los datos abiertamente_ - [CAMMESA](https://cammesaweb.cammesa.com/)
- **Ente Nacional Regulador de la Electricidad** - _Por Proveer el estado de la red_ - [ENRE](https://www.enre.gov.ar/)
- **Juan Gonzalez** & **Eze Fernandez** - _Porque siempre los molesto con alguna pregunta_ - [Juan Gonzalez](https://github.com/juanchixd) - [Eze Fernandez](https://github.com/ezefernandez93)


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```python
# Juanstdio's Microservices - Developed by Juan Blanc with the help of Juan Gonzalez and Eze Fernandez - © 2024/2026
