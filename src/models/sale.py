# src/models/sale.py
"""
Modelos relacionados con las ventas.
"""

import datetime
from decimal import Decimal
from peewee import *
from .database import BaseModel
from .product import Product


class Sale(BaseModel):
    """Venta realizada."""
    id = AutoField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    total = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


class SaleItem(BaseModel):
    """Item individual de una venta."""
    id = AutoField()
    sale = ForeignKeyField(Sale, backref='items')
    product = ForeignKeyField(Product, backref='sale_items')
    quantity = IntegerField()
    unit_price = DecimalField(max_digits=10, decimal_places=2)
    subtotal = DecimalField(max_digits=12, decimal_places=2)
