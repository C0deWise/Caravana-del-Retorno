
"""
registro_retorno_grupo_detallado_modelo.py
==========================================
Propósito: Modelo Pydantic que define la estructura de datos para grupos de asistentes
          en un retorno. Contiene información del grupo, su líder, miembros,
          y necesidades agrupadas.
"""

from pydantic import BaseModel


class RegistroRetornoGrupoDetallado(BaseModel):
    cod_grupo: int
    lider_nombre: str
    lider_celular: str
    nombre_usuarios: list[str]
    notas: str | None
    num_hospedaje: int 
    num_transporte: int
    num_parqueadero_motos: int
    num_parqueadero_carros: int