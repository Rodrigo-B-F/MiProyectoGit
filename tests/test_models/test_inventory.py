"""
Pruebas unitarias para los modelos Inventory y StockMovement.
"""

import pytest
from datetime import datetime
from models.inventory import Inventory, StockMovement
from peewee import IntegrityError


@pytest.mark.unit
@pytest.mark.database
class TestInventory:
    """Pruebas para el modelo Inventory."""
    
    def test_create_inventory(self, test_db, sample_product):
        """Prueba crear un registro de inventario."""
        # Arrange & Act
        inventory = Inventory.create(
            product=sample_product,
            quantity=100
        )
        
        # Assert
        assert inventory.id is not None
        assert inventory.product == sample_product
        assert inventory.quantity == 100
    
    def test_inventory_unique_per_product(self, test_db, sample_product, sample_inventory):
        """Prueba que solo puede haber un registro de inventario por producto."""
        # Act & Assert
        with pytest.raises(IntegrityError):
            Inventory.create(
                product=sample_product,
                quantity=50
            )
    
    def test_update_inventory_quantity(self, test_db, sample_inventory):
        """Prueba actualizar la cantidad en inventario."""
        # Arrange
        new_quantity = 25
        
        # Act
        sample_inventory.quantity = new_quantity
        sample_inventory.save()
        
        # Assert
        updated_inventory = Inventory.get_by_id(sample_inventory.id)
        assert updated_inventory.quantity == new_quantity
    
    def test_inventory_last_updated_auto_set(self, test_db, sample_product):
        """Prueba que last_updated se establece automáticamente."""
        # Act
        inventory = Inventory.create(
            product=sample_product,
            quantity=50
        )
        
        # Assert
        assert inventory.last_updated is not None
        assert isinstance(inventory.last_updated, datetime)
    
    def test_inventory_default_quantity(self, test_db, sample_product):
        """Prueba el valor por defecto de quantity."""
        # Act
        inventory = Inventory.create(
            product=sample_product
        )
        
        # Assert
        assert inventory.quantity == 0


@pytest.mark.unit
@pytest.mark.database
class TestStockMovement:
    """Pruebas para el modelo StockMovement."""
    
    def test_create_stock_movement_entry(self, test_db, sample_product):
        """Prueba crear un movimiento de entrada de stock."""
        # Arrange & Act
        movement = StockMovement.create(
            product=sample_product,
            batch=0,
            change=50,  # Entrada positiva
            reason="purchase",
            reference="PO-001"
        )
        
        # Assert
        assert movement.id is not None
        assert movement.product == sample_product
        assert movement.change == 50
        assert movement.reason == "purchase"
    
    def test_create_stock_movement_exit(self, test_db, sample_product):
        """Prueba crear un movimiento de salida de stock."""
        # Arrange & Act
        movement = StockMovement.create(
            product=sample_product,
            batch=0,
            change=-10,  # Salida negativa
            reason="sale",
            reference="SALE-001"
        )
        
        # Assert
        assert movement.change == -10
        assert movement.reason == "sale"
    
    def test_stock_movement_timestamp_auto_set(self, test_db, sample_product):
        """Prueba que timestamp se establece automáticamente."""
        # Act
        movement = StockMovement.create(
            product=sample_product,
            change=25,
            reason="adjustment"
        )
        
        # Assert
        assert movement.timestamp is not None
        assert isinstance(movement.timestamp, datetime)
    
    def test_stock_movement_without_batch(self, test_db, sample_product):
        """Prueba crear un movimiento sin referencia a lote."""
        # Act
        movement = StockMovement.create(
            product=sample_product,
            batch=None,
            change=15,
            reason="adjustment"
        )
        
        # Assert
        assert movement.batch is None
    
    def test_multiple_stock_movements(self, test_db, sample_product):
        """Prueba crear múltiples movimientos para un producto."""
        # Act
        movement1 = StockMovement.create(
            product=sample_product,
            change=100,
            reason="purchase"
        )
        movement2 = StockMovement.create(
            product=sample_product,
            change=-20,
            reason="sale"
        )
        movement3 = StockMovement.create(
            product=sample_product,
            change=-5,
            reason="adjustment"
        )
        
        # Assert
        movements = list(sample_product.movements)
        assert len(movements) == 3
        assert movement1 in movements
        assert movement2 in movements
        assert movement3 in movements
    
    def test_calculate_net_stock_from_movements(self, test_db, sample_product):
        """Prueba calcular el stock neto a partir de movimientos."""
        # Arrange
        StockMovement.create(product=sample_product, change=100, reason="purchase")
        StockMovement.create(product=sample_product, change=50, reason="purchase")
        StockMovement.create(product=sample_product, change=-30, reason="sale")
        StockMovement.create(product=sample_product, change=-10, reason="sale")
        
        # Act
        movements = list(sample_product.movements)
        net_stock = sum(m.change for m in movements)
        
        # Assert
        assert net_stock == 110  # 100 + 50 - 30 - 10
