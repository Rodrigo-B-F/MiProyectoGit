from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Footer
from textual.containers import Vertical

class AddScreen(Screen):
    """Pantalla con las opciones para agregar productos o stock."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Static("AGREGAR", id="main-title")
        yield Vertical(
            Button("AGREGAR UN NUEVO PRODUCTO", id="add_new_product"),
            Button("AGREGAR ESTOCK A UN PRODUCTO", id="add_stock"),
            Button("SALIR", id="exit_add_menu"),
            id="add-menu-container"
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_add_menu":
            self.dismiss()
        elif event.button.id == "add_new_product":
            self.app.push_screen("add_product_form")
        elif event.button.id == "add_stock":
            self.app.push_screen("add_stock_form")
