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
    """
    Esquema para la creación de un nuevo usuario.
    Contiene todos los campos requeridos para el registro y las validaciones de formato.
    """
    tipo_doc: TipoDoc = Field(..., description="Tipo de documento de identidad del usuario.", examples=["CC", "CE"])
    documento: str = Field(..., description="Número de documento de identidad.", min_length=1, max_length=20)
    celular: str = Field(..., description="Número de celular del usuario.", examples=["+57 3001234567"])
    correo: str = Field(..., description="Correo electrónico del usuario.", examples=["usuario@example.com"])
    contrasenia: str = Field(..., description="Contraseña para el acceso al sistema.", min_length=8, max_length=72)
    nombre: str = Field(..., description="Nombre(s) del usuario.", examples=["Juan"])
    apellido: str = Field(..., description="Apellido(s) del usuario.", examples=["Pérez"])
    genero: Genero = Field(..., description="Género del usuario.", examples=["M", "F", "otro"])
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento en formato YYYY-MM-DD.", examples=["1990-01-15"])
    pais: str = Field(..., description="País de residencia.", examples=["Colombia"])
    departamento: Optional[str] = Field(None, description="Departamento de residencia (opcional).", examples=["Cundinamarca"])
    ciudad: Optional[str] = Field(None, description="Ciudad de residencia (opcional).", examples=["Bogotá"])
    codigo_colonia: Optional[int] = Field(None, description="ID de la colonia a la que pertenece (opcional).")
    codigo_rol: int = Field(1, description="ID del rol asignado al usuario (por defecto: 1 - usuario).")

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

    @field_validator("genero")
    @classmethod
    def validar_genero(cls, v: Genero) -> Genero:
        """Valida que el género corresponda a uno de los valores permitidos."""
        valores = [e.value for e in Genero]
        if v not in Genero.__members__.values():
            raise ValueError(f"Género inválido. Valores permitidos: {valores}")
        return v

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        """Valida que el formato del correo electrónico sea estándar."""
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, v):
            raise ValueError("El correo ingresado no es válido.")
        return v.strip().lower()

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "tipo_doc": "CC",
                "documento": "123456789",
                "celular": "+573001234567",
                "correo": "juan.perez@example.com",
                "contrasenia": "una_contrasenia_segura",
                "nombre": "Juan",
                "apellido": "Pérez",
                "genero": "M",
                "fecha_nacimiento": "1995-05-10",
                "pais": "Colombia",
            }
        },
    }


class UsuarioSalida(BaseModel):
    """Esquema para la salida de datos básicos de un usuario."""
    id: int = Field(..., validation_alias="us_codigo", description="ID único del usuario.")
    nombre: str = Field(..., validation_alias="us_nombre", description="Nombre completo del usuario.")
    apellido: str = Field(..., validation_alias="us_apellido", description="Apellidos del usuario.")
    correo: str = Field(..., validation_alias="us_correo", description="Correo electrónico del usuario.")
    documento: str = Field(..., validation_alias="us_documento", description="Número de documento del usuario.")

    model_config = {"from_attributes": True}


class UsuarioNombre(BaseModel):
    """Esquema para mostrar únicamente el nombre y apellido de un usuario."""
    nombre: str = Field(..., validation_alias="us_nombre", description="Nombre del usuario.")
    apellido: str = Field(..., validation_alias="us_apellido", description="Apellido del usuario.")

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}