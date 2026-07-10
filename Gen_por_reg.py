import os
from datetime import datetime
import mysql.connector
import requests

# URL del endpoint
URL_API = "https://api.cammesa.com/demanda-svc/generacion/ObtieneGeneracioEnergiaPorRegion?id_region=1002"

connection = None
cursor = None

try:
    # 1. Obtener datos desde la API primero (si falla, no tocamos la Base de Datos)
    print("🌐 Solicitando datos a la API de CAMMESA...")
    response = requests.get(URL_API)
    response.raise_for_status()
    data = response.json()
    print("✅ Datos obtenidos correctamente")

    # 2. Conexión a la base de datos usando variables de entorno
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "juanserver"),
        user=os.getenv("DB_USER", "gen_reg"),
        password=os.getenv("DB_PASSWORD"),  # Se lee del entorno
    )
    cursor = connection.cursor()
    print("🔌 Conexión a MySQL establecida")

    # 3. Crear tabla temporal basada en la actual
    print("🧱 Preparando tabla temporal...")
    cursor.execute("DROP TABLE IF EXISTS generacion_por_region_tmp")
    cursor.execute(
        "CREATE TABLE generacion_por_region_tmp LIKE generacion_por_region"
    )

    # 4. Insertar datos en la tabla temporal
    print("⬇️ Insertando registros...")
    for row in data:
        fecha_str = row.get("fecha")
        if not fecha_str:
            continue

        # Truncar milisegundos si vienen en el string (ej: 2026-07-10T12:00:00.000)
        fecha = datetime.strptime(fecha_str[:19], "%Y-%m-%dT%H:%M:%S")

        cursor.execute(
            """
            INSERT INTO generacion_por_region_tmp 
            (fecha, sumTotal, hidraulico, termico, nuclear, renovable, importacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                fecha,
                row.get("sumTotal"),
                row.get("hidraulico"),
                row.get("termico"),
                row.get("nuclear"),
                row.get("renovable"),
                row.get("importacion"),
            ),
        )

    # 5. Intercambiar tablas de forma segura
    print("🔁 Intercambiando tablas atómicamente...")
    cursor.execute("DROP TABLE IF EXISTS generacion_por_region_old")
    cursor.execute(
        "RENAME TABLE generacion_por_region TO generacion_por_region_old"
    )
    cursor.execute(
        "RENAME TABLE generacion_por_region_tmp TO generacion_por_region"
    )
    cursor.execute("DROP TABLE generacion_por_region_old")

    # Confirmar cambios
    connection.commit()
    print("🚀 Datos actualizados correctamente con swap de tablas.")

except requests.RequestException as req_err:
    print(f"❌ Error al obtener los datos de la API: {req_err}")

except mysql.connector.Error as db_err:
    print(f"❌ Error de MySQL: {db_err}")
    if connection:
        print("↩️ Realizando Rollback debido al error")
        connection.rollback()

except Exception as e:
    print(f"❌ Error inesperado: {e}")

finally:
    # Asegurar el cierre de conexiones pase lo que pase
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
        print("🔌 Conexión a MySQL cerrada limpiamente")