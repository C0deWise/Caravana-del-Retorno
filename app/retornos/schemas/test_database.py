import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError
from app.core.database import check_db_connection

@patch("app.core.database.engine")
def test_check_db_connection_success(mock_engine):
    """
    Prueba que check_db_connection retorna True cuando la conexión es exitosa.
    Simulamos que engine.connect() retorna una conexión válida.
    """
    # Configuramos el mock para el contexto 'with engine.connect() as conn:'
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    
    # Ejecutamos la función
    result = check_db_connection()
    
    # Verificaciones
    assert result is True
    mock_connection.execute.assert_called_once()

@patch("app.core.database.engine")
def test_check_db_connection_failure(mock_engine):
    """
    Prueba que check_db_connection retorna False cuando ocurre un OperationalError.
    """
    # Configuramos el mock para que lance una excepción al conectar
    mock_engine.connect.side_effect = OperationalError("Connection refused", params=None, orig=Exception())
    
    result = check_db_connection()
    
    assert result is False