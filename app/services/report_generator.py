# app/services/report_generator.py

import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from app.models import Transaction


def generate_csv_report(transactions: list[Transaction], user_email: str) -> str:
    filename = f"report_{user_email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = f"/tmp/{filename}"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Type", "Symbol", "Quantity", "Price"])
        for txn in transactions:
            writer.writerow([
                txn.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                txn.type.capitalize(),
                txn.stock_symbol,
                txn.quantity,
                f"{txn.price:.2f}"
            ])

    return filepath


def generate_pdf_report(transactions: list[Transaction], user_email: str) -> BytesIO:
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Stock Transaction Report for {user_email}")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 100
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Date")
    p.drawString(150, y, "Type")
    p.drawString(220, y, "Symbol")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")
    y -= 20

    p.setFont("Helvetica", 10)
    for txn in transactions:
        if y < 40:
            p.showPage()
            y = height - 50
        p.drawString(50, y, txn.timestamp.strftime("%Y-%m-%d"))
        p.drawString(150, y, txn.type.capitalize())
        p.drawString(220, y, txn.stock_symbol)
        p.drawString(300, y, str(txn.quantity))
        p.drawString(350, y, f"{txn.price:.2f}")
        y -= 15

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer