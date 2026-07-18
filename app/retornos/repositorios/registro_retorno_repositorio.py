"""
Modulo que define el repositorio para el registro a un retorno.
Contiene los métodos para interactuar con la base de datos relacionados con el 
proceso de registro a un retorno.
"""

from app.retornos.esquemas.retorno_esquemas import RetornoResponse
from app.retornos.modelos.retorno_modelo import Retorno
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.retornos.esquemas.registro_retorno_esquema import RegistroRetornoCrear, RegistroRetornoEditar, RegistroRetornoDarseDeBaja, RegistroRetornoRespuesta
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.usuarios.models.usuario import Usuario

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
            num_parqueadero_carro=registro_retorno.num_parqueadero_carro,
            num_parqueadero_moto=registro_retorno.num_parqueadero_moto,
            anotacion=registro_retorno.anotacion
        )
        self.db.add(nuevo_registro)
        await self.db.commit()
        await self.db.refresh(nuevo_registro)
        return nuevo_registro
    async def actualizar_registro_retorno(self, registro_id: int, datos_actualizados: RegistroRetornoEditar) -> RegistroRetorno:
        """Actualiza un registro de retorno existente con nuevos datos."""
        registro = await self.obtener_registro_retorno_por_id(registro_id)
        if not registro:
            return None
        
        if datos_actualizados.num_hospedaje is not None:
            registro.num_hospedaje = datos_actualizados.num_hospedaje
        if datos_actualizados.num_transporte is not None:
            registro.num_transporte = datos_actualizados.num_transporte
        if datos_actualizados.num_parqueadero_moto is not None:
            registro.num_parqueadero_moto = datos_actualizados.num_parqueadero_moto
        if datos_actualizados.num_parqueadero_carro is not None:
            registro.num_parqueadero_carro = datos_actualizados.num_parqueadero_carro
        if datos_actualizados.anotacion is not None:
            registro.anotacion = datos_actualizados.anotacion

        await self.db.commit()
        await self.db.refresh(registro)
        return registro

    async def obtener_registro_retorno_por_usuario_y_retorno(self, usuario_id, retorno_id): 
        """Obtiene un registro de retorno específico para un usuario y retorno dados."""
        resultado = await self.db.execute(select(RegistroRetorno).filter(RegistroRetorno.usuario == usuario_id, RegistroRetorno.retorno == retorno_id))
        return resultado.scalars().first()
    
    async def obtener_registro_retorno_por_id(self, registro_id: int) -> RegistroRetorno:
        """Obtiene un registro de retorno por su ID."""
        resultado = await self.db.execute(select(RegistroRetorno).filter(RegistroRetorno.codigo == registro_id))
        return resultado.scalars().first()
    async def eliminar_registro_retorno(self, datos: RegistroRetornoDarseDeBaja) -> bool:
        """Elimina un registro de retorno específico para un usuario y retorno dados."""
        resultado = await self.db.execute(select(RegistroRetorno).filter(RegistroRetorno.usuario == datos.usuario, RegistroRetorno.retorno == datos.retorno))
        registro = resultado.scalars().first()
        if registro:
            await self.db.delete(registro)
            await self.db.commit()
            return True
        return False
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
    
    async def hay_registros_retorno_colonia(self, cod_retorno:int, cod_colonia:int) -> bool:
        """
         Consulta si hay registros en cod_retorno de la colonia cod_colonia
         retorna:
            True: Hay registros 
            False: No hay registros
        """
        stmt = select(RegistroRetorno).join(Usuario,
                   Usuario.us_codigo == RegistroRetorno.usuario).where(
                Usuario.co_codigo == cod_colonia,
                RegistroRetorno.retorno == cod_retorno
            )
        resultado = (await self.db.execute(stmt)).first()
        return resultado is not None

    async def hay_registros_retorno(self, cod_retorno:int)-> bool:
        """
         Consulta si hay registros en cod_retorno
         retorna:
            True: Hay registros 
            False: No hay registros
        """
        stmt = select(RegistroRetorno).where(
                RegistroRetorno.retorno == cod_retorno
            )
        resultado = (await self.db.execute(stmt)).first()
        return resultado is not None

