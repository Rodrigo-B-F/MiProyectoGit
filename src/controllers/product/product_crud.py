"""
Módulo de CRUD de productos.
Contiene funciones para crear, actualizar y cambiar estado de productos.
"""

from peewee import IntegrityError
import datetime
from decimal import Decimal
from models import db, Category, Product, Inventory, StockMovement

def add_product(name, barcode, category_name, location, sale_price, initial_quantity):
    """
    Registra un nuevo producto y su inventario inicial.
    Retorna True si la operación fue exitosa, False en caso de error.
    """
    try:
        db.connect()
        with db.atomic():
            # Verificar si ya existe un producto con el mismo nombre
            existing_product = Product.select().where(Product.name == name).first()
            if existing_product:
                return False, f"Ya existe un producto con el nombre '{name}'"
            
            category, _ = Category.get_or_create(name=category_name)

            product = Product.create(
                name=name,
                barcode=barcode,
                category=category,
                location=location,
                sale_price=Decimal(sale_price)
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

def update_product_details(product_id, name, new_barcode, category_name, location, 
                           sale_price, active_status=None):
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
            product.location = location
            product.sale_price = Decimal(sale_price)

            if active_status is not None:
                # Convert string "True"/"False" to boolean
                if isinstance(active_status, str):
                    product.active = active_status == "True"
                else:
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
