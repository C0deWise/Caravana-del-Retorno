"""
    persona_repositorio.py se encarga de la gestion de las personas que no son usuarios del sistema, 
    pero asisten a los retornos mediante los grupos de retorno. 
"""

from sqlalchemy.ext.asyncio import AsyncSession


class PersonaRepositorio:
    """
    Repositorio para gestionar las operaciones relacionadas con las personas en el sistema de retorno.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_persona(self, datos):
        """
        Crea una nueva persona en la base de datos.
        :param datos: Datos necesarios para crear una persona.
        :return: La persona creada.
        """
        pass