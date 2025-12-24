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

    if (price >= 1) {
        return price.toLocaleString(undefined, { minimumFractionDigits: 2 });
    }
    if (price >= 0.01) {
        return price.toLocaleString(undefined, { minimumFractionDigits: 4 });
    }
    return price.toLocaleString(undefined, { minimumFractionDigits: 6 });
}

// ===== Create row =====
function createCryptoRow(rank, crypto) {
    const symbol = baseSymbol(crypto.symbol);

    const row = document.createElement("div");
    row.className = "crypto-row";
    row.dataset.symbol = crypto.symbol; // BTCUSDT for trade

    // Always use crypto.name from API if available
    const displayName = crypto.name?.trim() ? crypto.name : symbol;

    row.innerHTML = `
        <div class="rank">${rank}</div>
        <div class="name">${displayName}</div>
        <div class="symbol">${symbol}</div>
        <div class="price" id="price-${symbol}">${formatPrice(crypto.price)}</div>
        <div class="change ${crypto.change?.startsWith("-") ? "negative" : "positive"}"
             id="change-${symbol}">
             ${crypto.change ?? "0%"}
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

    // Sort cryptos by price descending
    const sortedCryptos = cryptos.sort((a, b) => (b.price || 0) - (a.price || 0));

    sortedCryptos.forEach((c, i) => {
        container.appendChild(createCryptoRow(i + 1, c));
    });
}

// ===== Market Overview =====
function updateMarketOverview(data) {
    MARKET_OVERVIEW_COINS.forEach(coin => {
        const item = data.find(
            d => baseSymbol(d.symbol) === coin.symbol
        );

        if (!item) return;

        document.getElementById(coin.idPrice).textContent =
            formatPrice(item.price);

        const ch = document.getElementById(coin.idChange);
        ch.textContent = item.change ?? "0%";
        ch.className = `change ${
            item.change?.startsWith("-") ? "negative" : "positive"
        }`;
    });
}

// ===== Fetch & render (always sorted) =====
async function fetchCryptoPrices() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();
        if (!data?.length) return;

        // Always re-render to maintain sorting
        renderCryptoTable(data);
        updateMarketOverview(data);
    } catch (e) {
        console.error("Fetch error:", e);
    }
}

// ===== Poll every 3 seconds =====
fetchCryptoPrices();
setInterval(fetchCryptoPrices, 3000);

// ===== Row click for trading =====
document.addEventListener("click", (e) => {
    const row = e.target.closest(".crypto-row");
    if (!row) return;
  
    const symbol = row.dataset.symbol; // BTCUSDT, ETHUSDT, etc.
  
    window.location.href = `/static/tradingterminal.html?symbol=${symbol}`;
  });