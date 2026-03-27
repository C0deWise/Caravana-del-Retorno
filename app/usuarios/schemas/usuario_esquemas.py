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
