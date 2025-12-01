"""
Módulo de CRUD de productos.
Contiene funciones para crear, actualizar y cambiar estado de productos.
"""

from peewee import IntegrityError
import datetime
from decimal import Decimal
from models import db, Category, Product, Inventory, StockMovement

def add_product(name, barcode, category_name, unit, location, purchase_price, sale_price, initial_quantity, expiration_date=None):
    """
    Registra un nuevo producto y su inventario inicial.
    Retorna True si la operación fue exitosa, False en caso de error.
    """
    try:
        db.connect()
        with db.atomic():
            category, _ = Category.get_or_create(name=category_name)

            product = Product.create(
                name=name,
                barcode=barcode,
                category=category,
                unit=unit,
                location=location,
                purchase_price=Decimal(purchase_price),
                sale_price=Decimal(sale_price),
                expiration_date=expiration_date
            )

            Inventory.create(
                product=product,
                quantity=initial_quantity,
                last_updated=datetime.datetime.now()
            )

            StockMovement.create(
                product=product,
                change=initial_quantity,
                reason='initial_stock',
                reference='Primer Ingreso'
            )
        
        return True, f"Producto '{name}' agregado y {initial_quantity} unidades en stock."

    except IntegrityError:
        return False, f"Error: El código de barras '{barcode}' ya existe."
    except Exception as e:
        return False, f"Error desconocido al agregar producto: {e}"
    finally:
        if not db.is_closed():
            db.close()

def toggle_product_status(barcode, new_status=None):
    """
    Activa o desactiva un producto (cambia el campo 'active').
    Si new_status no se proporciona, invierte el estado actual.
    
    Retorna (True, mensaje_exito) o (False, mensaje_error).
    """
    try:
        db.connect()
        product = Product.get(Product.barcode == barcode)
        
        if new_status is None:
            product.active = not product.active
        else:
            product.active = new_status
            
        product.save()
        
        status_str = "activado" if product.active else "desactivado"
        return True, f"Producto '{product.name}' {status_str} exitosamente."
        
    except Product.DoesNotExist:
        return False, f"Producto con código {barcode} no encontrado."
    except Exception as e:
        return False, f"Error al cambiar estado del producto: {e}"
    finally:
        if not db.is_closed():
            db.close()

def update_product_details(product_id, name, new_barcode, category_name, unit, location, 
                           purchase_price, sale_price, expiration_date_str, 
                           date_added_str, active_status=None):
    """
    Actualiza los detalles de un producto por su ID.
    """
    try:
        db.connect()
        with db.atomic():
            product = Product.get_by_id(product_id)
            
            # Actualizar categoría
            if category_name:
                category, _ = Category.get_or_create(name=category_name)
                product.category = category
            
            # Actualizar campos básicos
            product.name = name
            product.barcode = new_barcode
            product.unit = unit
            product.location = location
            product.purchase_price = Decimal(purchase_price)
            product.sale_price = Decimal(sale_price)
            
            # Actualizar fechas si se proporcionan
            if expiration_date_str and expiration_date_str != "N/A":
                try:
                    product.expiration_date = datetime.datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass # Mantener fecha anterior si el formato es inválido
            
            if date_added_str:
                try:
                    product.date_added = datetime.datetime.strptime(date_added_str, '%Y-%m-%d')
                except ValueError:
                    pass

            if active_status is not None:
                product.active = active_status

            product.save()
            
        return True, "Producto actualizado exitosamente."
        
    except Product.DoesNotExist:
        return False, f"Producto con ID {product_id} no encontrado."
    except IntegrityError:
        return False, f"Error: El código de barras '{new_barcode}' ya está en uso por otro producto."
    except Exception as e:
        return False, f"Error al actualizar producto: {e}"
    finally:
        if not db.is_closed():
            db.close()
