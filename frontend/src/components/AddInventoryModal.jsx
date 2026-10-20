import { useState, useEffect } from "react";

export default function AddInventoryModal({
  isOpen,
  onClose,
  onInventoryAdded,
  products = [],
  API,
  initialProductId = null,
}) {
  const [formData, setFormData] = useState({
    product_id: initialProductId || products[0]?.product_id || 1,
    batch_number: "",
    quantity: "20",
    purchase_date: new Date().toISOString().slice(0, 10),
    expiry_date: "",
    storage_temperature: "4.0",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  // Auto-populate when modal opens or initialProductId changes
  useEffect(() => {
    if (!isOpen) return;

    const targetId = initialProductId || formData.product_id || products[0]?.product_id;
    const selectedProd = products.find((p) => p.product_id === Number(targetId)) || products[0];

    if (selectedProd) {
      const shelfDays = selectedProd.shelf_life_days || 7;
      const exp = new Date();
      exp.setDate(exp.getDate() + shelfDays);

      let defTemp = "4.0";
      if (selectedProd.category === "Bakery") defTemp = "18.0";
      else if (selectedProd.category === "Vegetable") defTemp = "12.0";
      else if (selectedProd.category === "Fruit") defTemp = "10.0";
      else if (selectedProd.category === "Meat") defTemp = "2.0";

      const prefix = selectedProd.product_name
        .replace(/[^a-zA-Z]/g, "")
        .slice(0, 4)
        .toUpperCase() || "BATCH";
      const randomSuffix = Math.floor(Math.random() * 90) + 10;

      setFormData({
        product_id: selectedProd.product_id,
        batch_number: `${prefix}-B0${randomSuffix}`,
        quantity: "25",
        purchase_date: new Date().toISOString().slice(0, 10),
        expiry_date: exp.toISOString().slice(0, 10),
        storage_temperature: defTemp,
      });
      setError("");
    }
  }, [isOpen, initialProductId, products]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const payload = {
        product_id: parseInt(formData.product_id, 10),
        batch_number: formData.batch_number.trim() || undefined,
        quantity: parseInt(formData.quantity, 10),
        purchase_date: formData.purchase_date || undefined,
        expiry_date: formData.expiry_date,
        storage_temperature: formData.storage_temperature ? parseFloat(formData.storage_temperature) : undefined,
      };

      if (!payload.product_id) {
        throw new Error("Please select a product.");
      }
      if (isNaN(payload.quantity) || payload.quantity < 0) {
        throw new Error("Quantity must be 0 or greater.");
      }
      if (!payload.expiry_date) {
        throw new Error("Expiry date is required.");
      }

      const res = await fetch(`${API}/inventory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to add inventory batch.");
      }

      const created = await res.json();
      onInventoryAdded(created);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-dialog"
        onClick={(e) => e.stopPropagation()}
        style={{
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <div className="modal-header">
          <h3>Add New Inventory Batch</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            flex: 1,
            minHeight: 0,
            overflow: "hidden",
          }}
        >
          <div className="modal-body" style={{ overflowY: "auto", flex: 1, padding: "20px 24px" }}>
            {error && (
              <div
                style={{
                  background: "#fef2f2",
                  color: "#dc2626",
                  padding: "10px 14px",
                  borderRadius: 6,
                  border: "1px solid #fecaca",
                  marginBottom: 16,
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                {error}
              </div>
            )}

            <div className="form-group">
              <label>Select Product *</label>
              <select
                value={formData.product_id}
                onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                required
              >
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_name} ({p.category}) - Shelf Life: {p.shelf_life_days}d
                  </option>
                ))}
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Batch Code</label>
                <input
                  type="text"
                  placeholder="e.g. MILK-B002"
                  value={formData.batch_number}
                  onChange={(e) => setFormData({ ...formData, batch_number: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Quantity (Units) *</label>
                <input
                  type="number"
                  min="0"
                  placeholder="e.g. 20"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Purchase Date</label>
                <input
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Expiry Date *</label>
                <input
                  type="date"
                  value={formData.expiry_date}
                  onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Storage Temperature (°C)</label>
              <input
                type="number"
                step="0.5"
                placeholder="e.g. 4.0"
                value={formData.storage_temperature}
                onChange={(e) => setFormData({ ...formData, storage_temperature: e.target.value })}
              />
            </div>
          </div>

          <div
            className="modal-footer"
            style={{
              padding: "14px 24px",
              background: "#f8fafc",
              borderTop: "1px solid #e2e8f0",
              display: "flex",
              justifyContent: "flex-end",
              alignItems: "center",
              gap: 12,
              flexShrink: 0,
            }}
          >
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              style={{ padding: "8px 16px" }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
              style={{
                padding: "8px 22px",
                fontWeight: 700,
                fontSize: 13.5,
                background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                boxShadow: "0 2px 8px rgba(16, 185, 129, 0.3)",
                cursor: submitting ? "not-allowed" : "pointer",
              }}
            >
              {submitting ? "Saving..." : "Save Batch"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
