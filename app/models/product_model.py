from datetime import datetime
from app.database import DatabaseConnection
from app.models.variant_model import ProductVariant
from app.models.stock_movement_model import StockMovement
from app.utils.upload import remover_imagem_produto

class Product:
    def __init__(self, store_id: int, name: str, category_id: int = None, 
                 description: str = None, weight_g: float = 0.0, 
                 length_cm: float = 0.0, width_cm: float = 0.0, 
                 height_cm: float = 0.0, is_active: int = 1, 
                 variants: list = None, id: int = None, 
                 created_at: str = None, category_name: str = None):
        self.id = id
        self.store_id = store_id
        self.category_id = category_id
        self.name = name.strip() if name else ""
        self.description = description.strip() if description else None
        self.weight_g = max(0.0, float(weight_g)) if weight_g is not None else 0.0
        self.length_cm = max(0.0, float(length_cm)) if length_cm is not None else 0.0
        self.width_cm = max(0.0, float(width_cm)) if width_cm is not None else 0.0
        self.height_cm = max(0.0, float(height_cm)) if height_cm is not None else 0.0
        self.is_active = 1 if is_active in [1, "1", True] else 0
        self.variants = variants or []
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.category_name = category_name

    @property
    def total_stock(self) -> int:
        return sum(v.stock_quantity for v in self.variants)

    @property
    def min_price(self) -> float:
        if not self.variants:
            return 0.0
        return min(v.price for v in self.variants)

    @property
    def max_price(self) -> float:
        if not self.variants:
            return 0.0
        return max(v.price for v in self.variants)

    @property
    def price_range(self) -> str:
        if not self.variants:
            return "R$ 0,00"
        p_min = self.min_price
        p_max = self.max_price
        if p_min == p_max:
            return f"R$ {p_min:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {p_min:,.2f} - R$ {p_max:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @property
    def has_low_stock_variant(self) -> bool:
        return any(0 < v.stock_quantity <= v.min_stock for v in self.variants)

    @property
    def has_out_of_stock_variant(self) -> bool:
        return any(v.stock_quantity == 0 for v in self.variants)

    @classmethod
    def _construir_filtros(cls, store_id: int, busca: str = None, category_id: int = None, status: str = None):
        sql_where = " WHERE p.store_id = ?"
        params = [store_id]

        if busca:
            sql_where += " AND (p.name LIKE ? OR pv.sku LIKE ? OR pv.barcode LIKE ?)"
            t = f"%{busca}%"
            params.extend([t, t, t])

        if category_id:
            sql_where += " AND p.category_id = ?"
            params.append(category_id)

        if status == "ativo":
            sql_where += " AND p.is_active = 1"
        elif status == "inativo":
            sql_where += " AND p.is_active = 0"
        elif status == "baixo":
            sql_where += " AND p.is_active = 1 AND pv.stock_quantity > 0 AND pv.stock_quantity <= pv.min_stock"
        elif status == "esgotado":
            sql_where += " AND p.is_active = 1 AND pv.stock_quantity = 0"

        return sql_where, params

    @classmethod
    def contar_por_loja(cls, store_id: int, busca: str = None, category_id: int = None, status: str = None) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql_where, params = cls._construir_filtros(store_id, busca, category_id, status)
            query = f"""
                SELECT COUNT(DISTINCT p.id) AS total
                FROM products p
                LEFT JOIN product_variants pv ON pv.product_id = p.id
                {sql_where}
            """
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def listar_por_loja(cls, store_id: int, busca: str = None, category_id: int = None, 
                        status: str = None, limite: int = 10, offset: int = 0):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql_where, params = cls._construir_filtros(store_id, busca, category_id, status)
            query = f"""
                SELECT DISTINCT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN product_variants pv ON pv.product_id = p.id
                {sql_where}
                ORDER BY p.id DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limite, offset])
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            produtos = []
            for row in rows:
                p_id = row["id"]
                cursor.execute("""
                    SELECT * FROM product_variants
                    WHERE product_id = ?
                    ORDER BY id ASC
                """, (p_id,))
                var_rows = cursor.fetchall()
                variantes = [
                    ProductVariant(
                        id=vr["id"],
                        product_id=vr["product_id"],
                        sku=vr["sku"],
                        barcode=vr["barcode"],
                        variant_name=vr["variant_name"],
                        cost_price=vr["cost_price"],
                        price=vr["price"],
                        stock_quantity=vr["stock_quantity"],
                        min_stock=vr["min_stock"],
                        image_url=vr["image_url"],
                        created_at=vr["created_at"],
                        product_name=row["name"]
                    )
                    for vr in var_rows
                ]
                produtos.append(
                    cls(
                        id=row["id"],
                        store_id=row["store_id"],
                        category_id=row["category_id"],
                        name=row["name"],
                        description=row["description"],
                        weight_g=row["weight_g"] if "weight_g" in row.keys() else 0.0,
                        length_cm=row["length_cm"] if "length_cm" in row.keys() else 0.0,
                        width_cm=row["width_cm"] if "width_cm" in row.keys() else 0.0,
                        height_cm=row["height_cm"] if "height_cm" in row.keys() else 0.0,
                        is_active=row["is_active"],
                        created_at=row["created_at"],
                        category_name=row["category_name"],
                        variants=variantes
                    )
                )
            return produtos

    @classmethod
    def buscar_por_id(cls, product_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ? AND p.store_id = ?
            """, (product_id, store_id))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("""
                SELECT * FROM product_variants
                WHERE product_id = ?
                ORDER BY id ASC
            """, (product_id,))
            var_rows = cursor.fetchall()
            variantes = [
                ProductVariant(
                    id=vr["id"],
                    product_id=vr["product_id"],
                    sku=vr["sku"],
                    barcode=vr["barcode"],
                    variant_name=vr["variant_name"],
                    cost_price=vr["cost_price"],
                    price=vr["price"],
                    stock_quantity=vr["stock_quantity"],
                    min_stock=vr["min_stock"],
                    image_url=vr["image_url"],
                    created_at=vr["created_at"],
                    product_name=row["name"]
                )
                for vr in var_rows
            ]

            return cls(
                id=row["id"],
                store_id=row["store_id"],
                category_id=row["category_id"],
                name=row["name"],
                description=row["description"],
                weight_g=row["weight_g"] if "weight_g" in row.keys() else 0.0,
                length_cm=row["length_cm"] if "length_cm" in row.keys() else 0.0,
                width_cm=row["width_cm"] if "width_cm" in row.keys() else 0.0,
                height_cm=row["height_cm"] if "height_cm" in row.keys() else 0.0,
                is_active=row["is_active"],
                created_at=row["created_at"],
                category_name=row["category_name"],
                variants=variantes
            )

    def salvar(self, cursor=None):
        def _executar(c):
            if self.id:
                query = """
                    UPDATE products SET
                        category_id = ?, name = ?, description = ?,
                        weight_g = ?, length_cm = ?, width_cm = ?, height_cm = ?,
                        is_active = ?
                    WHERE id = ? AND store_id = ?
                """
                c.execute(query, (
                    self.category_id, self.name, self.description,
                    self.weight_g, self.length_cm, self.width_cm, self.height_cm,
                    self.is_active, self.id, self.store_id
                ))
            else:
                query = """
                    INSERT INTO products (
                        store_id, category_id, name, description,
                        weight_g, length_cm, width_cm, height_cm, is_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                c.execute(query, (
                    self.store_id, self.category_id, self.name, self.description,
                    self.weight_g, self.length_cm, self.width_cm, self.height_cm,
                    self.is_active, self.created_at
                ))
                self.id = c.lastrowid

            for v in self.variants:
                v.product_id = self.id
                v.salvar(cursor=c)

            return self

        if cursor:
            return _executar(cursor)

        with DatabaseConnection() as conn:
            c = conn.cursor()
            res = _executar(c)
            return res

    @classmethod
    def excluir(cls, product_id: int, store_id: int):
        images_to_remove = []

        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pv.image_url 
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.id = ? AND p.store_id = ?
            """, (product_id, store_id))
            rows = cursor.fetchall()
            images_to_remove = [r["image_url"] for r in rows if r["image_url"]]

            cursor.execute("DELETE FROM products WHERE id = ? AND store_id = ?", (product_id, store_id))

        for img in images_to_remove:
            remover_imagem_produto(img)

    @classmethod
    def obter_metricas_dashboard(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM products WHERE store_id = ? AND is_active = 1", (store_id,))
            total_produtos = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(DISTINCT p.id) AS baixo
                FROM products p
                JOIN product_variants pv ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1 AND pv.stock_quantity > 0 AND pv.stock_quantity <= pv.min_stock
            """, (store_id,))
            baixo_estoque = cursor.fetchone()["baixo"]

            cursor.execute("""
                SELECT COUNT(DISTINCT p.id) AS esgotados
                FROM products p
                JOIN product_variants pv ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1 AND pv.stock_quantity = 0
            """, (store_id,))
            esgotados = cursor.fetchone()["esgotados"]

            cursor.execute("""
                SELECT 
                    COALESCE(SUM(pv.stock_quantity * pv.price), 0.0) AS valor_estoque,
                    COALESCE(SUM(pv.stock_quantity * pv.cost_price), 0.0) AS custo_estoque
                FROM products p
                JOIN product_variants pv ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1
            """, (store_id,))
            fin = cursor.fetchone()

            return {
                "total_produtos": total_produtos,
                "baixo_estoque": baixo_estoque,
                "esgotados": esgotados,
                "valor_estoque": fin["valor_estoque"],
                "custo_estoque": fin["custo_estoque"]
            }

    @classmethod
    def listar_produtos_criticos(cls, store_id: int, limite: int = 5):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT pv.*, p.name AS product_name
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1 AND pv.stock_quantity <= pv.min_stock
                ORDER BY pv.stock_quantity ASC, pv.id ASC
                LIMIT ?
            """
            cursor.execute(query, (store_id, limite))
            rows = cursor.fetchall()
            return [
                ProductVariant(
                    id=r["id"],
                    product_id=r["product_id"],
                    sku=r["sku"],
                    barcode=r["barcode"],
                    variant_name=r["variant_name"],
                    cost_price=r["cost_price"],
                    price=r["price"],
                    stock_quantity=r["stock_quantity"],
                    min_stock=r["min_stock"],
                    image_url=r["image_url"],
                    created_at=r["created_at"],
                    product_name=r["product_name"]
                )
                for r in rows
            ]

__all__ = ["Product", "ProductVariant", "StockMovement"]