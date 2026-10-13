from datetime import datetime, timezone
from app.database import DatabaseConnection

class Store:
    def __init__(self, name: str, document: str = None, phone: str = None,
                 address: str = None, shopee_shop_id: str = None,
                 logo_url: str = None, id: int = None, created_at: str = None):
        self.id = id
        self.name = name.strip()
        self.document = document.strip() if document else None
        self.phone = phone.strip() if phone else None
        self.address = address.strip() if address else None
        self.shopee_shop_id = shopee_shop_id.strip() if shopee_shop_id else None
        self.logo_url = logo_url.strip() if logo_url else None
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def salvar(self):
        """Insere ou atualiza os dados completos da loja."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = """
                    INSERT INTO stores (name, document, phone, address, shopee_shop_id, logo_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    self.name,
                    self.document,
                    self.phone,
                    self.address,
                    self.shopee_shop_id,
                    self.logo_url,
                    self.created_at
                ))
                self.id = cursor.lastrowid
            else:
                query = """
                    UPDATE stores 
                    SET name = ?, document = ?, phone = ?, address = ?, shopee_shop_id = ?, logo_url = ?
                    WHERE id = ?
                """
                cursor.execute(query, (
                    self.name,
                    self.document,
                    self.phone,
                    self.address,
                    self.shopee_shop_id,
                    self.logo_url,
                    self.id
                ))
        return self

    @classmethod
    def buscar_por_id(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, name, document, phone, address, shopee_shop_id, logo_url, created_at 
                FROM stores 
                WHERE id = ?
            """
            cursor.execute(query, (store_id,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row["id"],
                    name=row["name"],
                    document=row["document"],
                    phone=row["phone"],
                    address=row["address"],
                    shopee_shop_id=row["shopee_shop_id"],
                    logo_url=row["logo_url"],
                    created_at=row["created_at"]
                )
        return None

    def __repr__(self):
        return f"<Store id={self.id} name={self.name} document={self.document}>"