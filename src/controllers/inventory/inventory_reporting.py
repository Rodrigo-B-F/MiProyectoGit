"""
Módulo de reportes de inventario.
Contiene funciones para listar productos con diferentes criterios de inventario.
"""

from peewee import JOIN
from datetime import datetime, timedelta
from models import db, Category, Product, Inventory, ProductBatch

def list_products_inventory(option):
    """
    Lista productos con inventario, categoría y ganancia.
    Option: 1 para activos, 0 para inactivos (o todos si se modifica la lógica).
    """
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
    """
    Lista productos con stock > 0.
    """
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product)
                 .join(Product)
                 .where(Inventory.quantity > 0)
                 .where(Product.active == True))
        
        results = []
        for inv in query:
            prod = inv.product
            results.append({
                "barcode": prod.barcode,
                "name": prod.name,
                "category_name": prod.category.name if prod.category else "N/A",
                "unit": prod.unit,
                "quantity": inv.quantity,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "location": prod.location,
                "active": prod.active
            })
        return results
    except Exception as e:
        print(f"Error al listar productos disponibles: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def list_out_of_stock_products():
    """
    Lista productos con stock = 0.
    """
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product)
                 .join(Product)
                 .where(Inventory.quantity <= 0)
                 .where(Product.active == True))
        
        results = []
        for inv in query:
            prod = inv.product
            results.append({
                "barcode": prod.barcode,
                "name": prod.name,
                "category_name": prod.category.name if prod.category else "N/A",
                "unit": prod.unit,
                "quantity": 0,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "location": prod.location,
                "active": prod.active
            })
        return results
    except Exception as e:
        print(f"Error al listar productos sin stock: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def list_expiring_products(days=30):
    """
    Lista productos (lotes) próximos a vencer en 'days' días.
    """
    try:
        db.connect()
        target_date = datetime.now().date() + timedelta(days=days)
        
        # Buscar en lotes activos
        query = (ProductBatch
                 .select(ProductBatch, Product)
                 .join(Product)
                 .where(
                     (ProductBatch.expiration_date <= target_date) &
                     (ProductBatch.expiration_date >= datetime.now().date()) &
                     (ProductBatch.active == True) &
                     (ProductBatch.quantity > 0)
                 )
                 .order_by(ProductBatch.expiration_date))
        
        results = []
        for batch in query:
            prod = batch.product
            results.append({
                "barcode": prod.barcode,
                "name": prod.name,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "expiration_date": batch.expiration_date,
                "days_until": (batch.expiration_date - datetime.now().date()).days
            })
        return results
    except Exception as e:
        print(f"Error al listar productos por vencer: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def list_batches_for_product(product_barcode):
    """
    Lista todos los lotes de un producto específico.
    """
    try:
        db.connect()
        product = Product.get(Product.barcode == product_barcode)
        batches = ProductBatch.select().where(ProductBatch.product == product).order_by(ProductBatch.expiration_date)
        
        results = []
        for batch in batches:
            results.append({
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "expiration_date": batch.expiration_date,
                "purchase_date": batch.purchase_date,
                "active": batch.active
            })
        return results
    except Product.DoesNotExist:
        return []
    except Exception as e:
        print(f"Error al listar lotes: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
