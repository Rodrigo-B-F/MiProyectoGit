"""
Módulo de mantenimiento de lotes.
Contiene funciones para consolidar y corregir inventarios de lotes.
"""

from peewee import fn
from models import db, Product, ProductBatch, Inventory

def consolidate_inventory(product_id):
    """
    Recalcula el inventario total basado en la suma de los lotes activos.
    Útil para corregir inconsistencias.
    """
    try:
        db.connect()
        with db.atomic():
            product = Product.get_by_id(product_id)
            
            # Sumar cantidad de lotes activos
            total_batch_qty = (ProductBatch
                               .select(fn.SUM(ProductBatch.quantity))
                               .where(ProductBatch.product == product)
                               .where(ProductBatch.active == True)
                               .scalar()) or 0
            
            # Actualizar inventario
            inventory, _ = Inventory.get_or_create(product=product)
            inventory.quantity = total_batch_qty
            inventory.save()
            
        return True, f"Inventario consolidado: {total_batch_qty} unidades."
        
    except Product.DoesNotExist:
        return False, "Producto no encontrado."
    except Exception as e:
        return False, f"Error al consolidar inventario: {e}"
    finally:
        if not db.is_closed():
            db.close()
