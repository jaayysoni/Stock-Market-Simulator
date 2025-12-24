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