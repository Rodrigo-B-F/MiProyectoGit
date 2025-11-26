# src/views/cli.py

import sys
import os

# --- Configuración de ruta para importaciones ---
# Permite ejecutar este script directamente desde src/views/ sin errores de importación.
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

import datetime
import pandas as pd

# --- Importaciones de Controladores y Modelos ---
from models import init_db
from controllers.product_controller import (
    add_product,
    toggle_product_status,
    update_product_details,
    find_product_by_name_or_barcode,
    apply_expiring_product_offer
)
from controllers.inventory_controller import (
    record_purchase,
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    list_expiring_products,
    list_categories,
    list_products_by_category,
    update_category,
)
from controllers.sale_controller import (
    record_sale,
    list_sales_history,
    sales_summary_by_date
)

# Inicialización de la Base de Datos
print("Inicializando base de datos...")
init_db()
print("Base de datos lista.")


def show_menu():
    """Muestra el menú y pide una opción."""
    print("\n--- Menú de Gestión de Tienda ---")
    print("1. Agregar Nuevo Producto y Stock Inicial")
    print("2. Registrar Entrada de Stock (Compra)")
    print("3. Registrar Venta")
    print("4. Listar Inventario de Productos activos")
    print("5. Listar Inventario de Productos inactivos")
    print("6. Listar Productos por Categoría")
    print("7. Listar Productos con Stock Disponible")
    print("8. Listar Productos sin Stock Disponible")
    print("9. Buscar Producto por Nombre/Código")
    print("10. Modificar Detalles del Producto")
    print("11. Filtrar Productos Próximos a Vencer (10 días por defecto)")
    print("12. Activar/Desactivar Producto")
    print("13. Listar Historial de Ventas")
    print("14. Resumen de Ventas por Fecha")
    print("15. **APLICAR OFERTA** (Vencimiento < 10 días)")
    print("16. Modificar Categoría")
    print("17. Salir")
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


def handle_search_product():
    """Busca productos por nombre o código de barras."""
    print("\n--- Búsqueda de Productos ---")
    query = input("Ingresa Nombre o Código de Barras a buscar: ")
    data = find_product_by_name_or_barcode(query)
    
    if data:
        print(f"\nSe encontraron {len(data)} resultados:")
        df = pd.DataFrame(data)
        print(df[['name', 'barcode', 'category_name', 'quantity', 'unit', 'purchase_price', 'sale_price', 'profit', 'date_added', 'expiration_date', 'location', 'active']].to_markdown(index=False))
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
        print(df[['name', 'barcode', 'category_name', 'quantity', 'unit', 'purchase_price', 'sale_price', 'profit', 'date_added', 'expiration_date', 'location', 'active']].to_markdown(index=False))
    else:
        print(f"No hay productos que venzan en los próximos {days} días.")


def handle_list_sales_history():
    """Lista el historial de ventas."""
    print("\n--- Historial de Ventas ---")
    data = list_sales_history()
    
    if data:
        df = pd.DataFrame(data)
        print(df[['sale_id', 'timestamp', 'product', 'barcode', 'quantity', 'unit_price', 'subtotal']].to_markdown(index=False))
    else:
        print("No hay ventas registradas.")


def handle_list_available_products():
    """Lista solo los productos con stock > 0."""
    print("\n--- Productos con Stock Disponible ---")
    data = list_available_products()

    if data:
        df = pd.DataFrame(data)
        print(df[['name', 'barcode', 'category_name', 'quantity', 'unit', 'purchase_price', 'sale_price', 'profit', 'date_added', 'expiration_date', 'location', 'active']].to_markdown(index=False))
    else:
        print("No hay productos con stock disponible.")


def handle_list_out_of_stock_products():
    """Lista solo los productos sin stock (quantity = 0)."""
    print("\n--- Productos sin Stock Disponible ---")
    data = list_out_of_stock_products()

    if data:
        df = pd.DataFrame(data)
        print(df[['name', 'barcode', 'category_name', 'quantity', 'unit', 'purchase_price', 'sale_price', 'profit', 'date_added', 'expiration_date', 'location', 'active']].to_markdown(index=False))
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
    """Maneja la lógica para listar categorías y luego productos de una categoría seleccionada (usando ID)."""
    print("\n--- Listado de Productos por Categoría ---")
    
    # 1. Listar categorías para que el usuario pueda elegir
    categories = list_categories()
    if not categories:
        print("No se encontraron categorías. Agregue productos para crear categorías.")
        return

    print("\nCategorías disponibles:")
    # Mapeamos el número de opción al ID de la categoría para facilitar la selección
    category_map = {}
    for i, cat in enumerate(categories):
        print(f"[{i+1}]. {cat['name']}") 
        category_map[str(i+1)] = cat['id']
    
    # 2. Pedir al usuario que seleccione una categoría
    while True:
        choice = input("Ingrese el número de la categoría que desea ver o 'r' para regresar: ").lower()
        if choice == 'r':
            return
            
        if choice in category_map:
            category_id = category_map[choice]
            # Obtenemos el nombre para el feedback de la lista original
            category_name = categories[int(choice)-1]['name'] 
            break
        else:
            print("Opción no válida. Intente de nuevo.")
            
    # 3. Llamar al servicio y formatear
    print(f"\nBuscando productos en la categoría: {category_name}...")
    try:
        # Usamos la función de servicio que ahora espera el ID
        products_data = list_products_by_category(category_id) 
        
        if products_data:
            print(f"\n--- Productos en la Categoría: {category_name} ({len(products_data)} encontrados) ---")
            
            # Usar pandas para formato de tabla
            df = pd.DataFrame(products_data)
            # Rellenar valores nulos (como None en expiration_date) con una cadena vacía
            df = df.fillna('') 
            # Imprimir como tabla sin el índice de pandas
            print(df.to_string(index=False))
        else:
            print(f"No se encontraron productos para la categoría '{category_name}'.")

    except Exception as e:
        print(f"\nERROR: Ocurrió un error al listar los productos: {e}")


def handle_toggle_status():
    """Pide el código de barras y el nuevo estado del producto."""
    print("\n--- Activar/Desactivar Producto ---")
    try:
        barcode = input("Código de Barras del Producto a modificar: ")
        
        # Permite ingresar A/D o presionar Enter para invertir el estado actual
        status_input = input("Estado (A = Activar, D = Desactivar, o Enter para invertir): ").upper()
        
        new_status = None
        if status_input == 'A':
            new_status = True
        elif status_input == 'D':
            new_status = False

        success, message = toggle_product_status(barcode, new_status)
        
        print(f"\nResultado: {'Éxito' if success else 'Error'} - {message}")
        
    except Exception as e:
        print(f"\nError inesperado: {e}")


def show_update_menu():
    """Muestra el menú de opciones para actualizar un solo campo."""
    print("\n--- Campo a Actualizar ---")
    print("1. Nombre")
    print("2. Código de Barras")
    print("3. Nombre de Categoría")
    print("4. Unidad de Medida")
    print("5. Precio de Compra")
    print("6. Precio de Venta")
    print("7. Fecha de Expiración (YYYY-MM-DD, o 'vacío' para eliminar)")
    print("8. Ubicación")
    print("9. Ver Detalles y Salir")
    return input("Selecciona una opción: ")


def handle_update_product():
    """Permite al usuario actualizar un solo campo de un producto a la vez mediante menú."""
    print("\n--- Modificar Detalles de Producto ---")
    
    # El usuario debe especificar qué producto quiere modificar
    old_barcode = input("Ingresa el Código de Barras del producto a modificar: ")
    
    # Bucle para permitir múltiples modificaciones al mismo producto
    while True:
        choice = show_update_menu()
        new_value = None
        
        if choice == '9':
            # Opción 9: Ver detalles y salir
            print("\n--- Información Actual del Producto ---")
            data = find_product_by_name_or_barcode(old_barcode)
            
            if data:
                # Usar la primera coincidencia (debería ser única por barcode)
                df = pd.DataFrame(data)
                print(df[['name', 'barcode', 'category_name', 'quantity', 'unit', 
                          'purchase_price', 'sale_price', 'profit', 'date_added', 
                          'expiration_date', 'location', 'active']].to_markdown(index=False))
            else:
                print(f"Producto con código {old_barcode} no encontrado.")
            break # Salir del bucle
            
        elif choice == '1': # Nombre
            new_value = input("Ingresa el NUEVO Nombre: ")
            success, message = update_product_details(old_barcode, name=new_value)
            
        elif choice == '2': # Código de Barras
            new_barcode = input("Ingresa el NUEVO Código de Barras: ")
            success, message = update_product_details(old_barcode, new_barcode=new_barcode)
            if success:
                # Si el código de barras se actualizó, usamos el nuevo para futuras búsquedas
                old_barcode = new_barcode
            
        elif choice == '3': # Nombre de Categoría
            new_value = input("Ingresa el NUEVO Nombre de Categoría: ")
            success, message = update_product_details(old_barcode, category_name=new_value)
            
        elif choice == '4': # Unidad de Medida
            new_value = input("Ingresa la NUEVA Unidad de Medida: ")
            success, message = update_product_details(old_barcode, unit=new_value)
            
        elif choice == '5': # Precio de Compra
            try:
                price_str = input("Ingresa el NUEVO Precio de Compra: ")
                price = float(price_str) if price_str.strip() else None
                success, message = update_product_details(old_barcode, purchase_price=price)
            except ValueError:
                success, message = False, "Error: El precio de compra debe ser un número."
                
        elif choice == '6': # Precio de Venta
            try:
                price_str = input("Ingresa el NUEVO Precio de Venta: ")
                price = float(price_str) if price_str.strip() else None
                success, message = update_product_details(old_barcode, sale_price=price)
            except ValueError:
                success, message = False, "Error: El precio de venta debe ser un número."
                
        elif choice == '7': # Fecha de Expiración
            new_date = input("Ingresa la NUEVA Fecha de Vencimiento (YYYY-MM-DD, o vacío para eliminar): ")
            success, message = update_product_details(old_barcode, expiration_date_str=new_date)
            
        elif choice == '8': # Ubicación
            new_value = input("Ingresa la NUEVA Ubicación: ")
            success, message = update_product_details(old_barcode, location=new_value)
            
        else:
            print("Opción no válida. Inténtalo de nuevo.")
            continue

        # Muestra el resultado de la operación (excepto en la opción 9)
        if choice != '9':
            print(f"\nResultado de la Actualización: {'Éxito' if success else 'Error'} - {message}")


def handle_apply_offer():
    """Ejecuta el proceso de aplicar ofertas automáticas."""
    print("\n--- Aplicar Oferta por Vencimiento (< 10 días) ---")
    
    # Opción para permitir al usuario cambiar el límite de días (opcional)
    try:
        days_str = input("Límite de días para la oferta (Dejar vacío para usar 10 días por defecto): ")
        days = int(days_str) if days_str.strip() else 10
    except ValueError:
        print("\nError: Ingresa un número válido de días. Usando 10 por defecto.")
        days = 10
    
    success, message = apply_expiring_product_offer(days)
    print(message)

    # Mostrar los productos que acaban de entrar en oferta (opcional)
    if success:
        print("\n--- Productos en Oferta (Precio Venta = Precio Compra) ---")
        handle_expiring_products() # Reutilizamos la función de listado


def handle_update_category():
    """Permite modificar el nombre y/o descripción de una categoría existente."""
    print("\n--- Modificar Categoría ---")
    
    # 1. Listar categorías disponibles
    categories = list_categories()
    if not categories:
        print("No se encontraron categorías. Agregue productos para crear categorías.")
        return
    
    print("\nCategorías disponibles:")
    category_map = {}
    for i, cat in enumerate(categories):
        desc_preview = cat['description'][:50] if cat['description'] else "(Sin descripción)"
        print(f"[{i+1}]. {cat['name']} - {desc_preview}")
        category_map[str(i+1)] = cat['id']
    
    # 2. Pedir al usuario que seleccione una categoría
    while True:
        choice = input("\nIngrese el número de la categoría o 'r' para regresar: ").lower()
        if choice == 'r':
            return
            
        if choice in category_map:
            category_id = category_map[choice]
            category_name = categories[int(choice)-1]['name']
            current_desc = categories[int(choice)-1]['description']
            break
        else:
            print("Opción no válida. Intente de nuevo.")
    
    # 3. Mostrar información actual
    print(f"\nCategoría seleccionada: {category_name}")
    print(f"Descripción actual: {current_desc if current_desc else '(Sin descripción)'}")
    
    # 4. Pedir nuevos datos
    print("\nDeje vacío si no desea modificar el campo.")
    new_name = input(f"Nuevo Nombre (Actual: {category_name}): ")
    new_description = input(f"Nueva Descripción (Actual: {current_desc if current_desc else 'Ninguna'}): ")
    
    if not new_name.strip() and not new_description.strip():
        print("Operación cancelada. No se realizaron cambios.")
        return
    
    # 5. Actualizar la categoría
    success, message = update_category(category_id, name=new_name, description=new_description)
    print(f"\nResultado: {'Éxito' if success else 'Error'} - {message}")


def handle_list_inventory(option):
    if option == 1:
        print("\n--- Listado de Inventario de productos activos ---")
    elif option == 2:
        print("\n--- Listado de Inventario de productos inactivos ---")
    
    data = list_products_inventory(option)
    
    if data:
        # Usa pandas para una tabla legible en consola
        df = pd.DataFrame(data)
        # Selecciona solo las columnas más relevantes para la consola
        print(df[['name', 'barcode', 'category_name', 'quantity', 'unit', 'purchase_price', 'sale_price', 'profit', 'date_added', 'expiration_date', 'location', 'active']].to_markdown(index=False))
    else:
        print("El inventario está vacío.")


def main():
    """Argumentos para la función handle_list_inventory():
       1: Productos activos
       2: Productos inactivos"""
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            handle_add_product()
        elif choice == '2':
            handle_list_inventory(1)
            handle_record_purchase()
        elif choice == '3':
            handle_list_inventory(1)
            handle_record_sale()
        elif choice == '4':
            handle_list_inventory(1)
        elif choice == '5':
            handle_list_inventory(2)
        elif choice == '6':
            handle_list_categories_and_products()
        elif choice == '7':
            handle_list_available_products()
        elif choice == '8':
            handle_list_out_of_stock_products()
        elif choice == '9':
            handle_search_product()
        elif choice == '10':
            handle_list_inventory(1)
            handle_update_product()
        elif choice == '11':
            handle_expiring_products()
        elif choice == '12':
            handle_list_inventory(1)
            handle_list_inventory(2)
            handle_toggle_status()
        elif choice == '13':
            handle_list_sales_history()
        elif choice == '14':
            handle_sales_summary_by_date()
        elif choice == '15':
            handle_apply_offer()
        elif choice == '16':
            handle_update_category()
        elif choice == '17':
            print("Saliendo del programa. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    main()