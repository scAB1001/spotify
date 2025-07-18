from core.models.Song import Song
from core.data_access import get_all_songs

class Controller:
    def __init__(self):
        self._downloaded_songs = None
        self.playlists = {"Chill Vibes": []}

    @property
    def downloaded_songs(self):
        if self._downloaded_songs is None:
            self._downloaded_songs = self.load_downloaded_songs()
        return self._downloaded_songs

    def load_downloaded_songs(self):
        rows = get_all_songs()
        return [self._row_to_song(row) for row in rows]

    def _row_to_song(self, row):
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
        song.bitrate = row["bitrate"]
        song.sample_rate = row["sample_rate"]
        song.channels = row["channels"]
        song.file_size = row["file_size"]
        song.created_at = row["created_at"]
        song.updated_at = row["updated_at"]
        return song

    def add_to_playlist(self, playlist_name, song):
        if playlist_name not in self.playlists:
            self.playlists[playlist_name] = []
        self.playlists[playlist_name].append(song)

    def get_playlist(self, playlist_name):
        return self.playlists.get(playlist_name, [])
    
    def get_num_downloaded_songs(self):
        return len(self._downloaded_songs)
        

# Singleton instance
controller = Controller()
