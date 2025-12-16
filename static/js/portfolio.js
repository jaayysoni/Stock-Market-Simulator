// portfolio.js

async function fetchPortfolio() {
    try {
        // Fetch portfolio holdings from backend
        const res = await fetch("/api/portfolio/holdings", {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("access_token")
            }
        });

        const data = await res.json();
        if (!data.holdings || data.holdings.length === 0) {
            document.getElementById("portfolio-body").innerHTML = `<tr><td colspan="6">No holdings yet.</td></tr>`;
            return;
        }

        const tbody = document.getElementById("portfolio-body");
        tbody.innerHTML = "";

        let totalQuantity = 0, totalInvestment = 0, totalCurrent = 0;

        data.holdings.forEach(item => {
            const totalInv = item.quantity * item.avg_price;
            const pl = item.live_price ? (item.live_price - item.avg_price) * item.quantity : 0;
            totalQuantity += item.quantity;
            totalInvestment += totalInv;
            totalCurrent += item.live_price ? item.live_price * item.quantity : totalInv;

            tbody.innerHTML += `
                <tr>
                    <td>${item.symbol}</td>
                    <td>${item.quantity}</td>
                    <td>₹${item.avg_price.toFixed(2)}</td>
                    <td>₹${totalInv.toFixed(2)}</td>
                    <td>₹${item.live_price ? item.live_price.toFixed(2) : '--'}</td>
                    <td class="${pl >= 0 ? 'profit' : 'loss'}">₹${pl.toFixed(2)}</td>
                </tr>
            `;
        });

        // Update totals in footer
        document.getElementById("sum-quantity").textContent = totalQuantity.toFixed(4);
        document.getElementById("sum-investment").textContent = `₹${totalInvestment.toFixed(2)}`;
        document.getElementById("sum-current").textContent = `₹${totalCurrent.toFixed(2)}`;
        const totalPL = totalCurrent - totalInvestment;
        const plElement = document.getElementById("sum-profit-loss");
        plElement.textContent = `₹${totalPL.toFixed(2)}`;
        plElement.className = totalPL >= 0 ? "profit" : "loss";

        // Update summary boxes
        const totalPLPercent = totalInvestment > 0 ? (totalPL / totalInvestment) * 100 : 0;
        const totalPLText = `₹${totalPL.toFixed(2)} (${totalPLPercent.toFixed(2)}%)`;
        document.getElementById("total-pl-amount").textContent = totalPLText;
        document.getElementById("total-pl-amount").className = totalPL >= 0 ? "profit" : "loss";

        // TODO: Update 24H P/L if your backend provides 24h change data
        document.getElementById("daily-pl-amount").textContent = "₹0.00 (+0.00%)";

    } catch (err) {
        console.error("Error fetching portfolio:", err);
    }
}

// Refresh portfolio every 30 seconds
fetchPortfolio();
setInterval(fetchPortfolio, 30000);