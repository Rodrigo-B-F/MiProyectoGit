from peewee import IntegrityError, JOIN, fn, DoesNotExist
import datetime
from decimal import Decimal

# Importamos los modelos definidos en models.py
from .models import db, Category, Product, Inventory, StockMovement, Sale, SaleItem

# --- GESTIÓN DE PRODUCTOS E INVENTARIO ---

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


def record_purchase(product_barcode, quantity, purchase_price):
    """Registra la compra de stock para un producto existente."""
    try:
        db.connect()
        with db.atomic():
            product = Product.get(Product.barcode == product_barcode)
            product.purchase_price = Decimal(purchase_price)
            product.save()

            inventory = Inventory.get(Inventory.product == product)
            inventory.quantity += quantity
            inventory.last_updated = datetime.datetime.now()
            inventory.save()
            
            StockMovement.create(
                product=product,
                change=quantity,
                reason='purchase',
                reference=f'Compra de {quantity} unidades'
            )
            
        return True, f"Stock actualizado. {quantity} unidades de '{product.name}' añadidas. Nuevo stock: {inventory.quantity}"
        
    except Product.DoesNotExist:
        return False, f"Error: Producto con código {product_barcode} no encontrado."
    except Exception as e:
        return False, f"Error al registrar la compra: {e}"
    finally:
        if not db.is_closed():
            db.close()


def record_sale(items_to_sell):
    """Registra una venta completa (con múltiples productos)."""
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

                inventory.quantity -= qty
                inventory.last_updated = datetime.datetime.now()
                inventory.save()

                StockMovement.create(
                    product=product, change=-qty,
                    reason='sale', reference=f'Venta ID: {sale.id}'
                )

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



# USE ESTA FUNCIÓN PARA EL cli.py
"""def find_product_by_name_or_barcode(search):
    # Busca productos por nombre o código de barras.
    
    try:
        db.connect()
        query = (Product
                 .select(Product, Inventory, Category)
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(
                     (Product.name.contains(search)) |
                     (Product.barcode == search)
                 ))
        data = []
        for prod in query:
            inv = None
            try:
                inv = Inventory.get(Inventory.product == prod)
            except Inventory.DoesNotExist:
                pass

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
        print(f"Error al buscar producto: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()"""

"""def find_product_by_name_or_barcode(query):
    #Busca un producto por nombre o código de barras.
    #Retorna el ID, nombre y código de barras del producto encontrado, o None.
    from peewee import DoesNotExist
    try:
        db.connect()
        product = Product.get(
            (Product.name.contains(query)) | 
            (Product.barcode == query)
        )
        # Retornamos datos esenciales para la TUI
        return {
            "id": product.id,
            "name": product.name, 
            "barcode": product.barcode,
            "category_name": product.category.name if product.category else 'N/A',
            "unit": product.unit,
            # Añadir más campos si se van a mostrar en la TUI de selección
        }
    except DoesNotExist:
        return None
    except Exception as e:
        # print(f"Error en la búsqueda: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()"""

# CAMBIADO PARA EL TUI
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

def filter_products_by_category(category_name):
    """Filtra el inventario por categoría."""
    try:
        db.connect()
        query = (Product
                 .select(Product, Inventory, Category)
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Category.name.contains(category_name))
                 .dicts())
        return list(query)
    except Exception as e:
        print(f"Error al filtrar por categoría: {e}")
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
        
        # 1. Ajustar la consulta para seleccionar los modelos Product, Inventory y Category
        query = (Product
                 .select(Product, Inventory, Category) 
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER) # Incluimos Category
                 .where(
                     (Product.expiration_date.is_null(False)) &
                     (Product.expiration_date <= date_limit) &
                     (Product.expiration_date >= datetime.date.today()) &
                     (Product.active == True)
                 )
                 .order_by(Product.expiration_date))
        
        data = []
        for prod in query:
            # Intentar obtener el inventario, si no existe, quantity es 0
            inv_quantity = prod.inventory.quantity if hasattr(prod, 'inventory') else 0

            # 2. Construir el diccionario con todos los campos solicitados
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
    """
    Lista productos que pertenecen a categorías cuyo nombre contiene `category_name`
    (búsqueda insensible a mayúsculas).
    Retorna lista de diccionarios con: name, barcode, category_name, quantity, sale_price, profit, expiration_date, location.
    """
    try:
        db.connect()
        # Buscamos productos asociados a categorías que coincidan (case-insensitive)
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

#USE ESTA FUNCIÓN PARA EL CLI
"""def update_product_details(old_barcode, name=None, new_barcode=None, category_name=None, unit=None, 
                           location=None, purchase_price=None, sale_price=None, 
                           expiration_date_str=None):
    Modifica los detalles de un producto existente.
    Usa old_barcode para encontrar el producto. Solo actualiza los campos
    que no son None o cadenas vacías.
    
    Retorna (True, mensaje_exito) o (False, mensaje_error).
    try:
        db.connect()
        with db.atomic():
            # 1. Buscar el producto usando el código de barras actual
            product = Product.get(Product.barcode == old_barcode)
            
            # 2. Actualizar Código de Barras (manejo de unicidad)
            if new_barcode is not None and new_barcode.strip():
                new_barcode = new_barcode.strip()
                if new_barcode != old_barcode:
                    # Verificar si el nuevo código ya existe
                    if Product.select().where(Product.barcode == new_barcode).exists():
                        raise IntegrityError(f"Error: El nuevo código de barras '{new_barcode}' ya está en uso.")
                    product.barcode = new_barcode # Si es único, se actualiza
            
            # 3. Actualizar otros campos si fueron proporcionados
            if name is not None and name.strip():
                product.name = name.strip()
            
            # Si se proporciona un nombre de categoría, asegúrate de que exista o créala
            if category_name is not None and category_name.strip():
                category, _ = Category.get_or_create(name=category_name.strip())
                product.category = category
            
            if unit is not None and unit.strip():
                product.unit = unit.strip()
            
            if location is not None and location.strip():
                product.location = location.strip()
            
            # Manejo de precios (se asume que se envían como float/Decimal desde el CLI)
            if purchase_price is not None:
                product.purchase_price = Decimal(purchase_price)
            
            if sale_price is not None:
                product.sale_price = Decimal(sale_price)
                
            # Manejo de fecha de vencimiento
            if expiration_date_str is not None:
                if expiration_date_str.strip():
                    # Intenta parsear la fecha (YYYY-MM-DD)
                    product.expiration_date = datetime.datetime.strptime(expiration_date_str.strip(), '%Y-%m-%d').date()
                else:
                    product.expiration_date = None # Permite quitar la fecha
            
            product.save()
            
        return True, f"Producto '{product.name}' (Código {product.barcode}) actualizado exitosamente."
        
    except Product.DoesNotExist:
        return False, f"Error: Producto con código {old_barcode} no encontrado."
    except IntegrityError as ie:
        return False, str(ie) 
    except ValueError:
        return False, "Error de valor: Los precios o la fecha (formato YYYY-MM-DD) son inválidos."
    except Exception as e:
        return False, f"Error al actualizar producto: {e}"
    finally:
        if not db.is_closed():
            db.close()"""

#CAMBIADO PARA EL TUI
def update_product_details(product_id, name, new_barcode, category_name, unit, location, 
                           purchase_price, sale_price, expiration_date_str, 
                           date_added_str, active_status=None): # <-- Parámetro añadido
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
            
            # --- LÓGICA AÑADIDA ---
            # 7. Manejo de fecha de adquisición (Asumimos que ya está validada por la TUI)
            if date_added_str:
                product.date_added = datetime.datetime.strptime(date_added_str, '%Y-%m-%d').date()
            # --- FIN LÓGICA AÑADIDA ---
                    
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
            # Opcional: Solo si el precio de venta es actualmente mayor al precio de compra
            (Product.sale_price > Product.purchase_price) 
        )
        
        count = 0
        updated_products = []

        with db.atomic():
            for product in products_to_update:
                # 2. Aplicar la oferta (Precio de Venta = Precio de Compra)
                # No se actualiza si ya tiene el precio de compra o menos
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

#AÑADIDOS PARA QUE FUNCIONE EL TUI

def get_product_details_by_id(product_id):
    """
    Obtiene todos los detalles de un producto por su ID.
    """
    try:
        db.connect()
        
        # Si tienes la propiedad 'profit' en models.py, puedes incluirla
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
        # print(f"Error al obtener detalles por ID: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()

    