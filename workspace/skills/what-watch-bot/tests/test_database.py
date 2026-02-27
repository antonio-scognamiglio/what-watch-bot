import pytest
import json
import time
from src.database import get_prefs, get_watched_ids, make_cache_key, load_cache, save_cache, CACHE_TTL_SECONDS

def test_make_cache_key_is_deterministic():
    """Property: Same inputs yield identical hash keys."""
    prefs1 = {'genres': ['Action', 'Comedy'], 'language': 'it-IT'}
    prefs2 = {'language': 'it-IT', 'genres': ['Comedy', 'Action']} # order reversed

    key1 = make_cache_key(1234, 'movie', prefs1)
    key2 = make_cache_key(1234, 'movie', prefs2)

    assert key1 == key2

def test_make_cache_key_differs_on_input_change():
    """Property: Changing seed or media_type changes hash."""
    prefs = {}
    key1 = make_cache_key(1111, 'movie', prefs)
    key2 = make_cache_key(2222, 'movie', prefs)
    key3 = make_cache_key(1111, 'tv', prefs)

    assert key1 != key2
    assert key1 != key3

def test_get_prefs_empty_db(mock_db):
    """Test getting preferences when table is empty."""
    prefs = get_prefs(mock_db)
    assert prefs == {}

def test_get_prefs_with_data(mock_db):
    """Test retrieving parsed JSON and raw text preferences."""
    mock_db.execute("INSERT INTO prefs (key, value) VALUES ('language', 'en-US')")
    mock_db.execute("INSERT INTO prefs (key, value) VALUES ('genres', '[\"Action\"]')")
    mock_db.commit()

    prefs = get_prefs(mock_db)
    assert prefs['language'] == 'en-US'
    assert prefs['genres'] == ['Action']

def test_get_watched_ids(mock_db):
    """Test retrieving watched list."""
    mock_db.execute("INSERT INTO watched (tmdb_id, title) VALUES (123, 'Matrix')")
    mock_db.execute("INSERT INTO watched (tmdb_id, title) VALUES (456, 'Avatar')")
    mock_db.commit()

    watched = get_watched_ids(mock_db)
    assert watched == {123, 456}

def test_save_and_load_cache(mock_db):
    """Test standard cache I/O pipeline."""
    cache_key = "test_key_123"
    pool = [{"id": 1, "title": "Test"}]
    tmdb_movie = [2, 3]
    tmdb_tv = [1]

    # Save
    save_cache(mock_db, cache_key, pool, tmdb_movie, tmdb_tv, False)

    # Load
    cached = load_cache(mock_db, cache_key)
    assert cached is not None
    assert cached['pool'] == pool
    assert cached['tmdb_pages_movie'] == tmdb_movie
    assert cached['tmdb_pages_tv'] == tmdb_tv
    assert cached['exhausted'] is False

def test_load_cache_miss(mock_db):
    """Test missing cache returns None."""
    assert load_cache(mock_db, "missing_key") is None

def test_load_cache_expired(mock_db):
    """Test that expired cache returns None and deletes the row (Pattern 8 logic)."""
    cache_key = "expired_key"
    expired_time = int(time.time()) - CACHE_TTL_SECONDS - 10

    # Insert expired data
    save_cache(mock_db, cache_key, [], [], [], True, created_at=expired_time)

    # Try to load
    cached = load_cache(mock_db, cache_key)

    # Assert
    assert cached is None
    # Verify it was deleted (side effect check)
    cursor = mock_db.cursor()
    cursor.execute("SELECT * FROM search_cache WHERE cache_key = ?", (cache_key,))
    assert cursor.fetchone() is None
