from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.sale import SaleCreate, SaleResponse

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("", response_model=List[SaleResponse])
def get_sales():
    """Retrieve all sales transactions joined with product names."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    s.sale_id,
                    s.product_id,
                    p.product_name,
                    p.category,
                    s.quantity_sold,
                    s.selling_price,
                    s.sale_date,
                    s.sale_time
                FROM sales s
                JOIN products p
                    ON s.product_id = p.product_id
                ORDER BY s.sale_id DESC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "sale_id": r[0],
                    "product_id": r[1],
                    "product_name": r[2],
                    "category": r[3],
                    "quantity_sold": int(r[4]),
                    "selling_price": float(r[5]),
                    "sale_date": str(r[6]),
                    "sale_time": str(r[7]) if r[7] is not None else None
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load sales: {str(error)}"
        )


@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def record_sale(sale: SaleCreate):
    """Record a new sale transaction and adjust inventory."""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check product
            cursor.execute("""
                SELECT product_name, category, selling_price
                FROM products
                WHERE product_id = %s
            """, (sale.product_id,))
            prod = cursor.fetchone()
            if not prod:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {sale.product_id} not found"
                )

            product_name, category, catalog_price = prod
            actual_price = sale.selling_price if sale.selling_price is not None else float(catalog_price)

            # Insert sale
            cursor.execute("""
                INSERT INTO sales (
                    product_id,
                    quantity_sold,
                    selling_price,
                    sale_date,
                    sale_time
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    COALESCE(%s, CURRENT_DATE),
                    COALESCE(%s, CURRENT_TIME)
                )
                RETURNING
                    sale_id,
                    product_id,
                    quantity_sold,
                    selling_price,
                    sale_date,
                    sale_time
            """, (
                sale.product_id,
                sale.quantity_sold,
                actual_price,
                sale.sale_date,
                sale.sale_time
            ))
            row = cursor.fetchone()

            # Optional FIFO deduction from oldest unexpired inventory batch if available
            cursor.execute("""
                UPDATE inventory
                SET quantity = GREATEST(quantity - %s, 0)
                WHERE inventory_id = (
                    SELECT inventory_id FROM inventory
                    WHERE product_id = %s AND quantity > 0
                    ORDER BY expiry_date ASC
                    LIMIT 1
                )
            """, (sale.quantity_sold, sale.product_id))

            return {
                "sale_id": row[0],
                "product_id": row[1],
                "product_name": product_name,
                "category": category,
                "quantity_sold": int(row[2]),
                "selling_price": float(row[3]),
                "sale_date": str(row[4]),
                "sale_time": str(row[5]) if row[5] is not None else None
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to record sale: {str(error)}"
        )
