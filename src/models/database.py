# src/models/database.py
"""
Configuración de base de datos y modelo base para Peewee ORM.
"""

import datetime
from peewee import *
from config import DB_PATH

# Conexión a la base de datos SQLite
db = SqliteDatabase(DB_PATH)

# Modelo base para que todas las tablas usen la misma BD
class BaseModel(Model):
    class Meta:
        database = db


def init_db():
    """Inicializa la base de datos y crea todas las tablas."""
    from .category import Category
    from .product import Product
    from .inventory import Inventory, StockMovement
    from .sale import Sale, SaleItem
    
    db.connect()
    db.create_tables([Category, Product, Inventory, StockMovement, Sale, SaleItem])
    db.close()
