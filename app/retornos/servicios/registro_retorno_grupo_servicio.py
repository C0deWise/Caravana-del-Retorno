"""
    registro_retorno_grupo_servicio.py define el servicio para gestionar el registro de grupos a retornos.
"""

from fastapi import HTTPException, status
from app.retornos.esquemas.registro_retorno_grupo_esquema import RegistroRetornoGrupoCrear, RegistroRetornoGrupoRespuesta
from app.retornos.repositorios.grupo_retorno_repositorio import GrupoRetornoRepositorio
from app.retornos.repositorios.registro_retorno_grupo_repositorio import RegistroRetornoGrupoRepositorio
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.retornos.repositorios.persona_repositorio import PersonaRepositorio
from app.retornos.repositorios.retorno_grupo_usuario_repositorio import RetornoGrupoUsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioSalida


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

        # 3. Validar que el grupo tenga al menos 1 integrante (usuario o persona) aparte del líder
        num_usuarios_adicionales = await self.repositorio_usuario_grupo.contar_miembros_adicionales(datos.cod_grupo)
        personas_en_grupo = await self.repositorio_persona.obtener_personas_por_grupo(datos.cod_grupo)
        num_personas = len(personas_en_grupo)
        total_integrantes_adicionales = num_usuarios_adicionales + num_personas
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
        Retorna la lista completa de integrantes de un grupo, incluyendo al líder,
        usuarios adicionales y personas (asistentes no usuarios).
        """
        grupo = await self.repositorio_grupo.obtener_grupo_por_id(gr_codigo)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El grupo con código {gr_codigo} no existe."
            )
        
        # 1. Obtener los datos del líder
        lider = await self.repositorio_grupo.obtener_lider_por_grupo_id(gr_codigo)
        
        # 2. Obtener usuarios miembros (invitados que aceptaron)
        miembros_usuarios = await self.repositorio_usuario_grupo.obtener_miembros_por_grupo(gr_codigo)
        
        # 3. Obtener personas (asistentes adicionales no registrados como usuarios)
        personas = await self.repositorio_persona.obtener_personas_por_grupo(gr_codigo)
        
        resultado: list[UsuarioSalida] = []
        
        if lider:
            resultado.append(UsuarioSalida.model_validate(lider))
            
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

    
