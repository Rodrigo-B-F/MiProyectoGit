from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from controllers import list_categories, list_products_by_category
from src.utils.translations import PRODUCT_FIELDS, TUI_MENU_OPTIONS
from . import INVENTORY_DISPLAY_KEYS
from .notification import NotificationScreen

class ViewByCategoryScreen(Screen):
    """Pantalla que permite seleccionar una categoría y luego muestra sus productos."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]
    categories_map: dict = {} 

    def compose(self) -> ComposeResult:
        yield Header(name=TUI_MENU_OPTIONS['view_by_category'])
        yield Static("Seleccione una categoría para ver sus productos:", id="category_title")
        yield Static("Cargando categorías...", id="list_feedback")
        yield DataTable(id="category_list_table")
        yield Static("", id="products_title", classes="hidden")
        yield DataTable(id="products_by_category_table", classes="hidden")
        yield Footer()

    def on_mount(self) -> None:
        self.load_categories()
        table = self.query_one("#category_list_table", DataTable)
        table.cursor_type = "row"
        
    def load_categories(self) -> None:
        table = self.query_one("#category_list_table", DataTable)
        feedback = self.query_one("#list_feedback", Static)
        
        table.clear(columns=True)
        self.categories_map = {}
        feedback.update("Cargando categorías...")

        try:
            category_data = list_categories()
            if not category_data:
                feedback.update(" No se encontraron categorías en la base de datos.")
                table.add_column("Aviso")
                table.add_row("No hay categorías.")
                return

            table.add_column(PRODUCT_FIELDS['name'], key="name")
            table.add_column(PRODUCT_FIELDS['description'], key="description")
            
            for category in category_data:
                category_id = category["id"]
                category_name = category["name"]
                self.categories_map[category_id] = category_name
                table.add_row(
                    category_name,
                    category["description"] if category["description"] else "N/A",
                    key=str(category_id)
                )
            feedback.update(f" Se encontraron [b]{len(category_data)}[/b] categorías. Seleccione una.")
        except Exception as e:
            feedback.update(f" ERROR: {e}")
            self.app.push_screen(NotificationScreen(f"Error al listar categorías: {e}"))
            
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Check which table triggered the event
        if event.control.id == "category_list_table":
            category_id_key = event.row_key.value
            try:
                category_id = int(category_id_key) 
            except ValueError:
                self.app.push_screen(NotificationScreen(f"Error: La clave de categoría '{category_id_key}' no es un número válido."))
                return
                
            category_name = self.categories_map.get(category_id, "Desconocida")
            self.list_products_for_category(category_id, category_name)
        
    def list_products_for_category(self, category_id: int, category_name: str) -> None:
        products_table = self.query_one("#products_by_category_table", DataTable)
        products_title = self.query_one("#products_title", Static)
        
        products_table.clear(columns=True)
        products_table.remove_class("hidden")
        products_title.update(f"Cargando productos para: [b]{category_name}[/b]")
        products_title.remove_class("hidden")

        try:
            products_data = list_products_by_category(category_id)
            if not products_data:
                products_table.add_column("Aviso")
                products_table.add_row("No hay productos en esta categoría.")
                products_title.update(f"Productos en la Categoría [b]{category_name}[/b]: (0 encontrados)")
                return

            headers = [PRODUCT_FIELDS.get(key, key) for key in INVENTORY_DISPLAY_KEYS]
            products_table.add_columns(*headers)
            original_keys = INVENTORY_DISPLAY_KEYS
            for row_dict in products_data:
                string_row = [str(row_dict.get(key, "N/A")) for key in original_keys]
                products_table.add_row(*string_row)
                
            products_title.update(f"Productos en la Categoría [b]{category_name}[/b]: ({len(products_data)} encontrados)")
        except Exception as e:
            products_title.update(f"ERROR: No se pudo consultar la categoría {category_name}")
            products_table.add_column("Error")
            products_table.add_row(f"Detalle del error: {e}")
            self.app.push_screen(NotificationScreen(f"Error grave en el servicio: {e}"))
