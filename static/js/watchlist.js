const API_BASE = "/api/watchlist";

// ✅ Fetch full watchlist
async function loadWatchlist() {
    try {
        const res = await fetch(`${API_BASE}/full`);
        const data = await res.json();

        const table = document.getElementById("watchlistTable");
        table.innerHTML = "";

        if (data.length === 0) {
            table.innerHTML = `<tr class="empty-state"><td colspan="4">No stocks added yet.</td></tr>`;
            return;
        }

        data.forEach(item => {
            table.innerHTML += `
                <tr>
                    <td>${item.symbol}</td>
                    <td>${item.stock_name || "Loading..."}</td>
                    <td>${item.current_price !== null ? item.current_price : "Updating..."}</td>
                    <td><span class="remove-btn" onclick="removeStock('${item.symbol}')">✖</span></td>
                </tr>
            `;
        });

    } catch (err) {
        console.error("Error loading watchlist:", err);
    }
}

// ✅ Add stock to watchlist
document.getElementById("addForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const symbol = document.getElementById("stockSymbol").value.trim().toUpperCase();
    if (!symbol) return;

    try {
        const res = await fetch(API_BASE + "/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol })
        });

        if (res.ok) {
            loadWatchlist();
            document.getElementById("stockSymbol").value = "";
        } else {
            const errData = await res.json();
            alert(errData.detail || "Error adding stock");
        }

    } catch (err) {
        console.error("Add error:", err);
    }
});

// ✅ Remove stock
async function removeStock(symbol) {
    if (!confirm(`Remove ${symbol} from watchlist?`)) return;

    try {
        const res = await fetch(`${API_BASE}/${symbol}`, { method: "DELETE" });
        if (res.status === 204) {
            loadWatchlist();
        } else {
            alert("Error removing stock");
        }
    } catch (err) {
        console.error("Remove error:", err);
    }
}

// ✅ Load on start
window.onload = loadWatchlist;