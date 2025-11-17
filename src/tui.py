# src/tui.py

import datetime
from decimal import Decimal
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, Button, DataTable, Static, Input, Label, Log
from textual.containers import Vertical, Horizontal, ScrollableContainer, Grid
from textual.binding import Binding

# --- Importar la lógica de negocio y la BD ---
from backend.models import init_db
from backend.services import (
    add_product,
    record_purchase,
    record_sale,
    list_products_inventory,
    find_product_by_name_or_barcode,
    list_expiring_products,
    list_sales_history,
    sales_summary_by_date,
    list_available_products,
    list_out_of_stock_products,
    list_categories,
    list_products_by_category,
    toggle_product_status,
    update_product_details,
    apply_expiring_product_offer,
    get_product_details_by_id
)

# --- Inicializar la BD al arrancar ---
print("Inicializando base de datos...")
init_db()
print("Base de datos lista.")


# --- Pantalla de Notificación (Modal) ---
# Usaremos esta pantalla como un "pop-up" para los botones
# que aún no tienen una interfaz asignada.
class NotificationScreen(ModalScreen):
    """Una pantalla modal para mostrar un mensaje al usuario."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        # Usamos un contenedor Vertical para centrar el botón
        yield Vertical(
            Static(self.message, id="message"),
            Button("Aceptar", variant="primary", id="accept_button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Cierra la modal (pop-up)
        self.dismiss()

# --- Pantalla Menú de Agregados ---
class AddScreen(Screen):
    """Pantalla con las opciones para agregar productos o stock."""

    CSS_PATH = "tui.css"

    # Definir atajos de teclado
    BINDINGS = [
        ("escape", "dismiss", "Volver (ESC)"), # 'dismiss' cierra la pantalla actual
    ]

    def compose(self) -> ComposeResult:
        """Define el layout de la pantalla de agregados."""
        
        yield Static("AGREGAR", id="main-title") # Reutilizamos el estilo del título
        
        # Usaremos un Vertical container para que los botones se apilen (como en la imagen)
        yield Vertical(
            Button("AGREGAR UN NUEVO PRODUCTO", id="add_new_product"),
            Button("AGREGAR ESTOCK A UN PRODUCTO", id="add_stock"),
            Button("SALIR", id="exit_add_menu"),
            id="add-menu-container"
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejador de eventos para los botones del menú de agregados."""
        
        if event.button.id == "exit_add_menu":
            self.dismiss()

        elif event.button.id == "add_new_product":
            # ABRIMOS EL FORMULARIO
            self.app.push_screen("add_product_form")
            
        elif event.button.id == "add_stock":
            # ABRIMOS EL FORMULARIO DE ENTRADA DE STOCK
            self.app.push_screen("add_stock_form")


# --- Pantalla Formulario para Añadir Producto ---
class AddProductFormScreen(Screen):
    """Formulario para agregar un nuevo producto y su stock inicial (Opción 1)."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Cancelar (ESC)"), 
    ]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR UN NUEVO PRODUCTO") # Usaremos Header para el título
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
            Input(placeholder="Ej: Pasillo A", id="location", classes="form-input", value=""), # Campo opcional
            
            Label("Precio de Compra:"),
            Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price", classes="form-input"),
            
            Label("Precio de Venta:"),
            Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price", classes="form-input"),
            
            Label("Cantidad Inicial en Stock:"),
            Input(placeholder="Ej: 100 (Solo números enteros)", id="initial_quantity", classes="form-input"),
            
            Label("Fecha de Vencimiento (YYYY-MM-DD - Opcional):"),
            Input(placeholder="Ej: 2026-12-31 (Dejar vacío si no aplica)", id="expiration_date", classes="form-input", value=""),

            Static("", id="form_feedback"), # Para mostrar errores de validación o mensajes
            
            Grid(
                Button("GUARDAR", id="save_product"),
                Button("CANCELAR", id="cancel_product"),
                id="form-buttons-grid"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja el guardado o la cancelación del formulario."""
        
        if event.button.id == "cancel_product":
            self.dismiss()
        
        elif event.button.id == "save_product":
            self.handle_save()

    def handle_save(self) -> None:
        """Recolecta, valida y guarda los datos del producto."""
        
        feedback = self.query_one("#form_feedback")
        
        try:
            # 1. Recolectar datos y limpiar espacios
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
            
            # 2. Validación básica de campos requeridos
            if not all([data["name"], data["barcode"], data["category_name"], data["unit"], data["purchase_price"], data["sale_price"], data["initial_quantity"]]):
                feedback.update(" [b]ERROR:[/b] Los campos principales no pueden estar vacíos.")
                return

            # 3. Conversión de tipos y validación de formato
            try:
                purchase_price_f = float(data["purchase_price"])
                sale_price_f = float(data["sale_price"])
                initial_quantity_i = int(data["initial_quantity"])
            except ValueError:
                feedback.update(" [b]ERROR:[/b] Precios y Cantidad deben ser números válidos.")
                return

            # 4. Validación de fecha
            exp_date = None
            if data["expiration_date"]:
                try:
                    # Intenta parsear la fecha YYYY-MM-DD
                    exp_date = datetime.datetime.strptime(data["expiration_date"], '%Y-%m-%d').date()
                except ValueError:
                    feedback.update(" [b]ERROR:[/b] Formato de fecha de vencimiento inválido. Use YYYY-MM-DD.")
                    return

            # 5. Llamar al servicio de backend
            success, message = add_product(
                data["name"], data["barcode"], data["category_name"], data["unit"], data["location"],
                purchase_price_f, sale_price_f, initial_quantity_i, exp_date
            )
            
            # 6. Mostrar resultado
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.dismiss() # Cierra el formulario si el guardado fue exitoso

        except Exception as e:
            # Este catch atrapa errores de BD (IntegrityError, etc.)
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}. ¿El código de barras ya existe?")
            self.app.push_screen(NotificationScreen(f"Error: {e}"))

# --- Pantalla Formulario para Agregar Stock (Compra) ---
class AddStockFormScreen(Screen):
    """Formulario para registrar una entrada de stock (Compra) - Opción 2."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Cancelar (ESC)"), 
    ]

    def compose(self) -> ComposeResult:
        yield Header(name="AGREGAR ESTOCK A UN PRODUCTO")
        yield ScrollableContainer(
            Static("Ingrese el código de barras y la cantidad de stock a agregar:", id="form-instruction"),
            
            Label("Código de Barras del Producto:"),
            Input(placeholder="Ej: 777123456", id="barcode", classes="form-input"),
            
            Label("Cantidad a Agregar:"),
            Input(placeholder="Ej: 50 (Solo números enteros)", id="quantity", classes="form-input"),

            # --- CORRECCIÓN ---
            # Se añade el campo de precio de compra, requerido por services.py
            Label("Nuevo Precio de Compra:"),
            Input(placeholder="Ej: 5.50 (Se actualizará en el sistema)", id="purchase_price", classes="form-input"),
            
            # Se elimina el campo "Referencia" que no se usa en record_purchase
            # --- FIN CORRECCIÓN ---

            Static("", id="form_feedback"),
            
            Grid(
                Button("REGISTRAR ENTRADA", id="register_stock"),
                Button("CANCELAR", id="cancel_stock"),
                id="form-buttons-grid"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja el registro o la cancelación del formulario."""
        if event.button.id == "cancel_stock":
            self.dismiss()
        
        elif event.button.id == "register_stock":
            self.handle_save()

    def handle_save(self) -> None:
        """Recolecta, valida y registra la entrada de stock."""
        feedback = self.query_one("#form_feedback")
        
        try:
            # 1. Recolectar datos
            barcode = self.query_one("#barcode", Input).value.strip()
            quantity_str = self.query_one("#quantity", Input).value.strip()
            # --- CORRECCIÓN: Obtener el precio ---
            price_str = self.query_one("#purchase_price", Input).value.strip()
            
            # 2. Validación de campos requeridos
            # --- CORRECCIÓN: Validar el precio ---
            if not all([barcode, quantity_str, price_str]):
                feedback.update(" [b]ERROR:[/b] Código de Barras, Cantidad y Precio son obligatorios.")
                return

            # 3. Conversión de tipos y validación de cantidad
            try:
                quantity_i = int(quantity_str)
                # --- CORRECCIÓN: Convertir precio ---
                purchase_price_f = float(price_str)
                
                if quantity_i <= 0 or purchase_price_f < 0:
                    feedback.update(" [b]ERROR:[/b] La cantidad debe ser positiva y el precio no puede ser negativo.")
                    return
            except ValueError:
                feedback.update(" [b]ERROR:[/b] La Cantidad o el Precio no son números válidos.")
                return
            
            # 4. Llamar al servicio de backend record_purchase
            # --- CORRECCIÓN CLAVE ---
            # Se usan los nombres de argumentos correctos:
            # 'product_barcode' en lugar de 'barcode'
            # 'purchase_price' en lugar de 'reference'
            success, message = record_purchase(
                product_barcode=barcode,
                quantity=quantity_i,
                purchase_price=purchase_price_f
            )
            # --- FIN CORRECCIÓN CLAVE ---
            
            # 5. Mostrar resultado
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.dismiss() # Cierra el formulario si el registro fue exitoso

        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}. Verifique el código de barras.")
            # También mostramos el error en un pop-up por si es grave
            self.app.push_screen(NotificationScreen(f"Error: {e}"))


# --- Pantalla Menú de Visualización (VER) ---
class ViewScreen(Screen):
    """Pantalla con las opciones para visualizar reportes e inventario."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Volver (ESC)"), # 'dismiss' cierra la pantalla actual
    ]

    def compose(self) -> ComposeResult:
        """Define el layout de la pantalla de visualización."""
        
        yield Header(name="VER") # Título
        
        # Usamos un Vertical container para apilar los 8 botones
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
        """Manejador de eventos para los botones del menú de visualización."""
        
        if event.button.id == "exit_view_menu":
            self.dismiss() # Regresa al Menú Principal
        
        elif event.button.id == "view_search": # ABRIMOS LA PANTALLA DE BÚSQUEDA
            self.app.push_screen("search_product_screen")
            
        elif event.button.id == "view_active": # Usamos la pantalla genérica: list_products_inventory(1)
            self.app.push_screen(InventoryViewerScreen(
                title="PRODUCTOS ACTIVOS", 
                list_function=list_products_inventory, 
                list_args=[1] # El argumento 1 es para productos activos
            ))
            
        elif event.button.id == "view_inactive": # Usamos la misma pantalla genérica: list_products_inventory(2)
            self.app.push_screen(InventoryViewerScreen(
                title="PRODUCTOS INACTIVOS", 
                list_function=list_products_inventory, 
                list_args=[2] # El argumento 2 es para productos inactivos
            ))

        elif event.button.id == "view_available": #Llama a list_available_products()
            self.app.push_screen(InventoryViewerScreen(
                title="PRODUCTOS CON STOCK", 
                list_function=list_available_products
            ))

        elif event.button.id == "view_out_of_stock": #Llama a list_out_of_stock_products()
            self.app.push_screen(InventoryViewerScreen(
                title="PRODUCTOS SIN STOCK", 
                list_function=list_out_of_stock_products
            ))
            
        elif event.button.id == "view_expiring": #Llama a list_expiring_products(days_limit)
            DAYS = 10 # Usaremos 10 días como límite por defecto
            self.app.push_screen(InventoryViewerScreen(
                title=f"PROX. A VENCER ({DAYS} DÍAS)", 
                list_function=list_expiring_products,
                list_args=[DAYS]
            ))
            
        elif event.button.id == "view_by_category": #Abre la pantalla de selector de categoría
            self.app.push_screen("view_by_category_screen")

# --- Pantalla para Buscar Producto (Formulario + Resultados) ---
class SearchProductScreen(Screen):
    """Pantalla para buscar un producto por nombre o código de barras (Opción 9)."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Volver (ESC)"), 
    ]

    def compose(self) -> ComposeResult:
        """Define el layout de la pantalla de búsqueda."""
        
        yield Header(name="BUSCAR PRODUCTO")
        
        # 1. Contenedor del Formulario de Búsqueda
        yield Vertical(
            Label("Ingrese el Nombre o Código de Barras a buscar:"),
            Input(placeholder="Ej: Leche o 777123456", id="search_input", classes="form-input"),
            Static("", id="search_feedback"), # Para mensajes de error/resultado
            Button("BUSCAR", id="execute_search"),
            classes="search-form-container"
        )
        
        # 2. Tabla de Resultados (Inicialmente vacía)
        yield Static("Resultados:", id="results_title")
        yield DataTable(id="search_results_table")
        
        yield Footer()

    def on_mount(self) -> None:
        """Configura la tabla al cargar la pantalla."""
        table = self.query_one(DataTable)
        table.cursor_type = "row" # Permite seleccionar filas

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejador de eventos."""
        
        if event.button.id == "execute_search":
            self.execute_search()

    def execute_search(self) -> None:
        """Realiza la búsqueda llamando al servicio y actualiza la tabla."""
        
        search_term = self.query_one("#search_input", Input).value.strip()
        table = self.query_one(DataTable)
        feedback = self.query_one("#search_feedback")
        
        # Limpiamos resultados anteriores y mensajes
        table.clear(columns=True)
        feedback.update("")
        
        if not search_term:
            feedback.update(" [b]ERROR:[/b] Ingrese un término de búsqueda.")
            return

        try:
            # Llamamos al servicio de backend
            results = find_product_by_name_or_barcode(search_term)

            if not results:
                feedback.update(f" No se encontraron productos para '{search_term}'.")
                return

            # --- Llenar la Tabla ---
            # 1. Columnas (usando las claves del primer resultado)
            headers = results[0].keys()
            table.add_columns(*headers)
            
            # 2. Filas
            for row_dict in results:
                # Convertir todos los valores a string para la tabla
                string_row = [str(item) for item in row_dict.values()]
                table.add_row(*string_row)

            feedback.update(f" Búsqueda exitosa. Se encontraron {len(results)} producto(s).")
            
        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")
            self.app.push_screen(NotificationScreen(f"Error en la búsqueda: {e}"))

# --- Pantalla Genérica para Listar Inventario (Reutilizable) ---
class InventoryViewerScreen(Screen):
    """Muestra una lista de productos utilizando una función de servicio específica."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Volver (ESC)"), 
    ]
    
    # 1. Constructor para recibir la función y el título
    def __init__(self, title: str, list_function, list_args=None, header_map: dict | None = None, **kwargs): # <-- AÑADIR header_map
        super().__init__(**kwargs)
        self.screen_title = title
        self.list_function = list_function # Ej: list_products_inventory
        self.list_args = list_args if list_args is not None else [] # Ej: [1] o [2]
        self.header_map = header_map #

    def compose(self) -> ComposeResult:
        # Usamos el título que pasamos en el constructor
        yield Header(name=self.screen_title) 
        
        yield Static("Cargando datos...", id="list_feedback")
        yield DataTable(id="inventory_table")
        
        yield Footer()

    def on_mount(self) -> None:
        """Llama a la función de servicio y llena la tabla."""
        self.load_data()

    def load_data(self) -> None:
        """Llama al servicio de backend y actualiza la tabla."""
        
        table = self.query_one(DataTable)
        feedback = self.query_one("#list_feedback", Static)
        
        table.clear(columns=True)
        table.cursor_type = "row"
        feedback.update("Cargando datos...")

        try:
            # 2. Llamamos a la función genérica con sus argumentos
            inventory_data = self.list_function(*self.list_args)

            if not inventory_data:
                feedback.update(f" No se encontraron registros para: [b]{self.screen_title}[/b].")
                table.add_column("Aviso")
                table.add_row("No hay datos disponibles.")
                return

            # --- INICIO DE LA MODIFICACIÓN ---
            
            # 3. Llenar la Tabla (usando el header_map si existe)
            if self.header_map:
                # A. Usar el mapa para las columnas (en el orden definido)
                headers = self.header_map.values()
                table.add_columns(*headers)
                
                # B. Obtener las claves originales (para leer el dict de datos)
                original_keys = self.header_map.keys()
                
                for row_dict in inventory_data:
                    # C. Construir la fila en el orden del mapa
                    string_row = [str(row_dict.get(key, "N/A")) for key in original_keys]
                    table.add_row(*string_row)
            
            else:
                # D. Comportamiento anterior (si no hay mapa, usar keys)
                headers = inventory_data[0].keys()
                table.add_columns(*headers)
                
                for row_dict in inventory_data:
                    string_row = [str(item) for item in row_dict.values()]
                    table.add_row(*string_row)
            
            # --- FIN DE LA MODIFICACIÓN ---

            feedback.update(f" Se encontraron [b]{len(inventory_data)}[/b] registros.")
            
        except Exception as e:
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")
            self.app.push_screen(NotificationScreen(f"Error al listar: {e}"))

# --- Pantalla para Ver Productos por Categoría (Opción 6) ---
class ViewByCategoryScreen(Screen):
    """Pantalla que permite seleccionar una categoría y luego muestra sus productos."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Volver (ESC)"), 
    ]
    
    # 1. Almacenará el ID de la categoría seleccionada (para el manejo de eventos)
    # y la lista de categorías (para mapear el nombre al ID).
    categories_map: dict = {} 

    def compose(self) -> ComposeResult:
        """Define el layout: Título, lista de categorías y tabla de resultados (oculta)."""
        
        yield Header(name="VER POR CATEGORÍA")
        
        yield Static("Seleccione una categoría para ver sus productos:", id="category_title")
        yield Static("Cargando categorías...", id="list_feedback")
        
        # Tabla principal para listar las categorías
        yield DataTable(id="category_list_table")
        
        # Tabla secundaria para mostrar los productos de la categoría seleccionada
        yield Static("", id="products_title", classes="hidden") # Inicialmente oculta
        yield DataTable(id="products_by_category_table", classes="hidden") # Inicialmente oculta
        
        yield Footer()

    def on_mount(self) -> None:
        """Llama al servicio para cargar la lista de categorías."""
        self.load_categories()
        table = self.query_one("#category_list_table", DataTable)
        table.cursor_type = "row"
        
    def load_categories(self) -> None:
        """Llama al servicio de backend para obtener y listar las categorías."""
        
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

            # --- Llenar la Tabla de Categorías ---
            table.add_column("ID", key="id")
            table.add_column("Nombre", key="name")
            table.add_column("Descripción", key="description")
            
            # Llenar filas y mapear ID a nombre
            for category in category_data:
                category_id = category["id"]
                category_name = category["name"]
                self.categories_map[category_id] = category_name # Guardamos el mapeo

                table.add_row(
                    category_id,
                    category_name,
                    category["description"] if category["description"] else "N/A",
                    key=category_id # Usamos el ID de la categoría como clave de la fila
                )

            feedback.update(f" Se encontraron [b]{len(category_data)}[/b] categorías. Seleccione una.")
            
        except Exception as e:
            feedback.update(f" ERROR: {e}")
            self.app.push_screen(NotificationScreen(f"Error al listar categorías: {e}"))
            
    # 2. Manejar la selección de fila para listar los productos
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Se activa cuando el usuario selecciona una categoría en la tabla."""
        
        # 1. Obtener la clave de la fila. Esta clave es el ID de la categoría que usamos
        #    al llenar la tabla (table.add_row(..., key=category_id)).
        category_id_key = event.row_key.value
        
        try:
            # 2. CONVERSIÓN CRÍTICA: Aseguramos que sea un entero para el servicio de backend.
            category_id = int(category_id_key) 
        except ValueError:
            # En caso de error inesperado, mostramos un mensaje
            self.app.push_screen(NotificationScreen(f"Error: La clave de categoría '{category_id_key}' no es un número válido."))
            return
            
        # 3. Obtener el nombre
        category_name = self.categories_map.get(category_id, "Desconocida")
        
        # 4. Llamar al listado
        self.list_products_for_category(category_id, category_name)
        
    def list_products_for_category(self, category_id: int, category_name: str) -> None:
        """Llama al servicio para listar productos de una categoría y llena la tabla de resultados."""
        
        products_table = self.query_one("#products_by_category_table", DataTable)
        products_title = self.query_one("#products_title", Static)
        
        products_table.clear(columns=True)
        products_table.remove_class("hidden")
        
        # Retroalimentación de carga
        products_title.update(f"Cargando productos para: [b]{category_name}[/b]")
        products_title.remove_class("hidden")

        try:
            # CAMBIO CLAVE: Usamos la función basada en ID.
            products_data = list_products_by_category(category_id)

            if not products_data:
                products_table.add_column("Aviso")
                products_table.add_row("No hay productos en esta categoría.")
                products_title.update(f"Productos en la Categoría [b]{category_name}[/b]: (0 encontrados)")
                return

            # --- Llenar la Tabla de Productos ---
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

class ModifyProductScreen(Screen):
    """
    Pantalla para buscar un producto y modificar sus detalles directamente.
    """
    CSS_PATH = "tui.css"
    
    BINDINGS = [
        ("escape", "dismiss", "Menú (ESC)"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.current_product_id: int | None = None
        self.current_product_data: dict | None = None

    def show_form(self) -> None:
        """Muestra el formulario oculto."""
        self.query_one("#modify-form-title", Static).remove_class("hidden")
        self.query_one("#modify-form-grid", Grid).remove_class("hidden")
        self.query_one("#save_modifications", Button).remove_class("hidden")

    def hide_form(self) -> None:
        """Oculta el formulario."""
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
            
            # Tabla de resultados (inicialmente vacía)
            DataTable(id="modify_results_table"),

            # ------------------------------------------------------------------
            # Formulario de Modificación - Inicialmente oculto
            # ------------------------------------------------------------------
            Static("--- Detalles del Producto Seleccionado ---", id="modify-form-title", classes="hidden"),
            Grid(
                # ID (Solo lectura)
                Label("ID (No Modificable):"),
                Input(id="modify_id", classes="form-input", disabled=True),
                
                # Nombre
                Label("Nombre del Producto:"),
                Input(placeholder="Ej: Leche Entera", id="name_input", classes="form-input"),
                
                # Barcode
                Label("Código de Barras:"),
                Input(placeholder="Ej: 777123456 (Debe ser único)", id="barcode_input", classes="form-input"),
                
                # Categoría
                Label("Categoría:"),
                Input(placeholder="Ej: Lácteos", id="category_input", classes="form-input"),
                
                # Unidad
                Label("Unidad de Medida:"),
                Input(placeholder="Ej: unidad, kg, litro", id="unit_input", classes="form-input"),

                # P. Compra
                Label("Precio de Compra:"),
                Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price_input", classes="form-input"),
                
                # P. Venta
                Label("Precio de Venta:"),
                Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price_input", classes="form-input"),
                
                # Profit (Solo lectura)
                Label("Ganancia (Solo Lectura):"),
                Input(id="profit_input", classes="form-input", disabled=True),

                # Ubicación
                Label("Ubicación:"),
                Input(placeholder="Ej: Pasillo A", id="location_input", classes="form-input"),

                # Fecha de Adquisición
                Label("Fecha Adquisición (YYYY-MM-DD):"),
                Input(placeholder="Ej: 2026-12-31 (Dejar vacío si no aplica)", id="date_added_input", classes="form-input"),

                # Fecha Vencimiento
                Label("Fecha de Vencimiento (YYYY-MM-DD):"),
                Input(placeholder="Ej: 2026-12-31 (Dejar vacío si no aplica)", id="expiration_date_input", classes="form-input"),
                
                # Estado
                Label("Estado Activo (True/False):"),
                Input(placeholder="True o False", id="active_input", classes="form-input"),

                # Botón de Guardar
                Button("GUARDAR CAMBIOS", id="save_modifications", variant="primary", classes="hidden"),

                id="modify-form-grid",
                classes="hidden" # El Grid completo se oculta inicialmente
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja la búsqueda y el guardado."""
        if event.button.id == "run_modify_search":
            self.run_search()
        elif event.button.id == "save_modifications":
            self.handle_save()
    
    # ----------------------------------------------------------
    # LÓGICA DE BÚSQUEDA
    # ----------------------------------------------------------
    def run_search(self) -> None:
        """Ejecuta la búsqueda y llena la DataTable."""
        search_query = self.query_one("#modify_search_input", Input).value.strip()
        table = self.query_one("#modify_results_table", DataTable)
        feedback = self.query_one("#modify_search_feedback", Static)
        
        # Limpiar tabla y estado anterior
        feedback.update("")
        self.current_product_data = None
        self.hide_form() # Ocultar el formulario al iniciar una nueva búsqueda
        # FIX: Usar clear(columns=True) para borrar columnas y filas
        table.clear(columns=True)

        if not search_query:
            feedback.update(" [b]ADVERTENCIA:[/b] Ingrese un criterio de búsqueda.")
            return

        results = find_product_by_name_or_barcode(search_query) # Asumimos que esta función devuelve una lista de dicts
        
        if not results:
            feedback.update(" [b]INFORMACIÓN:[/b] No se encontraron productos.")
            return

        table.add_columns("ID", "Nombre", "Código de Barras", "Categoría", "Unidad", "Stock", "Precio Compra", "Precio Venta", "Ganancia", "Fecha Adquisición", "Fecha Expiración", "Ubicación", "Estado")
        table.cursor_type = "row" # Para permitir la selección
        
        for p in results:
            # Usamos el ID del producto como clave (key) para identificar la fila
            table.add_row(
                p["id"], p["name"], p["barcode"], p["category_name"], p["unit"], p.get("quantity", "N/A"), p["purchase_price"], p["sale_price"], p["profit"], p["date_added"], p["expiration_date"], p["location"], p["active"],
                key=str(p["id"])
            )
        
        feedback.update(f" [b]ÉXITO:[/b] {len(results)} producto(s) encontrado(s). Seleccione uno para modificar.")
    
    # ----------------------------------------------------------
    # LÓGICA DE CARGA DE DATOS (Al seleccionar fila)
    # ----------------------------------------------------------
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Cuando el usuario selecciona la fila, carga los datos en el formulario."""
        
        try:
            # 1. Obtener el ID del producto (usando la clave de la fila)
            product_id = int(event.row_key.value)
            self.current_product_id = product_id

            # 2. Obtener todos los detalles del producto (usando la función de services.py)
            product_data = get_product_details_by_id(product_id)
            if not product_data:
                self.query_one("#modify_search_feedback", Static).update(f" [b]ERROR:[/b] Detalles para ID {product_id} no encontrados.")
                self.hide_form()
                return
            
            self.current_product_data = product_data
            
            # 3. Mostrar el formulario y cargar los datos
            self.show_form()
            self.populate_form(product_data)
            
            self.query_one("#modify_search_feedback", Static).update(f" [b]PRODUCTO CARGADO:[/b] '{product_data['name']}'. Modifique los campos y Guarde.")

        except ValueError:
            self.query_one("#modify_search_feedback", Static).update(" [b]ERROR:[/b] El ID de la fila no es válido.")
        except Exception as e:
            self.query_one("#modify_search_feedback", Static).update(f" [b]ERROR INESPERADO:[/b] {e}")


    def populate_form(self, data: dict) -> None:
        """Rellena los campos de entrada con los datos del diccionario."""
        
        # Campos de solo lectura
        self.query_one("#modify_id", Input).value = str(data["id"])
        self.query_one("#profit_input", Input).value = str(data["profit"])

        # --- FIX: Formatear la fecha de adquisición ---
        purchase_date_obj = data["purchase_date"]
        if purchase_date_obj:
            # Asegura que sea solo 'YYYY-MM-DD'
            purchase_date_str = purchase_date_obj.strftime('%Y-%m-%d')
        else:
            purchase_date_str = "" # Usar vacío si no hay fecha
            
        self.query_one("#date_added_input", Input).value = purchase_date_str
        # --- FIN FIX ---

        # Campos modificables
        self.query_one("#name_input", Input).value = data["name"]
        self.query_one("#barcode_input", Input).value = data["barcode"]
        self.query_one("#category_input", Input).value = data["category_name"]
        self.query_one("#unit_input", Input).value = data["unit"]
        self.query_one("#location_input", Input).value = data["location"] if data["location"] else ""
        
        self.query_one("#purchase_price_input", Input).value = str(data["purchase_price"])
        self.query_one("#sale_price_input", Input).value = str(data["sale_price"])
        
        # --- FIX: Formatear la fecha de vencimiento (por consistencia) ---
        exp_date_obj = data["expiration_date"]
        if exp_date_obj:
            exp_date_str = exp_date_obj.strftime('%Y-%m-%d')
        else:
            exp_date_str = ""
            
        self.query_one("#expiration_date_input", Input).value = exp_date_str
        # --- FIN FIX ---
        
        self.query_one("#active_input", Input).value = str(data["active"])

    # ----------------------------------------------------------
    # LÓGICA DE GUARDADO
    # ----------------------------------------------------------
    def handle_save(self) -> None:
        """Recolecta, valida y guarda los datos modificados llamando a services.py."""
        
        if not self.current_product_id:
            self.query_one("#modify_search_feedback", Static).update(" [b]ERROR:[/b] No hay producto seleccionado para guardar.")
            return

        try:
            # Recolectar datos del formulario (incluida la nueva fecha)
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
                # --- CAMPO AÑADIDO ---
                "date_added": self.query_one("#date_added_input", Input).value.strip(),
            }
            
            # Validación de campos (incluida la nueva fecha)
            if not all([data["name"], data["barcode"], data["category_name"], data["unit"], 
                        data["purchase_price"], data["sale_price"], data["active"], 
                        data["date_added"]]): # <- Añadido data["date_added"]
                self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] Los campos principales (incluida Fecha Adquisición) no pueden estar vacíos."))
                return

            purchase_price_f = float(data["purchase_price"])
            sale_price_f = float(data["sale_price"])
            active_status = data["active"].capitalize()

            if active_status not in ["True", "False"]:
                self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] El campo 'Estado Activo' debe ser 'True' o 'False'."))
                return

            # --- VALIDACIÓN AÑADIDA ---
            # Validar la fecha de adquisición (debe tener formato correcto)
            try:
                datetime.datetime.strptime(data["date_added"], '%Y-%m-%d').date()
            except ValueError:
                self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] Formato de Fecha de Adquisición inválido. Use YYYY-MM-DD."))
                return
            # --- FIN VALIDACIÓN ---


            # Llamar al servicio de backend para actualizar (enviando el nuevo dato)
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
                # --- CAMPO AÑADIDO ---
                date_added_str=data["date_added"],
                active_status=active_status
            )
            
            # Mostrar resultado
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.hide_form()
                self.query_one("#modify_results_table", DataTable).clear()
                self.query_one("#modify_search_input", Input).value = ""

        except ValueError:
            self.app.push_screen(NotificationScreen(" [b]ERROR:[/b] Los precios son inválidos."))
        except Exception as e:
            self.app.push_screen(NotificationScreen(f" [b]ERROR INESPERADO:[/b] {e}"))

class SaleScreen(Screen):
    """Pantalla de Terminal Punto de Venta (TPV) para registrar ventas."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Cancelar Venta (ESC)"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # 1. Estado de la pantalla
        self.cart: list[dict] = [] # El carrito de compras
        self.current_product: dict | None = None # El producto buscado
        self.total_sale: Decimal = Decimal("0.0")
        self.selected_cart_row: int | None = None 

    def compose(self) -> ComposeResult:
        """Define el layout de la pantalla de venta."""
        yield Header(name="REGISTRAR VENTA (TPV)")
        
        # Usaremos un Grid para organizar la pantalla
        with Grid(id="sale-grid"):
            
            # --- Columna Izquierda (Búsqueda y Carrito) ---
            with Vertical(id="sale-left-pane"):
                yield Static("1. Buscar Producto", classes="sale-subtitle")
                
                # Grupo de Búsqueda
                with Horizontal(classes="sale-group"):
                    # --- CORRECCIÓN ---
                    yield Input(placeholder="Buscar por Código de Barras...", id="sale_search_input")
                    yield Button("Buscar", id="sale_search_button", variant="primary")
                    # --- FIN CORRECCIÓN ---

                # Grupo para Añadir (inicialmente deshabilitado)
                yield Static("Producto Encontrado:", id="sale_found_label", classes="hidden")
                yield Static("", id="sale_found_product", classes="sale-found-text") # <-- yield ya estaba aquí
                
                with Horizontal(classes="sale-group"):
                    # --- CORRECCIÓN ---
                    yield Input(placeholder="Cant.", id="sale_quantity_input", value="1", disabled=True)
                    yield Button("Añadir al Carrito", id="sale_add_to_cart_button", disabled=True)
                    # --- FIN CORRECCIÓN ---
                
                # Feedback
                yield Log(id="sale_feedback_log", max_lines=10)

            # --- Columna Derecha (Carrito y Total) ---
            with Vertical(id="sale-right-pane"):
                yield Static("2. Carrito de Compras", classes="sale-subtitle")
                yield DataTable(id="sale_cart_table")
                yield Button("Quitar Producto Seleccionado", id="sale_remove_item_button", variant="error", disabled=True)
                # Total
                yield Static(f"TOTAL: Bs {self.total_sale:.2f}", id="sale_total_display")
                
                # Acciones Finales
                with Horizontal(classes="sale-group"):
                    # --- CORRECCIÓN ---
                    yield Button("CANCELAR VENTA", id="sale_cancel_button", variant="error")
                    yield Button("FINALIZAR VENTA", id="sale_finalize_button", variant="success")
                    # --- FIN CORRECCIÓN ---

        yield Footer()

    def on_mount(self) -> None:
        """Configura la tabla del carrito al cargar la pantalla."""
        table = self.query_one("#sale_cart_table", DataTable)
        table.add_columns("Producto", "Cant.", "P. Unit.", "Subtotal")
        table.cursor_type = "row"
        self.log_message("Sistema TPV listo. Busque un producto para comenzar.")

    # --- Helpers de UI ---

    def log_message(self, message: str) -> None:
        """Añade un mensaje al log de feedback."""
        self.query_one("#sale_feedback_log", Log).write_line(message)

    def enable_add_controls(self, enabled: bool) -> None:
        """Habilita o deshabilita los controles para añadir al carrito."""
        self.query_one("#sale_quantity_input", Input).disabled = not enabled
        self.query_one("#sale_add_to_cart_button", Button).disabled = not enabled
        self.query_one("#sale_found_label", Static).set_class(not enabled, "hidden")

    def clear_search_state(self) -> None:
        """Limpia el estado de búsqueda después de añadir al carrito."""
        self.current_product = None
        self.query_one("#sale_search_input", Input).value = ""
        self.query_one("#sale_quantity_input", Input).value = "1"
        self.query_one("#sale_found_product", Static).update("")
        self.enable_add_controls(False)
        self.query_one("#sale_search_input", Input).focus()

    def update_cart_display(self) -> None:
        """Refresca la tabla del carrito con los datos de self.cart."""
        table = self.query_one("#sale_cart_table", DataTable)
        table.clear()
        
        self.total_sale = Decimal("0.0")
        for item in self.cart:
            table.add_row(
                item["name"],
                item["quantity"],
                f"{item['unit_price']:.2f}",
                f"{item['subtotal']:.2f}"
            )
            self.total_sale += item["subtotal"]
        
        # Actualizar el total
        total_display = self.query_one("#sale_total_display", Static)
        total_display.update(f"TOTAL: Bs {self.total_sale:.2f}")
        # Al refrescar la tabla, se pierde la selección.
        # Deshabilitamos el botón de quitar y reseteamos el índice.
        self.query_one("#sale_remove_item_button", Button).disabled = True
        self.selected_cart_row = None

    def action_dismiss(self) -> None:
        """Al presionar ESC, resetea la pantalla antes de salir."""
        self.reset_sale_screen()
        super().dismiss()

    def reset_sale_screen(self) -> None:
        """Resetea la pantalla de venta completa a su estado inicial."""
        
        # 1. Resetear estado interno (los datos)
        self.cart.clear() # Vacía la lista de productos
        self.current_product = None
        self.total_sale = Decimal("0.0")
        self.selected_cart_row = None
        
        # 2. Resetear UI del carrito y total
        # (update_cart_display ya limpia la tabla y resetea el botón 'Quitar')
        self.update_cart_display() 
        
        # 3. Resetear UI de búsqueda
        # (clear_search_state ya limpia los inputs y el 'producto encontrado')
        self.clear_search_state()
        
        # 4. Limpiar el log y poner mensaje inicial
        self.query_one("#sale_feedback_log", Log).clear()
        self.log_message("Sistema TPV listo. Busque un producto para comenzar.")

    # --- Manejadores de Eventos ---

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja todos los clics de botones en la pantalla de venta."""
        
        if event.button.id == "sale_search_button":
            self.handle_search()
        
        elif event.button.id == "sale_add_to_cart_button":
            self.handle_add_to_cart()

        elif event.button.id == "sale_remove_item_button":
            self.handle_remove_from_cart()
        
        elif event.button.id == "sale_finalize_button":
            self.handle_finalize_sale()

        elif event.button.id == "sale_cancel_button":
            self.action_dismiss() # Cierra la pantalla de venta

    def handle_search(self) -> None:
        """Busca el producto por código de barras."""
        search_term = self.query_one("#sale_search_input", Input).value.strip()
        if not search_term:
            self.log_message("[ERROR] Ingrese un código de barras.")
            return

        # find_product_by_name_or_barcode devuelve una LISTA
        results = find_product_by_name_or_barcode(search_term)
        
        if not results:
            self.log_message(f"[ERROR] Producto '{search_term}' no encontrado.")
            self.current_product = None
            self.enable_add_controls(False)
            return
        
        # Usamos el primer resultado (asumiendo búsqueda por barcode único)
        self.current_product = results[0]
        
        # Verificar si el producto está activo
        if self.current_product["active"] != "Activo": # El servicio devuelve "Activo" o "Inactivo"
             self.log_message(f"[ERROR] Producto '{self.current_product['name']}' está INACTIVO.")
             self.current_product = None
             self.enable_add_controls(False)
             return

        # Mostrar datos del producto encontrado
        found_text = self.query_one("#sale_found_product", Static)
        
        # --- MODIFICACIÓN ESTÉTICA ---
        # Cambiamos "Precio" por "Precio Unit." y "Stock" por "Stock Disp."
        found_text.update(
            f"Nombre: [b]{self.current_product['name']}[/b]\n"
            f"Precio Unit.: Bs {self.current_product['sale_price']:.2f} (Stock Disp.: {self.current_product['quantity']})"
        )
        # --- FIN DE LA MODIFICACIÓN ---
        
        self.log_message(f"Producto encontrado: {self.current_product['name']}.")
        self.enable_add_controls(True)
        self.query_one("#sale_quantity_input", Input).focus()

    def handle_add_to_cart(self) -> None:
        """Valida y añade el producto buscado al carrito."""
        if not self.current_product:
            self.log_message("[ERROR] No hay producto seleccionado.")
            return

        try:
            quantity = int(self.query_one("#sale_quantity_input", Input).value)
            if quantity <= 0:
                raise ValueError("La cantidad debe ser positiva.")
        except ValueError:
            self.log_message("[ERROR] Cantidad inválida. Debe ser un número entero > 0.")
            return
            
        # --- Validación de Stock (lado cliente) ---
        # El servicio 'find_product_by_name_or_barcode' devuelve 'quantity' como el stock actual
        stock_available = int(self.current_product["quantity"])
        
        if quantity > stock_available:
            self.log_message(f"[ERROR] Stock insuficiente para '{self.current_product['name']}'.")
            self.log_message(f"Disponible: {stock_available}, Solicitado: {quantity}")
            return
            
        # Preparar datos para el carrito
        unit_price = Decimal(self.current_product["sale_price"])
        subtotal = unit_price * Decimal(quantity)

        # (Opcional: Verificar si ya está en el carrito y sumar, por ahora lo añadimos)
        
        cart_item = {
            "barcode": self.current_product["barcode"],
            "name": self.current_product["name"],
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal
        }
        
        self.cart.append(cart_item)
        self.log_message(f"[AÑADIDO] {quantity} x {cart_item['name']}")
        
        # Actualizar la UI
        self.update_cart_display()
        self.clear_search_state()

    def handle_finalize_sale(self) -> None:
        """Prepara los datos y llama al servicio record_sale."""
        if not self.cart:
            self.log_message("[ERROR] El carrito está vacío. Añada productos.")
            return
            
        # La función 'record_sale' espera una lista de dicts
        # con 'barcode' y 'quantity'
        items_to_sell = [
            {"barcode": item["barcode"], "quantity": item["quantity"]}
            for item in self.cart
        ]
        
        self.log_message("Procesando venta... por favor espere.")
        
        try:
            # Llamamos al servicio de backend
            success, message = record_sale(items_to_sell)
            
            # Mostramos el resultado en un Pop-up
            self.app.push_screen(NotificationScreen(message))
            
            if success:
                self.reset_sale_screen()
                super().dismiss() # Cerramos la pantalla de Venta si fue exitosa
            else:
                # Si falló (ej. stock insuficiente detectado en el backend),
                # nos quedamos en la pantalla de venta para que el usuario corrija.
                self.log_message(f"[FALLO EN VENTA] {message}")

        except Exception as e:
            self.log_message(f"[ERROR CRÍTICO] {e}")
            self.app.push_screen(NotificationScreen(f"Error crítico al vender: {e}"))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Maneja la selección de un item en la tabla del carrito."""
        
        if event.control.id == "sale_cart_table":
            # El atributo correcto es 'cursor_row', no 'row_index'
            if event.cursor_row is not None: # <--- CORREGIDO
                # Guardamos el índice de la fila (0, 1, 2, ...)
                self.selected_cart_row = event.cursor_row # <--- CORREGIDO
                # Activamos el botón de quitar
                self.query_one("#sale_remove_item_button", Button).disabled = False
                # Log opcional
                try:
                    self.log_message(f"Item '{self.cart[event.cursor_row]['name']}' seleccionado.") # <--- CORREGIDO
                except IndexError:
                    pass # Evitar error si hay desfase

    def handle_remove_from_cart(self) -> None:
        """Quita el producto seleccionado (self.selected_cart_row) del carrito."""
        
        if self.selected_cart_row is None:
            self.log_message("[ERROR] No hay un producto seleccionado para quitar.")
            return
            
        try:
            # Usamos .pop() para quitar el item de la lista usando su índice
            removed_item = self.cart.pop(self.selected_cart_row)
            
            self.log_message(f"[QUITADO] {removed_item['quantity']} x {removed_item['name']}")
            
            # Refrescar la tabla y los totales
            # update_cart_display también reseteará la selección
            self.update_cart_display()
            
        except IndexError:
            self.log_message("[ERROR] El item seleccionado ya no existe.")
            # Refrescar por si acaso
            self.update_cart_display()
        except Exception as e:
            self.log_message(f"[ERROR INESPERADO] {e}")

class HistoryScreen(Screen):
    """Pantalla con las opciones para ver el historial de ventas."""

    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Volver (ESC)"),
    ]

    def compose(self) -> ComposeResult:
        """Define el layout de la pantalla de historial."""
        
        yield Static("HISTORIAL DE VENTAS", id="main-title")
        
        # Usamos un Vertical container para apilar los botones
        yield Vertical(
            Button("HISTORIAL POR VENTAS (DETALLADO)", id="history_sales"),
            Button("RESUMEN POR FECHA (TOTALES)", id="history_date"),
            Button("SALIR", id="exit_history_menu"),
            id="history-menu-container" # Usaremos este ID para los estilos
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejador de eventos para los botones del menú de historial."""
        
        if event.button.id == "exit_history_menu":
            self.dismiss()

        elif event.button.id == "history_sales":
            # --- AÑADIR MAPA 1 ---
            # Define la traducción de las columnas
            sales_map = {
                "sale_id": "ID",
                "timestamp": "Fecha de Venta",
                "product": "Nombre Producto",
                "barcode": "Código de Barras",
                "quantity": "Cantidad",
                "unit_price": "Precio Unidad",
                "subtotal": "Precio Total" # Usamos 'subtotal' como pediste
            }
            
            self.app.push_screen(InventoryViewerScreen(
                title="HISTORIAL POR VENTAS (DETALLADO)", 
                list_function=list_sales_history,
                header_map=sales_map # <-- Pasar el mapa
            ))
            
        elif event.button.id == "history_date":
            # --- AÑADIR MAPA 2 ---
            # Define la traducción de las columnas
            date_map = {
                "date": "Fecha de Venta",
                "total_sales": "Total de Ventas",
                "total_amount": "Monto total"
            }
            
            self.app.push_screen(InventoryViewerScreen(
                title="RESUMEN DE VENTAS POR FECHA", 
                list_function=sales_summary_by_date,
                header_map=date_map # <-- Pasar el mapa
            ))

class ModifySelectionScreen(ModalScreen):
    """Modal para seleccionar el campo específico a modificar."""
    
    BINDINGS = [
        Binding("escape", "dismiss_self", "Cancelar"),
    ]
    
    # Mapeo de botones a los nombres de campo reales en la DB/servicios
    # 'category_name' es el nombre que espera el servicio de actualización
    FIELD_MAP = {
        "modify_name": "name",
        "modify_barcode": "barcode",
        "modify_category": "category_name", 
        "modify_unit": "unit",
        "modify_purchase_price": "purchase_price",
        "modify_sale_price": "sale_price",
        "modify_expiration_date": "expiration_date",
        "modify_location": "location",
    }

    def __init__(self, product_id: int, product_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_id = product_id
        self.product_name = product_name
    
    def compose(self) -> ComposeResult:
        with Vertical(id="selection-modal", classes="selection-container"):
            yield Static(f"¿Qué detalle de '[b]{self.product_name}[/b]' desea modificar?", classes="modal-title")
            yield Button("1. Nombre", id="modify_name")
            yield Button("2. Código de Barras", id="modify_barcode")
            yield Button("3. Nombre de Categoría", id="modify_category")
            yield Button("4. Unidad de Medida", id="modify_unit")
            yield Button("5. Precio de Compra", id="modify_purchase_price")
            yield Button("6. Precio de Venta", id="modify_sale_price")
            yield Button("7. Fecha de Expiración", id="modify_expiration_date")
            yield Button("8. Ubicación", id="modify_location")
            yield Button("9. Ver Detalles y Salir", id="view_details_exit", variant="warning")
            yield Button("Cancelar Modificación", id="cancel_modification", variant="error")
            
    def action_dismiss_self(self):
        """Atajo de teclado para cancelar."""
        self.dismiss(None) # Devuelve None si se cancela
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        
        if button_id == "cancel_modification":
            self.action_dismiss_self()
        
        elif button_id == "view_details_exit":
            # Devolvemos None, la pantalla anterior maneja el cierre del modal
            self.dismiss(None) 
            
        elif button_id in self.FIELD_MAP:
            field_name = self.FIELD_MAP[button_id]
            # Devolvemos el ID y el campo a modificar
            self.dismiss((self.product_id, field_name))

class ModifyProductFormScreen(Screen):
    """
    Formulario para modificar los detalles de un producto existente.
    """
    CSS_PATH = "tui.css"

    BINDINGS = [
        ("escape", "dismiss", "Cancelar (ESC)"), 
    ]
    
    # El ID del producto se guarda al crear la pantalla
    def __init__(self, product_id: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.product_id = product_id

    def compose(self) -> ComposeResult:
        """Define los campos de entrada para la modificación."""
        yield Header(name="MODIFICAR PRODUCTO")
        yield ScrollableContainer(
            Static(f"Modificando producto ID: [b]{self.product_id}[/b]", id="form-instruction"),
            
            # Campos de solo lectura (ID y Profit)
            Label("ID (No Modificable):"),
            Input(id="modify_id", classes="form-input", disabled=True),
            
            Label("Nombre del Producto:"),
            Input(placeholder="Ej: Leche Entera", id="name_input", classes="form-input"),
            
            Label("Código de Barras:"),
            Input(placeholder="Ej: 777123456 (Debe ser único)", id="barcode_input", classes="form-input"),
            
            Label("Categoría:"),
            Input(placeholder="Ej: Lácteos", id="category_input", classes="form-input"),
            
            Label("Unidad de Medida:"),
            Input(placeholder="Ej: unidad, kg, litro", id="unit_input", classes="form-input"),
            
            Label("Ubicación:"),
            Input(placeholder="Ej: Pasillo A", id="location_input", classes="form-input"),
            
            Label("Precio de Compra:"),
            Input(placeholder="Ej: 5.50 (Solo números)", id="purchase_price_input", classes="form-input"),
            
            Label("Precio de Venta:"),
            Input(placeholder="Ej: 7.00 (Solo números)", id="sale_price_input", classes="form-input"),
            
            Label("Ganancia (Profit) (Solo Lectura):"),
            Input(id="profit_input", classes="form-input", disabled=True),
            
            Label("Fecha de Vencimiento (YYYY-MM-DD - Opcional):"),
            Input(placeholder="Ej: 2026-12-31 (Dejar vacío si no aplica)", id="expiration_date_input", classes="form-input"),
            
            Label("Estado Activo (True/False):"),
            Input(placeholder="True o False", id="active_input", classes="form-input"),

            Static("", id="form_feedback"),
            
            Grid(
                Button("GUARDAR CAMBIOS", id="save_modifications", variant="primary"),
                Button("CANCELAR", id="cancel_modifications", variant="error"),
                id="form-buttons-grid"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Carga los datos del producto seleccionado al iniciar la pantalla."""
        product_data = get_product_details_by_id(self.product_id)
        
        if product_data:
            # Precargar todos los Inputs con los datos del producto
            self.query_one("#modify_id", Input).value = str(product_data["id"])
            self.query_one("#name_input", Input).value = product_data["name"]
            self.query_one("#barcode_input", Input).value = product_data["barcode"]
            self.query_one("#category_input", Input).value = product_data["category_name"]
            self.query_one("#unit_input", Input).value = product_data["unit"]
            self.query_one("#location_input", Input).value = product_data["location"] if product_data["location"] else ""
            
            self.query_one("#purchase_price_input", Input).value = str(product_data["purchase_price"])
            self.query_one("#sale_price_input", Input).value = str(product_data["sale_price"])
            
            # El campo Profit es de solo lectura (como solicitaste)
            self.query_one("#profit_input", Input).value = str(product_data["profit"])
            
            # Manejo de la fecha de expiración, si es None, se usa cadena vacía
            exp_date_str = str(product_data["expiration_date"]) if product_data["expiration_date"] else ""
            self.query_one("#expiration_date_input", Input).value = exp_date_str
            
            # Estado activo
            self.query_one("#active_input", Input).value = str(product_data["active"])
        else:
            # Si no se encuentra el producto, notificar y cerrar
            self.app.push_screen(NotificationScreen(f"Error: No se encontró el producto con ID {self.product_id}."))
            self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja el guardado o la cancelación."""
        if event.button.id == "cancel_modifications":
            self.dismiss()
        
        elif event.button.id == "save_modifications":
            self.handle_save()

    def handle_save(self) -> None:
        """Recolecta, valida y guarda los datos modificados."""
        feedback = self.query_one("#form_feedback")
        
        try:
            # 1. Recolectar datos del formulario
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
            }
            
            # 2. Validación básica de campos no vacíos
            if not all([data["name"], data["barcode"], data["category_name"], data["unit"], data["purchase_price"], data["sale_price"], data["active"]]):
                feedback.update(" [b]ERROR:[/b] Los campos principales no pueden estar vacíos.")
                return

            # 3. Conversión de tipos y validación de formato
            try:
                purchase_price_f = float(data["purchase_price"])
                sale_price_f = float(data["sale_price"])
                active_status = data["active"].capitalize() # Para aceptar true/false en minúsculas

                if active_status not in ["True", "False"]:
                    feedback.update(" [b]ERROR:[/b] El campo 'Estado Activo' debe ser 'True' o 'False'.")
                    return
                    
            except ValueError:
                feedback.update(" [b]ERROR:[/b] Los precios deben ser números válidos.")
                return

            # 4. Llamar al servicio de backend para actualizar
            success, message = update_product_details(
                product_id=self.product_id,
                name=data["name"],
                new_barcode=data["barcode"],
                category_name=data["category_name"],
                unit=data["unit"],
                location=data["location"],
                purchase_price=purchase_price_f,
                sale_price=sale_price_f,
                expiration_date_str=data["expiration_date"],
                active_status=active_status
            )
            
            # 5. Mostrar resultado
            self.app.push_screen(NotificationScreen(message))
            if success:
                self.dismiss() # Cierra el formulario si el guardado fue exitoso

        except Exception as e:
            # Captura errores que podrían no ser de validación (ej. errores de conexión o peewee)
            feedback.update(f" [b]ERROR INESPERADO:[/b] {e}")


# --- Pantalla Principal (El Menú) ---
# Esta es la pantalla que diseñaste en tu imagen.
class MainMenuScreen(Screen):
    """La pantalla principal que muestra el menú de opciones."""

    CSS_PATH = "tui.css"
    
    # Definir atajos de teclado (usando Binding para evitar el Footer si no se usa)
    BINDINGS = [
        Binding("escape", "quit_app", "Salir (ESC)"),
    ]

    def compose(self) -> ComposeResult:
        """Define el layout (la interfaz) de la app."""
        
        # 1. Título "MENÚ PRINCIPAL"
        yield Static("MENÚ PRINCIPAL", id="main-title")

        # 2. La cuadrícula de 2x3 con los botones
        yield Grid(
            Button("AGREGAR", id="agregar"),
            Button("VER", id="ver"),
            Button("MODIFICAR PRODUCTO (DETALLES)", id="modificar"),
            Button("VENDER", id="vender"),
            Button("HISTORIAL", id="historial"),
            Button("SALIR", id="salir"),
            id="menu-grid"
        )
        
        # El Footer es opcional, pero ayuda a mostrar los bindings (como 'q')
        yield Footer()

    def action_quit_app(self) -> None:
        """Cierra la aplicación (llamado por el atajo 'q')."""
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejador de eventos para todos los botones del menú."""

        button_id = event.button.id

        if button_id == "salir":
            self.app.exit() # Cierra la aplicación

        elif button_id == "agregar":
            # ABRIMOS LA PANTALLA DE AGREGAR
            self.app.push_screen("add_menu")

        elif button_id == "ver":
            # ABRIMOS LA PANTALLA DE VER
            self.app.push_screen("view_menu")
        
        elif button_id == "modificar":
            self.app.push_screen("modify_product_screen") 
            
        elif button_id == "vender":
            # ABRIMOS LA PANTALLA DE VENDER
            self.app.push_screen("sale_screen")

        elif button_id == "historial":
            self.app.push_screen("history_menu")


# --- La Aplicación Principal ---
class InventoryTUI(App):
    """La aplicación TUI principal."""

    # Cargar el archivo CSS
    CSS_PATH = "tui.css"
    
    # Definir las pantallas que la app conoce
    SCREENS = {
        "main_menu": MainMenuScreen,
        "notify": NotificationScreen,
        "add_menu": AddScreen,
        "add_product_form": AddProductFormScreen,
        "add_stock_form": AddStockFormScreen,
        "view_menu": ViewScreen,
        "search_product_screen": SearchProductScreen,
        "view_by_category_screen": ViewByCategoryScreen,
        "modify_product_screen": ModifyProductScreen,
        "modify_selection_screen": ModifySelectionScreen,
        "modify_product_form_screen": ModifyProductFormScreen,
        "sale_screen": SaleScreen,
        "history_menu": HistoryScreen,
    }

    def on_mount(self) -> None:
        """Se llama cuando la app se carga por primera vez."""
        # Mostramos la pantalla del menú principal
        self.push_screen("main_menu")


# --- Punto de entrada para ejecutar la app ---
if __name__ == "__main__":
    app = InventoryTUI()
    app.run()