from datetime import datetime
from app.database import DatabaseConnection

class StockMovement:
    def __init__(self, variant_id: int, movement_type: str, quantity: int, 
                 previous_stock: int = 0, resulting_stock: int = 0, 
                 user_id: int = None, reason: str = None, id: int = None, 
                 created_at: str = None, user_name: str = None, 
                 variant_sku: str = None, variant_name: str = None, 
                 product_name: str = None):
        self.id = id
        self.variant_id = variant_id
        self.user_id = user_id
        self.movement_type = movement_type
        self.quantity = quantity
        self.previous_stock = previous_stock
        self.resulting_stock = resulting_stock
        self.reason = reason
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.user_name = user_name
        self.variant_sku = variant_sku
        self.variant_name = variant_name
        self.product_name = product_name

    def salvar(self, cursor=None):
        def _executar(c):
            query = """
                INSERT INTO stock_movements (
                    variant_id, user_id, movement_type, quantity,
                    previous_stock, resulting_stock, reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            c.execute(query, (
                self.variant_id, self.user_id, self.movement_type, self.quantity,
                self.previous_stock, self.resulting_stock, self.reason, self.created_at
            ))
            self.id = c.lastrowid
            return self

        if cursor:
            return _executar(cursor)

        with DatabaseConnection() as conn:
            c = conn.cursor()
            res = _executar(c)
            return res

    @classmethod
    def _construir_filtros_movimentos(cls, store_id: int, busca: str = None, tipo: str = None):
        sql_where = " WHERE p.store_id = ?"
        params = [store_id]

        if busca:
            sql_where += " AND (p.name LIKE ? OR pv.sku LIKE ? OR sm.reason LIKE ?)"
            termo = f"%{busca}%"
            params.extend([termo, termo, termo])

        if tipo in ["entrada", "saida", "ajuste"]:
            sql_where += " AND sm.movement_type = ?"
            params.append(tipo)

        return sql_where, params

    @classmethod
    def contar_por_loja(cls, store_id: int, busca: str = None, tipo: str = None) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql_where, params = cls._construir_filtros_movimentos(store_id, busca, tipo)
            query = f"""
                SELECT COUNT(*) AS total
                FROM stock_movements sm
                JOIN product_variants pv ON sm.variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                {sql_where}
            """
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def listar_por_loja(cls, store_id: int, busca: str = None, tipo: str = None, limite: int = 20, offset: int = 0):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql_where, params = cls._construir_filtros_movimentos(store_id, busca, tipo)
            query = f"""
                SELECT sm.*, u.name AS user_name, pv.sku AS variant_sku, pv.variant_name, p.name AS product_name
                FROM stock_movements sm
                JOIN product_variants pv ON sm.variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                LEFT JOIN users u ON sm.user_id = u.id
                {sql_where}
                ORDER BY sm.id DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limite, offset])
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row["id"],
                    variant_id=row["variant_id"],
                    user_id=row["user_id"],
                    movement_type=row["movement_type"],
                    quantity=row["quantity"],
                    previous_stock=row["previous_stock"] if "previous_stock" in row.keys() else 0,
                    resulting_stock=row["resulting_stock"] if "resulting_stock" in row.keys() else 0,
                    reason=row["reason"],
                    created_at=row["created_at"],
                    user_name=row["user_name"],
                    variant_sku=row["variant_sku"],
                    variant_name=row["variant_name"],
                    product_name=row["product_name"]
                )
                for row in rows
            ]

    @classmethod
    def contar_por_variante(cls, variant_id: int, store_id: int) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) AS total
                FROM stock_movements sm
                JOIN product_variants pv ON sm.variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE sm.variant_id = ? AND p.store_id = ?
            """
            cursor.execute(query, (variant_id, store_id))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def listar_por_variante(cls, variant_id: int, store_id: int, limite: int = 20, offset: int = 0):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT sm.*, u.name AS user_name, pv.sku AS variant_sku, pv.variant_name, p.name AS product_name
                FROM stock_movements sm
                JOIN product_variants pv ON sm.variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                LEFT JOIN users u ON sm.user_id = u.id
                WHERE sm.variant_id = ? AND p.store_id = ?
                ORDER BY sm.id DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (variant_id, store_id, limite, offset))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row["id"],
                    variant_id=row["variant_id"],
                    user_id=row["user_id"],
                    movement_type=row["movement_type"],
                    quantity=row["quantity"],
                    previous_stock=row["previous_stock"] if "previous_stock" in row.keys() else 0,
                    resulting_stock=row["resulting_stock"] if "resulting_stock" in row.keys() else 0,
                    reason=row["reason"],
                    created_at=row["created_at"],
                    user_name=row["user_name"],
                    variant_sku=row["variant_sku"],
                    variant_name=row["variant_name"],
                    product_name=row["product_name"]
                )
                for row in rows
            ]