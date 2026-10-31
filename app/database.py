import sqlite3
from flask import current_app
from config import Config

class DatabaseConnection:
    def __init__(self, db_path=None):
        if db_path:
            self.db_path = db_path
        else:
            try:
                self.db_path = current_app.config["DATABASE"]
            except RuntimeError:
                self.db_path = Config.DATABASE
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path, timeout=15.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()