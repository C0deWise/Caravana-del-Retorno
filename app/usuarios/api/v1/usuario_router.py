"""
    usuario_router.py define el router para las operaciones relacionadas con los usuarios.
    Aquí se implementan los endpoints para registrar usuarios y solicitar parentesco.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.usuarios.repository.parentesco_repositorio import ParentescoRepositorio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear, ParentescoRespuestaDetallada
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear
from app.usuarios.docs.registro_doc import registrar_docs, registrar_body
from app.usuarios.docs.solicitud_parentesco_doc import solicitar_parentesco_docs, solicitar_parentesco_body
from app.usuarios.docs.listar_parentescos_doc import listar_parentescos_docs

router = APIRouter()

def get_usuario_servicio(db: AsyncSession = Depends(get_async_db)) -> UsuarioServicio:
    repositorio = UsuarioRepositorio(db)
    repositorio_parentesco = ParentescoRepositorio(db)
    return UsuarioServicio(repositorio, repositorio_parentesco)


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED, **registrar_docs
)
async def registrar_usuario(
    schema: registrar_body,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    try:
        usuario = await servicio.registrar(schema)
        return {"mensaje": "Usuario registrado exitosamente.", "nombre": usuario.us_nombre + " " + usuario.us_apellido}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/solicitar-parentesco", status_code=status.HTTP_201_CREATED, **solicitar_parentesco_docs
)
async def solicitar_parentesco(
    parentesco_crear: solicitar_parentesco_body,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    try:
        await servicio.solicitar_parentesco(parentesco_crear)
        return {"mensaje": "Solicitud de parentesco enviada exitosamente."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
@router.get(
    "/{codigo_usuario}/parentescos",
    status_code=status.HTTP_200_OK,
    **listar_parentescos_docs
)
async def listar_parentescos_usuario(
    codigo_usuario: int,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    try:
        parentescos = await servicio.listar_parentescos_usuario(codigo_usuario)
        return parentescos
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )