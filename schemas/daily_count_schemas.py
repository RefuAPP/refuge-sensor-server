from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DailyCountResponse(BaseModel):
    daily_count: int = Field(
        description='Daily count can be a negative or positive integer',
        example=42  
    )
    day: str = Field(
        min_length=10, max_length=10, description='Day must be in YYYY-MM-DD format',
        example='2023-10-10'
    )

class WeeklyCountResponse(BaseModel):
    weekly_count: int = Field(
        description='Weekly count can be a negative or positive integer',
        example=300  
    )
    start_date: str = Field(
        min_length=10, max_length=10, description='Start date must be in YYYY-MM-DD format',
        example='2023-10-01'
    )
    end_date: str = Field(
        min_length=10, max_length=10, description='End date must be in YYYY-MM-DD format',
        example='2023-10-07'
    )

class UnauthorizedResponse(BaseModel):
    detail: str = Field(..., example="Acceso no autorizado", description="Acceso no autorizado debido a autenticación fallida.")

class ForbiddenResponse(BaseModel):
    detail: str = Field(..., example="Acceso prohibido", description="Acceso prohibido a este recurso.")

class NotFoundResponse(BaseModel):
    detail: str = Field(..., example="Refugio no encontrado", description="El refugio especificado no existe.")

class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]] = Field(..., example=[{"loc": ["timestamp"], "msg": "value is not a valid datetime", "type": "type_error.datetime"}], description="Error de validación en los campos.")

class InternalServerErrorResponse(BaseModel):
    detail: str = Field(..., example="Error interno del servidor", description="Ocurrió un error no previsto en el servidor.")
