let transactions = [];

// ===== Helper Functions =====
function formatDateTime(dt) {
  if (!dt) return "-";
  const d = new Date(dt);
  return isNaN(d) ? dt : d.toLocaleString("en-IN", { hour12: false });
}

function formatPriceUSD(price) {
  if (price === null || price === undefined) return "-";
  price = parseFloat(price);
  if (price >= 1) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  if (price >= 0.01) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 4 })}`;
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 6 })}`;
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
    container.textContent = "No transactions found.";
    return;
  }

  let filtered = transactions.filter(tx => {
    if (!filter) return true;
    return (
      (tx.crypto_symbol && tx.crypto_symbol.toLowerCase().includes(filter.toLowerCase())) ||
      tx.transaction_type.toLowerCase().includes(filter.toLowerCase())
    );
  });

  filtered.sort((a, b) => {
    if (sort === "date-desc") return new Date(b.timestamp) - new Date(a.timestamp);
    if (sort === "date-asc") return new Date(a.timestamp) - new Date(b.timestamp);
    if (sort === "crypto-asc") return (a.crypto_symbol || "").localeCompare(b.crypto_symbol || "");
    if (sort === "crypto-desc") return (b.crypto_symbol || "").localeCompare(a.crypto_symbol || "");
    return 0;
  });

  const grouped = groupByMonth(filtered);

  Object.keys(grouped).forEach(month => {
    const section = document.createElement("div");
    section.className = "month-section";
    section.innerHTML = `<div class="month-title">${month}</div>`;

    const table = document.createElement("table");
    table.className = "transaction-table";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Type</th>
          <th>Crypto</th>
          <th>Quantity / Amount</th>
          <th>Price</th>
          <th>Date & Time</th>
          <th>Status</th>
        </tr>
      </thead>
    `;

    const tbody = document.createElement("tbody");

    grouped[month].forEach(tx => {
      const type = tx.transaction_type ? tx.transaction_type.toUpperCase() : "UNKNOWN";
      const quantity = tx.quantity ?? tx.amount ?? "-";
      const price = tx.price ? formatPriceUSD(tx.price) : "-";

      // Assign class for color: green for BUY, red for SELL
      const typeClass = type === "BUY" ? "buy" : type === "SELL" ? "sell" : "";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="${typeClass}">${type}</td>
        <td>${tx.crypto_symbol || "-"}</td>
        <td>${quantity}</td>
        <td>${price}</td>
        <td>${formatDateTime(tx.timestamp)}</td>
        <td>${tx.status || "COMPLETED"}</td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    section.appendChild(table);
    container.appendChild(section);
  });
}

// ===== Fetch ALL Transactions (PUBLIC) =====
async function fetchTransactions() {
  const container = document.getElementById("transactions-container");
  container.innerHTML = "Loading transactions...";

  try {
    const res = await fetch("/api/transactions", {
      method: "GET",
      cache: "no-store",
      headers: { "Accept": "application/json" }
    });

    if (!res.ok) {
      container.textContent = "⚠️ Failed to load transactions.";
      return;
    }

    transactions = await res.json();
    renderTransactions();
  } catch (err) {
    console.error(err);
    container.textContent = "⚠️ Error loading transactions.";
  }
}

// ===== Search + Sort =====
document.getElementById("transaction-search").addEventListener("input", e => {
  renderTransactions(e.target.value, document.getElementById("transaction-sort").value);
});
document.getElementById("transaction-sort").addEventListener("change", e => {
  renderTransactions(document.getElementById("transaction-search").value, e.target.value);
});

// ===== Initial Load =====
fetchTransactions();
setInterval(fetchTransactions, 30000);