import { useState } from "react";

export default function AddProductModal({ isOpen, onClose, onProductAdded, API }) {
  const [formData, setFormData] = useState({
    product_name: "",
    category: "Dairy",
    unit: "kg",
    purchase_price: "",
    selling_price: "",
    shelf_life_days: "",
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
        product_name: formData.product_name.trim(),
        category: formData.category,
        unit: formData.unit,
        purchase_price: parseFloat(formData.purchase_price) || 0,
        selling_price: parseFloat(formData.selling_price) || 0,
        shelf_life_days: parseInt(formData.shelf_life_days, 10),
      };

      if (!payload.product_name) {
        throw new Error("Product name is required.");
      }
      if (isNaN(payload.shelf_life_days) || payload.shelf_life_days <= 0) {
        throw new Error("Shelf life must be a positive integer.");
      }

      const res = await fetch(`${API}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to create product.");
      }

      const created = await res.json();
      onProductAdded(created);
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
          <h3>Add New Perishable Product</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div style={{ color: "#dc3545", marginBottom: 12, fontSize: 13 }}>⚠️ {error}</div>}
            <div className="form-group">
              <label>Product Name *</label>
              <input
                type="text"
                placeholder="e.g. Greek Yogurt, Strawberries"
                value={formData.product_name}
                onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  <option value="Dairy">Dairy</option>
                  <option value="Bakery">Bakery</option>
                  <option value="Vegetable">Vegetable</option>
                  <option value="Fruit">Fruit</option>
                  <option value="Meat">Meat</option>
                </select>
              </div>

              <div className="form-group">
                <label>Unit</label>
                <select
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                >
                  <option value="kg">kg</option>
                  <option value="litre">litre</option>
                  <option value="packet">packet</option>
                  <option value="piece">piece</option>
                  <option value="dozen">dozen</option>
                  <option value="gram">gram</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Purchase Price (₹)</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  placeholder="e.g. 40.00"
                  value={formData.purchase_price}
                  onChange={(e) => setFormData({ ...formData, purchase_price: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Selling Price (₹)</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  placeholder="e.g. 55.00"
                  value={formData.selling_price}
                  onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Shelf Life (Days) *</label>
              <input
                type="number"
                min="1"
                placeholder="e.g. 5"
                value={formData.shelf_life_days}
                onChange={(e) => setFormData({ ...formData, shelf_life_days: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Saving..." : "Save Product"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
