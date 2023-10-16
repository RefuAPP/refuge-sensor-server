from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import hashlib
import logging  # Añadido para el logging
from schemas.response_models import SensorData, SensorDataErrorResponse, UnauthorizedResponse, ForbiddenResponse, NotFoundResponse, ValidationErrorResponse, SuccessResponse
from .db_config import cursor, conn  

# Configuración de logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()

counter = 0
last_activation_time = datetime.min  # Tiempo de la última activación del sensor

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
    global last_activation_time  # Tiempo de la última activación del sensor
    
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
        
        if last_activation_time is None or (current_time - last_activation_time).seconds >= 5:
            people_in = 0
            people_out = 0

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
            conn.commit()

    except Exception as e:
        logging.exception(f"Excepción no manejada: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

