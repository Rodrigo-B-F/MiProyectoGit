"""
Módulo de transacciones de venta (Simplificado).
Contiene la lógica para registrar ventas y actualización de inventario.
"""

from peewee import IntegrityError
import datetime
from decimal import Decimal
from models import db, Product, Inventory, StockMovement, Sale, SaleItem

def record_sale(items_data):
    """
    Registra una venta de múltiples productos.
    items_data: Lista de diccionarios [{'barcode': '...', 'quantity': 1}, ...]
    """
    if not items_data:
        return False, "No hay productos en la venta."

    try:
        db.connect()
        with db.atomic():
            # 1. Crear registro de Venta
            sale = Sale.create(total=0) # El total se calculará al final
            total_sale_amount = Decimal('0.00')

            for item in items_data:
                barcode = item['barcode']
                quantity_to_sell = int(item['quantity'])
                
                if quantity_to_sell <= 0:
                    raise ValueError(f"Cantidad inválida para el producto {barcode}")

                product = Product.get(Product.barcode == barcode)
                
                # Verificar stock total
                inventory = Inventory.get(Inventory.product == product)
                if inventory.quantity < quantity_to_sell:
                    raise ValueError(f"Stock insuficiente para '{product.name}'. Disponible: {inventory.quantity}")

                # 2. Actualizar Inventario Total
                inventory.quantity -= quantity_to_sell
                inventory.last_updated = datetime.datetime.now()
                inventory.save()

                # 3. Registrar Movimiento
                StockMovement.create(
                    product=product,
                    change=-quantity_to_sell,
                    reason='sale',
                    reference=f'Venta #{sale.id}'
                )

                # 4. Crear Item de Venta
                subtotal = product.sale_price * quantity_to_sell
                SaleItem.create(
                    sale=sale,
                    product=product,
                    quantity=quantity_to_sell,
                    unit_price=product.sale_price,
                    subtotal=subtotal
                )
                
                total_sale_amount += subtotal

            # Actualizar total de la venta
            sale.total = total_sale_amount
            sale.save()

        return True, f"Venta registrada exitosamente. Total: {total_sale_amount}"

    except Product.DoesNotExist:
        return False, f"Producto no encontrado."
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error al registrar venta: {e}"
    finally:
        if not db.is_closed():
            db.close()
