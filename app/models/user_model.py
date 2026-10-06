from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import DatabaseConnection

class User:
    ROLES = ("owner", "manager", "operator")

    def __init__(self, name: str, email: str, password_hash: str = None, 
                 store_id: int = None, role: str = "operator", 
                 id: int = None, created_at: str = None):
        self.id = id
        self.store_id = store_id
        self.name = name.strip()
        self.email = email.strip().lower() if email else ""
        self.password_hash = password_hash
        self.role = role if role in self.ROLES else "operator"
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def salvar(self):
        """Insere ou atualiza o usuário com loja e perfil associados."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = """
                    INSERT INTO users (store_id, name, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (self.store_id, self.name, self.email, self.password_hash, self.role, self.created_at))
                self.id = cursor.lastrowid
            else:
                query = """
                    UPDATE users 
                    SET store_id = ?, name = ?, email = ?, password_hash = ?, role = ?
                    WHERE id = ?
                """
                cursor.execute(query, (self.store_id, self.name, self.email, self.password_hash, self.role, self.id))
        return self

    @classmethod
    def buscar_por_email(cls, email: str):
        sanitized_email = email.strip().lower()
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, store_id, name, email, password_hash, role, created_at FROM users WHERE email = ?"
            cursor.execute(query, (sanitized_email,))
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
    def buscar_por_id(cls, user_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, store_id, name, email, password_hash, role, created_at FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))
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
    def excluir(cls, user_id: int, store_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM users WHERE id = ? AND store_id = ?"
            cursor.execute(query, (user_id, store_id))

    @classmethod
    def listar_por_loja(cls, store_id: int):
        """Retorna todos os membros de equipe vinculados à mesma loja."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, store_id, name, email, password_hash, role, created_at FROM users WHERE store_id = ? ORDER BY id ASC"
            cursor.execute(query, (store_id,))
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

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"