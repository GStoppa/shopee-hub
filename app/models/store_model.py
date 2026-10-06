from datetime import datetime, timezone
from app.database import DatabaseConnection

class Store:
    def __init__(self, name: str, id: int = None, created_at: str = None):
        self.id = id
        self.name = name.strip()
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def salvar(self):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = "INSERT INTO stores (name, created_at) VALUES (?, ?)"
                cursor.execute(query, (self.name, self.created_at))
                self.id = cursor.lastrowid
            else:
                query = "UPDATE stores SET name = ? WHERE id = ?"
                cursor.execute(query, (self.name, self.id))
        return self

    @classmethod
    def buscar_por_id(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, name, created_at FROM stores WHERE id = ?"
            cursor.execute(query, (store_id,))
            row = cursor.fetchone()
            if row:
                return cls(id=row["id"], name=row["name"], created_at=row["created_at"])
        return None

    def __repr__(self):
        return f"<Store id={self.id} name={self.name}>"