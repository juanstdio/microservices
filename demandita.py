import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configuración de la conexión a la base de datos
db_config = {
    'user': 'apiuser',        
    'password': 'Oopsie',  
    'host': 'xxx.xxx.xxx.xxx',         
    'database': 'juanserver'     
}
# Conexión y consulta
connection = mysql.connector.connect(**db_config)
# Consulta principal
query_main = "SELECT Fecha_Hora, DemHoy, Predespacho FROM cammesa_raw;"
df = pd.read_sql(query_main, connection)
query_additional = """
SELECT * FROM juanserver.cammesa_raw 
WHERE id = (SELECT id FROM juanserver.cammesa_raw WHERE DemHoy IS NULL LIMIT 1) - 1;
"""
additional_data = pd.read_sql(query_additional, connection)
connection.close()
# Convertir Fecha_Hora a tipo datetime
df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'])
df['Predespacho'] = df['Predespacho'].interpolate(method='linear')
# Identificar el máximo en DemHoy
max_demanda = df.loc[df['DemHoy'].idxmax()]
# Extraer el valor adicional (ajusta el nombre de la columna según tu estructura)
valor_adicional = additional_data['DemHoy'].values[0] if not additional_data.empty else None
# Graficar los datos
plt.figure(figsize=(19.2, 10.8))  # Tamaño de imagen 1920x1080
plt.plot(df['Fecha_Hora'], df['DemHoy'], label='Demanda', color='red', linewidth=1, marker='o', markersize=2)
plt.plot(df['Fecha_Hora'], df['Predespacho'], label='Pre Despacho', color='green', linewidth=1, marker='o', markersize=2)
# Configuración del gráfico
plt.xlabel('Fecha y Hora')
plt.ylabel('Demanda (MW)')
plt.title('Demanda | Pre Despacho Argentina')
plt.legend()
plt.grid(True)
# Formateo de fecha en el eje x
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Mostrar cada hora para evitar superposición
plt.gcf().autofmt_xdate(rotation=45)
# Anotar el punto máximo de DemHoy
plt.annotate(
    f'Máximo: {max_demanda["DemHoy"]:.2f} MW',
    xy=(max_demanda['Fecha_Hora'], max_demanda['DemHoy']),
    xytext=(max_demanda['Fecha_Hora'], max_demanda['DemHoy'] + 200),  # Posición de la etiqueta un poco más arriba
    arrowprops=dict(facecolor='blue', arrowstyle="->"),
    fontsize=10,
    color='red'
)
# Agregar un cuadro de texto con el valor adicional
if valor_adicional is not None:
    plt.text(
        0.95,  # Posición en el eje X
        0.95,  # Posición en el eje Y, ajusta según sea necesario
        f'Demanda actual: {valor_adicional:.2f} MW',
        fontsize=12,
        ha='right',
        va='top',
        transform=plt.gca().transAxes,
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
    )
# Guardar gráfico como PNG
plt.tight_layout()
plt.savefig("grafico_demanda_predespacho.png", dpi=100)  # Resolución 100 DPI
# Mostrar gráfico
plt.show()
