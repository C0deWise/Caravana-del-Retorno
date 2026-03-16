from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear
from app.usuarios.docs.registro_doc import registrar_docs, registrar_body
router = APIRouter(prefix="/usuario", tags=["Usuario"])


def get_usuario_servicio(db: AsyncSession = Depends(get_async_db)) -> UsuarioServicio:
    repositorio = UsuarioRepositorio(db)
    return UsuarioServicio(repositorio)


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,
)
async def registrar_usuario(
    schema: UsuarioCrear,
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