from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, DataTable, Static, Input, Label
from textual.containers import Vertical
from controllers import find_product_by_name_or_barcode
from src.utils.translations import PRODUCT_FIELDS, TUI_MENU_OPTIONS, INPUT_PROMPTS
from . import INVENTORY_DISPLAY_KEYS
from .notification import NotificationScreen

class SearchProductScreen(Screen):
    """Pantalla para buscar un producto por nombre o código de barras."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name=TUI_MENU_OPTIONS['view_search'])
        yield Vertical(
            Label(INPUT_PROMPTS['search_query']),
            Input(placeholder="Ej: Leche o 777123456", id="search_input", classes="form-input"),
            Static("", id="search_feedback"),
            Button("BUSCAR", id="execute_search"),
            classes="search-form-container"
        )
        yield Static("Resultados:", id="results_title")
        yield DataTable(id="search_results_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "execute_search":
            self.execute_search()

    def execute_search(self) -> None:
        search_term = self.query_one("#search_input", Input).value.strip()
        table = self.query_one(DataTable)
        feedback = self.query_one("#search_feedback")
        
        table.clear(columns=True)
        feedback.update("")
        
        if not search_term:
            feedback.update(" [b]ERROR:[/b] Ingrese un término de búsqueda.")
            return

        try:
            results = find_product_by_name_or_barcode(search_term)
            if not results:
                feedback.update(f" No se encontraron productos para '{search_term}'.")
                return

            headers = [PRODUCT_FIELDS.get(key, key) for key in INVENTORY_DISPLAY_KEYS]
            table.add_columns(*headers)
            original_keys = INVENTORY_DISPLAY_KEYS
            for row_dict in results:
                string_row = [str(row_dict.get(key, "N/A")) for key in original_keys]
                table.add_row(*string_row)

            feedback.update(f" Búsqueda exitosa. Se encontraron {len(results)} producto(s).")
        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")
            self.app.push_screen(NotificationScreen(f"Error en la búsqueda: {e}"))
