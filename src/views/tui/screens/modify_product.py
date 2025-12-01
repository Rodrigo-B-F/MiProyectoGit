import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label, DataTable
from textual.containers import ScrollableContainer, Grid
from controllers import find_product_by_name_or_barcode, get_product_details_by_id, update_product_details
from src.utils.translations import PRODUCT_FIELDS, INPUT_PROMPTS
from .notification import NotificationScreen

class ModifyProductScreen(Screen):
    """Pantalla para buscar un producto y modificar sus detalles directamente."""
    CSS_PATH = "../tui.css"
    BINDINGS = [("escape", "dismiss", "Menú (ESC)")]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.current_product_id: int | None = None
        self.current_product_data: dict | None = None

    def show_form(self) -> None:
        self.query_one("#modify-form-title", Static).remove_class("hidden")
        self.query_one("#modify-form-grid", Grid).remove_class("hidden")
        self.query_one("#save_modifications", Button).remove_class("hidden")

    def hide_form(self) -> None:
        self.query_one("#modify-form-title", Static).add_class("hidden")
        self.query_one("#modify-form-grid", Grid).add_class("hidden")
        self.query_one("#save_modifications", Button).add_class("hidden")

    def compose(self) -> ComposeResult:
        yield Header(name="BUSCAR Y MODIFICAR PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese el nombre o código de barras para buscar:", classes="subtitle"),
            Input(placeholder="Buscar por Nombre o Barcode...", id="modify_search_input"),
            Button("BUSCAR", id="run_modify_search", variant="primary"),
            Static("", id="modify_search_feedback"),
            DataTable(id="modify_results_table"),
            Static("--- Detalles del Producto Seleccionado ---", id="modify-form-title", classes="hidden"),
            Grid(
                Label(INPUT_PROMPTS['name']), Input(placeholder="Ej: Leche Entera", id="name_input", classes="form-input"),
                Label(INPUT_PROMPTS['barcode']), Input(placeholder="Ej: 777123456 (Debe ser único)", id="barcode_input", classes="form-input"),
                Label(INPUT_PROMPTS['category_name']), Input(placeholder="Ej: Lácteos", id="category_input", classes="form-input"),
                Label(INPUT_PROMPTS['unit']), Input(placeholder="Ej: unidad, kg, litro", id="unit_input", classes="form-input"),
                Label(INPUT_PROMPTS['purchase_price']), Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price_input", classes="form-input"),
                Label(INPUT_PROMPTS['sale_price']), Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price_input", classes="form-input"),
                Label(f"{PRODUCT_FIELDS['profit']} (Solo Lectura):"), Input(id="profit_input", classes="form-input", disabled=True),
                Label(INPUT_PROMPTS['location']), Input(placeholder="Ej: Pasillo A", id="location_input", classes="form-input"),
                Label(f"{PRODUCT_FIELDS['date_added']} (YYYY-MM-DD):"), Input(placeholder="Ej: 2026-12-31", id="date_added_input", classes="form-input"),
                Label(INPUT_PROMPTS['expiration_date']), Input(placeholder="Ej: 2026-12-31", id="expiration_date_input", classes="form-input"),
                Label(f"{PRODUCT_FIELDS['active']} (True/False):"), Input(placeholder="True o False", id="active_input", classes="form-input"),
                Button("GUARDAR CAMBIOS", id="save_modifications", variant="primary", classes="hidden"),
                id="modify-form-grid", classes="hidden"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run_modify_search":
            self.run_search()
        elif event.button.id == "save_modifications":
            self.handle_save()
    
    def run_search(self) -> None:
        search_query = self.query_one("#modify_search_input", Input).value.strip()
        table = self.query_one("#modify_results_table", DataTable)
        feedback = self.query_one("#modify_search_feedback", Static)
        
        feedback.update("")
        self.current_product_data = None
        self.hide_form()
        table.clear(columns=True)

        if not search_query:
            feedback.update(" [b]ADVERTENCIA:[/b] Ingrese un criterio de búsqueda.")
            return

        results = find_product_by_name_or_barcode(search_query)
        
        if not results:
            feedback.update(" [b]INFORMACIÓN:[/b] No se encontraron productos.")
            return

        table.add_columns(PRODUCT_FIELDS['name'], PRODUCT_FIELDS['barcode'], PRODUCT_FIELDS['category_name'], PRODUCT_FIELDS['unit'], PRODUCT_FIELDS['quantity'], PRODUCT_FIELDS['purchase_price'], PRODUCT_FIELDS['sale_price'], PRODUCT_FIELDS['profit'], PRODUCT_FIELDS['date_added'], PRODUCT_FIELDS['expiration_date'], PRODUCT_FIELDS['location'], PRODUCT_FIELDS['active'])
        table.cursor_type = "row"
        
        for p in results:
            table.add_row(
                p["name"], p["barcode"], p["category_name"], p["unit"], p.get("quantity", "N/A"), p["purchase_price"], p["sale_price"], p["profit"], p["date_added"], p["expiration_date"], p["location"], p["active"],
                key=str(p["id"])
            )
        
        feedback.update(f" [b]ÉXITO:[/b] {len(results)} producto(s) encontrado(s). Seleccione uno para modificar.")
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        try:
            product_id = int(event.row_key.value)
            self.current_product_id = product_id
            product_data = get_product_details_by_id(product_id)
            if not product_data:
                self.query_one("#modify_search_feedback", Static).update(f" [b]ERROR:[/b] Detalles para ID {product_id} no encontrados.")
                self.hide_form()
                return
            
            self.current_product_data = product_data
            self.show_form()
            self.populate_form(product_data)
            self.query_one("#modify_search_feedback", Static).update(f" [b]PRODUCTO CARGADO:[/b] '{product_data['name']}'. Modifique los campos y Guarde.")
        except ValueError:
            self.query_one("#modify_search_feedback", Static).update(" [b]ERROR:[/b] El ID de la fila no es válido.")
        except Exception as e:
            self.query_one("#modify_search_feedback", Static).update(f" [b]ERROR INESPERADO:[/b] {e}")

    def populate_form(self, data: dict) -> None:
        self.query_one("#profit_input", Input).value = str(data["profit"])
        
        purchase_date_obj = data["date_added"]
        purchase_date_str = purchase_date_obj.strftime('%Y-%m-%d') if purchase_date_obj else ""
        self.query_one("#date_added_input", Input).value = purchase_date_str

        self.query_one("#name_input", Input).value = data["name"]
        self.query_one("#barcode_input", Input).value = data["barcode"]
        self.query_one("#category_input", Input).value = data["category_name"]
        self.query_one("#unit_input", Input).value = data["unit"]
        self.query_one("#location_input", Input).value = data["location"] if data["location"] else ""
        self.query_one("#purchase_price_input", Input).value = str(data["purchase_price"])
        self.query_one("#sale_price_input", Input).value = str(data["sale_price"])
        
        exp_date_obj = data["expiration_date"]
        exp_date_str = exp_date_obj.strftime('%Y-%m-%d') if exp_date_obj else ""
        self.query_one("#expiration_date_input", Input).value = exp_date_str
        
        self.query_one("#active_input", Input).value = str(data["active"])

    def handle_save(self) -> None:
        if not self.current_product_id:
            self.query_one("#modify_search_feedback", Static).update(" [b]ERROR:[/b] No hay producto seleccionado para guardar.")
            return

        try:
            data = {
                "name": self.query_one("#name_input", Input).value.strip(),
                "barcode": self.query_one("#barcode_input", Input).value.strip(),
                "category_name": self.query_one("#category_input", Input).value.strip(),
                "unit": self.query_one("#unit_input", Input).value.strip(),
                "location": self.query_one("#location_input", Input).value.strip(),
                "purchase_price": self.query_one("#purchase_price_input", Input).value.strip(),
                "sale_price": self.query_one("#sale_price_input", Input).value.strip(),
                "expiration_date": self.query_one("#expiration_date_input", Input).value.strip(),
                "active": self.query_one("#active_input", Input).value.strip(),
                "date_added": self.query_one("#date_added_input", Input).value.strip(),
            }
            
            if not all([data["name"], data["barcode"], data["category_name"], data["unit"], data["purchase_price"], data["sale_price"], data["active"], data["date_added"]]):
                self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] Los campos principales no pueden estar vacíos."))
                return

            purchase_price_f = float(data["purchase_price"])
            sale_price_f = float(data["sale_price"])
            active_status = data["active"].capitalize()

            if active_status not in ["True", "False"]:
                self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] El campo 'Estado Activo' debe ser 'True' o 'False'."))
                return

            try:
                datetime.datetime.strptime(data["date_added"], '%Y-%m-%d').date()
            except ValueError:
                self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] Formato de Fecha de Adquisición inválido. Use YYYY-MM-DD."))
                return

            success, message = update_product_details(
                product_id=self.current_product_id,
                name=data["name"],
                new_barcode=data["barcode"],
                category_name=data["category_name"],
                unit=data["unit"],
                location=data["location"],
                purchase_price=purchase_price_f,
                sale_price=sale_price_f,
                expiration_date_str=data["expiration_date"],
                date_added_str=data["date_added"],
                active_status=active_status
            )
            
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.hide_form()
                self.query_one("#modify_results_table", DataTable).clear()
                self.query_one("#modify_search_input", Input).value = ""

        except ValueError:
            self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] Los precios son inválidos."))
        except Exception as e:
            self.app.push_screen(NotificationScreen(f" [b]ERROR INESPERADO:[/b] {e}"))
