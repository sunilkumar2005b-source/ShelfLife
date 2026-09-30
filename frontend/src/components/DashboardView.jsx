import { useState, useEffect } from "react";
import ClearanceSimulatorModal from "./ClearanceSimulatorModal";

export default function DashboardView({
  products,
  inventory,
  spoilage,
  forecasts,
  intelligenceData,
  onNavigate,
  onRefresh,
  showToast,
}) {
  const [financialData, setFinancialData] = useState(null);
  const [activeScenario, setActiveScenario] = useState("normal");
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [isClearanceModalOpen, setIsClearanceModalOpen] = useState(false);

  const loadFinancialData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/reports/financial-risk");
      if (res.ok) {
        const data = await res.json();
        setFinancialData(data);
      }
    } catch (err) {
      console.error("Failed to load financial risk data:", err);
    }
  };

  useEffect(() => {
    loadFinancialData();
  }, [inventory, spoilage]);

  const handleApplyScenario = async (scenario, label) => {
    try {
      setScenarioLoading(true);
      setActiveScenario(scenario);
      const res = await fetch("http://127.0.0.1:8000/demo/apply-scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario }),
      });
      if (res.ok) {
        if (onRefresh) await onRefresh();
        await loadFinancialData();
        if (showToast) {
          showToast(`Applied "${label}" scenario! Inventory and ML models updated.`, "info");
        }
      }
    } catch (err) {
      console.error("Failed to apply demo scenario:", err);
      if (showToast) {
        showToast("Failed to apply demo scenario", "warning");
      }
    } finally {
      setScenarioLoading(false);
    }
  };

  // 1. Total products
  const totalProducts = products.length;

  // 2. Total stock units
  const totalStock = inventory.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0);

  // 3. Expiring products (<= 3 days)
  const expiringProducts = inventory.filter((item) => {
    if (!item.expiry_date) return false;
    const exp = new Date(item.expiry_date.slice(0, 10));
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffDays = Math.ceil((exp.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays <= 3;
  }).length;

  // 4. Spoilage risk breakdown
  const highRisk = spoilage.filter(
    (item) => String(item.risk_level).toLowerCase() === "high"
  ).length;

  const mediumRisk = spoilage.filter(
    (item) => String(item.risk_level).toLowerCase() === "medium"
  ).length;

  const lowRisk = spoilage.filter(
    (item) => String(item.risk_level).toLowerCase() === "low"
  ).length;

  const totalRiskBatches = highRisk + mediumRisk + lowRisk || 1;
  const highRiskPct = Math.round((highRisk / totalRiskBatches) * 100);
  const medRiskPct = Math.round((mediumRisk / totalRiskBatches) * 100);
  const lowRiskPct = Math.round((lowRisk / totalRiskBatches) * 100);

  // 5. Low-stock products
  const lowStockProducts = intelligenceData.filter(
    (item) => item.current_stock < item.predicted_demand || item.current_stock <= 10
  ).length;

  // 6. Overall inventory health average
  const avgHealth = intelligenceData.length > 0
    ? Math.round(intelligenceData.reduce((acc, i) => acc + (i.health_score || 0), 0) / intelligenceData.length)
    : 85;

  // Critical Attention Items
  const attentionProducts = intelligenceData.filter(
    (item) =>
      item.risk_level?.toLowerCase() === "high" ||
      item.recommendation === "Urgent Clearance" ||
      item.recommendation === "Sell Quickly"
  );

  return (
    <>
      {/* Faculty Demonstration Scenario Presets Command Bar */}
      <div className="scenario-bar">
        <div className="scenario-header">
          <span style={{ fontSize: 24 }}>🎓</span>
          <div>
            <div className="scenario-title">Faculty Live Demo Presets</div>
            <div className="scenario-desc">
              Inject dynamic environmental & retail stress events to test live ML adaptation:
            </div>
          </div>
        </div>

        <div className="scenario-btn-group">
          <button
            onClick={() => handleApplyScenario("normal", "Standard Baseline")}
            disabled={scenarioLoading}
            className={`scenario-btn ${activeScenario === "normal" ? "active" : ""}`}
            title="Standard operating conditions (22°C ambient, balanced stock)"
          >
            ☀️ Standard Baseline
          </button>
          <button
            onClick={() => handleApplyScenario("heatwave", "Heatwave Crisis (41.5°C)")}
            disabled={scenarioLoading}
            className={`scenario-btn ${activeScenario === "heatwave" ? "active" : ""}`}
            style={activeScenario === "heatwave" ? { background: "#dc2626", borderColor: "#f87171" } : {}}
            title="Elevates ambient temp to 41.5°C, accelerating perishable degradation"
          >
            🔥 Heatwave (41.5°C)
          </button>
          <button
            onClick={() => handleApplyScenario("urgent_clearance", "Imminent Expiration Wave")}
            disabled={scenarioLoading}
            className={`scenario-btn ${activeScenario === "urgent_clearance" ? "active" : ""}`}
            style={activeScenario === "urgent_clearance" ? { background: "#d97706", borderColor: "#fbbf24" } : {}}
            title="Advances expiry dates to within 24-48 hours"
          >
            ⚡ Urgent Clearance
          </button>
          <button
            onClick={() => handleApplyScenario("stockout_crisis", "Demand Surge & Stockout")}
            disabled={scenarioLoading}
            className={`scenario-btn ${activeScenario === "stockout_crisis" ? "active" : ""}`}
            style={activeScenario === "stockout_crisis" ? { background: "#7c3aed", borderColor: "#a78bfa" } : {}}
            title="Triples projected demand to trigger emergency restock rules"
          >
            📉 Stockout Crisis
          </button>
        </div>
      </div>

      {/* Toolbar / Header */}
      <div className="table-toolbar">
        <div>
          <h2 className="page-title">Executive Retail Intelligence Command Center</h2>
          <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: 13.5 }}>
            Automated monitoring of perishable capital, predictive spoilage, and rule-based decision support.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            className="btn btn-secondary"
            onClick={() => setIsClearanceModalOpen(true)}
            title="Simulate clearance markdowns to rescue revenue"
          >
            💰 Markdown Simulator
          </button>
          <button
            className="btn btn-primary"
            onClick={() => onNavigate("intelligence")}
            title="Open comprehensive rule engine table"
          >
            Open Decision Engine &rarr;
          </button>
        </div>
      </div>

      {/* 6 Key Stat Cards */}
      <div className="cards">
        <div className="card" onClick={() => onNavigate("products")} style={{ cursor: "pointer" }} title="View all catalog items">
          <h3>Cataloged Perishables</h3>
          <p>{totalProducts}</p>
        </div>

        <div className="card" onClick={() => onNavigate("inventory")} style={{ cursor: "pointer" }} title="View physical batch stock">
          <h3>Total Physical Stock</h3>
          <p>{totalStock.toLocaleString()} <span style={{ fontSize: 15, color: "#64748b", fontWeight: 500 }}>units</span></p>
        </div>

        <div
          className="card"
          onClick={() => onNavigate("inventory")}
          style={{ cursor: "pointer", borderLeftColor: expiringProducts > 0 ? "#ef4444" : "#10b981" }}
          title="Batches within 3 days of expiration"
        >
          <h3>Expiring Soon (≤3 Days)</h3>
          <p style={{ color: expiringProducts > 0 ? "#dc2626" : "#059669" }}>
            {expiringProducts}
          </p>
        </div>

        <div className="card high-card" onClick={() => onNavigate("spoilage")} style={{ cursor: "pointer" }} title="Logistic regression high-risk batches">
          <h3>High Spoilage Risk</h3>
          <p>{highRisk}</p>
        </div>

        <div className="card medium-card" onClick={() => onNavigate("intelligence")} style={{ cursor: "pointer" }} title="Items below safe reorder thresholds">
          <h3>Low Stock / Restock</h3>
          <p>{lowStockProducts}</p>
        </div>

        <div className="card" onClick={() => onNavigate("intelligence")} style={{ cursor: "pointer" }} title="Composite inventory freshness score">
          <h3>Composite Health</h3>
          <p style={{ color: avgHealth >= 70 ? "#059669" : avgHealth >= 45 ? "#d97706" : "#dc2626" }}>
            {avgHealth}%
          </p>
        </div>
      </div>

      {/* Financial Valuation & Perishable Waste Exposure (Section 9) */}
      {financialData && (
        <div className="financial-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
            <div>
              <div style={{ fontSize: 11.5, letterSpacing: "0.6px", textTransform: "uppercase", color: "#a7f3d0", fontWeight: 700 }}>
                Financial Exposure & Capital Preservation
              </div>
              <h3 style={{ margin: "2px 0 0", fontSize: 18, color: "#ffffff", fontWeight: 800 }}>
                Perishable Portfolio Valuation & Waste Risk
              </h3>
            </div>
            <button
              className="btn"
              onClick={() => setIsClearanceModalOpen(true)}
              style={{
                background: "rgba(255, 255, 255, 0.15)",
                color: "#ffffff",
                border: "1px solid rgba(255, 255, 255, 0.25)",
                fontSize: 12.5,
              }}
            >
              ⚡ Run Clearance Salvage Model
            </button>
          </div>

          <div className="financial-grid">
            <div className="financial-metric">
              <h4>Total Cost Valuation</h4>
              <p>₹{financialData.total_inventory_cost_valuation?.toLocaleString()}</p>
              <div style={{ fontSize: 11.5, color: "#a7f3d0", marginTop: 4 }}>
                Potential Retail: ₹{financialData.total_retail_potential_revenue?.toLocaleString()}
              </div>
            </div>

            <div className="financial-metric" style={{ borderColor: "rgba(239, 68, 68, 0.4)", background: "rgba(239, 68, 68, 0.1)" }}>
              <h4 style={{ color: "#fca5a5" }}>Capital at Spoilage Risk</h4>
              <p style={{ color: "#fecaca" }}>₹{financialData.capital_at_high_risk?.toLocaleString()}</p>
              <div style={{ fontSize: 11.5, color: "#fca5a5", marginTop: 4 }}>
                {financialData.capital_at_risk_percentage}% of total stock value
              </div>
            </div>

            <div className="financial-metric" style={{ borderColor: "rgba(245, 158, 11, 0.4)", background: "rgba(245, 158, 11, 0.1)" }}>
              <h4 style={{ color: "#fde68a" }}>Projected Profit Loss</h4>
              <p style={{ color: "#fef3c7" }}>₹{financialData.projected_lost_retail_margin?.toLocaleString()}</p>
              <div style={{ fontSize: 11.5, color: "#fde68a", marginTop: 4 }}>
                Unrecovered margin if unsold
              </div>
            </div>

            <div className="financial-metric" style={{ borderColor: "rgba(16, 185, 129, 0.4)", background: "rgba(16, 185, 129, 0.1)" }}>
              <h4 style={{ color: "#6ee7b7" }}>Salvageable Capital</h4>
              <p style={{ color: "#a7f3d0" }}>
                ₹{Math.round(financialData.capital_at_high_risk * 0.65).toLocaleString()}
              </p>
              <div style={{ fontSize: 11.5, color: "#6ee7b7", marginTop: 4 }}>
                Via dynamic clearance pricing
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Spoilage Risk Distribution with Visual Proportion Bar */}
      <div className="section">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <div>
            <h2 style={{ margin: 0 }}>Spoilage Risk Distribution</h2>
            <p style={{ margin: "2px 0 0", color: "#64748b", fontSize: 13 }}>
              Supervised Logistic Regression classification across current perishable inventory
            </p>
          </div>
          <span className="badge badge-fresh">88.89% Test Accuracy</span>
        </div>

        {/* Multi-segment visual bar */}
        <div style={{ width: "100%", height: 10, background: "#e2e8f0", borderRadius: 9999, overflow: "hidden", display: "flex", margin: "14px 0" }}>
          <div style={{ width: `${highRiskPct}%`, background: "#ef4444" }} title={`High Risk: ${highRiskPct}%`} />
          <div style={{ width: `${medRiskPct}%`, background: "#f59e0b" }} title={`Medium Risk: ${medRiskPct}%`} />
          <div style={{ width: `${lowRiskPct}%`, background: "#10b981" }} title={`Low Risk: ${lowRiskPct}%`} />
        </div>

        <div className="cards" style={{ marginBottom: 0, gridTemplateColumns: "repeat(3, 1fr)" }}>
          <div className="card high-card" onClick={() => onNavigate("spoilage")} style={{ cursor: "pointer" }}>
            <h3>High Risk Tier (≥60% Prob)</h3>
            <p>{highRisk} <span style={{ fontSize: 14, color: "#64748b" }}>({highRiskPct}%)</span></p>
          </div>
          <div className="card medium-card" onClick={() => onNavigate("spoilage")} style={{ cursor: "pointer" }}>
            <h3>Medium Risk Tier (30-59%)</h3>
            <p>{mediumRisk} <span style={{ fontSize: 14, color: "#64748b" }}>({medRiskPct}%)</span></p>
          </div>
          <div className="card" onClick={() => onNavigate("spoilage")} style={{ cursor: "pointer", borderLeftColor: "#10b981" }}>
            <h3>Low Risk Tier (&lt;30%)</h3>
            <p style={{ color: "#059669" }}>{lowRisk} <span style={{ fontSize: 14, color: "#64748b" }}>({lowRiskPct}%)</span></p>
          </div>
        </div>
      </div>

      {/* Immediate Attention & Inventory Intelligence */}
      <div className="section">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h2 style={{ margin: 0 }}>Priority Attention Queue</h2>
            <p style={{ margin: "2px 0 0", color: "#64748b", fontSize: 13 }}>
              Batches flagged for immediate intervention (imminent expiry or high degradation probability)
            </p>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <a
              href="http://127.0.0.1:8000/reports/inventory-audit.csv"
              download="shelflife_inventory_audit.csv"
              className="btn btn-secondary"
              onClick={() => showToast && showToast("Downloading complete inventory audit CSV...", "info")}
              style={{ fontSize: 12 }}
            >
              📥 Export Audit CSV
            </a>
            <button className="btn btn-primary" onClick={() => onNavigate("intelligence")} style={{ fontSize: 12 }}>
              Inspect All Batches &rarr;
            </button>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Current Stock</th>
                <th>Days to Expiry</th>
                <th>Spoilage Prob</th>
                <th>Risk Tier</th>
                <th>Rule Recommendation</th>
                <th>Quick Action</th>
              </tr>
            </thead>
            <tbody>
              {attentionProducts.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: "center", color: "#64748b", padding: 25 }}>
                    ✅ All inventory batches are currently healthy with no urgent actions required.
                  </td>
                </tr>
              ) : (
                attentionProducts.map((item) => (
                  <tr key={item.inventory_id}>
                    <td><strong>{item.product_name}</strong></td>
                    <td>{item.current_stock} units</td>
                    <td>
                      <span className={`badge ${item.days_remaining <= 2 ? "badge-expired" : "badge-expiring"}`}>
                        {item.days_remaining} day(s) left
                      </span>
                    </td>
                    <td>
                      <strong>
                        {item.spoilage_probability_percent || Math.round((item.spoilage_probability || 0) * 100)}%
                      </strong>
                    </td>
                    <td>
                      <span className={`badge ${item.risk_level?.toLowerCase() === "high" ? "badge-expired" : "badge-expiring"}`}>
                        {item.risk_level}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-ai" style={{ fontWeight: 700 }}>
                        {item.recommendation}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        onClick={() => setIsClearanceModalOpen(true)}
                        style={{ padding: "4px 10px", fontSize: 11.5 }}
                      >
                        ⚡ Markdown
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <ClearanceSimulatorModal
        isOpen={isClearanceModalOpen}
        onClose={() => setIsClearanceModalOpen(false)}
        showToast={showToast}
      />
    </>
  );
}
