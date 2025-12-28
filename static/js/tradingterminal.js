/* ==========================================================
   Trading Terminal — Binance Chart (FINAL, SYMBOL-SAFE)
   - URL symbol is authoritative
   - No double USDT mapping
   - Safe DOM init
   - Chart.js guaranteed
   - REST candles + Live WS
   ========================================================== */

   let chartTitle;
   let ctx;
   let stockChart = null;
   
   let labels = [];
   let prices = [];
   
   let currentSymbol = "BTCUSDT";
   let latestPrice = null;
   let lastPushedPrice = null;
   
   let ws = null;
   let BINANCE_WS_URL = "wss://stream.binance.com:9443";
   const UPDATE_INTERVAL = 2000;
   
   // ================= SYMBOL HANDLING =================
   
   function normalizeSymbol(symbol) {
     if (!symbol) return "BTCUSDT";
     symbol = symbol.toUpperCase();
     return symbol.endsWith("USDT") ? symbol : `${symbol}USDT`;
   }
   
   function getSymbolFromURL() {
     const params = new URLSearchParams(window.location.search);
     return normalizeSymbol(params.get("symbol"));
   }
   
   // ================= BACKEND CONFIG =================
   
   async function fetchWSUrl() {
     try {
       const res = await fetch("/crypto/config/ws-url");
       if (!res.ok) throw new Error("WS config fetch failed");
       const json = await res.json();
       if (json.ws_url) BINANCE_WS_URL = json.ws_url;
       console.log("✔ WS URL:", BINANCE_WS_URL);
     } catch {
       console.warn("⚠ Using fallback WS URL");
     }
   }
   
   // ================= CHART INIT =================
   
   function initChart() {
     stockChart = new Chart(ctx, {
       type: "line",
       data: {
         labels,
         datasets: [{
           label: currentSymbol.replace("USDT", ""),
           data: prices,
           borderWidth: 2,
           tension: 0.3,
           pointRadius: 2,
           borderColor: "#00ff99",
           backgroundColor: "rgba(0,255,153,0.1)",
           fill: true
         }]
       },
       options: {
         responsive: true,
         maintainAspectRatio: false,
         plugins: { legend: { display: false } },
         scales: {
           x: { ticks: { color: "#c9d1d9" }, grid: { color: "#30363d" } },
           y: { ticks: { color: "#c9d1d9" }, grid: { color: "#30363d" } }
         }
       }
     });
   }
   
   // ================= HISTORICAL DATA =================
   
   async function fetchThirtyMinData(symbol) {
     try {
       console.log("📡 Fetching candles:", symbol);
   
       const resp = await fetch(
         `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=30m&limit=48`
       );
       if (!resp.ok) throw new Error("Klines fetch failed");
   
       const data = await resp.json();
   
       labels.length = 0;
       prices.length = 0;
   
       data.forEach(candle => {
         const time = new Date(candle[0]);
         labels.push(
           time.toLocaleTimeString("en-IN", {
             hour12: false,
             hour: "2-digit",
             minute: "2-digit"
           })
         );
         prices.push(parseFloat(candle[4]));
       });
   
       if (!prices.length) return;
   
       latestPrice = prices[prices.length - 1];
       lastPushedPrice = latestPrice;
   
       stockChart.data.datasets[0].label = symbol.replace("USDT", "");
       stockChart.update();
   
       chartTitle.textContent =
         `${symbol.replace("USDT", "")} • LIVE PRICE: ₹${latestPrice.toLocaleString("en-IN")}`;
   
     } catch (err) {
       console.error("❌ Candle fetch error:", err);
     }
   }
   
   // ================= LIVE UPDATER =================
   
   function startChartUpdater() {
     setInterval(() => {
       if (
         latestPrice === null ||
         latestPrice === lastPushedPrice ||
         !stockChart
       ) return;
   
       const now = new Date();
       labels.push(
         now.toLocaleTimeString("en-IN", {
           hour12: false,
           hour: "2-digit",
           minute: "2-digit"
         })
       );
       prices.push(latestPrice);
   
       if (prices.length > 100) {
         prices.shift();
         labels.shift();
       }
   
       stockChart.update();
   
       chartTitle.textContent =
         `${currentSymbol.replace("USDT", "")} • LIVE PRICE: ₹${latestPrice.toLocaleString("en-IN")}`;
   
       lastPushedPrice = latestPrice;
     }, UPDATE_INTERVAL);
   }
   
   // ================= BINANCE WS =================
   
   function connectWS(symbol) {
     if (ws) ws.close();
   
     ws = new WebSocket(`${BINANCE_WS_URL}/ws/${symbol.toLowerCase()}@trade`);
   
     ws.onopen = () => console.log("🔗 WS connected:", symbol);
   
     ws.onmessage = event => {
       const data = JSON.parse(event.data);
       const price = parseFloat(data.p);
       if (!isNaN(price)) latestPrice = price;
     };
   
     ws.onerror = err => console.error("❌ WS error:", err);
   
     ws.onclose = () => {
       console.warn("⚠ WS disconnected, reconnecting...");
       setTimeout(() => connectWS(symbol), 3000);
     };
   }
   
   // ================= INIT =================
   
   document.addEventListener("DOMContentLoaded", async () => {
     console.log("🚀 Trading Terminal loaded");
   
     chartTitle = document.getElementById("chartTitle");
     const canvas = document.getElementById("stockChart");
   
     if (!canvas) {
       console.error("❌ Canvas #stockChart not found");
       return;
     }
   
     canvas.style.height = "400px";
     ctx = canvas.getContext("2d");
   
     if (typeof Chart === "undefined") {
       console.error("❌ Chart.js not loaded");
       return;
     }
   
     // 🔒 LOCK SYMBOL FROM URL
     currentSymbol = getSymbolFromURL();
     console.log("🔐 Locked symbol:", currentSymbol);
   
     await fetchWSUrl();
     initChart();
     await fetchThirtyMinData(currentSymbol);
     connectWS(currentSymbol);
     startChartUpdater();
   });

// ===========================
// Virtual Balance (Dashboard)
// ===========================

async function loadVirtualBalance() {
  try {
      const res = await fetch("/api/balance"); // ✅ correct API
      if (!res.ok) throw new Error("Failed to fetch balance: " + res.status);

      const data = await res.json();
      const balanceEl = document.getElementById("balance");

      if (balanceEl) {
          const balance = typeof data.balance === "number" ? data.balance : 0;
          balanceEl.textContent =
              "₹ " + balance.toLocaleString("en-IN", { minimumFractionDigits: 2 });
      }
  } catch (err) {
      console.error("Failed to load balance:", err);
      const balanceEl = document.getElementById("balance");
      if (balanceEl) balanceEl.textContent = "₹ --";
  }
}

// Initial load
document.addEventListener("DOMContentLoaded", () => {
  loadVirtualBalance();

  // Refresh balance every 5 seconds
  setInterval(loadVirtualBalance, 5000);
});


// showing holding using portfolio api from main.py 
/* =================================================
   TRADING TERMINAL – HOLDINGS (PORTFOLIO API)
   Reference: portfolio.js
   ================================================= */

   async function fetchHoldings() {
    try {
      const res = await fetch("/api/portfolio/holdings");
      if (!res.ok) throw new Error("API error");
  
      const data = await res.json();
      const tbody = document.getElementById("holdingsBody");
      tbody.innerHTML = "";
  
      if (!data.holdings || data.holdings.length === 0) {
        tbody.innerHTML = `<tr>
        <td colspan="5" style="text-align:center; opacity:0.7;">
          No trades yet.
        </td>
      </tr>`;
        return;
      }
  
      data.holdings.forEach(item => {
        const qty = Number(item.quantity) || 0;
        const avgPrice = Number(item.avg_price) || 0;
        const livePrice =
          item.live_price !== null && item.live_price !== undefined
            ? Number(item.live_price)
            : null;

        tbody.innerHTML += `
          <tr>
            <td>${item.symbol}</td>
            <td>${qty.toFixed(6)}</td>
            <td>₹${formatPrice(avgPrice)}</td>
            <td>${livePrice !== null ? `₹${formatPrice(livePrice)}` : "--"}</td>
          </tr>
        `;
      });
  
    } catch (err) {
      console.error("❌ Error fetching holdings:", err);
    }
  }
  function formatPrice(price) {
    if (price === null || price === undefined) return "--";
  
    if (price >= 1) return price.toFixed(2);          // BTC, ETH, SOL
    if (price >= 0.01) return price.toFixed(4);       // mid-priced tokens
    return price.toFixed(8);                           // SHIB, PEPE, etc
  }
  /* -------------------------------
     QUICK TRADE FROM HOLDINGS
  -------------------------------- */
  function quickTrade(symbol, side) {
    const stockInput = document.getElementById("simStockInput");
    const qtyInput = document.getElementById("simQtyInput");
  
    stockInput.value = symbol;
    qtyInput.focus();
  
    if (side === "BUY") {
      document.getElementById("buyBtn").click();
    } else {
      document.getElementById("sellBtn").click();
    }
  }
  
  /* -------------------------------
     INITIAL LOAD + AUTO REFRESH
  -------------------------------- */
  document.addEventListener("DOMContentLoaded", () => {
    fetchHoldings();
    setInterval(fetchHoldings, 5000); // trading terminal refresh
  });

/* =================================================
   BUY / SELL FRONTEND INTEGRATION (FULL)
   ================================================= */

   document.addEventListener("DOMContentLoaded", () => {
    const buyBtn = document.getElementById("buyBtn");
    const sellBtn = document.getElementById("sellBtn");
    const qtyInput = document.getElementById("simQtyInput");
    const stockInput = document.getElementById("simStockInput");
  
    // 🔒 Lock crypto input from URL
    stockInput.value = currentSymbol.replace("USDT", "");
    stockInput.disabled = true;
  
    buyBtn.addEventListener("click", () => executeOrder("BUY"));
    sellBtn.addEventListener("click", () => executeOrder("SELL"));
  });
  
  async function executeOrder(side) {
    const qtyInput = document.getElementById("simQtyInput");
    const quantity = parseFloat(qtyInput.value);
  
    if (!quantity || quantity <= 0) {
      alert("❌ Enter a valid quantity");
      return;
    }
  
    if (!currentSymbol) {
      alert("❌ Symbol not detected");
      return;
    }
  
    const endpoint = side === "BUY" ? "/api/order/buy" : "/api/order/sell";
  
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: currentSymbol,
          quantity: quantity
        })
      });
  
      const data = await res.json();
  
      if (!res.ok) {
        alert("❌ " + (data.error || data.detail?.[0]?.msg || "Order failed"));
        return;
      }
  
      // ✅ SUCCESS: Show alert
      alert(
        `✅ ${side} ORDER EXECUTED\n\n` +
        `Symbol: ${data.symbol}\n` +
        `Qty: ${data.quantity}\n` +
        `Price: ₹${data.price.toLocaleString("en-IN")}\n` +
        `${side === "BUY" ? `Spent: ₹${data.spent.toLocaleString("en-IN")}` : `Received: ₹${data.received.toLocaleString("en-IN")}`}`
      );
  
      // Clear input
      qtyInput.value = "";
  
      // 🔄 Refresh all relevant data
      loadVirtualBalance();
      fetchHoldings();
      fetchTodaysTrades();
  
    } catch (err) {
      console.error("Order error:", err);
      alert("❌ Server error");
    }
  }
  
  /* =================================================
     FETCH TODAY'S TRADES (Optional)
     ================================================= */
  async function fetchTodaysTrades() {
    try {
      const res = await fetch("/api/transactions"); // make sure your API endpoint returns today's transactions
      if (!res.ok) throw new Error("Failed to fetch trades");
      const data = await res.json();
  
      const tbody = document.getElementById("tradesBody");
      tbody.innerHTML = "";
  
      if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; opacity:0.7;">No trades yet.</td></tr>`;
        return;
      }
  
      data.forEach(tx => {
        const pl = tx.profit_loss ?? 0;
        const plClass = pl >= 0 ? "profit" : "loss";
  
        tbody.innerHTML += `
          <tr>
            <td>${new Date(tx.timestamp).toLocaleString("en-IN", { hour12: false })}</td>
            <td>${tx.crypto_symbol}</td>
            <td>${tx.transaction_type}</td>
            <td>${tx.quantity}</td>
            <td>₹${tx.price.toLocaleString("en-IN")}</td>
          </tr>`;
      });
    } catch (err) {
      console.error("Error fetching today's trades:", err);
    }
  }
  
  // Initial load for today's trades
  document.addEventListener("DOMContentLoaded", fetchTodaysTrades);



  // Virtual balance update 

document.addEventListener("DOMContentLoaded", () => {
    const balanceEl = document.getElementById("balance");
    const balanceInput = document.getElementById("balanceInput");
    const addBtn = document.getElementById("addFundsBtn");
    const removeBtn = document.getElementById("removeFundsBtn");

    // ===== Load balance from backend =====
    async function loadBalance() {
        try {
            const res = await fetch("/api/balance");
            const data = await res.json();
            if (res.ok) {
                balanceEl.textContent = `₹${data.balance.toLocaleString("en-IN")}`;
            } else {
                console.error("Failed to fetch balance:", data);
            }
        } catch (err) {
            console.error("Error loading balance:", err);
        }
    }

    // ===== Update balance (Add/Remove Funds) =====
    async function updateBalance(action) {
        const amount = parseFloat(balanceInput.value);
        if (!amount || amount <= 0) {
            alert("❌ Enter a valid amount");
            return;
        }

        try {
            const res = await fetch("/api/balance/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action, amount })
            });
            const data = await res.json();

            if (!res.ok) {
                alert("❌ " + (data.error || "Failed to update balance"));
                return;
            }

            alert(`✅ Balance updated: ₹${data.balance.toLocaleString("en-IN")}`);
            balanceInput.value = "";
            loadBalance();
        } catch (err) {
            console.error("Error updating balance:", err);
            alert("❌ Server error");
        }
    }

    // ===== Event Listeners for Add/Remove =====
    addBtn.addEventListener("click", () => updateBalance("add"));
    removeBtn.addEventListener("click", () => updateBalance("remove"));

    // ===== Buy/Sell Integration =====
    const buyBtn = document.getElementById("buyBtn");
    const sellBtn = document.getElementById("sellBtn");
    const qtyInput = document.getElementById("simQtyInput");
    const stockInput = document.getElementById("simStockInput");

    if (typeof currentSymbol !== "undefined") {
        stockInput.value = currentSymbol.replace("USDT", "");
        stockInput.disabled = true;
    }

    async function executeOrder(side) {
        const quantity = parseFloat(qtyInput.value);
        const symbol = stockInput.value.toUpperCase();

        if (!quantity || quantity <= 0) {
            alert("❌ Enter a valid quantity");
            return;
        }
        if (!symbol) {
            alert("❌ Symbol not detected");
            return;
        }

        const endpoint = side === "BUY" ? "/api/order/buy" : "/api/order/sell";

        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbol: symbol + "USDT", quantity })
            });

            const data = await res.json();

            if (!res.ok) {
                alert("❌ " + (data.error || "Order failed"));
                return;
            }

            alert(
                `✅ ${side} ORDER EXECUTED\n` +
                `Symbol: ${data.symbol}\n` +
                `Qty: ${data.quantity}\n` +
                `Price: ₹${data.price.toLocaleString("en-IN")}\n` +
                `Balance: ₹${data.balance.toLocaleString("en-IN")}`
            );

            qtyInput.value = "";

            // Refresh balance and holdings
            loadBalance();
            if (typeof fetchHoldings === "function") fetchHoldings();

        } catch (err) {
            console.error("Order error:", err);
            alert("❌ Server error");
        }
    }

    // ===== Initial Load =====
    loadBalance();
});