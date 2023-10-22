from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import hashlib
import logging
from schemas.response_models import SensorData, SensorDataErrorResponse, UnauthorizedResponse, ForbiddenResponse, \
    NotFoundResponse, ValidationErrorResponse, SuccessResponse
from .db_config import cursor, conn

logging.basicConfig(level=logging.INFO)

router = APIRouter()

counter = None  
last_activation_time = datetime.min  


async def initialize_counter(id_refugio: str):
    global counter
    cursor.execute("SELECT current_count FROM refugios WHERE id_refugio = %s", (id_refugio,))
    result = cursor.fetchone()
    if result:
        counter = result[0]


@router.post("/sensor/",
             response_model=None,
             responses={
                 200: {"description": "Operación exitosa", "model": SuccessResponse},
                 401: {"description": "Error: Unauthorized", "model": UnauthorizedResponse},
                 403: {"description": "Error: Forbidden", "model": ForbiddenResponse},
                 404: {"description": "Error: Not Found", "model": NotFoundResponse},
                 422: {"description": "Validation Error", "model": ValidationErrorResponse},
                 500: {"description": "Internal Server Error", "model": SensorDataErrorResponse}
             },
             summary="Actualiza el contador de personas en un refugio",
             description="Este endpoint recibe datos del sensor y actualiza el contador de personas en el refugio correspondiente.",
             response_description="Retorna un objeto que confirma que los datos del sensor se han procesado.")
async def update_counter(data: SensorData):
    global counter
    global last_activation_time

    if counter is None:  
        await initialize_counter(data.id_refugio)

    try:
        received_hash = hashlib.sha256(data.password.encode()).hexdigest()
        cursor.execute("SELECT password_hash FROM refugios WHERE id_refugio = %s", (data.id_refugio,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Refugio no encontrado")

        stored_hash = result[0]

        if received_hash != stored_hash:
            raise HTTPException(status_code=401, detail="Hash inválido")

        current_time = datetime.strptime(data.timestamp, '%Y-%m-%d %H:%M:%S')

        if (current_time - last_activation_time).seconds >= 5:
            people_in = 0
            people_out = 0
            logging.info(f"Intentando insertar: {data.timestamp}, {data.id_refugio}, {people_in}, {people_out}, {counter}")  
            if data.status == "Obstacle":
                if data.sensor_id == 1:
                    counter += 1
                    people_in = 1
                elif data.sensor_id == 2:
                    counter = max(0, counter - 1)
                    people_out = 1

            logging.info(f"Contador actualizado: {counter}")

            last_activation_time = current_time

            cursor.execute(
                "INSERT INTO eventos (timestamp, id_refugio, people_in, people_out, current_count) VALUES (%s, %s, %s, %s, %s)",
                (data.timestamp, data.id_refugio, people_in, people_out, counter)
            )
            logging.info(f"Evento insertado: timestamp={data.timestamp}, id_refugio={data.id_refugio}, people_in={people_in}, people_out={people_out}, counter={counter}")

            cursor.execute(
                "UPDATE refugios SET current_count = %s WHERE id_refugio = %s",
                (counter, data.id_refugio)
            )
            conn.commit()
            logging.info("Commit realizado.")
    except Exception as e:
        logging.exception(f"Excepción no manejada: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
