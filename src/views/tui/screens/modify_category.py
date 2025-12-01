from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label, DataTable
from textual.containers import Vertical
from controllers import list_categories, update_category
from .notification import NotificationScreen

class ModifyCategoryScreen(Screen):
    """Pantalla para modificar el nombre y descripción de categorías."""
    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]
    
    categories_map: dict = {}
    current_category_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Header(name="MODIFICAR CATEGORÍA")
        
        yield Static("Seleccione una categoría para modificar:", classes="subtitle")
        yield DataTable(id="mod_cat_table")
        
        # Formulario (oculto inicialmente)
        yield Vertical(
            Static("--- Editar Categoría Seleccionada ---", classes="subtitle"),
            Label("Nombre:"),
            Input(id="cat_name_input", classes="form-input"),
            Label("Descripción:"),
            Input(id="cat_desc_input", classes="form-input"),
            Button("GUARDAR CAMBIOS", id="save_cat_btn", variant="primary"),
            id="mod_cat_form",
            classes="hidden"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.load_categories()

    def load_categories(self) -> None:
        table = self.query_one("#mod_cat_table", DataTable)
        table.clear(columns=True)
        table.add_columns("Nombre", "Descripción")
        table.cursor_type = "row"
        
        try:
            cats = list_categories()
            self.categories_map = {}
            if cats:
                for c in cats:
                    table.add_row(c['name'], c['description'] or "", key=str(c['id']))
                    self.categories_map[c['id']] = c
            else:
                table.add_row("N/A", "No hay categorías", "")
        except Exception as e:
            self.app.push_screen(NotificationScreen(f"Error al cargar categorías: {e}"))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        try:
            cat_id = int(event.row_key.value)
            self.current_category_id = cat_id
            cat_data = self.categories_map.get(cat_id)
            
            if cat_data:
                self.query_one("#cat_name_input", Input).value = cat_data['name']
                self.query_one("#cat_desc_input", Input).value = cat_data['description'] or ""
                self.query_one("#mod_cat_form", Vertical).remove_class("hidden")
        except ValueError:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_cat_btn":
            self.save_category()

    def save_category(self) -> None:
        if not self.current_category_id: return
        
        new_name = self.query_one("#cat_name_input", Input).value.strip()
        new_desc = self.query_one("#cat_desc_input", Input).value.strip()
        
        if not new_name:
            self.app.push_screen(NotificationScreen("El nombre no puede estar vacío."))
            return

        try:
            success, msg = update_category(self.current_category_id, name=new_name, description=new_desc)
            self.app.push_screen(NotificationScreen(msg))
            
            if success:
                self.query_one("#mod_cat_form", Vertical).add_class("hidden")
                self.load_categories() # Recargar lista
        except Exception as e:
            self.app.push_screen(NotificationScreen(f"Error al guardar: {e}"))
