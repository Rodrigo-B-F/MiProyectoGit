# src/controllers/product_controller.py
"""
Controlador de Productos - Lógica de negocio relacionada con productos.
"""

from peewee import IntegrityError, JOIN, DoesNotExist
import datetime
from decimal import Decimal

from models import db, Category, Product, Inventory, ProductBatch, StockMovement


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
        with db.atomic():
            product = Product.get(Product.barcode == barcode)
            
            # Determinar el nuevo estado
            if new_status is None:
                new_status = not product.active
            
            product.active = new_status
            product.save()
            
            status_text = "activado" if new_status else "desactivado"
            
        return True, f"Producto '{product.name}' ({barcode}) ha sido {status_text} exitosamente."
        
    except Product.DoesNotExist:
        return False, f"Error: Producto con código {barcode} no encontrado."
    except Exception as e:
        return False, f"Error al cambiar el estado del producto: {e}"
    finally:
        if not db.is_closed():
            db.close()


def find_product_by_name_or_barcode(query):
    """
    Busca un producto por nombre o código de barras.
    SIEMPRE retorna una lista de diccionarios.
    Esto evita errores en SearchScreen y ModifyScreen.
    """
    try:
        db.connect()

        # JOIN correcto con Inventory
        product_query = (
            Product
            .select(Product, Inventory)
            .join(Inventory, JOIN.LEFT_OUTER)
            .where(
                (Product.name.contains(query)) |
                (Product.barcode == query)
            )
        )

        results = []

        for prod in product_query:
            # Obtener inventario real
            inv = Inventory.get_or_none(Inventory.product == prod)
            quantity = inv.quantity if inv else 0

            profit = prod.sale_price - prod.purchase_price

            # Armar diccionario del producto
            results.append({
                "id": prod.id,
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else "N/A",
                "unit": prod.unit,
                "quantity": quantity,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": profit,
                "date_added": prod.date_added.strftime('%Y-%m-%d'),
                "expiration_date": (
                    prod.expiration_date.strftime('%Y-%m-%d')
                    if prod.expiration_date else "N/A"
                ),
                "location": prod.location,
                "active": "Activo" if prod.active else "Inactivo",
            })

        return results

    except Exception:
        return []  # SAFE para todas las pantallas

    finally:
        if not db.is_closed():
            db.close()


def list_products_by_category(category_id):
    """
    Lista productos que pertenecen a una categoría específica.
    Retorna lista de diccionarios con: name, barcode, category_name, quantity, sale_price, profit, expiration_date, location.
    """
    try:
        db.connect()
        query = (Product
                 .select(Product, Inventory, Category)
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Category.id == category_id)
                 .order_by(Product.name))

        data = []
        for prod in query:
            # Obtener inventario si existe
            inv = None
            try:
                inv = Inventory.get(Inventory.product == prod)
            except Inventory.DoesNotExist:
                inv = None

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
        print(f"Error al listar por categoría: {e}")
        return []
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
            # 1. Buscar el producto por ID
            product = Product.get_by_id(product_id)
            
            # 2. Actualizar la categoría (usar o crear)
            if category_name and product.category.name != category_name:
                 category, _ = Category.get_or_create(name=category_name)
                 product.category = category

            # 3. Actualizar campos simples
            if name: product.name = name
            if new_barcode: product.barcode = new_barcode
            if unit: product.unit = unit
            
            product.location = location if location else None
            
            # 4. Actualizar precios (Decimal)
            if purchase_price is not None:
                product.purchase_price = Decimal(purchase_price)
            
            if sale_price is not None:
                product.sale_price = Decimal(sale_price)

            # 5. Manejo del estado 'active'
            if active_status is not None:
                product.active = active_status == "True"

            # 6. Manejo de fecha de vencimiento
            if expiration_date_str is not None:
                expiration_date_str = expiration_date_str.strip()
                if expiration_date_str:
                    product.expiration_date = datetime.datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                else:
                    product.expiration_date = None
            
            # 7. Manejo de fecha de adquisición
            if date_added_str:
                product.date_added = datetime.datetime.strptime(date_added_str, '%Y-%m-%d').date()
                    
            product.save()
            
            return True, f"Producto '{product.name}' (Código {product.barcode}) actualizado exitosamente."
            
    except Product.DoesNotExist:
        return False, f"Error: Producto con ID {product_id} no encontrado."
    except IntegrityError:
        return False, f"Error: El código de barras '{new_barcode}' ya existe en otro producto."
    except ValueError:
        return False, "Error de valor: Los precios o las fechas (formato YYYY-MM-DD) son inválidos."
    except Exception as e:
        return False, f"Error inesperado al actualizar el producto: {e}"
    finally:
        if not db.is_closed():
            db.close()


def apply_expiring_product_offer(days_limit=10):
    """
    Aplica una oferta a productos que expiran dentro del límite de días especificado.
    El precio de venta se reduce al precio de compra.
    Retorna (True, mensaje) o (False, mensaje).
    """
    try:
        db.connect()
        date_limit = datetime.date.today() + datetime.timedelta(days=days_limit)
        
        # 1. Encontrar productos que expiran en el límite de días
        products_to_update = Product.select().where(
            (Product.expiration_date.is_null(False)) &
            (Product.expiration_date <= date_limit) &
            (Product.expiration_date >= datetime.date.today()) &
            (Product.sale_price > Product.purchase_price) 
        )
        
        count = 0
        updated_products = []

        with db.atomic():
            for product in products_to_update:
                # 2. Aplicar la oferta (Precio de Venta = Precio de Compra)
                if product.sale_price > product.purchase_price:
                    product.sale_price = product.purchase_price
                    product.save()
                    updated_products.append(product.name)
                    count += 1
        
        if count > 0:
            return True, f"Éxito: Se aplicó la oferta a {count} productos (P.Venta = P.Compra). Productos afectados: {', '.join(updated_products)}"
        else:
            return True, f"Ningún producto encontrado que expire en los próximos {days_limit} días o que necesitara una actualización de precio."
            
    except Exception as e:
        return False, f"Error al aplicar la oferta: {e}"
    finally:
        if not db.is_closed():
            db.close()


def get_product_details_by_id(product_id):
    """
    Obtiene todos los detalles de un producto por su ID.
    """
    try:
        db.connect()
        
        product = Product.get_by_id(product_id)
        
        # Obtener inventario si existe
        inv = Inventory.get_or_none(Inventory.product == product)

        # Calcular el profit
        profit = product.sale_price - product.purchase_price

        return {
            "id": product.id,
            "name": product.name,
            "barcode": product.barcode,
            "category_name": product.category.name if product.category else 'N/A',
            "unit": product.unit,
            "location": product.location,
            "purchase_price": product.purchase_price,
            "sale_price": product.sale_price,
            "profit": profit,
            "quantity": inv.quantity if inv else 0,
            "purchase_date": product.date_added,
            "expiration_date": product.expiration_date,
            "active": product.active
        }
    except DoesNotExist:
        return None
    except Exception as e:
        return None
    finally:
        if not db.is_closed():
            db.close()
