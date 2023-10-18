import psycopg2

from setup_database import Configuration

DB_NAME = Configuration.get("DB_NAME")
DB_USER = Configuration.get("DB_USER")
DB_PASS = Configuration.get("DB_PASS")
DB_HOST = Configuration.get("DB_HOST")
DB_PORT = Configuration.get("DB_PORT")

# Conectar a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()
