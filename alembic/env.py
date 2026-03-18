import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Carga el .env
load_dotenv()

# Importa tu Base
from app.core.database import Base
from app import models

config = context.config

load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Resto de la configuración...
target_metadata = Base.metadata