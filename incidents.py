import requests
from datetime import datetime, timedelta
import json
import pymysql

def obtener_datos_desde_api(url):
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return datos
    except requests.exceptions.RequestException as e:
        print("Error al obtener datos desde la API:", e)
        return None

def main():
    fecha_hora_actual = datetime.now()
    todos_los_datos = []

    for i in range(6):
        fecha_hasta = fecha_hora_actual - timedelta(days=i*5)
        fecha_desde = fecha_hasta - timedelta(days=5)
        fecha_desde_str = fecha_desde.strftime("%Y-%m-%dT00:00:00.000-03:00")
        fecha_hasta_str = fecha_hasta.strftime("%Y-%m-%dT00:00:00.000-03:00")
        url_api = f"https://api.cammesa.com/pub-svc/public/especial/perturbacionesSadiEventoFallaNotifENRE?fechadesde={fecha_desde_str}&fechahasta={fecha_hasta_str}"
        print(url_api)
        datos = obtener_datos_desde_api(url_api)
        if datos:
            todos_los_datos.extend(datos)

    if todos_los_datos:
        datos_json = json.dumps(todos_los_datos, indent=4, ensure_ascii=False)
        with open("datos_perturbaciones.json", "w", encoding="utf-8") as f:
            f.write(datos_json)
        
        config = {
            'host': 'xxx.xxx.xxx.xxx',
            'user': 'insertuser',
            'password': 'whoelse',
            'database': 'juanserver',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

        def insertar_datos(datos):
            connection = pymysql.connect(**config)
            try:
                with connection.cursor() as cursor:
                    for dato in datos:
                        sql = """
                        INSERT INTO perturbaciones (
                            tipo, fechaFalla, horaFalla, creado, modificado, causa, descripcion,
                            maquinas, potencia, potencia1, fechaFin, horaFin, equipos, lugar, 
                            fechaFin1, horaFin1, donde, area, libre, frase1, frase2, libre3, 
                            frase3, frase4, version
                        ) VALUES (
                            %(tipo)s, %(fechaFalla)s, %(horaFalla)s, %(creado)s, %(modificado)s, %(causa)s, %(descripcion)s,
                            %(maquinas)s, %(potencia)s, %(potencia1)s, %(fechaFin)s, %(horaFin)s, %(equipos)s, %(lugar)s, 
                            %(fechaFin1)s, %(horaFin1)s, %(donde)s, %(area)s, %(libre)s, %(frase1)s, %(frase2)s, %(libre3)s, 
                            %(frase3)s, %(frase4)s, %(version)s
                        )
                        """
                        cursor.execute(sql, dato)
                connection.commit()
            finally:
                connection.close()

        with open('datos_perturbaciones.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)

        insertar_datos(datos)

if __name__ == "__main__":
    main()
