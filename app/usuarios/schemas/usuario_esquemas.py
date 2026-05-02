"""
Este módulo define los esquemas Pydantic para la validación de datos de la entidad Usuario.
Estos esquemas se utilizan en la API para validar la entrada de datos,
serializar la salida y generar la documentación automática de los endpoints.
"""



from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime
from typing import Optional

from app.usuarios.models.usuario import TipoDoc, Genero

import re

class UsuarioCrear(BaseModel):
    tipo_doc: TipoDoc
    documento: str
    celular: str
    codigo_colonia: Optional[int] = None
    codigo_rol: int = 1
    nombre: str
    apellido: str
    genero: Genero
    fecha_nacimiento: date
    pais: str
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    correo: str
    contrasenia: str

    @field_validator("documento")
    @classmethod
    def documento_no_vacio(cls, v: str) -> str:
        """Valida que el documento no esté vacío."""
        if not v.strip():
            raise ValueError("El documento no puede estar vacío.")
        return v

    @field_validator("celular")
    @classmethod
    def celular_valido(cls, v: str) -> str:
        """
        Valida el formato del número de celular.
        Permite solo dígitos, espacios y el símbolo '+' al inicio.
        La longitud debe estar entre 7 y 15 dígitos.
        """
        digits = v.replace("+", "").replace(" ", "")
        if not digits.isdigit():
            raise ValueError("El celular solo puede contener números, espacios y '+'.")
        if not (7 <= len(digits) <= 15):
            raise ValueError("El celular debe tener entre 7 y 15 dígitos.")
        return v

    @field_validator("nombre", "apellido")
    @classmethod
    def solo_letras(cls, v: str) -> str:
        """Valida que los nombres y apellidos contengan solo letras y espacios."""
        if not v.replace(" ", "").isalpha():
            raise ValueError("El campo solo puede contener letras.")
        return v.strip()

   

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, v):
            raise ValueError("El correo ingresado no es válido.")
        return v.strip().lower()

class UsuarioSalida(BaseModel):
    """Esquema para la salida de datos básicos de un usuario."""
    id: int = Field(..., validation_alias="us_codigo", description="ID único del usuario.")
    nombre: str = Field(..., validation_alias="us_nombre", description="Nombre completo del usuario.")
    apellido: str = Field(..., validation_alias="us_apellido", description="Apellidos del usuario.")
    correo: str = Field(..., validation_alias="us_correo", description="Correo electrónico del usuario.")
    documento: str = Field(..., validation_alias="us_documento", description="Número de documento del usuario.")

    model_config = {"from_attributes": True, "populate_by_name": True}


class UsuarioNombre(BaseModel):
    """Esquema para mostrar únicamente el nombre y apellido de un usuario."""
    nombre: str = Field(..., validation_alias="us_nombre", description="Nombre del usuario.")
    apellido: str = Field(..., validation_alias="us_apellido", description="Apellido del usuario.")

    model_config = {"from_attributes": True, "populate_by_name": True}


class UsuarioDetallado(BaseModel):
    """Esquema para la salida de datos detallados de un usuario, ideal para vistas de administrador."""
    id: int = Field(validation_alias="us_codigo")
    fecha_creacion: datetime = Field(validation_alias="us_fecha_creacion")
    tipo_doc: TipoDoc = Field(validation_alias="us_tipo_doc")
    documento: str = Field(validation_alias="us_documento")
    celular: str = Field(validation_alias="us_celular")
    correo: str = Field(validation_alias="us_correo")
    codigo_colonia: Optional[int] = Field(validation_alias="co_codigo")
    codigo_rol: int = Field(validation_alias="ro_codigo")
    nombre: str = Field(validation_alias="us_nombre")
    apellido: str = Field(validation_alias="us_apellido")
    genero: Genero = Field(validation_alias="us_genero")
    fecha_nacimiento: date = Field(validation_alias="us_fecha_nacimiento")
    pais: str = Field(validation_alias="us_pais")
    departamento: Optional[str] = Field(validation_alias="us_departamento")
    ciudad: Optional[str] = Field(validation_alias="us_ciudad")

    model_config = {"from_attributes": True, "populate_by_name": True}
class UsuarioResumen(BaseModel):
    codigo: int = Field(alias="us_codigo")
    nombre: str = Field(alias="us_nombre")
    apellido: str = Field(alias="us_apellido")
    model_config = {"from_attributes": True, "populate_by_name": True}


class UsuarioConsultaColonia(BaseModel):
    id: int 
    nombre: str
    apellido: str 
    codigo_colonia: int
    documento: str 
    tipo_doc: str 
    genero: str 
    fecha_nacimiento: date 
    celular: str
    correo: str
    role: int 

    model_config = {"from_attributes": True, "populate_by_name": True}