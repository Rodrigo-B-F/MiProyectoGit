"""
Módulo de gestión de stock e inventario (Simplificado).
Contiene funciones para registrar entradas de stock.
"""

from peewee import IntegrityError
import datetime
from models import db, Product, Inventory, StockMovement

def add_stock(product_barcode, quantity):
    """
    Registra una entrada de stock para un producto.
    Actualiza el inventario total.
    """
    try:
        db.connect()
        with db.atomic():
            product = Product.get(Product.barcode == product_barcode)
            
            # Actualizar Inventario Total
            inventory, created = Inventory.get_or_create(product=product)
            inventory.quantity += quantity
            inventory.last_updated = datetime.datetime.now()
            inventory.save()

            # Registrar Movimiento
            StockMovement.create(
                product=product,
                change=quantity,
                reason='stock_entry',
                reference='Entrada de Stock'
            )

        return True, f"Stock agregado. Stock total: {inventory.quantity}"

    except Product.DoesNotExist:
        return False, f"Producto con código {product_barcode} no encontrado."
    except Exception as e:
        return False, f"Error al agregar stock: {e}"
    finally:
        if not db.is_closed():
            db.close()
