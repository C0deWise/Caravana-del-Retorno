from unittest import AsyncMock, MagicMock
import sys
import os
import pytest

@pytest.fixture
def mock_repositorio():
    repositorio = MagicMock()
    repositorio.registrar_retorno = AsyncMock()
    return repositorio