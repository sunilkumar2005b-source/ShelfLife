import { useState, useEffect } from "react";
import API_BASE from "../apiConfig";

export default function AdjustStockModal({
  isOpen,
  onClose,
  batch = null,
  onBatchUpdated,
  API = API_BASE,
  showToast,
}) {
  const [newQuantity, setNewQuantity] = useState(0);
  const [reason, setReason] = useState("spoilage_discard");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (batch) {
      setNewQuantity(Number(batch.quantity) || 0);
      setError("");
    }
  }, [batch]);

  if (!isOpen || !batch) return null;

  const currentQty = Number(batch.quantity) || 0;
  const difference = Number(newQuantity) - currentQty;

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError("");

    const targetQty = parseInt(newQuantity, 10);
    if (isNaN(targetQty) || targetQty < 0) {
      setError("Quantity cannot be negative.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API}/inventory/${batch.inventory_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quantity: targetQty,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to update batch quantity.");
      }

      const updatedBatch = await response.json();
      if (showToast) {
        const diffText =
          difference < 0
            ? `Deducted ${Math.abs(difference)} unit(s) (${reason.replace("_", " ")})`
            : difference > 0
            ? `Added ${difference} unit(s)`
            : "No quantity change";
        showToast(
          `Batch ${batch.batch_number}: ${diffText}. New stock: ${targetQty} units.`,
          "info"
        );
      }

      if (onBatchUpdated) {
        onBatchUpdated(updatedBatch);
      }
      onClose();
    } catch (err) {
      setError(err.message || "Failed to adjust stock.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
        <div className="modal-header" style={{ background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)" }}>
          <h3>Adjust / Deduct Batch Stock</h3>
          <button className="modal-close" onClick={onClose} title="Close">
            &times;
          </button>
        </div>

        <form onSubmit={handleUpdate}>
          <div className="modal-body">
            <div style={{ background: "#f8fafc", padding: "12px 16px", borderRadius: 8, border: "1px solid #e2e8f0", marginBottom: 16 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>
                {batch.product_name}
              </div>
              <div style={{ fontSize: 12.5, color: "#64748b", marginTop: 2, display: "flex", gap: 12 }}>
                <span>Batch: <code>{batch.batch_number || `BATCH-${batch.inventory_id}`}</code></span>
                <span>Expiry: <strong>{batch.expiry_date}</strong></span>
              </div>
            </div>

            {error && (
              <div style={{ background: "#fef2f2", color: "#991b1b", padding: "10px 14px", borderRadius: 8, fontSize: 13, marginBottom: 14, border: "1px solid #fecaca" }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label>Reason for Stock Adjustment</label>
              <select value={reason} onChange={(e) => setReason(e.target.value)}>
                <option value="spoilage_discard">Discard Damaged / Spoiled Units</option>
                <option value="manual_sale">Sold Units (Direct Batch Decrement)</option>
                <option value="stocktake_correction">Physical Inventory Count Correction</option>
                <option value="store_consumption">In-Store Sample / Testing</option>
              </select>
            </div>

            <div className="form-group">
              <label>Current Physical Stock in Batch: <strong>{currentQty} units</strong></label>
              <div style={{ display: "flex", gap: 8, marginTop: 6, marginBottom: 12 }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: 12, padding: "4px 10px" }}
                  onClick={() => setNewQuantity(Math.max(0, currentQty - 1))}
                >
                  -1 Unit
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: 12, padding: "4px 10px" }}
                  onClick={() => setNewQuantity(Math.max(0, currentQty - 5))}
                >
                  -5 Units
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: 12, padding: "4px 10px" }}
                  onClick={() => setNewQuantity(Math.max(0, currentQty - 10))}
                >
                  -10 Units
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: 12, padding: "4px 10px", color: "#dc2626" }}
                  onClick={() => setNewQuantity(0)}
                >
                  Clear to 0
                </button>
              </div>

              <label style={{ fontSize: 13, fontWeight: 600, color: "#334155" }}>
                New Batch Stock Quantity *
              </label>
              <input
                type="number"
                min="0"
                value={newQuantity}
                onChange={(e) => setNewQuantity(Math.max(0, parseInt(e.target.value, 10) || 0))}
                required
              />
            </div>

            <div style={{ fontSize: 13, color: difference < 0 ? "#dc2626" : difference > 0 ? "#059669" : "#64748b", fontWeight: 600 }}>
              {difference < 0
                ? `Net Adjustment: Decrementing batch by ${Math.abs(difference)} unit(s)`
                : difference > 0
                ? `Net Adjustment: Incrementing batch by ${difference} unit(s)`
                : "No change in quantity"}
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Updating..." : "Save Stock Adjustment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
