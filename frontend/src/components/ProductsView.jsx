import { useState, useMemo } from "react";
import { CartIcon, PlusIcon } from "./Icons";

export default function ProductsView({
  products = [],
  inventory = [],
  suppliers = [],
  onOpenAddModal,
  onOpenRecordSale,
  onOpenAddBatch,
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [sortField, setSortField] = useState("product_name");
  const [sortDirection, setSortDirection] = useState("asc");

  const categories = useMemo(() => {
    return ["all", ...new Set(products.map((p) => p.category).filter(Boolean))];
  }, [products]);

  // Compute on-hand stock and batch count per product
  const stockByProductId = useMemo(() => {
    return inventory.reduce((acc, item) => {
      acc[item.product_id] = (acc[item.product_id] || 0) + (Number(item.quantity) || 0);
      return acc;
    }, {});
  }, [inventory]);

  const batchCountByProductId = useMemo(() => {
    return inventory.reduce((acc, item) => {
      acc[item.product_id] = (acc[item.product_id] || 0) + 1;
      return acc;
    }, {});
  }, [inventory]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const getSupplierName = (product) => {
    if (product.category === "Dairy") return "Fresh Dairy Suppliers";
    if (product.category === "Bakery") return "Daily Bakery Foods";
    if (product.category === "Vegetable") return "Green Fresh Vegetables";
    if (product.category === "Fruit") return "Fruit World Suppliers";
    return suppliers[0]?.supplier_name || "Authorized Vendor";
  };

  const processedProducts = useMemo(() => {
    return products
      .map((p) => {
        const purchase = Number(p.purchase_price) || 0;
        const selling = Number(p.selling_price) || 0;
        const marginPct = selling > 0 ? Math.round(((selling - purchase) / selling) * 100) : 0;
        const onHand = stockByProductId[p.product_id] || 0;
        const batchCount = batchCountByProductId[p.product_id] || 0;
        return {
          ...p,
          marginPct,
          onHand,
          batchCount,
          supplierName: getSupplierName(p),
        };
      })
      .filter((p) => {
        const nameMatch =
          p.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (p.category && p.category.toLowerCase().includes(searchTerm.toLowerCase()));
        const catMatch = selectedCategory === "all" || p.category === selectedCategory;
        return nameMatch && catMatch;
      })
      .sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];

        if (typeof valA === "string") valA = valA.toLowerCase();
        if (typeof valB === "string") valB = valB.toLowerCase();

        if (valA < valB) return sortDirection === "asc" ? -1 : 1;
        if (valA > valB) return sortDirection === "asc" ? 1 : -1;
        return 0;
      });
  }, [products, stockByProductId, searchTerm, selectedCategory, sortField, sortDirection, suppliers]);

  return (
    <>
      <div className="table-toolbar" style={{ justifyContent: "flex-end", marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            className="btn btn-primary"
            onClick={() => onOpenRecordSale && onOpenRecordSale()}
            style={{
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              fontWeight: 700,
              boxShadow: "0 2px 8px rgba(16, 185, 129, 0.3)",
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
            }}
            title="Record customer sale & deduct stock via FEFO"
          >
            <CartIcon size={15} /> Record Sale (POS)
          </button>
          <button className="btn btn-secondary" onClick={onOpenAddModal} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <PlusIcon size={14} /> Add New Product
          </button>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setSelectedCategory(c)}
            className={`btn ${selectedCategory === c ? "btn-primary" : "btn-secondary"}`}
            style={{ fontSize: 12.5, padding: "6px 14px", textTransform: "capitalize" }}
          >
            {c === "all" ? "All Categories" : c}
          </button>
        ))}
      </div>

      <div className="section" style={{ marginTop: 0 }}>
        <div className="table-toolbar" style={{ marginBottom: 16 }}>
          <div style={{ position: "relative", width: 320, maxWidth: "100%" }}>
            <input
              type="text"
              className="search-input"
              placeholder="Search product title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: "100%", paddingRight: searchTerm ? 32 : 14 }}
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                style={{
                  position: "absolute",
                  right: 10,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  color: "#94a3b8",
                  fontSize: 14,
                }}
                title="Clear search"
              >
                &times;
              </button>
            )}
          </div>

          <div style={{ fontSize: 13, color: "#64748b" }}>
            Showing <strong>{processedProducts.length}</strong> of {products.length} products
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th className="sortable" onClick={() => handleSort("product_id")}>
                  ID {sortField === "product_id" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("product_name")}>
                  Product Name {sortField === "product_name" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("category")}>
                  Category {sortField === "category" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("onHand")}>
                  Stock On-Hand {sortField === "onHand" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th>Unit</th>
                <th className="sortable" onClick={() => handleSort("purchase_price")}>
                  Cost Price {sortField === "purchase_price" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("selling_price")}>
                  Selling Price {sortField === "selling_price" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("marginPct")}>
                  Margin {sortField === "marginPct" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th className="sortable" onClick={() => handleSort("shelf_life_days")}>
                  Shelf Life {sortField === "shelf_life_days" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
                </th>
                <th>Supplier</th>
                <th style={{ textAlign: "center" }}>POS Action</th>
              </tr>
            </thead>
            <tbody>
              {processedProducts.length === 0 ? (
                <tr>
                  <td colSpan="11" style={{ textAlign: "center", padding: 30, color: "#64748b" }}>
                    No products matching your search or category selection.
                  </td>
                </tr>
              ) : (
                processedProducts.map((p) => (
                  <tr key={p.product_id}>
                    <td>
                      <code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: 4, fontSize: 12 }}>
                        #{p.product_id}
                      </code>
                    </td>
                    <td>
                      <strong style={{ color: "#0f172a" }}>{p.product_name}</strong>
                    </td>
                    <td>
                      <span className="badge" style={{ background: "#f1f5f9", color: "#334155" }}>
                        {p.category}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
                        <strong style={{ color: p.onHand > 0 ? "#059669" : "#dc2626", fontSize: 14 }}>
                          {p.onHand}
                        </strong>
                        <span style={{ fontSize: 12, color: "#64748b" }}>{p.unit}</span>
                        {p.batchCount > 1 && (
                          <span
                            style={{
                              fontSize: 10.5,
                              color: "#475569",
                              background: "#f1f5f9",
                              border: "1px solid #e2e8f0",
                              padding: "1px 5px",
                              borderRadius: 4,
                            }}
                            title={`${p.batchCount} active batches in inventory`}
                          >
                            {p.batchCount} batches
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ color: "#64748b" }}>{p.unit}</td>
                    <td>₹{Number(p.purchase_price).toFixed(2)}</td>
                    <td>
                      <strong style={{ color: "#0f172a" }}>₹{Number(p.selling_price).toFixed(2)}</strong>
                    </td>
                    <td>
                      <span
                        className="badge"
                        style={{
                          background: p.marginPct >= 30 ? "#ecfdf5" : "#fffbeb",
                          color: p.marginPct >= 30 ? "#065f46" : "#92400e",
                          border: `1px solid ${p.marginPct >= 30 ? "#a7f3d0" : "#fde68a"}`,
                        }}
                      >
                        +{p.marginPct}%
                      </span>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: p.shelf_life_days <= 3 ? "#dc2626" : "#334155" }}>
                        {p.shelf_life_days} days
                      </span>
                    </td>
                    <td style={{ fontSize: 12.5, color: "#475569" }}>{p.supplierName}</td>
                    <td style={{ textAlign: "center" }}>
                      <button
                        className="btn btn-primary"
                        onClick={() => onOpenRecordSale && onOpenRecordSale(p.product_id)}
                        disabled={p.onHand <= 0}
                        style={{
                          padding: "4px 12px",
                          fontSize: 12,
                          background: p.onHand > 0 ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "#cbd5e1",
                          cursor: p.onHand > 0 ? "pointer" : "not-allowed",
                        }}
                        title={p.onHand > 0 ? "Sell units of this product via POS" : "Out of stock"}
                      >
                        Sell
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
