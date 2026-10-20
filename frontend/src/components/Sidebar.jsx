import React from "react";
import {
  DashboardIcon,
  InventoryIcon,
  CatalogIcon,
  RiskIcon,
  ForecastIcon,
  IntelligenceIcon,
  CartIcon,
  RefreshIcon,
  BrandLogoIcon,
} from "./Icons";

export default function Sidebar({
  activePage,
  setActivePage,
  inventoryCount = 0,
  productsCount = 0,
  highRiskCount = 0,
  forecastsCount = 0,
  urgentClearanceCount = 0,
  onOpenRecordSale,
  backendOnline = true,
  isRefreshing = false,
  onRefresh,
}) {
  const navItems = [
    {
      id: "dashboard",
      label: "Executive Dashboard",
      icon: <DashboardIcon size={19} />,
      badge: null,
    },
    {
      id: "inventory",
      label: "Inventory Batches",
      icon: <InventoryIcon size={19} />,
      badge: { text: inventoryCount > 0 ? inventoryCount : 10, type: "neutral" },
    },
    {
      id: "products",
      label: "Catalog",
      icon: <CatalogIcon size={19} />,
      badge: { text: productsCount > 0 ? productsCount : 10, type: "neutral" },
    },
    {
      id: "spoilage",
      label: "Spoilage Risk Radar",
      icon: <RiskIcon size={19} />,
      badge: { text: `${highRiskCount > 0 ? highRiskCount : 10} High`, type: "danger" },
    },
    {
      id: "forecast",
      label: "Demand Forecasts",
      icon: <ForecastIcon size={19} />,
      badge: { text: forecastsCount > 0 ? forecastsCount : 10, type: "neutral" },
    },
    {
      id: "intelligence",
      label: "AI Decision Engine",
      icon: <IntelligenceIcon size={19} />,
      badge:
        urgentClearanceCount > 0
          ? { text: `${urgentClearanceCount} Alert`, type: "danger" }
          : null,
    },
  ];

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <BrandLogoIcon size={22} />
        </div>
        <div className="sidebar-brand-text">
          <h2>ShelfLife</h2>
          <span>Retail AI Platform</span>
        </div>
      </div>

      {/* Quick Action Button */}
      <div className="sidebar-action-wrap">
        <button
          className="sidebar-pos-btn"
          onClick={() => onOpenRecordSale && onOpenRecordSale(null)}
          title="Open Point of Sale to record customer sale with FEFO stock deduction"
        >
          <CartIcon size={16} />
          <span>Record Sale (POS)</span>
        </button>
      </div>

      {/* Navigation Links */}
      <div className="sidebar-section-title">Navigation</div>
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-nav-item ${isActive ? "active" : ""}`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="sidebar-nav-icon">{item.icon}</span>
              <span className="sidebar-nav-label">{item.label}</span>
              {item.badge && (
                <span className={`sidebar-badge badge-${item.badge.type}`}>
                  {item.badge.text}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status and Telemetry Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-telemetry">
          <div className="telemetry-row">
            <span className={`telemetry-dot ${backendOnline ? "online" : "offline"}`} />
            <span className="telemetry-label">
              {backendOnline ? "Core API Live (Port 8000)" : "Core API Disconnected"}
            </span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-dot online" />
            <span className="telemetry-label">ML Models: Ridge + Logistic</span>
          </div>
        </div>

        <button
          className="sidebar-refresh-btn"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Synchronize fresh inventory and inference data from database"
        >
          <RefreshIcon size={14} className={isRefreshing ? "spin-icon" : ""} />
          <span>{isRefreshing ? "Synchronizing..." : "Refresh Database"}</span>
        </button>
      </div>
    </aside>
  );
}
