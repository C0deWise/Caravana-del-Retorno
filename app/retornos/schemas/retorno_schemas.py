"""
Schemas de validación para Retorno.
Define la estructura de entrada y salida de la API,
separando la representación HTTP del modelo de base de datos.
"""

from pydantic import BaseModel, Field, model_validator
import datetime


class RetornoCreate(BaseModel):
    """Datos requeridos para crear un nuevo retorno."""
    re_anio: int = Field(..., examples=[datetime.date.today().year], description="Año del retorno. No puede ser anterior al año actual.")
    re_estado: str = Field(default="activo", examples=["activo"], description="Estado del retorno")


class RetornoResponse(BaseModel):
    """Datos retornados tras crear o consultar un retorno."""
    re_codigo: int
    re_fecha_creacion: datetime.datetime
    re_anio: int
    re_estado: str

    class Config:
        from_attributes = True