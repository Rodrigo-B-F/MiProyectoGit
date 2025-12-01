from utils.translations import MENU_OPTIONS, INPUT_PROMPTS

def show_menu():
    """Muestra el menú y pide una opción."""
    print(f"\n{MENU_OPTIONS['main_title']}")
    for option in MENU_OPTIONS['main_menu']:
        print(option)
    return input(INPUT_PROMPTS['select_option'])
