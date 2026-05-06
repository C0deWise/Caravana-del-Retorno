"""
    solicitud_grupo_retorno_repositorio.py Repositorio para manejar las operaciones de las solicitudes de grupos de retorno a usuarios.
"""



from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado 
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
            pass

        async def aceptar_solicitud_grupo_retorno(self, solicitud_id: int):
            pass

        async def obtener_solicitudes_por_grupo_retorno(self, grupo_retorno_id: int):
            pass