import pytest
from fastapi import HTTPException
from app.utils import riot_get
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_riot_get_expired_key():
    # 1. Arrange: Simulating aiohttp.ClientSession behavior
    mock_response = AsyncMock()
    mock_response.status = 403
    
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    
    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager
    
    # 2 & 3. Act and Assert: Verifying if the function raises the correct HTTPException
    with pytest.raises(HTTPException) as erro:
        await riot_get(mock_session, "https://api-falsa.riotgames.com")
        
    assert erro.value.status_code == 403
    assert erro.value.detail == "API Key expired or no permission"

@pytest.mark.asyncio
async def test_riot_get_success():
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": "123", "name": "Fake Player"}
    
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    
    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager
    
    # Act
    resultado = await riot_get(mock_session, "https://api.riotgames.com/sucesso")
    
    # Assert
    assert resultado == {"id": "123", "name": "Fake Player"}
