"""
Modulo que define el servicio para el registro a un retorno.
Contiene la lógica de negocio relacionada con el proceso de registro a un retorno,
utilizando el repositorio para interactuar con la base de datos y los esquemas para 
estructurar los datos de entrada y salida.
"""

from app.retornos.excepciones.retorno_excepciones import RegistroIndividualParqueaderoExcedidoError
from app.retornos.esquemas.retorno_esquemas import RetornoResponse
from app.retornos.modelos.retorno_modelo import Retorno
from sqlalchemy.ext.asyncio import AsyncSession
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoDarseDeBaja, RegistroRetornoRespuesta
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.retornos.excepciones.registro_retorno_excepciones import RetornoEstadoFinalizadoDarseDeBaja, RetornoNoExistente, RetornoEstadoFinalizado, UsuarioNoExistente, UsuarioNoRegistradoEnRetorno, UsuarioSinColonia, UsuarioYaRegistrado

class RegistroRetornoServicio:
    def __init__(self, repositorio: RegistroRetornoRepositorio, retorno_repositorio: RetornoRepository = None, usuario_servicio: UsuarioServicio = None) -> None:
        self.repositorio = repositorio 
        self.retorno_repositorio = retorno_repositorio
        self.usuario_servicio = usuario_servicio

    async def crear_registro_retorno(self, data: RegistroRetornoCrear) -> RegistroRetornoRespuesta:
        """
        Proceso de registro a un retorno, validando que el retorno exista, que el usuario exista 
        y tenga colonia asignada, y que no esté ya registrado en ese retorno.
        Parámetros:
            - data (RegistroRetornoCrear): Esquema con los datos necesarios para crear un registro de retorno.
        Retorna:
            - RegistroRetornoRespuesta: Esquema con los datos del registro de retorno creado.
        Excepciones:
            - RetornoNoExistente: Si el retorno especificado no existe.
            - RetornoEstadoFinalizado: Si el retorno especificado ya ha finalizado.
            - UsuarioNoExistente: Si el usuario especificado no existe.
            - UsuarioSinColonia: Si el usuario especificado no pertenece a ninguna colonia.
            - UsuarioYaRegistrado: Si el usuario ya está registrado en el retorno especificado.
        """
        retorno = await self.retorno_repositorio.get_by_codigo(data.retorno)
        if not retorno:
            raise RetornoNoExistente(data.retorno)
        
        if retorno.estado == "finalizado":
            raise RetornoEstadoFinalizado(data.retorno)
        
        usuario = await self.usuario_servicio.obtener_usuario_por_id(data.usuario)

        if not usuario:
            raise UsuarioNoExistente(data.usuario)

        if not usuario.co_codigo:
            raise UsuarioSinColonia(data.usuario)
        
        usuario_existente = await self.repositorio.obtener_registro_retorno_por_usuario_y_retorno(data.usuario, data.retorno)
        if usuario_existente:
            raise UsuarioYaRegistrado(data.usuario, data.retorno)
        total_parqueaderos = data.num_parqueadero_carro + data.num_parqueadero_moto
        if total_parqueaderos > 1:
            raise RegistroIndividualParqueaderoExcedidoError()
        nuevo_registro = await self.repositorio.crear_registro_retorno(data)
        return RegistroRetornoRespuesta.model_validate(nuevo_registro)

    async def obtener_registro_retorno_por_usuario_y_retorno(
        self,
        usuario_id: int,
        retorno_id: int,
    ) -> RegistroRetornoRespuesta | None:
        """
        Obtiene un registro de retorno específico para un usuario y retorno dados.
        Paramétros:
            - usuario_id (int): ID del usuario.
            - retorno_id (int): ID del retorno.
        Retorna:
            - RegistroRetornoRespuesta: Esquema con los datos del registro de retorno encontrado, o None si no existe. 
        """
      
        registro = await self.repositorio.obtener_registro_retorno_por_usuario_y_retorno(usuario_id, retorno_id)
        if registro is None:
            return None
        return RegistroRetornoRespuesta.model_validate(registro)
    
    async def darse_de_baja(self, datos: RegistroRetornoDarseDeBaja):
        """
        Permite a un usuario darse de baja de un retorno específico, eliminando su registro de retorno.
        Retorna:
            - bool: True si el registro de retorno fue eliminado exitosamente, False si no se encontró el registro.
        """
        retorno = await self.retorno_repositorio.get_by_codigo(datos.retorno)
        if not retorno:
            raise RetornoNoExistente(datos.retorno)
        
        if retorno.estado == "finalizado":
            raise RetornoEstadoFinalizadoDarseDeBaja(datos.retorno)
        
        usuario = await self.usuario_servicio.obtener_usuario_por_id(datos.usuario)

        if not usuario:
            raise UsuarioNoExistente(datos.usuario)
        usuario_registrado = await self.repositorio.obtener_registro_retorno_por_usuario_y_retorno(datos.usuario, datos.retorno)
        if not usuario_registrado:
            raise UsuarioNoRegistradoEnRetorno(datos.usuario, datos.retorno)
        
        return await self.repositorio.eliminar_registro_retorno(datos)
       
    
    async def obtener_registros_retorno_por_usuario(self, usuario_id):
        return await self.repositorio.obtener_registros_retorno_por_usuario(usuario_id)
    
    async def obtener_registros_retorno_activos_por_usuario(self, usuario_id) -> list[RetornoResponse]:
        usuario = await self.usuario_servicio.obtener_usuario_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoExistente(usuario_id)
        
        return await self.repositorio.obtener_registros_retorno_activos_usuario(usuario_id)
