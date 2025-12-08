from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static, Button, Footer
from textual.containers import Grid
from textual.binding import Binding

class MainMenuScreen(Screen):
    """La pantalla principal que muestra el menú de opciones."""
    CSS_PATH = "../tui.css"
    BINDINGS = [Binding("escape", "quit_app", "Salir (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("MENÚ PRINCIPAL")
        yield Grid(
            Button("AGREGAR", id="agregar"),
            Button("VER", id="ver"),
            Button("MODIFICAR", id="modify_menu"),
            Button("VENDER", id="vender"),
            Button("HISTORIAL", id="historial"),
            Button("SALIR", id="salir"),
            id="menu-grid"
        )
        yield Footer()

    def action_quit_app(self) -> None:
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "salir":
            self.app.exit()
        elif button_id == "agregar":
            self.app.push_screen("add_menu")
        elif button_id == "ver":
            self.app.push_screen("view_menu")
        elif button_id == "modify_menu":
            self.app.push_screen("modify_menu_screen") 
        elif button_id == "vender":
            self.app.push_screen("sale_screen")
        elif button_id == "historial":
            self.app.push_screen("history_menu")
