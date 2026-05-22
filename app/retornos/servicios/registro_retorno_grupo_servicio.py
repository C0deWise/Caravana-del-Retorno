"""
    registro_retorno_grupo_servicio.py define el servicio para gestionar el registro de grupos a retornos.
"""

from fastapi import HTTPException, status
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear, RegistroRetornoGrupoRespuesta, RegistroRetornoGrupoEditar
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.persona_repositorio import PersonaRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida
from app.retornos.excepciones.registro_retorno_grupo_excepciones import (
    RetornoNoExistente, 
    RetornoNoActivo, 
    RegistroGrupoRetornoNoExistente,
    GrupoRetornoNoExistente,
    RegistroGrupoRetornoNoExiste
)

class RegistroRetornoGrupoServicio: 
    def __init__(
        self, 
        repositorio_registro_grupo: RegistroRetornoGrupoRepositorio, 
        repositorio_grupo: GrupoRetornoRepositorio,
        repositorio_retorno: RetornoRepository,
        repositorio_usuario_grupo: RetornoGrupoUsuarioRepositorio,
        repositorio_persona: PersonaRepositorio # Nuevo repositorio para personas
    ):
        self.repositorio_registro_grupo = repositorio_registro_grupo
        self.repositorio_grupo = repositorio_grupo
        self.repositorio_retorno = repositorio_retorno
        self.repositorio_usuario_grupo = repositorio_usuario_grupo
        self.repositorio_persona = repositorio_persona # Asignar el nuevo repositorio

    def _validar_retorno(self, retorno, codigo_retorno, accion):
        if not retorno:
            raise RetornoNoExistente(codigo_retorno)
        
        if retorno.estado != "activo":
            raise RetornoNoActivo(codigo_retorno, retorno.estado.value, accion)

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
        
        self._validar_retorno(ultimo_retorno, datos.retorno, "registrarse")

        # 3. Validar que el grupo tenga al menos 1 integrante (usuario o persona) aparte del líder
        num_usuarios_adicionales = await self.repositorio_usuario_grupo.contar_miembros_adicionales(datos.cod_grupo)
        personas_en_grupo = await self.repositorio_persona.obtener_personas_por_grupo(datos.cod_grupo)
        num_personas = len(personas_en_grupo)
        total_integrantes_adicionales = num_usuarios_adicionales + num_personas + 1 # +1 para incluir al líder en el conteo total de integrantes del grupo
        if total_integrantes_adicionales < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grupo debe tener al menos un integrante (usuario o persona) aparte del líder para ser registrado."
            )
        total_parqueaderos = datos.num_parqueadero_carro + datos.num_parqueadero_moto
        if total_parqueaderos > total_integrantes_adicionales:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grupo no puede solicitar más parqueaderos que el número de integrantes que tiene el grupo."
            )

        if datos.num_hospedaje > total_integrantes_adicionales:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grupo no puede solicitar más hospedajes que el número de integrantes que tiene el grupo."
            )
        
        if datos.num_transporte > total_integrantes_adicionales:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El grupo no puede solicitar más transportes que el número de integrantes que tiene el grupo."
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
        #asociar al lider con el grupo de retorno registrado
        await self.repositorio_usuario_grupo.asociar_usuario_a_grupo_retorno(grupo.us_codigo_lider, datos.cod_grupo)
        return RegistroRetornoGrupoRespuesta.model_validate(registro)

    async def obtener_miembros_por_grupo(self, gr_codigo: int) -> list[UsuarioSalida]:
        """
        Retorna la lista completa de integrantes de un grupo, incluyendo al líder,
        usuarios adicionales y personas (asistentes no usuarios).
        """
        grupo = await self.repositorio_grupo.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El grupo con código {gr_codigo} no existe."
            )
        
    
        
        # 1. Obtener usuarios miembros (invitados que aceptaron)
        miembros_usuarios = await self.repositorio_usuario_grupo.obtener_miembros_por_grupo(gr_codigo)
        
        # 2. Obtener personas (asistentes adicionales no registrados como usuarios)
        personas = await self.repositorio_persona.obtener_personas_por_grupo(gr_codigo)
        
        resultado: list[UsuarioSalida] = []
            
        for m in miembros_usuarios:
            resultado.append(UsuarioSalida.model_validate(m))
            
        # Mapeo manual de Persona a UsuarioSalida para unificar la lista de integrantes
        for p in personas:
            resultado.append(UsuarioSalida(
                id=p.pe_codigo,
                nombre=p.pe_nombre,
                apellido=p.pe_apellido,
                correo=p.pe_correo,
                documento=p.pe_documento
            ))
            
        return resultado

    async def editar_registro_retorno_grupo(self, registro_id: int, datos: RegistroRetornoGrupoEditar) -> RegistroRetornoGrupoRespuesta:
        """
        Edita un registro de grupo en un retorno aplicando validaciones de negocio.
        Parámetros:
            registro_id: ID del registro de grupo a editar.
            datos: Datos actualizados para el registro de grupo.
        Retorna:
            RegistroRetornoGrupoRespuesta: El registro de grupo actualizado.
        Excepciones:
            HTTPException 404: Si el registro de grupo no existe.
            HTTPException 400: Si el retorno asociado al registro no está activo.
        """
        registro_existente = await self.repositorio_registro_grupo.obtener_registro_por_id(registro_id)
        if not registro_existente:
            raise RegistroGrupoRetornoNoExiste(registro_id)

        retorno = await self.repositorio_retorno.get_by_codigo(registro_existente.retorno)
        self._validar_retorno(retorno, registro_existente.retorno, "editar este registro")
        
        registro_actualizado = await self.repositorio_registro_grupo.editar_registro_grupo_retorno(registro_id, datos)
        return RegistroRetornoGrupoRespuesta.model_validate(registro_actualizado)
    
    async def consultar_registro_por_grupo_y_retorno(self, gr_codigo: int, re_codigo: int) -> RegistroRetornoGrupoRespuesta:
        """
        Consulta el registro de un grupo en un retorno específico.
        Parámetros:
            gr_codigo: Código del grupo a consultar.
            re_codigo: Código del retorno a consultar.
        Retorna:
            RegistroRetornoGrupoRespuesta con los detalles del registro encontrado.
        Excepciones:
            HTTPException 404: Si el grupo o el retorno no existen, o si no hay un registro para ese grupo en ese retorno.
        """
        retorno = await self.repositorio_retorno.get_by_codigo(re_codigo)
        if not retorno:
            raise RetornoNoExistente(re_codigo)
        
        grupo = await self.repositorio_grupo.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise GrupoRetornoNoExistente(gr_codigo)
        
        registro = await self.repositorio_registro_grupo.obtener_registro_por_grupo_y_retorno(gr_codigo, re_codigo)
        if not registro:
            raise RegistroGrupoRetornoNoExistente(gr_codigo, re_codigo)
        return RegistroRetornoGrupoRespuesta.model_validate(registro)
