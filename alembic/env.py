import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.core.database import Base
# Aqui importas tus modelos para que Alembic pueda detectarlos
# from app.models import Usuario, Colonia, Rol etc...

# Importación de modelos para que Alembic los detecte
from app.usuarios.models.usuario import Rol
from app.usuarios.models.parentesco import Parentesco
from app.colonias.models.colonia_model import Colonia
from app.colonias.models.solicitud_colonia import SolicitudColonia
from app.retornos.modelos.retorno_modelo import Retorno
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.usuarios.models.usuario import Usuario, Rol
from app.usuarios.models.parentesco import Parentesco
from app.multimedia.modelos.multimedia_modelo import Multimedia
from app.retornos.modelos.grupo_retorno_modelo import GrupoRetorno
from app.retornos.modelos.persona_modelo import Persona
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.retorno_grupo_usuario_modelo import RetornoGrupoUsuario
from app.retornos.modelos.solicitud_grupo_retorno_modelo import SolicitudGrupoRetorno
from app.retornos.modelos.persona_grupo_retorno_modelo import persona_grupo_retorno
from app.publicacion.modelos.publicacion_modelo import Publicacion

# Verificar que los modelos se cargan correctamente
print("Modelos detectados:", list(Base.metadata.tables.keys()))
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
    
print("USANDO DB:", os.getenv("DATABASE_URL"))