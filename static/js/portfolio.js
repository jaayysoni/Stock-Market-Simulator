// ===== USD formatter =====
function formatUSD(value) {
    return "$" + Number(value).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// ===== Fetch portfolio =====
async function fetchPortfolio() {
    try {
        const res = await fetch("/api/portfolio/holdings");
        const data = await res.json();

        const tbody = document.getElementById("portfolio-body");

        if (!data.holdings || data.holdings.length === 0) {
            tbody.innerHTML =
                `<tr><td colspan="7">No holdings yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";

        let totalQuantity = 0;
        let totalInvestment = 0;
        let totalCurrentValue = 0;
        let dailyPLValue = 0;

        data.holdings.forEach(item => {
            const totalInv = item.quantity * item.avg_price;
            const currentValue = item.live_price
                ? item.live_price * item.quantity
                : totalInv;

            const pl = currentValue - totalInv;

            // 🔹 Daily P/L using 24h change %
            const changePercent = parseFloat(
                (item.change ?? "0").toString().replace("%", "")
            );

            const dailyPL = isNaN(changePercent)
                ? 0
                : (currentValue * changePercent) / 100;

            totalQuantity += item.quantity;
            totalInvestment += totalInv;
            totalCurrentValue += currentValue;
            dailyPLValue += dailyPL;

            // ===== Clickable row =====
            const tr = document.createElement("tr");
            tr.dataset.symbol = item.symbol;
            tr.classList.add("portfolio-row");

            tr.innerHTML = `
                <td>${item.symbol}</td>
                <td>${item.quantity.toFixed(6)}</td>
                <td>${formatUSD(item.avg_price)}</td>
                <td>${formatUSD(totalInv)}</td>
                <td>${item.live_price ? formatUSD(item.live_price) : "--"}</td>
                <td class="${pl >= 0 ? 'profit' : 'loss'}">${formatUSD(pl)}</td>
            `;

            tbody.appendChild(tr);
        });

        // ===== Totals =====
        document.getElementById("sum-quantity").textContent =
            totalQuantity.toFixed(4);

        document.getElementById("sum-investment").textContent =
            formatUSD(totalInvestment);

        document.getElementById("sum-current").textContent =
            formatUSD(totalCurrentValue);

        const totalPL = totalCurrentValue - totalInvestment;
        const plElement = document.getElementById("sum-profit-loss");
        plElement.textContent = formatUSD(totalPL);
        plElement.className = totalPL >= 0 ? "profit" : "loss";

        // ===== Summary (Total P/L) =====
        const totalPLPercent =
            totalInvestment > 0
                ? (totalPL / totalInvestment) * 100
                : 0;

        const summaryEl = document.getElementById("total-pl-amount");
        summaryEl.textContent =
            `${formatUSD(totalPL)} (${totalPLPercent.toFixed(2)}%)`;
        summaryEl.className = totalPL >= 0 ? "profit" : "loss";

        // ===== Summary (24H P/L) =====
        const dailyPLPercent =
            totalCurrentValue > 0
                ? (dailyPLValue / totalCurrentValue) * 100
                : 0;

        const dailyEl = document.getElementById("daily-pl-amount");
        dailyEl.textContent =
            `${formatUSD(dailyPLValue)} (${dailyPLPercent.toFixed(2)}%)`;
        dailyEl.className = dailyPLValue >= 0 ? "profit" : "loss";

    } catch (err) {
        console.error("❌ Error fetching portfolio:", err);
    }
}

// ===== Row click → Trading terminal =====
document.addEventListener("click", (e) => {
    const row = e.target.closest(".portfolio-row");
    if (!row) return;

    const symbol = row.dataset.symbol;
    if (!symbol) return;

    window.location.href =
        `/static/tradingterminal.html?symbol=${symbol}`;
});

// ===== Initial load + auto refresh =====
fetchPortfolio();
setInterval(fetchPortfolio, 30000);