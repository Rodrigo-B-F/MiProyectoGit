# src/models/product.py
"""
Modelo de Producto.
"""

import datetime
from decimal import Decimal
from peewee import *
from .database import BaseModel
from .category import Category


class Product(BaseModel):
    """Producto del inventario."""
    id = AutoField()
    name = CharField()
    barcode = CharField(unique=True, index=True)   # Código de barras único
    category = ForeignKeyField(Category, backref='products', null=True)
    unit = CharField()                             # Ej: 'kg', 'litro', 'unidad'
    location = CharField(null=True)                # Ej: 'Pasillo A - Estante 3'
    purchase_price = DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    sale_price = DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    date_added = DateTimeField(default=datetime.datetime.now)
    expiration_date = DateField(null=True)
    active = BooleanField(default=True)            # Si el producto está disponible

    @property
    def profit(self):
        """Devuelve la ganancia unitaria (venta - compra)."""
        return (self.sale_price - self.purchase_price)
