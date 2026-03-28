"""
    parentesco_esquemas.py define los esquemas de entrada y salida de Pydantic para las relaciones de parentesco entre usuarios.
"""



from app.usuarios.schemas.usuario_esquemas import UsuarioResumen
from pydantic import BaseModel, field_validator, Field
from datetime import date
from typing import Optional


from app.usuarios.models.parentesco import EstadoSolicitudParentesco, TipoParentesco

class ParentescoCrear(BaseModel):
    codigo_solicitante: int
    codigo_destinatario: int
    tipo_parentesco: TipoParentesco

class ParentescoRespuesta(BaseModel):
    codigo: int
    fecha_creacion: date
    estado: EstadoSolicitudParentesco
    codigo_solicitante: int
    codigo_destinatario: int
    tipo_parentesco: TipoParentesco

    model_config = {"from_attributes": True}

class ParentescoRespuestaDetallada(BaseModel):
    codigo: int = Field(alias="pa_codigo")
    tipo_parentesco: TipoParentesco = Field(alias="pa_tipo_parentesco")
    estado: EstadoSolicitudParentesco = Field(alias="pa_estado")
    solicitante: UsuarioResumen
    destinatario: UsuarioResumen
    model_config = {"from_attributes": True, "populate_by_name": True}