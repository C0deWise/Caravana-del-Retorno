"""
Schemas de validación para Retorno.
Define la estructura de entrada y salida de la API,
separando la representación HTTP del modelo de base de datos.
"""

from enum import Enum
from pydantic import BaseModel, Field, model_validator, ConfigDict
import datetime


class RetornoEstado(str, Enum):
    """Estados permitidos para un evento de Retorno."""
    ACTIVO = "activo"
    FINALIZADO = "finalizado"


class RetornoCreate(BaseModel):
    """Datos requeridos para crear un nuevo retorno."""
    anio: int = Field(..., examples=[datetime.date.today().year], description="Año del retorno. No puede ser anterior al año actual.")
    estado: RetornoEstado = Field(default=RetornoEstado.ACTIVO, examples=[RetornoEstado.ACTIVO], description="Estado del retorno")


class RetornoResponse(BaseModel):
    """Datos retornados tras crear o consultar un retorno."""
    codigo: int
    fecha_creacion: datetime.datetime
    anio: int
    estado: RetornoEstado

    model_config = ConfigDict(from_attributes=True)