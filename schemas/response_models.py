from typing import List, Dict, Any

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    timestamp: str = Field(example="2023-12-31 23:59:59", description="El timestamp del evento.")
    status: str = Field(example="Obstacle", description="El estado del sensor.")
    sensor_id: int = Field(example=1, description="El ID del sensor.")
    id_refugio: str = Field(example="d4504a10-9fe9-4006-aae6-2a399cd5a286", description="El ID del refugio.")
    password: str = Field(example="ChangeMe123", description="La contraseña para autenticación.")


# Respuestas de Error
class SuccessResponse(BaseModel):
    message: str = Field(..., example="Datos del sensor procesados correctamente.", description="Mensaje de éxito.")
    counter: int = Field(..., example=42, description="Contador actualizado.")


class SensorDataErrorResponse(BaseModel):
    error: str = Field(..., example="Hash inválido", description="Error genérico del sensor.")


class UnauthorizedResponse(BaseModel):
    detail: str = Field(..., example="Acceso no autorizado",
                        description="Acceso no autorizado debido a autenticación fallida.")


class ForbiddenResponse(BaseModel):
    detail: str = Field(..., example="Acceso prohibido", description="Acceso prohibido a este recurso.")


class NotFoundResponse(BaseModel):
    detail: str = Field(..., example="Refugio no encontrado", description="El refugio especificado no existe.")


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]] = Field(..., example=[
        {"loc": ["timestamp"], "msg": "value is not a valid datetime", "type": "type_error.datetime"}],
                                         description="Error de validación en los campos.")


class InternalServerErrorResponse(BaseModel):
    detail: str = Field(..., example="Error interno del servidor",
                        description="Ocurrió un error no previsto en el servidor.")


class SuccessResponse(BaseModel):
    message: str = Field(..., example="Datos del sensor procesados correctamente.", description="Mensaje de éxito.")

class LastActivityResponse(BaseModel):
    last_activity: str = Field(..., example="2023-12-31 23:59:59", description="Última hora de actividad registrada.")