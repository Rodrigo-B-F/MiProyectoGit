"""
Módulo de búsqueda de productos.
Contiene funciones para buscar y listar productos.
"""

from peewee import JOIN
from models import db, Category, Product, Inventory

def find_product_by_name_or_barcode(query):
    """
    Busca un producto por nombre, código de barras o categoría.
    Usa coincidencias parciales para mejor experiencia de búsqueda.
    SIEMPRE retorna una lista de diccionarios.
    """
    try:
        if db.is_closed():
            db.connect()

        # JOIN con Category e Inventory para buscar en todos los campos
        product_query = (
            Product
            .select(Product, Inventory, Category)
            .join(Inventory, JOIN.LEFT_OUTER)
            .switch(Product)
            .join(Category, JOIN.LEFT_OUTER)
            .where(
                (Product.name.contains(query)) |
                (Product.barcode.contains(query)) |  # Coincidencia parcial en barcode
                (Category.name.contains(query))      # Búsqueda por categoría
            )
        )

        results = []

        for prod in product_query:
            # Obtener inventario real
            inv = Inventory.get_or_none(Inventory.product == prod)
            quantity = inv.quantity if inv else 0

            # Armar diccionario del producto
            results.append({
                "id": prod.id,
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": prod.category.name if prod.category else "Sin Categoría",
                "location": prod.location,
                "sale_price": prod.sale_price,
                "quantity": quantity,
                "active": prod.active
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
                "quantity": quantity,
                "sale_price": prod.sale_price,
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
            "location": product.location,
            "sale_price": product.sale_price,
            "quantity": quantity,
            "active": product.active
        }
        
    except Product.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error al obtener detalles del producto: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()
