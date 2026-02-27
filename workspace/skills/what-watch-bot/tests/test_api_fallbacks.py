import pytest
from unittest.mock import Mock
import requests
from src.api.omdb import get_omdb_ratings, fetch_omdb_plot
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
