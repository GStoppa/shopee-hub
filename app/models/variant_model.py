from datetime import datetime
from app.database import DatabaseConnection
from app.models.stock_movement_model import StockMovement
from app.utils.upload import remover_imagem_produto

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
        
        self.cost_price = max(0.0, float(cost_price)) if cost_price is not None else 0.0
        self.price = max(0.0, float(price)) if price is not None else 0.0
        self.stock_quantity = max(0, int(stock_quantity)) if stock_quantity is not None else 0
        self.min_stock = max(1, int(min_stock)) if min_stock is not None else 5
        
        self.image_url = image_url.strip() if image_url else None
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.product_name = product_name

    @property
    def margin_percent(self) -> float:
        if self.price > 0:
            margem = ((self.price - self.cost_price) / self.price) * 100
            return round(margem, 2)
        return 0.0

    @property
    def display_name(self) -> str:
        if self.product_name:
            if self.variant_name and self.variant_name != "Padrão":
                return f"{self.product_name} - {self.variant_name}"
            return self.product_name
        return self.variant_name

    @classmethod
    def sku_existe(cls, sku: str, store_id: int, exclude_variant_id: int = None, cursor=None) -> bool:
        sku_limpo = sku.strip().upper()
        query = """
            SELECT pv.id
            FROM product_variants pv
            JOIN products p ON pv.product_id = p.id
            WHERE UPPER(pv.sku) = ? AND p.store_id = ?
        """
        params = [sku_limpo, store_id]
        if exclude_variant_id:
            query += " AND pv.id != ?"
            params.append(exclude_variant_id)

        if cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchone() is not None

        with DatabaseConnection() as conn:
            c = conn.cursor()
            c.execute(query, tuple(params))
            return c.fetchone() is not None

    def salvar(self, cursor=None):
        def _executar(c):
            if self.id:
                query = """
                    UPDATE product_variants SET
                        sku = ?, barcode = ?, variant_name = ?, cost_price = ?,
                        price = ?, stock_quantity = ?, min_stock = ?, image_url = ?
                    WHERE id = ?
                """
                c.execute(query, (
                    self.sku, self.barcode, self.variant_name, self.cost_price,
                    self.price, self.stock_quantity, self.min_stock, self.image_url,
                    self.id
                ))
            else:
                query = """
                    INSERT INTO product_variants (
                        product_id, sku, barcode, variant_name, cost_price, price,
                        stock_quantity, min_stock, image_url, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                c.execute(query, (
                    self.product_id, self.sku, self.barcode, self.variant_name,
                    self.cost_price, self.price, self.stock_quantity, self.min_stock,
                    self.image_url, self.created_at
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
            if not row:
                return None
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

    @classmethod
    def contar_por_produto(cls, product_id: int) -> int:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM product_variants WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            return row["total"] if row else 0

    @classmethod
    def atualizar_stock(cls, variant_id: int, store_id: int, new_stock: int, user_id: int = None, motivo: str = "Ajuste manual") -> bool:
        new_stock = max(0, int(new_stock))
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pv.id, pv.stock_quantity
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ? AND p.store_id = ?
            """, (variant_id, store_id))
            row = cursor.fetchone()
            if not row:
                return False

            old_stock = row["stock_quantity"]
            if old_stock == new_stock:
                return True

            diff = new_stock - old_stock
            tipo = "entrada" if diff > 0 else "saida"

            cursor.execute("UPDATE product_variants SET stock_quantity = ? WHERE id = ?", (new_stock, variant_id))

            StockMovement(
                variant_id=variant_id,
                user_id=user_id,
                movement_type=tipo,
                quantity=abs(diff),
                previous_stock=old_stock,
                resulting_stock=new_stock,
                reason=motivo
            ).salvar(cursor=cursor)

            return True

    @classmethod
    def registrar_movimento(cls, variant_id: int, store_id: int, user_id: int, tipo: str, quantidade: int, motivo: str) -> bool:
        quantidade = max(0, int(quantidade))
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pv.id, pv.stock_quantity
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.id
                WHERE pv.id = ? AND p.store_id = ?
            """, (variant_id, store_id))
            row = cursor.fetchone()
            if not row:
                return False

            old_stock = row["stock_quantity"]

            if tipo == "entrada":
                new_stock = old_stock + quantidade
                qtd_mov = quantidade
            elif tipo == "saida":
                if old_stock < quantidade:
                    return False
                new_stock = old_stock - quantidade
                qtd_mov = quantidade
            elif tipo == "ajuste":
                new_stock = quantidade
                qtd_mov = abs(new_stock - old_stock)
                tipo_real = "entrada" if new_stock >= old_stock else "saida"
            else:
                return False

            cursor.execute("UPDATE product_variants SET stock_quantity = ? WHERE id = ?", (new_stock, variant_id))

            StockMovement(
                variant_id=variant_id,
                user_id=user_id,
                movement_type=tipo if tipo != "ajuste" else tipo_real,
                quantity=qtd_mov,
                previous_stock=old_stock,
                resulting_stock=new_stock,
                reason=motivo
            ).salvar(cursor=cursor)

            return True

    @classmethod
    def excluir(cls, variant_id: int, store_id: int) -> bool:
        image_to_remove = None

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

            image_to_remove = row["image_url"]
            cursor.execute("DELETE FROM product_variants WHERE id = ?", (variant_id,))

        if image_to_remove:
            remover_imagem_produto(image_to_remove)

        return True