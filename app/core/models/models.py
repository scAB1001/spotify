import sqlite3
from datetime import datetime
from abc import ABC, abstractmethod
from core.db import create_tables, get_connection
from typing import List

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
            conn = get_connection()
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
            conn = get_connection()
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
        return ('DELETE FROM songs WHERE file_path = ?', (self.file_path,))
        
    @classmethod
    def from_file(cls, filepath: str) -> "Song":
        """
        Create a Song instance by parsing an MP3 file’s ID3 tags and audio info.
        """
        # import here to avoid circular
        from mutagen.mp3 import MP3  # type: ignore
        from mutagen.easyid3 import EasyID3  # type: ignore
        import os

        try:
            audio = MP3(filepath, ID3=EasyID3)
        except Exception as e:
            raise ValueError(f"Cannot parse MP3 ({filepath}): {e}")

        # Tier 1: core metadata
        title = audio.get("title", [os.path.splitext(os.path.basename(filepath))[0]])[0]
        artist = audio.get("artist", ["Unknown Artist"])[0]
        album = audio.get("album", ["Unknown Album"])[0]
        year   = int(audio.get("date", [0])[0]) if audio.get("date") else 0
        genre  = audio.get("genre", ["Unknown"])[0]
        duration = int(audio.info.length)
        file_name = os.path.basename(filepath)

        song = cls(
            title=title,
            artist=artist,
            album=album,
            year=year,
            genre=genre,
            file_path=filepath,
            file_name=file_name,
            duration=duration,
            file_format="mp3"
        )

        # Tier 2: technical info
        song.bitrate     = audio.info.bitrate // 1000
        song.sample_rate = audio.info.sample_rate
        song.channels    = "Stereo" if audio.info.channels == 2 else "Mono"
        song.file_size   = os.path.getsize(filepath)

        return song

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Song":
        """
        Create a Song instance from a DB row (with dict-style access).
        """
        song = cls(
            title      = row["title"],
            artist     = row["artist"],
            album      = row["album"],
            year       = row["year"],
            genre      = row["genre"],
            file_path  = row["file_path"],
            file_name  = row["file_name"],
            duration   = row["duration"],
            file_format= row["file_format"]
        )
        # Tier 2 fields
        song.bitrate     = row["bitrate"]
        song.sample_rate = row["sample_rate"]
        song.channels    = row["channels"]
        song.file_size   = row["file_size"]
        song.created_at  = row["created_at"]
        song.updated_at  = row["updated_at"]
        return song
        
    @classmethod
    def get_all_songs(cls):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM songs ORDER BY title")
        rows = cur.fetchall()
        conn.close()
        return rows

    @classmethod
    def find_by_title(cls, title):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM songs WHERE title LIKE ?", (f"%{title}%",))
        results = cur.fetchall()
        conn.close()
        return results


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
