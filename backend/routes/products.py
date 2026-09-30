from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products():
    """Retrieve all catalog products."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    product_id,
                    product_name,
                    category,
                    unit,
                    purchase_price,
                    selling_price,
                    shelf_life_days
                FROM products
                ORDER BY product_id
            """)
            rows = cursor.fetchall()
            return [
                {
                    "product_id": r[0],
                    "product_name": r[1],
                    "category": r[2],
                    "unit": r[3],
                    "purchase_price": float(r[4]) if r[4] is not None else 0.0,
                    "selling_price": float(r[5]) if r[5] is not None else 0.0,
                    "shelf_life_days": int(r[6])
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load products: {str(error)}"
        )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int):
    """Retrieve a single product by ID."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    product_id,
                    product_name,
                    category,
                    unit,
                    purchase_price,
                    selling_price,
                    shelf_life_days
                FROM products
                WHERE product_id = %s
            """, (product_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )
            return {
                "product_id": row[0],
                "product_name": row[1],
                "category": row[2],
                "unit": row[3],
                "purchase_price": float(row[4]) if row[4] is not None else 0.0,
                "selling_price": float(row[5]) if row[5] is not None else 0.0,
                "shelf_life_days": int(row[6])
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product: {str(error)}"
        )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    """Add a new product to the catalog."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO products (
                    product_name,
                    category,
                    unit,
                    purchase_price,
                    selling_price,
                    shelf_life_days
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    product_id,
                    product_name,
                    category,
                    unit,
                    purchase_price,
                    selling_price,
                    shelf_life_days
            """, (
                product.product_name,
                product.category,
                product.unit,
                product.purchase_price,
                product.selling_price,
                product.shelf_life_days
            ))
            row = cursor.fetchone()
            new_pid = row[0]

            # Auto-generate initial ML demand forecast for new product
            try:
                from ml.inference import predict_demand
                pred = predict_demand(
                    category=row[2],
                    stock_quantity=0,
                    reorder_level=20,
                    reorder_quantity=15,
                    unit_price=float(row[5]) if row[5] is not None else 4.0,
                    shelf_life_days=int(row[6]),
                )
                cursor.execute("""
                    INSERT INTO demand_forecasts (product_id, forecast_date, predicted_demand, model_name)
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """, (new_pid, pred["predicted_demand"], pred["model_name"]))
            except Exception:
                pass

            return {
                "product_id": row[0],
                "product_name": row[1],
                "category": row[2],
                "unit": row[3],
                "purchase_price": float(row[4]),
                "selling_price": float(row[5]),
                "shelf_life_days": int(row[6])
            }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create product: {str(error)}"
        )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    """Update an existing product."""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check existence
            cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )

            fields = []
            values = []
            if product.product_name is not None:
                fields.append("product_name = %s")
                values.append(product.product_name)
            if product.category is not None:
                fields.append("category = %s")
                values.append(product.category)
            if product.unit is not None:
                fields.append("unit = %s")
                values.append(product.unit)
            if product.purchase_price is not None:
                fields.append("purchase_price = %s")
                values.append(product.purchase_price)
            if product.selling_price is not None:
                fields.append("selling_price = %s")
                values.append(product.selling_price)
            if product.shelf_life_days is not None:
                fields.append("shelf_life_days = %s")
                values.append(product.shelf_life_days)

            if not fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update"
                )

            values.append(product_id)
            query = f"""
                UPDATE products
                SET {', '.join(fields)}
                WHERE product_id = %s
                RETURNING
                    product_id,
                    product_name,
                    category,
                    unit,
                    purchase_price,
                    selling_price,
                    shelf_life_days
            """
            cursor.execute(query, tuple(values))
            row = cursor.fetchone()
            return {
                "product_id": row[0],
                "product_name": row[1],
                "category": row[2],
                "unit": row[3],
                "purchase_price": float(row[4]),
                "selling_price": float(row[5]),
                "shelf_life_days": int(row[6])
            }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update product: {str(error)}"
        )


@router.delete("/{product_id}")
def delete_product(product_id: int):
    """Delete a product from the catalog."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )

            # Clean up dependent ML predictions and forecasts before deleting product
            cursor.execute("DELETE FROM demand_forecasts WHERE product_id = %s", (product_id,))
            cursor.execute("DELETE FROM spoilage_predictions WHERE product_id = %s", (product_id,))
            cursor.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            return {"message": f"Product {product_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to delete product (check if related records exist): {str(error)}"
        )
