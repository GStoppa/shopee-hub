from datetime import datetime, timezone
from app.database import DatabaseConnection

class Product:
    def __init__(self, user_id: int, name: str, sku: str, price: float, stock_quantity: int = 0, id: int = None, created_at: str = None):
        self.id = id
        self.user_id = user_id
        self.name = name.strip()
        self.sku = sku.strip().upper()
        self.price = float(price)
        self.stock_quantity = int(stock_quantity)
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def salvar(self):
        """Insere ou atualiza o produto na base de dados de forma parametrizada."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = """
                    INSERT INTO products (user_id, name, sku, price, stock_quantity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (self.user_id, self.name, self.sku, self.price, self.stock_quantity, self.created_at))
                self.id = cursor.lastrowid
            else:
                query = """
                    UPDATE products
                    SET name = ?, sku = ?, price = ?, stock_quantity = ?
                    WHERE id = ? AND user_id = ?
                """
                cursor.execute(query, (self.name, self.sku, self.price, self.stock_quantity, self.id, self.user_id))
        return self

    @classmethod
    def listar_por_usuario(cls, user_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM products WHERE user_id = ? ORDER BY id DESC"
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()

            return [
                cls(
                    id=row["id"],
                    user_id=row["user_id"],
                    name=row["name"],
                    sku=row["sku"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    @classmethod
    def buscar_por_id(cls, product_id: int, user_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM products WHERE id = ? AND user_id = ?"
            cursor.execute(query, (product_id, user_id))
            row = cursor.fetchone()

            if row:
                return cls(
                    id=row["id"],
                    user_id=row["user_id"],
                    name=row["name"],
                    sku=row["sku"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    created_at=row["created_at"]
                )
        return None

    @classmethod
    def atualizar_estoque(cls, product_id: int, user_id: int, nova_quantidade: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "UPDATE products SET stock_quantity = ? WHERE id = ? AND user_id = ?"
            cursor.execute(query, (nova_quantidade, product_id, user_id))

    @classmethod
    def excluir(cls, product_id: int, user_id: int):
        """Elimina o produto garantindo que pertence ao utilizador autenticado."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM products WHERE id = ? AND user_id = ?"
            cursor.execute(query, (product_id, user_id))