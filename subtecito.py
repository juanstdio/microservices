#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import mysql.connector
import requests
from bs4 import BeautifulSoup


def get_db_config():
    """Genera la configuración de BD leyendo el entorno en tiempo de ejecución."""
    return {
        "host": os.getenv("DB_HOST", "192.168.0.121"),
        "user": os.getenv("DB_USER", "juan"),
        "password": os.getenv("DB_PASSWORD"),  # Obligatorio en entorno
        "database": os.getenv("DB_NAME", "meshtastic"),
    }


def obtener_ultimo_estado(cursor, linea):
    """Busca el último estado guardado para una línea específica."""
    query = "SELECT estado FROM estado_subte WHERE linea = %s ORDER BY fecha_registro DESC LIMIT 1"
    cursor.execute(query, (linea,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def guardar_en_db_optimizado(datos):
    """Se encarga de abrir la conexión y evaluar si hay cambios de estado."""
    conn = None
    cursor = None
    try:
        db_config = get_db_config()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insertados = 0
        for linea, estado_actual in datos:
            ultimo_estado = obtener_ultimo_estado(cursor, linea)

            # Solo insertamos si el estado cambió o si es la primera vez
            if ultimo_estado != estado_actual:
                sql = "INSERT INTO estado_subte (linea, estado) VALUES (%s, %s)"
                cursor.execute(sql, (linea, estado_actual))
                print(f"[*] CAMBIO DETECTADO - {linea}: {estado_actual}")
                insertados += 1

        conn.commit()

        if insertados > 0:
            print(f"--- Se registraron {insertados} cambios en la DB ---")
        else:
            print(
                "--- No hubo cambios en los servicios. Nada que guardar. ---"
            )

    except mysql.connector.Error as err:
        print(f"❌ Error en MySQL: {err}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def parsear_html_subte(html):
    """Analiza el snippet HTML recibido por streaming."""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("div", class_="row")
    lista_para_db = []

    print(f"\n{'LINEA':<12} | {'ESTADO'}")
    print("-" * 50)

    for row in rows:
        img = row.find("img")
        if img and "alt" in img.attrs:
            linea = img["alt"]
            estado_div = row.find("div", class_="col-9")
            estado = (
                estado_div.get_text(strip=True) if estado_div else "Sin datos"
            )

            print(f"{linea:<12} | {estado}")
            lista_para_db.append((linea, estado))

    return lista_para_db


def procesar_estado_subte():
    """Conecta con SignalR de Metrovías vía Server-Sent Events."""
    base_url = "https://aplicacioneswp.metrovias.com.ar/estadolineas/signalr"
    connection_data = '[{"name":"moveshape"}]'
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        print("🌐 Negociando token de conexión con Metrovías...")
        r_neg = requests.post(
            f"{base_url}/negotiate",
            params={
                "clientProtocol": "2.0",
                "connectionData": connection_data,
            },
            headers=headers,
            timeout=15,
        )
        r_neg.raise_for_status()
        token = r_neg.json()["ConnectionToken"]

        conn_params = {
            "transport": "serverSentEvents",
            "clientProtocol": "2.0",
            "connectionToken": token,
            "connectionData": connection_data,
        }

        print("🔌 Conectando al streaming (SSE) de Metrovías...")
        response = requests.get(
            f"{base_url}/connect",
            params=conn_params,
            headers=headers,
            stream=True,
            timeout=15,
        )
        response.raise_for_status()

        # Leemos el stream hasta interceptar la primera carga útil de datos válida
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: {"):
                    raw_json = decoded[5:].strip()
                    data = json.loads(raw_json)

                    if "M" in data and len(data["M"]) > 0:
                        mensaje = data["M"][0]
                        if "A" in mensaje and len(mensaje["A"]) > 0:
                            html_snippet = mensaje["A"][0]

                            # Parsear el HTML interno del mensaje
                            datos_subte = parsear_html_subte(html_snippet)

                            # Guardar de forma optimizada
                            if datos_subte:
                                guardar_en_db_optimizado(datos_subte)
                            return  # Cortamos el bucle una vez procesada la captura

    except requests.RequestException as req_err:
        print(f"❌ Error de comunicación de red: {req_err}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    procesar_estado_subte()