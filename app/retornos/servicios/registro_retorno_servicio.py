from sqlalchemy.ext.asyncio import AsyncSession
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.retornos.repositorios.registro_retorno_repositorio import RegistroRetornoRepositorio
from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoRespuesta
from app.retornos.repositorios.retorno_repositorio import RetornoRepository
from app.usuarios.services.usuario_servicio import UsuarioServicio
from app.retornos.excepciones.registro_retorno_excepciones import RetornoNoExistente, RetornoEstadoFinalizado, UsuarioNoExistente, UsuarioSinColonia, UsuarioYaRegistrado

class RegistroRetornoServicio:
    def __init__(self, repositorio: RegistroRetornoRepositorio = None, retorno_repositorio: RetornoRepository = None, usuario_servicio: UsuarioServicio = None) -> None:
        self.repositorio = repositorio 
        self.retorno_repositorio = retorno_repositorio
        self.usuario_servicio = usuario_servicio

    async def crear_registro_retorno(self, data: RegistroRetornoCrear) -> RegistroRetornoRespuesta:
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
        
        return await self.repositorio.crear_registro_retorno(data)

    async def obtener_registro_retorno_por_usuario_y_retorno(self, usuario_id, retorno_id):
        return await self.repositorio.obtener_registro_retorno_por_usuario_y_retorno(usuario_id, retorno_id)