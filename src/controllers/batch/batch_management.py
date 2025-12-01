"""
Módulo de gestión de lotes.
Contiene funciones para listar y obtener resúmenes de lotes.
"""

from datetime import datetime
from models import db, Product, ProductBatch

def list_product_batches(product_id):
    """
    Lista los lotes de un producto específico, ordenados por fecha de vencimiento (FEFO).
    """
    try:
        db.connect()
        batches = (ProductBatch
                   .select()
                   .where(ProductBatch.product_id == product_id)
                   .where(ProductBatch.active == True)
                   .order_by(ProductBatch.expiration_date.asc()))
        
        results = []
        for batch in batches:
            expiration_display = "Sin fecha"
            if batch.expiration_date:
                expiration_display = batch.expiration_date.strftime('%Y-%m-%d')
                
            results.append({
                "id": batch.id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "expiration_date": batch.expiration_date,
                "expiration_display": expiration_display,
                "purchase_price": batch.purchase_price
            })
        return results
    except Exception as e:
        print(f"Error al listar lotes: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def get_batch_summary(product_barcode):
    """
    Retorna un string con el resumen de lotes para mostrar en UI.
    Ej: "Lote 1: 10u (Vence: 2023-12-01) | Lote 2: 5u (Vence: ...)"
    """
    try:
        db.connect()
        product = Product.get(Product.barcode == product_barcode)
        batches = (ProductBatch
                   .select()
                   .where(ProductBatch.product == product)
                   .where(ProductBatch.active == True)
                   .where(ProductBatch.quantity > 0)
                   .order_by(ProductBatch.expiration_date.asc()))
        
        if not batches:
            return None
            
        summary_parts = []
        for batch in batches:
            exp_str = batch.expiration_date.strftime('%Y-%m-%d') if batch.expiration_date else "Sin Venc."
            summary_parts.append(f"Lote {batch.batch_number}: {batch.quantity}u (Vence: {exp_str})")
            
        return " | ".join(summary_parts)
        
    except Product.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error al obtener resumen de lotes: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()
