from core.db import create_tables, get_connection
from core.models.Song import Song

def init_db():
    create_tables()

def get_all_songs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM songs ORDER BY title ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Optional stub for filtering, paging, etc.
def find_song_by_title(title: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM songs WHERE title LIKE ?", (f"%{title}%",))
    results = cursor.fetchall()
    conn.close()
    return results
