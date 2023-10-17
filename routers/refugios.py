from fastapi import APIRouter, HTTPException
from datetime import date, timedelta
from .db_config import cursor, conn  
from schemas.daily_count_schemas import DailyCountResponse, IntervalCountResponse, UnauthorizedResponse, ForbiddenResponse, NotFoundResponse, ValidationErrorResponse, InternalServerErrorResponse
from fastapi.responses import JSONResponse

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
        cursor.execute("SELECT current_count FROM refugios WHERE id_refugio = %s", (id_refugio,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Refugio no encontrado")
        daily_count = result[0]

        return {"daily_count": daily_count, "day": str(day)}
 
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/refugio/{id_refugio}/weekly_count_by_day/",
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
@router.get("/refugio/{id_refugio}/weekly_count_by_day/",
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
        # Obtener el current_count de la tabla refugios
        cursor.execute("SELECT current_count FROM refugios WHERE id_refugio = %s", (id_refugio,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Refugio no encontrado")
        refugio_current_count = result[0]

        cursor.execute("""
            SELECT DATE(timestamp), current_count
            FROM (
                SELECT DATE(timestamp) as date, current_count
                FROM eventos
                WHERE id_refugio = %s AND DATE(timestamp) BETWEEN %s AND %s
                ORDER BY timestamp DESC
            ) as subquery
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp);

        """, (id_refugio, start_date, end_date))

        result = cursor.fetchall()
        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        db_results = {str(r[0]): r[1] for r in result}
        if str(date.today()) in db_results:
            db_results[str(date.today())] = refugio_current_count
        today_str = str(date.today())
        weekly_data = [
            {"date": str(d), "count": refugio_current_count if str(d) == str(date.today()) else db_results.get(str(d), 0)}
            for d in all_dates
        ]


        return JSONResponse(content={"weekly_data": weekly_data, "current_count": refugio_current_count}, status_code=200)

    except Exception as e:
        conn.rollback()
        return JSONResponse(content={"detail": str(e)}, status_code=500)
