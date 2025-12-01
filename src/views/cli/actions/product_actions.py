import datetime
from controllers import (
    add_product,
    toggle_product_status,
    update_product_details,
    find_product_by_name_or_barcode,
    apply_expiring_product_offer
)
from utils.translations import INPUT_PROMPTS, MESSAGES, PRODUCT_FIELDS, MENU_OPTIONS
from utils.cli_utils import print_dataframe, print_success, print_error

def handle_add_product():
    """Pide los datos y llama a la función para agregar un producto."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][0][3:]} ---") # Remove "1. "
    
    try:
        name = input(INPUT_PROMPTS['name'])
        barcode = input(INPUT_PROMPTS['barcode'])
        category_name = input(INPUT_PROMPTS['category_name'])
        unit = input(INPUT_PROMPTS['unit'])
        location = input(INPUT_PROMPTS['location'])
        purchase_price = float(input(INPUT_PROMPTS['purchase_price']))
        sale_price = float(input(INPUT_PROMPTS['sale_price']))
        initial_quantity = int(input(INPUT_PROMPTS['initial_quantity']))
        
        # Pedir fecha de vencimiento
        exp_date_str = input(INPUT_PROMPTS['expiration_date'])
        expiration_date = datetime.datetime.strptime(exp_date_str, '%Y-%m-%d').date() if exp_date_str else None

        success, message = add_product(
            name, barcode, category_name, unit, location, 
            purchase_price, sale_price, initial_quantity, expiration_date
        )

        if success:
            print_success(message)
        else:
            print_error(message)
        
    except ValueError:
        print(MESSAGES['invalid_number'])
    except Exception as e:
        print(MESSAGES['unexpected_error'].format(error=e))

def handle_search_product():
    """Busca productos por nombre o código de barras."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][8][3:]} ---")
    query = input(INPUT_PROMPTS['search_query'])
    data = find_product_by_name_or_barcode(query)
    
    if data:
        print(f"\nSe encontraron {len(data)} resultados:")
        print_dataframe(data, columns=['name', 'barcode', 'category_name', 'quantity', 'unit', 'purchase_price', 'sale_price', 'profit', 'date_added', 'expiration_date', 'location', 'active'])
    else:
        print(MESSAGES['no_results'])

def handle_toggle_status():
    """Pide el código de barras y el nuevo estado del producto."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][11][4:]} ---")
    try:
        barcode = input(INPUT_PROMPTS['barcode_modify'])
        
        # Permite ingresar A/D o presionar Enter para invertir el estado actual
        status_input = input(INPUT_PROMPTS['status_modify']).upper()
        
        new_status = None
        if status_input == 'A':
            new_status = True
        elif status_input == 'D':
            new_status = False

        success, message = toggle_product_status(barcode, new_status)
        
        if success:
            print_success(message)
        else:
            print_error(message)
        
    except Exception as e:
        print(MESSAGES['unexpected_error'].format(error=e))

def handle_apply_offer():
    """Ejecuta el proceso de aplicar ofertas automáticas."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][14][4:]} ---")
    
    try:
        days_str = input(INPUT_PROMPTS['days_offer'])
        days = int(days_str) if days_str.strip() else 10
    except ValueError:
        print("\nError: Ingresa un número válido de días. Usando 10 por defecto.")
        days = 10
    
    success, message = apply_expiring_product_offer(days)
    print(message)

    # Mostrar los productos que acaban de entrar en oferta (opcional)
    # Note: This creates a circular dependency if we import handle_expiring_products directly.
    # We will handle this by importing inside the function or restructuring.
    # For now, let's just print the message.

def show_update_menu():
    """Muestra el menú de opciones para actualizar un solo campo."""
    print(f"\n{MENU_OPTIONS['update_menu_title']}")
    for option in MENU_OPTIONS['update_menu']:
        print(option)
    return input(INPUT_PROMPTS['select_option'])

def handle_update_product():
    """Permite al usuario actualizar un solo campo de un producto a la vez mediante menú."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][9][4:]} ---")
    
    old_barcode = input(INPUT_PROMPTS['barcode_modify'])
    
    while True:
        choice = show_update_menu()
        
        if choice == '9':
            # Ver detalles y salir
            print("\n--- Información Actual del Producto ---")
            data = find_product_by_name_or_barcode(old_barcode)
            
            if data:
                print_dataframe(data, columns=['name', 'barcode', 'category_name', 'quantity', 'unit', 
                          'purchase_price', 'sale_price', 'profit', 'date_added', 
                          'expiration_date', 'location', 'active'])
            else:
                print(f"Producto con código {old_barcode} no encontrado.")
            break
            
        elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
            field_map = {
                '1': ('name', 'Nombre'),
                '2': ('new_barcode', 'Código de Barras'),
                '3': ('category_name', 'Nombre de Categoría'),
                '4': ('unit', 'Unidad de Medida'),
                '5': ('purchase_price', 'Precio de Compra'),
                '6': ('sale_price', 'Precio de Venta'),
                '7': ('expiration_date_str', 'Fecha de Vencimiento'),
                '8': ('location', 'Ubicación')
            }
            
            field_key, field_label = field_map[choice]
            new_value = input(INPUT_PROMPTS['new_value'].format(field=field_label))
            
            kwargs = {field_key: new_value}
            
            # Conversiones específicas
            if choice in ['5', '6']:
                try:
                    kwargs[field_key] = float(new_value) if new_value.strip() else None
                except ValueError:
                    print_error(f"El {field_label} debe ser un número.")
                    continue
            
            success, message = update_product_details(old_barcode, **kwargs)
            
            if success:
                print_success(message)
                if choice == '2':
                    old_barcode = new_value # Actualizar barcode si cambió
            else:
                print_error(message)
            
        else:
            print(MESSAGES['invalid_option'])
