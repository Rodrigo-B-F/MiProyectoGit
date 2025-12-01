"""
Módulo de reportes de ventas.
Contiene funciones para listar historial y resúmenes de ventas.
"""

from peewee import fn
from models import db, Sale, SaleItem, Product

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
