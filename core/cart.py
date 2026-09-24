from dataclasses import dataclass, field


@dataclass
class CartItem:
    product_id: int
    barcode: str
    name: str
    unit_price_cents: int
    quantity: int = 1

    @property
    def subtotal_cents(self) -> int:
        return self.unit_price_cents * self.quantity


class Cart:
    def __init__(self):
        self.items: dict[str, CartItem] = {}  # chave = barcode

    def add_product(self, product, quantity: int = 1):
        """Recebe uma linha do banco (sqlite3.Row) e adiciona ao carrinho."""
        if quantity <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        barcode = product["barcode"]

        if barcode in self.items:
            self.items[barcode].quantity += quantity
        else:
            self.items[barcode] = CartItem(
                product_id=product["id"],
                barcode=barcode,
                name=product["name"],
                unit_price_cents=product["price_cents"],
                quantity=quantity,
            )

    def remove_product(self, barcode: str):
        self.items.pop(barcode, None)

    def set_quantity(self, barcode: str, quantity: int):
        if barcode not in self.items:
            return
        if quantity <= 0:
            self.remove_product(barcode)
        else:
            self.items[barcode].quantity = quantity

    def clear(self):
        self.items.clear()

    @property
    def total_cents(self) -> int:
        return sum(item.subtotal_cents for item in self.items.values())

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.values())

    def __len__(self):
        return len(self.items)