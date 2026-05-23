"""
    usuario_router.py define el router para las operaciones relacionadas con los usuarios.
    Aquí se implementan los endpoints para registrar usuarios, solicitar parentesco, consulta y búsqueda de usuarios,
gestionando las solicitudes HTTP y las respuestas correspondientes.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.usuarios.auth_dependencies import get_current_user, require_roles
from app.usuarios.models.usuario import Usuario
from app.usuarios.repository.parentesco_repositorio import ParentescoRepositorio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear, ParentescoRespuestaDetallada
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.usuarios.docs.registro_doc import registrar_docs, registrar_body
from app.usuarios.docs.solicitud_parentesco_doc import solicitar_parentesco_docs, solicitar_parentesco_body
from app.usuarios.schemas.usuario_esquemas import (
    AuthResponse,
    LoginRequest,
    MensajeRespuesta,
    RefreshRequest,
    UsuarioConsultaColonia,
    UsuarioCrear,
    UsuarioSalida,
    UsuarioNombre,
    UsuarioDetallado,
    UsuarioSesion,
)
from app.usuarios.docs.listar_parentescos_doc import listar_parentescos_docs
from app.usuarios.security import TokenError, decode_token

router = APIRouter(prefix="/usuario", tags=["Usuario"])
settings = get_settings()


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/usuario",
    )


def get_usuario_servicio(db: Annotated[AsyncSession, Depends(get_db)]) -> UsuarioServicio:
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
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
    summary="Iniciar sesion con correo y contrasena",
    description="Valida credenciales, entrega access token JWT y configura refresh token en cookie HttpOnly.",
)
async def login_usuario(
    schema: LoginRequest,
    response: Response,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
):
    try:
        usuario = await servicio.autenticar(schema.correo, schema.contrasenia)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token, refresh_token = servicio.generar_tokens(usuario)
    _set_refresh_cookie(response, refresh_token)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token if settings.DEBUG else None,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        usuario=servicio.construir_sesion_usuario(usuario),
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
    summary="Renovar access token",
    description="Renueva access token usando refresh token en cookie HttpOnly o body para pruebas manuales.",
)
async def refresh_token_usuario(
    request: Request,
    response: Response,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    schema: RefreshRequest | None = Body(default=None),
):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token and schema:
        refresh_token = schema.refresh_token

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontro refresh token",
        )

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    usuario = await servicio.obtener_usuario_por_id(int(payload["sub"]))
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado para refresh token",
        )

    access_token, new_refresh_token = servicio.generar_tokens(usuario)
    _set_refresh_cookie(response, new_refresh_token)

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token if settings.DEBUG else None,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        usuario=servicio.construir_sesion_usuario(usuario),
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UsuarioSesion,
    summary="Obtener sesion actual",
    description="Retorna informacion del usuario autenticado a partir del Bearer token.",
)
async def obtener_sesion_actual(
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    usuario_actual: Usuario = Depends(get_current_user),
):
    return servicio.construir_sesion_usuario(usuario_actual)


@router.get(
    "/panel-lider",
    status_code=status.HTTP_200_OK,
    response_model=MensajeRespuesta,
    summary="Endpoint protegido para lider y administrativo",
)
async def endpoint_lider_admin(
    _: Usuario = Depends(require_roles(2, 3)),
):
    return MensajeRespuesta(mensaje="Acceso concedido para lider o administrativo")


@router.get(
    "/panel-admin",
    status_code=status.HTTP_200_OK,
    response_model=MensajeRespuesta,
    summary="Endpoint protegido solo para administrativo",
)
async def endpoint_admin(
    _: Usuario = Depends(require_roles(3)),
):
    return MensajeRespuesta(mensaje="Acceso concedido para administrativo")


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,**registrar_docs
)
async def registrar_usuario(
    schema: registrar_body,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)], 
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
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(1, 2)),
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
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(3)),
):
    """
    Obtiene una lista de todos los usuarios con su información básica.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.obtener_todos()

@router.get("/buscar_id/{usuario_id}", response_model=UsuarioDetallado, summary="Obtener usuario por ID")
async def obtener_usuario(
    usuario_id: int,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(2, 3)),
):
    """
    Obtiene la información detallada de un usuario específico por su ID.


    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    try:
        return await servicio.obtener_por_id(usuario_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    

@router.get("/nombres", response_model=list[UsuarioNombre], summary="Listar nombres de todos los usuarios")
async def listar_nombres_usuarios(
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(1, 2, 3)),
):
    """
    Obtiene una lista con únicamente los nombres y apellidos de todos los usuarios.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.obtener_todos()


@router.get("/todos", response_model=list[UsuarioDetallado], summary="Listar todos los usuarios (detallado)")
async def listar_usuarios_completo(
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(3)),
):
    """
    Obtiene una lista de todos los usuarios con toda su información detallada.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.obtener_todos()


@router.get("/buscar/{nombre}", response_model=list[UsuarioSalida], summary="Buscar usuarios por nombre")
async def buscar_usuario_por_nombre(
    nombre: str,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(1, 2, 3)),
):
    """
    Busca y devuelve usuarios cuyo nombre coincida parcialmente con el término de búsqueda.

    **Acceso:** Requiere autenticación y rol de **Administrador**.
    """
    return await servicio.buscar_por_nombre(nombre)


@router.get("/buscar_documento/{documento}", response_model=UsuarioSalida, summary="Buscar un usuario por documento")
async def buscar_usuario_por_documento(
    documento: str,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(2, 3)),
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
    
@router.get(
    "/{codigo_usuario}/parentescos",
    status_code=status.HTTP_200_OK,
    **listar_parentescos_docs
)
async def listar_parentescos_usuario(
    codigo_usuario: int,
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(1, 2)),
):
    try:
        parentescos = await servicio.listar_parentescos_usuario(codigo_usuario)
        return parentescos
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/colonia/{colonia}", response_model=list[UsuarioConsultaColonia], summary="Buscar usuarios por colonia")
async def buscar_usuario_por_colonia(
    colonia: int, 
    servicio: Annotated[UsuarioServicio, Depends(get_usuario_servicio)],
    _: Usuario = Depends(require_roles(1, 2, 3)),
):
    """Busca y devuelve una lista de usuarios miembros  en una colonia específica."""
    return await servicio.buscar_por_colonia(colonia)