// ===========================
// dashboard.js (FIXED + Sorted by Price)
// ===========================

const API_URL = "/dashboard/prices";

// ===== Market Overview coins =====
const MARKET_OVERVIEW_COINS = [
    { idPrice: "bse-price", idChange: "bse-change", symbol: "BTC" },
    { idPrice: "nse-price", idChange: "nse-change", symbol: "ETH" },
    { idPrice: "banknifty-price", idChange: "banknifty-change", symbol: "DOGE" },
    { idPrice: "nifty50-price", idChange: "nifty50-change", symbol: "SHIB" },
];

// ===== Helpers =====
const baseSymbol = (binanceSymbol) =>
    binanceSymbol?.replace("USDT", "").toUpperCase();

// ===== Price formatter =====
function formatPrice(price) {
    if (price === null || price === undefined) return "--";
    price = parseFloat(price);

    let formatted;
    if (price >= 1) {
        formatted = price.toLocaleString(undefined, { minimumFractionDigits: 2 });
    } else if (price >= 0.01) {
        formatted = price.toLocaleString(undefined, { minimumFractionDigits: 4 });
    } else {
        formatted = price.toLocaleString(undefined, { minimumFractionDigits: 6 });
    }

    return `$${formatted}`;
}

// ===== Percentage formatter (REQUIRED) =====
function formatChange(change) {
    if (change === null || change === undefined) return "0%";

    let value = change.toString().trim();
    value = value.replace("%", "");

    const num = parseFloat(value);
    if (isNaN(num)) return "0%";

    return `${num.toFixed(2)}%`;
}

// ===== Create row =====
function createCryptoRow(rank, crypto) {
    const symbol = baseSymbol(crypto.symbol);

    const row = document.createElement("div");
    row.className = "crypto-row";
    row.dataset.symbol = crypto.symbol;

    const displayName = crypto.name?.trim() ? crypto.name : symbol;

    row.innerHTML = `
        <div class="rank">${rank}</div>
        <div class="name">${displayName}</div>
        <div class="symbol">${symbol}</div>
        <div class="price">${formatPrice(crypto.price)}</div>
        <div class="change ${crypto.change?.startsWith("-") ? "negative" : "positive"}">
            ${formatChange(crypto.change)}
        </div>
    `;

    return row;
}

// ===== Render Top 90 sorted by price =====
function renderCryptoTable(cryptos) {
    const container = document.getElementById("top-winners-body");
    if (!container) return;

    container.innerHTML = "";

    const header = document.createElement("div");
    header.className = "crypto-row header";
    header.innerHTML = `
        <div class="rank">#</div>
        <div class="name">Name</div>
        <div class="symbol">Symbol</div>
        <div class="price">Price</div>
        <div class="change">24h %</div>
    `;
    container.appendChild(header);

    const sortedCryptos = cryptos.sort((a, b) => (b.price || 0) - (a.price || 0));

    sortedCryptos.forEach((c, i) => {
        container.appendChild(createCryptoRow(i + 1, c));
    });
}

// ===== Market Overview =====
function updateMarketOverview(data) {
    MARKET_OVERVIEW_COINS.forEach(coin => {
        const item = data.find(d => baseSymbol(d.symbol) === coin.symbol);
        if (!item) return;

        document.getElementById(coin.idPrice).textContent =
            formatPrice(item.price);

        const ch = document.getElementById(coin.idChange);
        ch.textContent = formatChange(item.change);
        ch.className = `change ${
            item.change?.startsWith("-") ? "negative" : "positive"
        }`;
    });
}

// ===== Fetch & render =====
async function fetchCryptoPrices() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();
        if (!data?.length) return;

        renderCryptoTable(data);
        updateMarketOverview(data);
    } catch (e) {
        console.error("Fetch error:", e);
    }
}

fetchCryptoPrices();
setInterval(fetchCryptoPrices, 3000);

// ===== Row click for trading =====
document.addEventListener("click", (e) => {
    const row = e.target.closest(".crypto-row");
    if (!row || row.classList.contains("header")) return;

    const symbol = row.dataset.symbol;
    if (!symbol) return;

    window.location.href = `/static/tradingterminal.html?symbol=${symbol}`;
});

// ===========================
// Virtual Balance (Dashboard)
// ===========================

async function loadVirtualBalance() {
    try {
        const res = await fetch("/api/balance");
        if (!res.ok) throw new Error(res.status);

        const data = await res.json();
        const balanceEl = document.getElementById("balance");

        if (balanceEl) {
            const balance = typeof data.balance === "number" ? data.balance : 0;
            balanceEl.textContent =
                "$" + balance.toLocaleString(undefined, { minimumFractionDigits: 2 });
        }
    } catch (err) {
        const balanceEl = document.getElementById("balance");
        if (balanceEl) balanceEl.textContent = "$ --";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadVirtualBalance();
    setInterval(loadVirtualBalance, 5000);
});




// ===== Search Top 90 Cryptos (works with auto-refresh) =====
function attachCryptoSearch() {
    const searchInput = document.getElementById("search-input");
    const container = document.getElementById("top-winners-body");

    if (!searchInput || !container) return;

    // This function applies the filter based on current input
    const applyFilter = () => {
        const query = searchInput.value.trim().toLowerCase();
        const rows = container.querySelectorAll(".crypto-row:not(.header)");

        rows.forEach(row => {
            const name = row.querySelector(".name").textContent.toLowerCase();
            const symbol = row.querySelector(".symbol").textContent.toLowerCase();

            row.style.display = (name.includes(query) || symbol.includes(query)) ? "" : "none";
        });
    };

    // Trigger filtering on input
    searchInput.addEventListener("input", applyFilter);

    // Also re-apply filter after each table render
    // Override your renderCryptoTable to include this
    const originalRender = window.renderCryptoTable;
    window.renderCryptoTable = function(cryptos) {
        originalRender(cryptos); // render table as usual
        applyFilter();            // then apply current search filter
    };
}

// Call this once
attachCryptoSearch();





// ===== Market Overview Card Clicks =====
function attachMarketOverviewClicks() {
    const cards = document.querySelectorAll(".index-card");

    cards.forEach(card => {
        card.style.cursor = "pointer"; // indicate it's clickable

        card.addEventListener("click", () => {
            const symbol = card.dataset.symbol; // get symbol from data-attribute
            if (!symbol) return;

            // Map symbols from your overview to real trading symbols
            const symbolMap = {
                "BSE": "BTC",
                "NSE": "ETH",
                "BANKNIFTY": "DOGE",
                "NIFTY50": "SHIB"
            };

            const tradingSymbol = symbolMap[symbol] || symbol;
            window.location.href = `/static/tradingterminal.html?symbol=${tradingSymbol}`;
        });
    });
}

// Attach after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    attachMarketOverviewClicks();
});