import psycopg2
from psycopg2 import sql

db_name = "refuapi"  
db_user = "alex"
db_pass = "contraseña"
db_host = "localhost"


conn = psycopg2.connect(dbname="postgres", user=db_user, password=db_pass, host=db_host)


conn.autocommit = True

cursor = conn.cursor()

try:
    # Crear la base de datos
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    print(f"Base de datos '{db_name}' creada exitosamente.")
except Exception as e:
    print(f"Error al crear la base de datos: {e}")

cursor.close()
conn.close()
