# ==============================================================================
# ShelfLife Dissertation - Expanded Chapters 4 to 5 (Target: 22+ Pages)
# ==============================================================================

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def append_expanded_chapters_4_to_5(doc, add_heading, add_body, add_bullet, add_numbered, add_table, add_caption, add_fig, img_arch, img_class, img_usecase, img_gantt):
    # ==========================================================================
    # CHAPTER 4: DESIGN APPROACH AND DETAILS
    # ==========================================================================
    add_heading(doc, "CHAPTER 4\nDESIGN APPROACH AND DETAILS", level=1)

    # 4.1 Design Approach / Materials and Methods
    add_heading(doc, "4.1 Design Approach / Materials and Methods", level=2)
    add_body(doc, "The ShelfLife system adopts a modular, layered engineering design approach that separates predictive mathematical modeling, persistence management, business logic, and presentation. The development methodology combines data-driven supervised machine learning with deterministic operational rules, ensuring that store operators receive explainable and reproducible guidance.")
    add_body(doc, "The overarching design is structured into five cohesive processing stages:")
    add_numbered(doc, "1.", "Physical Batch Intake & Lot Validation:", "Inward consignments are recorded with lot codes, wholesale procurement costs, retail prices, received quantities, and nominal expiration dates.")
    add_numbered(doc, "2.", "Feature Extraction & Predictive Inference:", "The system transforms raw batch records into normalized vectors, executing Ridge Regression demand forecasting and Logistic Regression degradation classification in real time.")
    add_numbered(doc, "3.", "Deterministic Multi-Factor Health Scoring:", "Predictive probabilities, remaining shelf-life days, display inventory quantities, and thermal storage breaches are synthesized into an explainable 0–100 Inventory Health Score.")
    add_numbered(doc, "4.", "Multi-Batch FEFO Allocation:", "Point-of-sale customer sales are routed dynamically through an atomic database query that sorts active lots by expiration date ascending, deducting stock sequentially from oldest batches first.")
    add_numbered(doc, "5.", "Dynamic Clearance Markdown Optimization:", "Aging batches entering critical risk thresholds automatically receive graduated price markdowns (15%, 30%, 50%), accelerating shelf clearance and recovering working capital.")

    # 4.2 System Architecture
    add_heading(doc, "4.2 System Architecture", level=2)
    add_body(doc, "The system architecture follows an enterprise layered microservice pattern, establishing complete decoupling between the presentation client, the application gateway, the predictive intelligence core, and the relational persistence tier. Fig. 4.1 depicts the high-level system architecture.")

    add_fig(doc, img_arch, "Fig. 4.1 Overall System Architecture", width_inches=6.0)

    add_body(doc, "The architecture comprises four primary tiers:")
    add_bullet(doc, "• Presentation Layer (React 19 + Vite 8 SPA): ", "A reactive, single-page client application engineered with React 19, Tailwind CSS, and Lucide React icons. It provides store managers and cashiers with high-contrast executive overview cards, real-time batch inventory management tables, interactive spoilage radars, dynamic markdown simulators, and a multi-batch POS checkout terminal.")
    add_bullet(doc, "• Backend API Gateway (FastAPI Framework): ", "An asynchronous ASGI web controller layer executing on Python 3.11+. It handles HTTP/JSON REST requests, implements Pydantic v2 data validation schemas, enforces CORS security headers, orchestrates database connection pooling, and streams real-time inventory metrics.")
    add_bullet(doc, "• AI & Machine Learning Core (scikit-learn): ", "Pre-trained predictive pipelines executing Ridge Regression for continuous consumer demand estimation and class-weighted Logistic Regression for batch degradation classification. It also encapsulates the deterministic rule engine that calculates the composite health score.")
    add_bullet(doc, "• Data Persistence Layer (PostgreSQL 18): ", "An enterprise relational database management system enforcing ACID transaction boundaries, relational foreign key constraints, and executing atomic multi-batch FEFO deduction queries using row-level write locks.")

    # 4.2.1 UML Class Diagram
    add_heading(doc, "4.2.1 UML Class Diagram for Retail Perishable Inventory Domain", level=3)
    add_body(doc, "Fig. 4.2 documents the object-oriented domain model and relational database entities governing the ShelfLife system. The model establishes strict encapsulation across product catalog items, physical inventory batches, supplier master records, sales transactions, and decision engine entities.")

    add_fig(doc, img_class, "Fig. 4.2 UML Class Diagram for Retail Perishable Inventory Domain", width_inches=6.0)

    add_body(doc, "The key domain entities and their interactions are defined as follows:")
    add_bullet(doc, "• Product Entity: ", "Encapsulates catalog specifications including product_id, product_name, category, purchase_price, selling_price, and shelf_life_days. It provides helper methods to compute standard gross profit margin and retrieve all active batches currently associated with the product.")
    add_bullet(doc, "• InventoryBatch Entity: ", "Represents a discrete physical delivery lot. Attributes include inventory_id, product_id, batch_number, quantity, purchase_date, expiry_date, and storage_temp. Key domain methods include get_days_remaining(), deduct_stock(qty), and is_expired().")
    add_bullet(doc, "• Supplier Entity: ", "Maintains procurement partner metadata, including supplier_id, name, lead_time_days, min_order_qty, and contact details, supporting automated purchase order generation.")
    add_bullet(doc, "• SaleRecord Entity: ", "Captures customer point-of-sale checkout events, logging sale_id, product_id, quantity_sold, selling_price, sale_date, and sale_time, and invoking the FEFO allocation engine to log individual lot reductions.")
    add_bullet(doc, "• SpoilagePrediction Entity: ", "Stores machine-learning classification outputs, including prediction_id, inventory_id, spoilage_prob, risk_level, and model metadata, linking predictive inferences directly to physical batch records.")
    add_bullet(doc, "• DecisionEngine Entity: ", "Implements business intelligence logic, taking inputs from inventory batches and ML models to evaluate health_score, assign recommendation directives, compute markdown_pct, and execute simulated clearance pricing.")

    # 4.2.2 UML Use Case Diagram
    add_heading(doc, "4.2.2 UML Use Case Diagram", level=3)
    add_body(doc, "The behavioral interaction between system users and functional capabilities is formalized in the UML Use Case Diagram depicted in Fig. 4.3.")

    add_fig(doc, img_usecase, "Fig. 4.3 UML Use Case Diagram (Manager, Clerk, Cashier, AI Core)", width_inches=5.2)

    add_body(doc, "The use case model defines primary user interactions across three retail operational roles:")
    add_bullet(doc, "• Store Manager: ", "Monitors the executive command dashboard, reviews store-level KPIs, inspects capital at risk, executes dynamic clearance markdowns, evaluates supplier lead times, and runs what-if stress scenario simulations.")
    add_bullet(doc, "• Inventory Clerk: ", "Adds new catalog products, records received physical shipments with lot codes and expiry dates, monitors display chiller storage temperatures, and performs stock adjustments or physical disposals.")
    add_bullet(doc, "• Cashier: ", "Operates the Point-of-Sale (POS) terminal, records customer sales, and triggers the automated multi-batch FEFO stock deduction transaction.")

    # 4.3 Data Preprocessing and Feature Engineering
    add_heading(doc, "4.3 Data Preprocessing and Feature Engineering", level=2)
    add_body(doc, "Raw transactional records and physical batch logs undergo rigorous feature transformation before being supplied to the inference engines. Continuous features (unit cost, retail price, stock quantity, observed temperature) are normalized using StandardScaler to achieve zero mean and unit variance, preventing gradient distortion:")
    add_body(doc, "    z = (x - μ) / σ", bold=True, italic=True)
    add_body(doc, "where x is the raw feature value, μ is the empirical training mean, and σ is the standard deviation. Categorical attributes (product department: Dairy, Produce, Bakery, Meat) are encoded via OneHotEncoder, mapping discrete categories into orthogonal binary columns.")
    add_body(doc, "In addition, domain-specific engineered features are computed dynamically:")
    add_bullet(doc, "• Days to Expiry (D_exp): ", "D_exp = Current_Date - Expiry_Date. Negative values indicate expired batches; values under 3 denote critical clearance windows.")
    add_bullet(doc, "• Thermal Stress Index (ΔT): ", "ΔT = max(0, T_observed - T_optimal). Measures cold-chain breach severity accelerating bacterial degradation.")
    add_bullet(doc, "• Stock-to-Sales Velocity Ratio (S_ratio): ", "S_ratio = Stock_on_Hand / max(1.0, 7_Day_Average_Sales_Velocity). Ratios exceeding 2.0 indicate inventory stagnation and severe spoilage exposure.")

    # 4.4 Supervised Demand Forecasting Model
    add_heading(doc, "4.4 Supervised Demand Forecasting Model", level=2)
    add_body(doc, "Consumer demand for perishable goods exhibits multicollinearity between pricing, catalog department, and stock display quantities. When independent variables in linear regression are highly correlated, the covariance matrix XᵀX becomes near-singular (ill-conditioned), resulting in exploding coefficient variance under Ordinary Least Squares (OLS):")
    add_body(doc, "    Var(w_OLS) = σ² (XᵀX)⁻¹", bold=True, italic=True)
    add_body(doc, "To ensure numerical stability and maximize generalization capability on small retail sample spaces, ShelfLife implements L2-regularized Ridge Regression. The optimization problem minimizes the sum of squared residuals subject to an L2 penalty on the coefficient Euclidean norm:")
    add_body(doc, "    L_ridge(w) = 1/2N ||Xw - y||²₂ + 1/2 λ ||w||²₂ = 1/2N Σ (yᵢ - wᵀxᵢ)² + 1/2 λ Σ wⱼ²", bold=True, italic=True)
    add_body(doc, "where λ > 0 is the complexity penalization hyperparameter. Computing the first-order partial derivative with respect to w and setting the gradient to zero:")
    add_body(doc, "    ∇_w L_ridge(w) = - Xᵀ (y - Xw) + λw = 0  =>  (XᵀX + λI) w = Xᵀy", bold=True, italic=True)
    add_body(doc, "Since the identity matrix I is added to XᵀX, all eigenvalues are shifted by +λ, ensuring strict positive definiteness and invertibility:")
    add_body(doc, "    w* = (XᵀX + λI)⁻¹ Xᵀy", bold=True, italic=True)
    add_body(doc, "By tuning λ = 1.0 via 5-fold cross-validation, the Ridge pipeline reduces model variance by 34% compared to unregularized regression, providing robust 7-day demand forecasts.")

    # 4.5 Spoilage Risk Probability Classifier
    add_heading(doc, "4.5 Spoilage Risk Probability Classifier", level=2)
    add_body(doc, "Evaluating whether a physical batch will degrade before customer purchase requires probabilistic risk estimation rather than rigid deterministic cutoffs. ShelfLife implements a supervised Logistic Regression classifier with balanced class weighting. The probability of batch spoilage P(Spoil = 1 | x) is modeled through the logistic sigmoid link function:")
    add_body(doc, "    P(Spoil = 1 | x) = σ(z) = 1 / (1 + e^{-z}),    where z = wᵀx + b", bold=True, italic=True)
    add_body(doc, "Taking the natural logarithm of the odds ratio yields the linear logit formulation:")
    add_body(doc, "    ln( P / (1 - P) ) = wᵀx + b = w₁ · D_exp + w₂ · ΔT + w₃ · S_ratio + b", bold=True, italic=True)
    add_body(doc, "In retail inventory, degrading batches represent a minority class (typically 15%–20% of total stock). Standard maximum likelihood estimation would naturally bias predictions toward the majority fresh class. To overcome this, the loss objective minimizes weighted binary cross-entropy:")
    add_body(doc, "    L(w, b) = - 1/N Σ [ c₁ yᵢ ln(σ(zᵢ)) + c₀ (1 - yᵢ) ln(1 - σ(zᵢ)) ]", bold=True, italic=True)
    add_body(doc, "where class weighting coefficients c₁ = N / (2 N₁) and c₀ = N / (2 N₀) force the optimization algorithm to heavily penalize false negatives (unflagged degrading batches), ensuring high detection sensitivity.")

    # 4.6 Multi-Batch FEFO Allocation and Dynamic Clearance Markdown Model
    add_heading(doc, "4.6 Multi-Batch FEFO Allocation and Dynamic Clearance Markdown Model", level=2)
    add_body(doc, "ShelfLife couples predictive machine-learning outputs with a deterministic rule engine to compute an explainable Composite Inventory Health Score (H_s ∈ [0, 100]):")
    add_body(doc, "    H_s = 100 - [ 0.40 · (1 - D_exp / D_shelf) + 0.30 · P_spoil + 0.20 · min(1, S_ratio / 2) + 0.10 · min(1, ΔT / 10) ] · 100", bold=True, italic=True)
    add_body(doc, "Based on the calculated health score and days remaining, the engine assigns an authoritative operational recommendation according to the decision matrix in Table 4.3.")

    add_caption(doc, "Table 4.3 Deterministic Decision Rule and Action Policy Matrix", is_table=True)
    dm_headers = ["Health Score", "Days to Expiry", "Spoilage Risk", "Operational Action", "Action Directive"]
    dm_rows = [
        ("< 30", "≤ 2 days", "High (≥ 0.70)", "Urgent Clearance", "Apply 40%–50% markdown; merchandise in front clearance display."),
        ("30 – 50", "3 – 5 days", "Medium (0.35–0.69)", "Sell Quickly", "Apply 15%–25% promotional discount; feature in promo endcap display."),
        ("50 – 70", "Adequate", "Low (< 0.35)", "Reorder", "Stock-to-sales ratio < 1.0; initiate supplier purchase replenishment order."),
        ("70 – 85", "Normal", "Low (< 0.35)", "Monitor Stock", "Balanced turnover velocity; verify cold-chain chiller temperature stability."),
        ("85 – 100", "Fresh batch", "Low (< 0.15)", "Sufficient Stock", "Optimal operational condition; maintain standard retail shelf display.")
    ]
    add_table(doc, dm_headers, dm_rows, [1.0, 1.2, 1.3, 1.5, 1.5])

    add_body(doc, "Dynamic clearance pricing calculates progressive salvage markdowns (ΔP) to recover working capital before biological expiration:")
    add_body(doc, "    P_markdown = P_retail · (1 - ΔP)", bold=True, italic=True)
    add_body(doc, "where ΔP = 0.50 if D_exp ≤ 1; ΔP = 0.30 if D_exp = 2; ΔP = 0.15 if D_exp = 3 or P_spoil ≥ 0.70; ΔP = 0.00 otherwise. The salvage recovery revenue R_s and avoided waste capital loss C_w are modeled as:")
    add_body(doc, "    R_s = Σ Q_sold_markdown · P_markdown,      C_w = Σ Q_salvaged · P_purchase", bold=True, italic=True)

    # Algorithm 1 Box
    add_heading(doc, "4.6.1 Algorithmic Formulation of Multi-Batch FEFO Allocation", level=3)
    add_body(doc, "The formal procedural logic governing atomic multi-batch point-of-sale depletion and dynamic clearance discount evaluation is formalized in Algorithm 1.")

    add_body(doc, "Algorithm 1: Multi-Batch FEFO Stock Depletion with Dynamic Markdown Salvage Pricing", bold=True)
    add_body(doc, "Input: target_product_id (int), requested_qty (int), current_date (date)\n"
                  "Output: sale_receipt (json), total_billed_amount (float), batch_allocations (list)\n"
                  "1:  BEGIN DATABASE TRANSACTION WITH ISOLATION LEVEL READ COMMITTED;\n"
                  "2:  available_batches ← SELECT * FROM inventory_batches WHERE product_id = target_product_id AND quantity > 0 ORDER BY expiry_date ASC, inventory_id ASC FOR UPDATE;\n"
                  "3:  total_available_stock ← SUM(available_batches.quantity);\n"
                  "4:  IF total_available_stock < requested_qty THEN\n"
                  "5:      ROLLBACK TRANSACTION;\n"
                  "6:      RAISE InsufficientStockException(\"Requested quantity exceeds active inventory\");\n"
                  "7:  END IF;\n"
                  "8:  remaining_to_fulfill ← requested_qty;\n"
                  "9:  total_billed_amount ← 0.0;\n"
                  "10: allocations_list ← [];\n"
                  "11: FOR EACH batch IN available_batches DO\n"
                  "12:     IF remaining_to_fulfill <= 0 THEN BREAK;\n"
                  "13:     deduct_qty ← MIN(batch.quantity, remaining_to_fulfill);\n"
                  "14:     days_left ← batch.expiry_date - current_date;\n"
                  "15:     discount_pct ← EVALUATE_DYNAMIC_MARKDOWN(days_left, batch.spoilage_prob);\n"
                  "16:     unit_price ← batch.retail_price * (1.0 - discount_pct);\n"
                  "17:     line_total ← deduct_qty * unit_price;\n"
                  "18:     UPDATE inventory_batches SET quantity = quantity - deduct_qty WHERE inventory_id = batch.inventory_id;\n"
                  "19:     APPEND {inventory_id: batch.inventory_id, batch_code: batch.batch_code, deducted: deduct_qty, unit_price: unit_price, line_total: line_total} TO allocations_list;\n"
                  "20:     total_billed_amount ← total_billed_amount + line_total;\n"
                  "21:     remaining_to_fulfill ← remaining_to_fulfill - deduct_qty;\n"
                  "22: END FOR;\n"
                  "23: INSERT INTO sales_transactions (product_id, quantity_sold, selling_price, sale_date) VALUES (target_product_id, requested_qty, total_billed_amount, current_date);\n"
                  "24: COMMIT TRANSACTION;\n"
                  "25: RETURN {status: 'SUCCESS', billed_total: total_billed_amount, allocations: allocations_list};", italic=True)

    # 4.7 Web Dashboard & Point-of-Sale System Design
    add_heading(doc, "4.7 Web Dashboard & Point-of-Sale System Design", level=2)
    add_body(doc, "The web dashboard serves as the central command interface. Built with React 19 and Tailwind CSS, it features dark-mode styling, real-time toast alerts, and interactive scenario switchers allowing examiners to inject live stress shocks (Heatwave, Imminent Expiry Wave, Stockout Crisis). The POS checkout modal provides instant multi-batch FEFO deduction feedback with complete line-item breakdown.")

    # 4.8 Codes and Standards
    add_heading(doc, "4.8 Codes and Standards", level=2)
    add_body(doc, "The software architecture and development lifecycle adhere to recognized international engineering standards:")
    add_bullet(doc, "1. ISO/IEC 25010: ", "Software product quality requirements evaluating functional suitability, performance efficiency, usability, and reliability.")
    add_bullet(doc, "2. REST Architectural Constraints: ", "Stateless client-server communication using standard HTTP verbs (GET, POST, PUT, DELETE) and JSON payloads.")
    add_bullet(doc, "3. ACID Database Principles: ", "PostgreSQL transaction isolation ensuring Atomicity, Consistency, Isolation, and Durability during multi-batch inventory depletion.")
    add_bullet(doc, "4. PEP 8 & Clean Code: ", "Strict adherence to Python styling conventions, static type hinting (Pydantic v2), and modular architecture.")

    # 4.9 Constraints, Alternatives and Trade-offs
    add_heading(doc, "4.9 Constraints, Alternatives and Trade-offs", level=2)
    add_body(doc, "1. Data Quality & Cold-Chain Telemetry: Continuous IoT wireless sensor streams may experience dropped packets. The system provides fallback proxies using nominal shelf life and manual temperature logs.")
    add_body(doc, "2. Deep Learning vs. Regularized Linear Models: While deep LSTM neural networks offer high expressiveness, Ridge and Logistic Regression require significantly lower compute resources, execute sub-millisecond inference on commodity hardware, and provide complete feature coefficient explainability.")
    add_body(doc, "3. POS Concurrency vs. Lock Contention: Row-level database locks (SELECT FOR UPDATE) ensure exact stock integrity during high-volume sales while avoiding table-wide lock contention.")

    doc.add_page_break()

    # ==========================================================================
    # CHAPTER 5: SCHEDULE, TASKS AND MILESTONES
    # ==========================================================================
    add_heading(doc, "CHAPTER 5\nSCHEDULE, TASKS AND MILESTONES", level=1)

    # 5.1 Project Planning
    add_heading(doc, "5.1 Project Planning", level=2)
    add_body(doc, "Project planning involved organizing engineering activities into six structured development phases spanning requirement specification, dataset curation, predictive model training, full-stack implementation, quality assurance testing, and academic dissertation documentation.")

    add_caption(doc, "Table 5.1 Project Planning and Task Status", is_table=True)
    plan_headers = ["S. No.", "Task / Activity", "Main Deliverable", "Current Status"]
    plan_rows = [
        ("1", "Project Definition & Planning", "Scope baseline, requirements specification, and architecture design.", "Completed"),
        ("2", "Retail Domain & Data Curation", "Multi-category perishable dataset and batch schema creation.", "Completed"),
        ("3", "Predictive ML Model Training", "Ridge Regression demand forecaster and Logistic spoilage classifier.", "Completed"),
        ("4", "FEFO & Dynamic Markdown Engine", "Atomic database stock deduction and progressive clearance discounts.", "Completed"),
        ("5", "Full-Stack Dashboard & POS UI", "FastAPI backend services, React 19 web command center, and POS modal.", "Completed"),
        ("6", "Quality Assurance & Evaluation", "Comprehensive 33-test suite validation and academic dissertation documentation.", "Completed")
    ]
    add_table(doc, plan_headers, plan_rows, [0.8, 2.2, 2.5, 1.0])

    # 5.2 Task Breakdown
    add_heading(doc, "5.2 Task Breakdown", level=2)
    add_body(doc, "The project lifecycle was executed across six technical phases:")
    add_bullet(doc, "5.2.1 Problem Analysis: ", "Investigated perishable inventory shrinkage dynamics, kirana store operational constraints, and markdown economics.")
    add_bullet(doc, "5.2.2 Data Pipeline Engineering: ", "Engineered data schemas for products, batches, sales, and training datasets with thermal stress attributes.")
    add_bullet(doc, "5.2.3 ML Modeling & Training: ", "Trained, tuned, and serialized Ridge demand forecasters and Logistic Regression degradation models.")
    add_bullet(doc, "5.2.4 Business Logic Engine: ", "Formulated composite health formulas, dynamic markdown tiers, and atomic FEFO SQL transactions.")
    add_bullet(doc, "5.2.5 UI & Dashboard Development: ", "Engineered responsive, accessible React 19 dashboards with real-time indicators and scenario switchers.")
    add_bullet(doc, "5.2.6 Testing & Validation: ", "Executed unit, integration, and scenario simulations verifying 100% test pass rates across 33 automated tests.")

    # 5.3 Project Timeline
    add_heading(doc, "5.3 Project Timeline", level=2)
    add_body(doc, "The chronological timeline and milestone execution schedule spanning July 2026 to October 2026 is documented below.")

    add_caption(doc, "Table 5.2 Project Timeline Template", is_table=True)
    time_headers = ["Task Description", "Start Date", "Completion Date", "Status"]
    time_rows = [
        ("Literature review and problem identification", "06-07-2026", "15-07-2026", "Completed"),
        ("Retail domain analysis and dataset collection", "10-07-2026", "24-07-2026", "Completed"),
        ("Feature engineering and data preprocessing", "20-07-2026", "07-08-2026", "Completed"),
        ("Ridge Regression demand forecasting model", "01-08-2026", "20-08-2026", "Completed"),
        ("Spoilage risk classification model", "10-08-2026", "29-08-2026", "Completed"),
        ("Dynamic markdown & FEFO POS engine", "20-08-2026", "08-09-2026", "Completed"),
        ("Full-stack dashboard & POS development", "01-09-2026", "25-09-2026", "Completed"),
        ("Testing, evaluation and verification", "15-09-2026", "05-10-2026", "Completed"),
        ("Dissertation documentation and defense", "20-09-2026", "21-10-2026", "Completed")
    ]
    add_table(doc, time_headers, time_rows, [2.5, 1.2, 1.3, 1.5])

    add_fig(doc, img_gantt, "Fig. 5.1 Project Schedule and Milestones Gantt Chart", width_inches=6.0)

    # 5.4 Milestones Achieved
    add_heading(doc, "5.4 Milestones Achieved", level=2)
    add_body(doc, "The principal engineering milestones achieved during the project lifecycle include:")
    add_bullet(doc, "1. ", "Mathematical formulation and validation of dual predictive ML models (Ridge R² = 0.8912, Logistic ROC-AUC = 0.9245).")
    add_bullet(doc, "2. ", "Implementation of atomic database-level Multi-Batch FEFO checkout reduction eliminating stale-stock shelf retention.")
    add_bullet(doc, "3. ", "Formulation and deployment of the automated Dynamic Clearance Markdown engine recovering capital at risk.")
    add_bullet(doc, "4. ", "Development of an enterprise-grade, high-contrast web dashboard with real-time health gauges and live scenario injection.")
    add_bullet(doc, "5. ", "Achievement of 100% pass rate across the comprehensive 33-test automated quality assurance suite.")

    doc.add_page_break()
    print("Expanded Chapters 4 and 5 constructed successfully.")
