# src/controllers/__init__.py
"""
Módulo de controladores - Lógica de negocio del patrón MVC.
Exporta todas las funciones de los controladores para facilitar imports.
"""

# Product Controller
from .product_controller import (
    add_product,
    toggle_product_status,
    find_product_by_name_or_barcode,
    list_products_by_category,
    update_product_details,
    apply_expiring_product_offer,
    get_product_details_by_id
)

# Inventory Controller
from .inventory_controller import (
    record_purchase,
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    list_expiring_products,
    list_categories
)

# Sale Controller
from .sale_controller import (
    record_sale,
    list_sales_history,
    sales_summary_by_date
)

__all__ = [
    # Product Controller
    'add_product',
    'toggle_product_status',
    'find_product_by_name_or_barcode',
    'list_products_by_category',
    'update_product_details',
    'apply_expiring_product_offer',
    'get_product_details_by_id',
    
    # Inventory Controller
    'record_purchase',
    'list_products_inventory',
    'list_available_products',
    'list_out_of_stock_products',
    'list_expiring_products',
    'list_categories',
    
    # Sale Controller
    'record_sale',
    'list_sales_history',
    'sales_summary_by_date',
]
