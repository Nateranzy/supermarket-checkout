import tkinter as tk
from tkinter import ttk

from core.reports import get_today_summary, get_top_products


def show_reports(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("Relatório do dia")
    win.geometry("420x420")

    summary = get_today_summary()

    tk.Label(win, text=f"Resumo de {summary['date']}", font=("Segoe UI", 13, "bold")).pack(pady=10)
    tk.Label(win, text=f"Vendas realizadas: {summary['sale_count']}").pack(anchor="w", padx=20)
    tk.Label(win, text=f"Total faturado: R$ {summary['total_cents'] / 100:.2f}").pack(anchor="w", padx=20)

    tk.Label(win, text="Por forma de pagamento:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
    if not summary["by_method"]:
        tk.Label(win, text="  (nenhuma venda ainda)").pack(anchor="w", padx=20)
    for method, cents in summary["by_method"].items():
        tk.Label(win, text=f"  {method}: R$ {cents / 100:.2f}").pack(anchor="w", padx=20)

    tk.Label(win, text="Produtos mais vendidos hoje:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

    columns = ("name", "quantity", "total")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=8)
    tree.heading("name", text="Produto")
    tree.heading("quantity", text="Qtd")
    tree.heading("total", text="Total")
    tree.column("quantity", width=50, anchor="center")
    tree.column("total", width=100, anchor="e")
    tree.pack(fill="both", expand=True, padx=20, pady=5)

    for prod in get_top_products(summary["date"], summary["date"]):
        tree.insert("", "end", values=(
            prod["name"], prod["total_quantity"], f"R$ {prod['total_cents'] / 100:.2f}",
        ))

    tk.Button(win, text="Fechar", command=win.destroy).pack(pady=10)