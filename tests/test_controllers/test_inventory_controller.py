"""
Pruebas unitarias para inventory_controller.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from controllers import (
    record_purchase,
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    list_expiring_products,
    list_categories,
    list_batches_for_product
)
from models.product import Product
from models.inventory import Inventory
from models.batch import ProductBatch


@pytest.mark.unit
@pytest.mark.database
class TestInventoryController:
    """Pruebas para el controlador de inventario."""
    
    def test_record_purchase_new_batch(self, test_db, sample_product, sample_inventory):
        # Arrange
        initial_quantity = sample_inventory.quantity
        purchase_qty = 20
        expiration = (datetime.now() + timedelta(days=180)).date()
        
        # Act
        success, message = record_purchase(
            product_barcode=sample_product.barcode,
            quantity=purchase_qty,
            purchase_price='1200.00',
            expiration_date=expiration
        )
        
        # Assert
        assert success is True
        
        # Verificar que se creó el lote
        batches = list(ProductBatch.select().where(ProductBatch.product == sample_product))
        assert len(batches) >= 1
        
        # Verificar que se actualizó el inventario
        updated_inventory = Inventory.get(Inventory.product == sample_product)
        assert updated_inventory.quantity == initial_quantity + purchase_qty
    
    def test_record_purchase_existing_batch(self, test_db, sample_product, sample_batch, sample_inventory):
        """Prueba registrar una compra agregando a un lote existente."""
        # Arrange
        initial_batch_qty = sample_batch.quantity
        initial_inventory_qty = sample_inventory.quantity
        purchase_qty = 5
        
        # Act - Compra con la misma fecha de vencimiento
        success, message = record_purchase(
            product_barcode=sample_product.barcode,
            quantity=purchase_qty,
            purchase_price='1200.00',
            expiration_date=sample_batch.expiration_date
        )
        
        # Assert
        assert success is True
        
        # Verificar que se actualizó el lote existente
        updated_batch = ProductBatch.get_by_id(sample_batch.id)
        assert updated_batch.quantity == initial_batch_qty + purchase_qty
        
        # Verificar inventario
        updated_inventory = Inventory.get(Inventory.product == sample_product)
        assert updated_inventory.quantity == initial_inventory_qty + purchase_qty
    
    def test_list_products_inventory(self, test_db, sample_product, sample_inventory):
        """Prueba listar todos los productos con inventario."""
        # Act - option=1 lista productos activos
        results = list_products_inventory(option=1)
        
        # Assert
        assert len(results) >= 1
        assert any(r['barcode'] == sample_product.barcode for r in results)
    
    def test_list_available_products(self, test_db, sample_product, sample_inventory):
        """Prueba listar solo productos con stock disponible."""
        # Arrange
        sample_inventory.quantity = 10
        sample_inventory.save()
        
        # Act
        results = list_available_products()
        
        # Assert
        assert len(results) >= 1
        assert any(r['barcode'] == sample_product.barcode for r in results)
    
    def test_list_out_of_stock_products(self, test_db, sample_product, sample_inventory):
        """Prueba listar solo productos sin stock."""
        # Arrange
        sample_inventory.quantity = 0
        sample_inventory.save()
        
        # Act
        results = list_out_of_stock_products()
        
        # Assert
        assert len(results) >= 1
        assert any(r['barcode'] == sample_product.barcode for r in results)
    
    def test_list_expiring_products(self, test_db, sample_category):
        """Prueba listar productos próximos a vencer."""
        # Arrange - Crear producto que vence pronto
        expiring_product = Product.create(
            name="Producto Venciendo",
            barcode="EXP001",
            category=sample_category,
            unit="unidad",
            location="Almacén",
            purchase_price=Decimal('10.00'),
            sale_price=Decimal('15.00'),
            expiration_date=(datetime.now() + timedelta(days=5)).date()
        )
        
        Inventory.create(
            product=expiring_product,
            quantity=10
        )

        # Crear un lote para que aparezca en el reporte
        ProductBatch.create(
            product=expiring_product,
            quantity=10,
            expiration_date=expiring_product.expiration_date,
            batch_number=0,
            purchase_price=expiring_product.purchase_price
        )
        
        # Act
        results = list_expiring_products(days=10)
        
        # Assert
        assert len(results) >= 1
        assert any(r['barcode'] == 'EXP001' for r in results)
    
    def test_list_categories(self, test_db, sample_category, sample_category_2):
        """Prueba listar todas las categorías."""
        # Act
        results = list_categories()
        
        # Assert
        assert len(results) == 2
        category_names = [c['name'] for c in results]
        assert sample_category.name in category_names
        assert sample_category_2.name in category_names
    
    def test_list_batches_for_product(self, test_db, sample_product, sample_batch, sample_batch_2):
        """Prueba listar lotes de un producto."""
        # Act
        results = list_batches_for_product(sample_product.barcode)
        
        # Assert
        assert len(results) >= 2
        batch_numbers = [b['batch_number'] for b in results]
        assert sample_batch.batch_number in batch_numbers
        assert sample_batch_2.batch_number in batch_numbers
    
    def test_list_batches_for_nonexistent_product(self, test_db):
        """Prueba listar lotes de un producto que no existe."""
        # Act
        results = list_batches_for_product('NOEXISTE')
        
        # Assert
        assert results == []
