# src/models/category.py
"""
Modelo de Categoría de productos.
"""

from peewee import *
from .database import BaseModel


class Category(BaseModel):
    """Categoría de productos del inventario."""
    id = AutoField()
    name = CharField(unique=True)
    description = TextField(null=True)
