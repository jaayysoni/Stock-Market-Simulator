/* ===============================
   Trading Terminal JS
   =============================== */

/* ========= CONFIG ========= */
const API_BASE = "/crypto";

/* ========= DOM ELEMENTS ========= */
const balanceEl = document.getElementById("balance");
const stockInput = document.getElementById("simStockInput");
const qtyInput = document.getElementById("simQtyInput");
const buyBtn = document.getElementById("buyBtn");
const sellBtn = document.getElementById("sellBtn");
const holdingsBody = document.getElementById("holdingsBody");
const tradesBody = document.getElementById("tradesBody");
const chartTitle = document.getElementById("chartTitle");
const chartContainer = document.getElementById("chartContainer"); // new container

/* ========= STATE ========= */
let balance = 100000;
let holdings = {
  BTCUSDT: { qty: 1, avgPrice: 42000 },
  ETHUSDT: { qty: 5, avgPrice: 2200 }
};
let trades = [];
let currentSymbol = null;
let currentRange = "1M";
let stockChart = null;

/* ===============================
   UTILITIES
   =============================== */
function formatDate(ts) {
  const d = new Date(ts);
  return d.toLocaleDateString();
}

function normalizeSymbol(symbol) {
  if (!symbol) return null;
  return symbol.toUpperCase().endsWith("USDT")
    ? symbol.toUpperCase()
    : symbol.toUpperCase() + "USDT";
}

function updateBalance() {
  balanceEl.textContent = "₹" + balance.toFixed(2);
}

/* ===============================
   CHART FUNCTIONS
   =============================== */
async function loadChart(symbol, range = "1M") {
  const normalized = normalizeSymbol(symbol);
  if (!normalized) return;

  currentSymbol = normalized;
  currentRange = range;
  chartTitle.textContent = `${currentSymbol} • ${range}`;

  try {
    const res = await fetch(
      `${API_BASE}/history?symbol=${currentSymbol}&time_range=${range}`
    );
    if (!res.ok) throw new Error("History not available");

    const data = await res.json();
    let candles = data.candles;

    // Fallback mock data
    if (!candles || candles.length === 0) {
      candles = Array.from({ length: 30 }, (_, i) => ({
        time: Date.now() - (29 - i) * 86400000,
        close: 100 + Math.random() * 20
      }));
    }

    const labels = candles.map(c => formatDate(c.time));
    const prices = candles.map(c => c.close);

    renderChart(labels, prices);
  } catch (err) {
    console.error(err);
    alert("Chart data not available");
  }
}

function renderChart(labels, prices) {
  const ctx = document.getElementById("stockChart").getContext("2d");

  if (stockChart) stockChart.destroy();

  stockChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Close Price",
          data: prices,
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.25,
          borderColor: "#00ff99",
          backgroundColor: "rgba(0, 255, 153, 0.1)"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false, // fills container height
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: {
          ticks: { color: "#c9d1d9" },
          grid: { color: "#30363d" }
        }
      }
    }
  });
}

/* ===============================
   HISTORY BUTTONS
   =============================== */
document.querySelectorAll(".history-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    if (!currentSymbol) return alert("Select a crypto first");
    loadChart(currentSymbol, btn.dataset.range);
  });
});

/* ===============================
   HOLDINGS & TRADES
   =============================== */
function renderHoldings() {
  holdingsBody.innerHTML = "";

  Object.keys(holdings).forEach(symbol => {
    const h = holdings[symbol];
    const row = document.createElement("tr");

    row.innerHTML = `
      <td class="clickable" data-symbol="${symbol}">${symbol}</td>
      <td>${h.qty}</td>
      <td>${h.avgPrice.toFixed(2)}</td>
      <td>—</td>
      <td class="profit">—</td>
      <td>
        <button class="sim-btn buy trade-btn" data-symbol="${symbol}">Trade</button>
      </td>
    `;

    holdingsBody.appendChild(row);
  });

  document.querySelectorAll(".clickable").forEach(el => {
    el.addEventListener("click", () => {
      stockInput.value = el.dataset.symbol;
      loadChart(el.dataset.symbol, "1D");
    });
  });
}

function renderTrades() {
  tradesBody.innerHTML = "";
  trades.forEach(tr => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${tr.time}</td>
      <td>${tr.symbol}</td>
      <td>${tr.action}</td>
      <td>${tr.qty}</td>
      <td>${tr.price}</td>
      <td class="${tr.pl >= 0 ? "profit" : "loss"}">${tr.pl.toFixed(2)}</td>
    `;
    tradesBody.appendChild(row);
  });
}

/* ===============================
   BUY / SELL
   =============================== */
function buyStock() {
  const symbol = normalizeSymbol(stockInput.value.trim());
  const qty = parseInt(qtyInput.value);
  if (!symbol || !qty) return alert("Invalid input");

  const price = 100;
  const cost = qty * price;

  if (balance < cost) return alert("Insufficient balance");

  balance -= cost;
  holdings[symbol] = holdings[symbol]
    ? {
        qty: holdings[symbol].qty + qty,
        avgPrice:
          ((holdings[symbol].avgPrice * holdings[symbol].qty) + cost) /
          (holdings[symbol].qty + qty)
      }
    : { qty, avgPrice: price };

  logTrade(symbol, "BUY", qty, price);
  updateBalance();
  renderHoldings();
}

function sellStock() {
  const symbol = normalizeSymbol(stockInput.value.trim());
  const qty = parseInt(qtyInput.value);

  if (!holdings[symbol] || holdings[symbol].qty < qty)
    return alert("Not enough holdings");

  const price = 100;
  balance += qty * price;
  holdings[symbol].qty -= qty;

  if (holdings[symbol].qty === 0) delete holdings[symbol];

  logTrade(symbol, "SELL", qty, price);
  updateBalance();
  renderHoldings();
}

function logTrade(symbol, action, qty, price) {
  trades.unshift({
    time: new Date().toLocaleTimeString(),
    symbol,
    action,
    qty,
    price,
    pl: 0
  });
  renderTrades();
}

/* ===============================
   EVENTS
   =============================== */
buyBtn.addEventListener("click", buyStock);
sellBtn.addEventListener("click", sellStock);

document.addEventListener("DOMContentLoaded", () => {
  updateBalance();
  renderHoldings();
  renderTrades();

  // 🔑 READ SYMBOL FROM URL
  const params = new URLSearchParams(window.location.search);
  const urlSymbol = params.get("symbol");

  loadChart(urlSymbol || "BTC", "1M");
});