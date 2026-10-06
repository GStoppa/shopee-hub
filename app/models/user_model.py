from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import DatabaseConnection

class User:
    def __init__(self, name: str, email: str, password_hash: str = None, id: int = None, created_at: str = None):
        self.id = id
        self.name = name
        self.email = email.strip().lower() if email else ""
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def salvar(self):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                query = """
                    INSERT INTO users (name, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(query, (self.name, self.email, self.password_hash, self.created_at))
                self.id = cursor.lastrowid
            else:
                query = """
                    UPDATE users 
                    SET name = ?, email = ?, password_hash = ?
                    WHERE id = ?
                """
                cursor.execute(query, (self.name, self.email, self.password_hash, self.id))
        return self

    @classmethod
    def buscar_por_email(cls, email: str):
        sanitized_email = email.strip().lower()
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?"
            cursor.execute(query, (sanitized_email,))
            row = cursor.fetchone()

            if row:
                return cls(
                    id=row["id"],
                    name=row["name"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    created_at=row["created_at"]
                )
        return None

    @classmethod
    def buscar_por_id(cls, user_id: int):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, name, email, password_hash, created_at FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()

            if row:
                return cls(
                    id=row["id"],
                    name=row["name"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    created_at=row["created_at"]
                )
        return None

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"