from peewee import IntegrityError, JOIN, fn
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


def list_products_inventory():
    """Lista productos con inventario, categoría y ganancia."""
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .join(Category, JOIN.LEFT_OUTER))

        data = []
        for inv in query:
            prod = inv.product
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
                "quantity": inv.quantity,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "expiration_date": prod.expiration_date
            })
        return data
    except Exception as e:
        print(f"Error al listar inventario: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()




def find_product_by_name_or_barcode(search):
    """Busca productos por nombre o código de barras."""
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
                "quantity": inv.quantity if inv else 0,
                "sale_price": prod.sale_price
            })
        return data
    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return []
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


def list_expiring_products(days=30):
    """Lista productos próximos a vencer en X días."""
    try:
        db.connect()
        date_limit = datetime.date.today() + datetime.timedelta(days=days)
        query = (Product
                 .select(Product.name, Product.expiration_date, Inventory.quantity, Product.location)
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .where(
                     (Product.expiration_date.is_null(False)) &
                     (Product.expiration_date <= date_limit) &
                     (Product.expiration_date >= datetime.date.today())
                 )
                 .order_by(Product.expiration_date)
                 .dicts())
        return list(query)
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
                "quantity": inv.quantity,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "expiration_date": prod.expiration_date
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
                "quantity": inv.quantity,
                "sale_price": prod.sale_price,
                "expiration_date": prod.expiration_date
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


def list_products_by_category(category_name):
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
                 .where(fn.LOWER(Category.name).contains(category_name.lower()))
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
                "quantity": inv.quantity if inv else 0,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "expiration_date": prod.expiration_date,
                "location": prod.location
            })
        return data
    except Exception as e:
        print(f"Error al listar por categoría: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
