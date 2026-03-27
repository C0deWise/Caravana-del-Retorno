"""
    parentesco_repositorio.py define el repositorio para gestionar las relaciones de parentesco entre usuarios.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.usuarios.models.parentesco import Parentesco, EstadoSolicitudParentesco
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear

class ParentescoRepositorio:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def solicitar_parentesco(self, parentesco_crear: ParentescoCrear) -> Parentesco:
        parentesco = Parentesco(
            us_codigo_solicitante=parentesco_crear.codigo_solicitante,
            us_codigo_destinatario=parentesco_crear.codigo_destinatario,
            pa_tipo_parentesco=parentesco_crear.tipo_parentesco
        )
        self.db.add(parentesco)
        await self.db.commit()
        await self.db.refresh(parentesco)
        return parentesco

    async def existe_solicitud_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una solicitud de parentesco entre dos usuarios."""
        result = await self.db.execute(
            select(Parentesco).where(
                Parentesco.us_codigo_solicitante == codigo_solicitante,
                Parentesco.us_codigo_destinatario == codigo_destinatario,
                Parentesco.pa_estado == EstadoSolicitudParentesco.PENDIENTE
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def existe_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una relacion de parentesco entre dos usuarios."""
        result = await self.db.execute(
            select(Parentesco).where(
                Parentesco.us_codigo_solicitante == codigo_solicitante,
                Parentesco.us_codigo_destinatario == codigo_destinatario,
                Parentesco.pa_estado == EstadoSolicitudParentesco.ACEPTADA   
            )
        )
        return result.scalar_one_or_none() is not None