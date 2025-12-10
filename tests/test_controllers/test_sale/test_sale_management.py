"""
Tests for Sale Management Controller
"""

import pytest
from controllers import record_sale
from models import Sale, SaleItem, Inventory


class TestRecordSale:
    """Tests for record_sale function"""
    
    def test_record_sale_success(self, test_db, sample_inventory):
        """Test recording a successful sale"""
        initial_quantity = sample_inventory.quantity
        
        items = [{
            'barcode': sample_inventory.product.barcode,
            'quantity': 5,
            'unit_price': sample_inventory.product.sale_price
        }]
        
        success, message = record_sale(items)
        
        assert success is True
        assert "registrada" in message.lower()
        
        # Verify inventory was reduced
        updated_inventory = Inventory.get_by_id(sample_inventory.id)
        assert updated_inventory.quantity == initial_quantity - 5
        
        # Verify sale was created
        assert Sale.select().count() == 1
        assert SaleItem.select().count() == 1
    
    def test_record_sale_insufficient_stock(self, test_db, sample_inventory):
        """Test recording sale with insufficient stock"""
        items = [{
            'barcode': sample_inventory.product.barcode,
            'quantity': 1000,  # More than available
            'unit_price': sample_inventory.product.sale_price
        }]
        
        success, message = record_sale(items)
        
        assert success is False
        assert "insuficiente" in message.lower()
    
    def test_record_sale_empty_items(self, test_db):
        """Test recording sale with no items"""
        success, message = record_sale([])
        
        assert success is False
