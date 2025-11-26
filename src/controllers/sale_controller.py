# src/controllers/sale_controller.py
"""
Controlador de Ventas - Lógica de negocio relacionada con ventas.
"""

from peewee import IntegrityError, JOIN, fn
import datetime
from decimal import Decimal

from models import db, Product, Inventory, StockMovement, Sale, SaleItem, ProductBatch


def record_sale(items_to_sell):
    """
    Registra una venta completa (con múltiples productos).
    Implementa FEFO (First Expired, First Out): vende primero los lotes que vencen antes.
    """
    try:
        db.connect()
        with db.atomic():
            sale = Sale.create(total=Decimal('0.00'))
            final_total = Decimal('0.00')

            for item_data in items_to_sell:
                barcode = item_data['barcode']
                qty = int(item_data['quantity'])
                if qty <= 0:
                    raise ValueError(f"Cantidad inválida para {barcode}.")

                try:
                    product = Product.get(Product.barcode == barcode)
                    inventory = Inventory.get(Inventory.product == product)
                except Product.DoesNotExist:
                    raise Exception(f"Producto con código {barcode} no encontrado.")

                if inventory.quantity < qty:
                    raise Exception(f"Stock insuficiente para '{product.name}'. Disponible: {inventory.quantity}, Solicitado: {qty}")
                
                unit_price = product.sale_price
                subtotal = (Decimal(qty) * unit_price).quantize(Decimal('0.01'))
                
                SaleItem.create(
                    sale=sale, product=product,
                    quantity=qty, unit_price=unit_price,
                    subtotal=subtotal
                )

                # FEFO: Deducir de lotes ordenados por fecha de vencimiento
                remaining_to_sell = qty
                batches_used = []
                
                # Obtener lotes activos ordenados por fecha de vencimiento (más próximos primero)
                # Los lotes sin fecha van al final
                batches = (ProductBatch
                          .select()
                          .where(
                              (ProductBatch.product == product) &
                              (ProductBatch.active == True) &
                              (ProductBatch.quantity > 0)
                          )
                          .order_by(
                              ProductBatch.expiration_date.asc(nulls='LAST')
                          ))
                
                for batch in batches:
                    if remaining_to_sell <= 0:
                        break
                    
                    # Cuánto podemos tomar de este lote
                    qty_from_batch = min(batch.quantity, remaining_to_sell)
                    
                    # Deducir del lote
                    batch.quantity -= qty_from_batch
                    if batch.quantity == 0:
                        batch.active = False
                    batch.save()
                    
                    # Registrar movimiento por lote
                    StockMovement.create(
                        product=product,
                        batch=batch.batch_number,
                        change=-qty_from_batch,
                        reason='sale',
                        reference=f'Venta ID: {sale.id} - Lote {batch.batch_number}'
                    )
                    
                    batches_used.append({
                        'batch_num': batch.batch_number,
                        'quantity': qty_from_batch,
                        'expiration': batch.expiration_date
                    })
                    
                    remaining_to_sell -= qty_from_batch
                
                if remaining_to_sell > 0:
                    raise Exception(f"Error interno: No se pudo deducir toda la cantidad de lotes para '{product.name}'.")
                
                # Actualizar inventario total
                inventory.quantity -= qty
                inventory.last_updated = datetime.datetime.now()
                inventory.save()

                final_total += subtotal

            sale.total = final_total
            sale.save()
            
        return True, f"Venta ID {sale.id} registrada exitosamente. Total: Bs {final_total}"

    except IntegrityError:
        return False, "Error de integridad de datos durante la transacción."
    except Exception as e:
        return False, f"Error al registrar la venta: {e}"
    finally:
        if not db.is_closed():
            db.close()


def list_sales_history():
    """Lista todas las ventas realizadas con sus items."""
    try:
        db.connect()
        query = (SaleItem
                 .select(
                     SaleItem,
                     Sale,
                     Product
                 )
                 .join(Sale)
                 .switch(SaleItem)
                 .join(Product)
                 .order_by(Sale.timestamp.desc()))

        sales_data = []
        for item in query:
            sales_data.append({
                "sale_id": item.sale.id,
                "timestamp": item.sale.timestamp,
                "product": item.product.name if item.product else None,
                "barcode": item.product.barcode if item.product else None,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
                "total_sale": item.sale.total
            })
        return sales_data
    except Exception as e:
        print(f"Error al listar historial de ventas: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def sales_summary_by_date():
    """Devuelve el resumen de ventas agrupado por fecha."""
    try:
        db.connect()
        query = (Sale
                 .select(
                     fn.strftime('%Y-%m-%d', Sale.timestamp).alias("date"),
                     fn.COUNT(Sale.id).alias("total_sales"),
                     fn.SUM(Sale.total).alias("total_amount")
                 )
                 .group_by(fn.strftime('%Y-%m-%d', Sale.timestamp))
                 .order_by(fn.strftime('%Y-%m-%d', Sale.timestamp).desc())
                 .dicts())

        return list(query)
    except Exception as e:
        print(f"Error al generar resumen de ventas: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
