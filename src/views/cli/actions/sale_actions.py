from controllers import (
    record_sale,
    list_sales_history,
    sales_summary_by_date
)
from utils.translations import INPUT_PROMPTS, MESSAGES, MENU_OPTIONS
from utils.cli_utils import print_dataframe, print_success, print_error

def handle_record_sale():
    """Pide los datos de los productos a vender y registra la venta."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][2][3:]} ---")
    items_to_sell = []
    
    while True:
        barcode = input(INPUT_PROMPTS['barcode_search']).upper()
        if barcode == 'FIN':
            break
            
        try:
            quantity = int(input(INPUT_PROMPTS['quantity_sell'].format(barcode=barcode)))
            if quantity > 0:
                items_to_sell.append({'barcode': barcode, 'quantity': quantity})
            else:
                print(MESSAGES['quantity_positive'])
        except ValueError:
            print("Cantidad inválida. Intente de nuevo.")
            
    if not items_to_sell:
        print(MESSAGES['sale_cancelled'])
        return

    # Llama al servicio para registrar la venta
    success, message = record_sale(items_to_sell)
    
    if success:
        print_success(message)
    else:
        print_error(message)

def handle_list_sales_history():
    """Lista el historial de ventas."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][12][4:]} ---")
    data = list_sales_history()
    
    if data:
        print_dataframe(data, columns=['sale_id', 'timestamp', 'product', 'barcode', 'quantity', 'unit_price', 'subtotal'])
    else:
        print(MESSAGES['no_sales'])

def handle_sales_summary_by_date():
    """Muestra el resumen de ventas agrupadas por fecha."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][13][4:]} ---")
    data = sales_summary_by_date()

    if data:
        print_dataframe(data, columns=['date', 'total_sales', 'total_amount'])
    else:
        print("No hay ventas registradas para resumir.")
