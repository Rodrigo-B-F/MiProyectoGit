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
                 .join(Category, JOIN.LEFT_OUTER)
                 .where(Product.active == option))
        
        data = []
        for inv in query:
            prod = inv.product
            data.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else None,
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
