import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.cart import Cart


def make_fake_product(id=1, barcode="123", name="Produto Teste", price_cents=500):
    return {"id": id, "barcode": barcode, "name": name, "price_cents": price_cents}


def test_add_product_new_item():
    cart = Cart()
    cart.add_product(make_fake_product())
    assert len(cart) == 1
    assert cart.total_cents == 500


def test_add_same_product_twice_sums_quantity():
    cart = Cart()
    produto = make_fake_product()
    cart.add_product(produto)
    cart.add_product(produto)
    assert len(cart) == 1
    assert cart.items["123"].quantity == 2
    assert cart.total_cents == 1000


def test_remove_product():
    cart = Cart()
    cart.add_product(make_fake_product())
    cart.remove_product("123")
    assert len(cart) == 0


def test_set_quantity_to_zero_removes_item():
    cart = Cart()
    cart.add_product(make_fake_product())
    cart.set_quantity("123", 0)
    assert len(cart) == 0


def test_total_items_counts_quantities_not_lines():
    cart = Cart()
    cart.add_product(make_fake_product(barcode="123"), quantity=3)
    cart.add_product(make_fake_product(barcode="456"), quantity=2)
    assert cart.total_items == 5
    assert len(cart) == 2