



from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.notificaciones.repositories.notificacion_repositorio import NotificacionRepository
from app.notificaciones.schemas.notificacion_esquema import NotificacionRespuesta
from app.notificaciones.schemas.notificacion_esquema import NotificacionRespuesta
from app.notificaciones.services.notificacion_consultar_actualizar_service import NotificacionConsultarActualizarService
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio


router = APIRouter()


def get_notificaciones_consultar_actualizar_servicio(db: Annotated[AsyncSession, Depends(get_db)]):
    repositorio_notificacion = NotificacionRepository(db)
    repositorio_usuario = UsuarioRepositorio(db)
    return NotificacionConsultarActualizarService(repositorio_notificacion, repositorio_usuario)


@router.get("/usuario/{id_usuario}/no-leidas", response_model=list[NotificacionRespuesta])
async def consultar_notificaciones_no_leidas_usuario(
    id_usuario: int,
    servicio: Annotated[NotificacionConsultarActualizarService, Depends(get_notificaciones_consultar_actualizar_servicio)]
):
    return await servicio.consultar_notificaciones_no_leidas_usuario(id_usuario)

@router.get("/{id_notificacion}", response_model=NotificacionRespuesta)
async def consultar_notificacion_por_id(
    id_notificacion: int,
    servicio: Annotated[NotificacionConsultarActualizarService, Depends(get_notificaciones_consultar_actualizar_servicio)]
):
    return await servicio.consultar_notificacion_id(id_notificacion)

@router.put("/{id_notificacion}/marcar-leida", response_model=NotificacionRespuesta)
async def actualizar_estado_notificacion_leida_por_id(
    id_notificacion: int,
    servicio: Annotated[NotificacionConsultarActualizarService, Depends(get_notificaciones_consultar_actualizar_servicio)]
):
    return await servicio.actualizar_estado_notificacion_leida_por_id(id_notificacion)

@router.put("/marcar-leida/lote", response_model=list[NotificacionRespuesta])
async def actualizar_estado_notificacion_leida_lote(
    notificaciones_id: list[int],
    servicio: Annotated[NotificacionConsultarActualizarService, Depends(get_notificaciones_consultar_actualizar_servicio)]
):
    return await servicio.actualizar_estado_notificacion_leida_lote(notificaciones_id)

@router.put("/usuario/{id_usuario}/marcar-leidas", response_model=list[NotificacionRespuesta])
async def actualizar_estado_notificacion_leida_lote_por_usuario(
    id_usuario: int,
    servicio: Annotated[NotificacionConsultarActualizarService, Depends(get_notificaciones_consultar_actualizar_servicio)]
):
    return await servicio.actualizar_estado_notificacion_leida_lote_por_usuario(id_usuario)

    