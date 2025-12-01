"""
Translations Module
===================
Spanish translations for all field names, UI labels, and messages.
Adapted for MiProyectoGit.
"""

# Product field translations (used in headers and prompts)
PRODUCT_FIELDS = {
    'name': 'NOMBRE',
    'barcode': 'CÓDIGO DE BARRAS',
    'category_name': 'CATEGORÍA',
    'description': 'DESCRIPCIÓN',
    'unit': 'UNIDAD',
    'location': 'UBICACIÓN',
    'purchase_price': 'PRECIO COMPRA',
    'sale_price': 'PRECIO VENTA',
    'initial_quantity': 'CANTIDAD INICIAL',
    'quantity': 'CANTIDAD',
    'expiration_date': 'VENCIMIENTO',
    'profit': 'GANANCIA',
    'date_added': 'FECHA AGREGADO',
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
        '11. Filtrar Productos Próximos a Vencer (10 días por defecto)',
        '12. Activar/Desactivar Producto',
        '13. Listar Historial de Ventas',
        '14. Resumen de Ventas por Fecha',
        '15. **APLICAR OFERTA** (Vencimiento < 10 días)',
        '16. Modificar Categoría',
        '17. Salir'
    ],
    'update_menu_title': '--- Campo a Actualizar ---',
    'update_menu': [
        '1. Nombre',
        '2. Código de Barras',
        '3. Nombre de Categoría',
        '4. Unidad de Medida',
        '5. Precio de Compra',
        '6. Precio de Venta',
        '7. Fecha de Expiración (YYYY-MM-DD, o "vacío" para eliminar)',
        '8. Ubicación',
        '9. Ver Detalles y Salir'
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
    'unit': 'Unidad de Medida (Ej: unidad, kg): ',
    'location': 'Ubicación (Ej: Pasillo A): ',
    'purchase_price': 'Precio de Compra: ',
    'sale_price': 'Precio de Venta: ',
    'initial_quantity': 'Cantidad Inicial en Stock: ',
    'expiration_date': 'Fecha de Vencimiento (YYYY-MM-DD o dejar vacío): ',
    'quantity_purchase': 'Cantidad de unidades compradas: ',
    'new_purchase_price': 'Nuevo Precio de Compra (se actualizará en el sistema): ',
    'barcode_search': 'Código de Barras del producto (o "FIN" para terminar): ',
    'quantity_sell': 'Cantidad a vender de {barcode}: ',
    'search_query': 'Ingresa Nombre o Código de Barras a buscar: ',
    'days_expiring': 'Buscar productos que venzan en los próximos [días]: ',
    'barcode_modify': 'Código de Barras del Producto a modificar: ',
    'status_modify': 'Estado (A = Activar, D = Desactivar, o Enter para invertir): ',
    'category_select': 'Ingrese el número de la categoría que desea ver o "r" para regresar: ',
    'days_offer': 'Límite de días para la oferta (Dejar vacío para usar 10 días por defecto): ',
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
    'no_expiring': 'No hay productos que venzan en los próximos {days} días.',
    'no_sales': 'No hay ventas registradas.',
    'no_stock': 'No hay productos sin stock.',
    'no_categories': 'No se encontraron categorías. Agregue productos para crear categorías.',
    'invalid_option': 'Opción no válida. Inténtalo de nuevo.',
    'bye': 'Saliendo del programa. ¡Hasta pronto!'
}
