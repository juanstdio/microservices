#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import locale
import os
from datetime import datetime
import mysql.connector
from curl_cffi import requests as curl_requests

# URL base del archivo del SMN
URL_BASE = (
    "https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/"
)


def get_db_config():
    """Genera la configuración de BD leyendo el entorno en tiempo de ejecución."""
    return {
        "host": os.getenv("DB_HOST", "192.168.0.121"),
        "user": os.getenv("DB_USER", "SMN"),
        "password": os.getenv("DB_PASSWORD"),  # Obligatorio en entorno
        "database": os.getenv("DB_NAME", "SMN"),
    }


def obtener_nombre_archivo():
    """Genera el nombre del archivo basado en la fecha actual UTC."""
    hoy = datetime.utcnow()
    return f"tiepre{hoy.strftime('%Y%m%d')}.txt"


def descargar_archivo(nombre_archivo):
    """Descarga el archivo desde la URL usando curl_cffi."""
    url_completa = f"{URL_BASE}{nombre_archivo}"
    print(f"🌐 Descargando archivo desde: {url_completa} (usando curl_cffi)")

    try:
        response = curl_requests.get(
            url_completa,
            impersonate="chrome101",
            timeout=30,
        )

        if response.status_code == 200:
            with open(nombre_archivo, "wb") as f:
                f.write(response.content)
            print(f"✅ Archivo {nombre_archivo} descargado correctamente.")
            return nombre_archivo
        else:
            raise RuntimeError(
                f"No se pudo descargar el archivo: {response.status_code} ({response.reason})"
            )
    except Exception as e:
        raise RuntimeError(f"Error en curl_cffi: {e}")


def limpiar_tabla(cursor):
    """Limpia la tabla antes de cargar nuevos datos."""
    print("🔁 Dropeando tabla temporal vieja")
    cursor.execute("DROP TABLE IF EXISTS SMN.observaciones_meteorologicas_ro;")
    print("🧱 Creando tabla como la original")
    cursor.execute(
        "CREATE TABLE SMN.observaciones_meteorologicas_ro LIKE SMN.observaciones_meteorologicas;"
    )


def cargar_datos(cursor, archivo):
    """Carga los datos desde el archivo en la tabla."""
    # Configurar locale regional de forma segura
    try:
        locale.setlocale(locale.LC_TIME, "es_AR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "es_AR")
        except locale.Error:
            print(
                "⚠️ No se pudo establecer locale es_AR, se intentará parsear de todas formas."
            )

    print("⬇️ Insertando registros meteorológicos...")
    with open(archivo, "r", encoding="latin-1") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 10:  # Verifica columnas mínimas
                continue

            ciudad = row[0].strip()
            fecha_original = row[1].strip()
            hora = row[2].strip()
            nubes = row[3].strip()
            visibilidad = row[4].strip()
            temperatura = row[5].replace("No se calcula", "NULL").strip()
            sensacion_termica = row[6].replace("No se calcula", "NULL").strip()
            humedad = row[7].strip()
            viento = row[8].strip()
            presion = row[9].strip()

            # Convertir fecha al formato 'YYYY-MM-DD'
            try:
                fecha = datetime.strptime(fecha_original, "%d-%B-%Y").strftime(
                    "%Y-%m-%d"
                )
            except ValueError as e:
                print(
                    f"⚠️ Error al convertir la fecha '{fecha_original}': {e}"
                )
                continue

            # Casteos seguros frente a strings vacíos o corruptos
            try:
                temp_val = (
                    None
                    if temperatura == "NULL" or not temperatura
                    else float(temperatura)
                )
                st_val = (
                    None
                    if sensacion_termica == "NULL" or not sensacion_termica
                    else float(sensacion_termica)
                )
                hum_val = int(humedad) if humedad.isdigit() else None
            except ValueError:
                continue

            query = """
            INSERT INTO SMN.observaciones_meteorologicas_ro (
                ciudad, fecha, hora, nubes, visibilidad, temperatura, 
                sensacion_termica, humidity, direccion_viento, presion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Nota: Asegúrate de mapear "humidity" o "humedad" según el nombre exacto en tu BD original
            cursor.execute(
                query,
                (
                    ciudad,
                    fecha,
                    hora,
                    nubes,
                    visibilidad,
                    temp_val,
                    st_val,
                    hum_val,
                    viento,
                    presion,
                ),
            )


def main():
    conn = None
    cursor = None
    archivo_descargado = None

    try:
        # Generar nombre y descargar primero
        nombre_archivo = obtener_nombre_archivo()
        archivo_descargado = descargar_archivo(nombre_archivo)

        # Conectar a la base de datos
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Operaciones de BD
        limpiar_tabla(cursor)
        cargar_datos(cursor, archivo_descargado)

        # Confirmar inserciones iniciales
        conn.commit()
        print("✅ Data nueva insertada en tabla transitoria")

        # Swap de tablas atómico
        print("🔁 Renombrando tablas...")
        cursor.execute(
            "RENAME TABLE SMN.observaciones_meteorologicas TO SMN.om_temp, SMN.observaciones_meteorologicas_ro TO SMN.observaciones_meteorologicas;"
        )

        print("🧹 Eliminando tabla vieja obsoleta...")
        cursor.execute("DROP TABLE SMN.om_temp;")
        conn.commit()
        print("🚀 Proceso SMN finalizado exitosamente.")

    except Exception as e:
        print(f"❌ Error crítico en el microservicio: {e}")
        if conn:
            print("↩️ Ejecutando rollback...")
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("🔌 Conexión a la base de datos cerrada.")

        # Limpieza opcional del archivo plano local descargado
        if archivo_descargado and os.path.exists(archivo_descargado):
            try:
                os.remove(archivo_descargado)
                print(f"🗑️ Archivo local temporal {archivo_descargado} removido.")
            except Exception:
                pass


if __name__ == "__main__":
    main()