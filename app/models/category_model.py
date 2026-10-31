from datetime import datetime
from app.database import DatabaseConnection

class Category:
    def __init__(self, store_id: int, name: str, id: int = None, 
                 created_at: str = None, total_produtos: int = 0):
        self.id = id
        self.store_id = store_id
        self.name = name.strip() if name else ""
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_produtos = total_produtos

    def salvar(self, cursor=None):
        def _executar(c):
            if self.id is None:
                query = "INSERT INTO categories (store_id, name, created_at) VALUES (?, ?, ?)"
                c.execute(query, (self.store_id, self.name, self.created_at))
                self.id = c.lastrowid
            else:
                query = "UPDATE categories SET name = ? WHERE id = ? AND store_id = ?"
                c.execute(query, (self.name, self.id, self.store_id))

        if cursor:
            _executar(cursor)
        else:
            with DatabaseConnection() as conn:
                _executar(conn.cursor())
        return self

    @classmethod
    def listar_por_loja(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT c.*, COUNT(p.id) AS total_produtos
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                WHERE c.store_id = ?
                GROUP BY c.id
                ORDER BY c.name ASC
            """
            cursor.execute(query, (store_id,))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    created_at=row["created_at"],
                    total_produtos=row["total_produtos"] if "total_produtos" in row.keys() else 0
                )
                for row in rows
            ]

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
    def nome_existe(cls, name: str, store_id: int, exclude_id: int = None) -> bool:
        if not name:
            return False
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql = "SELECT id FROM categories WHERE store_id = ? AND LOWER(name) = LOWER(?)"
            params = [store_id, name.strip()]
            if exclude_id:
                sql += " AND id != ?"
                params.append(exclude_id)
            cursor.execute(sql, tuple(params))
            return cursor.fetchone() is not None

    @classmethod
    def excluir(cls, category_id: int, store_id: int) -> bool:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ? AND store_id = ?", (category_id, store_id))
            return cursor.rowcount > 0