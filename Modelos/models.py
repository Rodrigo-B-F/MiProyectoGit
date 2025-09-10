from peewee import *
import datetime

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

def ingresar_producto():
    
    continuar =  input("Ingresar datos s/n?: ")
    continuar = continuar.lower()

    while continuar == 's':
        
        continuar = "p"

        # Crear una categoría
        nombre_categoria=input("Nombre de categoría: ")
        cat_alimentos, created = Categoria.get_or_create(nombre=nombre_categoria)
        
        # Crear un producto  
        nombre=input("Nombre del producto: ")
        codigo_barras=input("Ingrese el código del producto: ")
        imagen=None
        unidades_medida=input("Ingrese unidad de medida: ")
        ubicacion=input("¿Dónde se ubica?: ")
        fecha_ingreso=datetime.date.today()
        stock_disponible=int(input("Ingrese cantidad: "))
        fecha_vencimiento=datetime.date(2025, 12, 31)
        precio_compra=float(input("Precio de compra: "))
        precio_venta=float(input("Precio de venta: "))
        ganancia=precio_venta - precio_venta
        
        while continuar != "s" and continuar != "n":
            continuar = input("Ingresar datos s/n?: ")
            if continuar != "s" and continuar != "n":
                print("Ingrese una opción valida...")
            else:
                break

        

        producto = Producto.create(
            categoria=cat_alimentos,
            nombre,
            codigo_barras,
            imagen=None,
            unidades_medida,
            ubicacion,
            fecha_ingreso,
            stock_disponible,
            fecha_vencimiento,
            precio_compra,
            precio_venta,
            ganancia

        )
    # Crear una categoría
    
    cat_alimentos, created = Categoria.get_or_create(nombre="Alimentos")
        
    # Crear un producto
        
    producto = Producto.create(
        categoria=cat_alimentos,
        nombre="Leche Entera",
        codigo_barras="1234567890123",
        imagen=None,
        unidades_medida="Litros",
        ubicacion="Pasillo 3",
        fecha_ingreso=datetime.date.today(),
        stock_disponible=50,
        fecha_vencimiento=datetime.date(2025, 12, 31),
        precio_compra=1.2,
        precio_venta=1.5,
        ganancia=0.3
    )

# Bloque de código que solo se ejecuta cuando corres este archivo directamente
if __name__ == '__main__':
    try:
        db.connect()
        db.create_tables([Categoria, Producto, Venta])
        print("Tablas creadas exitosamente.")
        
        funcion
        
        # Registrar una venta
        venta = Venta.create(
            producto=producto,
            cantidad_vendida=5
        )
        
        print("Datos insertados correctamente.")
        
    except OperationalError as e:
        print(f"Error al crear tablas: {e}. Puede que ya existan.")
    finally:
        if not db.is_closed():
            db.close()