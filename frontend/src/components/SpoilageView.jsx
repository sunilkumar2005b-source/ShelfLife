import { useState, useMemo } from "react";
import SpoilageSimulatorModal from "./SpoilageSimulatorModal";
import API_BASE from "../apiConfig";
import { DownloadIcon, SlidersIcon, RefreshIcon } from "./Icons";

export default function SpoilageView({ spoilage, inventory, onRefresh, showToast }) {
  const [filterRisk, setFilterRisk] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState("spoilage_probability");
  const [sortDirection, setSortDirection] = useState("desc");
  const [syncing, setSyncing] = useState(false);
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);

  const isTrained = spoilage.some((item) => item.model_name && item.model_name.includes("Trained ML"));

  const handleSync = async () => {
    try {
      setSyncing(true);
      const res = await fetch(`${API_BASE}/ml/sync-predictions`, { method: "POST" });
      if (res.ok) {
        if (onRefresh) await onRefresh();
        if (showToast) showToast("Live ML predictions recalculated for all batches!", "success");
      }
    } catch (err) {
      console.error("Sync error:", err);
      if (showToast) showToast("Failed to synchronize ML predictions", "warning");
    } finally {
      setSyncing(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const processedSpoilage = useMemo(() => {
    return spoilage
      .filter((item) => {
        const nameMatch = (item.product_name || "").toLowerCase().includes(searchTerm.toLowerCase());
        const riskMatch = filterRisk === "all" || (item.risk_level || "").toLowerCase() === filterRisk.toLowerCase();
        return nameMatch && riskMatch;
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
  }, [spoilage, searchTerm, filterRisk, sortField, sortDirection]);

  return (
    <>
      <div className="table-toolbar" style={{ justifyContent: "flex-end", marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 10 }}>
          <a
            href={`${API_BASE}/reports/spoilage-risk.csv`}
            download="shelflife_spoilage_risk.csv"
            className="btn btn-secondary"
            onClick={() => showToast && showToast("Exporting spoilage risk audit CSV...", "info")}
            style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
          >
            <DownloadIcon size={14} /> Export Risk CSV
          </a>
          <button
            className="btn btn-secondary"
            onClick={() => setIsSimulatorOpen(true)}
            style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
          >
            <SlidersIcon size={14} /> What-If Simulator
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSync}
            disabled={syncing}
            style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
          >
            <RefreshIcon size={14} className={syncing ? "spin-icon" : ""} />
            {syncing ? "Synchronizing ML..." : "Recalculate Predictions"}
          </button>
        </div>
      </div>

      {/* Model Attribution Banner */}
      <div className="demo-banner" style={{ background: isTrained ? "#f0fdf4" : undefined, borderColor: isTrained ? "#86efac" : undefined }}>
        <div>
          {isTrained ? (
            <>
              <strong style={{ color: "#166534" }}>Live ML Models Active:</strong> Degradation probabilities and risk tiers are evaluated by the trained <strong>Logistic Regression (scikit-learn)</strong> classifier (88.89% Test Accuracy, 96.03% High Spoilage Recall).
            </>
          ) : (
            <>
              <strong>Academic Demonstration Mode:</strong> Spoilage probabilities and risk classifications are currently sourced from <strong>Synthetic Demo Data</strong>.
            </>
          )}
        </div>
        <span className="demo-tag" style={{ background: isTrained ? "#dcfce7" : undefined, color: isTrained ? "#15803d" : undefined, borderColor: isTrained ? "#86efac" : undefined }}>
          {isTrained ? "Trained Logistic Model" : "Synthetic Demo Data"}
        </span>
      </div>

      {/* Risk Filter Buttons */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <button
          onClick={() => setFilterRisk("all")}
          className={`btn ${filterRisk === "all" ? "btn-primary" : "btn-secondary"}`}
          style={{ fontSize: 12.5, padding: "6px 14px" }}
        >
          All Risk Tiers ({spoilage.length})
        </button>
        <button
          onClick={() => setFilterRisk("high")}
          className={`btn ${filterRisk === "high" ? "btn-danger" : "btn-secondary"}`}
          style={{ fontSize: 12.5, padding: "6px 14px" }}
        >
          High Risk (&ge; 60%)
        </button>
        <button
          onClick={() => setFilterRisk("medium")}
          className={`btn ${filterRisk === "medium" ? "btn-primary" : "btn-secondary"}`}
          style={{
            fontSize: 12.5,
            padding: "6px 14px",
            background: filterRisk === "medium" ? "#d97706" : undefined,
            borderColor: filterRisk === "medium" ? "#d97706" : undefined,
          }}
        >
          Medium Risk (30-59%)
        </button>
        <button
          onClick={() => setFilterRisk("low")}
          className={`btn ${filterRisk === "low" ? "btn-primary" : "btn-secondary"}`}
          style={{ fontSize: 12.5, padding: "6px 14px" }}
        >
          Low Risk (&lt; 30%)
        </button>
      </div>

      <div className="section" style={{ marginTop: 0 }}>
        <div className="table-toolbar" style={{ marginBottom: 16 }}>
          <div style={{ position: "relative", width: 320, maxWidth: "100%" }}>
            <input
              type="text"
              className="search-input"
              placeholder="Search product title..."
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
                &times;
              </button>
            )}
          </div>

          <div style={{ fontSize: 13, color: "#64748b" }}>
            Showing <strong>{processedSpoilage.length}</strong> of {spoilage.length} predictions
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Batch / Prediction ID</th>
                <th className="sortable" onClick={() => handleSort("product_name")}>
                  Product Name {sortField === "product_name" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th>Category</th>
                <th className="sortable" onClick={() => handleSort("spoilage_probability")}>
                  Spoilage Probability {sortField === "spoilage_probability" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("risk_level")}>
                  Risk Tier {sortField === "risk_level" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th>Active Model</th>
                <th>Evaluation Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {processedSpoilage.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: "center", padding: 30, color: "#64748b" }}>
                    No spoilage records found matching the active filter.
                  </td>
                </tr>
              ) : (
                processedSpoilage.map((item) => {
                  const prob = item.spoilage_probability || 0;
                  const probPct = item.spoilage_probability_percent || Math.round(prob * 100);
                  const barColor = prob >= 0.6 ? "#ef4444" : prob >= 0.3 ? "#f59e0b" : "#10b981";

                  return (
                    <tr key={item.prediction_id || item.inventory_id}>
                      <td>
                        <code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: 4, fontSize: 12 }}>
                          PRED-#{item.prediction_id || item.inventory_id}
                        </code>
                      </td>
                      <td>
                        <strong style={{ color: "#0f172a" }}>{item.product_name}</strong>
                      </td>
                      <td>
                        <span style={{ fontSize: 12.5, color: "#475569" }}>{item.category}</span>
                      </td>
                      <td style={{ minWidth: 160 }}>
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <strong style={{ fontSize: 13, color: barColor }}>{probPct}%</strong>
                            <span style={{ fontSize: 11, color: "#64748b" }}>degradation</span>
                          </div>
                          <div style={{ width: "100%", height: 6, background: "#e2e8f0", borderRadius: 9999, overflow: "hidden" }}>
                            <div style={{ width: `${probPct}%`, height: "100%", background: barColor, borderRadius: 9999 }} />
                          </div>
                        </div>
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
                      <td>
                        <span className="badge badge-model">{item.model_name || "Logistic Regression"}</span>
                      </td>
                      <td style={{ fontSize: 12, color: "#64748b" }}>
                        {item.prediction_date ? item.prediction_date.slice(0, 19).replace("T", " ") : "Real-time"}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      <SpoilageSimulatorModal
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        showToast={showToast}
      />
    </>
  );
}
