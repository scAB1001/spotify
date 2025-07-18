import logging
from typing import List
from core.models.models import Song, SongCollection

logger = logging.getLogger(__name__)


class Controller:
    """
    Application controller for managing songs and playlists.
    Orchestrates DB-backed Song collections and in-memory playlists.
    """

    def __init__(self):
        self._downloaded_songs: SongCollection | None = None
        self.playlists: dict[str, SongCollection] = {}

    # ————— Downloaded Songs —————

    @property
    def downloaded_songs(self) -> SongCollection:
        """
        Lazy-load and return all downloaded songs as a SongCollection.
        """
        if self._downloaded_songs is None:
            self._downloaded_songs = self._load_downloaded_songs()
        return self._downloaded_songs

    def _load_downloaded_songs(self) -> SongCollection:
        """
        Fetch all songs from the DB, convert rows into Song instances,
        and wrap them into a SongCollection.
        """
        rows = Song.get_all_songs()
        songs: List[Song] = [Song.from_row(r) for r in rows]
        return SongCollection(songs)

    @property
    def num_downloaded_songs(self) -> int:
        """
        Total number of downloaded songs.
        """
        return self.downloaded_songs.total

    def search_downloaded_by_title(self, term: str) -> SongCollection:
        """
        Return a SongCollection filtered by title substring.
        """
        return self.downloaded_songs.filter_by_title(term)

    def import_mp3(self, filepath: str) -> bool:
        """
        Import a single MP3 file into the database via Song.from_file().
        Returns True on success, False if the song already exists or fails.
        """
        try:
            song = Song.from_file(filepath)      # parsing and metadata extraction in model
            song.save()                          # may raise ValueError on duplicate
            self._downloaded_songs = None        # invalidate cache
            logger.info(f"Imported: {song.title} by {song.artist}")
            return True
        except ValueError as ve:
            logger.warning(ve)
            return False
        except Exception as e:
            logger.error(f"Failed to import {filepath}: {e}")
            return False

    # ————— Playlists —————

    @property
    def playlist_names(self) -> list[str]:
        """
        List of all playlist names.
        """
        return list(self.playlists.keys())

    @property
    def num_playlists(self) -> int:
        """
        Total number of playlists.
        """
        return len(self.playlists)

    def get_playlist(self, name: str) -> SongCollection:
        """
        Retrieve the named playlist as a SongCollection (empty if not found).
        """
        return self.playlists.get(name, SongCollection([]))

    def add_to_playlist(self, name: str, song: Song) -> None:
        """
        Add a Song object to the given playlist, creating it if necessary.
        """
        if name not in self.playlists:
            self.playlists[name] = SongCollection([])
        self.playlists[name].append(song)

    # ————— Controller Utilities —————

    def clear_downloaded_cache(self) -> None:
        """
        Manually reset the downloaded songs cache.
        """
        self._downloaded_songs = None


# Singleton instance
controller = Controller()