# src/views/tui.py

import sys
import os

# --- Configuración para permitir ejecución directa ---
if __name__ == "__main__":
    # Subir dos niveles desde 'src/views/tui.py' para llegar a la raíz del proyecto
    # y luego apuntar a 'src' para que 'models' y 'controllers' sean importables
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

import datetime
from decimal import Decimal
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, Button, DataTable, Static, Input, Label, Log
from textual.containers import Vertical, Horizontal, ScrollableContainer, Grid
from textual.binding import Binding

# --- Importar la lógica de negocio y la BD ---
from models import init_db
from controllers.product_controller import (
    add_product,
    #toggle_product_status,
    update_product_details,
    find_product_by_name_or_barcode,
    apply_expiring_product_offer,
    get_product_details_by_id
)
from controllers.inventory_controller import (
    record_purchase,
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    list_expiring_products,
    list_categories,
    list_products_by_category,
    update_category
)
from controllers.sale_controller import (
    record_sale,
    list_sales_history,
    sales_summary_by_date
)

# --- Inicializar la BD al arrancar ---
print("Inicializando base de datos...")
init_db()
print("Base de datos lista.")


# --- Pantalla de Notificación (Modal) ---
class NotificationScreen(ModalScreen):
    """Una pantalla modal para mostrar un mensaje al usuario."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, id="message"),
            Button("Aceptar", variant="primary", id="accept_button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

# --- Pantalla Menú de Agregados ---
class AddScreen(Screen):
    """Pantalla con las opciones para agregar productos o stock."""

    CSS_PATH = "tui.css"
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


# --- Pantalla Formulario para Añadir Producto ---
class AddProductFormScreen(Screen):
    """Formulario para agregar un nuevo producto y su stock inicial."""

    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Cancelar (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR UN NUEVO PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese los datos del nuevo producto:", id="form-instruction"),
            Label("Nombre del Producto:"),
            Input(placeholder="Ej: Leche Entera", id="name", classes="form-input"),
            Label("Código de Barras:"),
            Input(placeholder="Ej: 777123456 (Debe ser único)", id="barcode", classes="form-input"),
            Label("Categoría:"),
            Input(placeholder="Ej: Lácteos (Se creará si no existe)", id="category_name", classes="form-input"),
            Label("Unidad de Medida:"),
            Input(placeholder="Ej: unidad, kg, litro", id="unit", classes="form-input"),
            Label("Ubicación:"),
            Input(placeholder="Ej: Pasillo A", id="location", classes="form-input", value=""),
            Label("Precio de Compra:"),
            Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price", classes="form-input"),
            Label("Precio de Venta:"),
            Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price", classes="form-input"),
            Label("Cantidad Inicial en Stock:"),
            Input(placeholder="Ej: 100 (Solo números enteros)", id="initial_quantity", classes="form-input"),
            Label("Fecha de Vencimiento (YYYY-MM-DD - Opcional):"),
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

# --- Pantalla Formulario para Agregar Stock (Compra) ---
class AddStockFormScreen(Screen):
    """Formulario para registrar una entrada de stock (Compra)."""

    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Cancelar (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR ESTOCK A UN PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese el código de barras y la cantidad de stock a agregar:", id="form-instruction"),
            Label("Código de Barras del Producto:"),
            Input(placeholder="Ej: 777123456", id="barcode", classes="form-input"),
            Label("Cantidad a Agregar:"),
            Input(placeholder="Ej: 50 (Solo números enteros)", id="quantity", classes="form-input"),
            Label("Nuevo Precio de Compra:"),
            Input(placeholder="Ej: 5.50 (Se actualizará en el sistema)", id="purchase_price", classes="form-input"),
            Label("Fecha de Vencimiento (YYYY-MM-DD - Opcional):"),
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


# --- Pantalla Menú de Visualización (VER) ---
class ViewScreen(Screen):
    """Pantalla con las opciones para visualizar reportes e inventario."""

    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="VER")
        yield Vertical(
            Button("BUSCAR PRODUCTO", id="view_search"),
            Button("PRODUCTOS ACTIVOS", id="view_active", classes="menu-button"),
            Button("PRODUCTOS INACTIVOS", id="view_inactive"),
            Button("PRODUCTOS CON STOCK", id="view_available"),
            Button("PRODUCTOS SIN STOCK", id="view_out_of_stock"),
            Button("VER PRÓXIMOS A VENCER", id="view_expiring"),
            Button("VER POR CATEGORÍA", id="view_by_category"),
            Button("SALIR", id="exit_view_menu"),
            id="view-menu-container"
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_view_menu":
            self.dismiss()
        elif event.button.id == "view_search":
            self.app.push_screen("search_product_screen")
        elif event.button.id == "view_active":
            # Mapeo de columnas para PRODUCTOS ACTIVOS con los nombres en español en el orden especificado
            header_map = {
                "name": "Nombre",
                "barcode": "Código de Barras",
                "category_name": "Categoría",
                "unit": "Envase",
                "quantity": "Cantidad",
                "purchase_price": "Precio de Compra",
                "sale_price": "Precio de Venta",
                "profit": "Ganancia",
                "location": "Ubicación",
                "active": "Estado"
            }
            self.app.push_screen(InventoryViewerScreen(title="PRODUCTOS ACTIVOS", list_function=list_products_inventory, list_args=[1], header_map=header_map))
        elif event.button.id == "view_inactive":
            self.app.push_screen(InventoryViewerScreen(title="PRODUCTOS INACTIVOS", list_function=list_products_inventory, list_args=[2]))
        elif event.button.id == "view_available":
            self.app.push_screen(InventoryViewerScreen(title="PRODUCTOS CON STOCK", list_function=list_available_products))
        elif event.button.id == "view_out_of_stock":
            self.app.push_screen(InventoryViewerScreen(title="PRODUCTOS SIN STOCK", list_function=list_out_of_stock_products))
        elif event.button.id == "view_expiring":
            DAYS = 10
            self.app.push_screen(InventoryViewerScreen(title=f"PROX. A VENCER ({DAYS} DÍAS)", list_function=list_expiring_products, list_args=[DAYS]))
        elif event.button.id == "view_by_category":
            self.app.push_screen("view_by_category_screen")

# --- Pantalla para Buscar Producto ---
class SearchProductScreen(Screen):
    """Pantalla para buscar un producto por nombre o código de barras."""

    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]

    def compose(self) -> ComposeResult:
        yield Header(name="BUSCAR PRODUCTO")
        yield Vertical(
            Label("Ingrese el Nombre o Código de Barras a buscar:"),
            Input(placeholder="Ej: Leche o 777123456", id="search_input", classes="form-input"),
            Static("", id="search_feedback"),
            Button("BUSCAR", id="execute_search"),
            classes="search-form-container"
        )
        yield Static("Resultados:", id="results_title")
        yield DataTable(id="search_results_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "execute_search":
            self.execute_search()

    def execute_search(self) -> None:
        search_term = self.query_one("#search_input", Input).value.strip()
        table = self.query_one(DataTable)
        feedback = self.query_one("#search_feedback")
        
        table.clear(columns=True)
        feedback.update("")
        
        if not search_term:
            feedback.update(" [b]ERROR:[/b] Ingrese un término de búsqueda.")
            return

        try:
            results = find_product_by_name_or_barcode(search_term)
            if not results:
                feedback.update(f" No se encontraron productos para '{search_term}'.")
                return

            headers = results[0].keys()
            table.add_columns(*headers)
            for row_dict in results:
                string_row = [str(item) for item in row_dict.values()]
                table.add_row(*string_row)

            feedback.update(f" Búsqueda exitosa. Se encontraron {len(results)} producto(s).")
        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")
            self.app.push_screen(NotificationScreen(f"Error en la búsqueda: {e}"))

# --- Pantalla Genérica para Listar Inventario ---
class InventoryViewerScreen(Screen):
    """Muestra una lista de productos utilizando una función de servicio específica."""

    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]
    
    def __init__(self, title: str, list_function, list_args=None, header_map: dict | None = None, **kwargs):
        super().__init__(**kwargs)
        self.screen_title = title
        self.list_function = list_function
        self.list_args = list_args if list_args is not None else []
        self.header_map = header_map

    def compose(self) -> ComposeResult:
        yield Header(name=self.screen_title) 
        yield Static("Cargando datos...", id="list_feedback")
        yield DataTable(id="inventory_table")
        yield Footer()

    def on_mount(self) -> None:
        self.load_data()

    def load_data(self) -> None:
        table = self.query_one(DataTable)
        feedback = self.query_one("#list_feedback", Static)
        
        table.clear(columns=True)
        table.cursor_type = "row"
        feedback.update("Cargando datos...")

        try:
            inventory_data = self.list_function(*self.list_args)

            if not inventory_data:
                feedback.update(f" No se encontraron registros para: [b]{self.screen_title}[/b].")
                table.add_column("Aviso")
                table.add_row("No hay datos disponibles.")
                return

            if self.header_map:
                headers = self.header_map.values()
                table.add_columns(*headers)
                original_keys = self.header_map.keys()
                for row_dict in inventory_data:
                    string_row = [str(row_dict.get(key, "N/A")) for key in original_keys]
                    table.add_row(*string_row)
            else:
                headers = inventory_data[0].keys()
                table.add_columns(*headers)
                for row_dict in inventory_data:
                    string_row = [str(item) for item in row_dict.values()]
                    table.add_row(*string_row)

            feedback.update(f" Se encontraron [b]{len(inventory_data)}[/b] registros.")
        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")
            self.app.push_screen(NotificationScreen(f"Error al listar: {e}"))

# --- Pantalla para Ver Productos por Categoría ---
class ViewByCategoryScreen(Screen):
    """Pantalla que permite seleccionar una categoría y luego muestra sus productos."""

    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Volver (ESC)")]
    categories_map: dict = {} 

    def compose(self) -> ComposeResult:
        yield Header(name="VER POR CATEGORÍA")
        yield Static("Seleccione una categoría para ver sus productos:", id="category_title")
        yield Static("Cargando categorías...", id="list_feedback")
        yield DataTable(id="category_list_table")
        yield Static("", id="products_title", classes="hidden")
        yield DataTable(id="products_by_category_table", classes="hidden")
        yield Footer()

    def on_mount(self) -> None:
        self.load_categories()
        table = self.query_one("#category_list_table", DataTable)
        table.cursor_type = "row"
        
    def load_categories(self) -> None:
        table = self.query_one("#category_list_table", DataTable)
        feedback = self.query_one("#list_feedback", Static)
        
        table.clear(columns=True)
        self.categories_map = {}
        feedback.update("Cargando categorías...")

        try:
            category_data = list_categories()
            if not category_data:
                feedback.update(" No se encontraron categorías en la base de datos.")
                table.add_column("Aviso")
                table.add_row("No hay categorías.")
                return

            table.add_column("ID", key="id")
            table.add_column("Nombre", key="name")
            table.add_column("Descripción", key="description")
            
            for category in category_data:
                category_id = category["id"]
                category_name = category["name"]
                self.categories_map[category_id] = category_name
                table.add_row(
                    category_id,
                    category_name,
                    category["description"] if category["description"] else "N/A",
                    key=str(category_id)
                )
            feedback.update(f" Se encontraron [b]{len(category_data)}[/b] categorías. Seleccione una.")
        except Exception as e:
            feedback.update(f" ERROR: {e}")
            self.app.push_screen(NotificationScreen(f"Error al listar categorías: {e}"))
            
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        category_id_key = event.row_key.value
        try:
            category_id = int(category_id_key) 
        except ValueError:
            self.app.push_screen(NotificationScreen(f"Error: La clave de categoría '{category_id_key}' no es un número válido."))
            return
            
        category_name = self.categories_map.get(category_id, "Desconocida")
        self.list_products_for_category(category_id, category_name)
        
    def list_products_for_category(self, category_id: int, category_name: str) -> None:
        products_table = self.query_one("#products_by_category_table", DataTable)
        products_title = self.query_one("#products_title", Static)
        
        products_table.clear(columns=True)
        products_table.remove_class("hidden")
        products_title.update(f"Cargando productos para: [b]{category_name}[/b]")
        products_title.remove_class("hidden")

        try:
            products_data = list_products_by_category(category_id)
            if not products_data:
                products_table.add_column("Aviso")
                products_table.add_row("No hay productos en esta categoría.")
                products_title.update(f"Productos en la Categoría [b]{category_name}[/b]: (0 encontrados)")
                return

            headers = products_data[0].keys()
            products_table.add_columns(*headers)
            for row_dict in products_data:
                string_row = [str(item) for item in row_dict.values()]
                products_table.add_row(*string_row)
                
            products_title.update(f"Productos en la Categoría [b]{category_name}[/b]: ({len(products_data)} encontrados)")
        except Exception as e:
            products_title.update(f"ERROR: No se pudo consultar la categoría {category_name}")
            products_table.add_column("Error")
            products_table.add_row(f"Detalle del error: {e}")
            self.app.push_screen(NotificationScreen(f"Error grave en el servicio: {e}"))

# --- Pantalla Menú de Modificación ---
class ModifyMenuScreen(Screen):
    """Pantalla de menú para seleccionar qué modificar (Producto o Categoría)."""
    CSS_PATH = "tui.css"
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

# --- Pantalla de Modificación de Categoría ---
class ModifyCategoryScreen(Screen):
    """Pantalla para modificar el nombre y descripción de categorías."""
    CSS_PATH = "tui.css"
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
        table.add_columns("ID", "Nombre", "Descripción")
        table.cursor_type = "row"
        
        try:
            cats = list_categories()
            self.categories_map = {}
            if cats:
                for c in cats:
                    table.add_row(c['id'], c['name'], c['description'] or "", key=str(c['id']))
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

# --- Pantalla de Modificación de Producto ---
class ModifyProductScreen(Screen):
    """Pantalla para buscar un producto y modificar sus detalles directamente."""
    CSS_PATH = "tui.css"
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
                Label("ID (No Modificable):"), Input(id="modify_id", classes="form-input", disabled=True),
                Label("Nombre del Producto:"), Input(placeholder="Ej: Leche Entera", id="name_input", classes="form-input"),
                Label("Código de Barras:"), Input(placeholder="Ej: 777123456 (Debe ser único)", id="barcode_input", classes="form-input"),
                Label("Categoría:"), Input(placeholder="Ej: Lácteos", id="category_input", classes="form-input"),
                Label("Unidad de Medida:"), Input(placeholder="Ej: unidad, kg, litro", id="unit_input", classes="form-input"),
                Label("Precio de Compra:"), Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price_input", classes="form-input"),
                Label("Precio de Venta:"), Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price_input", classes="form-input"),
                Label("Ganancia (Solo Lectura):"), Input(id="profit_input", classes="form-input", disabled=True),
                Label("Ubicación:"), Input(placeholder="Ej: Pasillo A", id="location_input", classes="form-input"),
                Label("Fecha Adquisición (YYYY-MM-DD):"), Input(placeholder="Ej: 2026-12-31", id="date_added_input", classes="form-input"),
                Label("Fecha de Vencimiento (YYYY-MM-DD):"), Input(placeholder="Ej: 2026-12-31", id="expiration_date_input", classes="form-input"),
                Label("Estado Activo (True/False):"), Input(placeholder="True o False", id="active_input", classes="form-input"),
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

        table.add_columns("ID", "Nombre", "Código de Barras", "Categoría", "Unidad", "Stock", "Precio Compra", "Precio Venta", "Ganancia", "Fecha Adquisición", "Fecha Expiración", "Ubicación", "Estado")
        table.cursor_type = "row"
        
        for p in results:
            table.add_row(
                p["id"], p["name"], p["barcode"], p["category_name"], p["unit"], p.get("quantity", "N/A"), p["purchase_price"], p["sale_price"], p["profit"], p["date_added"], p["expiration_date"], p["location"], p["active"],
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
        self.query_one("#modify_id", Input).value = str(data["id"])
        self.query_one("#profit_input", Input).value = str(data["profit"])
        
        purchase_date_obj = data["purchase_date"]
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

# --- Pantalla de Venta ---
class SaleScreen(Screen):
    """Pantalla de Terminal Punto de Venta (TPV) para registrar ventas."""
    CSS_PATH = "tui.css"
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
                    yield Input(placeholder="Buscar por Código de Barras...", id="sale_search_input")
                    yield Button("Buscar", id="sale_search_button", variant="primary")
                yield Static("Producto Encontrado:", id="sale_found_label", classes="hidden")
                yield Static("", id="sale_found_product", classes="sale-found-text")
                with Horizontal(classes="sale-group"):
                    yield Input(placeholder="Cant.", id="sale_quantity_input", value="1", disabled=True)
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
        table.add_columns("Producto", " ", "Cant.", "P. Unit.", "Subtotal")
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
        if self.current_product["active"] != "Activo":
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

# --- Pantalla de Historial ---
class HistoryScreen(Screen):
    """Pantalla con las opciones para ver el historial de ventas."""
    CSS_PATH = "tui.css"
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
                "sale_id": "ID",
                "timestamp": "Fecha de Venta",
                "product": "Nombre Producto",
                "barcode": "Código de Barras",
                "quantity": "Cantidad",
                "unit_price": "Precio Unidad",
                "subtotal": "Precio Total"
            }
            self.app.push_screen(InventoryViewerScreen(title="HISTORIAL POR VENTAS (DETALLADO)", list_function=list_sales_history, header_map=sales_map))
        elif event.button.id == "history_date":
            date_map = {
                "date": "Fecha de Venta",
                "total_sales": "Total de Ventas",
                "total_amount": "Monto total"
            }
            self.app.push_screen(InventoryViewerScreen(title="RESUMEN DE VENTAS POR FECHA", list_function=sales_summary_by_date, header_map=date_map))

# --- Pantalla Principal (El Menú) ---
class MainMenuScreen(Screen):
    """La pantalla principal que muestra el menú de opciones."""
    CSS_PATH = "tui.css"
    BINDINGS = [Binding("escape", "quit_app", "Salir (ESC)")]

    def compose(self) -> ComposeResult:
        yield Static("MENÚ PRINCIPAL", id="main-title")
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

# --- La Aplicación Principal ---
class InventoryTUI(App):
    """La aplicación TUI principal."""
    CSS_PATH = "tui.css"
    SCREENS = {
        "main_menu": MainMenuScreen,
        "notify": NotificationScreen,
        "add_menu": AddScreen,
        "add_product_form": AddProductFormScreen,
        "add_stock_form": AddStockFormScreen,
        "view_menu": ViewScreen,
        "search_product_screen": SearchProductScreen,
        "view_by_category_screen": ViewByCategoryScreen,
        "modify_menu_screen": ModifyMenuScreen,
        "modify_category_screen": ModifyCategoryScreen,
        "modify_product_screen": ModifyProductScreen,
        "sale_screen": SaleScreen,
        "history_menu": HistoryScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("main_menu")

if __name__ == "__main__":
    app = InventoryTUI()
    app.run()