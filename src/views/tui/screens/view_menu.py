from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button
from textual.containers import Vertical
from controllers import (
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products
)
from src.utils.translations import PRODUCT_FIELDS, TUI_MENU_OPTIONS
from . import INVENTORY_DISPLAY_KEYS
from .inventory_viewer import InventoryViewerScreen

class ViewScreen(Screen):
    """Pantalla con las opciones para visualizar reportes e inventario."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="VER")
        yield Vertical(
            Button(TUI_MENU_OPTIONS['view_search'], id="view_search"),
            Button(TUI_MENU_OPTIONS['view_active'], id="view_active", classes="menu-button"),
            Button(TUI_MENU_OPTIONS['view_inactive'], id="view_inactive"),
            Button(TUI_MENU_OPTIONS['view_available'], id="view_available"),
            Button(TUI_MENU_OPTIONS['view_out_of_stock'], id="view_out_of_stock"),
            Button(TUI_MENU_OPTIONS['view_by_category'], id="view_by_category"),
            Button(TUI_MENU_OPTIONS['exit'], id="exit_view_menu"),
            id="view-menu-container"
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_view_menu":
            self.dismiss()
        elif event.button.id == "view_search":
            self.app.push_screen("search_product_screen")
        elif event.button.id in ["view_active", "view_inactive", "view_available", "view_out_of_stock"]:
            inventory_map = {key: PRODUCT_FIELDS.get(key, key) for key in INVENTORY_DISPLAY_KEYS}
            
            if event.button.id == "view_active":
                self.app.push_screen(InventoryViewerScreen(title=TUI_MENU_OPTIONS['view_active'], list_function=list_products_inventory, list_args=[1], header_map=inventory_map))
            elif event.button.id == "view_inactive":
                self.app.push_screen(InventoryViewerScreen(title=TUI_MENU_OPTIONS['view_inactive'], list_function=list_products_inventory, list_args=[2], header_map=inventory_map))
            elif event.button.id == "view_available":
                self.app.push_screen(InventoryViewerScreen(title=TUI_MENU_OPTIONS['view_available'], list_function=list_available_products, header_map=inventory_map))
            elif event.button.id == "view_out_of_stock":
                self.app.push_screen(InventoryViewerScreen(title=TUI_MENU_OPTIONS['view_out_of_stock'], list_function=list_out_of_stock_products, header_map=inventory_map))
        elif event.button.id == "view_by_category":
            self.app.push_screen("view_by_category_screen")
