"""
    usuario_router.py define el router para las operaciones relacionadas con los usuarios.
    Aquí se implementan los endpoints para registrar.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear, UsuarioSalida
from app.usuarios.docs.registro_doc import registrar_docs, registrar_body
router = APIRouter(prefix="/usuario", tags=["Usuario"])


def get_usuario_servicio(db: AsyncSession = Depends(get_async_db)) -> UsuarioServicio:
    repositorio = UsuarioRepositorio(db)
    return UsuarioServicio(repositorio)


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


@router.get("/", response_model=list[UsuarioSalida])
async def listar_usuarios(
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    return await servicio.obtener_todos()


@router.get("/buscar/{nombre}", response_model=list[UsuarioSalida])
async def buscar_usuario_por_nombre(
    nombre: str,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    return await servicio.buscar_por_nombre(nombre)


@router.get("/buscar_documento/{documento}", response_model=UsuarioSalida)
async def buscar_usuario_por_documento(
    documento: str,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    usuario = await servicio.buscar_por_documento(documento)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return usuario