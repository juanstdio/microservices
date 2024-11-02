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
- [References](#references)
- [Contributing](#contribuciones)
- [Author](#author)
- [Gratitudes](#gratitudes)
- [License](#license)

## Incidents

Extrae las perturbaciones (Incidentes) del SADI en las últimas 5 semanas via API Pública y las carga en una base de Datos MySQL. Datos provistos amablemente por [CAMMESA](https://cammesaweb.cammesa.com/)
Ejemplo de visalización:
| tipo | fechaFalla | horaFalla | creado | modificado | causa | descripcion |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| 'Evento de Falla'	| '2024-05-26'|	 '00:00:00'	| '2024-05-26 00:00:00'	| NULL	| 'Se investigan.'	| '23:59:30 - Transnea: A las 23:21 h en E.T. Resistencia Norte desenganchó el TR1(132/33/13.2 kV) señalizando máxima corriente. Se produjeron 12.8 MW de cortes. Convocaron el técnico a la estación.'|

## Demandita
Genera una imagen PNG en tamaño 1920x1080 de la Demanda Actual del SADI vs el Predespacho (Demanda estimada). Datos provistos amablemente por [CAMMESA](https://cammesaweb.cammesa.com/) y extraídos desde una base de datos MySQL.

![](https://raw.githubusercontent.com/juanstdio/microservices/refs/heads/main/grafico_demanda_predespacho.png)


### Salto Grande - Datos Operativos

Extrae los datos operativos de la Represa Hidroeléctrica de Salto Grande y las carga en una base de datos MySQL. 
Datos provistos amablemente por [CTM Salto Grande](https://saltogrande.org/)
| idsaltogrande_explotacion |  HORA_FECHA_REPORTE |  PotI |  ETotal |  CaudalTur |  CaudalVer |  MaquinasDisp |  MaquinasActivas |  PotRotante |  avgCotaEmbalse |  avgCotaRestitu |  Temperatura |  SGU_T1 |  SGU_T2 |  SGA_GP |  SGA_RSM |  CE_T1 |  CE_T2 |  CE_CAMP |  CE_MERC |  CE_BELG |  TOTAL_SIS_URG |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| '3792' |  '2024-11-01 23:22:05' |  '888 MW' |  '30.255 MWh' |  '4.214 m3/s' |  '0 m3/s' |  '14' |  '14' |  '1.890 MW' |  '34 | 56 m' |  '8 | 09 m' |  '25 | 01 ÂºC' |  '66 MW' |  '68 MW' |  '394 MW' |  '82 MW' |  '58 MW' |  '122 MW' |  '318 MW' |  '69 MW' |  '192 MW' |  '-520 MW' |



## References

- [MariaDB MySQL](https://mariadb.org/)
- [MySQL Connector](https://www.mysql.com/products/connector/)
- [Requests](https://requests.readthedocs.io/en/latest/)
- [Beatiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [MatPlotLib](https://matplotlib.org/)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)

## Contribuciones

Las solicitudes de incorporación (_Pull Requests_) de cambios son bienvenidas. Para realizar cambios importantes, primero abra un problema (_issue_) para analizar lo que desea cambiar.
Asegúrese de actualizar las pruebas según corresponda.

## Author

- **Juan Blanc** - _Initial Development & Idea_ - [juanstdio](https://github.com/juanstdio)


## Gratitudes
- **Comision técnica Mixta de Salto Grande** - _Por Proveer los datos abiertamente_ - [CTM Salto Grande](https://saltogrande.org/)
- **Compañía Administradora del Mercado Mayorista Eléctrico S.A.** - _Por Proveer los datos abiertamente_ - [CAMMESA](https://cammesaweb.cammesa.com/)
- **Juan Gonzalez** & **Eze Fernandez** - _Porque siempre los molesto con alguna pregunta_ - [Juan Gonzalez](https://github.com/juanchixd) - [Eze Fernandez](https://github.com/ezefernandez93)


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```python
# Juanstdio's Microservices - Developed by Juan Blanc with the helf of Juan Gonzalez and Eze Fernandez - © 2024/2025
```
