from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button
from textual.containers import Vertical

class ModifyMenuScreen(Screen):
    """Pantalla de menú para seleccionar qué modificar (Producto o Categoría)."""
    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="MENÚ DE MODIFICACIÓN")
        yield Vertical(
            Button("MODIFICAR PRODUCTO (DETALLES)", id="modify_product"),
            Button("MODIFICAR CATEGORÍA", id="modify_category"),
            Button("SALIR", id="exit_modify_menu"),
            id="modify-menu-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_modify_menu":
            self.dismiss()
        elif event.button.id == "modify_product":
            self.app.push_screen("modify_product_screen")
        elif event.button.id == "modify_category":
            self.app.push_screen("modify_category_screen")
