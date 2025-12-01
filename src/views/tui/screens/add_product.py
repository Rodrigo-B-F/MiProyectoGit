import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.containers import ScrollableContainer, Grid
from controllers import add_product
from src.utils.translations import PRODUCT_FIELDS, INPUT_PROMPTS
from .notification import NotificationScreen

class AddProductFormScreen(Screen):
    """Formulario para agregar un nuevo producto y su stock inicial."""

    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Cancelar (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR UN NUEVO PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese los datos del nuevo producto:", id="form-instruction"),
            Label(INPUT_PROMPTS['name']),
            Input(placeholder="Ej: Leche Entera", id="name", classes="form-input"),
            Label(INPUT_PROMPTS['barcode']),
            Input(placeholder="Ej: 777123456 (Debe ser único)", id="barcode", classes="form-input"),
            Label(INPUT_PROMPTS['category_name']),
            Input(placeholder="Ej: Lácteos (Se creará si no existe)", id="category_name", classes="form-input"),
            Label(INPUT_PROMPTS['unit']),
            Input(placeholder="Ej: unidad, kg, litro", id="unit", classes="form-input"),
            Label(INPUT_PROMPTS['location']),
            Input(placeholder="Ej: Pasillo A", id="location", classes="form-input", value=""),
            Label(INPUT_PROMPTS['purchase_price']),
            Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price", classes="form-input"),
            Label(INPUT_PROMPTS['sale_price']),
            Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price", classes="form-input"),
            Label(INPUT_PROMPTS['initial_quantity']),
            Input(placeholder="Ej: 100 (Solo números enteros)", id="initial_quantity", classes="form-input"),
            Label(INPUT_PROMPTS['expiration_date']),
            Input(placeholder="Ej: 2026-12-31 (Dejar vacío si no aplica)", id="expiration_date", classes="form-input", value=""),
            Static("", id="form_feedback"),
            Grid(
                Button("GUARDAR", id="save_product"),
                Button("CANCELAR", id="cancel_product"),
                id="form-buttons-grid"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_product":
            self.dismiss()
        elif event.button.id == "save_product":
            self.handle_save()

    def handle_save(self) -> None:
        feedback = self.query_one("#form_feedback")
        try:
            data = {
                "name": self.query_one("#name", Input).value.strip(),
                "barcode": self.query_one("#barcode", Input).value.strip(),
                "category_name": self.query_one("#category_name", Input).value.strip(),
                "unit": self.query_one("#unit", Input).value.strip(),
                "location": self.query_one("#location", Input).value.strip(),
                "purchase_price": self.query_one("#purchase_price", Input).value.strip(),
                "sale_price": self.query_one("#sale_price", Input).value.strip(),
                "initial_quantity": self.query_one("#initial_quantity", Input).value.strip(),
                "expiration_date": self.query_one("#expiration_date", Input).value.strip(),
            }
            
            if not all([data["name"], data["barcode"], data["category_name"], data["unit"], data["purchase_price"], data["sale_price"], data["initial_quantity"]]):
                feedback.update(" [b]ERROR:[/b] Los campos principales no pueden estar vacíos.")
                return

            try:
                purchase_price_f = float(data["purchase_price"])
                sale_price_f = float(data["sale_price"])
                initial_quantity_i = int(data["initial_quantity"])
            except ValueError:
                feedback.update(" [b]ERROR:[/b] Precios y Cantidad deben ser números válidos.")
                return

            exp_date = None
            if data["expiration_date"]:
                try:
                    exp_date = datetime.datetime.strptime(data["expiration_date"], '%Y-%m-%d').date()
                except ValueError:
                    feedback.update(" [b]ERROR:[/b] Formato de fecha de vencimiento inválido. Use YYYY-MM-DD.")
                    return

            success, message = add_product(
                data["name"], data["barcode"], data["category_name"], data["unit"], data["location"],
                purchase_price_f, sale_price_f, initial_quantity_i, exp_date
            )
            
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.dismiss()

        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}. ¿El código de barras ya existe?")
            self.app.push_screen(NotificationScreen(f"Error: {e}"))
