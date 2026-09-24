from datetime import date

from core.database import get_connection


def get_sales_between(start_date: str, end_date: str) -> list[dict]:
    """start_date e end_date no formato 'YYYY-MM-DD'."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, total_cents, payment_method
            FROM sales
            WHERE date(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return [dict(row) for row in rows]


def get_today_summary() -> dict:
    today = date.today().isoformat()
    sales = get_sales_between(today, today)

    total_cents = sum(s["total_cents"] for s in sales)
    by_method: dict[str, int] = {}
    for s in sales:
        by_method[s["payment_method"]] = by_method.get(s["payment_method"], 0) + s["total_cents"]

    return {
        "date": today,
        "sale_count": len(sales),
        "total_cents": total_cents,
        "by_method": by_method,
    }


def get_top_products(start_date: str, end_date: str, limit: int = 5) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.name, SUM(si.quantity) AS total_quantity,
                   SUM(si.quantity * si.unit_price_cents) AS total_cents
            FROM sale_items si
            JOIN products p ON p.id = si.product_id
            JOIN sales s ON s.id = si.sale_id
            WHERE date(s.created_at) BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY total_quantity DESC
            LIMIT ?
            """,
            (start_date, end_date, limit),
        ).fetchall()
    return [dict(row) for row in rows]