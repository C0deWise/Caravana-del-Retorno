from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.colonias.excepciones.excepciones import SolicitudEstadoInvalido, SolicitudNoEncontrada
from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.colonias.repositories.solicitud_colonia_repository import SolicitudColoniaRepository 
from app.colonias.schemas.colonia_solicitud_schemas import SolicitudColoniaCrear, SolicitudColoniaRespuesta

class SolicitudColoniaService:

    def __init__(self, repositorio: SolicitudColoniaRepository):
        self.repositorio = repositorio

    def _mapear_solicitud(self, solicitud: SolicitudColonia) -> SolicitudColoniaRespuesta:
        return SolicitudColoniaRespuesta(
            codigo=solicitud.so_codigo,
            estado=solicitud.so_estado,
            fecha_creacion=solicitud.so_fecha_creacion,
            codigo_usuario=solicitud.us_codigo,
            codigo_colonia=solicitud.co_codigo,
            nombre_usuario=solicitud.usuario.us_nombre,
            apellido_usuario=solicitud.usuario.us_apellido,
        )

    async def crear_solicitud(self, data: SolicitudColoniaCrear) -> SolicitudColoniaRespuesta:

        solicitud = await self.repositorio.crear_solicitud_colonia(data)
       
        return self._mapear_solicitud(solicitud)

    async def _rechazar_solicitudes_colonia_pendientes_por_usuario(self, cod_usuario: int) -> int:
        return await self.repositorio.rechazar_solicitudes_pendientes_por_usuario(cod_usuario)

    async def obtener_solicitudes_pendientes_colonia(self, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = await self.repositorio.obtener_solicitudes_pendientes_por_colonia(cod_colonia)
        return [self._mapear_solicitud(s) for s in solicitudes]

    async def obtener_solicitudes_recientes_colonia(self, cod_colonia: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = await self.repositorio.obtener_solicitudes_recientes_por_colonia(cod_colonia)
        return [self._mapear_solicitud(s) for s in solicitudes]

    async def obtener_solicitudes_recientes_usuario(self, cod_usuario: int) -> list[SolicitudColoniaRespuesta]:
        solicitudes = await self.repositorio.obtener_solicitudes_recientes_por_usuario(cod_usuario)
        return [self._mapear_solicitud(s) for s in solicitudes]

    async def expirar_solicitudes_vencidas(self) -> int:
        return await self.repositorio.expirar_pendientes()
    
    async def aceptar_solicitud (self, codigo: int) -> SolicitudColoniaRespuesta:
        """Acepta una solicitud pendiente, cambiando su estado a 'aceptada'."""
        try:
            solicitud = await self.repositorio.aceptar_solicitud_colonia(codigo)
            await self._rechazar_solicitudes_colonia_pendientes_por_usuario(solicitud.us_codigo)
            return self._mapear_solicitud(solicitud)
        except SolicitudNoEncontrada as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except SolicitudEstadoInvalido as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        
    
    async def rechazar_solicitud (self, codigo: int) -> SolicitudColoniaRespuesta:
        """Rechaza una solicitud pendiente, cambiando su estado a 'rechazada'."""
        try:
            solicitud = await self.repositorio.rechazar_solicitud_colonia(codigo)
            return self._mapear_solicitud(solicitud)
        except SolicitudNoEncontrada as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except SolicitudEstadoInvalido as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    async def obtener_solicitud(self,codigo: int) -> SolicitudColoniaRespuesta:
        solicitud = await self.repositorio.obtener_solicitud_por_id(codigo)
        if not solicitud:
            raise ValueError(f"Solicitud con código {codigo} no encontrada.")
        return self._mapear_solicitud(solicitud)