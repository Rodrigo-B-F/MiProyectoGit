# src/models/inventory.py
"""
Modelos relacionados con el inventario y movimientos de stock.
"""

import datetime
from peewee import *
from .database import BaseModel
from .product import Product


class Inventory(BaseModel):
    """Inventario actual de cada producto."""
    id = AutoField()
    product = ForeignKeyField(Product, backref='inventory', unique=True)
    quantity = IntegerField(default=0)
    last_updated = DateTimeField(default=datetime.datetime.now)


class StockMovement(BaseModel):
    """Registro de movimientos de stock (entradas/salidas)."""
    id = AutoField()
    product = ForeignKeyField(Product, backref='movements')
    batch = IntegerField(null=True)         # Referencia al batch_number del lote
    change = IntegerField()                 # positivo = entrada, negativo = salida
    reason = CharField(null=True)           # 'purchase', 'sale', 'adjustment', etc.
    timestamp = DateTimeField(default=datetime.datetime.now)
    reference = CharField(null=True)        # Ej: ID de venta o nota
