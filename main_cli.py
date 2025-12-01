import sys
import os

# --- Configuración de ruta para importaciones ---
# Permite ejecutar este script desde la raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models import init_db
from views.cli.menus import show_menu
from views.cli.actions.product_actions import (
    handle_add_product,
    handle_search_product,
    handle_update_product,
    handle_toggle_status,
    handle_apply_offer
)
from views.cli.actions.inventory_actions import (
    handle_record_purchase,
    handle_list_inventory,
    handle_list_available_products,
    handle_list_out_of_stock_products,
    handle_expiring_products
)
from views.cli.actions.sale_actions import (
    handle_record_sale,
    handle_list_sales_history,
    handle_sales_summary_by_date
)
from views.cli.actions.category_actions import (
    handle_list_categories_and_products,
    handle_update_category
)
from utils.translations import MESSAGES

def main():
    """Función principal del CLI."""
    
    # Inicialización de la Base de Datos
    print(MESSAGES['init_db'])
    init_db()
    print(MESSAGES['db_ready'])
    
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
            print(MESSAGES['bye'])
            break
        else:
            print(MESSAGES['invalid_option'])

if __name__ == "__main__":
    main()
