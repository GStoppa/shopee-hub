from datetime import datetime
from app.database import DatabaseConnection

class Store:
    def __init__(self, name: str, document: str = None, phone: str = None, 
                 address: str = None, shopee_shop_id: str = None, 
                 ml_user_id: str = None, tiktok_shop_id: str = None, 
                 aliexpress_seller_id: str = None, logo_url: str = None, 
                 id: int = None, created_at: str = None):
        self.id = id
        self.name = name.strip() if name else ""
        self.document = document.strip() if document else ""
        self.phone = phone.strip() if phone else ""
        self.address = address.strip() if address else ""
        self.shopee_shop_id = shopee_shop_id.strip() if shopee_shop_id else ""
        self.ml_user_id = ml_user_id.strip() if ml_user_id else ""
        self.tiktok_shop_id = tiktok_shop_id.strip() if tiktok_shop_id else ""
        self.aliexpress_seller_id = aliexpress_seller_id.strip() if aliexpress_seller_id else ""
        self.logo_url = logo_url
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def salvar(self, cursor=None):
        def _executar(c):
            if self.id is None:
                query = """
                    INSERT INTO stores (name, document, phone, address, shopee_shop_id, 
                                        ml_user_id, tiktok_shop_id, aliexpress_seller_id, 
                                        logo_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                c.execute(query, (
                    self.name, self.document, self.phone, self.address, 
                    self.shopee_shop_id, self.ml_user_id, self.tiktok_shop_id,
                    self.aliexpress_seller_id, self.logo_url, self.created_at
                ))
                self.id = c.lastrowid
            else:
                query = """
                    UPDATE stores
                    SET name = ?, document = ?, phone = ?, address = ?, 
                        shopee_shop_id = ?, ml_user_id = ?, tiktok_shop_id = ?, 
                        aliexpress_seller_id = ?, logo_url = ?
                    WHERE id = ?
                """
                c.execute(query, (
                    self.name, self.document, self.phone, self.address, 
                    self.shopee_shop_id, self.ml_user_id, self.tiktok_shop_id,
                    self.aliexpress_seller_id, self.logo_url, self.id
                ))

        if cursor:
            _executar(cursor)
        else:
            with DatabaseConnection() as conn:
                _executar(conn.cursor())
        return self

    @classmethod
    def buscar_por_id(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stores WHERE id = ?", (store_id,))
            row = cursor.fetchone()
            if row:
                keys = row.keys()
                return cls(
                    id=row["id"],
                    name=row["name"],
                    document=row["document"],
                    phone=row["phone"],
                    address=row["address"],
                    shopee_shop_id=row["shopee_shop_id"] if "shopee_shop_id" in keys else "",
                    ml_user_id=row["ml_user_id"] if "ml_user_id" in keys else "",
                    tiktok_shop_id=row["tiktok_shop_id"] if "tiktok_shop_id" in keys else "",
                    aliexpress_seller_id=row["aliexpress_seller_id"] if "aliexpress_seller_id" in keys else "",
                    logo_url=row["logo_url"],
                    created_at=row["created_at"]
                )
        return None