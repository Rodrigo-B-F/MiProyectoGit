from controllers import (
    add_stock,
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products
)
from utils.translations import INPUT_PROMPTS, MESSAGES, MENU_OPTIONS
from utils.cli_utils import print_dataframe, print_success, print_error

def handle_record_purchase():
    """Pide los datos y llama a la función para registrar una entrada de stock."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][1][3:]} ---")
    try:
        barcode = input(INPUT_PROMPTS['barcode'])
        quantity = int(input(INPUT_PROMPTS['quantity_purchase']))
        
        success, message = add_stock(barcode, quantity)
        
        if success:
            print_success(message)
        else:
            print_error(message)
        
    except ValueError:
        print(MESSAGES['invalid_number'])

def handle_list_inventory(option):
    if option == 1:
        print(f"\n--- {MENU_OPTIONS['main_menu'][3][3:]} ---")
    elif option == 2:
        print(f"\n--- {MENU_OPTIONS['main_menu'][4][3:]} ---")
    
    data = list_products_inventory(option)
    
    if data:
        print_dataframe(data, columns=['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'location', 'active'])
    else:
        print("El inventario está vacío.")

def handle_list_available_products():
    """Lista solo los productos con stock > 0."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][6][3:]} ---")
    data = list_available_products()

    if data:
        print_dataframe(data, columns=['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'location', 'active'])
    else:
        print("No hay productos con stock disponible.")

def handle_list_out_of_stock_products():
    """Lista solo los productos sin stock (quantity = 0)."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][7][3:]} ---")
    data = list_out_of_stock_products()

    if data:
        print_dataframe(data, columns=['name', 'barcode', 'category_name', 'quantity', 'sale_price', 'location', 'active'])
    else:
        print(MESSAGES['no_stock'])
