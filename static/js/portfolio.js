async function fetchPortfolio() {
    try {
        const res = await fetch("/api/portfolio/holdings");
        const data = await res.json();

        if (!data.holdings || data.holdings.length === 0) {
            document.getElementById("portfolio-body").innerHTML =
                `<tr><td colspan="7">No holdings yet.</td></tr>`;
            return;
        }

        const tbody = document.getElementById("portfolio-body");
        tbody.innerHTML = "";

        let totalQuantity = 0;
        let totalInvestment = 0;
        let totalCurrentValue = 0;

        data.holdings.forEach(item => {
            const totalInv = item.quantity * item.avg_price;
            const currentValue = item.live_price
                ? item.live_price * item.quantity
                : totalInv;
            const pl = currentValue - totalInv;

            totalQuantity += item.quantity;
            totalInvestment += totalInv;
            totalCurrentValue += currentValue;

            tbody.innerHTML += `
                <tr>
                    <td>${item.symbol}</td>
                    <td>${item.quantity.toFixed(6)}</td>
                    <td>₹${item.avg_price.toFixed(2)}</td>
                    <td>₹${totalInv.toFixed(2)}</td>
                    <td>${item.live_price ? `₹${item.live_price.toFixed(2)}` : '--'}</td>
                    <td>₹${currentValue.toFixed(2)}</td>
                    <td class="${pl >= 0 ? 'profit' : 'loss'}">₹${pl.toFixed(2)}</td>
                </tr>
            `;
        });

        // Totals row
        document.getElementById("sum-quantity").textContent =
            totalQuantity.toFixed(4);
        document.getElementById("sum-investment").textContent =
            `₹${totalInvestment.toFixed(2)}`;
        document.getElementById("sum-current").textContent =
            `₹${totalCurrentValue.toFixed(2)}`;

        const totalPL = totalCurrentValue - totalInvestment;
        const plElement = document.getElementById("sum-profit-loss");
        plElement.textContent = `₹${totalPL.toFixed(2)}`;
        plElement.className = totalPL >= 0 ? "profit" : "loss";

        // Summary box
        const totalPLPercent =
            totalInvestment > 0
                ? (totalPL / totalInvestment) * 100
                : 0;
        const summaryEl = document.getElementById("total-pl-amount");
        summaryEl.textContent =
            `₹${totalPL.toFixed(2)} (${totalPLPercent.toFixed(2)}%)`;
        summaryEl.className = totalPL >= 0 ? "profit" : "loss";

        // Daily P/L placeholder
        document.getElementById("daily-pl-amount").textContent =
            "₹0.00 (+0.00%)";

    } catch (err) {
        console.error("❌ Error fetching portfolio:", err);
    }
}

// Initial load + auto refresh
fetchPortfolio();
setInterval(fetchPortfolio, 30000);