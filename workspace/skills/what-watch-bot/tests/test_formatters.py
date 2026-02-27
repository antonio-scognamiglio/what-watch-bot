import pytest
from src.utils.formatters import build_media_card
from src.config import GENRE_MAPPING

@pytest.fixture
def base_tmdb_item():
    return {
        'id': 123,
        'media_type': 'movie',
        'title': 'Test Movie',
        'release_date': '2023-05-15',
        'overview': 'Basic overview',
        'genre_ids': [28, 12], # Action, Adventure
        'poster_path': '/basic.jpg',
        'vote_average': 8.5,
        'is_watched': True
    }

@pytest.fixture
def mock_dependencies(mocker):
    mocker.patch('src.utils.formatters.get_youtube_trailer', return_value="https://youtube.com/trailer")
    mocker.patch('src.utils.formatters.get_tmdb_details', return_value={
        'overview': 'Detailed overview',
        'poster_path': '/detailed.jpg',
        'credits': {
            'cast': [{'name': 'Actor 1'}, {'name': 'Actor 2'}],
            'crew': [{'name': 'Director 1', 'job': 'Director'}]
        }
    })
    mocker.patch('src.utils.formatters.get_watch_providers', return_value=[{'name': 'netflix', 'tier': 'subscription'}])

def test_build_media_card_movie(base_tmdb_item, mock_dependencies):
    # GENRE_MAPPING contains {28: 'Action', 12: 'Adventure'}
    # Let's assume the user likes Action (28)
    card = build_media_card(base_tmdb_item, user_genre_ids=[28])
    
    assert card['id'] == 123
    assert card['type'] == 'movie'
    assert card['title'] == 'Test Movie'
    assert card['year'] == '2023'
    # Should prefer detailed overview
    assert card['overview'] == 'Detailed overview'
    assert 'Action' in card['genres']
    assert 'Adventure' in card['genres']
    assert card['matched_genres'] == ['Action']
    assert card['directors'] == ['Director 1']
    assert card['cast'] == ['Actor 1', 'Actor 2']
    assert card['ratings']['tmdb'] == 8.5
    assert card['platforms'][0]['name'] == 'netflix'
    assert card['trailer_url'] == "https://youtube.com/trailer"
    assert card['is_watched'] is True
    # The code prefers item.get('poster_path') over details.get('poster_path')
    assert card['poster_url'] == "https://image.tmdb.org/t/p/w500/basic.jpg"

def test_build_media_card_series(mocker):
    item = {
        'id': 456,
        'media_type': 'tv',
        'name': 'Test Series', # TV shows use 'name' instead of 'title'
        'first_air_date': '2021-09-01',
        'vote_average': 7.1
    }
    
    mocker.patch('src.utils.formatters.get_youtube_trailer', return_value=None)
    mocker.patch('src.utils.formatters.get_tmdb_details', return_value={
        'credits': {
            # TV shows use 'department': 'Directing' instead of 'job': 'Director'
            'crew': [{'name': 'Showrunner 1', 'department': 'Directing'}]
        }
    })
    mocker.patch('src.utils.formatters.get_watch_providers', return_value=[])
    
    card = build_media_card(item)
    
    assert card['title'] == 'Test Series'
    assert card['year'] == '2021'
    assert card['directors'] == ['Showrunner 1']
    assert card['trailer_url'] is None

def test_build_media_card_injected_ratings(base_tmdb_item, mock_dependencies):
    omdb_data = {
        'tomatometer': '90%',
        'imdb': '8.8',
        'metacritic': '82/100'
    }
    tmdb_custom_rating = 9.0
    
    card = build_media_card(base_tmdb_item, omdb_ratings=omdb_data, tmdb_rating=tmdb_custom_rating)
    
    assert card['ratings']['tomatometer'] == '90%'
    assert card['ratings']['imdb'] == '8.8'
    assert card['ratings']['metacritic'] == '82/100'
    assert card['ratings']['tmdb'] == 9.0

def test_build_media_card_no_details_fallback(base_tmdb_item, mocker):
    mocker.patch('src.utils.formatters.get_youtube_trailer', return_value=None)
    # Simulate TMDB details failing (returning None or empty dict)
    mocker.patch('src.utils.formatters.get_tmdb_details', return_value={})
    mocker.patch('src.utils.formatters.get_watch_providers', return_value=[])
    
    card = build_media_card(base_tmdb_item)
    
    # Should fallback to basic overview and poster
    assert card['overview'] == 'Basic overview'
    assert card['poster_url'] == "https://image.tmdb.org/t/p/w500/basic.jpg"
    assert card['cast'] == []
    assert card['directors'] == []

def test_build_media_card_english_overview_fallback(mocker):
    """Test that an empty localized overview triggers a second TMDB call in English."""
    item_no_overview = {
        'id': 999,
        'media_type': 'movie',
        'title': 'Unseen',
        'release_date': '2023-01-01',
        'overview': '',  # empty — simulates obscure film with no Italian translation
        'genre_ids': [],
        'vote_average': 6.6
    }
    mocker.patch('src.utils.formatters.get_youtube_trailer', return_value=None)
    mocker.patch('src.utils.formatters.get_watch_providers', return_value=[])

    mock_details = mocker.patch('src.utils.formatters.get_tmdb_details')
    mock_details.side_effect = [
        {'overview': '', 'credits': {'cast': [], 'crew': []}},        # it-IT: no translation
        {'overview': 'English fallback overview', 'credits': {}},      # en-US: has plot
    ]

    card = build_media_card(item_no_overview, language='it-IT')

    assert card['overview'] == 'English fallback overview'
    assert mock_details.call_count == 2
