from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoRespuesta
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno

class RegistroRetornoRepositorio:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_registro_retorno(self, registro_retorno: RegistroRetornoCrear) -> RegistroRetorno:
        nuevo_registro = RegistroRetorno(
            usuario=registro_retorno.usuario,
            retorno=registro_retorno.retorno,
            num_hospedaje=registro_retorno.num_hospedaje,
            num_transporte=registro_retorno.num_transporte,
            num_parqueadero=registro_retorno.num_parqueadero
        )
        self.db.add(nuevo_registro)
        await self.db.commit()
        await self.db.refresh(nuevo_registro)
        return nuevo_registro
    
    async def obtener_registro_retorno_por_usuario_y_retorno(self, usuario_id, retorno_id):
        resultado = await self.db.execute(select(RegistroRetorno).filter(RegistroRetorno.usuario == usuario_id, RegistroRetorno.retorno == retorno_id))
        return resultado.scalars().first()