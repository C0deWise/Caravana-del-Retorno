import sys
import os
import pytest

# Agregamos el directorio raíz del proyecto al sys.path para permitir importaciones absolutas
# como 'from app.core...'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Fixture para asegurar que las variables de entorno críticas existan durante los tests.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
    monkeypatch.setenv("SECRET_KEY", "testingsecret")
    monkeypatch.setenv("DEBUG", "True")