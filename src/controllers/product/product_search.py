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
                (
                    (Product.name.contains(query)) |
                    (Product.barcode.contains(query)) |
                    ((Product.category.is_null(False)) & (Category.name.contains(query)))
                ) &
                (Product.active == True)  # Only show active products
            )
        )

        results = []

        for prod in product_query:
            # Obtener inventario real
            inv = Inventory.get_or_none(Inventory.product == prod)
            quantity = inv.quantity if inv else 0

            # Safely get category name
            category_name = "Sin Categoría"
            if prod.category_id:
                try:
                    category_name = prod.category.name
                except:
                    category_name = "Sin Categoría"

            # Armar diccionario del producto
            results.append({
                "id": prod.id,
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": category_name,
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

def find_product_for_edit(query):
    """
    Busca un producto por nombre o código de barras INCLUYENDO inactivos.
    Usado para el formulario de edición donde necesitas poder modificar productos inactivos.
    """
    try:
        if db.is_closed():
            db.connect()

        # JOIN con Category e Inventory para buscar - SIN filtro de activo
        product_query = (
            Product
            .select(Product, Inventory, Category)
            .join(Inventory, JOIN.LEFT_OUTER)
            .switch(Product)
            .join(Category, JOIN.LEFT_OUTER)
            .where(
                (Product.name.contains(query)) |
                (Product.barcode.contains(query))
            )
        )

        results = []

        for prod in product_query:
            # Obtener inventario real
            inv = Inventory.get_or_none(Inventory.product == prod)
            quantity = inv.quantity if inv else 0

            # Safely get category name
            category_name = "Sin Categoría"
            if prod.category_id:
                try:
                    category_name = prod.category.name
                except:
                    category_name = "Sin Categoría"

            # Armar diccionario del producto
            results.append({
                "id": prod.id,
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": category_name,
                "location": prod.location,
                "sale_price": prod.sale_price,
                "quantity": quantity,
                "active": prod.active
            })

        return results

    except Exception as e:
        print(f"Error al buscar producto para editar: {e}")
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
                 .where((Category.id == category_id) & (Product.active == True)))
        
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

def list_products_without_category():
    """
    Lista todos los productos que NO tienen categoría asignada (category_id es NULL).
    """
    try:
        if db.is_closed():
            db.connect()
        
        query = (Product
                 .select(Product, Inventory)
                 .join(Inventory, JOIN.LEFT_OUTER)
                 .where((Product.category.is_null()) & (Product.active == True)))
        
        results = []
        for prod in query:
            inv = Inventory.get_or_none(Inventory.product == prod)
            quantity = inv.quantity if inv else 0
            
            results.append({
                "name": prod.name,
                "barcode": prod.barcode,
                "category_name": "Sin Categoría",
                "quantity": quantity,
                "sale_price": prod.sale_price,
                "location": prod.location,
                "active": prod.active
            })
            
        return results
        
    except Exception as e:
        print(f"Error al listar productos sin categoría: {e}")
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
        
        # Safely get category name
        category_name = "Sin Categoría"
        if product.category_id:
            try:
                category_name = product.category.name
            except:
                category_name = "Sin Categoría"
        
        return {
            "id": product.id,
            "name": product.name,
            "barcode": product.barcode,
            "category_name": category_name,
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
