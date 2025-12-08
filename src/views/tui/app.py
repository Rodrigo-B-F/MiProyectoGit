from textual.app import App
from .screens.main_menu import MainMenuScreen
from .screens.notification import NotificationScreen
from .screens.add_menu import AddScreen
from .screens.add_product import AddProductFormScreen
from .screens.add_stock import AddStockFormScreen
from .screens.view_menu import ViewScreen
from .screens.search_product import SearchProductScreen
from .screens.view_by_category import ViewByCategoryScreen
from .screens.modify_menu import ModifyMenuScreen
from .screens.modify_category import ModifyCategoryScreen
from .screens.modify_product import ModifyProductScreen
from .screens.sale import SaleScreen
from .screens.history import HistoryScreen

class InventoryTUI(App):
    """La aplicación TUI principal."""
    TITLE = "Sistema de Inventario"
    CSS_PATH = "tui.css"
    SCREENS = {
        "main_menu": MainMenuScreen,
        "notify": NotificationScreen,
        "add_menu": AddScreen,
        "add_product_form": AddProductFormScreen,
        "add_stock_form": AddStockFormScreen,
        "view_menu": ViewScreen,
        "search_product_screen": SearchProductScreen,
        "view_by_category_screen": ViewByCategoryScreen,
        "modify_menu_screen": ModifyMenuScreen,
        "modify_category_screen": ModifyCategoryScreen,
        "modify_product_screen": ModifyProductScreen,
        "sale_screen": SaleScreen,
        "history_menu": HistoryScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("main_menu")
