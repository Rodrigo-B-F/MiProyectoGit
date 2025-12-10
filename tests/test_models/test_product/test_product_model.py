"""
Tests for Product Model
"""

import pytest
from models import Product, Category


class TestProductModel:
    """Tests for Product model"""
    
    def test_create_product(self, test_db, sample_category):
        """Test creating a product"""
        product = Product.create(
            name="Test Product",
            barcode="1234567890",
            category=sample_category,
            sale_price=10.00,
            active=True
        )
        
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.barcode == "1234567890"
        assert product.active is True
    
    def test_product_category_relationship(self, test_db, sample_product):
        """Test product-category relationship"""
        assert sample_product.category is not None
        assert sample_product.category.name == "Lácteos"
    
    def test_product_unique_barcode(self, test_db, sample_product, sample_category):
        """Test barcode uniqueness constraint"""
        with pytest.raises(Exception):
            Product.create(
                name="Duplicate",
                barcode=sample_product.barcode,  # Duplicate
                category=sample_category,
                sale_price=15.00
            )
