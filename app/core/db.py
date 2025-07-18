import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'music.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-style access
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        album TEXT,
        year INTEGER,
        genre TEXT,
        file_path TEXT UNIQUE,
        file_name TEXT,
        duration INTEGER,
        file_format TEXT,
        bitrate INTEGER,
        sample_rate INTEGER,
        channels TEXT,
        file_size INTEGER,
        created_at TEXT,
        updated_at TEXT
    )
    ''')

    # Future stubs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_songs (
        playlist_id INTEGER,
        song_id INTEGER,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id),
        FOREIGN KEY (song_id) REFERENCES songs(id)
    )
    ''')

    conn.commit()
    conn.close()
