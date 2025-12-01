"""
Pruebas unitarias para el modelo ProductBatch.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from models.batch import ProductBatch
from peewee import IntegrityError


@pytest.mark.unit
@pytest.mark.database
class TestProductBatch:
    """Pruebas para el modelo ProductBatch."""
    
    def test_create_batch(self, test_db, sample_product):
        """Prueba crear un lote básico."""
        # Arrange & Act
        batch = ProductBatch.create(
            product=sample_product,
            quantity=50,
            expiration_date=datetime.now().date() + timedelta(days=180),
            purchase_date=datetime.now(),
            purchase_price=Decimal('1150.00'),
            batch_number=0,
            active=True
        )
        
        # Assert
        assert batch.id is not None
        assert batch.product == sample_product
        assert batch.quantity == 50
        assert batch.batch_number == 0
        assert batch.active is True
    
    def test_batch_unique_per_product(self, test_db, sample_product, sample_batch):
        """Prueba que el número de lote debe ser único por producto."""
        # Act & Assert
        with pytest.raises(IntegrityError):
            ProductBatch.create(
                product=sample_product,
                quantity=20,
                expiration_date=datetime.now().date() + timedelta(days=90),
                purchase_date=datetime.now(),
                purchase_price=Decimal('1200.00'),
                batch_number=sample_batch.batch_number,  # Número duplicado
                active=True
            )
    
    def test_batch_str_representation(self, test_db, sample_batch):
        """Prueba la representación en string del lote."""
        # Act
        result = str(sample_batch)
        
        # Assert
        assert "Lote" in result
        assert str(sample_batch.batch_number) in result
        assert "Vence:" in result
    
    def test_batch_without_expiration(self, test_db, sample_product):
        """Prueba crear un lote sin fecha de vencimiento."""
        # Act
        batch = ProductBatch.create(
            product=sample_product,
            quantity=100,
            expiration_date=None,
            purchase_date=datetime.now(),
            purchase_price=Decimal('1000.00'),
            batch_number=5,
            active=True
        )
        
        # Assert
        assert batch.expiration_date is None
        result = str(batch)
        assert "Vence:" not in result
    
    def test_update_batch_quantity(self, test_db, sample_batch):
        """Prueba actualizar la cantidad de un lote."""
        # Arrange
        original_quantity = sample_batch.quantity
        new_quantity = original_quantity - 3
        
        # Act
        sample_batch.quantity = new_quantity
        sample_batch.save()
        
        # Assert
        updated_batch = ProductBatch.get_by_id(sample_batch.id)
        assert updated_batch.quantity == new_quantity
    
    def test_deactivate_batch_when_empty(self, test_db, sample_batch):
        """Prueba desactivar un lote cuando se vacía."""
        # Act
        sample_batch.quantity = 0
        sample_batch.active = False
        sample_batch.save()
        
        # Assert
        updated_batch = ProductBatch.get_by_id(sample_batch.id)
        assert updated_batch.quantity == 0
        assert updated_batch.active is False
    
    def test_batch_purchase_date_auto_set(self, test_db, sample_product):
        """Prueba que purchase_date se establece automáticamente."""
        # Act
        batch = ProductBatch.create(
            product=sample_product,
            quantity=25,
            expiration_date=datetime.now().date() + timedelta(days=365),
            purchase_price=Decimal('1100.00'),
            batch_number=10
        )
        
        # Assert
        assert batch.purchase_date is not None
        assert isinstance(batch.purchase_date, datetime)
    
    def test_multiple_batches_same_product(self, test_db, sample_product):
        """Prueba crear múltiples lotes para el mismo producto."""
        # Act
        batch1 = ProductBatch.create(
            product=sample_product,
            quantity=10,
            batch_number=0,
            purchase_price=Decimal('1000.00')
        )
        batch2 = ProductBatch.create(
            product=sample_product,
            quantity=15,
            batch_number=1,
            purchase_price=Decimal('1050.00')
        )
        batch3 = ProductBatch.create(
            product=sample_product,
            quantity=20,
            batch_number=2,
            purchase_price=Decimal('1100.00')
        )
        
        # Assert
        batches = list(sample_product.batches)
        assert len(batches) == 3
        assert batch1 in batches
        assert batch2 in batches
        assert batch3 in batches
    
    def test_batch_expiration_check(self, test_db, sample_product):
        """Prueba verificar si un lote está vencido."""
        # Arrange - Crear lote vencido
        expired_batch = ProductBatch.create(
            product=sample_product,
            quantity=5,
            expiration_date=datetime.now().date() - timedelta(days=1),
            purchase_price=Decimal('1000.00'),
            batch_number=20
        )
        
        # Act & Assert
        assert expired_batch.expiration_date < datetime.now().date()
    
    def test_batch_default_values(self, test_db, sample_product):
        """Prueba los valores por defecto del lote."""
        # Act
        batch = ProductBatch.create(
            product=sample_product,
            batch_number=30
        )
        
        # Assert
        assert batch.quantity == 0
        assert batch.purchase_price == Decimal('0.00')
        assert batch.active is True
