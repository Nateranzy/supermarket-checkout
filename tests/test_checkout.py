import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from core.cart import Cart
from core.checkout import InsufficientPaymentError, PaymentMethod, finalize_sale
from core.database import get_connection, init_db


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Usa um banco de dados temporário para cada teste, sem afetar o real."""
    fake_db = tmp_path / "test.db"
    monkeypatch.setattr("core.database.DB_PATH", fake_db)
    init_db()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO products (barcode, name, price_cents, stock) VALUES (?, ?, ?, ?)",
            ("123", "Produto Teste", 500, 10),
        )
    yield


def make_cart_with_item():
    cart = Cart()
    with get_connection() as conn:
        produto = conn.execute("SELECT * FROM products WHERE barcode = ?", ("123",)).fetchone()
    cart.add_product(produto, quantity=2)  # total = 1000 centavos
    return cart


def test_finalize_sale_with_exact_cash():
    cart = make_cart_with_item()
    resultado = finalize_sale(cart, PaymentMethod.CASH, paid_cents=1000)
    assert resultado["change_cents"] == 0
    assert resultado["total_cents"] == 1000


def test_finalize_sale_with_change():
    cart = make_cart_with_item()
    resultado = finalize_sale(cart, PaymentMethod.CASH, paid_cents=1500)
    assert resultado["change_cents"] == 500


def test_finalize_sale_insufficient_cash_raises():
    cart = make_cart_with_item()
    with pytest.raises(InsufficientPaymentError):
        finalize_sale(cart, PaymentMethod.CASH, paid_cents=500)


def test_finalize_sale_card_ignores_paid_cents():
    cart = make_cart_with_item()
    resultado = finalize_sale(cart, PaymentMethod.CARD)
    assert resultado["change_cents"] == 0
    assert resultado["paid_cents"] == 1000


def test_finalize_sale_updates_stock():
    cart = make_cart_with_item()
    finalize_sale(cart, PaymentMethod.CARD)
    with get_connection() as conn:
        produto = conn.execute("SELECT stock FROM products WHERE barcode = ?", ("123",)).fetchone()
    assert produto["stock"] == 8  # 10 - 2


def test_finalize_sale_empty_cart_raises():
    cart = Cart()
    with pytest.raises(ValueError):
        finalize_sale(cart, PaymentMethod.CASH, paid_cents=1000)