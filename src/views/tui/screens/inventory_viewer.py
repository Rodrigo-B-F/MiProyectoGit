from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from .notification import NotificationScreen

class InventoryViewerScreen(Screen):
    """Muestra una lista de productos utilizando una función de servicio específica."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]
    
    def __init__(self, title: str, list_function, list_args=None, header_map: dict | None = None, **kwargs):
        super().__init__(**kwargs)
        self.screen_title = title
        self.list_function = list_function
        self.list_args = list_args if list_args is not None else []
        self.header_map = header_map

    def compose(self) -> ComposeResult:
        yield Header(name=self.screen_title) 
        yield Static("Cargando datos...", id="list_feedback")
        yield DataTable(id="inventory_table")
        yield Footer()

    def on_mount(self) -> None:
        self.load_data()

    def load_data(self) -> None:
        table = self.query_one(DataTable)
        feedback = self.query_one("#list_feedback", Static)
        
        table.clear(columns=True)
        table.cursor_type = "row"
        feedback.update("Cargando datos...")

        try:
            inventory_data = self.list_function(*self.list_args)

            if not inventory_data:
                feedback.update(f" No se encontraron registros para: [b]{self.screen_title}[/b].")
                table.add_column("Aviso")
                table.add_row("No hay datos disponibles.")
                return

            if self.header_map:
                headers = self.header_map.values()
                table.add_columns(*headers)
                original_keys = self.header_map.keys()
                for row_dict in inventory_data:
                    string_row = [str(row_dict.get(key, "N/A")) for key in original_keys]
                    table.add_row(*string_row)
            else:
                headers = inventory_data[0].keys()
                table.add_columns(*headers)
                for row_dict in inventory_data:
                    string_row = [str(item) for item in row_dict.values()]
                    table.add_row(*string_row)

            feedback.update(f" Se encontraron [b]{len(inventory_data)}[/b] registros.")
        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")
            self.app.push_screen(NotificationScreen(f"Error al listar: {e}"))
