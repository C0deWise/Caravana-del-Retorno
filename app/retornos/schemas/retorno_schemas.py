"""
Schemas de validación para Retorno.
Define la estructura de entrada y salida de la API,
separando la representación HTTP del modelo de base de datos.
"""

from pydantic import BaseModel, Field
import datetime


class RetornoCreate(BaseModel):
    """Datos requeridos para crear un nuevo retorno."""
    re_año: int = Field(..., example=2024, description="Año del retorno")
    re_estado: str = Field(default="activo", example="activo", description="Estado del retorno")


class RetornoResponse(BaseModel):
    """Datos retornados tras crear o consultar un retorno."""
    re_codigo: int
    re_fecha_creacion: datetime.date
    re_año: int
    re_estado: str

    class Config:
        from_attributes = True