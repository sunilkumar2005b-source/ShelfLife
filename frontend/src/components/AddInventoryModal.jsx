import { useState } from "react";

export default function AddInventoryModal({ isOpen, onClose, onInventoryAdded, products, API }) {
  const [formData, setFormData] = useState({
    product_id: products[0]?.product_id || 1,
    batch_number: "",
    quantity: "",
    purchase_date: new Date().toISOString().slice(0, 10),
    expiry_date: "",
    storage_temperature: "4.0",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

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
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Add New Inventory Batch</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div style={{ color: "#dc3545", marginBottom: 12, fontSize: 13 }}>⚠️ {error}</div>}

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

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Saving..." : "Save Batch"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
