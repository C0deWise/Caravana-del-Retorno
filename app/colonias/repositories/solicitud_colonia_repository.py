from datetime import datetime, timedelta, timezone
from typing import Optional
from app.usuarios.models.usuario import Usuario
from sqlalchemy.orm import joinedload
from app.colonias.excepciones.excepciones import SolicitudEstadoInvalido, SolicitudNoEncontrada
from app.colonias.models.solicitud_colonia import SolicitudColonia, EstadoSolicitud
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

class SolicitudColoniaRepository:
 
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def crear_solicitud_colonia(self, data: SolicitudColoniaCrear) -> SolicitudColonia:
        solicitud = SolicitudColonia(
            us_codigo=data.codigo_usuario,
            co_codigo=data.codigo_colonia,
            so_estado=EstadoSolicitud.pendiente,
        )
        self.db.add(solicitud)
        await self.db.commit()
        await self.db.refresh(solicitud, attribute_names=["usuario"])
        return solicitud
 
    async def obtener_solicitudes_pendientes_por_colonia(self, cod_colonia: int) -> list[SolicitudColonia]:
        resultado = await self.db.execute(
            select(SolicitudColonia)
            .where(
                SolicitudColonia.co_codigo == cod_colonia,
                SolicitudColonia.so_estado == EstadoSolicitud.pendiente,
            )
            .options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalars().all()
      
    async def obtener_solicitud_por_id(self, codigo: int) -> Optional[SolicitudColonia]:
        resultado = await self.db.execute(
            select(SolicitudColonia).where(SolicitudColonia.so_codigo == codigo).options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalar_one_or_none()

    async def get_all(self) -> list[SolicitudColonia]:
        resultado = await self.db.execute(select(SolicitudColonia))
        return resultado.scalars().all()

    async def aceptar_solicitud_colonia(self, codigo: int) -> SolicitudColonia:
        """Cambia el estado de una solicitud a aceptada"""
        solicitud = await self.obtener_solicitud_por_id(codigo)

        if not solicitud:
            raise SolicitudNoEncontrada(f"Solicitud con código {codigo} no encontrada.")
        
        if solicitud.so_estado != EstadoSolicitud.pendiente:
            raise SolicitudEstadoInvalido(f"Solo se pueden aceptar solicitudes pendientes. Solicitud {codigo} está en estado {solicitud.so_estado.value}.")
        
        solicitud.so_estado = EstadoSolicitud.aceptada
        usuario = await self.db.get(Usuario, solicitud.us_codigo)
        usuario.co_codigo = solicitud.co_codigo
        await self.db.commit()
        await self.db.refresh(solicitud)

        return solicitud

    async def rechazar_solicitud_colonia(self, codigo: int) -> SolicitudColonia:
        """Cambia el estado de una solicitud a rechazada"""
        solicitud = await self.obtener_solicitud_por_id(codigo)

        if not solicitud:
            raise SolicitudNoEncontrada(f"Solicitud con código {codigo} no encontrada.")
        
        if solicitud.so_estado != EstadoSolicitud.pendiente:
            raise SolicitudEstadoInvalido(f"Solo se pueden rechazar solicitudes pendientes. Solicitud {codigo} está en estado {solicitud.so_estado.value}.")
        
        solicitud.so_estado = EstadoSolicitud.rechazada
        await self.db.commit()
        await self.db.refresh(solicitud)

        return solicitud
    
    async def obtener_solicitudes_recientes_por_colonia(self, cod_colonia: int) -> list[SolicitudColonia]:
        limite = datetime.datetime.now(timezone.utc) - timedelta(days=30)
        resultado = await self.db.execute(
            select(SolicitudColonia)
            .where(
                SolicitudColonia.co_codigo == cod_colonia,
                SolicitudColonia.so_fecha_creacion > limite,
            )
            .options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalars().all()
 
    async def obtener_solicitudes_recientes_por_usuario(self, cod_usuario: int) -> list[SolicitudColonia]:
        limite = datetime.datetime.now(timezone.utc) - timedelta(days=30)
        resultado = await self.db.execute(
            select(SolicitudColonia)
            .where(
                SolicitudColonia.us_codigo == cod_usuario,
                SolicitudColonia.so_fecha_creacion > limite,
            )
            .options(joinedload(SolicitudColonia.usuario))
        )
        return resultado.scalars().all()
 
    async def expirar_pendientes(self) -> int:
        limite = datetime.utcnow() - timedelta(days=30)
        resultado = await self.db.execute(
            update(SolicitudColonia)
            .where(
                SolicitudColonia.so_estado == EstadoSolicitud.pendiente,
                SolicitudColonia.so_fecha_creacion <= limite,
            )
            .values(so_estado=EstadoSolicitud.expirada)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.commit()
        return resultado.rowcount
    
    async def rechazar_solicitudes_pendientes_por_usuario(self, usuario_id: int):
        stmt = (
            update(SolicitudColonia)
            .where(
                SolicitudColonia.us_codigo == usuario_id,
                SolicitudColonia.so_estado == EstadoSolicitud.pendiente
            )
            .values(so_estado=EstadoSolicitud.rechazada)
        )

        await self.db.execute(stmt)
        await self.db.commit()
