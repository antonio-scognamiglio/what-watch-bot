import pytest
from unittest.mock import Mock
import requests
from src.api.omdb import get_omdb_ratings, fetch_omdb_plot
from src.api.wikipedia import fetch_wikipedia_plot
from src.config import Config

@pytest.fixture(autouse=True)
def mock_keys(monkeypatch):
    """Ensure API keys are set for tests otherwise they skip execution."""
    monkeypatch.setattr(Config, 'OMDB_API_KEY', 'fake_key')

# --- OMDB TESTS ---

def test_get_omdb_ratings_success(mocker):
    """Test standard OMDB JSON parsing for valid movie."""
    mock_get = mocker.patch('requests.get')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Response": "True",
        "Ratings": [
            {"Source": "Rotten Tomatoes", "Value": "85%"},
            {"Source": "Internet Movie Database", "Value": "8.0/10"},
            {"Source": "Metacritic", "Value": "80/100"}
        ]
    }
    mock_get.return_value = mock_response

    ratings = get_omdb_ratings("The Matrix", "1999")
    
    assert ratings['tomatometer'] == 85
    assert ratings['imdb'] == 8.0
    assert ratings['metacritic'] == 80


def test_get_omdb_ratings_not_found(mocker):
    """Test OMDB gracefully returning empty dict when movie is not found."""
    mock_get = mocker.patch('requests.get')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Response": "False",
        "Error": "Movie not found!"
    }
    mock_get.return_value = mock_response

    ratings = get_omdb_ratings("Non Existent Movie Hash 123", "2025")
    assert ratings == {}


def test_fetch_omdb_plot_success(mocker):
    """Test fetching full OMDB plot."""
    mock_get = mocker.patch('requests.get')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Response": "True",
        "Plot": "A computer hacker learns from mysterious rebels about the true nature of his reality."
    }
    mock_get.return_value = mock_response

    plot = fetch_omdb_plot("The Matrix")
    assert "computer hacker" in plot


def test_fetch_omdb_plot_na(mocker):
    """Test when OMDB returns N/A for the plot."""
    mock_get = mocker.patch('requests.get')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Response": "True",
        "Plot": "N/A"
    }
    mock_get.return_value = mock_response

    plot = fetch_omdb_plot("Unknown Indie Movie")
    assert plot is None


# --- WIKIPEDIA TESTS ---

def test_fetch_wikipedia_plot_success(mocker):
    """Test standard Wikipedia search loop."""
    mock_get = mocker.patch('requests.get')
    
    # Needs two API calls: one for search, one for extract
    search_response = Mock()
    search_response.status_code = 200
    search_response.json.return_value = {
        "query": {"search": [{"title": "The Matrix (film)"}]}
    }
    
    extract_response = Mock()
    extract_response.status_code = 200
    extract_response.json.return_value = {
        "query": {
            "pages": {
                "123": {"extract": "The Matrix is a 1999 science fiction action film..."}
            }
        }
    }
    
    mock_get.side_effect = [search_response, extract_response]

    plot = fetch_wikipedia_plot("The Matrix (1999)", lang="en")
    
    assert "science fiction" in plot
    assert mock_get.call_count == 2


def test_fetch_wikipedia_plot_broad_fallback(mocker):
    """Test strict search failure falling back to broad search."""
    mock_get = mocker.patch('requests.get')
    
    # 1. Strict search fails
    strict_response = Mock()
    strict_response.status_code = 200
    strict_response.json.return_value = {"query": {"search": []}}
    
    # 2. Broad search succeeds
    broad_response = Mock()
    broad_response.status_code = 200
    broad_response.json.return_value = {
        "query": {"search": [{"title": "Matrix"}]}
    }
    
    # 3. Extract succeeds
    extract_response = Mock()
    extract_response.status_code = 200
    extract_response.json.return_value = {
        "query": {
            "pages": {
                "1": {"extract": "Matrix broad plot"}
            }
        }
    }
    
    mock_get.side_effect = [strict_response, broad_response, extract_response]

    plot = fetch_wikipedia_plot("Some Exact Long Title That Fails", lang="it")
    
    assert plot == "Matrix broad plot"
    assert mock_get.call_count == 3


def test_fetch_wikipedia_plot_not_found(mocker):
    """Test when Wikipedia finds totally nothing on both searches."""
    mock_get = mocker.patch('requests.get')
    
    fail_response = Mock()
    fail_response.status_code = 200
    fail_response.json.return_value = {"query": {"search": []}}
    
    # Both strict and broad return empty
    mock_get.side_effect = [fail_response, fail_response]

    plot = fetch_wikipedia_plot("Asdfqwertyuiop Movie")
    
    assert plot is None
    assert mock_get.call_count == 2
