"""Tests for LinkAce API integration and notifications."""
import pytest
from unittest.mock import patch, Mock
import json
from src.services.linkace_client import LinkAceClient
from src.services.notification_service import NotificationService

@pytest.fixture
def api_client():
    """Create a LinkAce API client."""
    return LinkAceClient(
        base_url="http://test.example.com",
        api_key="test_token"
    )

@pytest.fixture
def notification_service():
    """Create a notification service."""
    return NotificationService(
        topic_arn="arn:aws:sns:us-east-1:123456789012:test-topic",
        aws_region="us-east-1"
    )

# API Integration Tests
@pytest.mark.asyncio
async def test_list_links(api_client):
    """Test listing links from LinkAce."""
    mock_response = {
        "data": [
            {"id": 1, "url": "https://example1.com", "title": "Test 1"},
            {"id": 2, "url": "https://example2.com", "title": "Test 2"}
        ]
    }

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: mock_response
        )
        response = await api_client.list_bookmarks(page=1)
        links = response["data"]
        assert len(links) == 2
        assert links[0]["url"] == "https://example1.com"

@pytest.mark.asyncio
async def test_update_link(api_client):
    """Test updating a link in LinkAce."""
    link_id = 1
    update_data = {
        "status": 0,
        "tags": ["dead", "unreachable"]
    }

    with patch('httpx.AsyncClient.get') as mock_get, \
         patch('httpx.AsyncClient.put') as mock_put:
        # Mock the GET response for current link state
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "url": "https://example.com",
                "title": "Test Link",
                "tags": ["test"],
                "check_disabled": False,
                "status": 1
            }
        )
        # Mock the PUT response for update
        mock_put.return_value = Mock(
            status_code=200,
            json=lambda: {"data": {"id": link_id}}
        )
        
        # Should not raise any exceptions
        await api_client.update_link(link_id=link_id, **update_data)
        
        # Verify both calls happened
        mock_get.assert_called_once()
        mock_put.assert_called_once()

# Notification Tests
@pytest.mark.asyncio
async def test_notify_dead_link(notification_service):
    """Test dead link notification."""
    link_data = {
        "id": 1,
        "url": "https://example.com",
        "title": "Test Link"
    }
    
    check_result = {
        "status": 0,
        "error": "Connection failed",
        "status_code": None
    }

    with patch.object(notification_service, 'sns') as mock_sns:
        mock_sns.publish = Mock(return_value={"MessageId": "test123"})
        
        await notification_service.notify_dead_link(link_data, check_result)
        
        mock_sns.publish.assert_called_once()
        call_args = mock_sns.publish.call_args[1]
        assert 'Message' in call_args
        assert 'Subject' in call_args