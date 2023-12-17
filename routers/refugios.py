from fastapi import APIRouter, HTTPException
from datetime import datetime
from .db_config import conn
from schemas.daily_count_schemas import UnauthorizedResponse, ForbiddenResponse, NotFoundResponse, InternalServerErrorResponse
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/refugio/{id_refugio}",
            responses={
                200: {"description": "Operación exitosa"},
                401: {"description": "Error: Unauthorized"},
                403: {"description": "Error: Forbidden"},
                404: {"description": "Error: Not Found"},
                500: {"description": "Internal Server Error"}
            },
            summary="Obtiene la última actividad del sensor para un refugio específico",
            description="Retorna la última hora de actividad registrada por los sensores en el refugio",
            response_description="Retorna la última actividad")
async def get_last_activity(id_refugio: str):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT last_activity FROM refugios WHERE id_refugio = %s", (id_refugio,))
            result = cursor.fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Refugio no encontrado")
            last_activity = result[0]
            if last_activity is not None:
                last_activity = last_activity.isoformat()

        return JSONResponse(content={"last_activity": last_activity}, status_code=200)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/refugio/{id_refugio}",
            responses={
                200: {"description": "Operación exitosa"},
                401: {"description": "Error: Unauthorized"},
                403: {"description": "Error: Forbidden"},
                404: {"description": "Error: Not Found"},
                500: {"description": "Internal Server Error"}
            },
            summary="Actualiza la última actividad del sensor en un refugio",
            description="Actualiza la última hora de actividad registrada por los sensores en el refugio",
            response_description="Retorna un objeto que confirma que los datos del sensor se han procesado.")
async def update_last_activity(id_refugio: str):
    try:
        with conn.cursor() as cursor:
            current_time = datetime.now()
            cursor.execute("UPDATE refugios SET last_activity = %s WHERE id_refugio = %s", (current_time, id_refugio))
            conn.commit()
            return JSONResponse(content={"message": "Última actividad actualizada"}, status_code=200)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))