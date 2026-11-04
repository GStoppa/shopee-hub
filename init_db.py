import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
from config import Config

def migrar_colunas_tabela(cursor, nome_tabela, colunas_necessarias):
    cursor.execute(f"PRAGMA table_info({nome_tabela});")
    colunas_existentes = {linha[1] for linha in cursor.fetchall()}

    for nome_coluna, definicao in colunas_necessarias.items():
        if nome_coluna not in colunas_existentes:
            try:
                cursor.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN {nome_coluna} {definicao};")
                print(f"[MIGRAÇÃO] Coluna '{nome_coluna}' adicionada à tabela '{nome_tabela}'.")
            except sqlite3.OperationalError as e:
                print(f"[AVISO] Não foi possível adicionar '{nome_coluna}' em '{nome_tabela}': {e}")

def inicializar_banco():
    db_path = Config.DATABASE
    pasta_db = os.path.dirname(db_path)
    if pasta_db and not os.path.exists(pasta_db):
        os.makedirs(pasta_db, exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Ativa o modo WAL e chaves estrangeiras
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")

        # 1. Criação base das tabelas principais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                document TEXT,
                phone TEXT,
                address TEXT,
                shopee_shop_id TEXT,
                ml_user_id TEXT,
                tiktok_shop_id TEXT,
                aliexpress_seller_id TEXT,
                logo_url TEXT,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'operator',
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                name TEXT NOT NULL,
                description TEXT,
                weight_g REAL DEFAULT 0.0,
                length_cm REAL DEFAULT 0.0,
                width_cm REAL DEFAULT 0.0,
                height_cm REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                sku TEXT NOT NULL,
                barcode TEXT,
                variant_name TEXT NOT NULL DEFAULT 'Padrão',
                cost_price REAL NOT NULL DEFAULT 0.0,
                price REAL NOT NULL DEFAULT 0.0,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                min_stock INTEGER NOT NULL DEFAULT 5,
                image_url TEXT,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_id INTEGER NOT NULL REFERENCES product_variants(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                previous_stock INTEGER NOT NULL DEFAULT 0,
                resulting_stock INTEGER NOT NULL DEFAULT 0,
                reason TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # 2. Migração defensiva: garante a existência de todas as colunas em bases legadas
        migracoes = {
            "stores": {
                "document": "TEXT",
                "phone": "TEXT",
                "address": "TEXT",
                "shopee_shop_id": "TEXT",
                "ml_user_id": "TEXT",
                "tiktok_shop_id": "TEXT",
                "aliexpress_seller_id": "TEXT",
                "logo_url": "TEXT"
            },
            "products": {
                "category_id": "INTEGER",
                "description": "TEXT",
                "weight_g": "REAL DEFAULT 0.0",
                "length_cm": "REAL DEFAULT 0.0",
                "width_cm": "REAL DEFAULT 0.0",
                "height_cm": "REAL DEFAULT 0.0",
                "is_active": "INTEGER DEFAULT 1"
            },
            "product_variants": {
                "barcode": "TEXT",
                "variant_name": "TEXT DEFAULT 'Padrão'",
                "cost_price": "REAL DEFAULT 0.0",
                "min_stock": "INTEGER DEFAULT 5",
                "image_url": "TEXT"
            },
            "stock_movements": {
                "previous_stock": "INTEGER DEFAULT 0",
                "resulting_stock": "INTEGER DEFAULT 0",
                "reason": "TEXT",
                "user_id": "INTEGER"
            }
        }

        for tabela, colunas in migracoes.items():
            migrar_colunas_tabela(cursor, tabela, colunas)

        # 3. Criação de índices para otimização de consultas
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_store ON products(store_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_store ON categories(store_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_variants_sku ON product_variants(sku);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_variant ON stock_movements(variant_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_created ON stock_movements(created_at);")

        # 4. Assegurar loja padrão
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("SELECT id FROM stores LIMIT 1;")
        store_row = cursor.fetchone()
        if store_row:
            store_id = store_row["id"]
        else:
            cursor.execute("""
                INSERT INTO stores (name, document, phone, address, shopee_shop_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
            """, ("Minha Loja Shopee", "00.000.000/0001-00", "(11) 99999-9999", "São Paulo, SP", "SHOP123456", agora))
            store_id = cursor.lastrowid
            print(f"[INICIALIZAÇÃO] Loja padrão criada (ID: {store_id}).")

        # 5. Assegurar utilizador administrador
        cursor.execute("SELECT id FROM users WHERE email = 'admin@shopee.com';")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (store_id, name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                store_id,
                "Administrador",
                "admin@shopee.com",
                generate_password_hash("admin"),
                "owner",
                agora
            ))
            print("[INICIALIZAÇÃO] Utilizador 'admin@shopee.com' configurado com palavra-passe 'admin'.")

        # 6. Assegurar categorias padrão
        cursor.execute("SELECT COUNT(*) AS total FROM categories WHERE store_id = ?;", (store_id,))
        if cursor.fetchone()["total"] == 0:
            categorias_iniciais = ["Vestuário", "Calçados", "Acessórios", "Eletrônicos", "Geral"]
            for nome_cat in categorias_iniciais:
                cursor.execute("""
                    INSERT INTO categories (store_id, name, created_at)
                    VALUES (?, ?, ?);
                """, (store_id, nome_cat, agora))
            print(f"[INICIALIZAÇÃO] {len(categorias_iniciais)} categorias padrão registadas.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] Falha ao inicializar a base de dados: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    inicializar_banco()