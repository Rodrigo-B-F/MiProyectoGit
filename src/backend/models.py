import datetime
from decimal import Decimal
from peewee import *

db = SqliteDatabase('src/data/tienda.db')

# Modelo base para que todas las tablas usen la misma BD
class BaseModel(Model):
    class Meta:
        database = db

# -------------------
# TABLAS
# -------------------

class Category(BaseModel):
    id = AutoField()
    name = CharField(unique=True)
    description = TextField(null=True)

class Product(BaseModel):
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

class Inventory(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref='inventory', unique=True)
    quantity = IntegerField(default=0)
    last_updated = DateTimeField(default=datetime.datetime.now)

class StockMovement(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref='movements')
    change = IntegerField()            # positivo = entrada, negativo = salida
    reason = CharField(null=True)      # 'purchase', 'sale', 'adjustment', etc.
    timestamp = DateTimeField(default=datetime.datetime.now)
    reference = CharField(null=True)   # Ej: ID de venta o nota

class Sale(BaseModel):
    id = AutoField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    total = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

class SaleItem(BaseModel):
    id = AutoField()
    sale = ForeignKeyField(Sale, backref='items')
    product = ForeignKeyField(Product, backref='sale_items')
    quantity = IntegerField()
    unit_price = DecimalField(max_digits=10, decimal_places=2)
    subtotal = DecimalField(max_digits=12, decimal_places=2)

# -------------------
# FUNCIONES AUXILIARES
# -------------------

def init_db():
    """Inicializa la base de datos y crea las tablas."""
    db.connect()
    db.create_tables([Category, Product, Inventory, StockMovement, Sale, SaleItem])
    db.close()