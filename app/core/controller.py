import os
from mutagen.mp3 import MP3  # type: ignore
from mutagen.easyid3 import EasyID3  # type: ignore
from core.models.models import Song

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
        rows = Song.get_all_songs()
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

    def import_mp3(self, filepath):
        try:
            audio = MP3(filepath, ID3=EasyID3)
        except Exception as e:
            print(f"Skipping {filepath}: {e}")
            return

        # Extract metadata
        title = audio.get("title", [os.path.basename(filepath)])[0]
        artist = audio.get("artist", ["Unknown Artist"])[0]
        album = audio.get("album", ["Unknown Album"])[0]
        year = int(audio.get("date", [0])[0]) if audio.get("date") else 0
        genre = audio.get("genre", ["Unknown"])[0]
        duration = int(audio.info.length)
        file_size = os.path.getsize(filepath)

        song = Song(
            title=title,
            artist=artist,
            album=album,
            year=year,
            genre=genre,
            file_path=filepath,
            file_name=os.path.basename(filepath),
            duration=duration,
            file_format="mp3"
        )

        # Add Tier 2 info
        song.bitrate = audio.info.bitrate // 1000  # convert to kbps
        song.sample_rate = audio.info.sample_rate
        song.channels = "Stereo" if audio.info.channels == 2 else "Mono"
        song.file_size = file_size

        song.save()
        print(f"✔ Added: {title} by {artist}")
        

# Singleton instance
controller = Controller()
