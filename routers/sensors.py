from fastapi import APIRouter, HTTPException
from datetime import datetime
import hashlib
import logging
from schemas.response_models import SensorData, SensorDataErrorResponse, UnauthorizedResponse, ForbiddenResponse, NotFoundResponse, ValidationErrorResponse, SuccessResponse
from .db_config import cursor, conn

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/refugio/",
             response_model=None,
             responses={
                 200: {"description": "Operación exitosa", "model": SuccessResponse},
                 401: {"description": "Error: Unauthorized", "model": UnauthorizedResponse},
                 403: {"description": "Error: Forbidden", "model": ForbiddenResponse},
                 404: {"description": "Error: Not Found", "model": NotFoundResponse},
                 422: {"description": "Validation Error", "model": ValidationErrorResponse},
                 500: {"description": "Internal Server Error", "model": SensorDataErrorResponse}
            },
             summary="Actualiza la última actividad del sensor en un refugio",
             description="Este endpoint recibe datos del sensor y actualiza la última actividad en el refugio correspondiente.",
             response_description="Retorna un objeto que confirma que los datos del sensor se han procesado.")
async def update_sensor_activity(data: SensorData):
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

        cursor.execute(
            "UPDATE refugios SET last_activity = %s WHERE id_refugio = %s",
            (current_time, data.id_refugio)
        )
        conn.commit()
        logging.info(f"Última actividad actualizada: timestamp={data.timestamp}, id_refugio={data.id_refugio}")

    except Exception as e:
        logging.exception(f"Excepción no manejada: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))