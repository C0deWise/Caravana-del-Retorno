"""
    registro_retorno_grupo_servicio.py define el servicio para gestionar el registro de grupos a retornos.
"""

from fastapi import HTTPException, status
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear, RegistroRetornoGrupoRespuesta
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida


class RegistroRetornoGrupoServicio: 
    def __init__(
        self, 
        repositorio_registro_grupo: RegistroRetornoGrupoRepositorio, 
        repositorio_grupo: GrupoRetornoRepositorio,
        repositorio_retorno: RetornoRepository,
        repositorio_usuario_grupo: RetornoGrupoUsuarioRepositorio
    ):
        self.repositorio_registro_grupo = repositorio_registro_grupo
        self.repositorio_grupo = repositorio_grupo
        self.repositorio_retorno = repositorio_retorno
        self.repositorio_usuario_grupo = repositorio_usuario_grupo

    async def crear_registro_retorno_grupo(self, datos: RegistroRetornoGrupoCrear) -> RegistroRetornoGrupoRespuesta:
        """
        Registra un grupo en un retorno aplicando validaciones de negocio.
        """
        # 1. Validar que el grupo existe
        grupo = await self.repositorio_grupo.obtener_grupo_por_id(datos.cod_grupo)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El grupo con código {datos.cod_grupo} no existe."
            )

        # 2. Validar que el retorno sea el último vigente
        ultimo_retorno = await self.repositorio_retorno.obtener_ultimo_retorno()
        if not ultimo_retorno or ultimo_retorno.codigo != datos.retorno:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El registro solo es permitido para el último retorno vigente."
            )

        # 3. Validar que el grupo tenga al menos 1 integrante aparte del líder
        num_miembros = await self.repositorio_usuario_grupo.contar_miembros_adicionales(datos.cod_grupo)
        if num_miembros < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grupo debe tener al menos un integrante (aparte del líder) para ser registrado."
            )

        # 4. Restricción Adicional: Evitar duplicidad de registro
        ya_registrado = await self.repositorio_registro_grupo.obtener_registro_por_grupo_y_retorno(
            datos.cod_grupo, datos.retorno
        )
        if ya_registrado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este grupo ya se encuentra registrado para el retorno actual."
            )

        registro = await self.repositorio_registro_grupo.crear_registro_grupo_retorno(datos)
        return RegistroRetornoGrupoRespuesta.model_validate(registro)

    async def obtener_usuarios_por_grupo(self, gr_codigo: int) -> list[UsuarioSalida]:
        """
        Retorna la lista de usuarios pertenecientes a un grupo.
        """
        grupo = await self.repositorio_grupo.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El grupo con código {gr_codigo} no existe."
            )
        
        miembros = await self.repositorio_usuario_grupo.obtener_miembros_por_grupo(gr_codigo)
        return [UsuarioSalida.model_validate(m) for m in miembros]

    
