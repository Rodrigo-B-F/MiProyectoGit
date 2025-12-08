"""
Controladores de la aplicación (Simplificado).
Este archivo re-exporta las funciones de los módulos refactorizados para mantener compatibilidad.
"""

# Product Controller
from .product.product_crud import (
    add_product,
    toggle_product_status,
    update_product_details
)
from .product.product_search import (
    find_product_by_name_or_barcode,
    list_products_by_category,
    get_product_details_by_id
)
from .product.product_business import apply_expiring_product_offer

# Inventory Controller
from .inventory.stock_management import add_stock
from .inventory.inventory_reporting import (
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products
)
from .inventory.category_management import (
    list_categories,
    update_category
)

# Sale Controller
from .sale.sale_transaction import record_sale
from .sale.sale_reporting import (
    list_sales_history,
    sales_summary_by_date
)
