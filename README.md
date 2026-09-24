# Supermarket Checkout System (POS)

A point-of-sale (POS) system built in Python, simulating a supermarket checkout counter. The project is structured in layers to allow future migration to embedded hardware (e.g. Raspberry Pi).

## Features

- Barcode scanning (compatible with USB scanners, which work as keyboard input)
- Shopping cart with automatic quantity summing
- Payment by cash (with change calculation), card, and Pix
- Automatic stock deduction on every sale
- Simulated receipt
- Daily sales report (total revenue, breakdown by payment method, top-selling products)

## Tech Stack

- Python 3
- Tkinter (graphical interface)
- SQLite (database)
- Pytest (automated testing)

## Architecture

The project is divided into three layers:

# Supermarket Checkout System (POS)

A point-of-sale (POS) system built in Python, simulating a supermarket checkout counter. The project is structured in layers to allow future migration to embedded hardware (e.g. Raspberry Pi).

## Features

- Barcode scanning (compatible with USB scanners, which work as keyboard input)
- Shopping cart with automatic quantity summing
- Payment by cash (with change calculation), card, and Pix
- Automatic stock deduction on every sale
- Simulated receipt
- Daily sales report (total revenue, breakdown by payment method, top-selling products)

## Tech Stack

- Python 3
- Tkinter (graphical interface)
- SQLite (database)
- Pytest (automated testing)

## Architecture

The project is divided into three layers:


This separation allows swapping the interface (for example, to a touchscreen on a Raspberry Pi) without changing the business logic.

## How to Run

```bash
# Clone the repository
git clone https://github.com/Nateranzy/caixa-supermercado.git
cd caixa-supermercado

# Create and activate the virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows

# Install dependencies
pip install pytest

# Run the system
python main.py
```

## How to Test

```bash
pytest -v
```

## Sample Products (for testing)

| Barcode | Product |
|---|---|
| 7890000000011 | Whole Milk 1L |
| 7890000000028 | Refined Sugar 1kg |
| 7890000000035 | Roasted Coffee 500g |
| 7890000000042 | Chocolate Powder 400g |
| 7890000000059 | White Rice 5kg |

## Future Improvements

- Product registration through the interface
- Real receipt printing (thermal printer)
- Real hardware support (Raspberry Pi + barcode scanner)