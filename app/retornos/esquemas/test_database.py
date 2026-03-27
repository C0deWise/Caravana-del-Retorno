import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.exc import OperationalError
from app.core.database import check_db_connection

@pytest.mark.asyncio
@patch("app.core.database.engine")
async def test_check_db_connection_success(mock_engine):
    """
    Prueba que check_db_connection retorna True cuando la conexión es exitosa.
    Simulamos que engine.connect() retorna una conexión válida.
    """
    # Configuramos el mock para el contexto 'async with engine.connect() as conn:'
    mock_connection = AsyncMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_connection
    
    # Ejecutamos la función
    result = await check_db_connection()
    
    # Verificaciones
    assert result is True
    mock_connection.execute.assert_called_once()

@pytest.mark.asyncio
@patch("app.core.database.engine")
async def test_check_db_connection_failure(mock_engine):
    """
    Prueba que check_db_connection retorna False cuando ocurre un OperationalError.
    """
    # Configuramos el mock para que lance una excepción al conectar
    mock_engine.connect.side_effect = OperationalError("Connection refused", params=None, orig=Exception())
    
    result = await check_db_connection()
    
    assert result is False