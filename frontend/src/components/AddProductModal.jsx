import { useState } from "react";

export default function AddProductModal({ isOpen, onClose, onProductAdded, API }) {
  const [formData, setFormData] = useState({
    product_name: "",
    category: "Dairy",
    unit: "kg",
    purchase_price: "",
    selling_price: "",
    shelf_life_days: "7",
    initial_stock: "20",
    storage_temperature: "4.0",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const name = (formData.product_name || "").trim();
    const purchase = parseFloat(formData.purchase_price);
    const selling = parseFloat(formData.selling_price);
    const shelfLife = parseInt(formData.shelf_life_days, 10);

    if (!name) {
      setError("Please enter a Product Name (e.g. Cheese, Strawberries, Milk).");
      return;
    }
    if (isNaN(purchase) || purchase <= 0) {
      setError("Please enter a valid Purchase Price greater than 0.");
      return;
    }
    if (isNaN(selling) || selling <= 0) {
      setError("Please enter a valid Selling Price greater than 0.");
      return;
    }
    if (isNaN(shelfLife) || shelfLife <= 0) {
      setError("Please enter Shelf Life in days (e.g. 5, 7, 14).");
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        product_name: name,
        category: formData.category,
        unit: formData.unit,
        purchase_price: purchase,
        selling_price: selling,
        shelf_life_days: shelfLife,
      };

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

      // Automatically register initial inventory batch if initial stock is specified
      const initialQty = parseInt(formData.initial_stock, 10);
      if (!isNaN(initialQty) && initialQty > 0) {
        const expDate = new Date();
        expDate.setDate(expDate.getDate() + payload.shelf_life_days);
        const expDateStr = expDate.toISOString().slice(0, 10);

        const prefix = created.product_name
          .replace(/[^a-zA-Z]/g, "")
          .slice(0, 4)
          .toUpperCase() || "BATCH";
        const batchCode = `${prefix}-B001`;

        const batchPayload = {
          product_id: created.product_id,
          batch_number: batchCode,
          quantity: initialQty,
          purchase_date: new Date().toISOString().slice(0, 10),
          expiry_date: expDateStr,
          storage_temperature: parseFloat(formData.storage_temperature) || 4.0,
        };

        await fetch(`${API}/inventory`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(batchPayload),
        }).catch((err) => console.warn("Initial batch creation failed:", err));
      }

      onProductAdded(created);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCategoryChange = (newCat) => {
    let defaultTemp = "4.0";
    if (newCat === "Bakery") defaultTemp = "18.0";
    else if (newCat === "Vegetable") defaultTemp = "12.0";
    else if (newCat === "Fruit") defaultTemp = "10.0";
    else if (newCat === "Meat") defaultTemp = "2.0";

    setFormData({
      ...formData,
      category: newCat,
      storage_temperature: defaultTemp,
    });
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
          <h3>Add New Perishable Product</h3>
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
              <label>Product Name *</label>
              <input
                type="text"
                placeholder="e.g. Greek Yogurt, Strawberries, Cheese"
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
                  onChange={(e) => handleCategoryChange(e.target.value)}
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
                <label>Purchase Price (₹) *</label>
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
                <label>Selling Price (₹) *</label>
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
                placeholder="e.g. 7"
                value={formData.shelf_life_days}
                onChange={(e) => setFormData({ ...formData, shelf_life_days: e.target.value })}
                required
              />
            </div>

            {/* Initial Stock on Hand Section */}
            <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px dashed #cbd5e1" }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 8 }}>
                Initial Inventory Stock (Optional)
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Initial Stock on Hand (Units)</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="e.g. 20"
                    value={formData.initial_stock}
                    onChange={(e) => setFormData({ ...formData, initial_stock: e.target.value })}
                  />
                  <small style={{ color: "#64748b", fontSize: 11 }}>
                    Automatically creates initial batch with expiry date
                  </small>
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
                  <small style={{ color: "#64748b", fontSize: 11 }}>
                    Optimal storage conditions
                  </small>
                </div>
              </div>
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
              {submitting ? "Saving..." : "Save Product & Stock"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
