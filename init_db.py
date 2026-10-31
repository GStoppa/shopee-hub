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
                document TEXT,
                phone TEXT,
                address TEXT,
                shopee_shop_id TEXT,
                logo_url TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # 2. Tabela de Usuários
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

        # 3. Tabela de Categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE
            );
        """)

        # 4. Tabela de Produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                weight_g REAL DEFAULT 0,
                length_cm REAL DEFAULT 0,
                width_cm REAL DEFAULT 0,
                height_cm REAL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
            );
        """)

        # 5. Tabela de Variações de Produto
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                barcode TEXT,
                variant_name TEXT NOT NULL DEFAULT 'Padrão',
                cost_price REAL NOT NULL DEFAULT 0.0,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                min_stock INTEGER NOT NULL DEFAULT 5,
                image_url TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            );
        """)

        # 6. Tabela de Auditoria de Estoque
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_id INTEGER NOT NULL,
                user_id INTEGER,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                previous_stock INTEGER NOT NULL DEFAULT 0,
                resulting_stock INTEGER NOT NULL DEFAULT 0,
                reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (variant_id) REFERENCES product_variants (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            );
        """)

        # Migração defensiva: colunas de saldo
        cursor.execute("PRAGMA table_info(stock_movements);")
        colunas_sm = [col["name"] for col in cursor.fetchall()]
        if "previous_stock" not in colunas_sm:
            cursor.execute("ALTER TABLE stock_movements ADD COLUMN previous_stock INTEGER NOT NULL DEFAULT 0;")
        if "resulting_stock" not in colunas_sm:
            cursor.execute("ALTER TABLE stock_movements ADD COLUMN resulting_stock INTEGER NOT NULL DEFAULT 0;")

        # Índices de Alta Performance (Evita Full Table Scans)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_store_id ON users (store_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_store_id ON categories (store_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_store_id ON products (store_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category_id ON products (category_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_variants_product_id ON product_variants (product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_variants_sku ON product_variants (sku);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_movements_variant_id ON stock_movements (variant_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_movements_user_id ON stock_movements (user_id);")

        # Reparação: garante variações padrão para produtos antigos sem variação
        cursor.execute("""
            SELECT p.id, p.name, p.created_at
            FROM products p
            LEFT JOIN product_variants pv ON p.id = pv.product_id
            WHERE pv.id IS NULL;
        """)
        for prod in cursor.fetchall():
            cursor.execute("""
                INSERT INTO product_variants (
                    product_id, sku, variant_name, cost_price, price,
                    stock_quantity, min_stock, created_at
                )
                VALUES (?, ?, 'Padrão', 0.0, 0.0, 0, 5, ?);
            """, (prod["id"], f"SKU-{prod['id']}", prod["created_at"]))

    # Garante loja padrão
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM stores LIMIT 1;")
        store_row = cursor.fetchone()

    if not store_row:
        loja_padrao = Store(
            name="Shopee Matriz",
            document="00.000.000/0001-00",
            phone="(11) 99999-9999",
            address="São Paulo, SP"
        ).salvar()
        store_id = loja_padrao.id
    else:
        store_id = store_row["id"]

    # Garante administrador da loja se ainda não houver nenhum proprietário cadastrado
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE store_id = ? AND role = 'owner';", (store_id,))
        total_owners = cursor.fetchone()["total"]

    if total_owners == 0:
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

if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados inicializado com sucesso!")