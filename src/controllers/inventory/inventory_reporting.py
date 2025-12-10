"""
Módulo de reportes de inventario (Simplificado).
Contiene funciones para listar productos con diferentes criterios de inventario.
"""

from peewee import JOIN
from models import db, Category, Product, Inventory

def list_products_inventory(option):
    """
    Lista productos con inventario y categoría.
    Option: 1 para activos, 0 para inactivos (o todos si se modifica la lógica).
    """
    try:
        db.connect()
        if option == 1: option = True
        else: option = False
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Product.active == option))
        
        data = []
        for inv in query:
            prod = inv.product
            # Safely get category name
            category_name = None
            if prod.category_id:
                try:
                    category_name = prod.category.name
                except:
                    category_name = "Sin categoría"
            
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": category_name,
                "quantity": inv.quantity,
                "sale_price": prod.sale_price,
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
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Inventory.quantity > 0)
                 .where(Product.active == True))
        
        results = []
        for inv in query:
            prod = inv.product
            # Safely get category name
            category_name = "N/A"
            if prod.category_id:
                try:
                    category_name = prod.category.name
                except:
                    category_name = "Sin categoría"
            
            results.append({
                "barcode": prod.barcode,
                "name": prod.name,
                "category_name": category_name,
                "quantity": inv.quantity,
                "sale_price": prod.sale_price,
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
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Inventory.quantity <= 0)
                 .where(Product.active == True))
        
        results = []
        for inv in query:
            prod = inv.product
            # Safely get category name
            category_name = "N/A"
            if prod.category_id:
                try:
                    category_name = prod.category.name
                except:
                    category_name = "Sin categoría"
            
            results.append({
                "barcode": prod.barcode,
                "name": prod.name,
                "category_name": category_name,
                "quantity": 0,
                "sale_price": prod.sale_price,
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

def get_low_stock_products(threshold=10):
    """
    Obtiene productos con stock bajo (menor al umbral especificado).
    Retorna: nombre, código, categoría, cantidad, ubicación
    """
    try:
        db.connect()
        query = (Inventory
                 .select(Inventory, Product, Category)
                 .join(Product)
                 .switch(Product)
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Inventory.quantity < threshold)
                 .where(Product.active == True)
                 .order_by(Inventory.quantity.asc()))
        
        results = []
        for inv in query:
            prod = inv.product
            # Safely get category name
            category_name = "Sin Categoría"
            if prod.category_id:
                try:
                    category_name = prod.category.name
                except:
                    category_name = "Sin Categoría"
            
            results.append({
                'name': prod.name,
                'barcode': prod.barcode,
                'category_name': category_name,
                'quantity': inv.quantity,
                'location': prod.location if prod.location else 'Sin ubicación'
            })
        return results
    except Exception as e:
        print(f"Error al obtener productos con stock bajo: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
