"""
Tests for Sale and SaleItem Models
"""

import pytest
from datetime import datetime
from models import Sale, SaleItem


class TestSaleModel:
    """Tests for Sale model"""
    
    def test_create_sale(self, test_db):
        """Test creating a sale"""
        sale = Sale.create(
            total_amount=100.00,
            timestamp=datetime.now()
        )
        
        assert sale.id is not None
        assert sale.total_amount == 100.00
    
    def test_sale_items_relationship(self, test_db, sample_product):
        """Test sale-items relationship"""
        sale = Sale.create(total_amount=50.00)
        
        item = SaleItem.create(
            sale=sale,
            product=sample_product,
            quantity=2,
            unit_price=25.00,
            subtotal=50.00
        )
        
        assert item.sale == sale
        assert item.product == sample_product


class TestSaleItemModel:
    """Tests for SaleItem model"""
    
    def test_create_sale_item(self, test_db, sample_product):
        """Test creating a sale item"""
        sale = Sale.create(total_amount=25.50)
        
        item = SaleItem.create(
            sale=sale,
            product=sample_product,
            quantity=1,
            unit_price=25.50,
            subtotal=25.50
        )
        
        assert item.id is not None
        assert item.quantity == 1
        assert item.subtotal == 25.50
