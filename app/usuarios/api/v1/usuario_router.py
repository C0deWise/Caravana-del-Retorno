"""
    usuario_router.py define el router para las operaciones relacionadas con los usuarios.
    Aquí se implementan los endpoints para registrar usuarios, solicitar parentesco, consulta y búsqueda de usuarios,
gestionando las solicitudes HTTP y las respuestas correspondientes.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.usuarios.repository.parentesco_repositorio import ParentescoRepositorio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.docs.registro_doc import registrar_docs, registrar_body
from app.usuarios.docs.solicitud_parentesco_doc import solicitar_parentesco_docs, solicitar_parentesco_body
from app.usuarios.schemas.usuario_esquemas import UsuarioCrear, UsuarioSalida, UsuarioNombre, UsuarioDetallado

router = APIRouter(prefix="/usuario", tags=["Usuario"])


def get_usuario_servicio(db: AsyncSession = Depends(get_db)) -> UsuarioServicio:
    """
    Función de dependencia para obtener una instancia del servicio de usuarios.
    Inyecta la sesión de base de datos en el repositorio y luego en el servicio.

    Args:
        db (AsyncSession): Sesión de base de datos asíncrona.

    Returns:
        UsuarioServicio: Instancia del servicio de usuarios.
    """
    repositorio = UsuarioRepositorio(db)
    repositorio_parentesco = ParentescoRepositorio(db)
    return UsuarioServicio(repositorio, repositorio_parentesco)


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description=(
        "Crea un nuevo usuario en el sistema. "
        "**Acceso:** Público, no requiere autenticación."
    ),
    responses={
        201: {"description": "Usuario registrado exitosamente."},
        400: {"description": "Error de validación o de negocio (ej. duplicados)."},
        422: {"description": "Error de validación de Pydantic."}
    }
)
async def registrar_usuario(
    schema: Annotated[
        UsuarioCrear,
        Body(
            openapi_examples={
                "ejemplo_basico": {
                    "summary": "Registro básico",
                    "value": {
                        "tipo_doc": "CC",
                        "documento": "1234567890",
                        "celular": "+57 300 123 4567",
                        "correo": "juan.perez@gmail.com",
                        "contrasenia": "MiContrasenia123",
                        "nombre": "Juan",
                        "apellido": "Perez",
                        "genero": "M",
                        "fecha_nacimiento": "1995-06-15",
                        "pais": "Colombia",
                    },
                },
            }
        )
    ],
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    """
    Endpoint para registrar un nuevo usuario.

    Args:
        schema (UsuarioCrear): Datos del usuario a crear.
        servicio (UsuarioServicio): Servicio de usuarios inyectado.

    Returns:
        dict: Mensaje de éxito con el nombre del usuario.

    Raises:
        HTTPException: Si ocurren errores de validación o de negocio.
    """
    try:
        usuario = await servicio.registrar(schema)
        return {"mensaje": "Usuario registrado exitosamente.", "nombre": f"{usuario.us_nombre} {usuario.us_apellido}"}
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

@router.get("/", response_model=list[UsuarioSalida], summary="Listar todos los usuarios (básico)")
async def listar_usuarios(
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    """
    Obtiene una lista de todos los usuarios con su información básica.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.obtener_todos()


@router.get("/nombres", response_model=list[UsuarioNombre], summary="Listar nombres de todos los usuarios")
async def listar_nombres_usuarios(
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    """
    Obtiene una lista con únicamente los nombres y apellidos de todos los usuarios.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.obtener_todos()


@router.get("/todos", response_model=list[UsuarioDetallado], summary="Listar todos los usuarios (detallado)")
async def listar_usuarios_completo(
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    """
    Obtiene una lista de todos los usuarios con toda su información detallada.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.obtener_todos()


@router.get("/buscar/{nombre}", response_model=list[UsuarioSalida], summary="Buscar usuarios por nombre")
async def buscar_usuario_por_nombre(
    nombre: str,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    """
    Busca y devuelve usuarios cuyo nombre coincida parcialmente con el término de búsqueda.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.buscar_por_nombre(nombre)


@router.get("/buscar_documento/{documento}", response_model=UsuarioSalida, summary="Buscar un usuario por documento")
async def buscar_usuario_por_documento(
    documento: str,
    servicio: UsuarioServicio = Depends(get_usuario_servicio),
):
    """
    Busca y devuelve un usuario por su número de documento exacto.

    **Acceso:** Requiere autenticación y rol de **Administrador**.

    Raises:
        HTTPException: 404 si el usuario no es encontrado.
    """
    usuario = await servicio.buscar_por_documento(documento)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return usuario
