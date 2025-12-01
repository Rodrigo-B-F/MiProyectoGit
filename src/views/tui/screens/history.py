from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Footer
from textual.containers import Vertical
from controllers import list_sales_history, sales_summary_by_date
from src.utils.translations import PRODUCT_FIELDS
from .inventory_viewer import InventoryViewerScreen

class HistoryScreen(Screen):
    """Pantalla con las opciones para ver el historial de ventas."""
    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Static("HISTORIAL DE VENTAS", id="main-title")
        yield Vertical(
            Button("HISTORIAL POR VENTAS (DETALLADO)", id="history_sales"),
            Button("RESUMEN POR FECHA (TOTALES)", id="history_date"),
            Button("SALIR", id="exit_history_menu"),
            id="history-menu-container"
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_history_menu":
            self.dismiss()
        elif event.button.id == "history_sales":
            sales_map = {
                "timestamp": PRODUCT_FIELDS['timestamp'],
                "product": PRODUCT_FIELDS['product'],
                "barcode": PRODUCT_FIELDS['barcode'],
                "quantity": PRODUCT_FIELDS['quantity'],
                "unit_price": PRODUCT_FIELDS['unit_price'],
                "subtotal": PRODUCT_FIELDS['subtotal']
            }
            self.app.push_screen(InventoryViewerScreen(title="HISTORIAL POR VENTAS (DETALLADO)", list_function=list_sales_history, header_map=sales_map))
        elif event.button.id == "history_date":
            date_map = {
                "date": PRODUCT_FIELDS['date'],
                "total_sales": PRODUCT_FIELDS['total_sales'],
                "total_amount": PRODUCT_FIELDS['total_amount']
            }
            self.app.push_screen(InventoryViewerScreen(title="RESUMEN DE VENTAS POR FECHA", list_function=sales_summary_by_date, header_map=date_map))
