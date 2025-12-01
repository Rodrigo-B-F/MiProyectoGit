"""
Módulo de gestión de stock e inventario.
Contiene funciones para registrar compras y movimientos de stock.
"""

from peewee import IntegrityError
import datetime
from decimal import Decimal
from models import db, Product, ProductBatch, Inventory, StockMovement

def record_purchase(product_barcode, quantity, purchase_price, expiration_date=None):
    """
    Registra una compra de producto (entrada de stock).
    Crea o actualiza un lote y actualiza el inventario total.
    """
    try:
        db.connect()
        with db.atomic():
            product = Product.get(Product.barcode == product_barcode)
            
            # 1. Gestión de Lotes (FEFO)
            # Buscar si existe un lote activo con la misma fecha de vencimiento y precio
            # para agrupar (opcional, pero recomendado para reducir fragmentación)
            existing_batch = ProductBatch.get_or_none(
                (ProductBatch.product == product) &
                (ProductBatch.expiration_date == expiration_date) &
                (ProductBatch.purchase_price == Decimal(purchase_price)) &
                (ProductBatch.active == True)
            )

            if existing_batch:
                existing_batch.quantity += quantity
                existing_batch.save()
                batch_ref = existing_batch
                batch_action = "Actualizado lote existente"
            else:
                # Crear nuevo lote
                # Calcular número de lote (incremental por producto)
                last_batch = ProductBatch.select().where(ProductBatch.product == product).order_by(ProductBatch.batch_number.desc()).first()
                new_batch_number = (last_batch.batch_number + 1) if last_batch else 0
                
                batch_ref = ProductBatch.create(
                    product=product,
                    quantity=quantity,
                    expiration_date=expiration_date,
                    purchase_price=Decimal(purchase_price),
                    batch_number=new_batch_number
                )
                batch_action = f"Creado lote #{new_batch_number}"

            # 2. Actualizar Inventario Total
            inventory, created = Inventory.get_or_create(product=product)
            inventory.quantity += quantity
            inventory.last_updated = datetime.datetime.now()
            inventory.save()

            # 3. Registrar Movimiento
            StockMovement.create(
                product=product,
                batch=batch_ref.batch_number,
                change=quantity,
                reason='purchase',
                reference=f'Compra - {batch_action}'
            )

            # Actualizar precio de compra del producto (opcional: promedio o último)
            product.purchase_price = Decimal(purchase_price)
            product.save()

        return True, f"Compra registrada. {batch_action}. Stock total: {inventory.quantity}"

    except Product.DoesNotExist:
        return False, f"Producto con código {product_barcode} no encontrado."
    except Exception as e:
        return False, f"Error al registrar compra: {e}"
    finally:
        if not db.is_closed():
            db.close()
