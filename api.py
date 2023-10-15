from fastapi import FastAPI
import configparser
import psycopg2
from routers import refugios, sensors  
# Configuración
config = configparser.ConfigParser()
config.read('config.ini')

DB_NAME = config['DATABASE']['DB_NAME']
DB_USER = config['DATABASE']['DB_USER']
DB_PASS = config['DATABASE']['DB_PASS']
DB_HOST = config['DATABASE']['DB_HOST']
DB_PORT = config['DATABASE']['DB_PORT']

# Conexión a la base de datos
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

app = FastAPI()

# Incluye los routers
app.include_router(refugios.router)
app.include_router(sensors.router)  

