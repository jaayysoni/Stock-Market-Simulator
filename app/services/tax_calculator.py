def calculate_tax(sell_price: float, quantity: int) -> dict:
    gross_amount = sell_price * quantity

    # Simulated charges (based on average of Zerodha/Groww)
    stt = 0.001 * gross_amount
    stamp_duty = 0.00015 * gross_amount
    brokerage = 20.0  # flat fee per order
    gst = 0.18 * brokerage
    other_charges = 5.0  # miscellaneous exchange/SEBI charges

    total_tax = stt + stamp_duty + brokerage + gst + other_charges
    net_amount = gross_amount - total_tax

    return {
        "gross_amount": round(gross_amount, 2),
        "net_amount": round(net_amount, 2),
        "total_tax": round(total_tax, 2),
        "breakdown": {
            "STT": round(stt, 2),
            "Stamp Duty": round(stamp_duty, 2),
            "Brokerage": round(brokerage, 2),
            "GST": round(gst, 2),
            "Other Charges": round(other_charges, 2),
        }
    }