"""
Tests for Product Management Controller
"""

import pytest
from controllers import (
    add_product,
    update_product_details,
    toggle_product_status,
    find_product_by_name_or_barcode
)
from models import Product


class TestAddProduct:
    """Tests for add_product function"""
    
    def test_add_product_success(self, test_db, sample_category):
        """Test successful product creation"""
        success, message = add_product(
            name="Yogurt Natural 200g",
            barcode="7501234568",
            category_name=sample_category.name,
            location="Estante A2",
            sale_price=15.00,
            initial_quantity=10
        )
        
        assert success is True
        assert "exitosamente" in message.lower() or "agregado" in message.lower()
    
    def test_add_product_duplicate_barcode(self, test_db, sample_product):
        """Test creating product with duplicate barcode"""
        success, message = add_product(
            name="Otro Producto",
            barcode=sample_product.barcode,  # Duplicate
            category_name=sample_product.category.name,
            location="Test",
            sale_price=20.00,
            initial_quantity=5
        )
        
        assert success is False
        assert "ya existe" in message.lower() or "barcode" in message.lower()


class TestUpdateProduct:
    """Tests for update_product_details function"""
    
    def test_update_product_success(self, test_db, sample_product):
        """Test successful product update"""
        success, message = update_product_details(
            product_id=sample_product.id,
            name="Leche Descremada 1L - Actualizada",
            new_barcode=sample_product.barcode,
            category_name=sample_product.category.name,
            location=sample_product.location,
            sale_price=30.00
        )
        
        assert success is True
        assert "actualizado" in message.lower()
    
    def test_update_nonexistent_product(self, test_db):
        """Test updating non-existent product"""
        success, message = update_product_details(
            product_id=99999,
            name="No Existe",
            new_barcode="9999999999",
            category_name="Test",
            location="Test",
            sale_price=10.00
        )
        
        assert success is False
        assert "no encontrado" in message.lower()


class TestToggleProductStatus:
    """Tests for toggle_product_status function"""
    
    def test_toggle_product_status_success(self, test_db, sample_product):
        """Test successful product status toggle (soft delete)"""
        initial_status = sample_product.active
        success, message = toggle_product_status(sample_product.barcode)
        
        assert success is True
        # Verify status changed
        # Verify status changed
        updated_product = Product.get_by_id(sample_product.id)
        assert updated_product.active != initial_status
    
    def test_toggle_nonexistent_product(self, test_db):
        """Test toggling non-existent product"""
        success, message = toggle_product_status("9999999999")
        
        assert success is False


class TestFindProduct:
    """Tests for find_product_by_name_or_barcode function"""
    
    def test_find_by_barcode(self, test_db, sample_product):
        """Test finding product by barcode"""
        results = find_product_by_name_or_barcode(sample_product.barcode)
        
        assert len(results) > 0
        assert results[0]['barcode'] == sample_product.barcode
    
    def test_find_by_name(self, test_db, sample_product):
        """Test finding product by name"""
        results = find_product_by_name_or_barcode("Leche")
        
        assert len(results) > 0
        assert "Leche" in results[0]['name']
    
    def test_find_no_results(self, test_db):
        """Test search with no results"""
        results = find_product_by_name_or_barcode("NoExiste12345")
        
        assert len(results) == 0
