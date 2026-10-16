from datetime import datetime, timezone
from app.database import DatabaseConnection

class Category:
    def __init__(self, store_id: int, name: str, id: int = None, created_at: str = None):
        self.id = id
        self.store_id = store_id
        self.name = name.strip()
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def salvar(self):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = "INSERT INTO categories (store_id, name, created_at) VALUES (?, ?, ?)"
                cursor.execute(query, (self.store_id, self.name, self.created_at))
                self.id = cursor.lastrowid
            else:
                query = "UPDATE categories SET name = ? WHERE id = ? AND store_id = ?"
                cursor.execute(query, (self.name, self.id, self.store_id))
        return self

    @classmethod
    def buscar_por_id(cls, category_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ? AND store_id = ?", (category_id, store_id))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    created_at=row["created_at"]
                )
        return None

    @classmethod
    def listar_por_loja(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE store_id = ? ORDER BY name ASC", (store_id,))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    @classmethod
    def contar_produtos_vinculados(cls, category_id: int, store_id: int) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM products WHERE category_id = ? AND store_id = ?",
                (category_id, store_id)
            )
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def excluir(cls, category_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ? AND store_id = ?", (category_id, store_id))