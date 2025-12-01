"""
Pruebas unitarias para sale_controller.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from controllers import (
    record_sale,
    list_sales_history,
    sales_summary_by_date
)
from models.inventory import Inventory
from models.batch import ProductBatch
from models.sale import Sale, SaleItem


@pytest.mark.unit
@pytest.mark.database
class TestSaleController:
    """Pruebas para el controlador de ventas."""
    
    def test_record_sale_single_item(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba registrar una venta con un solo producto."""
        # Arrange
        initial_inventory = sample_inventory.quantity
        initial_batch_qty = sample_batch.quantity
        sale_qty = 3
        
        items_to_sell = [
            {
                'barcode': sample_product.barcode,
                'quantity': sale_qty
            }
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is True
        assert "registrada exitosamente" in message
        
        # Verificar que se creó la venta
        assert Sale.select().count() == 1
        sale = Sale.get()
        assert sale.total > 0
        
        # Verificar que se redujo el inventario
        updated_inventory = Inventory.get(Inventory.product == sample_product)
        assert updated_inventory.quantity == initial_inventory - sale_qty
        
        # Verificar que se redujo el lote
        updated_batch = ProductBatch.get_by_id(sample_batch.id)
        assert updated_batch.quantity == initial_batch_qty - sale_qty
    
    def test_record_sale_multiple_items(self, test_db, sample_product, sample_product_2, 
                                       sample_batch, sample_inventory):
        """Prueba registrar una venta con múltiples productos."""
        # Arrange
        # Crear inventario y lote para el segundo producto
        inventory2 = Inventory.create(product=sample_product_2, quantity=50)
        batch2 = ProductBatch.create(
            product=sample_product_2,
            quantity=50,
            batch_number=0,
            purchase_price=Decimal('2.50')
        )
        
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 2},
            {'barcode': sample_product_2.barcode, 'quantity': 5}
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is True
        
        # Verificar que se crearon los items de venta
        sale = Sale.get()
        items = list(sale.items)
        assert len(items) == 2
        
        # Verificar el total
        expected_total = (Decimal('2') * sample_product.sale_price + 
                         Decimal('5') * sample_product_2.sale_price)
        assert sale.total == expected_total
    
    def test_record_sale_insufficient_stock(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba que no se puede vender más de lo disponible."""
        # Arrange
        sample_inventory.quantity = 5
        sample_inventory.save()
        initial_sale_count = Sale.select().count()
        
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 10}  # Más de lo disponible
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is False
        assert "insuficiente" in message.lower()
        
        # Verificar que el inventario no cambió
        updated_inventory = Inventory.get(Inventory.product == sample_product)
        assert updated_inventory.quantity == 5
    
    def test_record_sale_nonexistent_product(self, test_db):
        """Prueba vender un producto que no existe."""
        # Arrange
        items_to_sell = [
            {'barcode': 'NOEXISTE', 'quantity': 1}
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is False
        assert "no encontrado" in message.lower()
    
    def test_record_sale_invalid_quantity(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba vender con cantidad inválida."""
        # Arrange
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 0}  # Cantidad inválida
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is False
        assert "inválida" in message.lower()
    
    def test_record_sale_fefo_logic(self, test_db, sample_product, sample_inventory):
        """Prueba que se aplica FEFO (First Expired, First Out)."""
        # Arrange - Crear lotes con diferentes fechas de vencimiento
        batch1 = ProductBatch.create(
            product=sample_product,
            quantity=10,
            expiration_date=(datetime.now() + timedelta(days=30)).date(),
            batch_number=0,
            purchase_price=Decimal('1000.00')
        )
        batch2 = ProductBatch.create(
            product=sample_product,
            quantity=10,
            expiration_date=(datetime.now() + timedelta(days=10)).date(),  # Vence antes
            batch_number=1,
            purchase_price=Decimal('1000.00')
        )
        
        sample_inventory.quantity = 20
        sample_inventory.save()
        
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 5}
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is True
        
        # Verificar que se dedujo del lote que vence primero (batch2)
        updated_batch1 = ProductBatch.get_by_id(batch1.id)
        updated_batch2 = ProductBatch.get_by_id(batch2.id)
        
        assert updated_batch2.quantity == 5  # Se dedujo de este
        assert updated_batch1.quantity == 10  # Este no se tocó
    
    def test_record_sale_deactivates_empty_batch(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba que un lote se desactiva cuando se vacía."""
        # Arrange
        sample_batch.quantity = 3
        sample_batch.save()
        sample_inventory.quantity = 3
        sample_inventory.save()
        
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 3}
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is True
        
        # Verificar que el lote se desactivó
        updated_batch = ProductBatch.get_by_id(sample_batch.id)
        assert updated_batch.quantity == 0
        assert updated_batch.active is False
    
    def test_list_sales_history(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba listar el historial de ventas."""
        # Arrange - Registrar una venta
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 2}
        ]
        record_sale(items_to_sell)
        
        # Act
        history = list_sales_history()
        
        # Assert
        assert len(history) >= 1
        assert history[0]['product'] == sample_product.name
        assert history[0]['quantity'] == 2
    
    def test_list_sales_history_empty(self, test_db):
        """Prueba listar historial cuando no hay ventas."""
        # Act
        history = list_sales_history()
        
        # Assert
        assert history == []
    
    def test_sales_summary_by_date(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba obtener resumen de ventas por fecha."""
        # Arrange - Registrar ventas
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 1}
        ]
        record_sale(items_to_sell)
        record_sale(items_to_sell)
        
        # Act
        summary = sales_summary_by_date()
        
        # Assert
        assert len(summary) >= 1
        today_summary = summary[0]
        assert today_summary['total_sales'] == 2
        assert today_summary['total_amount'] > 0
    
    def test_record_sale_multiple_batches(self, test_db, sample_product, sample_inventory):
        """Prueba vender cantidad que requiere múltiples lotes."""
        # Arrange
        batch1 = ProductBatch.create(
            product=sample_product,
            quantity=5,
            batch_number=0,
            purchase_price=Decimal('1000.00')
        )
        batch2 = ProductBatch.create(
            product=sample_product,
            quantity=5,
            batch_number=1,
            purchase_price=Decimal('1000.00')
        )
        
        sample_inventory.quantity = 10
        sample_inventory.save()
        
        items_to_sell = [
            {'barcode': sample_product.barcode, 'quantity': 8}  # Requiere ambos lotes
        ]
        
        # Act
        success, message = record_sale(items_to_sell)
        
        # Assert
        assert success is True
        
        # Verificar que se usaron ambos lotes
        updated_batch1 = ProductBatch.get_by_id(batch1.id)
        updated_batch2 = ProductBatch.get_by_id(batch2.id)
        
        assert updated_batch1.quantity == 0  # Se vació completamente
        assert updated_batch2.quantity == 2  # Se usaron 3 de este
