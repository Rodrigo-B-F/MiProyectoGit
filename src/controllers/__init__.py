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
    find_product_for_edit,
    list_products_by_category,
    list_products_without_category,
    get_product_details_by_id
)


# Inventory Controller
from .inventory.stock_management import add_stock
from .inventory.inventory_reporting import (
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    get_low_stock_products
)
from .inventory.category_management import (
    list_categories,
    update_category,
    delete_category
)

# Sale Controller
from .sale.sale_transaction import record_sale
from .sale.sale_reporting import (
    list_sales_history,
    sales_summary_by_date,
    get_top_selling_products,
    get_least_selling_products,
    get_unsold_products
)

# Reports
from .reports import generate_purchase_report
