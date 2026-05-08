
"""
registro_retorno_usuario_detallado_modelo.py
============================================
Propósito: Modelo Pydantic que define la estructura de datos para asistentes individuales
          en un retorno. Contiene información de contacto, necesidades de transporte
          y hospedaje, y notas adicionales.
"""

from pydantic import BaseModel


class RegistroRetornoUsuarioDetallado(BaseModel):
    celular: str
    nombre: str
    notas: str | None
    num_hospedaje: int
    num_transporte: int
    num_parqueadero_motos: int
    num_parqueadero_carros: int
