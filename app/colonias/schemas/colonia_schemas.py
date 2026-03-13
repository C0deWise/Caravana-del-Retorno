"""
Módulo que define los esquemas de validación para la entidad Colonia.
Contiene los modelos Pydantic usados para validar los datos de entrada
y estructurar las respuestas de la API relacionadas con colonias colombianas
en el exterior.
"""

from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Optional
import re

class ColoniaCrear (BaseModel):
    """Esquema de entrada para crear una colonia."""

    pais: str
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    lider_id: Optional[int] = None

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
        #Verificar que v sea diferente de None
        if v is not None:
            #Eliminar espacio al inicio y al final
            v = v.strip()
            #Convierte cada palabra con la inicial en mayúscula
            v = v.title()

            #Verificar que el campo no esté vacío
            if not v:
                raise ValueError("El campo no puede estar vacío")
            
            #Permitir letras tildes, espacios y guiones únicamente
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$", v):
                raise ValueError("El campo solo puede contener letras.")
        return v
    
    @model_validator(mode="after")
    def validar_ubicacion(self):
        """
        Valida la ubicación según el país de la colonia. Si el país es Colombia,
        los campos departamento y ciudad son obligatorios. Para colonias 
        extranjeras, estos campos deben estar vacíos.
        Parámetros:
            self (Colonia_Crear): Instancia del modelo con todos los campos
                                ya validados.
        Retorna:
            self (Colonia_Crear): La misma instancia si pasa la validación.
        Excepciones:
            ValueError: Si el país es Colombia y departamento o ciudad son nulos;
                        Si el país es extranjero y departamento y ciudad contienen 
                        valor.
        """

        if self.pais == "Colombia":
            if self.departamento is None or self.ciudad is None:
                raise ValueError("Los campos departamento y ciudad son obligatorios.")
        else:
            if self.departamento is not None or self.ciudad is not None:
                raise ValueError("Para colonias extranjeras se debe ingresar solo el país")

        return self
    
class ColoniaRespuesta (BaseModel):
    """Esquema de respúesta para una colonia creada."""

    id: int = Field(alias="co_codigo")
    pais: str = Field(alias="co_pais")
    departamento: Optional[str] = Field(alias="co_departamento")
    ciudad: Optional[str] = Field(alias="co_ciudad")
    lider_id: Optional[int]

    model_config = {"from_attributes": True, "populate_by_name": True}