import { useState } from "react";

export default function DemandSimulatorModal({ isOpen, onClose }) {
  const [category, setCategory] = useState("Fruits & Vegetables");
  const [stockQuantity, setStockQuantity] = useState(45);
  const [reorderLevel, setReorderLevel] = useState(25);
  const [reorderQuantity, setReorderQuantity] = useState(20);
  const [unitPrice, setUnitPrice] = useState(3.5);
  const [shelfLifeDays, setShelfLifeDays] = useState(12);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSimulate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ml/predict/demand", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category,
          stock_quantity: Number(stockQuantity),
          reorder_level: Number(reorderLevel),
          reorder_quantity: Number(reorderQuantity),
          unit_price: Number(unitPrice),
          shelf_life_days: Number(shelfLifeDays),
        }),
      });

      if (!response.ok) {
        throw new Error("Prediction request failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to generate prediction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: 540 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 18, color: "#1e293b" }}>
            🔮 Interactive Demand Forecasting Simulator
          </h3>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              fontSize: 20,
              cursor: "pointer",
              color: "#94a3b8",
            }}
          >
            &times;
          </button>
        </div>

        <p style={{ margin: "0 0 16px", fontSize: 13, color: "#64748b" }}>
          Test what-if market scenarios live against the trained <strong>Ridge Regression</strong> ML model.
        </p>

        {error && (
          <div style={{ background: "#fee2e2", color: "#991b1b", padding: 10, borderRadius: 6, marginBottom: 12, fontSize: 13 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSimulate}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Product Category
              </label>
              <select
                className="select-filter"
                style={{ width: "100%", boxSizing: "border-box" }}
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="Fruits & Vegetables">Fruits & Vegetables</option>
                <option value="Dairy">Dairy</option>
                <option value="Bakery">Bakery</option>
                <option value="Seafood">Seafood</option>
                <option value="Grains & Pulses">Grains & Pulses</option>
                <option value="Oils & Fats">Oils & Fats</option>
                <option value="Beverages">Beverages</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Unit Price ($)
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                value={unitPrice}
                onChange={(e) => setUnitPrice(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Shelf Life (Days)
              </label>
              <input
                type="number"
                min="1"
                value={shelfLifeDays}
                onChange={(e) => setShelfLifeDays(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Current Shelf Stock
              </label>
              <input
                type="number"
                min="0"
                value={stockQuantity}
                onChange={(e) => setStockQuantity(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Reorder Level
              </label>
              <input
                type="number"
                min="0"
                value={reorderLevel}
                onChange={(e) => setReorderLevel(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Reorder Batch Size
              </label>
              <input
                type="number"
                min="0"
                value={reorderQuantity}
                onChange={(e) => setReorderQuantity(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 16 }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: "8px 16px",
                borderRadius: 6,
                border: "1px solid #cbd5e1",
                background: "#f8fafc",
                cursor: "pointer",
                fontWeight: 600,
                color: "#475569",
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ minWidth: 140 }}
            >
              {loading ? "Forecasting..." : "Run ML Forecast"}
            </button>
          </div>
        </form>

        {result && (
          <div
            style={{
              marginTop: 16,
              padding: 14,
              borderRadius: 8,
              background: "#f0fdf4",
              border: "1px solid #86efac",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: "#166534" }}>
                Predicted Sales Volume:
              </span>
              <span style={{ fontSize: 20, fontWeight: 800, color: "#14532d" }}>
                {result.predicted_demand} units
              </span>
            </div>
            <div style={{ fontSize: 12, color: "#15803d", marginTop: 4 }}>
              <strong>Architecture:</strong> {result.model_name}
            </div>
            <div style={{ fontSize: 11, color: "#166534", marginTop: 2 }}>
              Inputs: Category: {result.category} | Stock: {stockQuantity} | Price: ${unitPrice} | Shelf Life: {shelfLifeDays}d
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
