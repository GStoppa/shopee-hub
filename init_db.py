from app.database import DatabaseConnection
from app.models.store_model import Store
from app.models.user_model import User

def inicializar_banco():
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        
        # 1. Tabela de Lojas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        # 2. Tabela de Usuários (com store_id e role)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'operator',
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE
            );
        """)
        
        # 3. Tabela de Produtos (vinculada à loja)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sku TEXT NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE
            );
        """)
    print("Tabelas 'stores', 'users' e 'products' prontas.")

    # Inserção da Loja Inicial e Usuário Dono (Owner)
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM stores LIMIT 1")
        store_row = cursor.fetchone()

    if not store_row:
        loja_padrao = Store(name="Shopee Matriz").salvar()
        print(f"Loja inicial criada com ID: {loja_padrao.id}")
        store_id = loja_padrao.id
    else:
        store_id = store_row["id"]

    admin_existente = User.buscar_por_email("admin@shopee.com")
    if not admin_existente:
        admin = User(
            name="Administrador Shopee", 
            email="admin@shopee.com", 
            store_id=store_id, 
            role="owner"
        )
        admin.set_password("123456")
        admin.salvar()
        print("Usuário 'admin@shopee.com' cadastrado como Dono (owner) da loja!")
    else:
        print("Usuário administrador já existente.")

if __name__ == "__main__":
    inicializar_banco()