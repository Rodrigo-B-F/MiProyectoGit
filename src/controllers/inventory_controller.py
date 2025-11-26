# src/controllers/inventory_controller.py
"""
Controlador de Inventario - Lógica de negocio relacionada con inventario y stocks.
"""

from peewee import IntegrityError, JOIN, fn
import datetime
from decimal import Decimal

from models import db, Category, Product, Inventory, StockMovement, ProductBatch


def record_purchase(product_barcode, quantity, purchase_price, expiration_date=None):
    """
    Registra la compra de stock para un producto existente.
    Gestiona lotes automáticamente basado en la fecha de vencimiento:
    - Si existe un lote con la misma fecha de vencimiento, agrega a ese lote
    - Si no existe, crea un nuevo lote con numeración secuencial
    """
    try:
        db.connect()
        with db.atomic():
            product = Product.get(Product.barcode == product_barcode)
            product.purchase_price = Decimal(purchase_price)
            product.save()

            # Buscar lote existente con la misma fecha de vencimiento
            existing_batch = None
            if expiration_date is not None:
                # Buscar lote activo con la misma fecha
                existing_batch = (ProductBatch
                                .select()
                                .where(
                                    (ProductBatch.product == product) &
                                    (ProductBatch.expiration_date == expiration_date) &
                                    (ProductBatch.active == True)
                                )
                                .first())
            else:
                # Si no hay fecha, buscar lote sin fecha de vencimiento
                existing_batch = (ProductBatch
                                .select()
                                .where(
                                    (ProductBatch.product == product) &
                                    (ProductBatch.expiration_date.is_null()) &
                                    (ProductBatch.active == True)
                                )
                                .first())
            
            if existing_batch:
                # Agregar al lote existente
                existing_batch.quantity += quantity
                existing_batch.purchase_price = Decimal(purchase_price)  # Actualizar precio
                existing_batch.save()
                
                batch_num = existing_batch.batch_number
                batch_info = f"Lote {batch_num}"
                
                # Registrar movimiento
                StockMovement.create(
                    product=product,
                    batch=batch_num,
                    change=quantity,
                    reason='purchase',
                    reference=f'Compra agregada a {batch_info}'
                )
                
                message_detail = f"agregadas a {batch_info} existente"
            else:
                # Crear nuevo lote
                # Obtener el siguiente número de lote
                max_batch = (ProductBatch
                           .select(fn.MAX(ProductBatch.batch_number))
                           .where(ProductBatch.product == product)
                           .scalar())
                next_batch_num = (max_batch + 1) if max_batch is not None else 0
                
                # Crear el nuevo lote
                new_batch = ProductBatch.create(
                    product=product,
                    quantity=quantity,
                    expiration_date=expiration_date,
                    purchase_date=datetime.datetime.now(),
                    purchase_price=Decimal(purchase_price),
                    batch_number=next_batch_num,
                    active=True
                )
                
                batch_info = f"Lote {next_batch_num}"
                
                # Registrar movimiento
                StockMovement.create(
                    product=product,
                    batch=next_batch_num,
                    change=quantity,
                    reason='purchase',
                    reference=f'Compra - nuevo {batch_info}'
                )
                
                exp_info = f" (Vence: {expiration_date})" if expiration_date else ""
                message_detail = f"en nuevo {batch_info}{exp_info}"

            # Actualizar inventario total
            inventory = Inventory.get(Inventory.product == product)
            inventory.quantity += quantity
            inventory.last_updated = datetime.datetime.now()
            inventory.save()
            
        return True, f"Stock actualizado. {quantity} unidades de '{product.name}' {message_detail}. Total: {inventory.quantity}"
        
    except Product.DoesNotExist:
        return False, f"Error: Producto con código {product_barcode} no encontrado."
    except Exception as e:
        return False, f"Error al registrar la compra: {e}"
    finally:
        if not db.is_closed():
            db.close()


def list_products_inventory(option):
    """Lista productos con inventario, categoría y ganancia."""
    try:
        db.connect()
        if option == 1: option = True
        else: option = False
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Product.active == option))
        
        data = []
        for inv in query:
            prod = inv.product
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
                "unit": prod.unit,
                "quantity": inv.quantity,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "date_added": prod.date_added,
"expiration_date": prod.expiration_date,
                "location": prod.location,
                "active": prod.active
            })
        return data
    except Exception as e:
        print(f"Error al listar inventario: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def list_available_products():
    """Lista únicamente productos con stock disponible (>0)."""
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Inventory.quantity > 0))

        data = []
        for inv in query:
            prod = inv.product
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
                "unit": prod.unit,
                "quantity": inv.quantity if inv else 0,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "date_added": prod.date_added,
                "expiration_date": prod.expiration_date,
                "location": prod.location,
                "active": prod.active
            })
        return data
    except Exception as e:
        print(f"Error al listar productos disponibles: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def list_out_of_stock_products():
    """Lista únicamente productos sin stock (quantity = 0)."""
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Inventory.quantity <= 0))

        data = []
        for inv in query:
            prod = inv.product
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
                "unit": prod.unit,
                "quantity": inv.quantity if inv else 0,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "date_added": prod.date_added,
                "expiration_date": prod.expiration_date,
                "location": prod.location,
                "active": prod.active
            })
        return data
    except Exception as e:
        print(f"Error al listar productos sin stock: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def list_expiring_products(days=10):
    """
    Lista productos próximos a vencer en X días.
    Retorna lista de diccionarios con todos los detalles del producto.
    """
    try:
        db.connect()
        date_limit = datetime.date.today() + datetime.timedelta(days=days)
        
        query = (Product
                 .select(Product, Inventory, Category) 
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(
                     (Product.expiration_date.is_null(False)) &
                     (Product.expiration_date <= date_limit) &
                     (Product.expiration_date >= datetime.date.today()) &
                     (Product.active == True)
                 )
                 .order_by(Product.expiration_date))
        
        data = []
        for prod in query:
            # Intentar obtener el inventario
            inv_quantity = prod.inventory.quantity if hasattr(prod, 'inventory') else 0

            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
                "unit": prod.unit,
                "quantity": inv_quantity,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "date_added": prod.date_added,
                "expiration_date": prod.expiration_date,
                "location": prod.location,
                "active": prod.active
            })
        return data
        
    except Exception as e:
        print(f"Error al listar vencimientos: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def list_categories():
    """Devuelve todas las categorías (id, name, description)."""
    try:
        db.connect()
        cats = []
        for c in Category.select().order_by(Category.name):
            cats.append({
                "id": c.id,
                "name": c.name,
                "description": c.description
            })
        return cats
    except Exception as e:
        print(f"Error al listar categorías: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def list_products_by_category(category_id):
    """Lista productos filtrados por ID de categoría."""
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Product.category == category_id))
        
        data = []
        for inv in query:
            prod = inv.product
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
                "unit": prod.unit,
                "quantity": inv.quantity,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "date_added": prod.date_added,
                "expiration_date": prod.expiration_date,
                "location": prod.location,
                "active": prod.active
            })
        return data
    except Exception as e:
        print(f"Error al listar productos por categoría: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def update_category(category_id, name=None, description=None):
    """Actualiza el nombre y/o descripción de una categoría existente."""
    try:
        db.connect()
        with db.atomic():
            category = Category.get_by_id(category_id)
            old_name = category.name
            
            # Actualizar solo los campos que se proporcionen
            if name is not None and name.strip():
                category.name = name.strip()
            if description is not None:
                category.description = description.strip() if description.strip() else None
            
            category.save()
            
        changes = []
        if name is not None and name.strip():
            changes.append(f"nombre cambiado de '{old_name}' a '{category.name}'")
        if description is not None:
            changes.append("descripción actualizada")
        
        change_msg = ", ".join(changes)
        return True, f"Categoría actualizada: {change_msg}."
        
    except Category.DoesNotExist:
        return False, f"Error: Categoría con ID {category_id} no encontrada."
    except IntegrityError:
        return False, f"Error: Ya existe una categoría con el nombre '{name}'."
    except Exception as e:
        return False, f"Error al actualizar la categoría: {e}"
    finally:
        if not db.is_closed():
            db.close()


def list_batches_for_product(product_barcode):
    """
    Lista todos los lotes activos de un producto específico.
    
    Args:
        product_barcode: Código de barras del producto
        
    Returns:
        Lista de diccionarios con información de lotes
    """
    try:
        db.connect()
        product = Product.get(Product.barcode == product_barcode)
        
        batches = (ProductBatch
                  .select()
                  .where(
                      (ProductBatch.product == product) &
                      (ProductBatch.active == True)
                  )
                  .order_by(ProductBatch.expiration_date.asc(nulls='LAST')))
        
        data = []
        for batch in batches:
            data.append({
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "purchase_date": batch.purchase_date.strftime('%Y-%m-%d %H:%M') if batch.purchase_date else "N/A",
                "expiration_date": batch.expiration_date.strftime('%Y-%m-%d') if batch.expiration_date else "Sin vencimiento"
            })
        return data
    except Product.DoesNotExist:
        return []
    except Exception as e:
        print(f"Error al listar lotes: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
