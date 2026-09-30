import { useState, useMemo } from "react";

export default function IntelligenceView({ intelligenceData, summaryData, showToast }) {
  const [search, setSearch] = useState("");
  const [filterAction, setFilterAction] = useState("all");
  const [sortField, setSortField] = useState("health_score");
  const [sortDirection, setSortDirection] = useState("asc");

  // Summary counts
  const urgentCount = summaryData?.urgent_clearance ?? intelligenceData.filter((i) => i.recommendation === "Urgent Clearance").length;
  const sellQuicklyCount = summaryData?.sell_quickly ?? intelligenceData.filter((i) => i.recommendation === "Sell Quickly").length;
  const reorderCount = summaryData?.reorder ?? intelligenceData.filter((i) => i.recommendation === "Reorder").length;
  const monitorCount = summaryData?.monitor ?? intelligenceData.filter((i) => i.recommendation === "Monitor Stock").length;
  const sufficientCount = summaryData?.sufficient ?? intelligenceData.filter((i) => i.recommendation === "Sufficient Stock").length;

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const processedData = useMemo(() => {
    return intelligenceData
      .filter((item) => {
        const nameMatch = (item.product_name || "").toLowerCase().includes(search.toLowerCase());
        const actionSlug = (item.recommendation || "").toLowerCase().replace(/\s+/g, "-");
        const actionMatch = filterAction === "all" || actionSlug === filterAction;
        return nameMatch && actionMatch;
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
  }, [intelligenceData, search, filterAction, sortField, sortDirection]);

  return (
    <>
      <div className="table-toolbar">
        <div>
          <h2 className="page-title">Inventory Intelligence & Decision Engine</h2>
          <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: 13.5 }}>
            Automated multi-factor synthesis: stock levels, predicted demand, shelf life, and spoilage risk.
          </p>
        </div>
      </div>

      {/* 5 Recommendation Summary KPI Cards */}
      <div className="intelligence-summary" style={{ marginBottom: 20 }}>
        <div
          className={`intelligence-card urgent-summary ${filterAction === "urgent-clearance" ? "filter-active" : ""}`}
          onClick={() => {
            const next = filterAction === "urgent-clearance" ? "all" : "urgent-clearance";
            setFilterAction(next);
            if (showToast && next !== "all") showToast("Filtered to Urgent Clearance items", "info");
          }}
          title="Click to filter Urgent Clearance items"
        >
          <span>🚨</span>
          <div>
            <h3>Urgent Clearance</h3>
            <strong>{urgentCount}</strong>
          </div>
        </div>

        <div
          className={`intelligence-card sell-summary ${filterAction === "sell-quickly" ? "filter-active" : ""}`}
          onClick={() => {
            const next = filterAction === "sell-quickly" ? "all" : "sell-quickly";
            setFilterAction(next);
            if (showToast && next !== "all") showToast("Filtered to Sell Quickly items", "info");
          }}
          title="Click to filter Sell Quickly items"
        >
          <span>⚡</span>
          <div>
            <h3>Sell Quickly</h3>
            <strong>{sellQuicklyCount}</strong>
          </div>
        </div>

        <div
          className={`intelligence-card reorder-summary ${filterAction === "reorder" ? "filter-active" : ""}`}
          onClick={() => {
            const next = filterAction === "reorder" ? "all" : "reorder";
            setFilterAction(next);
            if (showToast && next !== "all") showToast("Filtered to Reorder items", "info");
          }}
          title="Click to filter Reorder items"
        >
          <span>📦</span>
          <div>
            <h3>Reorder Stock</h3>
            <strong>{reorderCount}</strong>
          </div>
        </div>

        <div
          className={`intelligence-card monitor-summary ${filterAction === "monitor-stock" ? "filter-active" : ""}`}
          onClick={() => {
            const next = filterAction === "monitor-stock" ? "all" : "monitor-stock";
            setFilterAction(next);
            if (showToast && next !== "all") showToast("Filtered to Monitor Stock items", "info");
          }}
          title="Click to filter Monitor Stock items"
        >
          <span>👀</span>
          <div>
            <h3>Monitor Stock</h3>
            <strong>{monitorCount}</strong>
          </div>
        </div>

        <div
          className={`intelligence-card sufficient-summary ${filterAction === "sufficient-stock" ? "filter-active" : ""}`}
          onClick={() => {
            const next = filterAction === "sufficient-stock" ? "all" : "sufficient-stock";
            setFilterAction(next);
            if (showToast && next !== "all") showToast("Filtered to Sufficient Stock items", "info");
          }}
          title="Click to filter Sufficient Stock items"
        >
          <span>✅</span>
          <div>
            <h3>Sufficient Stock</h3>
            <strong>{sufficientCount}</strong>
          </div>
        </div>
      </div>

      <div className="section" style={{ marginTop: 0 }}>
        <div className="table-toolbar" style={{ marginBottom: 16 }}>
          <div style={{ position: "relative", width: 320, maxWidth: "100%" }}>
            <input
              type="text"
              className="search-input"
              placeholder="🔍 Search product title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: "100%", paddingRight: search ? 32 : 14 }}
            />
            {search && (
              <button
                onClick={() => setSearch("")}
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

          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: "#64748b" }}>Action Filter:</label>
            <select
              className="select-filter"
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
            >
              <option value="all">All Recommendations ({intelligenceData.length})</option>
              <option value="urgent-clearance">🚨 Urgent Clearance ({urgentCount})</option>
              <option value="sell-quickly">⚡ Sell Quickly ({sellQuicklyCount})</option>
              <option value="reorder">📦 Reorder ({reorderCount})</option>
              <option value="monitor-stock">👀 Monitor Stock ({monitorCount})</option>
              <option value="sufficient-stock">✅ Sufficient Stock ({sufficientCount})</option>
            </select>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th className="sortable" onClick={() => handleSort("product_name")}>
                  Product {sortField === "product_name" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("days_remaining")}>
                  Days Left {sortField === "days_remaining" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("current_stock")}>
                  Current Stock {sortField === "current_stock" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("predicted_demand")}>
                  Projected Demand {sortField === "predicted_demand" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("risk_level")}>
                  Spoilage Risk {sortField === "risk_level" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("health_score")}>
                  Health Score {sortField === "health_score" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("recommendation")}>
                  Recommended Action {sortField === "recommendation" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th style={{ minWidth: 280 }}>Decision Rationale</th>
              </tr>
            </thead>
            <tbody>
              {processedData.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: "center", padding: 30, color: "#64748b" }}>
                    No inventory records match the selected action filter or search query.
                  </td>
                </tr>
              ) : (
                processedData.map((item) => {
                  const score = item.health_score || 0;
                  const isCritical = score < 40;
                  const isAttention = score >= 40 && score < 70;
                  const scoreColor = isCritical ? "#ef4444" : isAttention ? "#f59e0b" : "#10b981";

                  return (
                    <tr key={item.inventory_id}>
                      <td>
                        <strong style={{ color: "#0f172a" }}>{item.product_name}</strong>
                      </td>
                      <td>
                        <span style={{ fontWeight: 700, color: item.days_remaining <= 2 ? "#dc2626" : "#0f172a" }}>
                          {item.days_remaining} day{item.days_remaining === 1 ? "" : "s"}
                        </span>
                      </td>
                      <td>
                        <strong style={{ color: item.current_stock <= 10 ? "#dc2626" : "#0f172a" }}>
                          {item.current_stock}
                        </strong>{" "}
                        <span style={{ fontSize: 12, color: "#64748b" }}>units</span>
                      </td>
                      <td>
                        <span style={{ color: "#475569" }}>{item.predicted_demand} units</span>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            item.risk_level?.toLowerCase() === "high"
                              ? "badge-expired"
                              : item.risk_level?.toLowerCase() === "medium"
                              ? "badge-expiring"
                              : "badge-fresh"
                          }`}
                        >
                          {item.risk_level}
                        </span>
                      </td>
                      <td style={{ minWidth: 150 }}>
                        <div className="health-meter-container">
                          <strong style={{ fontSize: 13, color: scoreColor }}>{score}/100</strong>
                          <div className="meter-track">
                            <div
                              className="meter-fill"
                              style={{
                                width: `${score}%`,
                                background: scoreColor,
                              }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>
                        <span
                          className="badge"
                          style={{
                            fontWeight: 700,
                            background:
                              item.recommendation === "Urgent Clearance"
                                ? "#fef2f2"
                                : item.recommendation === "Sell Quickly"
                                ? "#fffbeb"
                                : item.recommendation === "Reorder"
                                ? "#f0f9ff"
                                : "#ecfdf5",
                            color:
                              item.recommendation === "Urgent Clearance"
                                ? "#991b1b"
                                : item.recommendation === "Sell Quickly"
                                ? "#92400e"
                                : item.recommendation === "Reorder"
                                ? "#075985"
                                : "#065f46",
                            border: `1px solid ${
                              item.recommendation === "Urgent Clearance"
                                ? "#fecaca"
                                : item.recommendation === "Sell Quickly"
                                ? "#fde68a"
                                : item.recommendation === "Reorder"
                                ? "#bae6fd"
                                : "#a7f3d0"
                            }`,
                          }}
                        >
                          {item.recommendation}
                        </span>
                      </td>
                      <td style={{ fontSize: 12.5, lineHeight: 1.5, color: "#334155" }}>
                        {item.ai_explanation || item.explanation}
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
