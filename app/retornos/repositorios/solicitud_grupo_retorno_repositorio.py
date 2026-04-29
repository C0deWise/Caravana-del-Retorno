"""
    solicitud_grupo_retorno_repositorio.py Repositorio para manejar las operaciones de las solicitudes de grupos de retorno a usuarios.
"""



from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado 
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import selectinload

from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno

class SolicitudGrupoRetornoRepositorio:

        def __init__(self,db: AsyncSession):
            self.db = db
    
        async def crear_solicitud_grupo_retorno(self, us_codigo: int, gr_codigo: int) -> SolicitudGrupoRetorno:
            """Crea una nueva solicitud de unión a un grupo en la base de datos."""
            nueva_solicitud = SolicitudGrupoRetorno(
                us_codigo=us_codigo,
                gr_codigo=gr_codigo,
                solgr_estado=SolicitudGrupoRetornoEstado.PENDIENTE # Set default state
            )
            self.db.add(nueva_solicitud)
            await self.db.commit()
            await self.db.refresh(nueva_solicitud)
            return nueva_solicitud

        async def rechazar_solicitud_grupo_retorno(self, solicitud_id: int):
            result = await self.db.execute(select(SolicitudGrupoRetorno).filter(SolicitudGrupoRetorno.solgr_codigo == solicitud_id))
            solicitud = result.scalar_one_or_none()
            if solicitud:
                solicitud.solgr_estado = SolicitudGrupoRetornoEstado.RECHAZADO
                await self.db.commit()
            return solicitud

        async def rechazar_solicitudes_pendientes_por_usuario(self, usuario_id: int):
            stmt = (
                update(SolicitudGrupoRetorno)
                .where(
                    SolicitudGrupoRetorno.us_codigo == usuario_id,
                    SolicitudGrupoRetorno.solgr_estado == SolicitudGrupoRetornoEstado.PENDIENTE
                )
                .values(solgr_estado=SolicitudGrupoRetornoEstado.RECHAZADO)
            )

            await self.db.execute(stmt)
            await self.db.commit()
        async def aceptar_solicitud_grupo_retorno(self, solicitud_id: int):
            result = await self.db.execute(select(SolicitudGrupoRetorno).filter(SolicitudGrupoRetorno.solgr_codigo == solicitud_id))
            solicitud = result.scalar_one_or_none()
            if solicitud:
                solicitud.solgr_estado = SolicitudGrupoRetornoEstado.ACEPTADO
                await self.db.commit()
            return solicitud

        async def obtener_solicitudes_por_grupo_retorno(self, grupo_retorno_id: int):
            result = await self.db.execute(
                select(SolicitudGrupoRetorno)
                 .options(selectinload(SolicitudGrupoRetorno.usuario))
                .filter(SolicitudGrupoRetorno.gr_codigo == grupo_retorno_id)
                .order_by(SolicitudGrupoRetorno.solgr_time_stamp.desc()))
            return result.scalars().all()

        async def obtener_solicitud_por_id(self, solicitud_id: int) -> SolicitudGrupoRetorno | None:
            result = await self.db.execute(select(SolicitudGrupoRetorno).filter(SolicitudGrupoRetorno.solgr_codigo == solicitud_id))
            return result.scalar_one_or_none()
        
        async def obtener_solicitudes_recientes_por_usuario(self, usuario_id: int):
            fecha_limite = datetime.now(timezone.utc) - timedelta(days=30)
            result = await self.db.execute(
                select(SolicitudGrupoRetorno)
                .options(selectinload(SolicitudGrupoRetorno.grupo).selectinload(GrupoRetorno.lider))
                .filter(
                    SolicitudGrupoRetorno.us_codigo == usuario_id,
                    SolicitudGrupoRetorno.solgr_time_stamp >= fecha_limite
                )
                .order_by(SolicitudGrupoRetorno.solgr_time_stamp.desc())
            )
            return result.scalars().all()
        
        async def obtener_solicitudes_pendientes_por_usuario(self, usuario_id: int):
            result = await self.db.execute(
                select(SolicitudGrupoRetorno).filter(SolicitudGrupoRetorno.us_codigo == usuario_id, SolicitudGrupoRetorno.solgr_estado == SolicitudGrupoRetornoEstado.PENDIENTE).order_by(SolicitudGrupoRetorno.solgr_time_stamp.desc())
            )
        