"""Tests for URL checking functionality."""
import pytest
from unittest.mock import patch, Mock
import httpx
from src.checker import URLChecker

@pytest.fixture
def checker():
    """Create a URL checker instance."""
    return URLChecker()

@pytest.mark.asyncio
async def test_check_valid_url(checker):
    """Test checking a valid URL."""
    with patch('httpx.AsyncClient.head') as mock_head:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_head.return_value = mock_response

        result = await checker.check_url("https://example.com")
        assert result.is_alive is True
        assert result.status_code == 200
        assert result.error is None

@pytest.mark.asyncio
async def test_check_invalid_url(checker):
    """Test checking an invalid URL."""
    result = await checker.check_url("not-a-valid-url")
    assert result.is_alive is False
    assert result.error is not None

@pytest.mark.asyncio
async def test_check_dead_url(checker):
    """Test checking a dead URL."""
    with patch('httpx.AsyncClient.head') as mock_head:
        mock_head.side_effect = httpx.ConnectError("Connection failed")
        
        result = await checker.check_url("https://nonexistent.example.com")
        assert result.is_alive is False
        assert result.error is not None

@pytest.mark.asyncio
async def test_check_redirect(checker):
    """Test URL redirection."""
    with patch('httpx.AsyncClient.head') as mock_head, \
         patch('httpx.AsyncClient.get') as mock_get:

        # First response - redirect
        mock_response1 = Mock()
        mock_response1.status_code = 301
        mock_response1.headers = {"location": "https://new.example.com"}
        mock_response1.url = "https://old.example.com"
        mock_head.return_value = mock_response1
        
        # Second response - final destination
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.url = "https://new.example.com"
        mock_get.return_value = mock_response2

        result = await checker.check_url("https://old.example.com")
        assert result.status_code == 200
        assert result.final_url == "https://new.example.com"