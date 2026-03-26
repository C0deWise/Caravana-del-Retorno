import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar todos los modelos para registrarlos en Base.metadata
from app.colonias.models.colonia_model import Colonia
from app.usuarios.models.usuario import Rol
from app.usuarios.models.usuario import Usuario

from app.core.database import create_tables
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Creando tablas: %s", list(__import__('app.core.database', fromlist=['Base']).Base.metadata.tables.keys()))
    create_tables()