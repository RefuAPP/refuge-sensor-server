import psycopg2
import configparser

# Leer la configuración desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

DB_NAME = config['DATABASE']['DB_NAME']
DB_USER = config['DATABASE']['DB_USER']
DB_PASS = config['DATABASE']['DB_PASS']
DB_HOST = config['DATABASE']['DB_HOST']
DB_PORT = config['DATABASE']['DB_PORT']

# Conectar a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()
