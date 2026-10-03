import { useEffect, useState, useCallback } from "react";
import "./App.css";

import DashboardView from "./components/DashboardView";
import ProductsView from "./components/ProductsView";
import InventoryView from "./components/InventoryView";
import SpoilageView from "./components/SpoilageView";
import ForecastView from "./components/ForecastView";
import IntelligenceView from "./components/IntelligenceView";
import AddProductModal from "./components/AddProductModal";
import AddInventoryModal from "./components/AddInventoryModal";
import RecordSaleModal from "./components/RecordSaleModal";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [sales, setSales] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [spoilage, setSpoilage] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [intelligenceData, setIntelligenceData] = useState([]);
  const [intelligenceSummary, setIntelligenceSummary] = useState(null);

  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [backendOnline, setBackendOnline] = useState(true);

  // Toast notifications state
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = "success") => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  // Modals state
  const [isAddProductOpen, setIsAddProductOpen] = useState(false);
  const [isAddInventoryOpen, setIsAddInventoryOpen] = useState(false);
  const [isRecordSaleOpen, setIsRecordSaleOpen] = useState(false);
  const [selectedSaleProductId, setSelectedSaleProductId] = useState(null);

  const handleOpenRecordSale = (productId = null) => {
    setSelectedSaleProductId(productId);
    setIsRecordSaleOpen(true);
  };

  /* =========================================================
     FETCH DATA FROM FASTAPI BACKEND
  ========================================================= */
  const loadData = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      setIsRefreshing(true);
      setError("");

      const [
        pRes,
        invRes,
        sRes,
        supRes,
        spRes,
        dfRes,
        dashRes,
        intelRes,
        isumRes,
      ] = await Promise.all([
        fetch(`${API}/products`),
        fetch(`${API}/inventory`),
        fetch(`${API}/sales`),
        fetch(`${API}/suppliers`),
        fetch(`${API}/spoilage-predictions`),
        fetch(`${API}/demand-forecasts`),
        fetch(`${API}/dashboard-summary`),
        fetch(`${API}/inventory-intelligence`),
        fetch(`${API}/inventory-intelligence-summary`),
      ]);

      if (!pRes.ok || !invRes.ok) {
        throw new Error("Unable to communicate with ShelfLife backend.");
      }

      const [
        pData,
        invData,
        sData,
        supData,
        spData,
        dfData,
        dashData,
        intelData,
        isumData,
      ] = await Promise.all([
        pRes.json(),
        invRes.json(),
        sRes.json(),
        supRes.json(),
        spRes.json(),
        dfRes.json(),
        dashRes.json(),
        intelRes.json(),
        isumRes.json(),
      ]);

      setProducts(Array.isArray(pData) ? pData : []);
      setInventory(Array.isArray(invData) ? invData : []);
      setSales(Array.isArray(sData) ? sData : []);
      setSuppliers(Array.isArray(supData) ? supData : []);
      setSpoilage(Array.isArray(spData) ? spData : []);
      setForecasts(Array.isArray(dfData) ? dfData : []);
      setDashboardSummary(dashData);
      setIntelligenceData(Array.isArray(intelData) ? intelData : []);
      setIntelligenceSummary(isumData);
      setBackendOnline(true);

      if (silent) {
        showToast("Retail intelligence data updated from database", "info");
      }
    } catch (err) {
      console.error("ShelfLife API load error:", err);
      setError("Unable to connect to backend service. Please check if PostgreSQL and FastAPI are running.");
      setBackendOnline(false);
      showToast("Backend connection issue detected", "warning");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Quick navigation count calculations
  const highRiskCount = spoilage.filter((s) => String(s.risk_level).toLowerCase() === "high").length;
  const urgentClearanceCount = intelligenceData.filter(
    (i) => i.recommendation === "Urgent Clearance" || i.recommendation === "Sell Quickly"
  ).length;

  return (
    <div className="app">
      {/* Toast Notification Container */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            <span>
              {t.type === "success" && "✅"}
              {t.type === "info" && "ℹ️"}
              {t.type === "warning" && "⚠️"}
            </span>
            <span>{t.message}</span>
          </div>
        ))}
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-top">
          <div className="header-brand">
            <div className="header-brand-title">
              <h1>ShelfLife</h1>
              <span className="header-badge">AI Core v1.0 • M.Tech Software Engineering</span>
            </div>
            <p>Autonomous Perishable Inventory Management & Retail Decision Support</p>
          </div>

          <div className="header-actions">
            <button
              className="btn btn-primary"
              onClick={() => handleOpenRecordSale(null)}
              style={{
                background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                fontWeight: 700,
                boxShadow: "0 4px 12px rgba(16, 185, 129, 0.4)",
              }}
              title="Record a customer sale & automatically deduct stock via FEFO"
            >
              🛒 Record Sale (POS)
            </button>

            <div className="status-pill">
              <span className={`pulse-dot ${backendOnline ? "" : "offline"}`} />
              {backendOnline ? "API & PostgreSQL Live (:8000)" : "API Disconnected"}
            </div>

            <button
              className="btn btn-refresh"
              onClick={() => loadData(true)}
              title="Reload fresh data from database"
              disabled={isRefreshing}
            >
              <span style={{ display: "inline-block", transform: isRefreshing ? "rotate(180deg)" : "none", transition: "transform 0.5s ease" }}>
                🔄
              </span>{" "}
              {isRefreshing ? "Refreshing..." : "Refresh Data"}
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="navbar">
        <div className="navbar-inner">
          <button
            className={activePage === "dashboard" ? "active" : ""}
            onClick={() => setActivePage("dashboard")}
          >
            📊 Executive Dashboard
          </button>
          <button
            className={activePage === "inventory" ? "active" : ""}
            onClick={() => setActivePage("inventory")}
          >
            📦 Inventory Batches
            <span className="nav-counter">{inventory.length}</span>
          </button>
          <button
            className={activePage === "products" ? "active" : ""}
            onClick={() => setActivePage("products")}
          >
            🍎 Catalog
            <span className="nav-counter">{products.length}</span>
          </button>
          <button
            className={activePage === "spoilage" ? "active" : ""}
            onClick={() => setActivePage("spoilage")}
          >
            ⚠️ Spoilage Risk Radar
            {highRiskCount > 0 && (
              <span className="nav-counter" style={{ background: "#ef4444", color: "white" }}>
                {highRiskCount} High
              </span>
            )}
          </button>
          <button
            className={activePage === "forecast" ? "active" : ""}
            onClick={() => setActivePage("forecast")}
          >
            📈 Demand Forecasts
            <span className="nav-counter">{forecasts.length}</span>
          </button>
          <button
            className={activePage === "intelligence" ? "active" : ""}
            onClick={() => setActivePage("intelligence")}
          >
            🧠 AI Decision Engine
            {urgentClearanceCount > 0 && (
              <span className="nav-counter" style={{ background: "#dc2626", color: "white" }}>
                {urgentClearanceCount} Alert
              </span>
            )}
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main>
        {error && (
          <div className="error-box">
            <div>
              <strong>Connection Warning:</strong> {error}
            </div>
            <button className="btn btn-secondary" onClick={() => loadData(false)}>
              Retry Connection
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner" />
            <p style={{ fontSize: 16, color: "#10b981", fontWeight: 600 }}>
              Synchronizing retail intelligence models & inventory records...
            </p>
          </div>
        ) : (
          <>
            {activePage === "dashboard" && (
              <DashboardView
                products={products}
                inventory={inventory}
                spoilage={spoilage}
                forecasts={forecasts}
                intelligenceData={intelligenceData}
                onNavigate={setActivePage}
                onRefresh={() => loadData(true)}
                onOpenRecordSale={handleOpenRecordSale}
                showToast={showToast}
              />
            )}

            {activePage === "products" && (
              <ProductsView
                products={products}
                inventory={inventory}
                suppliers={suppliers}
                onOpenAddModal={() => setIsAddProductOpen(true)}
                onOpenRecordSale={handleOpenRecordSale}
                showToast={showToast}
              />
            )}

            {activePage === "inventory" && (
              <InventoryView
                inventory={inventory}
                onOpenAddBatch={() => setIsAddInventoryOpen(true)}
                onOpenRecordSale={handleOpenRecordSale}
                onRefresh={() => loadData(true)}
                showToast={showToast}
                API={API}
              />
            )}

            {activePage === "spoilage" && (
              <SpoilageView
                spoilage={spoilage}
                inventory={inventory}
                onRefresh={() => loadData(true)}
                showToast={showToast}
              />
            )}

            {activePage === "forecast" && (
              <ForecastView
                forecasts={forecasts}
                sales={sales}
                onRefresh={() => loadData(true)}
                showToast={showToast}
              />
            )}

            {activePage === "intelligence" && (
              <IntelligenceView
                intelligenceData={intelligenceData}
                summaryData={intelligenceSummary}
                showToast={showToast}
              />
            )}
          </>
        )}
      </main>

      {/* Modals */}
      <AddProductModal
        isOpen={isAddProductOpen}
        onClose={() => setIsAddProductOpen(false)}
        onProductAdded={(newProd) => {
          setProducts((prev) => [...prev, newProd]);
          showToast(`Product "${newProd.product_name}" added and ML predictions generated!`);
          loadData(true);
        }}
        API={API}
      />

      <AddInventoryModal
        isOpen={isAddInventoryOpen}
        onClose={() => setIsAddInventoryOpen(false)}
        onInventoryAdded={(newBatch) => {
          setInventory((prev) => [...prev, newBatch]);
          showToast(`Batch ${newBatch.batch_number} created with live degradation evaluation!`);
          loadData(true);
        }}
        products={products}
        API={API}
      />

      <RecordSaleModal
        isOpen={isRecordSaleOpen}
        onClose={() => setIsRecordSaleOpen(false)}
        products={products}
        inventory={inventory}
        onSaleCompleted={() => loadData(true)}
        initialProductId={selectedSaleProductId}
        API={API}
        showToast={showToast}
      />
    </div>
  );
}

export default App;