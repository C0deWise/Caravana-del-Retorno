"""
    usuario_esquemas.py define los esquemas de validación para los datos de los usuarios.
"""

from pydantic import BaseModel, field_validator
from datetime import date
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
        if not v.strip():
            raise ValueError("El documento no puede estar vacío.")
        return v

    @field_validator("celular")
    @classmethod
    def celular_valido(cls, v: str) -> str:
        digits = v.replace("+", "").replace(" ", "")
        if not digits.isdigit():
            raise ValueError("El celular solo puede contener números, espacios y '+'.")
        if not (7 <= len(digits) <= 15):
            raise ValueError("El celular debe tener entre 7 y 15 dígitos.")
        return v

    @field_validator("nombre", "apellido")
    @classmethod
    def solo_letras(cls, v: str) -> str:
        if not v.replace(" ", "").isalpha():
            raise ValueError("El campo solo puede contener letras.")
        return v.strip()

    @field_validator("genero")
    @classmethod
    def validar_genero(cls, v: Genero) -> Genero:
        valores = [e.value for e in Genero]
        if v not in Genero.__members__.values():
            raise ValueError(f"Género inválido. Valores permitidos: {valores}")
        return v
    model_config = {"from_attributes": True}

    @field_validator("correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, v):
            raise ValueError("El correo ingresado no es válido.")
        return v.strip().lower()