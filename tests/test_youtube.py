import pytest
from src.api.youtube import get_youtube_trailer

@pytest.fixture
def mock_youtube_config(mocker):
    # Ensure a dummy API key is set so the function proceeds
    mocker.patch('src.api.youtube.Config.YOUTUBE_API_KEY', 'dummy_key')

def test_get_youtube_trailer_missing_key(mocker):
    mocker.patch('src.api.youtube.Config.YOUTUBE_API_KEY', None)
    assert get_youtube_trailer("Inception") is None

def test_get_youtube_trailer_success(mocker, mock_youtube_config):
    mock_get = mocker.patch('src.api.youtube.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'items': [{'id': {'videoId': 'dQw4w9WgXcQ'}}]
    }
    
    result = get_youtube_trailer("Inception")
    
    assert result == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "https://www.googleapis.com/youtube/v3/search" in args[0]
    assert kwargs['params']['q'] == "Inception official trailer"

def test_get_youtube_trailer_localization(mocker, mock_youtube_config):
    mock_get = mocker.patch('src.api.youtube.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'items': [{'id': {'videoId': 'ita_trailer_123'}}]
    }
    
    result = get_youtube_trailer("Inception", language="it-IT", region="IT")
    
    assert result == "https://www.youtube.com/watch?v=ita_trailer_123"
    args, kwargs = mock_get.call_args
    assert kwargs['params']['q'] == "Inception trailer ufficiale"
    assert kwargs['params']['relevanceLanguage'] == "it"
    assert kwargs['params']['regionCode'] == "IT"

def test_get_youtube_trailer_no_items(mocker, mock_youtube_config):
    mock_get = mocker.patch('src.api.youtube.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'items': []}
    
    assert get_youtube_trailer("NonExistentMovie123") is None

def test_get_youtube_trailer_http_error(mocker, mock_youtube_config):
    mock_get = mocker.patch('src.api.youtube.requests.get')
    mock_get.return_value.status_code = 403
    
    assert get_youtube_trailer("Inception") is None

def test_get_youtube_trailer_exception(mocker, mock_youtube_config):
    mock_get = mocker.patch('src.api.youtube.requests.get')
    mock_get.side_effect = Exception("Network Error")
    
    assert get_youtube_trailer("Inception") is None
