# Script para obtener las últimas 12 imágenes del RADAR del INTA en paraná
# la salida del script es un video en MP4, require FFMPEG
# Creado en 2025 por Juan Blanc, Hobbista. 

import os
import requests
from datetime import datetime, timedelta
import subprocess

# Configuración inicial
base_url = "https://estaticos.smn.gob.ar/vmsr/radar/PAR_240_ZH_CMAX_"
output_dir = "imagenes_radar"
os.makedirs(output_dir, exist_ok=True)
max_images = 12
time_window_minutes = 240  # Buscar en las últimas 4 horas

# Obtener la hora actual UTC y redondearla al múltiplo de 10 minutos más cercano
now = datetime.utcnow()
minutes = now.minute
nearest_ten = (minutes // 10) * 10  # Redondea al múltiplo de 10 inferior
now = now.replace(minute=nearest_ten, second=0, microsecond=0)
print(f"Hora actual UTC ajustada: {now.strftime('%Y-%m-%d %H:%M:%SZ')}")

# Lista para almacenar las URLs válidas
valid_urls = []

# Probar URLs retrocediendo en intervalos de 10 minutos
for i in range(0, time_window_minutes, 10):  # Incrementos de 10 minutos
    timestamp = now - timedelta(minutes=i)
    base_timestamp_str = timestamp.strftime("%Y%m%d_%H%M")
    
    # Probar segundos de 01Z a 10Z
    for sec in range(1, 11):
        timestamp_str = f"{base_timestamp_str}{sec:02d}Z"
        url = f"{base_url}{timestamp_str}.png"
        
        # Verificar si la URL existe
        try:
            response = requests.head(url, timeout=2)
            print("probando url:",url)
            if response.status_code == 200:
                print(f"Encontrada imagen válida: {url}")
                valid_urls.append((timestamp_str, url))
                break  # Encontramos una válida, pasamos al siguiente intervalo
        except requests.RequestException:
            continue
    
    if len(valid_urls) >= max_images:
        break

# Si no encontramos suficientes imágenes, advertir
if len(valid_urls) < max_images:
    print(f"Solo se encontraron {len(valid_urls)} imágenes válidas.")
if len(valid_urls) == 0:
    print("No se encontraron imágenes. Abortando!!!")
    exit(1)

# Ordenar las imágenes por timestamp (de más antigua a más reciente)
valid_urls.sort()  # Ordena por timestamp_str

# Descargar las imágenes
downloaded_files = []
for timestamp_str, url in valid_urls:
    file_path = os.path.join(output_dir, f"PAR_240_ZH_CMAX_{timestamp_str}.png")
    print(f"Descargando {url} a {file_path}...")
    response = requests.get(url)
    with open(file_path, "wb") as f:
        f.write(response.content)
    downloaded_files.append(file_path)

# Crear el video con ffmpeg
output_video = "radar_video.mp4"
ffmpeg_cmd = [
    "ffmpeg",
    "-framerate", "2",
    "-pattern_type", "glob",
    "-i", f"{output_dir}/PAR_240_ZH_CMAX_*.png",
    "-vf", "scale=804:802,drawtext=text='@juanstdio_ups_bot':fontcolor=white:fontsize=24:x=(w-text_w-10):y=(h-text_h-10)", #Marca de agua
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-y",
    output_video
]
# Usamos ffmpeg porque es multicore.. nada mas
print("Creando video con ffmpeg...")
try:
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"Video creado exitosamente: {output_video}")
except subprocess.CalledProcessError as e:
    print(f"Error al crear el video: {e}")
