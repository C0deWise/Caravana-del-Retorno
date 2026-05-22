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


class ParentescoRespuestaDetallada(BaseModel):
    codigo: int 
    tipo_parentesco: TipoParentesco 
    estado: EstadoSolicitudParentesco 
    solicitante: UsuarioResumen
    destinatario: UsuarioResumen
    model_config = {"from_attributes": True, "populate_by_name": True}


class ParentescoRespuesta(BaseModel):
    codigo: int
    codigo_solicitante: int
    codigo_destinatario: int
    tipo_parentesco: TipoParentesco
    estado: EstadoSolicitudParentesco

    model_config = {"from_attributes": True}