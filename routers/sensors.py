from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import hashlib
from schemas.response_models import SensorData, SensorDataErrorResponse, UnauthorizedResponse, ForbiddenResponse, NotFoundResponse, ValidationErrorResponse, SuccessResponse
from .db_config import cursor, conn  

router = APIRouter()

counter = 0
ignore_until = {}
last_counter_update = datetime.min

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
    try:
        received_hash = hashlib.sha256(data.password.encode()).hexdigest()
        cursor.execute("SELECT password_hash FROM refugios WHERE id_refugio = %s", (data.id_refugio,))
        result = cursor.fetchone()
        
        if result is None:
            raise HTTPException(status_code=404, detail="Refugio no encontrado")
            
        stored_hash = result[0]
        
        if received_hash != stored_hash:
            raise HTTPException(status_code=401, detail="Hash inválido")
        
        global counter
        global ignore_until
        global last_counter_update

        timestamp_str = data.timestamp
        current_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        people_in = 0
        people_out = 0

        if current_time > ignore_until.get(data.sensor_id, datetime.min) and current_time > (last_counter_update + timedelta(seconds=5)):
            if data.status == "Obstacle":
                if data.sensor_id == 1:
                    counter += 1
                    people_in = 1
                elif data.sensor_id == 2:
                    counter -= 1
                    people_out = 1
            else:
                raise HTTPException(status_code=422, detail="Estado del sensor desconocido")

        last_counter_update = current_time
        ignore_until[data.sensor_id] = current_time + timedelta(seconds=5)

        cursor.execute(
            "INSERT INTO eventos (timestamp, id_refugio, people_in, people_out, current_count) VALUES (%s, %s, %s, %s, %s)",
            (timestamp_str, data.id_refugio, people_in, people_out, counter)
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
