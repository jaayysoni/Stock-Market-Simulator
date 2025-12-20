/* ===============================
   Live Binance WS + 1-Day 30-Minute Data
   Dynamic Crypto Selection
   Only Push If Price Changed + Throttle
   Page Auto-Reload Every 30 Seconds (symbol preserved)
   Fetch WS URL from backend .env
   =============================== */

   const chartTitle = document.getElementById("chartTitle");
   const ctx = document.getElementById("stockChart").getContext("2d");
   
   // ===== UTILITY: Convert universal symbol → Binance symbol =====
   function toBinanceSymbol(symbol) {
     if (!symbol) return "BTCUSDT";
     symbol = symbol.toUpperCase();
     if (symbol.endsWith("USDT")) return symbol; // already a pair
     return `${symbol}USDT`; // map universal → Binance
   }
   
   // ===== GET SYMBOL FROM URL =====
   function getSymbolFromURL() {
     const params = new URLSearchParams(window.location.search);
     return toBinanceSymbol(params.get("symbol"));
   }
   
   let currentSymbol = getSymbolFromURL() || "BTCUSDT";
   let BINANCE_WS_URL = "wss://stream.binance.com:9443"; // fallback
   
   let stockChart = null;
   let labels = [];
   let prices = [];
   let latestPrice = null;
   let lastPushedPrice = null;
   
   const UPDATE_INTERVAL = 2000; // 2 seconds
   let ws = null;
   
   // ===== FETCH WS URL FROM BACKEND =====
   async function fetchWSUrl() {
     try {
       const res = await fetch("/crypto/config/ws-url");
       const json = await res.json();
       if (json.ws_url) BINANCE_WS_URL = json.ws_url;
       console.log("Using Binance WS URL:", BINANCE_WS_URL);
     } catch (err) {
       console.error("Failed to fetch WS URL, using fallback:", err);
     }
   }
   
   // ===== INIT CHART =====
   function initChart() {
     stockChart = new Chart(ctx, {
       type: "line",
       data: {
         labels: labels,
         datasets: [{
           label: currentSymbol.replace("USDT", ""),
           data: prices,
           borderWidth: 2,
           tension: 0.25,
           pointRadius: 2,
           borderColor: "#00ff99",
           backgroundColor: "rgba(0,255,153,0.1)"
         }]
       },
       options: {
         responsive: true,
         maintainAspectRatio: false,
         plugins: { legend: { display: false } },
         scales: {
           x: { grid: { color: "#30363d" }, ticks: { color: "#c9d1d9" } },
           y: { grid: { color: "#30363d" }, ticks: { color: "#c9d1d9" } }
         }
       }
     });
   }
   
   // ===== FETCH 1-DAY 30-MIN DATA =====
   async function fetchThirtyMinData(symbol) {
     try {
       const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=30m&limit=48`;
       const resp = await fetch(url);
       const data = await resp.json();
   
       labels = [];
       prices = [];
       lastPushedPrice = null;
   
       const today = new Date();
       today.setHours(0, 0, 0, 0);
   
       data.forEach(candle => {
         const time = new Date(candle[0]);
         if (time.getDate() === today.getDate()) {
           const close = parseFloat(candle[4]);
           labels.push(
             time.toLocaleTimeString("en-IN", { hour12: false, hour: "2-digit", minute: "2-digit" })
           );
           prices.push(close);
         }
       });
   
       stockChart.data.labels = labels;
       stockChart.data.datasets[0].label = symbol.replace("USDT", "");
       stockChart.data.datasets[0].data = prices;
       stockChart.update();
   
       if (prices.length) {
         latestPrice = prices[prices.length - 1];
         lastPushedPrice = latestPrice;
         chartTitle.textContent = `${symbol.replace("USDT", "")} • LIVE PRICE: ₹${latestPrice.toLocaleString("en-IN")}`;
       }
   
     } catch (err) {
       console.error("Error fetching 30-min data:", err);
     }
   }
   
   // ===== LIVE PRICE PUSH (THROTTLED) =====
   function startChartUpdater() {
     setInterval(() => {
       if (latestPrice !== null && latestPrice !== lastPushedPrice) {
         const now = new Date();
         const slot = now.toLocaleTimeString("en-IN", { hour12: false, hour: "2-digit", minute: "2-digit" });
   
         labels.push(slot);
         prices.push(latestPrice);
   
         if (prices.length > 100) {
           prices.shift();
           labels.shift();
         }
   
         stockChart.update();
         chartTitle.textContent = `${currentSymbol.replace("USDT", "")} • LIVE PRICE: ₹${latestPrice.toLocaleString("en-IN")}`;
         lastPushedPrice = latestPrice;
       }
     }, UPDATE_INTERVAL);
   }
   
   // ===== BINANCE WEBSOCKET =====
   function connectWS(symbol) {
     if (ws) ws.close();
   
     ws = new WebSocket(`${BINANCE_WS_URL}/ws/${symbol.toLowerCase()}@trade`);
   
     ws.onopen = () => console.log(`WebSocket connected for ${symbol}`);
     ws.onclose = () => {
       console.log(`WebSocket disconnected for ${symbol}, reconnecting...`);
       setTimeout(() => connectWS(symbol), 3000);
     };
     ws.onerror = err => console.error("WebSocket error:", err);
   
     ws.onmessage = event => {
       const data = JSON.parse(event.data);
       const price = parseFloat(data.p);
       if (!isNaN(price)) latestPrice = price;
     };
   }
   
   // ===== SYMBOL SWITCH (OPTIONAL INTERNAL USE) =====
   async function changeSymbol(symbol) {
     currentSymbol = toBinanceSymbol(symbol);
     await fetchThirtyMinData(currentSymbol);
     connectWS(currentSymbol);
   }
   
   // ===== INIT =====
   document.addEventListener("DOMContentLoaded", async () => {
     await fetchWSUrl();           // fetch WS URL from backend first
     initChart();
     await fetchThirtyMinData(currentSymbol);
     connectWS(currentSymbol);
     startChartUpdater();
   
     // ✅ Auto-reload but KEEP symbol
     setTimeout(() => {
       window.location.href = `/trade?symbol=${currentSymbol.replace("USDT","")}`;
     }, 30000);
   });