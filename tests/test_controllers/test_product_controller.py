"""
Pruebas unitarias para product_controller.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from controllers import (
    add_product,
    toggle_product_status,
    find_product_by_name_or_barcode,
    list_products_by_category,
    update_product_details,
    get_product_details_by_id
)
from models.product import Product
from models.inventory import Inventory


@pytest.mark.unit
@pytest.mark.database
class TestProductController:
    """Pruebas para el controlador de productos."""
    
    def test_add_product_success(self, test_db):
        """Prueba agregar un producto exitosamente."""
        # Arrange
        product_data = {
            'name': 'Teclado Mecánico',
            'barcode': 'TEC001',
            'category_name': 'Periféricos',
            'unit': 'unidad',
            'location': 'Pasillo A',
            'purchase_price': '80.00',
            'sale_price': '120.00',
            'initial_quantity': 10
        }
        
        # Act
        success, message = add_product(**product_data)
        
        # Assert
        assert success is True
        assert 'Teclado Mecánico' in message
        assert Product.select().count() == 1
        
        # Verificar que se creó el inventario
        product = Product.get(Product.barcode == 'TEC001')
        inventory = Inventory.get(Inventory.product == product)
        assert inventory.quantity == 10
    
    def test_add_product_duplicate_barcode(self, test_db, sample_product):
        """Prueba que no se puede agregar un producto con código duplicado."""
        # Arrange
        product_data = {
            'name': 'Otro Producto',
            'barcode': sample_product.barcode,  # Código duplicado
            'category_name': 'Electrónica',
            'unit': 'unidad',
            'location': 'Pasillo B',
            'purchase_price': '50.00',
            'sale_price': '75.00',
            'initial_quantity': 5
        }
        
        # Act
        success, message = add_product(**product_data)
        
        # Assert
        assert success is False
        assert 'ya existe' in message.lower()
    
    def test_add_product_with_expiration(self, test_db):
        """Prueba agregar un producto con fecha de vencimiento."""
        # Arrange
        expiration = (datetime.now() + timedelta(days=90)).date()
        product_data = {
            'name': 'Yogurt',
            'barcode': 'YOG001',
            'category_name': 'Lácteos',
            'unit': 'unidad',
            'location': 'Refrigerador',
            'purchase_price': '1.50',
            'sale_price': '2.00',
            'initial_quantity': 20,
            'expiration_date': expiration
        }
        
        # Act
        success, message = add_product(**product_data)
        
        # Assert
        assert success is True
        product = Product.get(Product.barcode == 'YOG001')
        assert product.expiration_date == expiration
    
    def test_toggle_product_status(self, test_db, sample_product):
        """Prueba activar/desactivar un producto."""
        # Arrange
        assert sample_product.active is True
        
        # Act - Desactivar
        success, message = toggle_product_status(sample_product.barcode, new_status=False)
        
        # Assert
        assert success is True
        product = Product.get_by_id(sample_product.id)
        assert product.active is False
        
        # Act - Activar
        success, message = toggle_product_status(sample_product.barcode, new_status=True)
        
        # Assert
        assert success is True
        product = Product.get_by_id(sample_product.id)
        assert product.active is True
    
    def test_find_product_by_barcode(self, test_db, sample_product, sample_inventory):
        """Prueba buscar un producto por código de barras."""
        # Act
        results = find_product_by_name_or_barcode(sample_product.barcode)
        
        # Assert
        assert len(results) == 1
        assert results[0]['barcode'] == sample_product.barcode
        assert results[0]['name'] == sample_product.name
    
    def test_find_product_by_name(self, test_db, sample_product, sample_inventory):
        """Prueba buscar un producto por nombre."""
        # Act
        results = find_product_by_name_or_barcode('Laptop')
        
        # Assert
        assert len(results) >= 1
        assert any(r['name'] == sample_product.name for r in results)
    
    def test_find_product_not_found(self, test_db):
        """Prueba buscar un producto que no existe."""
        # Act
        results = find_product_by_name_or_barcode('NOEXISTE')
        
        # Assert
        assert results == []
    
    def test_list_products_by_category(self, test_db, sample_category, sample_product, sample_inventory):
        """Prueba listar productos por categoría."""
        # Act
        results = list_products_by_category(sample_category.id)
        
        # Assert
        assert len(results) >= 1
        assert any(r['name'] == sample_product.name for r in results)
    
    def test_get_product_details_by_id(self, test_db, sample_product):
        """Prueba obtener detalles de un producto por ID."""
        # Act
        result = get_product_details_by_id(sample_product.id)
        
        # Assert
        assert result is not None
        assert result['id'] == sample_product.id
        assert result['name'] == sample_product.name
        assert result['barcode'] == sample_product.barcode
    
    def test_update_product_details(self, test_db, sample_product):
        """Prueba actualizar los detalles de un producto."""
        # Arrange
        new_name = "Laptop HP Actualizada"
        new_price = "1600.00"
        
        # Act
        success, message = update_product_details(
            product_id=sample_product.id,
            name=new_name,
            new_barcode=sample_product.barcode,
            category_name=sample_product.category.name,
            unit=sample_product.unit,
            location=sample_product.location,
            purchase_price=str(sample_product.purchase_price),
            sale_price=new_price,
            expiration_date_str="",
            date_added_str=sample_product.date_added.strftime('%Y-%m-%d'),
            active_status=True
        )
        
        # Assert
        assert success is True
        updated_product = Product.get_by_id(sample_product.id)
        assert updated_product.name == new_name
        assert updated_product.sale_price == Decimal(new_price)
