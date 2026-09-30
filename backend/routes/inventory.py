from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryResponse])
def get_inventory():
    """Retrieve all inventory batches joined with product metadata."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.inventory_id,
                    i.product_id,
                    p.product_name,
                    p.category,
                    i.batch_number,
                    i.quantity,
                    i.purchase_date,
                    i.expiry_date,
                    i.storage_temperature
                FROM inventory i
                JOIN products p
                    ON i.product_id = p.product_id
                ORDER BY i.inventory_id
            """)
            rows = cursor.fetchall()
            return [
                {
                    "inventory_id": r[0],
                    "product_id": r[1],
                    "product_name": r[2],
                    "category": r[3],
                    "batch_number": r[4],
                    "quantity": int(r[5]),
                    "purchase_date": str(r[6]) if r[6] is not None else None,
                    "expiry_date": str(r[7]),
                    "storage_temperature": float(r[8]) if r[8] is not None else None
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load inventory: {str(error)}"
        )


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory_by_id(inventory_id: int):
    """Retrieve a single inventory batch by ID."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    i.inventory_id,
                    i.product_id,
                    p.product_name,
                    p.category,
                    i.batch_number,
                    i.quantity,
                    i.purchase_date,
                    i.expiry_date,
                    i.storage_temperature
                FROM inventory i
                JOIN products p
                    ON i.product_id = p.product_id
                WHERE i.inventory_id = %s
            """, (inventory_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inventory batch with ID {inventory_id} not found"
                )
            return {
                "inventory_id": row[0],
                "product_id": row[1],
                "product_name": row[2],
                "category": row[3],
                "batch_number": row[4],
                "quantity": int(row[5]),
                "purchase_date": str(row[6]) if row[6] is not None else None,
                "expiry_date": str(row[7]),
                "storage_temperature": float(row[8]) if row[8] is not None else None
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving inventory: {str(error)}"
        )


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(item: InventoryCreate):
    """Create a new inventory batch."""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check product exists
            cursor.execute("SELECT product_name, category FROM products WHERE product_id = %s", (item.product_id,))
            prod = cursor.fetchone()
            if not prod:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Referenced product_id {item.product_id} does not exist"
                )

            cursor.execute("""
                INSERT INTO inventory (
                    product_id,
                    batch_number,
                    quantity,
                    purchase_date,
                    expiry_date,
                    storage_temperature
                )
                VALUES (%s, %s, %s, COALESCE(%s, CURRENT_DATE), %s, %s)
                RETURNING
                    inventory_id,
                    product_id,
                    batch_number,
                    quantity,
                    purchase_date,
                    expiry_date,
                    storage_temperature
            """, (
                item.product_id,
                item.batch_number,
                item.quantity,
                item.purchase_date,
                item.expiry_date,
                item.storage_temperature
            ))
            row = cursor.fetchone()
            new_inv_id = row[0]

            # Auto-generate initial ML spoilage prediction for new batch
            try:
                from ml.inference import predict_spoilage
                from datetime import date
                expiry_dt = date.fromisoformat(str(item.expiry_date)[:10])
                days_rem = max(0, (expiry_dt - date.today()).days)
                spoilage = predict_spoilage(
                    category=prod[1],
                    stock_quantity=item.quantity,
                    days_remaining=days_rem,
                    unit_price=3.5,
                )
                cursor.execute("""
                    INSERT INTO spoilage_predictions (
                        product_id, inventory_id, prediction_date, days_remaining,
                        spoilage_probability, risk_level, model_name
                    )
                    VALUES (%s, %s, CURRENT_DATE, %s, %s, %s, %s)
                """, (
                    item.product_id,
                    new_inv_id,
                    days_rem,
                    spoilage["spoilage_probability"],
                    spoilage["risk_level"],
                    spoilage["model_name"],
                ))
            except Exception:
                pass

            return {
                "inventory_id": row[0],
                "product_id": row[1],
                "product_name": prod[0],
                "category": prod[1],
                "batch_number": row[2],
                "quantity": int(row[3]),
                "purchase_date": str(row[4]) if row[4] is not None else None,
                "expiry_date": str(row[5]),
                "storage_temperature": float(row[6]) if row[6] is not None else None
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create inventory batch: {str(error)}"
        )


@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(inventory_id: int, item: InventoryUpdate):
    """Update inventory batch details (e.g. quantity, expiry date, storage temp)."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                SELECT i.inventory_id, p.product_name, p.category, i.product_id
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                WHERE i.inventory_id = %s
            """, (inventory_id,))
            existing = cursor.fetchone()
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inventory batch with ID {inventory_id} not found"
                )

            fields = []
            values = []
            if item.batch_number is not None:
                fields.append("batch_number = %s")
                values.append(item.batch_number)
            if item.quantity is not None:
                fields.append("quantity = %s")
                values.append(item.quantity)
            if item.purchase_date is not None:
                fields.append("purchase_date = %s")
                values.append(item.purchase_date)
            if item.expiry_date is not None:
                fields.append("expiry_date = %s")
                values.append(item.expiry_date)
            if item.storage_temperature is not None:
                fields.append("storage_temperature = %s")
                values.append(item.storage_temperature)

            if not fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update"
                )

            values.append(inventory_id)
            query = f"""
                UPDATE inventory
                SET {', '.join(fields)}
                WHERE inventory_id = %s
                RETURNING
                    inventory_id,
                    product_id,
                    batch_number,
                    quantity,
                    purchase_date,
                    expiry_date,
                    storage_temperature
            """
            cursor.execute(query, tuple(values))
            row = cursor.fetchone()
            return {
                "inventory_id": row[0],
                "product_id": row[1],
                "product_name": existing[1],
                "category": existing[2],
                "batch_number": row[2],
                "quantity": int(row[3]),
                "purchase_date": str(row[4]) if row[4] is not None else None,
                "expiry_date": str(row[5]),
                "storage_temperature": float(row[6]) if row[6] is not None else None
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update inventory batch: {str(error)}"
        )


@router.delete("/{inventory_id}")
def delete_inventory(inventory_id: int):
    """Delete an inventory batch."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT inventory_id FROM inventory WHERE inventory_id = %s", (inventory_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inventory batch with ID {inventory_id} not found"
                )

            # Clean up dependent spoilage predictions before deleting batch
            cursor.execute("DELETE FROM spoilage_predictions WHERE inventory_id = %s", (inventory_id,))
            cursor.execute("DELETE FROM inventory WHERE inventory_id = %s", (inventory_id,))
            return {"message": f"Inventory batch {inventory_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to delete inventory batch: {str(error)}"
        )
