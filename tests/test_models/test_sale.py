"""
Pruebas unitarias para los modelos Sale y SaleItem.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from models.sale import Sale, SaleItem


@pytest.mark.unit
@pytest.mark.database
class TestSale:
    """Pruebas para el modelo Sale."""
    
    def test_create_sale(self, test_db):
        """Prueba crear una venta básica."""
        # Arrange & Act
        sale = Sale.create(
            total=Decimal('150.00')
        )
        
        # Assert
        assert sale.id is not None
        assert sale.total == Decimal('150.00')
    
    def test_sale_timestamp_auto_set(self, test_db):
        """Prueba que timestamp se establece automáticamente."""
        # Act
        sale = Sale.create(
            total=Decimal('200.00')
        )
        
        # Assert
        assert sale.timestamp is not None
        assert isinstance(sale.timestamp, datetime)
    
    def test_sale_default_total(self, test_db):
        """Prueba el valor por defecto del total."""
        # Act
        sale = Sale.create()
        
        # Assert
        assert sale.total == Decimal('0.00')
    
    def test_update_sale_total(self, test_db, sample_sale):
        """Prueba actualizar el total de una venta."""
        # Arrange
        new_total = Decimal('3500.00')
        
        # Act
        sample_sale.total = new_total
        sample_sale.save()
        
        # Assert
        updated_sale = Sale.get_by_id(sample_sale.id)
        assert updated_sale.total == new_total
    
    def test_sale_with_items(self, test_db, sample_sale, sample_sale_item):
        """Prueba que una venta puede tener items asociados."""
        # Act
        items = list(sample_sale.items)
        
        # Assert
        assert len(items) == 1
        assert items[0] == sample_sale_item


@pytest.mark.unit
@pytest.mark.database
class TestSaleItem:
    """Pruebas para el modelo SaleItem."""
    
    def test_create_sale_item(self, test_db, sample_sale, sample_product):
        """Prueba crear un item de venta."""
        # Arrange & Act
        item = SaleItem.create(
            sale=sample_sale,
            product=sample_product,
            quantity=3,
            unit_price=Decimal('1500.00'),
            subtotal=Decimal('4500.00')
        )
        
        # Assert
        assert item.id is not None
        assert item.sale == sample_sale
        assert item.product == sample_product
        assert item.quantity == 3
        assert item.unit_price == Decimal('1500.00')
        assert item.subtotal == Decimal('4500.00')
    
    def test_sale_item_subtotal_calculation(self, test_db, sample_sale, sample_product):
        """Prueba que el subtotal se calcula correctamente."""
        # Arrange
        quantity = 5
        unit_price = Decimal('100.00')
        expected_subtotal = Decimal(str(quantity)) * unit_price
        
        # Act
        item = SaleItem.create(
            sale=sample_sale,
            product=sample_product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=expected_subtotal
        )
        
        # Assert
        assert item.subtotal == Decimal('500.00')
    
    def test_multiple_items_in_sale(self, test_db, sample_sale, sample_product, sample_product_2):
        """Prueba crear múltiples items en una venta."""
        # Act
        item1 = SaleItem.create(
            sale=sample_sale,
            product=sample_product,
            quantity=2,
            unit_price=Decimal('1500.00'),
            subtotal=Decimal('3000.00')
        )
        item2 = SaleItem.create(
            sale=sample_sale,
            product=sample_product_2,
            quantity=10,
            unit_price=Decimal('3.00'),
            subtotal=Decimal('30.00')
        )
        
        # Assert
        items = list(sample_sale.items)
        assert len(items) == 2
        assert item1 in items
        assert item2 in items
    
    def test_calculate_sale_total_from_items(self, test_db, sample_product, sample_product_2):
        """Prueba calcular el total de una venta a partir de sus items."""
        # Arrange
        sale = Sale.create(total=Decimal('0.00'))
        
        item1 = SaleItem.create(
            sale=sale,
            product=sample_product,
            quantity=1,
            unit_price=Decimal('1500.00'),
            subtotal=Decimal('1500.00')
        )
        item2 = SaleItem.create(
            sale=sale,
            product=sample_product_2,
            quantity=5,
            unit_price=Decimal('3.00'),
            subtotal=Decimal('15.00')
        )
        
        # Act
        items = list(sale.items)
        calculated_total = sum(item.subtotal for item in items)
        
        # Assert
        assert calculated_total == Decimal('1515.00')
    
    def test_sale_item_product_relationship(self, test_db, sample_sale_item, sample_product):
        """Prueba la relación entre SaleItem y Product."""
        # Act
        sale_items = list(sample_product.sale_items)
        
        # Assert
        assert len(sale_items) == 1
        assert sale_items[0] == sample_sale_item
    
    def test_delete_sale_cascades_to_items(self, test_db, sample_sale, sample_product):
        """Prueba que eliminar una venta elimina sus items."""
        # Arrange
        item = SaleItem.create(
            sale=sample_sale,
            product=sample_product,
            quantity=1,
            unit_price=Decimal('100.00'),
            subtotal=Decimal('100.00')
        )
        item_id = item.id
        
        # Act
        sample_sale.delete_instance(recursive=True)
        
        # Assert
        with pytest.raises(SaleItem.DoesNotExist):
            SaleItem.get_by_id(item_id)
