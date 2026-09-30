from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.supplier import SupplierCreate, SupplierResponse

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierResponse])
def get_suppliers():
    """Retrieve all suppliers."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    supplier_id,
                    supplier_name,
                    contact_person,
                    phone,
                    email,
                    address,
                    average_delivery_days,
                    minimum_order_quantity,
                    is_active
                FROM suppliers
                ORDER BY supplier_id
            """)
            rows = cursor.fetchall()
            return [
                {
                    "supplier_id": r[0],
                    "supplier_name": r[1],
                    "contact_person": r[2],
                    "phone": r[3],
                    "email": r[4],
                    "address": r[5],
                    "average_delivery_days": int(r[6]) if r[6] is not None else 2,
                    "minimum_order_quantity": int(r[7]) if r[7] is not None else 1,
                    "is_active": bool(r[8]) if r[8] is not None else True
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load suppliers: {str(error)}"
        )


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: SupplierCreate):
    """Add a new supplier."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO suppliers (
                    supplier_name,
                    contact_person,
                    phone,
                    email,
                    address,
                    average_delivery_days,
                    minimum_order_quantity,
                    is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    supplier_id,
                    supplier_name,
                    contact_person,
                    phone,
                    email,
                    address,
                    average_delivery_days,
                    minimum_order_quantity,
                    is_active
            """, (
                supplier.supplier_name,
                supplier.contact_person,
                supplier.phone,
                supplier.email,
                supplier.address,
                supplier.average_delivery_days,
                supplier.minimum_order_quantity,
                supplier.is_active
            ))
            row = cursor.fetchone()
            return {
                "supplier_id": row[0],
                "supplier_name": row[1],
                "contact_person": row[2],
                "phone": row[3],
                "email": row[4],
                "address": row[5],
                "average_delivery_days": int(row[6]),
                "minimum_order_quantity": int(row[7]),
                "is_active": bool(row[8])
            }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create supplier: {str(error)}"
        )
