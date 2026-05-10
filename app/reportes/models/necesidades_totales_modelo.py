
"""
necesidades_totales_modelo.py
=============================
Propósito: Modelo Pydantic que define la estructura de datos para el total de necesidades
          en un retorno. Contiene agregados de hospedaje, transporte y parqueadero
          para todos los asistentes.
"""

from pydantic import BaseModel


class NecesidadesTotales(BaseModel):
    num_hospedaje: int
    num_transporte: int
    num_parqueadero_motos: int
    num_parqueadero_carros: int