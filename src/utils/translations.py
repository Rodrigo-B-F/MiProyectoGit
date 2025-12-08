"""
Translations Module
===================
Spanish translations for all field names, UI labels, and messages.
Adapted for MiProyectoGit.
"""

# Product field translations (used in headers and prompts)
PRODUCT_FIELDS = {
    'name': 'NOMBRE',
    'barcode': 'CÓDIGO',
    'category_name': 'CATEGORÍA',
    'description': 'DESCRIPCIÓN',
    'location': 'UBICACIÓN',
    'sale_price': 'PRECIO',
    'initial_quantity': 'CANTIDAD INICIAL',
    'quantity': 'STOCK',
    'active': 'ESTADO',
    # Sale fields
    'sale_id': 'ID VENTA',
    'timestamp': 'FECHA/HORA',
    'product': 'PRODUCTO',
    'unit_price': 'PRECIO UNIT.',
    'subtotal': 'SUBTOTAL',
    # Summary fields
    'date': 'FECHA',
    'total_sales': 'VENTAS TOTALES',
    'total_amount': 'MONTO TOTAL'
}

# Menu options
MENU_OPTIONS = {
    'main_title': '--- Menú de Gestión de Tienda ---',
    'main_menu': [
        '1. Agregar Nuevo Producto y Stock Inicial',
        '2. Registrar Entrada de Stock (Compra)',
        '3. Registrar Venta',
        '4. Listar Inventario de Productos activos',
        '5. Listar Inventario de Productos inactivos',
        '6. Listar Productos por Categoría',
        '7. Listar Productos con Stock Disponible',
        '8. Listar Productos sin Stock Disponible',
        '9. Buscar Producto por Nombre/Código',
        '10. Modificar Detalles del Producto',
        '11. Activar/Desactivar Producto',
        '12. Listar Historial de Ventas',
        '13. Resumen de Ventas por Fecha',
        '14. Modificar Categoría',
        '15. Salir'
    ],
    'update_menu_title': '--- Campo a Actualizar ---',
    'update_menu': [
        '1. Nombre',
        '2. Código de Barras',
        '3. Nombre de Categoría',
        '4. Precio de Venta',
        '5. Ubicación',
        '6. Ver Detalles y Salir'
    ]
}

# TUI Menu Options
TUI_MENU_OPTIONS = {
    'view_search': 'BUSCAR PRODUCTO',
    'view_active': 'PRODUCTOS ACTIVOS',
    'view_inactive': 'PRODUCTOS INACTIVOS',
    'view_available': 'PRODUCTOS CON STOCK',
    'view_out_of_stock': 'PRODUCTOS SIN STOCK',
    'view_expiring': 'VER PRÓXIMOS A VENCER',
    'view_by_category': 'VER POR CATEGORÍA',
    'exit': 'SALIR',
    'back': 'VOLVER',
    'add_product': 'AGREGAR NUEVO PRODUCTO',
    'add_stock': 'REGISTRAR ENTRADA DE STOCK',
    'modify_product': 'MODIFICAR PRODUCTO (DETALLES)',
    'modify_category': 'MODIFICAR CATEGORÍA',
    'history_sales': 'HISTORIAL POR VENTAS (DETALLADO)',
    'history_date': 'RESUMEN POR FECHA (TOTALES)'
}

# Input prompts
INPUT_PROMPTS = {
    'select_option': 'Selecciona una opción: ',
    'name': 'Nombre del Producto: ',
    'barcode': 'Código de Barras (Único): ',
    'category_name': 'Nombre de Categoría: ',
    'location': 'Ubicación (Ej: Pasillo A): ',
    'sale_price': 'Precio de Venta: ',
    'initial_quantity': 'Cantidad Inicial en Stock: ',
    'quantity_purchase': 'Cantidad de unidades compradas: ',
    'barcode_search': 'Código de Barras del producto (o "FIN" para terminar): ',
    'quantity_sell': 'Cantidad a vender de {barcode}: ',
    'search_query': 'Ingresa Nombre o Código de Barras a buscar: ',
    'barcode_modify': 'Código de Barras del Producto a modificar: ',
    'status_modify': 'Estado (A = Activar, D = Desactivar, o Enter para invertir): ',
    'category_select': 'Ingrese el número de la categoría que desea ver o "r" para regresar: ',
    'new_value': 'Ingresa el NUEVO {field}: '
}

# Messages
MESSAGES = {
    'init_db': 'Inicializando base de datos...',
    'db_ready': 'Base de datos lista.',
    'success': 'Éxito',
    'error': 'Error',
    'result_format': '\nResultado: {status} - {message}',
    'invalid_number': '\nError: Los precios y cantidades deben ser números válidos.',
    'unexpected_error': '\nError inesperado: {error}',
    'quantity_positive': 'La cantidad debe ser mayor que cero.',
    'sale_cancelled': 'Venta cancelada. No se agregaron productos.',
    'no_results': 'No se encontraron productos que coincidan con la búsqueda.',
    'no_sales': 'No hay ventas registradas.',
    'no_stock': 'No hay productos sin stock.',
    'no_categories': 'No se encontraron categorías. Agregue productos para crear categorías.',
    'invalid_option': 'Opción no válida. Inténtalo de nuevo.',
    'bye': 'Saliendo del programa. ¡Hasta pronto!'
}
