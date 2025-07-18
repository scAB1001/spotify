from core.models.Base import BaseModel

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
        from core.db import get_connection
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
