from app.database import DatabaseConnection
from app.models.user_model import User

def inicializar_banco():
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        # 1. Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        
        # 2. Tabela de Produtos (com chave estrangeira para users)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sku TEXT NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
    print("Tabelas 'users' e 'products' verificadas/criadas com sucesso.")

    # Registro de teste inicial
    admin_existente = User.buscar_por_email("admin@shopee.com")
    if not admin_existente:
        admin = User(name="Administrador Shopee", email="admin@shopee.com")
        admin.set_password("123456")
        admin.salvar()
        print("Usuário administrador inicial criado com sucesso!")
    else:
        print("Usuário administrador já existe no banco.")

if __name__ == "__main__":
    inicializar_banco()