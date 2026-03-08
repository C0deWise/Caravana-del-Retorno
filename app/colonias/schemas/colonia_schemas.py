"""
Módulo que define los esquemas de validación para la entidad Colonia.
Contiene los modelos Pydantic usados para validar los datos de entrada
y estructurar las respuestas de la API relacionadas con colonias colombianas
en el exterior.
"""

from pydantic import BaseModel, field_validator
import re

class ColoniaCrear (BaseModel):
    """Esquema de entrada para crear una colonia."""

    pais: str
    departamento: str
    ciudad: str

    @field_validator("pais", "departamento", "ciudad")
    @classmethod
    def solo_alfabetico(cls, v:str) -> str:
        """
        Valida que el valor del campo sea alfabético.
        Parámetros: 
            v (str): Valor del campo a validar.
        Retorna:
            str: Valor limpio sin espacios al inicio o al final.
        Excepciones:
            ValueError: Si el campo esta vacío o contiene caracteres no alfabéticos.
        """
        #Eliminar espacio al inicio y al final
        v = v.strip()

        #Verificar que el campo no esté vacío
        if not v:
            raise ValueError("El campo no puede estar vacío")
        
        #Permitir letras tildes, espacios y guiones únicamente
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$", v):
            raise ValueError("El campo solo puede contener letras.")
        return v
    
class ColoniaRespuesta (BaseModel):
    """Esquema de resúesta para una colonia creada."""

    id: int
    pais: str
    departamento: str
    ciudad: str

    model_config = {"from_attributes": True}