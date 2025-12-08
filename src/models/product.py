# src/models/product.py
"""
Modelo de Producto (Simplificado).
"""

from decimal import Decimal
from peewee import *
from .database import BaseModel
from .category import Category


class Product(BaseModel):
    """Producto del inventario."""
    id = AutoField()
    name = CharField(unique=True, index=True)      # Nombre único del producto
    barcode = CharField(unique=True, index=True)   # Código de barras único
    category = ForeignKeyField(Category, backref='products', null=True)
    location = CharField(null=True)                # Ej: 'Pasillo A - Estante 3'
    sale_price = DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    active = BooleanField(default=True)            # Si el producto está disponible
