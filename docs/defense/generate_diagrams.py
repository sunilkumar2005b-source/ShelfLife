"""
Script to generate high-resolution professional diagrams for the ShelfLife Review-2 PPT.
Generates:
1. docs/defense/uml_class_diagram.png
2. docs/defense/system_architecture_diagram.png
3. docs/defense/activity_workflow_diagram.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path("docs/defense")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. UML CLASS DIAGRAM
# -------------------------------------------------------------
def generate_class_diagram():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")

    # Title
    ax.text(7, 8.6, "ShelfLife - UML Class Diagram", fontsize=18, fontweight="bold", ha="center", color="#0f172a")

    def draw_class(x, y, w, h, title, attributes, methods, bg="#f8fafc", border="#334155"):
        # Header box
        hdr_h = 0.55
        rect_hdr = patches.FancyBboxPatch((x, y + h - hdr_h), w, hdr_h, boxstyle="square,pad=0",
                                          facecolor="#1e293b", edgecolor=border, linewidth=1.5)
        ax.add_patch(rect_hdr)
        ax.text(x + w/2, y + h - hdr_h/2, title, fontsize=11, fontweight="bold", ha="center", va="center", color="#ffffff")

        # Body box
        rect_body = patches.FancyBboxPatch((x, y), w, h - hdr_h, boxstyle="square,pad=0",
                                           facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect_body)

        # Content text
        curr_y = y + h - hdr_h - 0.25
        for attr in attributes:
            ax.text(x + 0.15, curr_y, attr, fontsize=8.5, va="center", color="#1e293b", family="monospace")
            curr_y -= 0.24

        # Divider line between attributes and methods
        curr_y -= 0.05
        ax.plot([x, x + w], [curr_y, curr_y], color="#cbd5e1", linewidth=1)
        curr_y -= 0.2

        for meth in methods:
            ax.text(x + 0.15, curr_y, meth, fontsize=8.5, va="center", color="#0369a1", family="monospace", fontweight="bold")
            curr_y -= 0.24

    # Class 1: Product
    draw_class(0.6, 5.0, 3.4, 3.0, "Product", [
        "- product_id: int",
        "- product_name: str",
        "- category: str",
        "- purchase_price: float",
        "- selling_price: float",
        "- shelf_life_days: int"
    ], [
        "+ get_profit_margin(): float",
        "+ get_active_batches(): List"
    ])

    # Class 2: InventoryBatch
    draw_class(5.3, 5.0, 3.4, 3.0, "InventoryBatch", [
        "- inventory_id: int",
        "- product_id: int",
        "- batch_number: str",
        "- quantity: int",
        "- purchase_date: date",
        "- expiry_date: date",
        "- storage_temp: float"
    ], [
        "+ get_days_remaining(): int",
        "+ deduct_stock(qty: int)",
        "+ is_expired(): bool"
    ])

    # Class 3: Supplier
    draw_class(10.0, 5.0, 3.4, 3.0, "Supplier", [
        "- supplier_id: int",
        "- name: str",
        "- lead_time_days: int",
        "- min_order_qty: int",
        "- contact_phone: str"
    ], [
        "+ place_purchase_order()",
        "+ evaluate_lead_time()"
    ])

    # Class 4: SaleRecord
    draw_class(0.6, 1.0, 3.4, 3.0, "SaleRecord", [
        "- sale_id: int",
        "- product_id: int",
        "- quantity_sold: int",
        "- selling_price: float",
        "- sale_date: date",
        "- sale_time: time"
    ], [
        "+ compute_revenue(): float",
        "+ log_transaction()"
    ])

    # Class 5: SpoilagePrediction
    draw_class(5.3, 1.0, 3.4, 3.0, "SpoilagePrediction", [
        "- prediction_id: int",
        "- inventory_id: int",
        "- spoilage_prob: float",
        "- risk_level: str",
        "- prediction_date: date",
        "- model_name: str"
    ], [
        "+ is_high_risk(): bool",
        "+ get_degradation_tier()"
    ])

    # Class 6: DecisionEngine
    draw_class(10.0, 1.0, 3.4, 3.0, "DecisionEngine", [
        "- health_score (H): float",
        "- recommendation: str",
        "- markdown_pct: float",
        "- preserved_capital: float"
    ], [
        "+ eval_health_score(H)",
        "+ execute_fefo_deduct()",
        "+ simulate_markdown()"
    ])

    # Connecting lines & multiplicities
    # Product -> InventoryBatch (1 to *)
    ax.annotate("", xy=(5.3, 6.5), xytext=(4.0, 6.5),
                arrowprops=dict(arrowstyle="-", color="#334155", lw=1.5))
    ax.text(4.15, 6.65, "1", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(5.05, 6.65, "*", fontsize=11, fontweight="bold", color="#1e293b")
    ax.text(4.65, 6.8, "has batches", fontsize=8.5, style="italic", ha="center", color="#64748b")

    # InventoryBatch -> Supplier (* to 1)
    ax.annotate("", xy=(10.0, 6.5), xytext=(8.7, 6.5),
                arrowprops=dict(arrowstyle="-", color="#334155", lw=1.5))
    ax.text(8.85, 6.65, "*", fontsize=11, fontweight="bold", color="#1e293b")
    ax.text(9.8, 6.65, "1", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(9.35, 6.8, "supplied by", fontsize=8.5, style="italic", ha="center", color="#64748b")

    # Product -> SaleRecord (1 to *)
    ax.annotate("", xy=(2.3, 4.0), xytext=(2.3, 5.0),
                arrowprops=dict(arrowstyle="-", color="#334155", lw=1.5))
    ax.text(2.45, 4.8, "1", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(2.45, 4.15, "*", fontsize=11, fontweight="bold", color="#1e293b")
    ax.text(1.7, 4.5, "records", fontsize=8.5, style="italic", ha="center", color="#64748b")

    # InventoryBatch -> SpoilagePrediction (1 to *)
    ax.annotate("", xy=(7.0, 4.0), xytext=(7.0, 5.0),
                arrowprops=dict(arrowstyle="-", color="#334155", lw=1.5))
    ax.text(7.15, 4.8, "1", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(7.15, 4.15, "*", fontsize=11, fontweight="bold", color="#1e293b")
    ax.text(6.3, 4.5, "evaluates", fontsize=8.5, style="italic", ha="center", color="#64748b")

    # SpoilagePrediction -> DecisionEngine (* to 1)
    ax.annotate("", xy=(10.0, 2.5), xytext=(8.7, 2.5),
                arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5))
    ax.text(9.35, 2.7, "triggers", fontsize=8.5, style="italic", ha="center", color="#64748b")

    plt.tight_layout()
    out_path = OUT_DIR / "uml_class_diagram.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_path}")

# -------------------------------------------------------------
# 2. SYSTEM ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.5)
    ax.axis("off")

    ax.text(7.5, 9.1, "SYSTEM ARCHITECTURE - ShelfLife", fontsize=19, fontweight="bold", ha="center", color="#0f172a")

    # 1. Frontend
    rf = patches.FancyBboxPatch((0.8, 7.3), 13.4, 1.45, boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor="#f0fdf4", edgecolor="#16a34a", linewidth=2)
    ax.add_patch(rf)
    ax.text(7.5, 8.45, "Frontend Layer (React 19 + Vite 8 SPA)", fontsize=13, fontweight="bold", ha="center", color="#166534")

    fe_boxes = [
        "Executive\nDashboard", "Inventory\nBatches", "Products\nCatalog", "POS\nCheckout",
        "Spoilage\nRisk Radar", "Demand\nForecasts", "Decision\nEngine", "Simulators\n(Markdown)"
    ]
    w_box = 1.45
    for i, b in enumerate(fe_boxes):
        bx = 1.1 + i * 1.62
        r = patches.FancyBboxPatch((bx, 7.42), w_box, 0.78, boxstyle="square,pad=0",
                                   facecolor="#ffffff", edgecolor="#86efac", linewidth=1.2)
        ax.add_patch(r)
        ax.text(bx + w_box/2, 7.81, b, fontsize=8.5, ha="center", va="center", color="#0f172a", fontweight="600")

    # Arrow 1: Frontend <-> Backend
    ax.annotate("", xy=(7.3, 6.75), xytext=(7.3, 7.25),
                arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2))
    ax.annotate("", xy=(7.7, 7.25), xytext=(7.7, 6.75),
                arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2))
    ax.text(8.7, 7.0, "HTTP / JSON REST APIs (Axios / Fetch)", fontsize=9, color="#0369a1", fontweight="bold")

    # 2. Backend
    rb = patches.FancyBboxPatch((0.8, 5.5), 13.4, 1.25, boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor="#eff6ff", edgecolor="#2563eb", linewidth=2)
    ax.add_patch(rb)
    ax.text(7.5, 6.45, "Backend API Gateway (FastAPI Framework)", fontsize=13, fontweight="bold", ha="center", color="#1e40af")

    be_boxes = ["/products", "/inventory", "/sales", "/ml/*", "/inventory-intelligence", "/reports/*", "/demo/*"]
    w_be = 1.65
    for i, b in enumerate(be_boxes):
        bx = 1.15 + i * 1.86
        r = patches.FancyBboxPatch((bx, 5.62), w_be, 0.62, boxstyle="square,pad=0",
                                   facecolor="#ffffff", edgecolor="#93c5fd", linewidth=1.2)
        ax.add_patch(r)
        ax.text(bx + w_be/2, 5.93, b, fontsize=9, ha="center", va="center", color="#1e3a8a", fontweight="bold", family="monospace")

    # Down arrows to services
    ax.annotate("", xy=(3.0, 4.8), xytext=(3.0, 5.45), arrowprops=dict(arrowstyle="->", color="#475569", lw=2))
    ax.annotate("", xy=(7.5, 4.8), xytext=(7.5, 5.45), arrowprops=dict(arrowstyle="->", color="#475569", lw=2))
    ax.annotate("", xy=(12.0, 4.8), xytext=(12.0, 5.45), arrowprops=dict(arrowstyle="->", color="#475569", lw=2))

    # 3. Middle Tier: 3 Domain Services
    # Left: AI & ML Services
    rs1 = patches.FancyBboxPatch((0.8, 2.7), 4.2, 2.05, boxstyle="round,pad=0.1,rounding_size=0.1",
                                 facecolor="#faf5ff", edgecolor="#7c3aed", linewidth=1.8)
    ax.add_patch(rs1)
    ax.text(2.9, 4.45, "AI & MACHINE LEARNING", fontsize=11, fontweight="bold", ha="center", color="#5b21b6")
    ml_items = [
        "- StandardScaler + OneHotEncoder",
        "- Ridge Regression (alpha=1.0)",
        "- Class-Weighted Logistic Reg.",
        "- Sub-2ms Batch Inference"
    ]
    for idx, item in enumerate(ml_items):
        ax.text(1.0, 4.05 - idx * 0.38, item, fontsize=8.5, color="#3b0764", family="sans-serif")

    # Middle: Rule Engine Core
    rs2 = patches.FancyBboxPatch((5.4, 2.7), 4.2, 2.05, boxstyle="round,pad=0.1,rounding_size=0.1",
                                 facecolor="#fefce8", edgecolor="#ca8a04", linewidth=1.8)
    ax.add_patch(rs2)
    ax.text(7.5, 4.45, "RULE ENGINE CORE", fontsize=11, fontweight="bold", ha="center", color="#854d0e")
    rule_items = [
        "- Composite Health Score (H: 0-100)",
        "- Multi-Factor Action Triggers",
        "- Atomic Multi-Batch FEFO Engine",
        "- Natural Language Explanations"
    ]
    for idx, item in enumerate(rule_items):
        ax.text(5.6, 4.05 - idx * 0.38, item, fontsize=8.5, color="#713f12", family="sans-serif")

    # Right: Financial Analytics
    rs3 = patches.FancyBboxPatch((10.0, 2.7), 4.2, 2.05, boxstyle="round,pad=0.1,rounding_size=0.1",
                                 facecolor="#fff7ed", edgecolor="#ea580c", linewidth=1.8)
    ax.add_patch(rs3)
    ax.text(12.1, 4.45, "FINANCIAL ANALYTICS", fontsize=11, fontweight="bold", ha="center", color="#9a3412")
    fin_items = [
        "- Total Inventory Cost Valuation",
        "- Spoilage Capital at Risk",
        "- Clearance Markdown Simulator",
        "- Streaming CSV Audit Exporter"
    ]
    for idx, item in enumerate(fin_items):
        ax.text(10.2, 4.05 - idx * 0.38, item, fontsize=8.5, color="#7c2d12", family="sans-serif")

    # Horizontal double arrows between services
    ax.annotate("", xy=(5.3, 3.7), xytext=(5.1, 3.7), arrowprops=dict(arrowstyle="<->", color="#64748b", lw=2))
    ax.annotate("", xy=(9.9, 3.7), xytext=(9.7, 3.7), arrowprops=dict(arrowstyle="<->", color="#64748b", lw=2))

    # Down arrow to Database
    ax.annotate("", xy=(7.5, 2.05), xytext=(7.5, 2.65), arrowprops=dict(arrowstyle="->", color="#0f172a", lw=2.5))
    ax.text(8.2, 2.35, "Atomic SQL Queries (psycopg2)", fontsize=9, color="#334155", fontweight="bold")

    # 4. Database Layer
    rdb = patches.FancyBboxPatch((0.8, 0.4), 13.4, 1.6, boxstyle="round,pad=0.1,rounding_size=0.15",
                                 facecolor="#f8fafc", edgecolor="#475569", linewidth=2)
    ax.add_patch(rdb)
    ax.text(7.5, 1.7, "Data Persistence Layer: PostgreSQL 18 Relational Database", fontsize=13, fontweight="bold", ha="center", color="#0f172a")

    db_tables = [
        ("products", "SKU, price, shelf life"),
        ("inventory", "batches, expiry, temp"),
        ("sales", "quantities sold, time"),
        ("suppliers", "lead time, MOQ"),
        ("demand_forecasts", "predictions, date"),
        ("spoilage_predictions", "P_spoil, risk tiers"),
        ("purchase_orders", "order qty, status"),
        ("weather_observations", "temp, humidity")
    ]
    w_tbl = 1.48
    for i, (tname, tdesc) in enumerate(db_tables):
        bx = 1.05 + i * 1.63
        r = patches.FancyBboxPatch((bx, 0.52), w_tbl, 0.95, boxstyle="square,pad=0",
                                   facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.2)
        ax.add_patch(r)
        ax.text(bx + w_tbl/2, 1.2, tname, fontsize=8.5, ha="center", va="center", color="#0f172a", fontweight="bold", family="monospace")
        ax.text(bx + w_tbl/2, 0.8, tdesc, fontsize=7.2, ha="center", va="center", color="#64748b", style="italic")

    plt.tight_layout()
    out_path = OUT_DIR / "system_architecture_diagram.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_path}")

# -------------------------------------------------------------
# 3. ACTIVITY WORKFLOW DIAGRAM
# -------------------------------------------------------------
def generate_activity_diagram():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(7, 8.65, "ShelfLife - End-to-End Activity Workflow", fontsize=18, fontweight="bold", ha="center", color="#0f172a")

    def draw_node(x, y, w, h, text, bg="#f8fafc", border="#334155", shape="round"):
        pad = 0.1 if shape == "round" else 0
        r = patches.FancyBboxPatch((x, y), w, h, boxstyle=f"{shape},pad={pad}",
                                   facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(r)
        ax.text(x + w/2, y + h/2, text, fontsize=9, ha="center", va="center", color="#0f172a", fontweight="600")

    # Start
    draw_node(5.2, 7.8, 3.6, 0.55, "Physical Goods Received (Inward Batch)", bg="#dcfce7", border="#16a34a")

    # Ingest
    draw_node(5.0, 6.8, 4.0, 0.6, "1. Ingest Batch Metadata (Lot, Expiry, Temp, Cost)", bg="#f1f5f9", border="#475569")
    ax.annotate("", xy=(7.0, 7.4), xytext=(7.0, 7.8), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))

    # Preprocessing
    draw_node(4.8, 5.8, 4.4, 0.6, "2. Preprocessing (StandardScaler + OneHotEncoder)", bg="#f1f5f9", border="#475569")
    ax.annotate("", xy=(7.0, 6.4), xytext=(7.0, 6.8), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))

    # Fork to 3 parallel checks
    ax.annotate("", xy=(2.4, 4.9), xytext=(7.0, 5.75), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))
    ax.annotate("", xy=(7.0, 4.9), xytext=(7.0, 5.75), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))
    ax.annotate("", xy=(11.6, 4.9), xytext=(7.0, 5.75), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))

    draw_node(0.6, 4.3, 3.6, 0.6, "3A. Ridge Regression\n(Cycle Demand Forecast)", bg="#ede9fe", border="#7c3aed")
    draw_node(5.2, 4.3, 3.6, 0.6, "3B. Logistic Regression\n(Spoilage Probability P_spoil)", bg="#ede9fe", border="#7c3aed")
    draw_node(9.8, 4.3, 3.6, 0.6, "3C. Cold-Chain Check\n(Storage Temp Violation)", bg="#fef3c7", border="#d97706")

    # Join to Health Score
    ax.annotate("", xy=(7.0, 3.5), xytext=(2.4, 4.25), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))
    ax.annotate("", xy=(7.0, 3.5), xytext=(7.0, 4.25), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))
    ax.annotate("", xy=(7.0, 3.5), xytext=(11.6, 4.25), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))

    draw_node(4.7, 2.85, 4.6, 0.65, "4. Rule Engine: Composite Health Score (H)\n(H = 0.40 Expiry + 0.35 Spoilage + 0.25 Stock)", bg="#eff6ff", border="#2563eb")

    # Decision on Health
    ax.annotate("", xy=(7.0, 2.3), xytext=(7.0, 2.8), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8))
    draw_node(1.0, 1.6, 3.6, 0.65, "Action: Urgent Clearance\n(Days <= 2d or P >= 60%)\nAuto 20%-50% Markdown", bg="#fee2e2", border="#dc2626")
    draw_node(5.2, 1.6, 3.6, 0.65, "Action: POS Customer Checkout\nAtomic FEFO Stock Depletion\n(Deplete Oldest Lot First)", bg="#e0f2fe", border="#0284c7")
    draw_node(9.4, 1.6, 3.6, 0.65, "Action: Reorder Purchase\n(Stock <= Reorder Level)\nAutomate Supplier PO", bg="#fef9c3", border="#ca8a04")

    ax.annotate("", xy=(2.8, 2.25), xytext=(7.0, 2.5), arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5))
    ax.annotate("", xy=(7.0, 2.25), xytext=(7.0, 2.5), arrowprops=dict(arrowstyle="->", color="#0284c7", lw=1.5))
    ax.annotate("", xy=(11.2, 2.25), xytext=(7.0, 2.5), arrowprops=dict(arrowstyle="->", color="#ca8a04", lw=1.5))

    # Commit
    draw_node(4.8, 0.5, 4.4, 0.6, "5. Commit to PostgreSQL & Update Financials\n(Real-Time Stock, Revenue & Waste Metrics)", bg="#dcfce7", border="#16a34a")
    ax.annotate("", xy=(7.0, 1.1), xytext=(2.8, 1.55), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5))
    ax.annotate("", xy=(7.0, 1.1), xytext=(7.0, 1.55), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5))
    ax.annotate("", xy=(7.0, 1.1), xytext=(11.2, 1.55), arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5))

    plt.tight_layout()
    out_path = OUT_DIR / "activity_workflow_diagram.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_class_diagram()
    generate_architecture_diagram()
    generate_activity_diagram()
    print("All diagrams generated successfully!")
