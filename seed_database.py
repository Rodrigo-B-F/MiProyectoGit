"""
Script para poblar la base de datos con productos de ejemplo
Crea 50 productos con códigos de barras entre 1 y 9999
"""

import sys
import os
import random

# Configuración de ruta
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models import init_db
from controllers import add_product

# Listas de productos por categoría con nombres únicos
PRODUCTOS = {
    'Lacteos': [
        ('Leche Entera', '1L'), ('Leche Descremada', '1L'), ('Yogurt Natural', '200g'), ('Yogurt Frutilla', '200g'),
        ('Queso Fresco', '500g'), ('Queso Maduro', '300g'), ('Mantequilla', '250g'), ('Crema de Leche', '200ml')
    ],
    'Panaderia': [
        ('Pan Blanco', 'Grande'), ('Pan Integral', 'Grande'), ('Pan de Molde', '500g'), ('Croissant', 'Unidad'),
        ('Galletas Dulces', 'Paquete'), ('Galletas Saladas', 'Paquete'), ('Tostadas', 'Caja'), ('Pan Frances', 'Unidad')
    ],
    'Bebidas': [
        ('Agua Mineral', '500ml'), ('Coca Cola', '2L'), ('Sprite', '2L'), ('Fanta', '2L'),
        ('Jugo Naranja', '1L'), ('Jugo Manzana', '1L'), ('Te Frio', '500ml'), ('Cafe Instantaneo', '100g')
    ],
    'Snacks': [
        ('Papas Fritas', 'Grande'), ('Doritos', 'Nacho'), ('Cheetos', 'Queso'), ('Palomitas', 'Mantequilla'),
        ('Chocolate Milka', 'Leche'), ('Chocolate Nestle', 'Clasico'), ('Caramelos', 'Surtidos'), ('Chicles', 'Menta')
    ],
    'Limpieza': [
        ('Detergente', 'Liquido 1L'), ('Jabon Liquido', '500ml'), ('Cloro', '1L'), ('Desinfectante', 'Spray'),
        ('Papel Higienico', '4 Rollos'), ('Servilletas', 'Paquete'), ('Esponja', 'Doble Cara'), ('Lavavajillas', '500ml')
    ],
    'Higiene': [
        ('Shampoo', 'Anticaspa'), ('Acondicionador', 'Suave'), ('Jabon de Baño', 'Glicerina'), ('Pasta Dental', 'Triple Accion'),
        ('Cepillo Dental', 'Suave'), ('Desodorante', 'Roll-on'), ('Crema Corporal', 'Hidratante'), ('Toallas Humedas', 'Pack')
    ],
    'Enlatados': [
        ('Atun en Lata', 'Aceite'), ('Sardinas', 'Tomate'), ('Duraznos', 'Almibar'), ('Arvejas', 'Lata'),
        ('Choclo', 'Grano'), ('Frijoles', 'Negros'), ('Salsa de Tomate', '200g'), ('Aceitunas', 'Verdes')
    ]
}

# Ubicaciones posibles
UBICACIONES = ['Pasillo A', 'Pasillo B', 'Pasillo C', 'Pasillo D', 'Refrigerador', 'Estante 1', 'Estante 2']

def seed_database():
    """Poblar la base de datos con productos de ejemplo"""
    
    print("Inicializando base de datos...")
    init_db()
    
    print("\nAgregando productos...")
    
    # Generar códigos de barras únicos
    barcodes = random.sample(range(1, 10000), 50)
    
    producto_index = 0
    productos_agregados = 0
    
    for categoria, productos in PRODUCTOS.items():
        for producto_tuple in productos:
            if producto_index >= 50:
                break
            
            # Combinar nombre base con variante para nombre único
            nombre_base, variante = producto_tuple
            producto = f"{nombre_base} {variante}"
            
            barcode = str(barcodes[producto_index])
            location = random.choice(UBICACIONES)
            price = round(random.uniform(5, 100), 2)
            quantity = random.randint(0, 100)
            
            success, message = add_product(
                name=producto,
                barcode=barcode,
                category_name=categoria,
                location=location,
                sale_price=price,
                initial_quantity=quantity
            )
            
            if success:
                productos_agregados += 1
                print(f"+ {productos_agregados}/50: {producto} (Codigo: {barcode})")
            else:
                print(f"- Error: {message}")
            
            producto_index += 1
        
        if producto_index >= 50:
            break
    
    print(f"\n¡Completado! Se agregaron {productos_agregados} productos a la base de datos.")
    print("\nResumen por categoria:")
    for categoria in PRODUCTOS.keys():
        print(f"  - {categoria}")

if __name__ == "__main__":
    seed_database()
