"""
Módulo de reportes de ventas.
Contiene funciones para listar historial y resúmenes de ventas.
"""

from peewee import fn, JOIN
from models import db, Sale, SaleItem, Product, Inventory

def list_sales_history():
    """
    Lista el historial de ventas detallado.
    """
    try:
        db.connect()
        query = (SaleItem
                 .select(SaleItem, Sale, Product)
                 .join(Sale)
                 .switch(SaleItem)
                 .join(Product)
                 .order_by(Sale.timestamp.desc()))
        
        history = []
        for item in query:
            history.append({
                "sale_id": item.sale.id,
                "timestamp": item.sale.timestamp.strftime("%Y-%m-%d %H:%M"),
                "product": item.product.name,
                "barcode": item.product.barcode,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal
            })
        return history
    except Exception as e:
        print(f"Error al listar historial de ventas: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def sales_summary_by_date():
    """
    Agrupa ventas por fecha.
    """
    try:
        db.connect()
        # SQLite: strftime('%Y-%m-%d', timestamp)
        query = (Sale
                 .select(fn.strftime('%Y-%m-%d', Sale.timestamp).alias('date'), 
                         fn.SUM(Sale.total).alias('total_amount'),
                         fn.COUNT(Sale.id).alias('total_sales'))
                 .group_by(fn.strftime('%Y-%m-%d', Sale.timestamp))
                 .order_by(fn.strftime('%Y-%m-%d', Sale.timestamp).desc()))
        
        summary = []
        for row in query:
            summary.append({
                "date": row.date,
                "total_amount": row.total_amount,
                "total_sales": row.total_sales
            })
        return summary
    except Exception as e:
        print(f"Error al obtener resumen de ventas: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def get_top_selling_products(limit=10):
    """
    Obtiene los productos más vendidos.
    Retorna: nombre, total vendido
    """
    try:
        db.connect()
        query = (SaleItem
                 .select(Product.name, fn.SUM(SaleItem.quantity).alias('total_sold'))
                 .join(Product)
                 .group_by(Product.id)
                 .order_by(fn.SUM(SaleItem.quantity).desc())
                 .limit(limit))
        
        results = []
        for item in query:
            results.append({
                'product': item.product.name,
                'total_sold': item.total_sold
            })
        return results
    except Exception as e:
        print(f"Error al obtener productos más vendidos: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def get_least_selling_products(limit=10):
    """
    Obtiene los productos menos vendidos (pero que tienen al menos 1 venta).
    Retorna: nombre, total vendido
    """
    try:
        db.connect()
        query = (SaleItem
                 .select(Product.name, fn.SUM(SaleItem.quantity).alias('total_sold'))
                 .join(Product)
                 .group_by(Product.id)
                 .order_by(fn.SUM(SaleItem.quantity).asc())
                 .limit(limit))
        
        results = []
        for item in query:
            results.append({
                'product': item.product.name,
                'total_sold': item.total_sold
            })
        return results
    except Exception as e:
        print(f"Error al obtener productos menos vendidos: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def get_unsold_products(limit=10):
    """
    Obtiene productos que nunca se han vendido.
    Retorna: nombre, total vendido (0)
    """
    try:
        db.connect()
        # Get all products that don't have any sales
        sold_product_ids = (SaleItem
                           .select(SaleItem.product)
                           .distinct())
        
        query = (Product
                 .select(Product.name)
                 .where(~(Product.id.in_(sold_product_ids)))
                 .limit(limit))
        
        results = []
        for product in query:
            results.append({
                'product': product.name,
                'total_sold': 0  # No sales
            })
        return results
    except Exception as e:
        print(f"Error al obtener productos no vendidos: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
