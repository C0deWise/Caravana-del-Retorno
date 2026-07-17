import asyncio
import logging
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, select
from passlib.context import CryptContext

import sys
import os

from app.retornos.modelos.retorno_grupo_usuario_modelo import RetornoGrupoUsuario
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.usuarios.models.usuario import Usuario, Rol, TipoDoc, Genero
from app.colonias.models.colonia_model import Colonia
from app.retornos.modelos.retorno_modelo import Retorno
from app.retornos.esquemas.retorno_esquemas import RetornoEstado
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.persona_modelo import Persona
from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Contexto para encriptar contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
CONTRASENA_ENCRIPTADA = pwd_context.hash("usuario123")


async def seed_data() -> None:
    """
    Script de seed que crea datos de prueba:
    - 3 Colonias
    - 6 Usuarios (2 por colonia, asociados a cada colonia)
    - 1 Retorno
    - 2 Grupos de retorno (liderados por usuarios)
    - 4 Personas (no usuarios)
    - Asociaciones de personas a grupos de retorno
    - Inscripciones individuales de usuarios a retorno
    - Inscripciones grupales de grupos a retorno
    """
    
    # Preparar URL de conexión
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        db_url = db_url.replace("://", "+asyncpg://", 1) if "+asyncpg" not in db_url else db_url

    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with async_session() as db:
        try:
            logger.info("Iniciando seed de datos...")

            # ═════════════════════════════════════════
            # VALIDACIÓN: Verificar si los datos ya existen
            # ═════════════════════════════════════════
            colonia_count_query = select(func.count(Colonia.codigo))
            result = await db.execute(colonia_count_query)
            colonia_count = result.scalar()
            
            if colonia_count > 0:
                logger.info("════════════════════════════════════════")
                logger.info("⚠ Datos de seed ya existen en la base de datos")
                logger.info(f"  • Colonias encontradas: {colonia_count}")
                logger.info("  • Omitiendo ejecución de seed de datos")
                logger.info("════════════════════════════════════════")
                return

            # ═════════════════════════════════════════
            # 1. CREAR COLONIAS
            # ═════════════════════════════════════════
            logger.info("Creando colonias...")
            
            colonias_data = [
                {"pais": "Colombia", "departamento": "Antioquia", "ciudad": "Medellín"},
                {"pais": "Colombia", "departamento": "Bogotá", "ciudad": "Bogotá"},
                {"pais": "Colombia", "departamento": "Valle del Cauca", "ciudad": "Cali"},
            ]
            
            colonias = []
            for colonia_data in colonias_data:
                colonia = Colonia(**colonia_data)
                db.add(colonia)
                colonias.append(colonia)
            
            await db.flush()  # Para obtener los IDs asignados
            logger.info(f"✓ {len(colonias)} colonias creadas")

            # ═════════════════════════════════════════
            # 2. CREAR USUARIOS (2 por colonia)
            # ═════════════════════════════════════════
            logger.info("Creando usuarios...")
            usuarios = []
            usuarios_data = [
                #admin
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "11111",
                    "us_celular": "3007777777",
                    "us_correo": "admin@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "admin",
                    "us_apellido": "admin",
                    "us_genero": Genero.M,
                    "us_fecha_nacimiento": date(1990, 5, 15),
                    "us_pais": "Colombia",
                    "us_departamento": "Antioquia",
                    "us_ciudad": "Medellín",
                    "ro_codigo": 3,  # admin
                },
                # Colonia 1
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "1001234567",
                    "us_celular": "3001111111",
                    "us_correo": "juan.perez@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "Juan",
                    "us_apellido": "Pérez",
                    "us_genero": Genero.M,
                    "us_fecha_nacimiento": date(1990, 5, 15),
                    "us_pais": "Colombia",
                    "us_departamento": "Antioquia",
                    "us_ciudad": "Medellín",
                    "co_codigo": colonias[0].codigo,
                    "ro_codigo": 1,  # usuario
                },
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "1002345678",
                    "us_celular": "3002222222",
                    "us_correo": "maria.garcia@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "María",
                    "us_apellido": "García",
                    "us_genero": Genero.OTRO,
                    "us_fecha_nacimiento": date(1992, 8, 20),
                    "us_pais": "Colombia",
                    "us_departamento": "Antioquia",
                    "us_ciudad": "Medellín",
                    "co_codigo": colonias[0].codigo,
                    "ro_codigo": 2,  # lider
                },
                # Colonia 2
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "1003456789",
                    "us_celular": "3003333333",
                    "us_correo": "carlos.lopez@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "Carlos",
                    "us_apellido": "López",
                    "us_genero": Genero.M,
                    "us_fecha_nacimiento": date(1988, 3, 10),
                    "us_pais": "Colombia",
                    "us_departamento": "Bogotá",
                    "us_ciudad": "Bogotá",
                    "co_codigo": colonias[1].codigo,
                    "ro_codigo": 1,
                },
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "1004567890",
                    "us_celular": "3004444444",
                    "us_correo": "ana.martinez@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "Ana",
                    "us_apellido": "Martínez",
                    "us_genero": Genero.F,
                    "us_fecha_nacimiento": date(1995, 12, 5),
                    "us_pais": "Colombia",
                    "us_departamento": "Bogotá",
                    "us_ciudad": "Bogotá",
                    "co_codigo": colonias[1].codigo,
                    "ro_codigo": 2,
                },
                # Colonia 3
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "1005678901",
                    "us_celular": "3005555555",
                    "us_correo": "luis.torres@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "Luis",
                    "us_apellido": "Torres",
                    "us_genero": Genero.M,
                    "us_fecha_nacimiento": date(1991, 7, 22),
                    "us_pais": "Colombia",
                    "us_departamento": "Valle del Cauca",
                    "us_ciudad": "Cali",
                    "co_codigo": colonias[2].codigo,
                    "ro_codigo": 1,
                },
                {
                    "us_tipo_doc": TipoDoc.CC,
                    "us_documento": "1006789012",
                    "us_celular": "3006666666",
                    "us_correo": "diana.cruz@email.com",
                    "us_contrasenia": CONTRASENA_ENCRIPTADA,
                    "us_nombre": "Diana",
                    "us_apellido": "Cruz",
                    "us_genero": Genero.F,
                    "us_fecha_nacimiento": date(1993, 11, 8),
                    "us_pais": "Colombia",
                    "us_departamento": "Valle del Cauca",
                    "us_ciudad": "Cali",
                    "co_codigo": colonias[2].codigo,
                    "ro_codigo": 2,
                },
            ]
            
            for usuario_data in usuarios_data:
                usuario = Usuario(**usuario_data)
                db.add(usuario)
                usuarios.append(usuario)
            
            await db.flush()
            logger.info(f"✓ {len(usuarios)} usuarios creados")

            # ═════════════════════════════════════════
            # 2.5 ESTABLECER LÍDERES DE COLONIAS
            # ═════════════════════════════════════════
            logger.info("Estableciendo líderes de colonias...")
            
            # Colonia 1: Líder María 
            colonias[0].lider = usuarios[2].us_codigo
            
            # Colonia 2: Líder Ana 
            colonias[1].lider = usuarios[3].us_codigo
            
            # Colonia 3: Líder Diana 
            colonias[2].lider = usuarios[6].us_codigo
            
            await db.flush()
            logger.info("✓ Líderes de colonias establecidos")

            # ═════════════════════════════════════════
            # 3. CREAR RETORNO
            # ═════════════════════════════════════════
            logger.info("Creando retorno...")
            
            retorno = Retorno(
                anio=2026,
                estado=RetornoEstado.ACTIVO,
                fecha_creacion=datetime.now()
            )
            db.add(retorno)
            await db.flush()
            logger.info(f"✓ Retorno creado: {retorno.codigo}")

            # ═════════════════════════════════════════
            # 4. CREAR GRUPOS DE RETORNO
            # ═════════════════════════════════════════
            logger.info("Creando grupos de retorno...")
            
            grupos = []
            # Grupo 1 liderado por María (usuario 2)
            grupo1 = GrupoRetorno(us_codigo_lider=usuarios[2].us_codigo)
            db.add(grupo1)
            grupos.append(grupo1)
            
            # Grupo 2 liderado por Ana (usuario 4)
            grupo2 = GrupoRetorno(us_codigo_lider=usuarios[3].us_codigo)
            db.add(grupo2)
            grupos.append(grupo2)
            
            await db.flush()
            logger.info(f"✓ {len(grupos)} grupos de retorno creados")

            # ═════════════════════════════════════════
            # 5. CREAR PERSONAS (no usuarios)
            # ═════════════════════════════════════════
            logger.info("Creando personas...")
            
            personas = []
            personas_data = [
                {
                    "pe_tipo_doc": TipoDoc.CC,
                    "pe_documento": "1007890123",
                    "pe_nombre": "Pedro",
                    "pe_apellido": "Ramírez",
                    "pe_correo": "pedro.ramirez@email.com",
                    "pe_fecha_nacimiento":date(2015, 5, 18),
                    "pe_genero": Genero.M
                },
                {
                    "pe_tipo_doc": TipoDoc.CC,
                    "pe_documento": "1008901234",
                    "pe_nombre": "Rosa",
                    "pe_apellido": "Sánchez",
                    "pe_correo": "rosa.sanchez@email.com",
                    "pe_fecha_nacimiento": date(1954, 8, 20),
                    "pe_genero": Genero.F
                },
                {
                    "pe_tipo_doc": TipoDoc.CC,
                    "pe_documento": "1009012345",
                    "pe_nombre": "Roberto",
                    "pe_apellido": "Díaz",
                    "pe_correo": "roberto.diaz@email.com",
                    "pe_fecha_nacimiento": date(2018, 1, 22),
                    "pe_genero": Genero.M
                },
                {
                    "pe_tipo_doc": TipoDoc.CC,
                    "pe_documento": "1010123456",
                    "pe_nombre": "Laura",
                    "pe_apellido": "Vega",
                    "pe_correo": "laura.vega@email.com",
                    "pe_fecha_nacimiento": date(2015, 2, 20),
                    "pe_genero": Genero.F
                },
            ]
            
            for persona_data in personas_data:
                persona = Persona(**persona_data)
                db.add(persona)
                personas.append(persona)
            
            await db.flush()
            logger.info(f"✓ {len(personas)} personas creadas")

            # ======================================
            # ASOCIAR USUARIOS A GRUPOS DE RETORNO
            # ======================================
            logger.info("Asociando usuarios a grupos de retorno...")
            # Grupo 1: María (lider)
            rgu1 = RetornoGrupoUsuario(us_codigo=usuarios[1].us_codigo, gr_codigo=grupos[0].gr_codigo)
            db.add(rgu1)

            # asociar a María (lider) al grupo 1
            rgu1_lider = RetornoGrupoUsuario(us_codigo=usuarios[2].us_codigo, gr_codigo=grupos[0].gr_codigo)
            db.add(rgu1_lider)

            # Grupo 2: Ana (lider)
            rgu2 = RetornoGrupoUsuario(us_codigo=usuarios[3].us_codigo, gr_codigo=grupos[1].gr_codigo)
            db.add(rgu2)

            # asociar a Ana (lider) al grupo 2
            rgu2_lider = RetornoGrupoUsuario(us_codigo=usuarios[4].us_codigo, gr_codigo=grupos[1].gr_codigo)
            db.add(rgu2_lider)
            await db.flush()
            logger.info("✓ Usuarios asociados a grupos de retorno")

            # ═════════════════════════════════════════
            # 7. ASOCIAR PERSONAS A GRUPOS
            # ═════════════════════════════════════════
            logger.info("Asociando personas a grupos de retorno...")
            
            # Grupo 1: Pedro y Rosa, lider: María
            pgr1 = persona_grupo_retorno(pe_codigo=personas[0].pe_codigo, gr_codigo=grupos[0].gr_codigo)
            db.add(pgr1)
            
            pgr2 = persona_grupo_retorno(pe_codigo=personas[1].pe_codigo, gr_codigo=grupos[0].gr_codigo)
            db.add(pgr2)
            
            # Grupo 2: Roberto y Laura, lider: Ana
            pgr3 = persona_grupo_retorno(pe_codigo=personas[2].pe_codigo, gr_codigo=grupos[1].gr_codigo)
            db.add(pgr3)
            
            pgr4 = persona_grupo_retorno(pe_codigo=personas[3].pe_codigo, gr_codigo=grupos[1].gr_codigo)
            db.add(pgr4)
            
            await db.flush()
            logger.info("✓ Personas asociadas a grupos de retorno")

            # ═════════════════════════════════════════
            # 8. CREAR INSCRIPCIONES INDIVIDUALES
            # ═════════════════════════════════════════
            logger.info("Creando inscripciones individuales...")
            
            inscripciones = []
            # Juan se inscribe
            reg1 = RegistroRetorno(
                usuario=usuarios[0].us_codigo,
                retorno=retorno.codigo,
                num_hospedaje=1,
                num_transporte=1,
                num_parqueadero_carro=1,
                num_parqueadero_moto=0,
                anotacion="Requiere transporte especial"
            )
            db.add(reg1)
            inscripciones.append(reg1)
            
            # Carlos se inscribe
            reg2 = RegistroRetorno(
                usuario=usuarios[2].us_codigo,
                retorno=retorno.codigo,
                num_hospedaje=1,
                num_transporte=1,
                num_parqueadero_carro=0,
                num_parqueadero_moto=1,
                anotacion="Trae moto"
            )
            db.add(reg2)
            inscripciones.append(reg2)
            
            # Luis se inscribe
            reg3 = RegistroRetorno(
                usuario=usuarios[4].us_codigo,
                retorno=retorno.codigo,
                num_hospedaje=1,
                num_transporte=0,
                num_parqueadero_carro=1,
                num_parqueadero_moto=0,
            )
            db.add(reg3)
            inscripciones.append(reg3)

            # Diana se inscribe
            reg4 = RegistroRetorno(
                usuario=usuarios[5].us_codigo,
                retorno=retorno.codigo,
                num_hospedaje=1,
                num_transporte=0,
                num_parqueadero_carro=1,
                num_parqueadero_moto=0,
            )
            db.add(reg4)
            inscripciones.append(reg4)
            await db.flush()
            logger.info(f"✓ {len(inscripciones)} inscripciones individuales creadas")

            # ═════════════════════════════════════════
            # 9. CREAR INSCRIPCIONES GRUPALES
            # ═════════════════════════════════════════
            logger.info("Creando inscripciones grupales...")
            
            inscripciones_grupales = []
            # Grupo 1 se inscribe
            reg_grupo1 = RegistroRetornoGrupo(
                cod_grupo=grupos[0].gr_codigo,
                retorno=retorno.codigo,
                num_hospedaje=2,
                num_transporte=2,
                num_parqueadero_carro=1,
                num_parqueadero_moto=0,
                anotacion="Grupo de Medellín"
            )
            db.add(reg_grupo1)
            inscripciones_grupales.append(reg_grupo1)
            
            # Grupo 2 se inscribe
            reg_grupo2 = RegistroRetornoGrupo(
                cod_grupo=grupos[1].gr_codigo,
                retorno=retorno.codigo,
                num_hospedaje=2,
                num_transporte=1,
                num_parqueadero_carro=1,
                num_parqueadero_moto=1,
                anotacion="Grupo de Cali"
            )
            db.add(reg_grupo2)
            inscripciones_grupales.append(reg_grupo2)
            
            await db.flush()
            logger.info(f"✓ {len(inscripciones_grupales)} inscripciones grupales creadas")

            # Confirmar transacción
            await db.commit()
            logger.info("════════════════════════════════════════")
            logger.info("✓ Seed de datos completado exitosamente")
            logger.info("════════════════════════════════════════")
            logger.info(f"  • Colonias: {len(colonias)}")
            logger.info(f"  • Usuarios: {len(usuarios)}")
            logger.info(f"  • Retornos: 1")
            logger.info(f"  • Grupos de retorno: {len(grupos)}")
            logger.info(f"  • Personas: {len(personas)}")
            logger.info(f"  • Inscripciones individuales: {len(inscripciones)}")
            logger.info(f"  • Inscripciones grupales: {len(inscripciones_grupales)}")
            logger.info("════════════════════════════════════════")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error durante el seed de datos: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
