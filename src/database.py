import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'watchbot.db')

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
    conn.commit()

def get_prefs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM prefs")
    rows = cursor.fetchall()
    prefs = {}
    for row in rows:
        try:
            prefs[row['key']] = json.loads(row['value'])
        except:
            prefs[row['key']] = row['value']
    return prefs

def get_watched_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT tmdb_id FROM watched")
    return set(row['tmdb_id'] for row in cursor.fetchall())
