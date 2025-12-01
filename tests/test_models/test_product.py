"""
Pruebas unitarias para el modelo Product.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from models.product import Product
from models.category import Category
from peewee import IntegrityError


@pytest.mark.unit
@pytest.mark.database
class TestProduct:
    """Pruebas para el modelo Product."""
    
    def test_create_product(self, test_db, sample_category):
        """Prueba crear un producto básico."""
        # Arrange & Act
        product = Product.create(
            name="Mouse Logitech",
            barcode="MOU001",
            category=sample_category,
            unit="unidad",
            location="Pasillo C - Estante 1",
            purchase_price=Decimal('15.00'),
            sale_price=Decimal('25.00'),
            active=True
        )
        
        # Assert
        assert product.id is not None
        assert product.name == "Mouse Logitech"
        assert product.barcode == "MOU001"
        assert product.category == sample_category
        assert product.purchase_price == Decimal('15.00')
        assert product.sale_price == Decimal('25.00')
        assert product.active is True
    
    def test_product_unique_barcode(self, test_db, sample_product, sample_category):
        """Prueba que el código de barras debe ser único."""
        # Act & Assert
        with pytest.raises(IntegrityError):
            Product.create(
                name="Otro Producto",
                barcode=sample_product.barcode,  # Código duplicado
                category=sample_category,
                unit="unidad",
                location="Pasillo A",
                purchase_price=Decimal('10.00'),
                sale_price=Decimal('15.00')
            )
    
    def test_product_profit_property(self, test_db, sample_product):
        """Prueba el cálculo de ganancia del producto."""
        # Act
        profit = sample_product.profit
        
        # Assert
        expected_profit = sample_product.sale_price - sample_product.purchase_price
        assert profit == expected_profit
        assert profit == Decimal('300.00')
    
    def test_product_with_expiration_date(self, test_db, sample_category):
        """Prueba crear un producto con fecha de vencimiento."""
        # Arrange
        expiration = datetime.now().date() + timedelta(days=90)
        
        # Act
        product = Product.create(
            name="Leche Entera",
            barcode="LEC001",
            category=sample_category,
            unit="litro",
            location="Refrigerador 1",
            purchase_price=Decimal('1.50'),
            sale_price=Decimal('2.00'),
            expiration_date=expiration
        )
        
        # Assert
        assert product.expiration_date == expiration
    
    def test_product_without_category(self, test_db):
        """Prueba crear un producto sin categoría (null permitido)."""
        # Act
        product = Product.create(
            name="Producto Sin Categoría",
            barcode="SIN001",
            category=None,
            unit="unidad",
            location="Almacén",
            purchase_price=Decimal('5.00'),
            sale_price=Decimal('10.00')
        )
        
        # Assert
        assert product.category is None
    
    def test_deactivate_product(self, test_db, sample_product):
        """Prueba desactivar un producto."""
        # Arrange
        assert sample_product.active is True
        
        # Act
        sample_product.active = False
        sample_product.save()
        
        # Assert
        updated_product = Product.get_by_id(sample_product.id)
        assert updated_product.active is False
    
    def test_update_product_prices(self, test_db, sample_product):
        """Prueba actualizar precios de un producto."""
        # Arrange
        new_purchase = Decimal('1100.00')
        new_sale = Decimal('1400.00')
        
        # Act
        sample_product.purchase_price = new_purchase
        sample_product.sale_price = new_sale
        sample_product.save()
        
        # Assert
        updated_product = Product.get_by_id(sample_product.id)
        assert updated_product.purchase_price == new_purchase
        assert updated_product.sale_price == new_sale
        assert updated_product.profit == Decimal('300.00')
    
    def test_product_date_added_auto_set(self, test_db, sample_category):
        """Prueba que date_added se establece automáticamente."""
        # Act
        product = Product.create(
            name="Teclado",
            barcode="TEC001",
            category=sample_category,
            unit="unidad",
            location="Pasillo A",
            purchase_price=Decimal('30.00'),
            sale_price=Decimal('50.00')
        )
        
        # Assert
        assert product.date_added is not None
        assert isinstance(product.date_added, datetime)
    
    def test_list_products_by_category(self, test_db, sample_category, sample_product):
        """Prueba listar productos por categoría."""
        # Arrange - Crear otro producto en la misma categoría
        Product.create(
            name="Monitor",
            barcode="MON001",
            category=sample_category,
            unit="unidad",
            location="Pasillo A",
            purchase_price=Decimal('200.00'),
            sale_price=Decimal('300.00')
        )
        
        # Act
        products = list(sample_category.products)
        
        # Assert
        assert len(products) == 2
    
    def test_product_with_batches(self, test_db, sample_product, sample_batch):
        """Prueba que un producto puede tener lotes asociados."""
        # Act
        batches = list(sample_product.batches)
        
        # Assert
        assert len(batches) == 1
        assert batches[0] == sample_batch
