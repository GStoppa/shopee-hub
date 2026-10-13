from app.database import DatabaseConnection
from app.models.store_model import Store
from app.models.user_model import User

def inicializar_banco():
    with DatabaseConnection() as conn:
        cursor = conn.cursor()

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE
            );
        """)

        cursor.execute("PRAGMA table_info(products);")
        product_cols = [row["name"] for row in cursor.fetchall()]

        if "sku" in product_cols:
            cursor.execute("ALTER TABLE products RENAME TO old_products;")

            cursor.execute("""
                CREATE TABLE products (
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

            cursor.execute("""
                CREATE TABLE product_variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    sku TEXT NOT NULL UNIQUE,
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

            cursor.execute("""
                SELECT id, store_id, name, sku, price, stock_quantity, created_at 
                FROM old_products;
            """)
            antigos = cursor.fetchall()

            for item in antigos:
                cursor.execute("""
                    INSERT INTO products (id, store_id, name, is_active, created_at)
                    VALUES (?, ?, ?, 1, ?);
                """, (item["id"], item["store_id"], item["name"], item["created_at"]))

                cursor.execute("""
                    INSERT INTO product_variants (
                        product_id, sku, variant_name, cost_price, price, 
                        stock_quantity, min_stock, created_at
                    )
                    VALUES (?, ?, 'Padrão', 0.0, ?, ?, 5, ?);
                """, (item["id"], item["sku"], item["price"], item["stock_quantity"], item["created_at"]))

            cursor.execute("DROP TABLE old_products;")
        else:
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    sku TEXT NOT NULL UNIQUE,
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_id INTEGER NOT NULL,
                user_id INTEGER,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (variant_id) REFERENCES product_variants (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            );
        """)

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