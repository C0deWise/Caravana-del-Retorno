"""
    init_db.py es un script independiente para crear las tablas en la base de datos.
    Se importa cada modelo para asegurarse de que estén registrados en Base.metadata, y luego se llama a create_tables().
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar todos los modelos para registrarlos en Base.metadata
from app.colonias.models.colonia_model import Colonia
from app.usuarios.models.usuario import Rol
from app.usuarios.models.usuario import Usuario
from app.usuarios.models.parentesco import Parentesco

from app.core.database import create_tables
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Creando tablas: %s", list(__import__('app.core.database', fromlist=['Base']).Base.metadata.tables.keys()))
    asyncio.run(create_tables())