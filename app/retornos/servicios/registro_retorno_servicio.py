"""
Modulo que define el servicio para el registro a un retorno.
Contiene la lógica de negocio relacionada con el proceso de registro a un retorno,
utilizando el repositorio para interactuar con la base de datos y los esquemas para 
estructurar los datos de entrada y salida.
"""

from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoEditar, RegistroRetornoRespuesta
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.retornos.excepciones.registro_retorno_excepciones import RegistroRetornoNoExistente, RetornoNoExistente, RetornoEstadoFinalizado, UsuarioNoExistente, UsuarioSinColonia, UsuarioYaRegistrado

class RegistroRetornoServicio:
    def __init__(
        self,
        repositorio: RegistroRetornoRepositorio,
        retorno_repositorio: RetornoRepository,
        usuario_servicio: UsuarioServicio,
    ) -> None:
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
        
        nuevo_registro = await self.repositorio.crear_registro_retorno(data)
        return RegistroRetornoRespuesta.model_validate(nuevo_registro)

    async def editar_registro_retorno(self,registro_id: int, data: RegistroRetornoEditar) -> RegistroRetornoRespuesta:
        """
        Edita un registro de retorno existente, permitiendo modificar las
        necesidades de transporte, hospedaje, parqueadero y anotaciones.
        """

        registro = await self.repositorio.obtener_registro_retorno_por_id(registro_id)

        if not registro:
            raise RegistroRetornoNoExistente(registro_id)

        await self.repositorio.actualizar_registro_retorno (registro_id, data)

        return RegistroRetornoRespuesta.model_validate(registro)
    
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