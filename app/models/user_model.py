from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import DatabaseConnection

class User:
    def __init__(self, name: str, email: str, store_id: int = None, 
                 role: str = "operator", password_hash: str = None, 
                 id: int = None, created_at: str = None):
        self.id = id
        self.store_id = store_id
        self.name = name.strip() if name else ""
        self.email = email.strip().lower() if email else ""
        self.password_hash = password_hash
        self.role = role if role in ["owner", "manager", "operator"] else "operator"
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def salvar(self, cursor=None):
        def _executar(c):
            if self.id is None:
                query = """
                    INSERT INTO users (store_id, name, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                c.execute(query, (
                    self.store_id, self.name, self.email, 
                    self.password_hash, self.role, self.created_at
                ))
                self.id = c.lastrowid
            else:
                query = """
                    UPDATE users
                    SET store_id = ?, name = ?, email = ?, password_hash = ?, role = ?
                    WHERE id = ?
                """
                c.execute(query, (
                    self.store_id, self.name, self.email, 
                    self.password_hash, self.role, self.id
                ))

        if cursor:
            _executar(cursor)
        else:
            with DatabaseConnection() as conn:
                _executar(conn.cursor())
        return self

    @classmethod
    def buscar_por_id(cls, user_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    created_at=row["created_at"]
                )
        return None

    @classmethod
    def buscar_por_email(cls, email: str):
        if not email:
            return None
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    created_at=row["created_at"]
                )
        return None

    @classmethod
    def listar_por_loja(cls, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE store_id = ? ORDER BY id ASC", (store_id,))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row["id"],
                    store_id=row["store_id"],
                    name=row["name"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    @classmethod
    def excluir(cls, user_id: int, store_id: int) -> bool:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ? AND store_id = ?", (user_id, store_id))
            return cursor.rowcount > 0