# microservices
Un lugar donde guardaré mis pequeños scripts para hacer cosas...

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=black)
![Status](https://img.shields.io/badge/Status-stable-green)
![GitHub repo size](https://img.shields.io/github/repo-size/juanstdio/microservices)
![GitHub license](https://img.shields.io/github/license/juanstdio/microservices) 
## Table of Contents

- [Incidentes](#incidents)
- [Demanda](#demandita)
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


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
