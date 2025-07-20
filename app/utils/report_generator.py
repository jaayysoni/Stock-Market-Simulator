# app/utils/report_generator.py

import csv
import os
from fpdf import FPDF
from datetime import datetime
from app.utils.tax_calculator import calculate_tax_summary

def generate_csv_report(user_id: int, transactions: list[dict], output_path: str = "reports") -> str:
    os.makedirs(output_path, exist_ok=True)
    filename = f"user_{user_id}_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(output_path, filename)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Stock", "Type", "Quantity", "Price", "Timestamp"])
        for tx in transactions:
            writer.writerow([
                tx["stock_symbol"],
                tx["transaction_type"],
                tx["quantity"],
                tx["price"],
                tx["timestamp"]
            ])

    return filepath


def generate_pdf_report(user_id: int, transactions: list[dict], output_path: str = "reports") -> str:
    os.makedirs(output_path, exist_ok=True)
    filename = f"user_{user_id}_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(output_path, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Stock Market Portfolio Report", ln=True, align="C")
    pdf.ln(10)

    tax_data = calculate_tax_summary(transactions)
    for key, value in tax_data.items():
        pdf.cell(200, 10, txt=f"{key.capitalize()}: {value}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Transactions:", ln=True)
    pdf.ln(5)
    for tx in transactions:
        line = f"{tx['timestamp']} | {tx['stock_symbol']} | {tx['transaction_type']} | Qty: {tx['quantity']} | ₹{tx['price']}"
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(filepath)
    return filepath