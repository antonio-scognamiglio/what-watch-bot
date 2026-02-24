import pytest
from unittest.mock import MagicMock
from src.utils.pagination import fetch_page_from_cache, _build_page_lists, _fetch_and_filter
from src.database import make_cache_key

@pytest.fixture
def mock_omdb_ratings(mocker):
    """Fixture to universally mock OMDb ratings so they always pass the threshold."""
    return mocker.patch(
        'src.utils.pagination.get_omdb_ratings',
        return_value={'tomatometer': 85, 'imdb': 8.0, 'metacritic': 80}
    )

def test_cache_miss_triggers_api_calls(mock_db, mocker, mock_omdb_ratings):
    """
    Test scenario: Cache is empty (MISS).
    Expectation: The paginator should call TMDB to find total pages, fetch results, and save them.
    """
    # Arrange
    mocker.patch('src.utils.pagination.get_tmdb_total_pages', side_effect=[5, 3]) # movie=5, tv=3 pages
    
    mock_search = mocker.patch('src.utils.pagination.search_tmdb')
    # Let TMDB return 3 items on the first page fetch
    mock_search.return_value = [
        {'id': 101, 'title': 'Movie 1', 'vote_average': 8.0, 'release_date': '2023-01-01'},
        {'id': 102, 'title': 'Movie 2', 'vote_average': 6.0, 'release_date': '2022-01-01'},
        {'id': 103, 'title': 'Movie 3', 'vote_average': 7.5, 'release_date': '2021-01-01'},
    ]

    cache_key = 'test_miss_key'
    
    # Act
    results = fetch_page_from_cache(
        conn=mock_db,
        cache_key=cache_key,
        items_per_page=2,
        seed=42,
        media_type_pref='movie',
        genres=[],
        platforms=[],
        min_year=None,
        watched_ids=set(),
        include_watched=False,
        language='en-US',
        region='US',
        rt_min_score=70
    )

    # Assert
    assert len(results) == 2
    assert results[0]['id'] in [101, 102, 103]
    assert results[1]['id'] in [101, 102, 103]
    
    # Verify the mock interactions
    mock_search.assert_called() # It should have hit the TMDB API

    # Check database side effects (remaining pool should be 1 item since 3 were returned and 2 requested)
    cursor = mock_db.cursor()
    cursor.execute("SELECT pool, exhausted FROM search_cache WHERE cache_key = ?", (cache_key,))
    row = cursor.fetchone()
    assert row is not None
    import json
    saved_pool = json.loads(row['pool'])
    assert len(saved_pool) == 1
    assert row['exhausted'] == 0


def test_cache_hit_bypasses_api_calls(mock_db, mocker, mock_omdb_ratings):
    """
    Test scenario: Cache already contains sufficient items (HIT).
    Expectation: API should NOT be called, results should be served directly from the DB pool.
    """
    # Arrange
    from src.database import save_cache
    cache_key = 'test_hit_key'
    initial_pool = [
        {'id': 201, 'title': 'Cached 1'},
        {'id': 202, 'title': 'Cached 2'},
        {'id': 203, 'title': 'Cached 3'}
    ]
    # Pre-seed the cache
    save_cache(mock_db, cache_key, initial_pool, tmdb_pages_movie=[], tmdb_pages_tv=[], exhausted=False)

    mock_search = mocker.patch('src.utils.pagination.search_tmdb')
    mock_total_pages = mocker.patch('src.utils.pagination.get_tmdb_total_pages')

    # Act
    results = fetch_page_from_cache(
        conn=mock_db,
        cache_key=cache_key,
        items_per_page=2,
        seed=123,
        media_type_pref='both',
        genres=[],
        platforms=[],
        min_year=None,
        watched_ids=set(),
        include_watched=False,
        language='en-US',
        region='US',
        rt_min_score=70
    )

    # Assert
    assert len(results) == 2
    assert results[0]['id'] == 201 # Cache pops front-to-back deterministically
    assert results[1]['id'] == 202

    # CRITICAL: Confirm APIs were completely bypassed
    mock_search.assert_not_called()
    mock_total_pages.assert_not_called()

    # Confirm cache was updated
    cursor = mock_db.cursor()
    cursor.execute("SELECT pool FROM search_cache WHERE cache_key = ?", (cache_key,))
    import json
    saved_pool = json.loads(cursor.fetchone()['pool'])
    assert len(saved_pool) == 1
    assert saved_pool[0]['id'] == 203


def test_watched_filtration(mock_db, mocker, mock_omdb_ratings):
    """
    Test scenario: Pool has a mix of watched and unwatched items.
    Expectation: Watched items should be skipped from rendering into the final pool.
    """
    mocker.patch('src.utils.pagination.get_tmdb_total_pages', return_value=1)
    
    mock_search = mocker.patch('src.utils.pagination.search_tmdb')
    mock_search.return_value = [
        {'id': 500, 'title': 'Watched Movie', 'vote_average': 8.0, 'release_date': '2020-01-01'},
        {'id': 501, 'title': 'Unwatched Movie', 'vote_average': 8.0, 'release_date': '2020-01-01'},
    ]

    watched_ids = {500} # User has seen ID 500

    results = fetch_page_from_cache(
        conn=mock_db,
        cache_key='filter_key',
        items_per_page=2,
        seed=1,
        media_type_pref='movie',
        genres=[],
        platforms=[],
        min_year=None,
        watched_ids=watched_ids,
        include_watched=False, # Ensure it gets skipped
        language='en-US',
        region='US',
        rt_min_score=70
    )

    # Assert that only the unwatched movie made it through the pipeline
    assert len(results) == 1
    assert results[0]['id'] == 501
