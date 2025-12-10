"""
Tests for Inventory Model
"""

import pytest
from models import Inventory


class TestInventoryModel:
    """Tests for Inventory model"""
    
    def test_create_inventory(self, test_db, sample_product):
        """Test creating inventory"""
        inventory = Inventory.create(
            product=sample_product,
            quantity=100,
            location="Test Location"
        )
        
        assert inventory.id is not None
        assert inventory.quantity == 100
        assert inventory.product == sample_product
    
    def test_inventory_product_relationship(self, test_db, sample_inventory):
        """Test inventory-product relationship"""
        assert sample_inventory.product is not None
        assert sample_inventory.product.name == "Leche Descremada 1L"
    
    def test_update_inventory_quantity(self, test_db, sample_inventory):
        """Test updating inventory quantity"""
        sample_inventory.quantity = 75
        sample_inventory.save()
        
        # Reload from database
        updated = Inventory.get(Inventory.id == sample_inventory.id)
        assert updated.quantity == 75
