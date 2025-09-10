from peewee import *

db = SqliteDatabase("tienda.db")

class BaseModel(Model):
    class Meta:
        database = db # Esta clase se conectará a la base de datos 'tienda.db'

# --- MODELO DE CATEGORÍAS ---
class Categoria(BaseModel):
    nombre = CharField(unique=True)

# --- MODELO DE PRODUCTOS ---
class Producto(BaseModel):
    # Relaciona el producto con una categoría
    categoria = ForeignKeyField(Categoria, backref='productos')
    
    nombre = CharField()
    codigo_barras = CharField(unique=True)
    imagen = CharField(null=True)
    unidades_medida = CharField()
    ubicacion = CharField(null=True)
    fecha_ingreso = DateField()
    stock_disponible = IntegerField()
    fecha_vencimiento = DateField(null=True)
    precio_compra = FloatField()
    precio_venta = FloatField()
    ganancia = FloatField(default=0.0) # Se calculará después

# --- MODELO DE VENTAS ---
class Venta(BaseModel):
    # Relaciona la venta con el producto vendido
    producto = ForeignKeyField(Producto, backref='ventas')
    
    fecha_hora = DateTimeField(default=datetime.datetime.now)
    cantidad_vendida = IntegerField()

import datetime

# Bloque de código que solo se ejecuta cuando corres este archivo directamente
if __name__ == '__main__':
    try:
        db.connect()
        db.create_tables([Categoria, Producto, Venta])
        print("Tablas creadas exitosamente.")
    except OperationalError as e:
        print(f"Error al crear tablas: {e}. Puede que ya existan.")
    finally:
        if not db.is_closed():
            db.close()