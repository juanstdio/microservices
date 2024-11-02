import requests
from bs4 import BeautifulSoup
import subprocess
import datetime
import mysql.connector

# URL de la página web
url = 'https://saltogrande.org/datos_horarios.php'
# obteniendo tiempo
now = datetime.datetime.now()

# format the current date and time as a string
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
# Conexión MySQL
cnx = mysql.connector.connect(user='insertuser', password='insertpasswod',
                              host='xxx.xxx.xxx.xxx', database='juanserver')
cursor = cnx.cursor()
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Obtener el contenido HTML de la página
    html_content = response.text
    # Parsear el contenido HTML usando BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Encontrar la tabla de valores 
    table = soup.find('table')
    cells = table.find_all('td')
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    HF = timestamp
    #print(cells[3].text.strip()) #PotI
    #print(cells[5].text.strip()) #ETotal
    #print(cells[7].text.strip()) #CaudalTur
    #print(cells[9].text.strip()) #CaudalVer
    #print(cells[11].text.strip()) #MaquinasDisp
    #print(cells[13].text.strip()) #MaquinasActivas
    #print(cells[15].text.strip()) #PotRotante
    #print(cells[19].text.strip()) #avgCotaEmbalse
    #print(cells[21].text.strip()) #avgCotaRestitu
    #print(cells[23].text.strip()) #Temperatura
    #print(cells[37].text.strip()) #TOTAL_SIS_URG
    #print(cells[41].text.strip()) #SGU_T1
    #print(cells[43].text.strip()) #SGU_T2
    #print(cells[45].text.strip()) #SGA_GP
    #print(cells[47].text.strip()) #SGA_RSM
    #print(cells[49].text.strip()) #CE_T1
    #print(cells[51].text.strip()) #CE_T2
    #print(cells[53].text.strip()) #CE_CAMP
    #print(cells[55].text.strip()) #CE_MERC
    #print(cells[57].text.strip()) #CE_BELG
    #print(HF)
    # Prints comentados, solo para debug fueron usados
    #DEFINICION DE VARIABLES
    PotI =cells[3].text.strip() #PotI
    ETotal =cells[5].text.strip() #ETotal
    CaudalTur =cells[7].text.strip() #CaudalTur
    CaudalVer =cells[9].text.strip() #CaudalVer
    MaquinasD =cells[11].text.strip() #MaquinasDispisp 
    MaquinasA =cells[13].text.strip() #MaquinasActivasctivas 
    PotRotant =cells[15].text.strip() #PotRotantee 
    avgCotaEm =cells[19].text.strip() #avgCotaEmbalsebalse 
    avgCotaRe =cells[21].text.strip() #avgCotaRestitustitu 
    Temperatu =cells[23].text.strip() #Temperaturara
    TOTAL_SIS =cells[37].text.strip() #TOTAL_SIS_URG_URG 
    SGU_T1 =cells[41].text.strip() #SGU_T1
    SGU_T2 =cells[43].text.strip() #SGU_T2
    SGA_GP =cells[45].text.strip() #SGA_GP
    SGA_RSM =cells[47].text.strip() #SGA_RSM
    CE_T1 =cells[49].text.strip() #CE_T1
    CE_T2 =cells[51].text.strip() #CE_T2
    CE_CAMP =cells[53].text.strip() #CE_CAMP
    CE_MERC =cells[55].text.strip() #CE_MERC
    CE_BELG =cells[57].text.strip() #CE_BELG
    print("cargando datos...")
    sql = "INSERT INTO saltogrande_explotacion (HORA_FECHA_REPORTE,PotI,ETotal,CaudalTur,CaudalVer,MaquinasDisp,MaquinasActivas,PotRotante,avgCotaEmbalse,avgCotaRestitu,Temperatura,TOTAL_SIS_URG,SGU_T1,SGU_T2,SGA_GP,SGA_RSM,CE_T1,CE_T2,CE_CAMP,CE_MERC,CE_BELG ) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (HF,PotI,ETotal,CaudalTur,CaudalVer,MaquinasD,MaquinasA,PotRotant,avgCotaEm,avgCotaRe,Temperatu,TOTAL_SIS,SGU_T1,SGU_T2,SGA_GP,SGA_RSM,CE_T1,CE_T2,CE_CAMP,CE_MERC,CE_BELG)) 
    # Commit the changes to the database
    cnx.commit()
    print('Cargado saltogrande_explotacion!')
    cursor.close()
    cnx.close()
    print("listop")
else:
    print("Error al cargar la página:", response.status_code)
