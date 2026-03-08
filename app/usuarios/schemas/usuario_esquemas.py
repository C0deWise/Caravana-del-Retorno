from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

from app.usuarios.models.usuario import TipoDoc, Genero

import re

class UsuarioSchema(BaseModel):
    us_tipo_doc: TipoDoc
    us_documento: str
    us_celular: str
    co_codigo: Optional[int] = None
    ro_codigo: int = 1
    us_nombre: str
    us_apellido: str
    us_genero: Genero
    us_fecha_nacimiento: date
    us_pais: str
    us_departamento: Optional[str] = None
    us_ciudad: Optional[str] = None
    us_correo: str
    us_contrasenia: str

    @field_validator("us_documento")
    @classmethod
    def documento_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El documento no puede estar vacío.")
        return v

    @field_validator("us_celular")
    @classmethod
    def celular_valido(cls, v: str) -> str:
        digits = v.replace("+", "").replace(" ", "")
        if not digits.isdigit():
            raise ValueError("El celular solo puede contener números, espacios y '+'.")
        if not (7 <= len(digits) <= 15):
            raise ValueError("El celular debe tener entre 7 y 15 dígitos.")
        return v

    @field_validator("us_nombre", "us_apellido")
    @classmethod
    def solo_letras(cls, v: str) -> str:
        if not v.replace(" ", "").isalpha():
            raise ValueError("El campo solo puede contener letras.")
        return v.strip()

    @field_validator("us_tipo_doc")
    @classmethod
    def validar_tipo_doc(cls, v: TipoDoc) -> TipoDoc:
        valores = [e.value for e in TipoDoc]
        if v not in TipoDoc.__members__.values():
            raise ValueError(f"Tipo de documento inválido. Valores permitidos: {valores}")
        return v

    @field_validator("us_genero")
    @classmethod
    def validar_genero(cls, v: Genero) -> Genero:
        valores = [e.value for e in Genero]
        if v not in Genero.__members__.values():
            raise ValueError(f"Género inválido. Valores permitidos: {valores}")
        return v
    model_config = {"from_attributes": True}

    @field_validator("us_correo")
    @classmethod
    def correo_valido(cls, v: str) -> str:
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, v):
            raise ValueError("El correo ingresado no es válido.")
        return v.strip().lower()