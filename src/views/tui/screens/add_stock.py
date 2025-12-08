import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.containers import ScrollableContainer, Grid
from controllers import add_stock
from src.utils.translations import INPUT_PROMPTS
from .notification import NotificationScreen

class AddStockFormScreen(Screen):
    """Formulario para registrar una entrada de stock."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Cancelar (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR STOCK A UN PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese el código de barras y la cantidad de stock a agregar:", id="form-instruction"),
            Label(INPUT_PROMPTS['barcode']),
            Input(placeholder="Ej: 777123456", id="barcode", classes="form-input"),
            Label(INPUT_PROMPTS['quantity_purchase']),
            Input(placeholder="Ej: 50 (Solo números enteros)", id="quantity", classes="form-input"),
            Static("", id="form_feedback"),
            Grid(
                Button("REGISTRAR ENTRADA", id="register_stock"),
                Button("CANCELAR", id="cancel_stock"),
                id="form-buttons-grid"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_stock":
            self.dismiss()
        elif event.button.id == "register_stock":
            self.handle_save()

    def handle_save(self) -> None:
        feedback = self.query_one("#form_feedback")
        try:
            barcode = self.query_one("#barcode", Input).value.strip()
            quantity_str = self.query_one("#quantity", Input).value.strip()
            
            if not all([barcode, quantity_str]):
                feedback.update(" [b]ERROR:[/b] Código de Barras y Cantidad son obligatorios.")
                return

            try:
                quantity_i = int(quantity_str)
                if quantity_i <= 0:
                    feedback.update(" [b]ERROR:[/b] La cantidad debe ser positiva.")
                    return
            except ValueError:
                feedback.update(" [b]ERROR:[/b] La Cantidad no es un número válido.")
                return
            
            success, message = add_stock(
                product_barcode=barcode,
                quantity=quantity_i
            )
            
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.dismiss()

        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}. Verifique el código de barras.")
            self.app.push_screen(NotificationScreen(f"Error: {e}"))
