import { useState, useEffect } from "react";
import API_BASE from "../apiConfig";

export default function ClearanceSimulatorModal({ isOpen, onClose }) {
  const [discountPercent, setDiscountPercent] = useState(30);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const runSimulation = async (discount) => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/reports/simulate-clearance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ discount_percent: Number(discount) }),
      });
      if (!response.ok) throw new Error("Clearance simulation failed.");
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to load simulation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      runSimulation(discountPercent);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: 640 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 18, color: "#1e293b" }}>
            Promotional Clearance Markdown Simulator
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
          Calculate how much capital can be salvaged by marking down high-risk batches before they spoil.
        </p>

        {error && (
          <div style={{ background: "#fee2e2", color: "#991b1b", padding: 10, borderRadius: 6, marginBottom: 12, fontSize: 13 }}>
            {error}
          </div>
        )}

        <div style={{ background: "#f8fafc", padding: 14, borderRadius: 8, border: "1px solid #e2e8f0", marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: "#334155" }}>
              Clearance Discount Rate: <strong>{discountPercent}% OFF</strong>
            </label>
            <span style={{ fontSize: 12, color: "#64748b" }}>Recommended: 20% - 40%</span>
          </div>
          <input
            type="range"
            min="10"
            max="70"
            step="5"
            value={discountPercent}
            onChange={(e) => {
              setDiscountPercent(e.target.value);
              runSimulation(e.target.value);
            }}
            style={{ width: "100%", cursor: "pointer" }}
          />
        </div>

        {result && (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 16 }}>
              <div style={{ background: "#fef2f2", border: "1px solid #fecaca", padding: 10, borderRadius: 6 }}>
                <div style={{ fontSize: 11, color: "#991b1b", fontWeight: 600 }}>Unmitigated Cost Loss</div>
                <div style={{ fontSize: 18, color: "#991b1b", fontWeight: 800 }}>₹{result.unmitigated_cost_loss.toFixed(2)}</div>
              </div>
              <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", padding: 10, borderRadius: 6 }}>
                <div style={{ fontSize: 11, color: "#166534", fontWeight: 600 }}>Salvaged Revenue</div>
                <div style={{ fontSize: 18, color: "#166534", fontWeight: 800 }}>₹{result.estimated_discounted_revenue_recovered.toFixed(2)}</div>
              </div>
              <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", padding: 10, borderRadius: 6 }}>
                <div style={{ fontSize: 11, color: "#1e40af", fontWeight: 600 }}>Batches Rescued</div>
                <div style={{ fontSize: 18, color: "#1e40af", fontWeight: 800 }}>{result.total_items_simulated} batches</div>
              </div>
            </div>

            <div style={{ maxHeight: 220, overflowY: "auto", border: "1px solid #e2e8f0", borderRadius: 6 }}>
              <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#f1f5f9", textAlign: "left" }}>
                    <th style={{ padding: "6px 10px" }}>Product</th>
                    <th style={{ padding: "6px 10px" }}>Units</th>
                    <th style={{ padding: "6px 10px" }}>Regular</th>
                    <th style={{ padding: "6px 10px" }}>Sale Price</th>
                    <th style={{ padding: "6px 10px" }}>Salvaged</th>
                  </tr>
                </thead>
                <tbody>
                  {result.simulated_items.map((item) => (
                    <tr key={item.inventory_id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "6px 10px" }}><strong>{item.product_name}</strong></td>
                      <td style={{ padding: "6px 10px" }}>{item.quantity}</td>
                      <td style={{ padding: "6px 10px", color: "#64748b", textDecoration: "line-through" }}>₹{item.original_price}</td>
                      <td style={{ padding: "6px 10px", color: "#166534", fontWeight: 700 }}>₹{item.discounted_price}</td>
                      <td style={{ padding: "6px 10px", fontWeight: 600 }}>₹{item.recovered_revenue}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
          <button
            type="button"
            onClick={onClose}
            className="btn btn-primary"
          >
            Close Simulator
          </button>
        </div>
      </div>
    </div>
  );
}
