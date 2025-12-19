/* ===============================
   Live Binance WS + 1-Day 30-Minute Data
   Only Push If Price Changed + Throttle
   Page Auto-Reload Every 30 Seconds
   =============================== */

   const chartTitle = document.getElementById("chartTitle");
   const ctx = document.getElementById("stockChart").getContext("2d");
   
   let currentSymbol = "BTCUSDT";
   let stockChart = null;
   let labels = [];
   let prices = [];
   let latestPrice = null;
   let lastPushedPrice = null; // track last charted price
   const UPDATE_INTERVAL = 2000; // 2 seconds
   
   /* ===============================
      INIT CHART
      =============================== */
   function initChart() {
     stockChart = new Chart(ctx, {
       type: "line",
       data: {
         labels: labels,
         datasets: [{
           label: currentSymbol,
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
   
   /* ===============================
      FETCH 1-DAY 30-MINUTE DATA (01:00 → 24:00)
      =============================== */
   async function fetchThirtyMinData() {
     try {
       const url = `https://api.binance.com/api/v3/klines?symbol=${currentSymbol}&interval=30m&limit=48`;
       const resp = await fetch(url);
       const data = await resp.json();
   
       const today = new Date();
       today.setHours(0,0,0,0); // 00:00 today
   
       data.forEach(candle => {
         const time = new Date(candle[0]);
         // only include candles from 01:00 onwards
         if (time.getDate() === today.getDate() && time.getHours() >= 1) {
           const close = parseFloat(candle[4]);
           labels.push(time.toLocaleTimeString("en-IN", { hour12: false, hour:'2-digit', minute:'2-digit' }));
           prices.push(close);
         }
       });
   
       stockChart.update();
   
       if (prices.length) {
         chartTitle.textContent = `${currentSymbol} • LIVE PRICE: ₹${prices[prices.length - 1].toLocaleString("en-IN")}`;
         lastPushedPrice = prices[prices.length - 1]; // initialize last pushed price
       }
     } catch (err) {
       console.error("Error fetching 30-min data:", err);
     }
   }
   
   /* ===============================
      PUSH LATEST PRICE EVERY 2 SEC IF CHANGED
      =============================== */
   function startChartUpdater() {
     setInterval(() => {
       if (latestPrice !== null && latestPrice !== lastPushedPrice) {
         const now = new Date();
         labels.push(now.toLocaleTimeString("en-IN", { hour12: false, hour:'2-digit', minute:'2-digit' }));
         prices.push(latestPrice);
   
         if (prices.length > 100) {
           prices.shift();
           labels.shift();
         }
   
         stockChart.update();
         chartTitle.textContent = `${currentSymbol} • LIVE PRICE: ₹${latestPrice.toLocaleString("en-IN")}`;
         lastPushedPrice = latestPrice; // update last pushed
       }
     }, UPDATE_INTERVAL);
   }
   
   /* ===============================
      CONNECT TO BINANCE WS
      =============================== */
   function connectWS() {
     const ws = new WebSocket(`wss://stream.binance.com:9443/ws/btcusdt@trade`);
   
     ws.onopen = () => console.log("WebSocket connected");
     ws.onclose = () => {
       console.log("WebSocket disconnected, reconnecting in 3s...");
       setTimeout(connectWS, 3000);
     };
     ws.onerror = (err) => console.error("WebSocket error:", err);
   
     ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       const price = parseFloat(data.p);
       if (!isNaN(price)) {
         latestPrice = price; // update buffer
       }
     };
   }
   
   /* ===============================
      INIT
      =============================== */
   document.addEventListener("DOMContentLoaded", async () => {
     initChart();
     await fetchThirtyMinData(); // fetch historical 30-min closes from 01:00
     connectWS();                 // start live updates
     startChartUpdater();         // push to chart every 2 sec if changed
   
     // Auto-refresh the whole page every 30 seconds
     setTimeout(() => {
       window.location.reload();
     }, 30000);
   });