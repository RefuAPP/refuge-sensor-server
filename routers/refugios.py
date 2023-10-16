from fastapi import APIRouter, HTTPException
from datetime import date, timedelta
from .db_config import cursor, conn  
from typing import List, Union, Dict
from schemas.daily_count_schemas import DailyCountResponse, WeeklyCountResponse, DayCount, IntervalCountResponse, UnauthorizedResponse, ForbiddenResponse, NotFoundResponse, ValidationErrorResponse, InternalServerErrorResponse
router = APIRouter()

@router.get("/refugio/{id_refugio}/daily_count/",
            response_model=DailyCountResponse,
            responses={
                200: {"description": "Operación exitosa", "model": DailyCountResponse},
                401: {"description": "Error: Unauthorized", "model": UnauthorizedResponse},
                403: {"description": "Error: Forbidden", "model": ForbiddenResponse},
                404: {"description": "Error: Not Found", "model": NotFoundResponse},
                422: {"description": "Validation Error", "model": ValidationErrorResponse},
                500: {"description": "Internal Server Error", "model": InternalServerErrorResponse}
            },
            summary="Obtiene el conteo diario de personas para un refugio específico",
            description="Si no se proporciona un día, se usa la fecha actual",
            response_description="Retorna el conteo diario y la fecha")
async def get_daily_count(id_refugio: str, day: date = None):
    if day is None:
        day = date.today()

    try:
        cursor.execute("""
            SELECT SUM(people_in) - SUM(people_out)
            FROM eventos
            WHERE id_refugio = %s AND DATE(timestamp) = %s
        """, (id_refugio, day))

        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Refugio no encontrado")

        daily_count = max(result[0], 0) if result[0] is not None else 0

        return {"daily_count": daily_count, "day": str(day)}
 
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/refugio/{id_refugio}/weekly_count_by_day/",
            response_model=Union[List[DayCount], Dict[str, str]],  
            responses={
                200: {"description": "Operación exitosa"},
                401: {"description": "Error: Unauthorized"},
                403: {"description": "Error: Forbidden"},
                404: {"description": "Error: Not Found"},
                422: {"description": "Validation Error"},
                500: {"description": "Internal Server Error"}
            },
            summary="Obtiene el conteo semanal de personas para un refugio específico, dividido por días",
            description="Si no se proporcionan fechas de inicio y fin, se usa la semana actual",
            response_description="Retorna el conteo semanal y el rango de fechas")
async def get_weekly_count_by_day(id_refugio: str, start_date: date = None, end_date: date = None):
    if start_date is None or end_date is None:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

    try:
        cursor.execute("""
            SELECT DATE(timestamp), SUM(people_in) - SUM(people_out)
            FROM eventos
            WHERE id_refugio = %s AND DATE(timestamp) BETWEEN %s AND %s
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        """, (id_refugio, start_date, end_date))

        result = cursor.fetchall()

        if result is None or len(result) == 0:
            return {"message": "No hay eventos"}

        weekly_data = [{"date": str(r[0]), "count": r[1]} for r in result]

        return weekly_data  

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/refugio/{id_refugio}/interval_count/",
            response_model=IntervalCountResponse,
            responses={
                200: {"description": "Operación exitosa"},
                401: {"description": "Error: Unauthorized", "model": UnauthorizedResponse},
                403: {"description": "Error: Forbidden", "model": ForbiddenResponse},
                404: {"description": "Error: Not Found", "model": NotFoundResponse},
                422: {"description": "Validation Error", "model": ValidationErrorResponse},
                500: {"description": "Internal Server Error", "model": InternalServerErrorResponse}
            },
            summary="Obtiene el número de entradas y salidas de personas para un refugio específico en un intervalo de fechas",
            description="Si no se proporcionan fechas de inicio y fin, se usa la semana actual",
            response_description="Retorna el número de personas que han entrado y salido")
async def get_interval_count(id_refugio: str, start_date: date = None, end_date: date = None):
    if start_date is None or end_date is None:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

    try:
        cursor.execute("""
            SELECT SUM(people_in), SUM(people_out)
            FROM eventos
            WHERE id_refugio = %s AND DATE(timestamp) BETWEEN %s AND %s
        """, (id_refugio, start_date, end_date))

        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Refugio no encontrado")

        people_in = result[0] if result[0] is not None else 0
        people_out = result[1] if result[1] is not None else 0

        return {"people_in": people_in, "people_out": people_out, "start_date": str(start_date), "end_date": str(end_date)}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))