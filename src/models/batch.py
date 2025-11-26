# src/models/batch.py
"""
Modelo de Lote de Producto.
Permite rastrear productos por lote con fechas de vencimiento específicas.
"""

import datetime
from decimal import Decimal
from peewee import *
from .database import BaseModel
from .product import Product


class ProductBatch(BaseModel):
    """Lote de producto con fecha de vencimiento específica."""
    id = AutoField()
    product = ForeignKeyField(Product, backref='batches')
    quantity = IntegerField(default=0)
    expiration_date = DateField(null=True)
    purchase_date = DateTimeField(default=datetime.datetime.now)
    purchase_price = DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    batch_number = IntegerField()  # Número secuencial por producto: 0, 1, 2, ...
    active = BooleanField(default=True)  # False cuando quantity = 0

    class Meta:
        indexes = (
            # Índice compuesto para búsquedas rápidas por producto
            (('product', 'batch_number'), True),  # Único por producto
        )

    def __str__(self):
        exp_str = f" (Vence: {self.expiration_date})" if self.expiration_date else ""
        return f"Lote {self.batch_number}{exp_str}"
