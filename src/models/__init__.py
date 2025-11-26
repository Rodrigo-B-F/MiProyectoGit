# src/models/__init__.py
"""
Módulo de modelos - Capa de datos del patrón MVC.
Exporta todos los modelos y funciones de base de datos.
"""

from .database import db, BaseModel, init_db
from .category import Category
from .product import Product
from .inventory import Inventory, StockMovement
from .sale import Sale, SaleItem
from .batch import ProductBatch

__all__ = [
    'db',
    'BaseModel',
    'init_db',
    'Category',
    'Product',
    'Inventory',
    'StockMovement',
    'Sale',
    'SaleItem',
    'ProductBatch',
]
