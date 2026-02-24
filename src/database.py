import sqlite3
import json
import os
import hashlib
import time

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'watchbot.db')

CACHE_TTL_SECONDS = 12 * 60 * 60  # 12 hours

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn

def _init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prefs (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watched (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT,
            media_type TEXT,
            flagged_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_cache (
            cache_key       TEXT PRIMARY KEY,
            pool            TEXT NOT NULL,          -- JSON array of enriched result cards remaining
            tmdb_pages_movie TEXT NOT NULL,         -- JSON array of TMDB movie page numbers still to process
            tmdb_pages_tv   TEXT NOT NULL,          -- JSON array of TMDB tv page numbers still to process
            exhausted       INTEGER DEFAULT 0,      -- 1 when all TMDB pages have been consumed
            created_at      INTEGER NOT NULL        -- unix timestamp for TTL
        )
    ''')
    conn.commit()

def get_prefs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM prefs")
    rows = cursor.fetchall()
    prefs = {}
    for row in rows:
        try:
            prefs[row['key']] = json.loads(row['value'])
        except Exception:
            prefs[row['key']] = row['value']
    return prefs

def get_watched_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT tmdb_id FROM watched")
    return set(row['tmdb_id'] for row in cursor.fetchall())

def make_cache_key(seed: int, media_type: str, prefs: dict) -> str:
    """
    Generate a stable cache key from search parameters.
    Any change to seed, media_type, or prefs (genres, platforms, language,
    region, rt_min_score, min_year, include_watched) produces a different key.
    """
    relevant = {
        'seed': seed,
        'media_type': media_type,
        'genres': sorted(prefs.get('genres', [])),
        'platforms': sorted(prefs.get('platforms', [])),
        'language': prefs.get('language', 'en-US'),
        'region': prefs.get('region', 'US'),
        'rt_min_score': prefs.get('rt_min_score', 70),
        'min_year': prefs.get('min_year'),
        'include_watched': prefs.get('include_watched', False),
    }
    raw = json.dumps(relevant, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()

def load_cache(conn, cache_key: str):
    """
    Load a valid (non-expired) cache entry. Returns None if missing or expired.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_cache WHERE cache_key = ?", (cache_key,))
    row = cursor.fetchone()
    if row is None:
        return None
    age = time.time() - row['created_at']
    if age > CACHE_TTL_SECONDS:
        cursor.execute("DELETE FROM search_cache WHERE cache_key = ?", (cache_key,))
        conn.commit()
        return None
    return {
        'pool': json.loads(row['pool']),
        'tmdb_pages_movie': json.loads(row['tmdb_pages_movie']),
        'tmdb_pages_tv': json.loads(row['tmdb_pages_tv']),
        'exhausted': bool(row['exhausted']),
        'created_at': row['created_at'],
    }

def save_cache(conn, cache_key: str, pool: list, tmdb_pages_movie: list,
               tmdb_pages_tv: list, exhausted: bool, created_at: int = None):
    """
    Insert or update a cache entry.
    """
    if created_at is None:
        created_at = int(time.time())
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO search_cache
            (cache_key, pool, tmdb_pages_movie, tmdb_pages_tv, exhausted, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        cache_key,
        json.dumps(pool, ensure_ascii=False),
        json.dumps(tmdb_pages_movie),
        json.dumps(tmdb_pages_tv),
        1 if exhausted else 0,
        created_at,
    ))
    conn.commit()
