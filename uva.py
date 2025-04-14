# Este script se conecta a la API del Banco Central de Argentina para descargar
# información histórica sobre el valor de la tasa UVA (Unidad de Valor Adquisitivo)
# correspondiente a los últimos 195 días. El proceso incluye los siguientes pasos:
#
# 1. **Autenticación y Configuración de la API**: Se configura la URL base de la API 
#    del Banco Central sin ninguna autenticación
#
# 2. **Petición HTTP**: El script realiza una solicitud HTTP GET a la API para obtener 
#    los datos históricos de la tasa UVA de los últimos 104 días. La fecha actual se usa 
#    para calcular el rango de los 180 días hacia atrás y 14 días posteriores.
#
# 3. **Procesamiento de Datos**: La respuesta de la API se recibe en formato JSON
#    El script procesa los datos para extraer solo la información relevante sobre la tasa UVA,
#    como la fecha y el valor de la tasa.
#
# 4. **Almacenamiento de Datos**: Los datos extraídos se almacenan en una base de datos
#
# 5. **Manejo de Errores**: El script incluye manejo de errores para capturar posibles problemas 
#    durante la conexión, la respuesta de la API o el procesamiento de los datos, proporcionando 
#    mensajes claros en caso de fallos.
#
# 6. **Automatización (opcional)**: El script puede configurarse para ejecutarse de forma 
#    automática en intervalos regulares (por ejemplo, cada día) para actualizar los datos.
#
# Este enfoque permite a los usuarios obtener datos históricos confiables sobre el valor de la 
# tasa UVA en Argentina para su análisis o integración en otras aplicaciones.

# Pensando por Juan Blanc en Diciembre 2024

import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

# Configuración de la base de datos como variable global
db_config = {
    'host': '111.111.111.111',
    'user': 'bcra',
    'password': 'missisipi',
    'database': 'bcra'
}

# Configuración de la URL
base_api_url = "https://api.bcra.gob.ar/estadisticas/v2.0/DatosVariable/31/{}/{}"

def respaldar_datos_actuales():
    """Clona los datos actuales de 'datos_uva' en 'datos_uva_anteriores'."""
    print("Respaldando datos actuales en 'datos_uva_anteriores'...")
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datos_uva_anteriores LIKE datos_uva;
        """)

        # Insertar brutamente datos actuales como histórico, se puede optimizar..
        cursor.execute("""
            INSERT INTO datos_uva_anteriores (idVariable, fecha, valor)
            SELECT idVariable, fecha, valor FROM datos_uva;
        """)

        connection.commit()
        print("Datos respaldados correctamente en 'datos_uva_anteriores'.")

    except Error as e:
        print(f"Error al respaldar los datos actuales: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Conexión a la base de datos cerrada.")

def obtener_rango_fechas():
    """Calcula las fechas desde hoy - 180 días hasta hoy + 14 días."""
    fecha_hoy = datetime.now()
    fecha_inicio = fecha_hoy - timedelta(days=180) #Ajustable!!
    fecha_fin = fecha_hoy + timedelta(days=14)

    return fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")

def obtener_datos_uva(url):
    print("Obteniendo datos del API...")
    try:
        response = requests.get(url,verify=False)  # si, el bcra no firma sus certificados
        response.raise_for_status()
        data = response.json()

        if data['status'] == 200 and 'results' in data:
            print(f"{len(data['results'])} registros obtenidos.")
            return data['results']
        else:
            print("Auch, la API devolvió un estado inesperado o no contiene resultados.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los datos del API: {e}")
        return []

def cargar_datos_en_db(data):
    """Carga los datos obtenidos en la tabla 'datos_uva'."""
    print("Conectando a la base de datos...")
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("drop table if exists bcra.datos_uva_ro;")
        cursor.execute("create table bcra.datos_uva_ro like bcra.datos_uva;")
        insert_query = """
            INSERT INTO datos_uva_ro (idVariable, fecha, valor)
            VALUES (%s, %s, %s)
        """

        print("Cargando datos en la base de datos...")
        for record in data:
            cursor.execute(insert_query, (record['idVariable'], record['fecha'], record['valor']))

        connection.commit()
        print("Datos cargados exitosamente.")
        cursor.execute("rename table bcra.datos_uva to bcra.datos_uva_temp, bcra.datos_uva_ro to bcra.datos_uva;")
        print("Truncando tabla vieja")
        cursor.execute("truncate table bcra.datos_uva_temp;")
        print("Dropeando tablas temporales")
        cursor.execute("drop table bcra.datos_uva_temp;")

    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Conexión a la base de datos cerrada.")

def main():
    fecha_inicio, fecha_fin = obtener_rango_fechas()
    print(f"Rango de fechas: {fecha_inicio} a {fecha_fin}")

    # Construir la URL
    api_url = base_api_url.format(fecha_inicio, fecha_fin)

    # Obtener datos del API
    datos_uva = obtener_datos_uva(api_url)

    # Cargar datos en la DB
    if datos_uva:
        respaldar_datos_actuales()  # Respaldar primero por el amor de dios
        cargar_datos_en_db(datos_uva)  # Ahora si
    else:
        print("No hay datos para cargar. Que onda?") #Seria muy RARO si pasa esto

if __name__ == "__main__":
    main()
