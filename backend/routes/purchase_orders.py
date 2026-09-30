from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderResponse

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.get("", response_model=List[PurchaseOrderResponse])
def get_purchase_orders():
    """Retrieve all purchase orders joined with suppliers and products."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    po.purchase_order_id,
                    po.supplier_id,
                    s.supplier_name,
                    po.product_id,
                    p.product_name,
                    po.quantity_ordered,
                    po.order_date,
                    po.expected_delivery_date,
                    po.status,
                    po.unit_cost
                FROM purchase_orders po
                JOIN suppliers s
                    ON po.supplier_id = s.supplier_id
                JOIN products p
                    ON po.product_id = p.product_id
                ORDER BY po.purchase_order_id DESC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "purchase_order_id": r[0],
                    "supplier_id": r[1],
                    "supplier_name": r[2],
                    "product_id": r[3],
                    "product_name": r[4],
                    "quantity_ordered": int(r[5]),
                    "order_date": str(r[6]),
                    "expected_delivery_date": str(r[7]) if r[7] is not None else None,
                    "status": r[8] or "Pending",
                    "unit_cost": float(r[9]) if r[9] is not None else 0.0,
                    "total_cost": round(int(r[5]) * (float(r[9]) if r[9] is not None else 0.0), 2)
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load purchase orders: {str(error)}"
        )


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(po: PurchaseOrderCreate):
    """Create a new purchase order."""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check supplier
            cursor.execute("SELECT supplier_name FROM suppliers WHERE supplier_id = %s", (po.supplier_id,))
            supp = cursor.fetchone()
            if not supp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Supplier with ID {po.supplier_id} not found"
                )

            # Check product
            cursor.execute("SELECT product_name, purchase_price FROM products WHERE product_id = %s", (po.product_id,))
            prod = cursor.fetchone()
            if not prod:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {po.product_id} not found"
                )

            unit_cost = po.unit_cost if po.unit_cost is not None else float(prod[1] or 0.0)

            cursor.execute("""
                INSERT INTO purchase_orders (
                    supplier_id,
                    product_id,
                    quantity_ordered,
                    order_date,
                    expected_delivery_date,
                    status,
                    unit_cost
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    COALESCE(%s, CURRENT_DATE),
                    %s,
                    COALESCE(%s, 'Pending'),
                    %s
                )
                RETURNING
                    purchase_order_id,
                    supplier_id,
                    product_id,
                    quantity_ordered,
                    order_date,
                    expected_delivery_date,
                    status,
                    unit_cost
            """, (
                po.supplier_id,
                po.product_id,
                po.quantity_ordered,
                po.order_date,
                po.expected_delivery_date,
                po.status,
                unit_cost
            ))
            row = cursor.fetchone()
            return {
                "purchase_order_id": row[0],
                "supplier_id": row[1],
                "supplier_name": supp[0],
                "product_id": row[2],
                "product_name": prod[0],
                "quantity_ordered": int(row[3]),
                "order_date": str(row[4]),
                "expected_delivery_date": str(row[5]) if row[5] is not None else None,
                "status": row[6],
                "unit_cost": float(row[7]),
                "total_cost": round(int(row[3]) * float(row[7]), 2)
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create purchase order: {str(error)}"
        )
