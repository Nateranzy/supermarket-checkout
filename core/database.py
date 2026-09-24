import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "caixa.db"

# Códigos de barras fictícios, só para testes
SAMPLE_PRODUCTS = [
    ("7890000000011", "Leite Integral 1L", 549, 100),
    ("7890000000028", "Açúcar Refinado 1kg", 429, 80),
    ("7890000000035", "Café Torrado 500g", 1890, 50),
    ("7890000000042", "Achocolatado 400g", 899, 60),
    ("7890000000059", "Arroz Branco 5kg", 2790, 40),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    return conn


def init_db():
    with closing(get_connection()) as conn, conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
                stock INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                total_cents INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                paid_cents INTEGER NOT NULL,
                change_cents INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL REFERENCES sales(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL,
                unit_price_cents INTEGER NOT NULL
            );
        """)


def seed_products():
    with closing(get_connection()) as conn, conn:
        conn.executemany(
            "INSERT OR IGNORE INTO products (barcode, name, price_cents, stock) "
            "VALUES (?, ?, ?, ?)",
            SAMPLE_PRODUCTS,
        )


def get_product_by_barcode(barcode):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM products WHERE barcode = ?", (barcode.strip(),)
        ).fetchone()