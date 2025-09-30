# Importación de la base de datos
from init_db import init_db 

# Importación de la lógica de negocio
from backend.models import init_db, db
from backend.services import (
    add_product,
    record_purchase,
    record_sale,
    list_products_inventory,
    find_product_by_name_or_barcode,
    filter_products_by_category,
    list_expiring_products,
    list_sales_history,
    sales_summary_by_date,
    list_available_products,
    list_out_of_stock_products,
    list_categories,
    list_products_by_category
)
import datetime
import pandas as pd

# Inicializamos la BD
init_db()

def show_menu():
    """Muestra el menú y pide una opción."""
    print("\n--- Menú de Gestión de Tienda ---")
    print("1. Agregar Nuevo Producto y Stock Inicial")
    print("2. Registrar Entrada de Stock (Compra)")
    print("3. Registrar Venta")
    print("4. Listar Inventario Completo")
    print("5. Listar Productos por Categoría")
    print("6. Listar Productos con Stock Disponible")
    print("7. Listar Productos sin Stock Disponible")
    print("8. Buscar Producto por Nombre/Código")
    print("9. Filtrar Productos Próximos a Vencer")
    print("10. Listar Historial de Ventas")
    print("11. Resumen de Ventas por Fecha")
    print("12. Salir")
    return input("Selecciona una opción: ")

def handle_add_product():
    """Pide los datos y llama a la función para agregar un producto."""
    print("\n--- Agregar Nuevo Producto ---")
    
    try:
        name = input("Nombre del Producto: ")
        barcode = input("Código de Barras (Único): ")
        category_name = input("Nombre de Categoría: ")
        unit = input("Unidad de Medida (Ej: unidad, kg): ")
        location = input("Ubicación (Ej: Pasillo A): ")
        purchase_price = float(input("Precio de Compra: "))
        sale_price = float(input("Precio de Venta: "))
        initial_quantity = int(input("Cantidad Inicial en Stock: "))
        
        # Pedir fecha de vencimiento
        exp_date_str = input("Fecha de Vencimiento (YYYY-MM-DD o dejar vacío): ")
        expiration_date = datetime.datetime.strptime(exp_date_str, '%Y-%m-%d').date() if exp_date_str else None

        success, message = add_product(
            name, barcode, category_name, unit, location, 
            purchase_price, sale_price, initial_quantity, expiration_date
        )

        print(f"\nResultado: {'Éxito' if success else 'Error'} - {message}")
        
    except ValueError:
        print("\nError: Los precios y cantidades deben ser números válidos.")
    except Exception as e:
        print(f"\nError inesperado: {e}")

def handle_record_purchase():
    """Pide los datos y llama a la función para registrar una compra (entrada de stock)."""
    print("\n--- Registrar Entrada de Stock (Compra) ---")
    try:
        barcode = input("Código de Barras del Producto Existente: ")
        quantity = int(input("Cantidad de unidades compradas: "))
        price = float(input("Nuevo Precio de Compra (se actualizará en el sistema): "))
        
        success, message = record_purchase(barcode, quantity, price)
        
        print(f"\nResultado: {'Éxito' if success else 'Error'} - {message}")
        
    except ValueError:
        print("\nError: La cantidad y el precio deben ser números válidos.")

def handle_record_sale():
    """Pide los datos de los productos a vender y registra la venta."""
    print("\n--- Registrar Venta ---")
    items_to_sell = []
    
    while True:
        barcode = input("Código de Barras del producto (o 'FIN' para terminar): ").upper()
        if barcode == 'FIN':
            break
            
        try:
            quantity = int(input(f"Cantidad a vender de {barcode}: "))
            if quantity > 0:
                items_to_sell.append({'barcode': barcode, 'quantity': quantity})
            else:
                print("La cantidad debe ser mayor que cero.")
        except ValueError:
            print("Cantidad inválida. Intente de nuevo.")
            
    if not items_to_sell:
        print("Venta cancelada. No se agregaron productos.")
        return

    # Llama al servicio para registrar la venta
    success, message = record_sale(items_to_sell)
    
    print(f"\nResultado de la Venta: {'Éxito' if success else 'Error'} - {message}")

def handle_list_inventory():
    """Lista todo el inventario de productos."""
    print("\n--- Listado de Inventario Completo ---")
    data = list_products_inventory()
    
    if data:
        # Usa pandas para una tabla legible en consola
        df = pd.DataFrame(data)
        # Selecciona solo las columnas más relevantes para la consola
        print(df[['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'expiration_date']].to_markdown(index=False))
    else:
        print("El inventario está vacío.")

def handle_search_product():
    """Busca productos por nombre o código de barras."""
    print("\n--- Búsqueda de Productos ---")
    query = input("Ingresa Nombre o Código de Barras a buscar: ")
    data = find_product_by_name_or_barcode(query)
    
    if data:
        print(f"\nSe encontraron {len(data)} resultados:")
        df = pd.DataFrame(data)
        print(df[['name', 'barcode', 'category_name', 'quantity', 'sale_price']].to_markdown(index=False))
    else:
        print("No se encontraron productos que coincidan con la búsqueda.")

def handle_expiring_products():
    """Filtra productos próximos a vencer."""
    print("\n--- Productos Próximos a Vencer ---")
    try:
        days = int(input("Buscar productos que venzan en los próximos [días]: "))
    except ValueError:
        print("\nError: Debes ingresar un número válido de días. Usando 30 por defecto.")
        days = 30
        
    data = list_expiring_products(days)
    
    if data:
        print(f"\n{len(data)} productos vencen en los próximos {days} días:")
        df = pd.DataFrame(data)
        print(df[['name', 'expiration_date', 'quantity', 'location']].to_markdown(index=False))
    else:
        print(f"No hay productos que venzan en los próximos {days} días.")

def handle_list_sales_history():
    """Lista el historial de ventas."""
    print("\n--- Historial de Ventas ---")
    data = list_sales_history()
    
    if data:
        df = pd.DataFrame(data)
        print(df[['sale_id', 'timestamp', 'product', 'barcode', 'quantity', 'unit_price', 'subtotal', 'total_sale']].to_markdown(index=False))
    else:
        print("No hay ventas registradas.")

def handle_list_available_products():
    """Lista solo los productos con stock > 0."""
    print("\n--- Productos con Stock Disponible ---")
    data = list_available_products()

    if data:
        df = pd.DataFrame(data)
        print(df[['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'expiration_date']].to_markdown(index=False))
    else:
        print("No hay productos con stock disponible.")

def handle_list_out_of_stock_products():
    """Lista solo los productos sin stock (quantity = 0)."""
    print("\n--- Productos sin Stock Disponible ---")
    data = list_out_of_stock_products()

    if data:
        df = pd.DataFrame(data)
        print(df[['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'expiration_date']].to_markdown(index=False))
    else:
        print("No hay productos sin stock.")

def handle_sales_summary_by_date():
    """Muestra el resumen de ventas agrupadas por fecha."""
    print("\n--- Resumen de Ventas por Fecha ---")
    data = sales_summary_by_date()

    if data:
        df = pd.DataFrame(data)
        print(df[['date', 'total_sales', 'total_amount']].to_markdown(index=False))
    else:
        print("No hay ventas registradas para resumir.")

def handle_list_categories_and_products():
    """Muestra las categorías y permite listar productos por categoría."""
    print("\n--- Categorías Disponibles ---")
    cats = list_categories()
    if not cats:
        print("No hay categorías registradas.")
        return

    # Mostrar listado numerado
    for i, c in enumerate(cats, start=1):
        desc = f" - {c['description']}" if c['description'] else ""
        print(f"{i}. {c['name']}{desc}")

    # Pedir selección
    sel = input("\nIngresa el número de categoría o escribe el nombre (ENTER para cancelar): ").strip()
    if sel == "":
        print("Operación cancelada.")
        return

    # Determinar nombre de categoría
    if sel.isdigit():
        idx = int(sel) - 1
        if idx < 0 or idx >= len(cats):
            print("Selección inválida.")
            return
        category_name = cats[idx]['name']
    else:
        category_name = sel

    # Obtener productos de la categoría
    data = list_products_by_category(category_name)
    if data:
        df = pd.DataFrame(data)
        # Muestra columnas útiles
        print(df[['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'profit', 'expiration_date', 'location']].to_markdown(index=False))
    else:
        print(f"No se encontraron productos para la categoría '{category_name}'.")


def main():
    """Función principal del CLI."""
    while True:
        choice = show_menu()
        
        if choice == '1':
            handle_add_product()
        elif choice == '2':
            handle_record_purchase()
        elif choice == '3':
            handle_record_sale()
        elif choice == '4':
            handle_list_inventory()
        elif choice == '5':
            handle_list_categories_and_products()
        elif choice == '6':
            handle_list_available_products()
        elif choice == '7':
            handle_list_out_of_stock_products()
        elif choice == '8':
            handle_search_product()
        elif choice == '9':
            handle_expiring_products()
        elif choice == '10':
            handle_list_sales_history()
        elif choice == '11':
            handle_sales_summary_by_date()
        elif choice == '12':
            print("Saliendo del programa. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    main()