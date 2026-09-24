import tkinter as tk

from core.cart import Cart


def show_receipt(parent: tk.Tk, cart_items: list, resultado: dict, payment_method: str):
    win = tk.Toplevel(parent)
    win.title(f"Cupom - Venda #{resultado['sale_id']}")
    win.geometry("320x420")
    win.resizable(False, False)

    text = tk.Text(win, font=("Consolas", 10), padx=10, pady=10)
    text.pack(fill="both", expand=True)

    linhas = [
        "==============================",
        "      SUPERMERCADO CARIRI",
        "==============================",
        f"Venda #{resultado['sale_id']}",
        "------------------------------",
    ]
    for item in cart_items:
        linhas.append(f"{item.quantity}x {item.name}")
        linhas.append(f"   R$ {item.unit_price_cents / 100:.2f} un. = R$ {item.subtotal_cents / 100:.2f}")
    linhas += [
        "------------------------------",
        f"TOTAL:  R$ {resultado['total_cents'] / 100:.2f}",
        f"PAGO ({payment_method}):  R$ {resultado['paid_cents'] / 100:.2f}",
        f"TROCO:  R$ {resultado['change_cents'] / 100:.2f}",
        "==============================",
        "     Obrigado pela compra!",
    ]

    text.insert("1.0", "\n".join(linhas))
    text.config(state="disabled")  # só leitura

    tk.Button(win, text="Fechar", command=win.destroy).pack(pady=8)