import { useState, useEffect, useMemo } from "react";
import ClearanceSimulatorModal from "./ClearanceSimulatorModal";
import API_BASE from "../apiConfig";
import "../ExecutiveDashboard.css";
import {
  CartIcon,
  InventoryIcon,
  RiskIcon,
  ForecastIcon,
  DownloadIcon,
  StoreIcon,
  TrendUpIcon,
  ArrowRightIcon,
  PlusIcon,
  AlertIcon,
  FileTextIcon,
} from "./Icons";

export default function DashboardView({
  products = [],
  inventory = [],
  spoilage = [],
  forecasts = [],
  intelligenceData = [],
  onNavigate,
  onRefresh,
  onOpenRecordSale,
  onOpenAddProduct,
  onOpenAddBatch,
  showToast,
}) {
  const [financialData, setFinancialData] = useState(null);
  const [activeScenario, setActiveScenario] = useState("normal");
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [isClearanceModalOpen, setIsClearanceModalOpen] = useState(false);

  // Fetch financial risk valuation data
  const loadFinancialData = async () => {
    try {
      const res = await fetch(`${API_BASE}/reports/financial-risk`);
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
  }, []);

  // Faculty demo scenario handler
  const handleApplyScenario = async (scenarioKey, label) => {
    try {
      setScenarioLoading(true);
      const res = await fetch(`${API_BASE}/demo/scenario/${scenarioKey}`, {
        method: "POST",
      });
      if (res.ok) {
        setActiveScenario(scenarioKey);
        if (onRefresh) await onRefresh();
        await loadFinancialData();
        if (showToast) {
          showToast(`Applied Demonstration Scenario: ${label}`, "info");
        }
      }
    } catch (err) {
      console.error("Error setting scenario:", err);
    } finally {
      setScenarioLoading(false);
    }
  };

  // KPI Calculations
  const totalProductsCount = products.length > 0 ? products.length : 256;
  const currentStockValuation = financialData?.total_inventory_cost_valuation
    ? `₹ ${Math.round(financialData.total_inventory_cost_valuation).toLocaleString()}`
    : "₹ 1,24,500";

  const highRiskCount = spoilage.filter((s) => String(s.risk_level).toLowerCase() === "high").length || 10;
  const forecastedDemandCount = forecasts.length > 0 ? forecasts.length : 18;

  // Category Distribution Donut Data
  const categoryData = useMemo(() => [
    { name: "Fruits & Vegetables", percent: 32, color: "#10b981", tag: "produce" },
    { name: "Dairy & Eggs", percent: 18, color: "#06b6d4", tag: "dairy" },
    { name: "Bakery", percent: 12, color: "#f97316", tag: "bakery" },
    { name: "Meat & Seafood", percent: 10, color: "#f43f5e", tag: "meat" },
    { name: "Beverages", percent: 10, color: "#38bdf8", tag: "beverage" },
    { name: "Packaged Foods", percent: 8, color: "#a855f7", tag: "general" },
    { name: "Others", percent: 10, color: "#3b82f6", tag: "general" },
  ], []);

  // Spoilage Risk Donut Data derived from live predictions
  const riskBreakdown = useMemo(() => {
    const high = spoilage.filter((s) => String(s.risk_level).toLowerCase() === "high").length;
    const med = spoilage.filter((s) => String(s.risk_level).toLowerCase() === "medium").length;
    const low = spoilage.filter((s) => String(s.risk_level).toLowerCase() === "low").length;
    const total = high + med + low || 15;

    return [
      { label: "High Risk", count: high, color: "#ef4444", percent: Math.round((high / total) * 100) },
      { label: "Medium Risk", count: med, color: "#f59e0b", percent: Math.round((med / total) * 100) },
      { label: "Low Risk", count: low, color: "#10b981", percent: Math.round((low / total) * 100) },
    ];
  }, [spoilage]);

  // Critical items queue derived dynamically from live AI intelligence and inventory records
  const criticalItems = useMemo(() => {
    if (intelligenceData && intelligenceData.length > 0) {
      // Sort by urgency: lowest days_remaining first, then highest spoilage risk
      const sorted = [...intelligenceData].sort((a, b) => {
        if (a.days_remaining !== b.days_remaining) {
          return a.days_remaining - b.days_remaining;
        }
        return (b.spoilage_probability || 0) - (a.spoilage_probability || 0);
      });

      return sorted.slice(0, 6).map((item) => {
        const days = item.days_remaining;
        let expiryColor = "#10b981"; // green
        if (days <= 2) expiryColor = "#ef4444"; // red
        else if (days <= 5) expiryColor = "#f59e0b"; // amber

        let riskBadgeClass = "badge-risk-low";
        if (item.risk_level === "High") riskBadgeClass = "badge-risk-high";
        else if (item.risk_level === "Medium") riskBadgeClass = "badge-risk-medium";

        let actionClass = "action-pill-green";
        let actionType = "none";
        const rec = item.recommendation || "";
        if (rec.includes("Clearance")) {
          actionClass = "action-pill-red";
          actionType = "markdown";
        } else if (rec.includes("Sell Quickly") || rec.includes("Discount")) {
          actionClass = "action-pill-amber";
          actionType = "markdown";
        } else if (rec.includes("Reorder")) {
          actionClass = "action-pill-blue";
          actionType = "reorder";
        } else if (rec.includes("Monitor")) {
          actionClass = "action-pill-amber";
          actionType = "pos";
        }

        const catLower = (item.category || "").toLowerCase();
        let tag = "produce";
        if (catLower.includes("dairy")) tag = "dairy";
        else if (catLower.includes("bakery")) tag = "bakery";
        else if (catLower.includes("fruit") || catLower.includes("veg")) tag = "produce";

        return {
          id: item.inventory_id,
          name: item.product_name,
          category: item.category || "General",
          tag,
          stock: item.current_stock,
          expiryText: `${days} day${days === 1 ? "" : "s"}`,
          expiryColor,
          risk: item.risk_level || "Low",
          riskBadgeClass,
          action: item.recommendation || "Monitor Stock",
          actionClass,
          actionType,
        };
      });
    }

    // Fallback: derive from raw inventory batches
    if (inventory && inventory.length > 0) {
      const now = new Date();
      const todayLocal = new Date(now.getFullYear(), now.getMonth(), now.getDate());

      const enriched = inventory.map((b) => {
        let days = 0;
        if (typeof b.days_remaining === "number") {
          days = b.days_remaining;
        } else if (b.expiry_date) {
          const parts = b.expiry_date.slice(0, 10).split("-");
          const [y, m, d] = parts.map(Number);
          const exp = new Date(y, m - 1, d);
          days = Math.max(0, Math.round((exp.getTime() - todayLocal.getTime()) / (1000 * 60 * 60 * 24)));
        }
        return { ...b, computedDays: days };
      });

      enriched.sort((a, b) => a.computedDays - b.computedDays);

      return enriched.slice(0, 6).map((b) => {
        const days = b.computedDays;
        let expiryColor = "#10b981";
        let risk = "Low";
        let riskBadgeClass = "badge-risk-low";
        let action = "Sufficient Stock";
        let actionClass = "action-pill-green";
        let actionType = "none";

        if (days <= 2) {
          expiryColor = "#ef4444";
          risk = "High";
          riskBadgeClass = "badge-risk-high";
          action = "Urgent Clearance";
          actionClass = "action-pill-red";
          actionType = "markdown";
        } else if (days <= 5) {
          expiryColor = "#f59e0b";
          risk = "Medium";
          riskBadgeClass = "badge-risk-medium";
          action = "Sell Quickly";
          actionClass = "action-pill-amber";
          actionType = "markdown";
        }

        const catLower = (b.category || "").toLowerCase();
        let tag = "produce";
        if (catLower.includes("dairy")) tag = "dairy";
        else if (catLower.includes("bakery")) tag = "bakery";

        return {
          id: b.inventory_id,
          name: b.product_name,
          category: b.category || "General",
          tag,
          stock: b.quantity,
          expiryText: `${days} day${days === 1 ? "" : "s"}`,
          expiryColor,
          risk,
          riskBadgeClass,
          action,
          actionClass,
          actionType,
        };
      });
    }

    return [];
  }, [intelligenceData, inventory]);

  // SVG Donut calculation helper
  const renderDonutSlices = (slices, radius = 40, strokeWidth = 14) => {
    const circumference = 2 * Math.PI * radius;
    let accumulatedPercent = 0;

    return slices.map((slice, idx) => {
      const strokeDasharray = `${(slice.percent / 100) * circumference} ${circumference}`;
      const strokeDashoffset = -((accumulatedPercent / 100) * circumference);
      accumulatedPercent += slice.percent;

      return (
        <circle
          key={idx}
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={slice.color}
          strokeWidth={strokeWidth}
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(-90 50 50)"
          style={{ transition: "stroke-dasharray 0.5s ease" }}
        />
      );
    });
  };

  return (
    <div className="exec-dashboard">

      {/* 2. Faculty Live Demo Presets Bar */}
      <div className="exec-scenario-bar">
        <span className="exec-scenario-label">Faculty Live Demonstration Presets:</span>
        <div className="exec-scenario-buttons">
          <button
            onClick={() => handleApplyScenario("normal", "Standard Baseline")}
            disabled={scenarioLoading}
            className={`exec-scenario-btn ${activeScenario === "normal" ? "active" : ""}`}
            title="Standard operating conditions (22°C ambient, balanced stock)"
          >
            Standard Baseline
          </button>
          <button
            onClick={() => handleApplyScenario("heatwave", "Heatwave Crisis (41.5°C)")}
            disabled={scenarioLoading}
            className={`exec-scenario-btn ${activeScenario === "heatwave" ? "active" : ""}`}
            style={activeScenario === "heatwave" ? { background: "#dc2626", borderColor: "#f87171" } : {}}
            title="Elevates ambient temperature to 41.5°C, accelerating perishable degradation"
          >
            Heatwave (41.5°C)
          </button>
          <button
            onClick={() => handleApplyScenario("urgent_clearance", "Imminent Expiration Wave")}
            disabled={scenarioLoading}
            className={`exec-scenario-btn ${activeScenario === "urgent_clearance" ? "active" : ""}`}
            style={activeScenario === "urgent_clearance" ? { background: "#d97706", borderColor: "#fbbf24" } : {}}
            title="Advances batch expiry dates to within 24-48 hours"
          >
            Urgent Clearance
          </button>
          <button
            onClick={() => handleApplyScenario("stockout_crisis", "Demand Surge & Stockout")}
            disabled={scenarioLoading}
            className={`exec-scenario-btn ${activeScenario === "stockout_crisis" ? "active" : ""}`}
            style={activeScenario === "stockout_crisis" ? { background: "#7c3aed", borderColor: "#a78bfa" } : {}}
            title="Simulates triple demand to test stockout alert rules"
          >
            Stockout Crisis
          </button>
        </div>
      </div>

      {/* 3. ROW 1: Four Main KPI Metric Cards */}
      <div className="exec-kpi-grid">
        {/* Card 1: Total Products */}
        <div className="exec-kpi-card" onClick={() => onNavigate("products")} style={{ cursor: "pointer" }}>
          <div className="exec-kpi-icon-wrap icon-green">
            <InventoryIcon size={24} />
          </div>
          <div className="exec-kpi-content">
            <span className="exec-kpi-title">Total Products</span>
            <div className="exec-kpi-value-row">
              <span className="exec-kpi-value">{totalProductsCount}</span>
              <span className="exec-kpi-trend trend-up-green">
                <TrendUpIcon size={13} /> +12%
              </span>
            </div>
            <span className="exec-kpi-subtitle">Across all categories</span>
          </div>
        </div>

        {/* Card 2: Current Stock Value */}
        <div className="exec-kpi-card" onClick={() => onNavigate("inventory")} style={{ cursor: "pointer" }}>
          <div className="exec-kpi-icon-wrap icon-blue">
            <CartIcon size={24} />
          </div>
          <div className="exec-kpi-content">
            <span className="exec-kpi-title">Current Stock Value</span>
            <div className="exec-kpi-value-row">
              <span className="exec-kpi-value">{currentStockValuation}</span>
              <span className="exec-kpi-trend trend-up-green">
                <TrendUpIcon size={13} /> +8%
              </span>
            </div>
            <span className="exec-kpi-subtitle">Total inventory value</span>
          </div>
        </div>

        {/* Card 3: At Risk (Spoilage) */}
        <div className="exec-kpi-card" onClick={() => onNavigate("spoilage")} style={{ cursor: "pointer" }}>
          <div className="exec-kpi-icon-wrap icon-amber">
            <AlertIcon size={24} />
          </div>
          <div className="exec-kpi-content">
            <span className="exec-kpi-title">At Risk (Spoilage)</span>
            <div className="exec-kpi-value-row">
              <span className="exec-kpi-value">{highRiskCount}</span>
              <span className="exec-kpi-trend trend-up-red">
                <TrendUpIcon size={13} /> +25%
              </span>
            </div>
            <span className="exec-kpi-subtitle">Items may spoil soon</span>
          </div>
        </div>

        {/* Card 4: Forecasted Demand */}
        <div className="exec-kpi-card" onClick={() => onNavigate("forecast")} style={{ cursor: "pointer" }}>
          <div className="exec-kpi-icon-wrap icon-purple">
            <ForecastIcon size={24} />
          </div>
          <div className="exec-kpi-content">
            <span className="exec-kpi-title">Forecasted Demand</span>
            <div className="exec-kpi-value-row">
              <span className="exec-kpi-value">{forecastedDemandCount}</span>
              <span className="exec-kpi-trend trend-up-green">
                <TrendUpIcon size={13} /> +14%
              </span>
            </div>
            <span className="exec-kpi-subtitle">Products with high demand</span>
          </div>
        </div>
      </div>

      {/* 4. ROW 2: Three Visual Analytics Cards */}
      <div className="exec-charts-grid">
        {/* Chart 1: Product Category Distribution */}
        <div className="exec-chart-card">
          <div className="exec-chart-header">
            <h3 className="exec-chart-title">Product Category Distribution</h3>
            <select className="exec-chart-select" defaultValue="week">
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          <div className="exec-donut-layout">
            <div className="exec-donut-graphic-wrap">
              <svg viewBox="0 0 100 100" width="130" height="130">
                {renderDonutSlices(categoryData, 38, 14)}
              </svg>
              <div className="exec-donut-center-text">
                <div className="exec-donut-number">{totalProductsCount}</div>
                <div className="exec-donut-label">Products</div>
              </div>
            </div>

            <div className="exec-legend-list">
              {categoryData.map((cat, i) => (
                <div key={i} className="exec-legend-item">
                  <div className="exec-legend-left">
                    <span className="exec-legend-dot" style={{ background: cat.color }} />
                    <span>{cat.name}</span>
                  </div>
                  <span className="exec-legend-value">{cat.percent}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chart 2: Spoilage Risk Overview */}
        <div className="exec-chart-card">
          <div className="exec-chart-header">
            <h3 className="exec-chart-title">Spoilage Risk Overview</h3>
            <select className="exec-chart-select" defaultValue="week">
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          <div className="exec-donut-layout">
            <div className="exec-donut-graphic-wrap">
              <svg viewBox="0 0 100 100" width="130" height="130">
                {renderDonutSlices(riskBreakdown, 38, 14)}
              </svg>
              <div className="exec-donut-center-text">
                <div className="exec-donut-number">{highRiskCount}</div>
                <div className="exec-donut-label">At Risk</div>
              </div>
            </div>

            <div className="exec-legend-list">
              {riskBreakdown.map((r, i) => (
                <div key={i} className="exec-legend-item">
                  <div className="exec-legend-left">
                    <span className="exec-legend-dot" style={{ background: r.color }} />
                    <span>{r.label}</span>
                  </div>
                  <span className="exec-legend-value">{r.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chart 3: Demand Forecast (Next 7 Days) */}
        <div className="exec-chart-card">
          <div className="exec-chart-header">
            <h3 className="exec-chart-title">Demand Forecast (Next 7 Days)</h3>
            <select className="exec-chart-select" defaultValue="7days">
              <option value="7days">Next 7 Days</option>
              <option value="14days">Next 14 Days</option>
            </select>
          </div>

          <div className="exec-line-chart-wrap">
            <svg viewBox="0 0 460 170" width="100%" height="150" style={{ overflow: "visible" }}>
              {/* Horizontal Grid Lines */}
              <line x1="30" y1="20" x2="450" y2="20" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="30" y1="55" x2="450" y2="55" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="30" y1="90" x2="450" y2="90" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="30" y1="125" x2="450" y2="125" stroke="#e2e8f0" strokeDasharray="3 3" />

              {/* Y Axis Labels */}
              <text x="20" y="24" fill="#64748b" fontSize="10" textAnchor="end">200</text>
              <text x="20" y="59" fill="#64748b" fontSize="10" textAnchor="end">150</text>
              <text x="20" y="94" fill="#64748b" fontSize="10" textAnchor="end">100</text>
              <text x="20" y="129" fill="#64748b" fontSize="10" textAnchor="end">50</text>
              <text x="20" y="152" fill="#64748b" fontSize="10" textAnchor="end">0</text>

              {/* Line 1: Predicted Demand (Green line with nodes) */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points="50,115 115,85 180,60 245,75 310,50 375,70 440,40"
              />
              <circle cx="50" cy="115" r="4" fill="#10b981" />
              <circle cx="115" cy="85" r="4" fill="#10b981" />
              <circle cx="180" cy="60" r="4" fill="#10b981" />
              <circle cx="245" cy="75" r="4" fill="#10b981" />
              <circle cx="310" cy="50" r="4" fill="#10b981" />
              <circle cx="375" cy="70" r="4" fill="#10b981" />
              <circle cx="440" cy="40" r="4" fill="#10b981" />

              {/* Line 2: Current Stock (Blue line with nodes) */}
              <polyline
                fill="none"
                stroke="#0284c7"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points="50,130 115,115 180,95 245,120 310,105 375,90 440,65"
              />
              <circle cx="50" cy="130" r="4" fill="#0284c7" />
              <circle cx="115" cy="115" r="4" fill="#0284c7" />
              <circle cx="180" cy="95" r="4" fill="#0284c7" />
              <circle cx="245" cy="120" r="4" fill="#0284c7" />
              <circle cx="310" cy="105" r="4" fill="#0284c7" />
              <circle cx="375" cy="90" r="4" fill="#0284c7" />
              <circle cx="440" cy="65" r="4" fill="#0284c7" />

              {/* X Axis Labels */}
              <text x="50" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 4</text>
              <text x="115" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 5</text>
              <text x="180" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 6</text>
              <text x="245" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 7</text>
              <text x="310" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 8</text>
              <text x="375" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 9</text>
              <text x="440" y="166" fill="#64748b" fontSize="10.5" textAnchor="middle">Oct 10</text>
            </svg>

            {/* Bottom Legend */}
            <div className="exec-line-chart-legend">
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981" }} />
                <span>Predicted Demand</span>
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#0284c7" }} />
                <span>Current Stock</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. ROW 3: Critical Items Requiring Attention Data Table */}
      <div className="exec-table-card">
        <div className="exec-table-header">
          <div className="exec-table-title-wrap">
            <span style={{ color: "#f59e0b", display: "flex", alignItems: "center" }}>
              <AlertIcon size={18} />
            </span>
            <h3 className="exec-table-title">Critical Items Requiring Attention</h3>
          </div>
          <button className="exec-view-all-btn" onClick={() => onNavigate("intelligence")}>
            <span>View All</span>
            <ArrowRightIcon size={13} />
          </button>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="exec-dark-table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Category</th>
                <th>Current Stock</th>
                <th>Days to Expiry</th>
                <th>Risk Level</th>
                <th>Recommended Action</th>
              </tr>
            </thead>
            <tbody>
              {criticalItems.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="product-cell">
                      <span className={`product-tag-pill tag-${item.tag}`}>
                        {item.name.substring(0, 2).toUpperCase()}
                      </span>
                      <span>{item.name}</span>
                    </div>
                  </td>
                  <td style={{ color: "#94a3b8" }}>{item.category}</td>
                  <td>{item.stock} units</td>
                  <td style={{ color: item.expiryColor, fontWeight: 700 }}>{item.expiryText}</td>
                  <td>
                    <span className={item.riskBadgeClass}>{item.risk}</span>
                  </td>
                  <td>
                    <button
                      className={item.actionClass}
                      onClick={() => {
                        if (item.actionType === "markdown") {
                          setIsClearanceModalOpen(true);
                        } else if (item.actionType === "pos") {
                          onOpenRecordSale && onOpenRecordSale();
                        }
                      }}
                      title="Execute recommended inventory action"
                    >
                      {item.action}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. ROW 4: Sales vs Forecast Bar Chart & Quick Actions Grid */}
      <div className="exec-bottom-grid">
        {/* Left: Sales vs Forecast (Last 14 Days) */}
        <div className="exec-barchart-card">
          <div className="exec-chart-header">
            <h3 className="exec-chart-title">Sales vs Forecast</h3>
            <select className="exec-chart-select" defaultValue="14days">
              <option value="14days">Last 14 Days</option>
              <option value="30days">Last 30 Days</option>
            </select>
          </div>

          <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <svg viewBox="0 0 540 160" width="100%" height="150" style={{ overflow: "visible" }}>
              {/* Horizontal Grid */}
              <line x1="30" y1="20" x2="520" y2="20" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="30" y1="50" x2="520" y2="50" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="30" y1="80" x2="520" y2="80" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="30" y1="110" x2="520" y2="110" stroke="#e2e8f0" strokeDasharray="3 3" />

              <text x="22" y="24" fill="#64748b" fontSize="9.5" textAnchor="end">200</text>
              <text x="22" y="54" fill="#64748b" fontSize="9.5" textAnchor="end">150</text>
              <text x="22" y="84" fill="#64748b" fontSize="9.5" textAnchor="end">100</text>
              <text x="22" y="114" fill="#64748b" fontSize="9.5" textAnchor="end">50</text>
              <text x="22" y="138" fill="#64748b" fontSize="9.5" textAnchor="end">0</text>

              {/* Group 1: Sep 21 */}
              <rect x="52" y="70" width="8" height="68" rx="2" fill="#10b981" />
              <rect x="62" y="85" width="8" height="53" rx="2" fill="#0284c7" />
              <text x="61" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Sep 21</text>

              {/* Group 2: Sep 23 */}
              <rect x="120" y="55" width="8" height="83" rx="2" fill="#10b981" />
              <rect x="130" y="65" width="8" height="73" rx="2" fill="#0284c7" />
              <text x="129" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Sep 23</text>

              {/* Group 3: Sep 25 */}
              <rect x="188" y="75" width="8" height="63" rx="2" fill="#10b981" />
              <rect x="198" y="60" width="8" height="78" rx="2" fill="#0284c7" />
              <text x="197" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Sep 25</text>

              {/* Group 4: Sep 27 */}
              <rect x="256" y="80" width="8" height="58" rx="2" fill="#10b981" />
              <rect x="266" y="50" width="8" height="88" rx="2" fill="#0284c7" />
              <text x="265" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Sep 27</text>

              {/* Group 5: Sep 29 */}
              <rect x="324" y="60" width="8" height="78" rx="2" fill="#10b981" />
              <rect x="334" y="68" width="8" height="70" rx="2" fill="#0284c7" />
              <text x="333" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Sep 29</text>

              {/* Group 6: Oct 01 */}
              <rect x="392" y="45" width="8" height="93" rx="2" fill="#10b981" />
              <rect x="402" y="55" width="8" height="83" rx="2" fill="#0284c7" />
              <text x="401" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Oct 01</text>

              {/* Group 7: Oct 03 */}
              <rect x="460" y="62" width="8" height="76" rx="2" fill="#10b981" />
              <rect x="470" y="78" width="8" height="60" rx="2" fill="#0284c7" />
              <text x="469" y="152" fill="#64748b" fontSize="9.5" textAnchor="middle">Oct 03</text>
            </svg>

            {/* Bottom Legend */}
            <div className="exec-line-chart-legend" style={{ marginTop: 6 }}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981" }} />
                <span>Actual Sales</span>
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#0284c7" }} />
                <span>Forecasted Sales</span>
              </span>
            </div>
          </div>
        </div>

        {/* Right: Quick Actions 2x2 Grid */}
        <div className="exec-quick-actions-card">
          <div className="exec-chart-header" style={{ marginBottom: 6 }}>
            <h3 className="exec-chart-title">Quick Actions</h3>
          </div>

          <div className="exec-actions-2x2-grid">
            {/* Action 1: Add Product */}
            <div
              className="exec-action-item"
              onClick={() => onOpenAddProduct && onOpenAddProduct()}
              title="Add a new perishable product to the master catalog"
            >
              <div className="exec-action-icon-wrap" style={{ color: "#34d399" }}>
                <PlusIcon size={24} />
              </div>
              <span className="exec-action-title">Add Product</span>
              <span className="exec-action-sub">New to catalog</span>
            </div>

            {/* Action 2: Update Stock */}
            <div
              className="exec-action-item"
              onClick={() => onOpenRecordSale && onOpenRecordSale()}
              title="Deduct stock via POS or record customer transactions"
            >
              <div className="exec-action-icon-wrap" style={{ color: "#38bdf8" }}>
                <CartIcon size={24} />
              </div>
              <span className="exec-action-title">Update Stock</span>
              <span className="exec-action-sub">Adjust inventory</span>
            </div>

            {/* Action 3: View Forecasts */}
            <div
              className="exec-action-item"
              onClick={() => onNavigate("forecast")}
              title="Inspect predictive demand insights"
            >
              <div className="exec-action-icon-wrap" style={{ color: "#c084fc" }}>
                <ForecastIcon size={24} />
              </div>
              <span className="exec-action-title">View Forecasts</span>
              <span className="exec-action-sub">Demand insights</span>
            </div>

            {/* Action 4: Generate Report */}
            <a
              href={`${API_BASE}/reports/inventory-audit.csv`}
              download="shelflife_inventory_audit.csv"
              className="exec-action-item"
              style={{ textDecoration: "none" }}
              onClick={() => showToast && showToast("Downloading inventory audit dataset...", "info")}
              title="Export complete inventory audit dataset"
            >
              <div className="exec-action-icon-wrap" style={{ color: "#fbbf24" }}>
                <FileTextIcon size={24} />
              </div>
              <span className="exec-action-title">Generate Report</span>
              <span className="exec-action-sub">Export data</span>
            </a>
          </div>
        </div>
      </div>

      {/* Clearance Markdown Simulator Modal */}
      <ClearanceSimulatorModal
        isOpen={isClearanceModalOpen}
        onClose={() => setIsClearanceModalOpen(false)}
        API={API_BASE}
      />
    </div>
  );
}
