from enum import Enum

from core.cart import Cart
from core.database import get_connection


class PaymentMethod(str, Enum):
    CASH = "dinheiro"
    CARD = "cartao"
    PIX = "pix"


class InsufficientPaymentError(Exception):
    """Levantado quando o valor pago em dinheiro é menor que o total."""


def finalize_sale(cart: Cart, payment_method: PaymentMethod, paid_cents: int | None = None) -> dict:
    if len(cart) == 0:
        raise ValueError("Carrinho vazio")

    total = cart.total_cents

    if payment_method == PaymentMethod.CASH:
        if paid_cents is None:
            raise ValueError("Informe o valor pago em dinheiro")
        if paid_cents < total:
            raise InsufficientPaymentError(
                f"Faltam R$ {(total - paid_cents) / 100:.2f}"
            )
        change_cents = paid_cents - total
    else:
        # Cartão e Pix: valor pago é exatamente o total, sem troco
        paid_cents = total
        change_cents = 0

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO sales (total_cents, payment_method, paid_cents, change_cents) "
            "VALUES (?, ?, ?, ?)",
            (total, payment_method.value, paid_cents, change_cents),
        )
        sale_id = cursor.lastrowid

        for item in cart.items.values():
            conn.execute(
                "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price_cents) "
                "VALUES (?, ?, ?, ?)",
                (sale_id, item.product_id, item.quantity, item.unit_price_cents),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item.quantity, item.product_id),
            )

    return {
        "sale_id": sale_id,
        "total_cents": total,
        "paid_cents": paid_cents,
        "change_cents": change_cents,
    }