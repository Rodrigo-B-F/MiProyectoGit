# src/controllers/batch_controller.py
"""
Controlador de Lotes - Lógica de negocio relacionada con lotes de productos.
"""

from peewee import JOIN
import datetime
from decimal import Decimal

from models import db, Product, ProductBatch


def list_product_batches(product_id):
    """
    Lista todos los lotes activos de un producto específico.
    Retorna ordenados por fecha de vencimiento (FEFO).
    """
    try:
        db.connect()
        
        product = Product.get_by_id(product_id)
        
        batches = (ProductBatch
                  .select()
                  .where(
                      (ProductBatch.product == product) &
                      (ProductBatch.active == True)
                  )
                  .order_by(ProductBatch.expiration_date.asc(nulls='LAST')))
        
        data = []
        for batch in batches:
            exp_str = batch.expiration_date.strftime('%Y-%m-%d') if batch.expiration_date else "Sin fecha"
            data.append({
                "batch_number": batch.batch_number,
                "batch_name": f"Lote {batch.batch_number}",
                "quantity": batch.quantity,
                "expiration_date": batch.expiration_date,
                "expiration_display": exp_str,
                "purchase_date": batch.purchase_date,
                "purchase_price": batch.purchase_price,
                "active": batch.active
            })
        
        return data
        
    except Product.DoesNotExist:
        print(f"Error: Producto con ID {product_id} no encontrado.")
        return []
    except Exception as e:
        print(f"Error al listar lotes: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_batch_summary(product_barcode):
    """
    Obtiene un resumen de lotes para un producto dado su código de barras.
    Útil para mostrar en la UI antes de agregar stock.
    """
    try:
        db.connect()
        
        product = Product.get(Product.barcode == product_barcode)
        
        batches = (ProductBatch
                  .select()
                  .where(
                      (ProductBatch.product == product) &
                      (ProductBatch.active == True) &
                      (ProductBatch.quantity > 0)
                  )
                  .order_by(ProductBatch.expiration_date.asc(nulls='LAST')))
        
        if not batches:
            return None
        
        summary = []
        for batch in batches:
            exp_str = f"Vence: {batch.expiration_date}" if batch.expiration_date else "Sin vencimiento"
            summary.append(f"Lote {batch.batch_number}: {batch.quantity} unidades ({exp_str})")
        
        return "\n".join(summary)
        
    except Product.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error al obtener resumen de lotes: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def consolidate_inventory(product_id):
    """
    Recalcula el inventory.quantity sumando todos los lotes activos.
    Útil para verificar consistencia de datos.
    """
    try:
        db.connect()
        from models import Inventory
        
        product = Product.get_by_id(product_id)
        
        # Sumar cantidad de todos los lotes activos
        total_from_batches = sum(
            batch.quantity
            for batch in product.batches
            if batch.active
        )
        
        # Actualizar inventario
        inventory = Inventory.get(Inventory.product == product)
        old_qty = inventory.quantity
        inventory.quantity = total_from_batches
        inventory.save()
        
        return True, f"Inventario consolidado: {old_qty} → {total_from_batches}"
        
    except Product.DoesNotExist:
        return False, f"Producto con ID {product_id} no encontrado."
    except Exception as e:
        return False, f"Error al consolidar inventario: {e}"
    finally:
        if not db.is_closed():
            db.close()
