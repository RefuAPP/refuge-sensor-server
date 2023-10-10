
import psycopg2
from psycopg2 import sql

# Leer la configuración desde el archivo config.ini (o cualquier fuente que prefieras)
config = {
    'dbname': 'refuapi',
    'user': 'alex',
    'password': 'refuapi',
    'host': 'localhost',
    'port': 5432
}

# Conectar a la base de datos PostgreSQL
try:
    conn = psycopg2.connect(**config)
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
    exit(1)

# Crear un cursor
cursor = conn.cursor()

# Crear la tabla 'refugios' si no existe
create_refugios_table_query = """
CREATE TABLE IF NOT EXISTS refugios (
    id_refugio VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL
);
"""

cursor.execute(create_refugios_table_query)

# Crear la tabla 'Eventos' si no existe
create_eventos_table_query = """
CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    id_refugio VARCHAR(255) NOT NULL,
    people_in INT,
    people_out INT,
    eventos INT,
    FOREIGN KEY (id_refugio) REFERENCES refugios(id_refugio)
);
"""

cursor.execute(create_eventos_table_query)

# Insertar el refugio por defecto
insert_default_refugio_query = """
INSERT INTO refugios (id_refugio, password_hash) VALUES ('abc', '5838f4dcfe55322a350bdc09e866fcf57aed3916832d30db3e7d30af204f3c14')
ON CONFLICT (id_refugio) DO NOTHING;
"""

cursor.execute(insert_default_refugio_query)

# Confirmar los cambios y cerrar la conexión
conn.commit()
cursor.close()
conn.close()

print("Configuración de la base de datos completada.")
