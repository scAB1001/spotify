import os
from mutagen.mp3 import MP3  # type: ignore
from mutagen.easyid3 import EasyID3  # type: ignore
from core.models.Song import Song

def import_mp3(filepath):
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
