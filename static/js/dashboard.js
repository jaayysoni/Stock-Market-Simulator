// ===========================
// dashboard.js
// ===========================

const API_URL = "/crypto/prices"; // FastAPI endpoint returning top 90 cryptos

// ===== Market Overview coins mapping =====
const MARKET_OVERVIEW_COINS = [
    { idPrice: "bse-price", idChange: "bse-change", symbol: "BTC" },
    { idPrice: "nse-price", idChange: "nse-change", symbol: "ETH" },
    { idPrice: "banknifty-price", idChange: "banknifty-change", symbol: "DOGE" },
    { idPrice: "nifty50-price", idChange: "nifty50-change", symbol: "SHIB" },
];

// ===== Utility: format price dynamically based on value =====
function formatPrice(price) {
    if (price === null || price === undefined) return "--";

    price = parseFloat(price);

    if (price >= 1) {
        // For coins ≥ 1, show 2–4 decimals
        return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 });
    } else if (price >= 0.01) {
        // For coins ≥ 0.01, show 4–6 decimals
        return price.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 6 });
    } else {
        // For very small coins, show 6–8 decimals
        return price.toLocaleString(undefined, { minimumFractionDigits: 6, maximumFractionDigits: 8 });
    }
}

// ===== Create a crypto row =====
function createCryptoRow(rank, crypto) {
    const row = document.createElement("div");
    row.classList.add("crypto-row");

    const rankDiv = document.createElement("div");
    rankDiv.classList.add("rank");
    rankDiv.textContent = rank;

    const nameDiv = document.createElement("div");
    nameDiv.classList.add("name");
    nameDiv.textContent = crypto.name;

    const symbolDiv = document.createElement("div");
    symbolDiv.classList.add("symbol");
    symbolDiv.textContent = crypto.symbol;

    const priceDiv = document.createElement("div");
    priceDiv.classList.add("price");
    priceDiv.textContent = formatPrice(crypto.price);
    priceDiv.id = `price-${crypto.symbol}`;

    const changeDiv = document.createElement("div");
    changeDiv.classList.add("change");
    const changeVal = crypto.change ?? "0%";
    changeDiv.textContent = changeVal;
    changeDiv.classList.add(changeVal.startsWith("-") ? "negative" : "positive");
    changeDiv.id = `change-${crypto.symbol}`;

    row.append(rankDiv, nameDiv, symbolDiv, priceDiv, changeDiv);
    return row;
}

// ===== Render Top 90 crypto table =====
function renderCryptoTable(cryptos) {
    const container = document.getElementById("top-winners-body");
    if (!container) return;

    container.innerHTML = "";

    // Sort by market cap if available
    cryptos.sort((a, b) => (b.market_cap || 0) - (a.market_cap || 0));

    // Add header row
    const header = document.createElement("div");
    header.classList.add("crypto-row", "header");
    header.innerHTML = `
        <div class="rank">#</div>
        <div class="name">Name</div>
        <div class="symbol">Symbol</div>
        <div class="price">Price</div>
        <div class="change">24h %</div>
    `;
    container.appendChild(header);

    cryptos.forEach((crypto, index) => {
        const row = createCryptoRow(index + 1, crypto);
        container.appendChild(row);
    });
}

// ===== Update only prices and changes in Top 90 table =====
function updateCryptoTable(cryptos) {
    cryptos.forEach(crypto => {
        const priceEl = document.getElementById(`price-${crypto.symbol}`);
        const changeEl = document.getElementById(`change-${crypto.symbol}`);

        if (priceEl) priceEl.textContent = formatPrice(crypto.price);
        if (changeEl) {
            const changeVal = crypto.change ?? "0%";
            changeEl.textContent = changeVal;
            changeEl.classList.remove("positive", "negative");
            changeEl.classList.add(changeVal.startsWith("-") ? "negative" : "positive");
        }
    });
}

// ===== Update Market Overview cards =====
function updateMarketOverview(data) {
    MARKET_OVERVIEW_COINS.forEach(coin => {
        const coinData = data.find(c => c.symbol.toUpperCase() === coin.symbol);
        const priceEl = document.getElementById(coin.idPrice);
        const changeEl = document.getElementById(coin.idChange);

        if (coinData) {
            if (priceEl) priceEl.textContent = formatPrice(coinData.price);
            if (changeEl) {
                const changeVal = coinData.change ?? "0%";
                changeEl.textContent = changeVal;
                changeEl.classList.remove("positive", "negative");
                changeEl.classList.add(changeVal.startsWith("-") ? "negative" : "positive");
            }
        }
    });
}

// ===== Fetch crypto data =====
async function fetchCryptoPrices() {
    try {
        const res = await fetch(API_URL);
        const json = await res.json();
        if (!json.success || !json.data) return;

        const data = json.data;

        // Update Top 90 table
        const container = document.getElementById("top-winners-body");
        if (container && container.children.length === 0) {
            renderCryptoTable(data);
        } else {
            updateCryptoTable(data);
        }

        // Update Market Overview cards
        updateMarketOverview(data);

    } catch (err) {
        console.error("Error fetching crypto prices:", err);
    }
}

// ===== Poll every 3 seconds =====
setInterval(fetchCryptoPrices, 3000);

// ===== Initial fetch =====
fetchCryptoPrices();