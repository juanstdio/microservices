#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import io
import os
import zipfile
from datetime import datetime, timedelta
import mysql.connector
import requests

# ======================================================
# CONFIG (Constantes globales sin credenciales)
# ======================================================

NEMO = "PROGRAMACION_DIARIA"
API_DOCS_URL = "https://api.cammesa.com/pub-svc/public/findDocumentosByNemoRango"
API_ATTACHMENT_URL = (
    "https://api.cammesa.com/pub-svc/public/findAttachmentByNemoId"
)

TABLE_NAME = "despacho_rsf"
CSV_NAME_TARGET = "RF_GENERADORES.csv"
TIMEOUT = 30


def get_db_config():
    """Genera la configuración de BD leyendo el entorno en tiempo de ejecución."""
    return {
        "host": os.getenv("DB_HOST", "192.168.0.121"),
        "user": os.getenv("DB_USER", "juan"),
        "password": os.getenv("DB_PASSWORD"),  # Obligatorio en entorno
        "database": os.getenv("DB_NAME", "juanserver"),
        "autocommit": False,
    }


# ======================================================
# 0) HORA DE HOY
# ======================================================


def rango_hoy():
    hoy = datetime.now()
    desde = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
    hasta = desde + timedelta(days=1) - timedelta(milliseconds=1)

    return (
        desde.strftime("%Y-%m-%dT%H:%M:%S.000-03:00"),
        hasta.strftime("%Y-%m-%dT%H:%M:%S.000-03:00"),
    )


FECHA_DESDE, FECHA_HASTA = rango_hoy()


# ======================================================
# 1) DOCUMENTOS
# ======================================================


def log(msg):
    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True
    )


def buscar_documentos():
    print("[1] Consultando documentos CAMMESA…")
    r = requests.get(
        API_DOCS_URL,
        params={
            "fechadesde": FECHA_DESDE,
            "fechahasta": FECHA_HASTA,
            "nemo": NEMO,
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    docs = r.json()
    print(f"[1] Documentos encontrados: {len(docs)}")
    if not docs:
        raise RuntimeError("No se encontraron documentos para el rango de hoy")
    return docs


def seleccionar_documento(documentos):
    print("[2] Seleccionando documento más reciente…")
    doc = sorted(documentos, key=lambda x: x["version"], reverse=True)[0]
    adj = doc["adjuntos"][0]
    print("[2] docId:", doc["id"])
    print("[2] ZIP:", adj["nombre"])
    return doc["id"], adj["nombre"]


# ======================================================
# 2) ZIP
# ======================================================


def descargar_zip(doc_id, zip_name):
    print("[3] Descargando ZIP desde CAMMESA…")
    r = requests.get(
        API_ATTACHMENT_URL,
        params={"attachmentId": zip_name, "docId": doc_id, "nemo": NEMO},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    print(f"[3] ZIP descargado ({len(r.content)} bytes)")
    return io.BytesIO(r.content)


# ======================================================
# 3) PARSE RSF
# ======================================================


def leer_rsf(zip_bytes):
    print("[4] Abriendo ZIP…")
    registros = []

    with zipfile.ZipFile(zip_bytes) as z:
        archivos = z.namelist()
        print("[4] Archivos dentro del ZIP:", archivos)

        if CSV_NAME_TARGET not in archivos:
            raise RuntimeError(f"{CSV_NAME_TARGET} no existe en el ZIP")

        print(f"[4] Leyendo {CSV_NAME_TARGET}…")

        with z.open(CSV_NAME_TARGET) as f:
            raw = f.read()

        # Intentamos UTF-8 primero (para mitigar el BOM)
        try:
            text = raw.decode("utf-8-sig")
            print("[4] Encoding detectado: utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin1")
            print("[4] Encoding detectado: latin1")

        lines = text.splitlines()
        header_line = lines[0]

        # Detectar delimitador real dinámicamente
        delimiter = "," if header_line.count(",") > header_line.count(";") else ";"
        print(f"[4] Delimitador detectado: '{delimiter}'")

        reader = csv.reader(lines, delimiter=delimiter)

        headers = next(reader)
        headers = [h.strip() for h in headers]
        print("[4] Headers detectados:", headers)

        idx = {name: i for i, name in enumerate(headers)}

        if "TIPO_RF" not in idx:
            raise RuntimeError("No se encontró la columna TIPO_RF")

        for row in reader:
            if not row or len(row) < len(headers):
                continue

            if row[idx["TIPO_RF"]].strip() != "RSF":
                continue

            area = row[idx["AREA"]].strip()
            grupo = row[idx["GRUPO"]].strip()
            central = f"{area} {grupo}"

            for h in range(1, 25):
                val = row[idx[f"H{h:02d}"]].strip()
                try:
                    valor = float(val)
                except ValueError:
                    valor = 0.0

                registros.append((central, h, valor))

    print(f"[4] Registros RSF parseados: {len(registros)}")
    return registros


# ======================================================
# 4) INSERT DB
# ======================================================


def cargar_en_db(registros):
    if not registros:
        log("⚠️ No hay registros para cargar en la Base de Datos.")
        return

    log("Conectando a la base de datos...")
    config = get_db_config()
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor()

    try:
        log("Creando tabla temporal despacho_rsf_tmp")
        cur.execute("DROP TABLE IF EXISTS despacho_rsf_tmp")
        cur.execute(f"CREATE TABLE despacho_rsf_tmp LIKE {TABLE_NAME}")

        insert_sql = """
            INSERT INTO despacho_rsf_tmp (central, hora, valor)
            VALUES (%s, %s, %s)
        """

        log("Insertando datos en tabla temporal...")
        cur.executemany(insert_sql, registros)
        cnx.commit()

        log(f"✅ {cur.rowcount} filas insertadas transitoriamente")
        log("Iniciando swap atómico de tablas...")

        cur.execute("DROP TABLE IF EXISTS old_despacho_rsf")
        cur.execute(
            f"""
            RENAME TABLE
                {TABLE_NAME} TO old_despacho_rsf,
                despacho_rsf_tmp TO {TABLE_NAME}
        """
        )

        cur.execute("DROP TABLE old_despacho_rsf")
        cnx.commit()
        log("🚀 Swap completado correctamente.")

    except mysql.connector.Error as db_err:
        log(f"❌ Error en la base de datos durante la carga: {db_err}")
        print("↩️ Ejecutando rollback...")
        cnx.rollback()
        raise
    finally:
        cur.close()
        cnx.close()
        log("🔌 Conexión DB cerrada")


# ======================================================
# MAIN
# ======================================================


def main():
    print("======================================")
    print(" CAMMESA RSF INGEST - INICIO")
    print(" Fecha:", datetime.now())
    print("======================================")
    log(f"Cargando PROGRAMACION_DIARIA para fecha: {FECHA_DESDE[:10]}")

    try:
        documentos = buscar_documentos()
        doc_id, zip_name = seleccionar_documento(documentos)
        zip_bytes = descargar_zip(doc_id, zip_name)
        registros = leer_rsf(zip_bytes)
        cargar_en_db(registros)
    except Exception as e:
        log(f"❌ El microservicio falló críticamente: {e}")

    print("======================================")
    print(" CAMMESA RSF INGEST - FIN")
    print(" Fecha:", datetime.now())
    print("======================================")


if __name__ == "__main__":
    main()