"""
Modulo que define el repositorio para el registro a un retorno.
Contiene los métodos para interactuar con la base de datos relacionados con el 
proceso de registro a un retorno.
"""

from app.retornos.esquemas.retorno_esquemas import RetornoResponse
from app.retornos.modelos.retorno_modelo import Retorno
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoRespuesta
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno

class RegistroRetornoRepositorio:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_registro_retorno(self, registro_retorno: RegistroRetornoCrear) -> RegistroRetorno:
        """Crea un nuevo registro de retorno en la base de datos."""
        nuevo_registro = RegistroRetorno(
            usuario=registro_retorno.usuario,
            retorno=registro_retorno.retorno,
            num_hospedaje=registro_retorno.num_hospedaje,
            num_transporte=registro_retorno.num_transporte,
            num_parqueadero=registro_retorno.num_parqueadero,
            anotacion=registro_retorno.anotacion
        )
        self.db.add(nuevo_registro)
        await self.db.commit()
        await self.db.refresh(nuevo_registro)
        return nuevo_registro
    
    async def obtener_registro_retorno_por_usuario_y_retorno(self, usuario_id, retorno_id): 
        """Obtiene un registro de retorno específico para un usuario y retorno dados."""
        resultado = await self.db.execute(select(RegistroRetorno).filter(RegistroRetorno.usuario == usuario_id, RegistroRetorno.retorno == retorno_id))
        return resultado.scalars().first()
    
    async def obtener_registros_retorno_activo_por_usuario(self, usuario_id):
        """Obtiene todos los registros de retorno asociados a un usuario específico."""
        resultado = await self.db.execute(select(RegistroRetorno).filter(RegistroRetorno.usuario == usuario_id))
        return resultado.scalars().all()
    
    async def obtener_registros_retorno_activos_usuario(self, usuario_id) -> list[Retorno]:
        """Obtiene todos los registros de retorno activos asociados a un usuario específico."""
        query = select(RegistroRetorno).join(Retorno).where(
            RegistroRetorno.usuario == usuario_id, 
            Retorno.estado == "activo"
        )
        resultado = await self.db.execute(query)
        return resultado.scalars().all()