import csv
import os
import re
import mysql.connector  # Cambiado a mysql.connector para unificar dependencias con tus otros servicios
import requests

# URL del endpoint del ENRE
URL_ENRE = "https://www.enre.gov.ar/mapaCortes/datos/Datos_PaginaWeb.js"


def parse_tipo(s):
    if "media" in s.lower():
        return "media"
    elif "baja" in s.lower():
        return "baja"
    return "alta"


def parse_empresa(s):
    return "Edesur" if "EDESUR" in s else "Edenor"


def _(s):
    return s


def dospuntos(s):
    return s.partition(": ")[-1].title().rstrip('"')


def number(s):
    return "".join(_ for _ in s if _.isdigit())


connection = None
cursor = None

try:
    # 1. Obtener datos desde la API/Web del ENRE
    print("🌐 Descargando datos desde el ENRE...")
    response = requests.get(URL_ENRE, timeout=30)
    response.raise_for_status()
    content = response.content.decode("utf8")
    print("✅ Datos descargados")

    # 2. Procesar Expresiones Regulares
    nuevos = []
    pattern = r"<h3>(EDENOR|EDESUR)<\/h3><p>\s*(\d+)\s*usuarios sin suministro electrico\.<\/p>"
    salida_1 = re.findall(pattern, content)
    print(f"📊 Resumen de cortes encontrado: {salida_1}")

    for incidente in re.findall(r"\[(\-.*?)\]", content):
        incidente = incidente.split(",")
        if len(incidente) == 11:
            # corte alta/media
            headers = {
                "latitud": _,
                "longitud": _,
                "nn": _,
                "tipo": parse_tipo,
                "empresa": parse_empresa,
                "partido": dospuntos,
                "localidad": dospuntos,
                "subestacion": dospuntos,
                "alimentador": dospuntos,
                "afectados": number,
                "normalizacion estimada": dospuntos,
            }
        else:
            headers = {
                "latitud": _,
                "longitud": _,
                "nn": _,
                "tipo": parse_tipo,
                "empresa": parse_empresa,
                "partido": dospuntos,
                "localidad": dospuntos,
                "afectados": number,
            }
        incidente = {
            header: f(value.strip())
            for (header, f), value in zip(headers.items(), incidente)
        }
        nuevos.append(incidente)

    salida_2 = nuevos

    # 3. Guardar reporte CSV local (Útil para logs o volúmenes del contenedor)
    csv_filename = "cortes_enre.csv"
    print(f"💾 Guardando copia local en {csv_filename}...")
    with open(csv_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "latitud",
                "longitud",
                "nn",
                "tipo",
                "empresa",
                "partido",
                "localidad",
                "subestacion",
                "alimentador",
                "afectados",
                "normalizacion estimada",
            ],
        )
        writer.writeheader()
        writer.writerows(nuevos)

    # 4. Conectar a la Base de Datos usando Variables de Entorno
    print("🔌 Conectando a la base de datos...")
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "192.168.0.121"),
        database=os.getenv("DB_NAME", "juanserver"),
        user=os.getenv("DB_USER", "ENRE"),
        password=os.getenv("DB_PASSWORD"),  # Obligatorio desde entorno
    )
    cursor = connection.cursor()

    # 5. Inserción masiva del resumen
    print("⬇️ Insertando resumen de cortes...")
    cursor.executemany(
        "INSERT INTO resumen_cortes (empresa, afectados) VALUES (%s, %s)",
        salida_1,
    )

    # 6. Preparar tablas para el detalle de cortes
    print("🧱 Preparando tablas temporales de detalles...")
    cursor.execute("DROP TABLE IF EXISTS juanserver.detalle_cortes_ro;")
    cursor.execute("DROP TABLE IF EXISTS juanserver.detalle_cortes_temp;")
    cursor.execute(
        "CREATE TABLE juanserver.detalle_cortes_ro LIKE juanserver.detalle_cortes;"
    )

    # 7. Iterar e insertar los detalles
    print("⬇️ Insertando detalle de cortes...")
    for item in salida_2:
        # Extraer y parsear de forma segura para evitar fallos de casteo
        try:
            lat = float(item["latitud"]) if item.get("latitud") else 0.0
            lon = float(item["longitud"]) if item.get("longitud") else 0.0
            afectados = (
                int(item["afectados"])
                if item.get("afectados") and item["afectados"].isdigit()
                else 0
            )
        except ValueError:
            continue  # Saltear filas con coordenadas corruptas

        query_params = (
            lat,
            lon,
            item.get("nn", "0"),
            item.get("tipo", "desconocido"),
            item.get("empresa", "desconocido"),
            item.get("partido", "desconocido"),
            item.get("localidad", "desconocido"),
            item.get("subestacion", "Desconocido"),
            item.get("alimentador", "Desconocido"),
            afectados,
            item.get("normalizacion estimada", "Sin Datos"),
        )

        # Insertar en tabla de lectura (_ro)
        cursor.execute(
            """
            INSERT INTO juanserver.detalle_cortes_ro 
            (latitud, longitud, nn, tipo, empresa, partido, localidad, subestacion, alimentador, afectados, normalizacion_estimada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            query_params,
        )

        # Insertar en tabla de backup (_bk)
        cursor.execute(
            """
            INSERT INTO juanserver.detalle_cortes_bk
            (latitud, longitud, nn, tipo, empresa, partido, localidad, subestacion, alimentador, afectados, normalizacion_estimada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            query_params,
        )

    # 8. Intercambio atómico de tablas (Swap)
    print("🔁 Renombrando tablas...")
    cursor.execute(
        "RENAME TABLE juanserver.detalle_cortes TO juanserver.detalle_cortes_temp, juanserver.detalle_cortes_ro TO juanserver.detalle_cortes;"
    )

    print("🧹 Limpiando tablas temporales...")
    cursor.execute("DROP TABLE juanserver.detalle_cortes_temp;")

    # Confirmar transacciones
    connection.commit()
    print("🚀 Proceso terminado con éxito. Datos actualizados en MariaDB/MySQL.")

except requests.RequestException as req_err:
    print(f"❌ Error de red/request con el ENRE: {req_err}")

except mysql.connector.Error as db_err:
    print(f"❌ Error en la base de datos: {db_err}")
    if connection:
        print("↩️ Ejecutando rollback...")
        connection.rollback()

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")

finally:
    # Garantizar el cierre de recursos siempre
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
        print("🔌 Conexión a la base de datos cerrada limpiamente.")