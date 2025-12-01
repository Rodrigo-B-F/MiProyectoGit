"""
Pruebas unitarias para batch_controller.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from controllers import (
    list_product_batches,
    get_batch_summary,
    consolidate_inventory
)
from models.batch import ProductBatch
from models.inventory import Inventory


@pytest.mark.unit
@pytest.mark.database
class TestBatchController:
    """Pruebas para el controlador de lotes."""
    
    def test_list_product_batches(self, test_db, sample_product, sample_batch, sample_batch_2):
        """Prueba listar lotes de un producto."""
        # Act
        results = list_product_batches(sample_product.id)
        
        # Assert
        assert len(results) == 2
        # Los lotes están ordenados por fecha de vencimiento (FEFO)
        # sample_batch_2 vence antes (180 días) que sample_batch (365 días)
        batch_numbers = [r['batch_number'] for r in results]
        assert sample_batch.batch_number in batch_numbers
        assert sample_batch_2.batch_number in batch_numbers
    
    def test_list_product_batches_ordered_by_expiration(self, test_db, sample_product):
        """Prueba que los lotes se ordenan por fecha de vencimiento (FEFO)."""
        # Arrange - Crear lotes con diferentes fechas de vencimiento
        batch1 = ProductBatch.create(
            product=sample_product,
            quantity=10,
            expiration_date=(datetime.now() + timedelta(days=30)).date(),
            batch_number=0,
            purchase_price=Decimal('100.00')
        )
        batch2 = ProductBatch.create(
            product=sample_product,
            quantity=15,
            expiration_date=(datetime.now() + timedelta(days=10)).date(),  # Vence antes
            batch_number=1,
            purchase_price=Decimal('100.00')
        )
        batch3 = ProductBatch.create(
            product=sample_product,
            quantity=20,
            expiration_date=(datetime.now() + timedelta(days=60)).date(),
            batch_number=2,
            purchase_price=Decimal('100.00')
        )
        
        # Act
        results = list_product_batches(sample_product.id)
        
        # Assert
        assert len(results) == 3
        # El primer lote debe ser el que vence más pronto
        assert results[0]['batch_number'] == batch2.batch_number
        assert results[1]['batch_number'] == batch1.batch_number
        assert results[2]['batch_number'] == batch3.batch_number
    
    def test_list_product_batches_only_active(self, test_db, sample_product):
        """Prueba que solo se listan lotes activos."""
        # Arrange
        active_batch = ProductBatch.create(
            product=sample_product,
            quantity=10,
            batch_number=0,
            active=True,
            purchase_price=Decimal('100.00')
        )
        inactive_batch = ProductBatch.create(
            product=sample_product,
            quantity=0,
            batch_number=1,
            active=False,
            purchase_price=Decimal('100.00')
        )
        
        # Act
        results = list_product_batches(sample_product.id)
        
        # Assert
        assert len(results) == 1
        assert results[0]['batch_number'] == active_batch.batch_number
    
    def test_list_product_batches_nonexistent_product(self, test_db):
        """Prueba listar lotes de un producto que no existe."""
        # Act
        results = list_product_batches(99999)
        
        # Assert
        assert results == []
    
    def test_get_batch_summary(self, test_db, sample_product, sample_batch, sample_batch_2):
        """Prueba obtener resumen de lotes de un producto."""
        # Act
        summary = get_batch_summary(sample_product.barcode)
        
        # Assert
        assert summary is not None
        assert "Lote" in summary
        assert str(sample_batch.batch_number) in summary
        assert str(sample_batch_2.batch_number) in summary
    
    def test_get_batch_summary_nonexistent_product(self, test_db):
        """Prueba obtener resumen de lotes de un producto que no existe."""
        # Act
        summary = get_batch_summary('NOEXISTE')
        
        # Assert
        assert summary is None
    
    def test_get_batch_summary_no_batches(self, test_db, sample_product):
        """Prueba obtener resumen cuando no hay lotes."""
        # Act
        summary = get_batch_summary(sample_product.barcode)
        
        # Assert
        assert summary is None
    
    def test_consolidate_inventory(self, test_db, sample_product, sample_inventory):
        """Prueba consolidar inventario desde lotes."""
        # Arrange - Crear lotes
        batch1 = ProductBatch.create(
            product=sample_product,
            quantity=10,
            batch_number=0,
            active=True,
            purchase_price=Decimal('100.00')
        )
        batch2 = ProductBatch.create(
            product=sample_product,
            quantity=15,
            batch_number=1,
            active=True,
            purchase_price=Decimal('100.00')
        )
        batch3 = ProductBatch.create(
            product=sample_product,
            quantity=0,
            batch_number=2,
            active=False,  # Inactivo, no debe contar
            purchase_price=Decimal('100.00')
        )
        
        # Act
        success, message = consolidate_inventory(sample_product.id)
        
        # Assert
        assert success is True
        
        # Verificar que el inventario se actualizó correctamente
        updated_inventory = Inventory.get(Inventory.product == sample_product)
        assert updated_inventory.quantity == 25  # 10 + 15
    
    def test_consolidate_inventory_nonexistent_product(self, test_db):
        """Prueba consolidar inventario de un producto que no existe."""
        # Act
        success, message = consolidate_inventory(99999)
        
        # Assert
        assert success is False
        assert "no encontrado" in message.lower()
    
    def test_batch_with_no_expiration(self, test_db, sample_product):
        """Prueba lotes sin fecha de vencimiento."""
        # Arrange
        batch = ProductBatch.create(
            product=sample_product,
            quantity=50,
            expiration_date=None,
            batch_number=10,
            purchase_price=Decimal('100.00')
        )
        
        # Act
        results = list_product_batches(sample_product.id)
        
        # Assert
        assert len(results) >= 1
        batch_data = next(b for b in results if b['batch_number'] == 10)
        assert batch_data['expiration_date'] is None
        assert batch_data['expiration_display'] == "Sin fecha"
