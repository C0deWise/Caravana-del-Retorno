"""
Dependencias FastAPI para autenticacion y autorizacion por roles.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.security import TokenError, decode_token

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token = credentials.credentials
    try:
        payload = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = int(payload["sub"])
    repositorio = UsuarioRepositorio(db)
    usuario = await repositorio.obtener_usuario_por_id(user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado para el token enviado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def require_roles(*allowed_role_codes: int):
    def _checker(usuario=Depends(get_current_user)):
        if usuario.ro_codigo not in allowed_role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este recurso",
            )
        return usuario

    return _checker
