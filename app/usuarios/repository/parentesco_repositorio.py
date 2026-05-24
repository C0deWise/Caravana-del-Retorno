"""
    parentesco_repositorio.py define el repositorio para gestionar las relaciones de parentesco entre usuarios.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.usuarios.models.parentesco import Parentesco, EstadoSolicitudParentesco
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear, ParentescoRespuesta

class ParentescoRepositorio:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def solicitar_parentesco(self, parentesco_crear: ParentescoCrear) -> Parentesco:
        parentesco = Parentesco(
            codigo_solicitante=parentesco_crear.codigo_solicitante,
            codigo_destinatario=parentesco_crear.codigo_destinatario,
            tipo_parentesco=parentesco_crear.tipo_parentesco
        )
        self.db.add(parentesco)
        await self.db.commit()
        await self.db.refresh(parentesco)
        return parentesco

    async def existe_solicitud_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una solicitud de parentesco bidireccional entre dos usuarios."""
        result = await self.db.execute(
            select(Parentesco).where(
                or_(
                    # Caso 1: A solicita a B
                    (Parentesco.codigo_solicitante == codigo_solicitante) & (Parentesco.codigo_destinatario == codigo_destinatario),
                    # Caso 2: B solicita a A
                    (Parentesco.codigo_solicitante == codigo_destinatario) & (Parentesco.codigo_destinatario == codigo_solicitante)
                ),
                Parentesco.estado == EstadoSolicitudParentesco.pendiente
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def existe_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una relación de parentesco aceptada bidireccional entre dos usuarios."""
        result = await self.db.execute(
            select(Parentesco).where(
                or_(
                    # Caso 1: A y B aceptaron parentesco (A solicitó a B)
                    (Parentesco.codigo_solicitante == codigo_solicitante) & (Parentesco.codigo_destinatario == codigo_destinatario),
                    # Caso 2: A y B aceptaron parentesco (B solicitó a A)
                    (Parentesco.codigo_solicitante == codigo_destinatario) & (Parentesco.codigo_destinatario == codigo_solicitante)
                ),
                Parentesco.estado == EstadoSolicitudParentesco.aceptada   
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def listar_parentescos_usuario(self, codigo_usuario: int) -> list[ParentescoRespuesta]:
        """Lista todas las relaciones de parentesco de un usuario."""
        result = await self.db.execute(
            select(Parentesco)
            .where(
                (Parentesco.codigo_destinatario == codigo_usuario) | (Parentesco.codigo_solicitante == codigo_usuario), Parentesco.estado != EstadoSolicitudParentesco.expirada)
            .options(selectinload(Parentesco.solicitante), selectinload(Parentesco.destinatario))
        )
        return result.scalars().all()
    
    async def obtener_parentesco_por_id_detallado(self, id_parentesco: int) -> Parentesco | None:
        """Obtiene un parentesco por su ID con sus relaciones cargadas."""
        result = await self.db.execute(
            select(Parentesco)
            .where(Parentesco.codigo == id_parentesco)
            .options(selectinload(Parentesco.solicitante), selectinload(Parentesco.destinatario))
        )
        return result.scalar_one_or_none()
    
    async def obtener_parentesco_por_id(self, id_parentesco: int) -> Parentesco | None:
        """Obtiene un parentesco por su ID con sus relaciones cargadas."""
        result = await self.db.execute(
            select(Parentesco)
            .where(Parentesco.codigo == id_parentesco)
        )
        return result.scalar_one_or_none()
    
    async def actualizar_estado_parentesco(self, id_parentesco: int, nuevo_estado: EstadoSolicitudParentesco) -> Parentesco:
        """Actualiza el estado de una solicitud de parentesco."""
        parentesco = await self.obtener_parentesco_por_id_detallado(id_parentesco)
        if not parentesco:
            raise ValueError("La solicitud de parentesco no existe.")
        parentesco.estado = nuevo_estado
        self.db.add(parentesco)
        await self.db.commit()
        await self.db.refresh(parentesco)
        return parentesco