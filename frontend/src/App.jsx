import { useEffect, useState, useCallback } from "react";
import "./App.css";

import Sidebar from "./components/Sidebar";
import DashboardView from "./components/DashboardView";
import ProductsView from "./components/ProductsView";
import InventoryView from "./components/InventoryView";
import SpoilageView from "./components/SpoilageView";
import ForecastView from "./components/ForecastView";
import IntelligenceView from "./components/IntelligenceView";
import AddProductModal from "./components/AddProductModal";
import AddInventoryModal from "./components/AddInventoryModal";
import RecordSaleModal from "./components/RecordSaleModal";
import {
  CartIcon,
  RefreshIcon,
  CheckIcon,
  InfoIcon,
  AlertIcon,
  StoreIcon,
} from "./components/Icons";

import { API_BASE as API } from "./apiConfig";

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
  const [selectedBatchProductId, setSelectedBatchProductId] = useState(null);

  const handleOpenRecordSale = (productId = null) => {
    setSelectedSaleProductId(productId);
    setIsRecordSaleOpen(true);
  };

  const handleOpenAddBatch = (productId = null) => {
    setSelectedBatchProductId(productId);
    setIsAddInventoryOpen(true);
  };

  // Resilient fetch helper: tries primary Vite proxy, then direct http://127.0.0.1:8000
  const fetchWithFallback = async (path) => {
    try {
      const primaryUrl = `${API}${path}`;
      const res = await fetch(primaryUrl);
      if (res.ok) return await res.json();
    } catch {}

    if (API !== "http://127.0.0.1:8000") {
      try {
        const fallbackUrl = `http://127.0.0.1:8000${path}`;
        const res = await fetch(fallbackUrl);
        if (res.ok) return await res.json();
      } catch {}
    }

    return null;
  };

  /* =========================================================
     FETCH DATA FROM FASTAPI BACKEND WITH DUAL RESILIENCE
  ========================================================= */
  const loadData = async (silent = false) => {
    if (!silent) {
      setIsRefreshing(true);
    }

    try {
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
        fetchWithFallback("/products"),
        fetchWithFallback("/inventory"),
        fetchWithFallback("/sales"),
        fetchWithFallback("/suppliers"),
        fetchWithFallback("/spoilage-predictions"),
        fetchWithFallback("/demand-forecasts"),
        fetchWithFallback("/dashboard-summary"),
        fetchWithFallback("/inventory-intelligence"),
        fetchWithFallback("/inventory-intelligence-summary"),
      ]);

      if (Array.isArray(pData) && pData.length > 0) setProducts(pData);
      if (Array.isArray(invData) && invData.length > 0) setInventory(invData);
      if (Array.isArray(sData)) setSales(sData);
      if (Array.isArray(supData)) setSuppliers(supData);
      if (Array.isArray(spData)) setSpoilage(spData);
      if (Array.isArray(dfData)) setForecasts(dfData);
      if (dashData) setDashboardSummary(dashData);
      if (Array.isArray(intelData)) setIntelligenceData(intelData);
      if (isumData) setIntelligenceSummary(isumData);

      // Verify that core data was received
      if ((pData && pData.length > 0) || (invData && invData.length > 0)) {
        setBackendOnline(true);
        setError("");
        setLoading(false);
        setIsRefreshing(false);
        if (silent) {
          showToast("Data synchronized with database", "info");
        }
      } else {
        throw new Error("Core endpoints not ready yet");
      }
    } catch (err) {
      console.warn("ShelfLife API connection waiting for backend:", err);
      setBackendOnline(false);
      setIsRefreshing(false);
      // Only display connecting message if no products loaded yet
      setProducts((currentProducts) => {
        if (currentProducts.length === 0) {
          setError("Connecting to ShelfLife Core Services on http://127.0.0.1:8000... Connecting automatically.");
        }
        return currentProducts;
      });
    }
  };

  // Initial load
  useEffect(() => {
    loadData();
  }, []);

  // Background auto-reconnect heartbeat: polls continuously until backend is online
  useEffect(() => {
    if (backendOnline && products.length > 0) return;

    const pingBackend = async () => {
      try {
        let isHealthy = false;
        try {
          const res = await fetch(`${API}/health`);
          if (res.ok) isHealthy = true;
        } catch {}

        if (!isHealthy && API !== "http://127.0.0.1:8000") {
          try {
            const res2 = await fetch("http://127.0.0.1:8000/health");
            if (res2.ok) isHealthy = true;
          } catch {}
        }

        if (isHealthy) {
          setError("");
          setBackendOnline(true);
          await loadData(true);
        }
      } catch {}
    };

    const interval = setInterval(pingBackend, 1500);
    return () => clearInterval(interval);
  }, [backendOnline, products.length]);

  // Quick navigation count calculations
  const highRiskCount = spoilage.filter((s) => String(s.risk_level).toLowerCase() === "high").length;
  const urgentClearanceCount = intelligenceData.filter(
    (i) => i.recommendation === "Urgent Clearance" || i.recommendation === "Sell Quickly"
  ).length;

  const pageTitles = {
    dashboard: "Executive Dashboard",
    inventory: "Inventory Batches & Expiry Management",
    products: "Perishable Product Catalog",
    spoilage: "Spoilage Risk Radar & ML Classification",
    forecast: "Demand Forecasting & Sales Projections",
    intelligence: "AI Decision Engine & Clearance Markdown",
  };

  return (
    <div className="app-layout">
      {/* Toast Notification Container */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            <span className="toast-icon">
              {t.type === "success" && <CheckIcon size={16} />}
              {t.type === "info" && <InfoIcon size={16} />}
              {t.type === "warning" && <AlertIcon size={16} />}
            </span>
            <span className="toast-message">{t.message}</span>
          </div>
        ))}
      </div>

      {/* Left Vertical Sidebar */}
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        inventoryCount={inventory.length}
        productsCount={products.length}
        highRiskCount={highRiskCount}
        forecastsCount={forecasts.length}
        urgentClearanceCount={urgentClearanceCount}
        onOpenRecordSale={handleOpenRecordSale}
        backendOnline={backendOnline}
        isRefreshing={isRefreshing}
        onRefresh={() => loadData(true)}
      />

      {/* Main Workspace (Right Side) */}
      <div className="app-workspace">
        {/* Top Header Bar */}
        <header className="workspace-topbar">
          <div className="topbar-left">
            <div className="topbar-breadcrumb">
              <span className="breadcrumb-root">ShelfLife</span>
              <span className="breadcrumb-sep">/</span>
              <span className="breadcrumb-active">{pageTitles[activePage] || "Dashboard"}</span>
            </div>
            <h1 className="topbar-title">{pageTitles[activePage] || "Dashboard"}</h1>
          </div>

          <div className="topbar-right">
            {activePage === "dashboard" && (
              <div className="store-badge" style={{ padding: "6px 14px", fontSize: "12.5px" }}>
                <StoreIcon size={15} />
                <span>Small Retail Store</span>
              </div>
            )}
            <div className="status-pill">
              <span className={`pulse-dot ${backendOnline ? "" : "offline"}`} />
              <span>{backendOnline ? "API & PostgreSQL Live (:8000)" : "API Disconnected"}</span>
            </div>

            <button
              className="btn btn-secondary topbar-refresh-btn"
              onClick={() => loadData(true)}
              title="Reload fresh data from database"
              disabled={isRefreshing}
            >
              <RefreshIcon size={15} className={isRefreshing ? "spin-icon" : ""} />
              <span>{isRefreshing ? "Refreshing..." : "Refresh Data"}</span>
            </button>

            <button
              className="btn btn-primary topbar-pos-btn"
              onClick={() => handleOpenRecordSale(null)}
              title="Record customer sale & automatically deduct stock via FEFO"
            >
              <CartIcon size={16} />
              <span>Record Sale (POS)</span>
            </button>
          </div>
        </header>

        {/* Content View Container */}
        <main className="workspace-content">
          {error && products.length === 0 && (
            <div className="error-box" style={{ background: "#fef3c7", borderColor: "#fde68a", color: "#92400e" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span className="pulse-dot offline" style={{ minWidth: 10, minHeight: 10 }} />
                <div>
                  <strong>Backend Status:</strong> {error}
                </div>
              </div>
              <button className="btn btn-secondary" onClick={() => loadData(false)}>
                Retry Connection
              </button>
            </div>
          )}

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner" />
              <p style={{ fontSize: 16, color: "#059669", fontWeight: 600 }}>
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
                  onOpenAddProduct={() => setIsAddProductOpen(true)}
                  onOpenAddBatch={() => setIsAddInventoryOpen(true)}
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
                  onOpenAddBatch={handleOpenAddBatch}
                  showToast={showToast}
                />
              )}

              {activePage === "inventory" && (
                <InventoryView
                  inventory={inventory}
                  onOpenAddBatch={() => handleOpenAddBatch(null)}
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
      </div>

      {/* Modals */}
      <AddProductModal
        isOpen={isAddProductOpen}
        onClose={() => setIsAddProductOpen(false)}
        onProductAdded={(newProd) => {
          setProducts((prev) => [...prev, newProd]);
          showToast(`Product "${newProd.product_name}" added and inventory initialized.`);
          loadData(true);
        }}
        API={API}
      />

      <AddInventoryModal
        isOpen={isAddInventoryOpen}
        onClose={() => {
          setIsAddInventoryOpen(false);
          setSelectedBatchProductId(null);
        }}
        onInventoryAdded={(newBatch) => {
          setInventory((prev) => [...prev, newBatch]);
          showToast(`Batch ${newBatch.batch_number} added. Stock on-hand updated.`);
          loadData(true);
        }}
        products={products}
        initialProductId={selectedBatchProductId}
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