import math
from datetime import datetime, timezone
from app.database import DatabaseConnection

class StockMovement:
    def __init__(self, variant_id: int, quantity: int, movement_type: str, 
                 previous_stock: int = 0, resulting_stock: int = 0,
                 reason: str = None, user_id: int = None, id: int = None, 
                 created_at: str = None, user_name: str = None, 
                 variant_sku: str = None, variant_name: str = None, product_name: str = None):
        self.id = id
        self.variant_id = variant_id
        self.user_id = user_id
        self.movement_type = movement_type
        self.quantity = int(quantity)
        self.previous_stock = int(previous_stock or 0)
        self.resulting_stock = int(resulting_stock or 0)
        self.reason = reason.strip() if reason else ""
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.user_name = user_name or "Sistema"
        self.variant_sku = variant_sku or ""
        self.variant_name = variant_name or ""
        self.product_name = product_name or ""

    def salvar(self, cursor=None):
        query = """
            INSERT INTO stock_movements (
                variant_id, user_id, movement_type, quantity, 
                previous_stock, resulting_stock, reason, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            self.variant_id, self.user_id, self.movement_type, self.quantity,
            self.previous_stock, self.resulting_stock, self.reason, self.created_at
        )
        if cursor:
            cursor.execute(query, params)
            self.id = cursor.lastrowid
        else:
            with DatabaseConnection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                self.id = c.lastrowid
        return self

    @classmethod
    def listar_por_variante(cls, variant_id: int, store_id: int):
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
            """
            cursor.execute(query, (variant_id, store_id))
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
    def contar_por_loja(cls, store_id: int) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) AS total
                FROM stock_movements sm
                JOIN product_variants pv ON sm.variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                WHERE p.store_id = ?
            """
            cursor.execute(query, (store_id,))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def listar_por_loja(cls, store_id: int, limite: int = 20, offset: int = 0):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT sm.*, u.name AS user_name, pv.sku AS variant_sku, pv.variant_name, p.name AS product_name
                FROM stock_movements sm
                JOIN product_variants pv ON sm.variant_id = pv.id
                JOIN products p ON pv.product_id = p.id
                LEFT JOIN users u ON sm.user_id = u.id
                WHERE p.store_id = ?
                ORDER BY sm.id DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (store_id, limite, offset))
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


class ProductVariant:
    def __init__(self, product_id: int, sku: str, price: float, 
                 variant_name: str = "Padrão", cost_price: float = 0.0, 
                 stock_quantity: int = 0, min_stock: int = 5, barcode: str = None, 
                 image_url: str = None, id: int = None, created_at: str = None,
                 product_name: str = None):
        self.id = id
        self.product_id = product_id
        self.sku = sku.strip().upper() if sku else ""
        self.barcode = barcode.strip() if barcode else None
        self.variant_name = variant_name.strip() if variant_name else "Padrão"
        self.cost_price = float(cost_price or 0.0)
        self.price = float(price or 0.0)
        self.stock_quantity = int(stock_quantity or 0)
        self.min_stock = int(min_stock or 5)
        self.image_url = image_url.strip() if image_url else None
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.product_name = product_name

    @property
    def margin_percent(self) -> float:
        if self.price > 0:
            return round(((self.price - self.cost_price) / self.price) * 100, 2)
        return 0.0

    @property
    def display_name(self) -> str:
        if self.product_name:
            if self.variant_name and self.variant_name != "Padrão":
                return f"{self.product_name} - {self.variant_name}"
            return self.product_name
        return self.variant_name

    def salvar(self, cursor=None):
        if self.id is None:
            query = """
                INSERT INTO product_variants (
                    product_id, sku, barcode, variant_name, cost_price, price, 
                    stock_quantity, min_stock, image_url, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                self.product_id, self.sku, self.barcode, self.variant_name,
                self.cost_price, self.price, self.stock_quantity,
                self.min_stock, self.image_url, self.created_at
            )
            if cursor:
                cursor.execute(query, params)
                self.id = cursor.lastrowid
            else:
                with DatabaseConnection() as conn:
                    c = conn.cursor()
                    c.execute(query, params)
                    self.id = c.lastrowid
        else:
            query = """
                UPDATE product_variants
                SET sku = ?, barcode = ?, variant_name = ?, cost_price = ?, price = ?, 
                    stock_quantity = ?, min_stock = ?, image_url = ?
                WHERE id = ? AND product_id = ?
            """
            params = (
                self.sku, self.barcode, self.variant_name, self.cost_price,
                self.price, self.stock_quantity, self.min_stock,
                self.image_url, self.id, self.product_id
            )
            if cursor:
                cursor.execute(query, params)
            else:
                with DatabaseConnection() as conn:
                    c = conn.cursor()
                    c.execute(query, params)
        return self

    @classmethod
    def sku_existe(cls, sku: str, exclude_variant_id: int = None) -> bool:
        if not sku:
            return False
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql = "SELECT id FROM product_variants WHERE UPPER(sku) = UPPER(?)"
            params = [sku.strip()]
            if exclude_variant_id:
                sql += " AND id != ?"
                params.append(exclude_variant_id)
            cursor.execute(sql, tuple(params))
            return cursor.fetchone() is not None

    @classmethod
    def contar_por_produto(cls, product_id: int) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM product_variants WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def excluir(cls, variant_id: int, store_id: int) -> bool:
        from app.utils.upload import remover_imagem_produto
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pv.image_url, pv.product_id
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ? AND p.store_id = ?
            """, (variant_id, store_id))
            row = cursor.fetchone()
            if not row:
                return False

            if row["image_url"]:
                remover_imagem_produto(row["image_url"])

            cursor.execute("DELETE FROM product_variants WHERE id = ?", (variant_id,))
            return True

    @classmethod
    def buscar_por_id(cls, variant_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT pv.*, p.name AS product_name
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ? AND p.store_id = ?
            """
            cursor.execute(query, (variant_id, store_id))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row["id"],
                    product_id=row["product_id"],
                    sku=row["sku"],
                    barcode=row["barcode"],
                    variant_name=row["variant_name"],
                    cost_price=row["cost_price"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    min_stock=row["min_stock"],
                    image_url=row["image_url"],
                    created_at=row["created_at"],
                    product_name=row["product_name"]
                )
        return None

    @classmethod
    def atualizar_stock(cls, variant_id: int, store_id: int, nova_quantidade: int, user_id: int = None, motivo: str = "Ajuste manual"):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query_busca = """
                SELECT pv.id, pv.stock_quantity
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ? AND p.store_id = ?
            """
            cursor.execute(query_busca, (variant_id, store_id))
            row = cursor.fetchone()
            if not row:
                return False

            estoque_antigo = row["stock_quantity"]
            diferenca = nova_quantidade - estoque_antigo
            tipo = "entrada" if diferenca > 0 else ("saida" if diferenca < 0 else "ajuste")

            cursor.execute("UPDATE product_variants SET stock_quantity = ? WHERE id = ?", (nova_quantidade, variant_id))

            movimento = StockMovement(
                variant_id=variant_id,
                user_id=user_id,
                movement_type=tipo,
                quantity=abs(diferenca),
                previous_stock=estoque_antigo,
                resulting_stock=nova_quantidade,
                reason=motivo
            )
            movimento.salvar(cursor=cursor)
            return True

    @classmethod
    def registrar_movimento(cls, variant_id: int, store_id: int, user_id: int, tipo: str, quantidade: int, motivo: str):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT pv.id, pv.stock_quantity
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ? AND p.store_id = ?
            """
            cursor.execute(query, (variant_id, store_id))
            row = cursor.fetchone()
            if not row:
                return False

            atual = row["stock_quantity"]
            if tipo == "entrada":
                novo_saldo = atual + quantidade
            elif tipo == "saida":
                novo_saldo = max(0, atual - quantidade)
            elif tipo == "ajuste":
                novo_saldo = max(0, quantidade)
            else:
                return False

            cursor.execute("UPDATE product_variants SET stock_quantity = ? WHERE id = ?", (novo_saldo, variant_id))

            qtd_registrada = quantidade if tipo != "ajuste" else abs(novo_saldo - atual)

            mov = StockMovement(
                variant_id=variant_id,
                user_id=user_id,
                movement_type=tipo,
                quantity=qtd_registrada,
                previous_stock=atual,
                resulting_stock=novo_saldo,
                reason=motivo
            )
            mov.salvar(cursor=cursor)
            return True


class Product:
    def __init__(self, store_id: int, name: str, category_id: int = None, 
                 description: str = None, weight_g: float = 0.0, length_cm: float = 0.0, 
                 width_cm: float = 0.0, height_cm: float = 0.0, is_active: int = 1, 
                 id: int = None, created_at: str = None, category_name: str = None,
                 variants: list = None):
        self.id = id
        self.store_id = store_id
        self.category_id = category_id
        self.name = name.strip() if name else ""
        self.description = description.strip() if description else ""
        self.weight_g = float(weight_g or 0.0)
        self.length_cm = float(length_cm or 0.0)
        self.width_cm = float(width_cm or 0.0)
        self.height_cm = float(height_cm or 0.0)
        self.is_active = int(is_active)
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.category_name = category_name
        self.variants = variants or []

    @property
    def total_stock(self) -> int:
        return sum(v.stock_quantity for v in self.variants)

    @property
    def price_range(self) -> str:
        if not self.variants:
            return "R$ 0,00"
        precos = [v.price for v in self.variants]
        menor = min(precos)
        maior = max(precos)
        if menor == maior:
            return f"R$ {menor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        p_min = f"{menor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        p_max = f"{maior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {p_min} - R$ {p_max}"

    def salvar(self, cursor=None):
        def _executar(c):
            if self.id is None:
                query = """
                    INSERT INTO products (
                        store_id, category_id, name, description, weight_g, 
                        length_cm, width_cm, height_cm, is_active, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                c.execute(query, (
                    self.store_id, self.category_id, self.name, self.description,
                    self.weight_g, self.length_cm, self.width_cm, self.height_cm,
                    self.is_active, self.created_at
                ))
                self.id = c.lastrowid
            else:
                query = """
                    UPDATE products
                    SET category_id = ?, name = ?, description = ?, weight_g = ?, 
                        length_cm = ?, width_cm = ?, height_cm = ?, is_active = ?
                    WHERE id = ? AND store_id = ?
                """
                c.execute(query, (
                    self.category_id, self.name, self.description, self.weight_g,
                    self.length_cm, self.width_cm, self.height_cm, self.is_active,
                    self.id, self.store_id
                ))

            if self.variants:
                for v in self.variants:
                    v.product_id = self.id
                    v.salvar(cursor=c)

        if cursor:
            _executar(cursor)
        else:
            with DatabaseConnection() as conn:
                _executar(conn.cursor())
        return self

    @classmethod
    def buscar_por_id(cls, product_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ? AND p.store_id = ?
            """
            cursor.execute(query, (product_id, store_id))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT * FROM product_variants WHERE product_id = ? ORDER BY id ASC", (product_id,))
            v_rows = cursor.fetchall()
            variantes = [
                ProductVariant(
                    id=v["id"],
                    product_id=v["product_id"],
                    sku=v["sku"],
                    barcode=v["barcode"],
                    variant_name=v["variant_name"],
                    cost_price=v["cost_price"],
                    price=v["price"],
                    stock_quantity=v["stock_quantity"],
                    min_stock=v["min_stock"],
                    image_url=v["image_url"],
                    created_at=v["created_at"],
                    product_name=row["name"]
                )
                for v in v_rows
            ]

            return cls(
                id=row["id"],
                store_id=row["store_id"],
                category_id=row["category_id"],
                name=row["name"],
                description=row["description"],
                weight_g=row["weight_g"],
                length_cm=row["length_cm"],
                width_cm=row["width_cm"],
                height_cm=row["height_cm"],
                is_active=row["is_active"],
                created_at=row["created_at"],
                category_name=row["category_name"],
                variants=variantes
            )

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
            sql_where += " AND pv.stock_quantity > 0 AND pv.stock_quantity <= pv.min_stock"
        elif status == "esgotado":
            sql_where += " AND pv.stock_quantity = 0"

        return sql_where, params

    @classmethod
    def contar_por_loja(cls, store_id: int, busca: str = None, category_id: int = None, status: str = None) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql_where, params = cls._construir_filtros(store_id, busca, category_id, status)
            sql = f"""
                SELECT COUNT(DISTINCT p.id) AS total
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN product_variants pv ON p.id = pv.product_id
                {sql_where}
            """
            cursor.execute(sql, tuple(params))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def listar_por_loja(cls, store_id: int, busca: str = None, category_id: int = None, 
                        status: str = None, limite: int = None, offset: int = 0):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            sql_where, params = cls._construir_filtros(store_id, busca, category_id, status)
            sql = f"""
                SELECT DISTINCT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN product_variants pv ON p.id = pv.product_id
                {sql_where}
                ORDER BY p.id DESC
            """
            if limite is not None:
                sql += " LIMIT ? OFFSET ?"
                params.extend([limite, offset])

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

            produtos = []
            for row in rows:
                cursor.execute("SELECT * FROM product_variants WHERE product_id = ? ORDER BY id ASC", (row["id"],))
                v_rows = cursor.fetchall()
                variantes = [
                    ProductVariant(
                        id=v["id"],
                        product_id=v["product_id"],
                        sku=v["sku"],
                        barcode=v["barcode"],
                        variant_name=v["variant_name"],
                        cost_price=v["cost_price"],
                        price=v["price"],
                        stock_quantity=v["stock_quantity"],
                        min_stock=v["min_stock"],
                        image_url=v["image_url"],
                        created_at=v["created_at"],
                        product_name=row["name"]
                    )
                    for v in v_rows
                ]
                produtos.append(
                    cls(
                        id=row["id"],
                        store_id=row["store_id"],
                        category_id=row["category_id"],
                        name=row["name"],
                        description=row["description"],
                        weight_g=row["weight_g"],
                        length_cm=row["length_cm"],
                        width_cm=row["width_cm"],
                        height_cm=row["height_cm"],
                        is_active=row["is_active"],
                        created_at=row["created_at"],
                        category_name=row["category_name"],
                        variants=variantes
                    )
                )
            return produtos

    @classmethod
    def excluir(cls, product_id: int, store_id: int):
        from app.utils.upload import remover_imagem_produto
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pv.image_url 
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.id = ? AND p.store_id = ?
            """, (product_id, store_id))
            rows = cursor.fetchall()
            for r in rows:
                if r["image_url"]:
                    remover_imagem_produto(r["image_url"])

            cursor.execute("DELETE FROM products WHERE id = ? AND store_id = ?", (product_id, store_id))

    @classmethod
    def obter_metricas_dashboard(cls, store_id: int) -> dict:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS total FROM products WHERE store_id = ? AND is_active = 1", (store_id,))
            total_produtos = cursor.fetchone()["total"]

            query_esgotados = """
                SELECT COUNT(*) AS esgotados
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1 AND pv.stock_quantity = 0
            """
            cursor.execute(query_esgotados, (store_id,))
            esgotados = cursor.fetchone()["esgotados"]

            query_baixo = """
                SELECT COUNT(*) AS baixo
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1 
                  AND pv.stock_quantity > 0 AND pv.stock_quantity <= pv.min_stock
            """
            cursor.execute(query_baixo, (store_id,))
            baixo_estoque = cursor.fetchone()["baixo"]

            query_valor = """
                SELECT 
                    COALESCE(SUM(pv.price * pv.stock_quantity), 0.0) AS total_venda,
                    COALESCE(SUM(pv.cost_price * pv.stock_quantity), 0.0) AS total_custo
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1
            """
            cursor.execute(query_valor, (store_id,))
            fin = cursor.fetchone()

        return {
            "total_produtos": total_produtos,
            "esgotados": esgotados,
            "baixo_estoque": baixo_estoque,
            "valor_estoque": float(fin["total_venda"]),
            "custo_estoque": float(fin["total_custo"])
        }

    @classmethod
    def listar_produtos_criticos(cls, store_id: int, limite: int = 8):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT pv.*, p.name AS product_name
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE p.store_id = ? AND p.is_active = 1 AND pv.stock_quantity <= pv.min_stock
                ORDER BY pv.stock_quantity ASC, pv.id DESC
                LIMIT ?
            """
            cursor.execute(query, (store_id, limite))
            rows = cursor.fetchall()
            return [
                ProductVariant(
                    id=row["id"],
                    product_id=row["product_id"],
                    sku=row["sku"],
                    barcode=row["barcode"],
                    variant_name=row["variant_name"],
                    cost_price=row["cost_price"],
                    price=row["price"],
                    stock_quantity=row["stock_quantity"],
                    min_stock=row["min_stock"],
                    image_url=row["image_url"],
                    created_at=row["created_at"],
                    product_name=row["product_name"]
                )
                for row in rows
            ]