"""
    grupo_retorno_servicio.py define el servicio para gestionar los grupos de retornos, solicitudes a grupos de retorno,
    y la asociación de usuarios a grupos de retorno. 
"""

from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.solicitud_grupo_retorno_repositorio import SolicitudGrupoRetornoRepositorio
from app.retornos.esquemas.grupo_retorno_esquema import GrupoRetornoCrear, GrupoRetornoRespuesta
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno # Import SolicitudGrupoRetorno
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida # Para el esquema de respuesta del líder
from app.usuarios.models.usuario import Usuario # Para el tipo de retorno del líder
from fastapi import HTTPException, status
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno

class GrupoRetornoServicio:
    def __init__(self, repositorio_retorno: RetornoRepository, repositorio_grupos: GrupoRetornoRepositorio, repositorio_solicitudes: SolicitudGrupoRetornoRepositorio , repositorio_usuario_grupo: RetornoGrupoUsuarioRepositorio, repositorio_usuario: UsuarioRepositorio, repositorio_registro_individual: RegistroRetornoRepositorio, repositorio_registro_grupo: RegistroRetornoGrupoRepositorio | None = None): # type: ignore
        self.repositorio_retorno = repositorio_retorno
        self.repositorio_grupos = repositorio_grupos
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_usuario_grupo = repositorio_usuario_grupo
        self.repositorio_usuario = repositorio_usuario
        self.repositorio_registro_individual = repositorio_registro_individual
        self.repositorio_registro_grupo = repositorio_registro_grupo

    async def crear_grupo_retorno(self, datos):
        """
        Crea un nuevo grupo de retorno.
        Valida que el líder especificado exista.
        """
        lider_existente = await self.repositorio_usuario.obtener_usuario_por_id(datos.lider)
        if not lider_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {datos.lider} no encontrado"
            )

        ultimo_retorno = await self.repositorio_retorno.obtener_ultimo_retorno()
        if ultimo_retorno:
            registro_individual = await self.repositorio_registro_individual.obtener_registro_retorno_por_usuario_y_retorno(
                datos.lider,
                ultimo_retorno.codigo
            )
            if registro_individual:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario líder ya cuenta con un registro de retorno individual para el evento actual."
                )

            if self.repositorio_registro_grupo:
                lider_ya_registrado_en_grupo = await self.repositorio_registro_grupo.existe_lider_con_grupo_registrado_en_retorno(
                    datos.lider,
                    ultimo_retorno.codigo
                )
                if lider_ya_registrado_en_grupo:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El usuario líder ya está inscrito de forma grupal para el evento actual."
                    )
        
        nuevo_grupo = await self.repositorio_grupos.crear_grupo_retorno(datos)
        return GrupoRetornoRespuesta.model_validate(nuevo_grupo)
    
    async def obtener_grupos_por_lider_id(self, us_codigo_lider: int) -> list[GrupoRetornoRespuesta]:
        """
        Obtiene todos los grupos de retorno liderados por un usuario específico.
        """
        lider_existente = await self.repositorio_usuario.obtener_usuario_por_id(us_codigo_lider)
        if not lider_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {us_codigo_lider} no encontrado"
            )
        grupos = await self.repositorio_grupos.obtener_grupos_por_lider_id(us_codigo_lider)
        return [GrupoRetornoRespuesta.model_validate(grupo) for grupo in grupos]

    async def obtener_lider_por_grupo_id(self, gr_codigo: int) -> UsuarioSalida:
        """Obtiene los detalles del líder de un grupo de retorno específico."""
        lider = await self.repositorio_grupos.obtener_lider_por_grupo_id(gr_codigo)
        if not lider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grupo de retorno con código {gr_codigo} no encontrado o no tiene un líder asignado.")
        return UsuarioSalida.model_validate(lider)

    async def existe_grupo_retorno(self, gr_codigo: int) -> bool:
        """Verifica la existencia de un grupo de retorno."""
        grupo = await self.repositorio_grupos.obtener_grupo_por_id(gr_codigo)
        return grupo is not None

    async def crear_solicitud_grupo_retorno(self, us_codigo: int, gr_codigo: int) -> SolicitudGrupoRetorno:
        """
        Crea una solicitud para que un usuario se una a un grupo.
        Valida la existencia del usuario y del grupo.
        """
        # Validar existencia del usuario (individuo)
        usuario = await self.repositorio_usuario.obtener_usuario_por_id(us_codigo)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El usuario con ID {us_codigo} no existe en el sistema."
            )

        # Validar existencia del grupo
        grupo = await self.repositorio_grupos.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El grupo de retorno con ID {gr_codigo} no existe."
            )
            
        # Restricción: El líder no puede enviarse una solicitud a sí mismo
        if grupo.us_codigo_lider == us_codigo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El líder del grupo no puede enviarse una solicitud de unión a sí mismo."
            )
            
        # Obtener el último retorno para las validaciones de negocio
        ultimo_retorno = await self.repositorio_retorno.obtener_ultimo_retorno()
        if ultimo_retorno:
            # Restricción 1: No debe estar en usuario_grupo_retorno para el retorno actual
            en_grupo = await self.repositorio_usuario_grupo.existe_usuario_en_grupo_para_retorno(us_codigo, ultimo_retorno.codigo)
            if en_grupo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario ya pertenece a un grupo de retorno registrado para el evento actual."
                )

            # Restricción 2: No debe tener un registro individual (registro_retorno)
            registro_individual = await self.repositorio_registro_individual.obtener_registro_retorno_por_usuario_y_retorno(
                us_codigo, 
                ultimo_retorno.codigo
            )
            if registro_individual:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario ya cuenta con un registro de retorno individual para el evento actual."
                )

        return await self.repositorio_solicitudes.crear_solicitud_grupo_retorno(us_codigo, gr_codigo)
    
    async def aceptar_solicitud_grupo_retorno(self, datos):
        pass

    async def rechazar_solicitud_grupo_retorno(self, datos):
        pass

    async def _asociar_usuario_a_grupo_retorno(self, datos):
        pass