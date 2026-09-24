import tkinter as tk

from tkinter import messagebox, ttk
from core.cart import Cart
from core.checkout import InsufficientPaymentError, PaymentMethod, finalize_sale
from core.database import get_product_by_barcode, init_db, seed_products
from ui.receipt_window import show_receipt  
from ui.reports_window import show_reports


class CheckoutWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Caixa - Supermercado")
        self.root.geometry("700x500")

        self.cart = Cart()

        self._build_widgets()
        self._refresh_cart()

    def _build_widgets(self):
        # --- Campo de código de barras ---
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill="x", padx=10)

        tk.Label(top_frame, text="Código de barras:", font=("Segoe UI", 11)).pack(side="left")

        self.barcode_var = tk.StringVar()
        entry = tk.Entry(top_frame, textvariable=self.barcode_var, font=("Segoe UI", 12))
        entry.pack(side="left", fill="x", expand=True, padx=8)
        entry.bind("<Return>", self._on_barcode_enter)
        entry.focus_set()

        # --- Tabela do carrinho ---
        columns = ("name", "quantity", "unit_price", "subtotal")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="Produto")
        self.tree.heading("quantity", text="Qtd")
        self.tree.heading("unit_price", text="Preço un.")
        self.tree.heading("subtotal", text="Subtotal")
        self.tree.column("quantity", width=60, anchor="center")
        self.tree.column("unit_price", width=100, anchor="e")
        self.tree.column("subtotal", width=100, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Delete>", self._on_remove_selected)

        # --- Total ---
        self.total_label = tk.Label(self.root, text="Total: R$ 0.00", font=("Segoe UI", 16, "bold"))
        self.total_label.pack(pady=5)

        # --- Botões ---
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(fill="x", padx=10)

        tk.Button(
            button_frame, text="Remover item selecionado (Del)",
            command=self._on_remove_selected,
        ).pack(side="left")

        tk.Button(
            button_frame, text="Finalizar venda", bg="#2e7d32", fg="white",
            font=("Segoe UI", 11, "bold"), command=self._on_finalize,
        ).pack(side="right")

        tk.Button(
            button_frame, text="Relatório do dia",
            command=lambda: show_reports(self.root),
        ).pack(side="right", padx=10)

    # --- Eventos ---

    def _on_barcode_enter(self, event=None):
        barcode = self.barcode_var.get().strip()
        self.barcode_var.set("")
        if not barcode:
            return

        produto = get_product_by_barcode(barcode)
        if produto is None:
            messagebox.showwarning("Não encontrado", f"Código não cadastrado: {barcode}")
            return

        self.cart.add_product(produto)
        self._refresh_cart()

    def _on_remove_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        barcode = selected[0]  # usamos o barcode como iid da linha
        self.cart.remove_product(barcode)
        self._refresh_cart()

    def _on_finalize(self):
        if len(self.cart) == 0:
            messagebox.showinfo("Carrinho vazio", "Bipe pelo menos um produto antes de finalizar.")
            return

        self._sold_items = list(self.cart.items.values())  # guarsda antes de limpar o carrinho
        PaymentDialog(self.root, self.cart, on_success=self._on_sale_success)

    def _on_sale_success(self, resultado):
        show_receipt(self.root, self._sold_items, resultado, self._last_payment_method)
        self.cart.clear()
        self._refresh_cart()
    # --- Atualização da tela ---

    def _refresh_cart(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.cart.items.values():
            self.tree.insert(
                "", "end", iid=item.barcode,
                values=(
                    item.name,
                    item.quantity,
                    f"R$ {item.unit_price_cents / 100:.2f}",
                    f"R$ {item.subtotal_cents / 100:.2f}",
                ),
            )
        self.total_label.config(text=f"Total: R$ {self.cart.total_cents / 100:.2f}")


class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, cart: Cart, on_success):
        super().__init__(parent)
        self.cart = cart
        self.on_success = on_success
        self.title("Pagamento")
        self.geometry("320x220")
        self.resizable(False, False)
        self.grab_set()  # trava a janela principal até fechar essa

        tk.Label(
            self, text=f"Total: R$ {cart.total_cents / 100:.2f}",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=10)

        self.method_var = tk.StringVar(value=PaymentMethod.CASH.value)
        for method in PaymentMethod:
            tk.Radiobutton(
                self, text=method.value.capitalize(), variable=self.method_var,
                value=method.value, command=self._toggle_cash_field,
            ).pack(anchor="w", padx=30)

        self.cash_frame = tk.Frame(self)
        self.cash_frame.pack(pady=5)
        tk.Label(self.cash_frame, text="Valor recebido (R$):").pack(side="left")
        self.paid_var = tk.StringVar()
        tk.Entry(self.cash_frame, textvariable=self.paid_var, width=10).pack(side="left", padx=5)

        tk.Button(self, text="Confirmar", bg="#2e7d32", fg="white", command=self._confirm).pack(pady=10)

    def _toggle_cash_field(self):
        if self.method_var.get() == PaymentMethod.CASH.value:
            self.cash_frame.pack(pady=5)
        else:
            self.cash_frame.pack_forget()

    def _confirm(self):
        method = PaymentMethod(self.method_var.get())
        paid_cents = None

        if method == PaymentMethod.CASH:
            raw = self.paid_var.get().strip().replace(",", ".")
            try:
                paid_cents = round(float(raw) * 100)
            except ValueError:
                messagebox.showerror("Valor inválido", "Digite um valor numérico válido.")
                return

            try:
                resultado = finalize_sale(self.cart, method, paid_cents)
            except InsufficientPaymentError as e:
                messagebox.showerror("Pagamento insuficiente", str(e))
                return

        self.master._last_payment_method = method.value
        self.destroy()
        self.on_success(resultado)


def main():
    init_db()
    seed_products()

    root = tk.Tk()
    CheckoutWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()