import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.containers import ScrollableContainer, Grid
from controllers import record_purchase
from src.utils.translations import INPUT_PROMPTS
from .notification import NotificationScreen

class AddStockFormScreen(Screen):
    """Formulario para registrar una entrada de stock (Compra)."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Cancelar (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR ESTOCK A UN PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese el código de barras y la cantidad de stock a agregar:", id="form-instruction"),
            Label(INPUT_PROMPTS['barcode']),
            Input(placeholder="Ej: 777123456", id="barcode", classes="form-input"),
            Label(INPUT_PROMPTS['quantity_purchase']),
            Input(placeholder="Ej: 50 (Solo números enteros)", id="quantity", classes="form-input"),
            Label(INPUT_PROMPTS['new_purchase_price']),
            Input(placeholder="Ej: 5.50 (Se actualizará en el sistema)", id="purchase_price", classes="form-input"),
            Label(INPUT_PROMPTS['expiration_date']),
            Input(placeholder="Ej: 2026-12-31 (Dejar vacío para no cambiar)", id="expiration_date", classes="form-input", value=""),
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
            price_str = self.query_one("#purchase_price", Input).value.strip()
            expiration_str = self.query_one("#expiration_date", Input).value.strip()
            
            if not all([barcode, quantity_str, price_str]):
                feedback.update(" [b]ERROR:[/b] Código de Barras, Cantidad y Precio son obligatorios.")
                return

            try:
                quantity_i = int(quantity_str)
                purchase_price_f = float(price_str)
                if quantity_i <= 0 or purchase_price_f < 0:
                    feedback.update(" [b]ERROR:[/b] La cantidad debe ser positiva y el precio no puede ser negativo.")
                    return
            except ValueError:
                feedback.update(" [b]ERROR:[/b] La Cantidad o el Precio no son números válidos.")
                return
            
            # Procesar fecha de vencimiento si se proporciona
            exp_date = None
            if expiration_str:
                try:
                    exp_date = datetime.datetime.strptime(expiration_str, '%Y-%m-%d').date()
                except ValueError:
                    feedback.update(" [b]ERROR:[/b] Formato de fecha de vencimiento inválido. Use YYYY-MM-DD.")
                    return
            
            success, message = record_purchase(
                product_barcode=barcode,
                quantity=quantity_i,
                purchase_price=purchase_price_f,
                expiration_date=exp_date
            )
            
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.dismiss()

        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}. Verifique el código de barras.")
            self.app.push_screen(NotificationScreen(f"Error: {e}"))
