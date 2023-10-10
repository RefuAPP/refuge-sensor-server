from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import configparser
import psycopg2
import hashlib

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

app = FastAPI()

class SensorData(BaseModel):
    timestamp: str
    status: str
    sensor_id: int
    id_refugio: str
    password: str  

counter = 0
ignore_until = {}
last_counter_update = datetime.min

@app.post("/sensor/")
async def update_counter(data: SensorData):
    received_hash = hashlib.sha256(data.password.encode()).hexdigest()
    
    cursor.execute("SELECT password_hash FROM refugios WHERE id_refugio = %s", (data.id_refugio,))
    result = cursor.fetchone()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
        
    stored_hash = result[0]

    if received_hash != stored_hash:
        print("Hash inválido")
        return {"error": "Hash inválido"}
    global counter
    global ignore_until
    global last_counter_update

    timestamp_str = data.timestamp
    current_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    print(f"Datos recibidos: {data.dict()}")
    print(f"Tiempo de ignorar hasta: {ignore_until}")
    print(f"Última actualización del contador: {last_counter_update}")

    people_in = 0
    people_out = 0

    if current_time > ignore_until.get(data.sensor_id, datetime.min) and current_time > (last_counter_update + timedelta(seconds=5)):
        if data.status == "Obstacle":
            if data.sensor_id == 1:
                counter += 1
                people_in = 1
                print("Sensor 1: Incrementar contador")
            elif data.sensor_id == 2:
                counter -= 1
                people_out = 1
                print("Sensor 2: Decrementar contador")
    else:
        print("Condición de tiempo no cumplida, ignorando este evento.")
        if data.sensor_id not in ignore_until:
            ignore_until[data.sensor_id] = datetime.min

    last_counter_update = current_time
    ignore_until[data.sensor_id] = current_time + timedelta(seconds=5)

    try:
        cursor.execute("SELECT 1;")
        print(f"Resultado de la consulta de diagnóstico: {cursor.fetchone()}")

        cursor.execute(
            "INSERT INTO Eventos (timestamp, id_refugio, people_in, people_out) VALUES (%s, %s, %s, %s)",
            (timestamp_str, data.id_refugio, people_in, people_out)  
        )
        conn.commit()

    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")

    print(f"Contador actual: {counter}, Gente entrando: {people_in}, Gente saliendo: {people_out}")
