"""
Tests for Category Model
"""

import pytest
from models import Category


class TestCategoryModel:
    """Tests for Category model"""
    
    def test_create_category(self, test_db):
        """Test creating a category"""
        category = Category.create(
            name="Bebidas",
            description="Bebidas en general"
        )
        
        assert category.id is not None
        assert category.name == "Bebidas"
    
    def test_category_unique_name(self, test_db, sample_category):
        """Test category name uniqueness"""
        with pytest.raises(Exception):
            Category.create(
                name=sample_category.name,  # Duplicate
                description="Test"
            )
    
    def test_category_products_relationship(self, test_db, sample_category, sample_product):
        """Test category-products relationship"""
        products = list(sample_category.products)
        assert len(products) > 0
        assert sample_product in products
