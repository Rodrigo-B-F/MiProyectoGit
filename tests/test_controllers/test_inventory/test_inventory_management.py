"""
Tests for Inventory Management Controller
"""

import pytest
from controllers import add_stock


class TestAddStock:
    """Tests for add_stock function"""
    
    def test_add_stock_existing_product(self, test_db, sample_inventory):
        """Test adding stock to existing product"""
        initial_quantity = sample_inventory.quantity
        
        success, message = add_stock(
            product_barcode=sample_inventory.product.barcode,
            quantity=20
        )
        
        assert success is True
        # Refresh from database
        from models import Inventory
        updated_inv = Inventory.get(Inventory.product == sample_inventory.product)
        assert updated_inv.quantity == initial_quantity + 20
    
    def test_add_stock_new_product(self, test_db, sample_product):
        """Test adding stock to product without inventory"""
        success, message = add_stock(
            product_barcode=sample_product.barcode,
            quantity=30
        )
        
        assert success is True
    
    def test_add_stock_invalid_product(self, test_db):
        """Test adding stock to non-existent product"""
        success, message = add_stock(
            product_barcode="9999999999",
            quantity=10
        )
        
        assert success is False
        assert "no encontrado" in message.lower()
