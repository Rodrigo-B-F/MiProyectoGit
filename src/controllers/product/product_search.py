"""
Módulo de búsqueda de productos.
Contiene funciones para buscar y listar productos.
"""

from peewee import JOIN
from models import db, Category, Product, Inventory

def find_product_by_name_or_barcode(query):
    """
    Busca un producto por nombre o código de barras.
    SIEMPRE retorna una lista de diccionarios.
    Esto evita errores en SearchScreen y ModifyScreen.
    """
    try:
        if db.is_closed():
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
                "category_name": prod.category.name if prod.category else "Sin Categoría",
                "unit": prod.unit,
                "location": prod.location,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "quantity": quantity,
                "profit": profit,
                "active": prod.active,
                "expiration_date": prod.expiration_date,
                "date_added": prod.date_added
            })

        return results

    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def list_products_by_category(category_id):
    """
    Lista todos los productos de una categoría específica por su ID.
    """
    try:
        if db.is_closed():
            db.connect()
        
        query = (Product
                 .select(Product, Inventory)
                 .join(Category)
                 .switch(Product)
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .where(Category.id == category_id))
        
        results = []
        for prod in query:
            inv = Inventory.get_or_none(Inventory.product == prod)
            quantity = inv.quantity if inv else 0
            
            results.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else "N/A",
                "unit": prod.unit,
                "quantity": quantity,
                "purchase_price": prod.purchase_price,
                "sale_price": prod.sale_price,
                "profit": prod.profit,
                "location": prod.location,
                "active": prod.active
            })
            
        return results
        
    except Exception as e:
        print(f"Error al listar productos por categoría: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def get_product_details_by_id(product_id):
    """
    Obtiene los detalles completos de un producto por su ID.
    Retorna un diccionario o None si no existe.
    """
    try:
        db.connect()
        product = Product.get_by_id(product_id)
        
        # Obtener inventario
        inv = Inventory.get_or_none(Inventory.product == product)
        quantity = inv.quantity if inv else 0
        
        return {
            "id": product.id,
            "name": product.name,
            "barcode": product.barcode,
            "category_name": product.category.name if product.category else "Sin Categoría",
            "unit": product.unit,
            "location": product.location,
            "purchase_price": product.purchase_price,
            "sale_price": product.sale_price,
            "quantity": quantity,
            "expiration_date": product.expiration_date,
            "date_added": product.date_added,
            "active": product.active,
            "profit": product.sale_price - product.purchase_price
        }
        
    except Product.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error al obtener detalles del producto: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()
