import sqlite3
import os
from datetime import datetime
from abc import ABC, abstractmethod
from core.db import create_tables, get_connection

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'music.db')


def init_db():
    create_tables()

class BaseModel(ABC):
    """
    Abstract base class for all models using raw SQLite.
    Provides basic save() and delete() methods.
    """

    created_at: str
    updated_at: str

    def __init__(self):
        now = datetime.now().isoformat()
        self.created_at = now
        self.updated_at = now

    @abstractmethod
    def _insert_query(self) -> tuple[str, tuple]:
        """Returns a (SQL string, parameters) tuple for insertion"""
        pass

    @abstractmethod
    def _delete_query(self) -> tuple[str, tuple]:
        """Returns a (SQL string, parameters) tuple for deletion"""
        pass

    def save(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            query, params = self._insert_query()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
        except Exception as e:
            print("Save Error:", e)
            return e

    def delete(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            query, params = self._delete_query()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
        except Exception as e:
            print("Delete Error:", e)
            return e

class Song(BaseModel):
    def __init__(self, title, artist, album, year, genre, file_path, file_name, duration, file_format):
        super().__init__()
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year
        self.genre = genre
        self.file_path = file_path
        self.file_name = file_name
        self.duration = duration
        self.file_format = file_format

        # Tier 2 defaults
        self.bitrate = None
        self.sample_rate = None
        self.channels = None
        self.file_size = None

    def _insert_query(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM songs WHERE file_path = ?", (self.file_path,))
        if cursor.fetchone():
            raise ValueError(f"Song already exists in database: <{self.file_path}>")
        conn.close()

        return (
            '''
            INSERT INTO songs (
                title, artist, album, year, genre, file_path, file_name,
                duration, file_format, bitrate, sample_rate, channels, file_size,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                self.title, self.artist, self.album, self.year, self.genre,
                self.file_path, self.file_name, self.duration, self.file_format,
                self.bitrate, self.sample_rate, self.channels, self.file_size,
                self.created_at, self.updated_at
            )
    )

    def _delete_query(self):
        return (
            'DELETE FROM songs WHERE file_path = ?',
            (self.file_path,)
        )
        

    def get_all_songs():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs ORDER BY title ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows


    def find_song_by_title(title: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE title LIKE ?", (f"%{title}%",))
        results = cursor.fetchall()
        conn.close()
        return results


from typing import List

class SongCollection:
    """
    A collection of Song objects with helper methods for querying and aggregation.
    """
    def __init__(self, songs: List[Song]):
        self._songs = songs

    @property
    def total(self) -> int:
        """Return the total number of songs in the collection."""
        return len(self._songs)

    def get_by_artist(self, artist_name: str) -> 'SongCollection':
        """Return a new SongCollection of songs matching the given artist."""
        matching = [s for s in self._songs if s.artist.lower() == artist_name.lower()]
        return SongCollection(matching)

    def __iter__(self):
        return iter(self._songs)

    def __getitem__(self, idx):
        return self._songs[idx]

    def __len__(self):
        return len(self._songs)

    def to_list(self) -> List[Song]:
        """Return a plain list of Song objects."""
        return list(self._songs)


class Controller:
    def __init__(self):
        self._downloaded_songs = None
        # playlists store Song objects; wrap into SongCollection on retrieval
        self.playlists = {"Chill Vibes": []}

    @property
    def downloaded_songs(self) -> SongCollection:
        """Lazy-load and return all downloaded songs as a SongCollection."""
        if self._downloaded_songs is None:
            raw = self.load_downloaded_songs()
            self._downloaded_songs = SongCollection(raw)
        return self._downloaded_songs

    def load_downloaded_songs(self) -> list[Song]:
        """Fetch all song records from DB and map to Song objects."""
        rows = Song.get_all_songs()
        return [self._row_to_song(row) for row in rows]

    def _row_to_song(self, row) -> Song:
        song = Song(
            title=row["title"],
            artist=row["artist"],
            album=row["album"],
            year=row["year"],
            genre=row["genre"],
            file_path=row["file_path"],
            file_name=row["file_name"],
            duration=row["duration"],
            file_format=row["file_format"]
        )
        # Tier 2 fields
        song.bitrate = row["bitrate"]
        song.sample_rate = row["sample_rate"]
        song.channels = row["channels"]
        song.file_size = row["file_size"]
        song.created_at = row["created_at"]
        song.updated_at = row["updated_at"]
        return song

    def get_num_downloaded_songs(self) -> int:
        """Return the total number of downloaded songs."""
        return self.downloaded_songs.total

    def add_to_playlist(self, playlist_name: str, song: Song):
        """Add a Song object to the named playlist."""
        if playlist_name not in self.playlists:
            self.playlists[playlist_name] = []
        self.playlists[playlist_name].append(song)

    def get_playlist(self, playlist_name: str) -> SongCollection:
        """Retrieve songs in the named playlist as a SongCollection."""
        songs = self.playlists.get(playlist_name, [])
        return SongCollection(songs)

# Singleton instance
controller = Controller()

