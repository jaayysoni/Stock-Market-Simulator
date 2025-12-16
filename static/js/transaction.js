let transactions = [];

// ===== Helper Functions =====
function formatDateTime(dt) {
  if (!dt) return "-";
  const d = new Date(dt);
  return isNaN(d) ? dt : d.toLocaleString("en-IN", { hour12: false });
}

function groupByMonth(transactions) {
  return transactions.reduce((acc, tx) => {
    const t = tx.timestamp ? new Date(tx.timestamp) : new Date();
    const month = t.toLocaleString("en-IN", { month: "long", year: "numeric" });
    if (!acc[month]) acc[month] = [];
    acc[month].push(tx);
    return acc;
  }, {});
}

// ===== Render Transactions =====
function renderTransactions(filter = "", sort = "date-desc") {
  const container = document.getElementById("transactions-container");
  container.innerHTML = "";

  if (!transactions.length) {
    container.textContent = "No transactions yet.";
    return;
  }

  // Filter
  let filtered = transactions.filter(tx => {
    if (!filter) return true;
    return (
      (tx.crypto_symbol && tx.crypto_symbol.toLowerCase().includes(filter.toLowerCase())) ||
      tx.transaction_type.toLowerCase().includes(filter.toLowerCase())
    );
  });

  // Sort
  filtered.sort((a, b) => {
    if (sort === "date-desc") return new Date(b.timestamp) - new Date(a.timestamp);
    if (sort === "date-asc") return new Date(a.timestamp) - new Date(b.timestamp);
    if (sort === "crypto-asc") return (a.crypto_symbol || "").localeCompare(b.crypto_symbol || "");
    if (sort === "crypto-desc") return (b.crypto_symbol || "").localeCompare(a.crypto_symbol || "");
    return 0;
  });

  if (!filtered.length) {
    container.textContent = "No matching transactions.";
    return;
  }

  const grouped = groupByMonth(filtered);

  Object.keys(grouped).forEach(month => {
    const section = document.createElement("div");
    section.className = "month-section";
    section.innerHTML = `<div class="month-title">${month}</div>`;
    const table = document.createElement("table");
    table.className = "transaction-table";
    table.innerHTML = `<thead>
      <tr>
        <th>Type</th><th>Crypto / Details</th><th>Quantity / Amount</th><th>Price</th><th>Date & Time</th><th>Status</th>
      </tr>
    </thead>`;
    const tbody = document.createElement("tbody");

    grouped[month].forEach(tx => {
      const tr = document.createElement("tr");
      const type = tx.transaction_type?.toLowerCase() || "unknown";
      const priceVal = Number(tx.price) || null;
      const amtVal = Number(tx.amount) || null;

      let typeClass = "";
      let details = "";
      let quantityAmount = "";
      let price = "";

      switch (type) {
        case "buy":
          typeClass = "buy";
          details = tx.crypto_symbol || "-";
          quantityAmount = tx.quantity || "-";
          price = priceVal ? `₹${priceVal.toLocaleString("en-IN")}` : "-";
          break;
        case "sell":
          typeClass = "sell";
          details = tx.crypto_symbol || "-";
          quantityAmount = tx.quantity || "-";
          price = priceVal ? `₹${priceVal.toLocaleString("en-IN")}` : "-";
          break;
        case "money-add":
          typeClass = "money-add";
          details = "Money Added";
          quantityAmount = amtVal ? `₹${amtVal.toLocaleString("en-IN")}` : "-";
          price = "-";
          break;
        case "money-remove":
          typeClass = "money-remove";
          details = "Money Deducted";
          quantityAmount = amtVal ? `₹${amtVal.toLocaleString("en-IN")}` : "-";
          price = "-";
          break;
        default:
          details = tx.crypto_symbol || "-";
          quantityAmount = tx.quantity || "-";
          price = priceVal ? `₹${priceVal.toLocaleString("en-IN")}` : "-";
      }

      tr.innerHTML = `
        <td class="${typeClass}">${type.replace("-", " ")}</td>
        <td>${details}</td>
        <td>${quantityAmount}</td>
        <td>${price}</td>
        <td>${formatDateTime(tx.timestamp)}</td>
        <td>${tx.status || "completed"}</td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    section.appendChild(table);
    container.appendChild(section);
  });
}

// ===== Verify Login =====
async function verifyLogin() {
  try {
    const res = await fetch("/auth/me", {
      method: "GET",
      credentials: "include",
      headers: { "Accept": "application/json", "Cache-Control": "no-store" }
    });
    if (res.status === 401) {
      window.location.href = "/static/login.html";
      return false;
    }
    const user = await res.json();
    document.getElementById("userWelcome").textContent = `Welcome, ${user.email}`;
    return true;
  } catch (err) {
    console.error("Auth check error:", err);
    window.location.href = "/static/login.html";
    return false;
  }
}

// ===== Fetch Transactions =====
async function fetchTransactions() {
  const container = document.getElementById("transactions-container");
  container.innerHTML = `<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>`;

  try {
    const baseUrl = window.location.origin;
    const res = await fetch(`${baseUrl}/api/transactions`, {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: { "Accept": "application/json", "Cache-Control": "no-store" }
    });

    if (!res.ok) {
      if (res.status === 401) window.location.href = "/static/login.html";
      else container.textContent = "⚠️ Failed to load transactions.";
      return;
    }

    const data = await res.json().catch(() => []);
    console.log("Fetched transactions:", data);

    transactions = Array.isArray(data)
      ? data.map(tx => ({
          transaction_type: tx.transaction_type?.toLowerCase() || "unknown",
          crypto_symbol: tx.crypto_symbol || null,
          quantity: tx.quantity || null,
          price: tx.price || null,
          amount: tx.amount || null,
          timestamp: tx.timestamp,
          status: tx.status || "completed"
        }))
      : [];

    renderTransactions();
  } catch (err) {
    console.error("Failed to fetch transactions:", err);
    container.textContent = "⚠️ Failed to load transactions. Please try again.";
  }
}

// ===== Logout =====
function logout() {
  fetch("/auth/logout", { method: "POST", credentials: "include" })
    .finally(() => {
      document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      window.location.href = "/static/login.html";
    });
}

// ===== Search + Sort =====
document.getElementById("transaction-search").addEventListener("input", e => {
  renderTransactions(e.target.value, document.getElementById("transaction-sort").value);
});
document.getElementById("transaction-sort").addEventListener("change", e => {
  renderTransactions(document.getElementById("transaction-search").value, e.target.value);
});

// ===== Initial Load =====
(async () => {
  const loggedIn = await verifyLogin();
  if (loggedIn) {
    await fetchTransactions();
    setInterval(fetchTransactions, 30000);
  }
})();