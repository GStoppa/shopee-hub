from datetime import datetime, timezone
from app.database import DatabaseConnection

class Product:
    def __init__(self, store_id: int, name: str, sku: str, price: float, 
                 stock_quantity: int = 0, id: int = None, created_at: str = None):
        self.id = id
        self.store_id = store_id
        self.name = name.strip()
        self.sku = sku.strip().upper()
        self.price = float(price)
        self.stock_quantity = int(stock_quantity)
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def salvar(self):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = """
                    INSERT INTO products (store_id, name, sku, price, stock_quantity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (self.store_id, self.name, self.sku, self.price, self.stock_quantity, self.created_at))
                self.id = cursor.lastrowid
            else:
                query = """
                    UPDATE products
                    SET name = ?, sku = ?, price = ?, stock_quantity = ?
                    WHERE id = ? AND store_id = ?
                """
                cursor.execute(query, (self.name, self.sku, self.price, self.stock_quantity, self.id, self.store_id))
        return self

    @classmethod
    def listar_por_loja(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM products WHERE store_id = ? ORDER BY id DESC"
            cursor.execute(query, (store_id,))
            rows = cursor.fetchall()

            return [
                cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    sku=row["sku"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    @classmethod
    def buscar_por_id(cls, product_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM products WHERE id = ? AND store_id = ?"
            cursor.execute(query, (product_id, store_id))
            row = cursor.fetchone()

            if row:
                return cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    sku=row["sku"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    created_at=row["created_at"]
                )
        return None

    @classmethod
    def atualizar_stock(cls, product_id: int, store_id: int, nova_quantidade: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE products 
                SET stock_quantity = ? 
                WHERE id = ? AND store_id = ?
            """
            cursor.execute(query, (nova_quantidade, product_id, store_id))

    @classmethod
    def excluir(cls, product_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM products WHERE id = ? AND store_id = ?"
            cursor.execute(query, (product_id, store_id))

    @classmethod
    def obter_metricas_dashboard(cls, store_id: int) -> dict:
        """Calcula totais consolidados, contagem de risco e valor monetário em armazém."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            
            # Total de itens cadastrados no catálogo desta loja
            cursor.execute("SELECT COUNT(*) AS total FROM products WHERE store_id = ?", (store_id,))
            total_produtos = cursor.fetchone()["total"]

            # Quantidade de produtos esgotados (estoque zero)
            cursor.execute("SELECT COUNT(*) AS esgotados FROM products WHERE store_id = ? AND stock_quantity = 0", (store_id,))
            esgotados = cursor.fetchone()["esgotados"]

            # Quantidade de produtos em nível baixo (entre 1 e 4 unidades)
            cursor.execute("SELECT COUNT(*) AS baixo FROM products WHERE store_id = ? AND stock_quantity > 0 AND stock_quantity < 5", (store_id,))
            baixo_estoque = cursor.fetchone()["baixo"]

            # Valor bruto total do estoque (preço unitário * quantidade em saldo)
            cursor.execute("SELECT COALESCE(SUM(price * stock_quantity), 0.0) AS total_valor FROM products WHERE store_id = ?", (store_id,))
            valor_estoque = cursor.fetchone()["total_valor"]

        return {
            "total_produtos": total_produtos,
            "esgotados": esgotados,
            "baixo_estoque": baixo_estoque,
            "valor_estoque": float(valor_estoque)
        }

    @classmethod
    def listar_produtos_criticos(cls, store_id: int, limite: int = 6):
        """Retorna os produtos que precisam de reposição imediata (estoque < 5)."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM products 
                WHERE store_id = ? AND stock_quantity < 5
                ORDER BY stock_quantity ASC, id DESC
                LIMIT ?
            """
            cursor.execute(query, (store_id, limite))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    sku=row["sku"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]