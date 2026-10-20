import { useState, useEffect, useMemo } from "react";
import API_BASE from "../apiConfig";

export default function RecordSaleModal({
  isOpen,
  onClose,
  products = [],
  inventory = [],
  onSaleCompleted,
  API = API_BASE,
  initialProductId = null,
  showToast,
}) {
  const [selectedProductId, setSelectedProductId] = useState("");
  const [quantitySold, setQuantitySold] = useState(1);
  const [customPrice, setCustomPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Set initial product when opened
  useEffect(() => {
    if (isOpen) {
      setError("");
      if (initialProductId) {
        setSelectedProductId(String(initialProductId));
      } else if (products.length > 0 && !selectedProductId) {
        setSelectedProductId(String(products[0].product_id));
      }
    }
  }, [isOpen, initialProductId, products]);

  // Selected product details
  const selectedProduct = useMemo(() => {
    return products.find((p) => String(p.product_id) === String(selectedProductId)) || null;
  }, [products, selectedProductId]);

  // Update default price when selected product changes
  useEffect(() => {
    if (selectedProduct) {
      setCustomPrice(Number(selectedProduct.selling_price || 0).toFixed(2));
      setQuantitySold(1);
    }
  }, [selectedProduct]);

  // Active batches for this product with quantity > 0, ordered by expiry date (FEFO)
  const productBatches = useMemo(() => {
    if (!selectedProductId) return [];
    return inventory
      .filter((i) => String(i.product_id) === String(selectedProductId) && Number(i.quantity) > 0)
      .sort((a, b) => new Date(a.expiry_date) - new Date(b.expiry_date));
  }, [inventory, selectedProductId]);

  // Total available stock across all active batches
  const totalAvailableStock = useMemo(() => {
    return productBatches.reduce((sum, b) => sum + (Number(b.quantity) || 0), 0);
  }, [productBatches]);

  // FEFO preview: show how the requested quantity will be deducted from batches
  const fefoPreview = useMemo(() => {
    const qty = Number(quantitySold) || 0;
    if (qty <= 0 || productBatches.length === 0) return [];

    let remaining = qty;
    const plan = [];

    for (const b of productBatches) {
      if (remaining <= 0) break;
      const bQty = Number(b.quantity) || 0;
      const deduct = Math.min(bQty, remaining);
      plan.push({
        batch_number: b.batch_number || `BATCH-${b.inventory_id}`,
        expiry_date: b.expiry_date,
        current_qty: bQty,
        deduct_qty: deduct,
        remaining_qty: bQty - deduct,
      });
      remaining -= deduct;
    }
    return plan;
  }, [productBatches, quantitySold]);

  if (!isOpen) return null;

  const unitPrice = parseFloat(customPrice) || 0;
  const totalBill = (unitPrice * (Number(quantitySold) || 0)).toFixed(2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const qty = parseInt(quantitySold, 10);
    if (isNaN(qty) || qty <= 0) {
      setError("Please enter a valid quantity sold (at least 1).");
      return;
    }

    if (qty > totalAvailableStock) {
      setError(`Cannot sell ${qty} units. Only ${totalAvailableStock} unit(s) in stock!`);
      return;
    }

    setLoading(true);
    try {
      const payload = {
        product_id: parseInt(selectedProductId, 10),
        quantity_sold: qty,
        selling_price: unitPrice,
      };

      const response = await fetch(`${API}/sales`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to record sale.");
      }

      const saleData = await response.json();
      if (showToast) {
        showToast(
          `Sale Recorded: ${qty}x "${selectedProduct?.product_name || "item"}" sold (₹${totalBill}). Stock deducted via FEFO!`,
          "success"
        );
      }

      if (onSaleCompleted) {
        onSaleCompleted(saleData);
      }
      onClose();
    } catch (err) {
      setError(err.message || "Failed to process sale.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 580 }}>
        <div className="modal-header" style={{ background: "linear-gradient(135deg, #059669 0%, #047857 100%)" }}>
          <h3>Record Sale & Deduct Inventory (POS Checkout)</h3>
          <button className="modal-close" onClick={onClose} title="Close">
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <p style={{ margin: "0 0 16px", fontSize: 13, color: "#64748b" }}>
              Records a customer sale transaction and automatically deducts units from the oldest expiring batches via <strong>FEFO (First-Expired, First-Out)</strong>.
            </p>

            {error && (
              <div style={{ background: "#fef2f2", color: "#991b1b", padding: "10px 14px", borderRadius: 8, fontSize: 13, marginBottom: 14, border: "1px solid #fecaca" }}>
                {error}
              </div>
            )}

            {/* Product selection */}
            <div className="form-group">
              <label>Select Perishable Product *</label>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                required
              >
                {products.map((p) => {
                  const stock = inventory
                    .filter((i) => i.product_id === p.product_id)
                    .reduce((sum, i) => sum + (Number(i.quantity) || 0), 0);
                  return (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_name} ({p.category}) — {stock} in stock
                    </option>
                  );
                })}
              </select>
            </div>

            {/* Stock indicator badge */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#f8fafc", padding: "10px 14px", borderRadius: 8, border: "1px solid #e2e8f0", marginBottom: 16 }}>
              <div>
                <span style={{ fontSize: 12, color: "#64748b" }}>Available On-Hand Stock:</span>
                <div style={{ fontSize: 18, fontWeight: 800, color: totalAvailableStock > 0 ? "#059669" : "#dc2626" }}>
                  {totalAvailableStock} units available
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: 12, color: "#64748b" }}>Active Batches:</span>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#334155" }}>
                  {productBatches.length} batch(es)
                </div>
              </div>
            </div>

            {/* Quantity and price row */}
            <div className="form-row">
              <div className="form-group">
                <label>Quantity to Sell *</label>
                <input
                  type="number"
                  min="1"
                  max={totalAvailableStock || 1}
                  value={quantitySold}
                  onChange={(e) => setQuantitySold(Math.max(1, parseInt(e.target.value, 10) || 1))}
                  required
                />
              </div>

              <div className="form-group">
                <label>Selling Price per Unit (₹) *</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  value={customPrice}
                  onChange={(e) => setCustomPrice(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Bill Summary */}
            <div style={{ background: "#ecfdf5", border: "1px solid #a7f3d0", padding: "12px 16px", borderRadius: 8, marginBottom: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontWeight: 600, color: "#065f46", fontSize: 14 }}>
                Total Sale Revenue:
              </span>
              <span style={{ fontSize: 22, fontWeight: 800, color: "#047857" }}>
                ₹{totalBill}
              </span>
            </div>

            {/* FEFO Deduction Preview Box */}
            {fefoPreview.length > 0 && (
              <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "10px 14px", marginBottom: 12 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#475569", marginBottom: 6, display: "flex", alignItems: "center", gap: 6 }}>
                  <span>FEFO Deduction Plan (Oldest Batches First):</span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {fefoPreview.map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: 12,
                        padding: "4px 8px",
                        background: "#ffffff",
                        borderRadius: 6,
                        border: "1px solid #e2e8f0",
                      }}
                    >
                      <span>
                        <code>{item.batch_number}</code> (Exp: {item.expiry_date})
                      </span>
                      <span style={{ fontWeight: 600, color: "#dc2626" }}>
                        -{item.deduct_qty} unit(s) &rarr; {item.remaining_qty} left
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || totalAvailableStock <= 0}
              style={{ background: "linear-gradient(135deg, #059669 0%, #047857 100%)" }}
            >
              {loading ? "Processing Sale..." : "Complete Sale & Deduct Stock"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
