import pytest
import requests
from src.api.tmdb import (
    get_tmdb_total_pages,
    search_tmdb,
    get_tmdb_details,
    search_tmdb_by_title,
    get_watch_providers
)

@pytest.fixture
def mock_tmdb_config(mocker):
    mocker.patch('src.api.tmdb.Config.TMDB_API_KEY', 'dummy_tmdb_key')

def test_get_tmdb_total_pages_success(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'total_pages': 15}
    
    pages = get_tmdb_total_pages('movie', genres=[28], providers=[8], min_year=2020)
    
    assert pages == 15
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert kwargs['params']['with_genres'] == '28'
    assert kwargs['params']['primary_release_date.gte'] == '2020-01-01'

def test_search_tmdb_success(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'results': [{'id': 1, 'title': 'Test Movie'}]
    }
    
    results = search_tmdb('movie', genres=[28], providers=[8], page=2)
    
    assert len(results) == 1
    assert results[0]['id'] == 1
    mock_get.assert_called_once()
    assert mock_get.call_args[1]['params']['page'] == 2

def test_search_tmdb_series_min_year(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'results': []}
    
    search_tmdb('tv', genres=[], providers=[], min_year=2015)
    
    assert mock_get.call_args[1]['params']['first_air_date.gte'] == '2015-01-01'

def test_get_tmdb_details_success(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'id': 123, 'title': 'Test'}
    
    details = get_tmdb_details(123, 'movie')
    
    assert details == {'id': 123, 'title': 'Test'}

def test_get_tmdb_details_failure(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 404
    
    assert get_tmdb_details(999, 'movie') is None

def test_search_tmdb_by_title_success(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'results': [{'id': 1}]}
    
    results = search_tmdb_by_title("Matrix")
    
    assert len(results) == 1
    assert results[0]['id'] == 1

def test_get_watch_providers_success(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'results': {
            'US': {
                'flatrate': [{'provider_name': 'Netflix'}],
                'free': [{'provider_name': 'Pluto TV'}],
                'ads': [{'provider_name': 'Tubi TV'}]
            }
        }
    }
    
    providers = get_watch_providers(123, 'movie', 'Matrix', region='US')
    
    assert len(providers) == 3
    assert providers[0]['name'] == 'Netflix'
    assert providers[0]['tier'] == 'subscription'
    assert providers[1]['name'] == 'Pluto TV'
    assert providers[1]['tier'] == 'free'
    assert providers[2]['name'] == 'Tubi TV'
    assert providers[2]['tier'] == 'ads'

def test_get_watch_providers_deduplication(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 200
    # Provide the same provider across different tiers to test set deduplication
    mock_get.return_value.json.return_value = {
        'results': {
            'US': {
                'flatrate': [{'provider_name': 'Hulu'}],
                'ads': [{'provider_name': 'Hulu'}]
            }
        }
    }
    
    providers = get_watch_providers(123, 'movie', 'Matrix', region='US')
    
    assert len(providers) == 1
    assert providers[0]['name'] == 'Hulu'
    assert providers[0]['tier'] == 'subscription' # Flatrate gets processed first

def test_get_watch_providers_failure(mocker, mock_tmdb_config):
    mock_get = mocker.patch('src.api.tmdb.requests.get')
    mock_get.return_value.status_code = 404
    
    assert get_watch_providers(999, 'movie', 'Test') == []
