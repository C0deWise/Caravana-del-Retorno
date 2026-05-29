"""
    grupo_retorno_servicio.py define el servicio para gestionar los grupos de retornos, solicitudes a grupos de retorno,
    y la asociación de usuarios a grupos de retorno. 
"""

from app.notificaciones.events.events import EventoBase, TipoEvento
from app.notificaciones.events.patron_observer import Publicador
from app.notificaciones.services.notificacion_crear_service import NotificacionCrearService
from app.retornos.esquemas.solicitud_retorno_grupo_esquema import SolicitudRetornoGrupoLiderRespuesta, SolicitudRetornoGrupoRespuesta, SolicitudRetornoGrupoUsuarioRespuesta
from app.retornos.excepciones.registro_retorno_excepciones import GrupoNoEncontrado, SolicitudGrupoRetornoEstadoInvalido, SolicitudGrupoRetornoNoExistente, UsuarioNoEstaEnUnGrupo, UsuarioNoPerteneceAlaMismaColonia
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.solicitud_grupo_retorno_repositorio import SolicitudGrupoRetornoRepositorio
from app.retornos.esquemas.grupo_retorno_esquema import GrupoRetornoCrear, GrupoRetornoEliminadoRespuesta, GrupoRetornoRespuesta
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno # Import SolicitudGrupoRetorno
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida # Para el esquema de respuesta del líder
from app.usuarios.models.usuario import Usuario # Para el tipo de retorno del líder
from fastapi import HTTPException, status
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno
from app.retornos.esquemas.solicitud_grupo_retorno_esquema import SolicitudGrupoRetornoEstado
class GrupoRetornoServicio:
    def __init__(self, repositorio_retorno: RetornoRepository = None, repositorio_grupos: GrupoRetornoRepositorio = None, repositorio_solicitudes: SolicitudGrupoRetornoRepositorio = None, repositorio_usuario_grupo: RetornoGrupoUsuarioRepositorio = None, repositorio_usuario: UsuarioRepositorio = None, repositorio_registro_individual: RegistroRetornoRepositorio = None, repositorio_registro_grupo: RegistroRetornoGrupoRepositorio = None,  servicio_notificaciones: NotificacionCrearService = None): # type: ignore
        self.repositorio_retorno = repositorio_retorno
        self.repositorio_grupos = repositorio_grupos
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_usuario_grupo = repositorio_usuario_grupo
        self.repositorio_usuario = repositorio_usuario
        self.repositorio_registro_individual = repositorio_registro_individual
        self.repositorio_registro_grupo = repositorio_registro_grupo
        self.publicador = Publicador(servicio_notificaciones)

    async def _validar_grupo_existente(self, gr_codigo: int):
        grupo = await self.repositorio_grupos.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise GrupoNoEncontrado(gr_codigo)
        return grupo

    async def _validar_usuario_existente(self, us_codigo: int):
        usuario = await self.repositorio_usuario.obtener_usuario_por_id(us_codigo)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Usuario con ID {us_codigo} no encontrado."
            )
        return usuario
    
    async def _validar_si_usuario_es_miembro(self, us_codigo: int, gr_codigo: int):
        miembro_en_grupo = await self.repositorio_usuario_grupo.existe_usuario_en_grupo_para_retorno(us_codigo, gr_codigo)
        if not miembro_en_grupo:
            raise UsuarioNoEstaEnUnGrupo(us_codigo, gr_codigo)
        
    async def _validar_si_usuario_es_lider(self, us_codigo: int, gr_codigo: int):
        grupo = await self._validar_grupo_existente(gr_codigo)
        print(grupo)
        if grupo.us_codigo_lider == us_codigo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El líder del grupo no puede ser removido. Para eliminar el grupo, por favor elimine el grupo completo."
            )

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
    
    async def aceptar_solicitud_grupo_retorno(self, sol_codigo:int):
        solicitud = await self.repositorio_solicitudes.obtener_solicitud_por_id(sol_codigo)
        if not solicitud:
            raise SolicitudGrupoRetornoNoExistente(sol_codigo)
        lider_grupo = solicitud.grupo.lider
        usuario_solicitud = solicitud.usuario
        if lider_grupo.co_codigo != usuario_solicitud.co_codigo:
            raise UsuarioNoPerteneceAlaMismaColonia(solicitud.us_codigo, solicitud.grupo.us_codigo_lider)
        if solicitud.solgr_estado != SolicitudGrupoRetornoEstado.PENDIENTE:
            raise SolicitudGrupoRetornoEstadoInvalido(solicitud.solgr_codigo, solicitud.solgr_estado.value)
        solicitud_aceptada = await self.repositorio_solicitudes.aceptar_solicitud_grupo_retorno(sol_codigo)
        if solicitud_aceptada:
            await self.repositorio_usuario_grupo.asociar_usuario_a_grupo_retorno(solicitud.us_codigo, solicitud.gr_codigo)
        await self._rechazar_solicitudes_pendientes_por_usuario(solicitud.us_codigo)
        return SolicitudRetornoGrupoRespuesta(
            id=solicitud_aceptada.solgr_codigo,
            usuario_id=solicitud_aceptada.us_codigo,
            grupo_id=solicitud_aceptada.gr_codigo,
            estado=solicitud_aceptada.solgr_estado,
            timestamp=solicitud_aceptada.solgr_time_stamp
        )
    
    async def rechazar_solicitud_grupo_retorno(self, sol_codigo:int):
        solicitud = await self.repositorio_solicitudes.obtener_solicitud_por_id(sol_codigo)
        if not solicitud:
            raise SolicitudGrupoRetornoNoExistente(sol_codigo)
        if solicitud.solgr_estado != SolicitudGrupoRetornoEstado.PENDIENTE:
            raise SolicitudGrupoRetornoEstadoInvalido(solicitud.solgr_codigo, solicitud.solgr_estado)
        solicitud_rechazada = await self.repositorio_solicitudes.rechazar_solicitud_grupo_retorno(sol_codigo)
        return SolicitudRetornoGrupoRespuesta(
            id=solicitud_rechazada.solgr_codigo,  
            usuario_id=solicitud_rechazada.us_codigo,
            grupo_id=solicitud_rechazada.gr_codigo,
            estado=solicitud_rechazada.solgr_estado,
            timestamp=solicitud_rechazada.solgr_time_stamp) 
    
    async def obtener_solicitudes_por_grupo_retorno(self, grupo_retorno_id):
        solicitudes = await self.repositorio_solicitudes.obtener_solicitudes_por_grupo_retorno(grupo_retorno_id)
        return [SolicitudRetornoGrupoLiderRespuesta(
            id=solicitud.solgr_codigo,
            usuario_id=solicitud.us_codigo,
            grupo_id=solicitud.gr_codigo,
            correo_usuario=solicitud.usuario.us_correo,
            estado=solicitud.solgr_estado,
            timestamp=solicitud.solgr_time_stamp
        ) for solicitud in solicitudes]

    async def obtener_solicitudes_recientes_por_usuario(self, usuario_id):
        solicitudes_recientes = await self.repositorio_solicitudes.obtener_solicitudes_recientes_por_usuario(usuario_id)
        return [SolicitudRetornoGrupoUsuarioRespuesta(
            id=solicitud.solgr_codigo,
            usuario_id=solicitud.us_codigo,
            grupo_id=solicitud.gr_codigo,
            nombre_lider=f"{solicitud.grupo.lider.us_nombre} {solicitud.grupo.lider.us_apellido}",
            estado=solicitud.solgr_estado,
            timestamp=solicitud.solgr_time_stamp
        ) for solicitud in solicitudes_recientes]

    async def _rechazar_solicitudes_pendientes_por_usuario(self, usuario_id):
        await self.repositorio_solicitudes.rechazar_solicitudes_pendientes_por_usuario(usuario_id)
    
    async def obtener_grupo_por_usuario_retorno(self, usuario_id: int, retorno_id: int) -> GrupoRetornoRespuesta | None:
        grupo = await self.repositorio_usuario_grupo.obtener_grupo_por_usuario_retorno(usuario_id, retorno_id)
        if grupo:
            return GrupoRetornoRespuesta.model_validate(grupo)
        raise UsuarioNoEstaEnUnGrupo(usuario_id, retorno_id)
    
    async def obtener_usuarios_por_grupo(self, gr_codigo: int) -> list[UsuarioSalida]:
        grupo =  await self.repositorio_grupos.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise GrupoNoEncontrado(gr_codigo)
        usuarios = await self.repositorio_usuario_grupo.obtener_miembros_por_grupo(gr_codigo)
        return [UsuarioSalida.model_validate(usuario) for usuario in usuarios]

    async def remover_miembro_de_grupo_retorno(self, us_codigo: int, gr_codigo: int):
        """Permite eliminar un miembro de una grupo de retorno específico, siempre y cuando no
        sea el líder del grupo.
        Parametros:
            - us_codigo (int): ID del usuario a eliminar del grupo.
            - gr_codigo (int): ID del grupo de retorno del cual se desea eliminar al usuario.
        Retorna:
            - bool: True si el usuario fue eliminado exitosamente, False si el usuario no era miembro del grupo o si se intentó eliminar al líder.
        """
        await self._validar_grupo_existente(gr_codigo)
        await self._validar_usuario_existente(us_codigo)
        await self._validar_si_usuario_es_miembro(us_codigo, gr_codigo)
        await self._validar_si_usuario_es_lider(us_codigo, gr_codigo)
        return await self.repositorio_usuario_grupo.remover_miembro_de_grupo_retorno(us_codigo, gr_codigo)

    
    async def eliminar_grupo_retorno(self, gr_codigo: int):
        grupo = await self.repositorio_grupos.obtener_grupo_por_id(gr_codigo)

        if not grupo:
            raise GrupoNoEncontrado(gr_codigo)

        miembros = await self.obtener_usuarios_por_grupo(gr_codigo)
        solicitudes = await self.obtener_solicitudes_por_grupo_retorno(gr_codigo)
        lider = await self.obtener_lider_por_grupo_id(gr_codigo)

        ids_usuarios_solicitudes_pendientes = [
            sol.usuario_id
            for sol in solicitudes
            if sol.estado == SolicitudGrupoRetornoEstado.PENDIENTE
        ]

        ids_miembros = [m.id for m in miembros]

        await self.repositorio_grupos.eliminar_grupo_retorno(gr_codigo)

        receptores_ids = (
            ids_miembros + ids_usuarios_solicitudes_pendientes
        )
        #excluir el id del lider para no mandarle la notificacion
        receptores_ids.remove(lider.id)
        evento = EventoBase(
            tipo_evento=TipoEvento.ELIMINAR_GRUPO_RETORNO,
            datos={
                "nombre_lider": f"{lider.nombre} {lider.apellido}"
            },
            receptores=receptores_ids
        )

        await self.publicador.notificar(evento=evento)

        return GrupoRetornoEliminadoRespuesta(
            gr_codigo=gr_codigo,
            mensaje="Grupo de retorno eliminado exitosamente."
        )
    