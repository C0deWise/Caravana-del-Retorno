"""
Módulo que define los esquemas de validación para la entidad Colonia.
Contiene los modelos Pydantic usados para validar los datos de entrada
y estructurar las respuestas de la API relacionadas con colonias colombianas
en el exterior.
"""

from datetime import date

from pydantic import BaseModel, field_validator, model_validator, Field
from datetime import datetime
from typing import Optional
import re
from app.colonias.models.colonia_model import ColoniaEstado
from app.usuarios.models.usuario import TipoDoc, Genero

class ColoniaCrear (BaseModel):
    """Esquema de entrada para crear una colonia."""

    pais: str
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    lider: Optional[int] = Field(default=None, gt=0, description="ID del usuario a asignar como líder de la colonia")

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
    
    @field_validator("lider")
    @classmethod
    def lider_no_cero(cls, v):
        if v == 0:
            raise ValueError("El campo líder no puede ser 0. Debe ser null o un ID válido.")
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

    codigo: int
    pais: str
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    estado: ColoniaEstado
    lider: Optional[int]= None

    model_config = {"from_attributes": True}

class ColoniaEstablecerLider (BaseModel):
    """Esquema de entrada para establecer un líder a una colonia."""

    lider: int = Field(..., gt=0, description="ID del usuario a asignar como líder de la colonia")

class ColoniaSacarMiembro (BaseModel):
    """Esquema de entrada para sacar un miembro de una colonia."""

    miembro_id: int = Field(..., gt=0, description="ID del usuario a sacar de la colonia") 

class UsuarioRemovidoColonia(BaseModel):
    """Esquema de respuesta para un usuario removido de una colonia."""
    id: int = Field(validation_alias="us_codigo")
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
 
    model_config = {"from_attributes": True, "populate_by_name": True}

class UsuarioRemovidoColoniaRespuesta(BaseModel):
    """Esquema de respuesta para la acción de remover un usuario de una colonia."""
    mensaje: str = Field(..., description="Mensaje de confirmación")
    usuario: UsuarioRemovidoColonia = Field(..., description="Datos del usuario removido")

    model_config = {"from_attributes": True}
