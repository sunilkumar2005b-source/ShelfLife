import { useState } from "react";
import API_BASE from "../apiConfig";

export default function SpoilageSimulatorModal({ isOpen, onClose }) {
  const [category, setCategory] = useState("Dairy");
  const [stockQuantity, setStockQuantity] = useState(35);
  const [daysRemaining, setDaysRemaining] = useState(2);
  const [unitPrice, setUnitPrice] = useState(4.0);
  const [salesVolume, setSalesVolume] = useState(40.0);
  const [turnoverRate, setTurnoverRate] = useState(30.0);
  const [totalShelfLife, setTotalShelfLife] = useState(10);

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
      const response = await fetch(`${API_BASE}/ml/predict/spoilage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category,
          stock_quantity: Number(stockQuantity),
          days_remaining: Number(daysRemaining),
          unit_price: Number(unitPrice),
          sales_volume: Number(salesVolume),
          turnover_rate: Number(turnoverRate),
          total_shelf_life: Number(totalShelfLife),
        }),
      });

      if (!response.ok) {
        throw new Error("Prediction request failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to assess spoilage risk.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: 540 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 18, color: "#1e293b" }}>
            Interactive Spoilage Risk Classifier
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
          Simulate batch expiration and depletion ratios using the trained <strong>Logistic Regression</strong> classifier.
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
                <option value="Dairy">Dairy</option>
                <option value="Fruits & Vegetables">Fruits & Vegetables</option>
                <option value="Bakery">Bakery</option>
                <option value="Seafood">Seafood</option>
                <option value="Grains & Pulses">Grains & Pulses</option>
                <option value="Oils & Fats">Oils & Fats</option>
                <option value="Beverages">Beverages</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Days Remaining to Expiry
              </label>
              <input
                type="number"
                min="0"
                value={daysRemaining}
                onChange={(e) => setDaysRemaining(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Current Batch Units
              </label>
              <input
                type="number"
                min="1"
                value={stockQuantity}
                onChange={(e) => setStockQuantity(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Total Rated Shelf Life (Days)
              </label>
              <input
                type="number"
                min="1"
                value={totalShelfLife}
                onChange={(e) => setTotalShelfLife(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Sales Velocity (Units/Month)
              </label>
              <input
                type="number"
                min="1"
                value={salesVolume}
                onChange={(e) => setSalesVolume(e.target.value)}
                style={{ width: "100%", padding: "7px 10px", borderRadius: 6, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>
                Turnover Velocity Index (1-100)
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={turnoverRate}
                onChange={(e) => setTurnoverRate(e.target.value)}
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
              style={{ minWidth: 150 }}
            >
              {loading ? "Evaluating..." : "Classify Spoilage"}
            </button>
          </div>
        </form>

        {result && (
          <div
            style={{
              marginTop: 16,
              padding: 14,
              borderRadius: 8,
              background: result.risk_level === "High" ? "#fef2f2" : result.risk_level === "Medium" ? "#fffbeb" : "#f0fdf4",
              border: `1px solid ${result.risk_level === "High" ? "#fca5a5" : result.risk_level === "Medium" ? "#fde68a" : "#86efac"}`,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: result.risk_level === "High" ? "#991b1b" : result.risk_level === "Medium" ? "#92400e" : "#166534" }}>
                Classified Spoilage Risk Tier:
              </span>
              <span
                className={`risk ${result.risk_level.toLowerCase()}`}
                style={{ fontSize: 14, padding: "4px 12px" }}
              >
                {result.risk_level} Risk ({(result.spoilage_probability * 100).toFixed(1)}%)
              </span>
            </div>
            <div style={{ fontSize: 12, marginTop: 6, color: "#475569" }}>
              <strong>Architecture:</strong> {result.model_name}
            </div>
            {result.class_probabilities && (
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>
                Class Probabilities: High: {(result.class_probabilities.High * 100).toFixed(1)}% | Medium: {(result.class_probabilities.Medium * 100).toFixed(1)}% | Low: {(result.class_probabilities.Low * 100).toFixed(1)}%
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
