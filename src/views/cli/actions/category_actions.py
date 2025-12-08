from controllers import (
    list_categories,
    list_products_by_category,
    update_category
)
from utils.translations import INPUT_PROMPTS, MESSAGES, MENU_OPTIONS
from utils.cli_utils import print_dataframe, print_success, print_error
import pandas as pd

def handle_list_categories_and_products():
    """Maneja la lógica para listar categorías y luego productos de una categoría seleccionada (usando ID)."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][5][3:]} ---")
    
    # 1. Listar categorías para que el usuario pueda elegir
    categories = list_categories()
    if not categories:
        print(MESSAGES['no_categories'])
        return

    print("\nCategorías disponibles:")
    # Mapeamos el número de opción al ID de la categoría para facilitar la selección
    category_map = {}
    for i, cat in enumerate(categories):
        print(f"[{i+1}]. {cat['name']}") 
        category_map[str(i+1)] = cat['id']
    
    # 2. Pedir al usuario que seleccione una categoría
    while True:
        choice = input(INPUT_PROMPTS['category_select']).lower()
        if choice == 'r':
            return
            
        if choice in category_map:
            category_id = category_map[choice]
            # Obtenemos el nombre para el feedback de la lista original
            category_name = categories[int(choice)-1]['name'] 
            break
        else:
            print(MESSAGES['invalid_option'])
            
    # 3. Llamar al servicio y formatear
    print(f"\nBuscando productos en la categoría: {category_name}...")
    try:
        # Usamos la función de servicio que ahora espera el ID
        products_data = list_products_by_category(category_id) 
        
        if products_data:
            print(f"\n--- Productos en la Categoría: {category_name} ({len(products_data)} encontrados) ---")
            print_dataframe(products_data)
        else:
            print(f"No se encontraron productos para la categoría '{category_name}'.")

    except Exception as e:
        print(MESSAGES['unexpected_error'].format(error=e))

def handle_update_category():
    """Permite modificar el nombre y/o descripción de una categoría existente."""
    print(f"\n--- {MENU_OPTIONS['main_menu'][13][4:]} ---")
    
    # 1. Listar categorías disponibles
    categories = list_categories()
    if not categories:
        print(MESSAGES['no_categories'])
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
            print(MESSAGES['invalid_option'])
    
    # 3. Mostrar información actual
    print(f"\nCategoría seleccionada: {category_name}")
    print(f"Descripción actual: {current_desc if current_desc else '(Sin descripción)'}")
    
    # 4. Pedir nuevos datos
    print("\nDeje vacío si no desea modificar el campo.")
    new_name = input(f"Nuevo Nombre (Actual: {category_name}): ").strip()
    new_description = input(f"Nueva Descripción (Actual: {current_desc if current_desc else 'Ninguna'}): ").strip()
    
    if not new_name and not new_description:
        print("Operación cancelada. No se realizaron cambios.")
        return
    
    # 5. Actualizar la categoría
    # Si el usuario no ingresó un nuevo nombre, usar el actual
    final_name = new_name if new_name else category_name
    # Si el usuario no ingresó descripción, usar la actual (puede ser None)
    final_description = new_description if new_description else current_desc
    
    success, message = update_category(category_id, name=final_name, description=final_description)
    
    if success:
        print_success(message)
    else:
        print_error(message)
