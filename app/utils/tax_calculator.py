# app/utils/tax_calculator.py

def calculate_tax_summary(transactions: list[dict]) -> dict:
    """
    Simulate average tax on capital gains.
    :param transactions: List of transaction dictionaries.
    :return: Dict with profit, loss, net, tax
    """
    profit = 0.0
    loss = 0.0

    for tx in transactions:
        if tx["transaction_type"] == "sell":
            sell_total = tx["price"] * tx["quantity"]
            avg_buy_price = tx.get("average_price", 0)
            buy_total = avg_buy_price * tx["quantity"]
            diff = sell_total - buy_total

            if diff > 0:
                profit += diff
            else:
                loss += abs(diff)

    net_gain = profit - loss
    tax_rate = 0.15  # flat 15% simulated tax
    tax = max(0.0, net_gain * tax_rate)

    return {
        "profit": round(profit, 2),
        "loss": round(loss, 2),
        "net_gain": round(net_gain, 2),
        "tax": round(tax, 2)
    }