import sqlite3
import os
from datetime import datetime
from abc import ABC, abstractmethod

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'music.db')


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
