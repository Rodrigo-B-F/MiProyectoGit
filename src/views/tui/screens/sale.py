from decimal import Decimal
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Log, DataTable
from textual.containers import Vertical, Horizontal, Grid
from controllers import find_product_by_name_or_barcode, record_sale
from src.utils.translations import PRODUCT_FIELDS, INPUT_PROMPTS
from .notification import NotificationScreen

class SaleScreen(Screen):
    """Pantalla de Terminal Punto de Venta (TPV) para registrar ventas."""
    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Cancelar Venta (ESC)")]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cart: list[dict] = []
        self.current_product: dict | None = None
        self.total_sale: Decimal = Decimal("0.0")
        self.selected_cart_row: int | None = None 

    def compose(self) -> ComposeResult:
        yield Header(name="REGISTRAR VENTA (TPV)")
        with Grid(id="sale-grid"):
            with Vertical(id="sale-left-pane"):
                yield Static("1. Buscar Producto", classes="sale-subtitle")
                with Horizontal(classes="sale-group"):
                    yield Input(placeholder=INPUT_PROMPTS['barcode_search'], id="sale_search_input")
                    yield Button("Buscar", id="sale_search_button", variant="primary")
                yield Static("Producto Encontrado:", id="sale_found_label", classes="hidden")
                yield Static("", id="sale_found_product", classes="sale-found-text")
                with Horizontal(classes="sale-group"):
                    yield Input(placeholder=PRODUCT_FIELDS['quantity'], id="sale_quantity_input", value="1", disabled=True)
                    yield Button("Añadir al Carrito", id="sale_add_to_cart_button", disabled=True)
                yield Log(id="sale_feedback_log", max_lines=10)

            with Vertical(id="sale-right-pane"):
                yield Static("2. Carrito de Compras", classes="sale-subtitle")
                yield DataTable(id="sale_cart_table")
                yield Static(f"TOTAL: Bs {self.total_sale:.2f}", id="sale_total_display")
                with Horizontal(classes="sale-group"):
                    yield Button("CANCELAR VENTA", id="sale_cancel_button", variant="error")
                    yield Button("FINALIZAR VENTA", id="sale_finalize_button", variant="success")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#sale_cart_table", DataTable)
        table.add_columns(PRODUCT_FIELDS['product'], " ", PRODUCT_FIELDS['quantity'], PRODUCT_FIELDS['unit_price'], PRODUCT_FIELDS['subtotal'])
        table.cursor_type = "cell"
        self.log_message("Sistema TPV listo. Busque un producto para comenzar.")

    def log_message(self, message: str) -> None:
        self.query_one("#sale_feedback_log", Log).write_line(message)

    def enable_add_controls(self, enabled: bool) -> None:
        self.query_one("#sale_quantity_input", Input).disabled = not enabled
        self.query_one("#sale_add_to_cart_button", Button).disabled = not enabled
        self.query_one("#sale_found_label", Static).set_class(not enabled, "hidden")

    def clear_search_state(self) -> None:
        self.current_product = None
        self.query_one("#sale_search_input", Input).value = ""
        self.query_one("#sale_quantity_input", Input).value = "1"
        self.query_one("#sale_found_product", Static).update("")
        self.enable_add_controls(False)
        self.query_one("#sale_search_input", Input).focus()

    def update_cart_display(self) -> None:
        table = self.query_one("#sale_cart_table", DataTable)
        table.clear()
        self.total_sale = Decimal("0.0")
        for item in self.cart:
            table.add_row(item["name"], "[-]", item["quantity"], f"{item['unit_price']:.2f}", f"{item['subtotal']:.2f}")
            self.total_sale += item["subtotal"]
        self.query_one("#sale_total_display", Static).update(f"TOTAL: Bs {self.total_sale:.2f}")
        self.selected_cart_row = None

    def action_dismiss(self) -> None:
        self.reset_sale_screen()
        super().dismiss()

    def reset_sale_screen(self) -> None:
        self.cart.clear()
        self.current_product = None
        self.total_sale = Decimal("0.0")
        self.selected_cart_row = None
        self.update_cart_display() 
        self.clear_search_state()
        self.query_one("#sale_feedback_log", Log).clear()
        self.log_message("Sistema TPV listo. Busque un producto para comenzar.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "sale_search_button":
            self.handle_search()
        elif event.button.id == "sale_add_to_cart_button":
            self.handle_add_to_cart()
        elif event.button.id == "sale_finalize_button":
            self.handle_finalize_sale()
        elif event.button.id == "sale_cancel_button":
            self.action_dismiss()

    def handle_search(self) -> None:
        search_term = self.query_one("#sale_search_input", Input).value.strip()
        if not search_term:
            self.log_message("[ERROR] Ingrese un código de barras.")
            return

        results = find_product_by_name_or_barcode(search_term)
        if not results:
            self.log_message(f"[ERROR] Producto '{search_term}' no encontrado.")
            self.current_product = None
            self.enable_add_controls(False)
            return
        
        self.current_product = results[0]
        if self.current_product["active"] is not True:
             self.log_message(f"[ERROR] Producto '{self.current_product['name']}' está INACTIVO.")
             self.current_product = None
             self.enable_add_controls(False)
             return

        found_text = self.query_one("#sale_found_product", Static)
        found_text.update(f"Nombre: [b]{self.current_product['name']}[/b]\nPrecio Unit.: Bs {self.current_product['sale_price']:.2f} (Stock Disp.: {self.current_product['quantity']})")
        self.log_message(f"Producto encontrado: {self.current_product['name']}.")
        self.enable_add_controls(True)
        self.query_one("#sale_quantity_input", Input).focus()

    def handle_add_to_cart(self) -> None:
        if not self.current_product:
            self.log_message("[ERROR] No hay producto seleccionado.")
            return

        try:
            quantity = int(self.query_one("#sale_quantity_input", Input).value)
            if quantity <= 0: raise ValueError
        except ValueError:
            self.log_message("[ERROR] Cantidad inválida. Debe ser un número entero > 0.")
            return
            
        stock_available = int(self.current_product["quantity"])
        if quantity > stock_available:
            self.log_message(f"[ERROR] Stock insuficiente para '{self.current_product['name']}'.")
            self.log_message(f"Disponible: {stock_available}, Solicitado: {quantity}")
            return
            
        unit_price = Decimal(self.current_product["sale_price"])
        subtotal = unit_price * Decimal(quantity)
        
        cart_item = {
            "barcode": self.current_product["barcode"],
            "name": self.current_product["name"],
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        }
        
        self.cart.append(cart_item)
        self.log_message(f"[AÑADIDO] {quantity} x {cart_item['name']}")
        self.update_cart_display()
        self.clear_search_state()

    def handle_finalize_sale(self) -> None:
        if not self.cart:
            self.log_message("[ERROR] El carrito está vacío. Añada productos.")
            return
            
        items_to_sell = [{"barcode": item["barcode"], "quantity": item["quantity"]} for item in self.cart]
        self.log_message("Procesando venta... por favor espere.")
        
        try:
            success, message = record_sale(items_to_sell)
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.reset_sale_screen()
                super().dismiss()
            else:
                self.log_message(f"[FALLO EN VENTA] {message}")
        except Exception as e:
            self.log_message(f"[ERROR CRÍTICO] {e}")
            self.app.push_screen(NotificationScreen(f"Error crítico al vender: {e}"))

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Handle clicking on cells in the cart table."""
        if event.control.id == "sale_cart_table":
            # Column index 1 is the "[-]" column (0=Producto, 1= , 2=Cant., etc.)
            if event.coordinate.column == 1:
                row_index = event.coordinate.row
                self.handle_remove_from_cart(row_index)

    def handle_remove_from_cart(self, row_index: int) -> None:
        """Remove an item from the cart by its row index."""
        try:
            removed_item = self.cart.pop(row_index)
            self.log_message(f"[QUITADO] {removed_item['quantity']} x {removed_item['name']}")
            self.update_cart_display()
        except IndexError:
            self.log_message("[ERROR] El item seleccionado ya no existe.")
            self.update_cart_display()
        except Exception as e:
            self.log_message(f"[ERROR INESPERADO] {e}")
