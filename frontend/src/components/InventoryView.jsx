import { useState, useMemo } from "react";

export default function InventoryView({ inventory, onOpenAddBatch, showToast }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortField, setSortField] = useState("daysRemaining");
  const [sortDirection, setSortDirection] = useState("asc"); // 'asc' or 'desc'

  const today = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  }, []);

  const enrichedInventory = useMemo(() => {
    return inventory.map((item) => {
      let daysRemaining = 0;
      let statusLabel = "Fresh";
      let badgeClass = "badge-fresh";

      if (item.expiry_date) {
        const exp = new Date(item.expiry_date.slice(0, 10));
        daysRemaining = Math.max(0, Math.ceil((exp.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)));

        if (daysRemaining === 0) {
          statusLabel = "Expired";
          badgeClass = "badge-expired";
        } else if (daysRemaining <= 2) {
          statusLabel = "Urgent";
          badgeClass = "badge-expired";
        } else if (daysRemaining <= 5) {
          statusLabel = "Expiring Soon";
          badgeClass = "badge-expiring";
        } else {
          statusLabel = "Good";
          badgeClass = "badge-fresh";
        }
      }

      return {
        ...item,
        daysRemaining,
        statusLabel,
        badgeClass,
      };
    });
  }, [inventory, today]);

  // Status counts for quick tabs
  const urgentCount = enrichedInventory.filter((i) => i.statusLabel === "Urgent").length;
  const expiringCount = enrichedInventory.filter((i) => i.statusLabel === "Expiring Soon").length;
  const goodCount = enrichedInventory.filter((i) => i.statusLabel === "Good").length;
  const expiredCount = enrichedInventory.filter((i) => i.statusLabel === "Expired").length;

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const processedInventory = useMemo(() => {
    return enrichedInventory
      .filter((item) => {
        const nameMatch =
          (item.product_name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
          (item.batch_number && item.batch_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
          (item.category && item.category.toLowerCase().includes(searchTerm.toLowerCase()));

        let filterMatch = true;
        if (statusFilter !== "all") {
          filterMatch = item.statusLabel.toLowerCase() === statusFilter.toLowerCase();
        }
        return nameMatch && filterMatch;
      })
      .sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];

        if (typeof valA === "string") valA = valA.toLowerCase();
        if (typeof valB === "string") valB = valB.toLowerCase();

        if (valA < valB) return sortDirection === "asc" ? -1 : 1;
        if (valA > valB) return sortDirection === "asc" ? 1 : -1;
        return 0;
      });
  }, [enrichedInventory, searchTerm, statusFilter, sortField, sortDirection]);

  return (
    <>
      <div className="table-toolbar">
        <div>
          <h2 className="page-title">Perishable Inventory Batches</h2>
          <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: 13.5 }}>
            Batch-level lifecycle tracking with cold-chain storage logging and expiry timelines.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <a
            href="http://127.0.0.1:8000/reports/inventory-audit.csv"
            download="shelflife_inventory_audit.csv"
            className="btn btn-secondary"
            onClick={() => showToast && showToast("Exporting inventory audit dataset...", "info")}
          >
            📥 Export Audit CSV
          </a>
          <button className="btn btn-primary" onClick={onOpenAddBatch}>
            + Add Inventory Batch
          </button>
        </div>
      </div>

      {/* Quick Filter Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <button
          onClick={() => setStatusFilter("all")}
          className={`btn ${statusFilter === "all" ? "btn-primary" : "btn-secondary"}`}
          style={{ fontSize: 12.5, padding: "6px 14px" }}
        >
          All Batches ({enrichedInventory.length})
        </button>
        <button
          onClick={() => setStatusFilter("urgent")}
          className={`btn ${statusFilter === "urgent" ? "btn-danger" : "btn-secondary"}`}
          style={{ fontSize: 12.5, padding: "6px 14px" }}
        >
          🚨 Urgent (≤2d) ({urgentCount})
        </button>
        <button
          onClick={() => setStatusFilter("expiring soon")}
          className={`btn ${statusFilter === "expiring soon" ? "btn-primary" : "btn-secondary"}`}
          style={{
            fontSize: 12.5,
            padding: "6px 14px",
            background: statusFilter === "expiring soon" ? "#d97706" : undefined,
            borderColor: statusFilter === "expiring soon" ? "#d97706" : undefined,
          }}
        >
          ⚠️ Expiring Soon ({expiringCount})
        </button>
        <button
          onClick={() => setStatusFilter("good")}
          className={`btn ${statusFilter === "good" ? "btn-primary" : "btn-secondary"}`}
          style={{ fontSize: 12.5, padding: "6px 14px" }}
        >
          ✅ Good Shelf Life ({goodCount})
        </button>
        {expiredCount > 0 && (
          <button
            onClick={() => setStatusFilter("expired")}
            className={`btn ${statusFilter === "expired" ? "btn-danger" : "btn-secondary"}`}
            style={{ fontSize: 12.5, padding: "6px 14px" }}
          >
            ❌ Expired ({expiredCount})
          </button>
        )}
      </div>

      <div className="section" style={{ marginTop: 0 }}>
        <div className="table-toolbar" style={{ marginBottom: 16 }}>
          <div style={{ position: "relative", width: 320, maxWidth: "100%" }}>
            <input
              type="text"
              className="search-input"
              placeholder="🔍 Search batch code or product name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: "100%", paddingRight: searchTerm ? 32 : 14 }}
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                style={{
                  position: "absolute",
                  right: 10,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  color: "#94a3b8",
                  fontSize: 14,
                }}
                title="Clear search"
              >
                ✕
              </button>
            )}
          </div>

          <div style={{ fontSize: 13, color: "#64748b" }}>
            Showing <strong>{processedInventory.length}</strong> of {enrichedInventory.length} records
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th className="sortable" onClick={() => handleSort("batch_number")}>
                  Batch Code {sortField === "batch_number" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("product_name")}>
                  Product {sortField === "product_name" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("category")}>
                  Category {sortField === "category" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("quantity")}>
                  Stock On-Hand {sortField === "quantity" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th>Purchase Date</th>
                <th className="sortable" onClick={() => handleSort("expiry_date")}>
                  Expiry Date {sortField === "expiry_date" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("storage_temperature")}>
                  Storage Temp {sortField === "storage_temperature" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("daysRemaining")}>
                  Days Left {sortField === "daysRemaining" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {processedInventory.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: "center", padding: 30, color: "#64748b" }}>
                    No inventory batches match your active search or filters.
                  </td>
                </tr>
              ) : (
                processedInventory.map((item) => {
                  const maxVisualDays = 15;
                  const barPct = Math.min(100, Math.max(10, Math.round((item.daysRemaining / maxVisualDays) * 100)));
                  const barColor = item.daysRemaining <= 2 ? "#ef4444" : item.daysRemaining <= 5 ? "#f59e0b" : "#10b981";

                  return (
                    <tr key={item.inventory_id}>
                      <td>
                        <code style={{ background: "#f1f5f9", padding: "3px 7px", borderRadius: 4, fontSize: 12, fontWeight: 600 }}>
                          {item.batch_number || `BATCH-${item.inventory_id}`}
                        </code>
                      </td>
                      <td>
                        <strong style={{ color: "#0f172a" }}>{item.product_name}</strong>
                      </td>
                      <td>
                        <span style={{ fontSize: 12.5, color: "#475569" }}>{item.category}</span>
                      </td>
                      <td>
                        <strong style={{ color: item.quantity <= 10 ? "#dc2626" : "#0f172a" }}>
                          {item.quantity}
                        </strong>{" "}
                        <span style={{ fontSize: 12, color: "#64748b" }}>units</span>
                      </td>
                      <td style={{ fontSize: 12.5, color: "#64748b" }}>{item.purchase_date || "—"}</td>
                      <td style={{ fontSize: 12.5, fontWeight: 600, color: "#334155" }}>{item.expiry_date}</td>
                      <td>
                        <span style={{ fontSize: 12.5, color: item.storage_temperature > 25 ? "#dc2626" : "#047857" }}>
                          {item.storage_temperature !== null && item.storage_temperature !== undefined
                            ? `${item.storage_temperature}°C`
                            : "Ambient"}
                        </span>
                      </td>
                      <td style={{ minWidth: 130 }}>
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                          <span style={{ fontWeight: 700, fontSize: 13, color: item.daysRemaining <= 2 ? "#dc2626" : "#0f172a" }}>
                            {item.daysRemaining} day{item.daysRemaining === 1 ? "" : "s"}
                          </span>
                          <div style={{ width: "100%", height: 5, background: "#e2e8f0", borderRadius: 9999, overflow: "hidden" }}>
                            <div style={{ width: `${barPct}%`, height: "100%", background: barColor, borderRadius: 9999 }} />
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${item.badgeClass}`}>
                          {item.statusLabel}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
