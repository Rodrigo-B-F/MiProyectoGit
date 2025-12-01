"""
Configuración de fixtures compartidas para todas las pruebas.
Este archivo se ejecuta automáticamente por pytest antes de las pruebas.
"""

import pytest
import sys
import os
from peewee import SqliteDatabase
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Importar modelos
from models.category import Category
from models.product import Product
from models.batch import ProductBatch
from models.inventory import Inventory, StockMovement
from models.sale import Sale, SaleItem

# Lista de todos los modelos
MODELS = [Category, Product, ProductBatch, Inventory, StockMovement, Sale, SaleItem]


@pytest.fixture
def test_db():
    """
    Fixture que crea una base de datos de prueba en memoria.
    Se ejecuta antes de cada prueba y se limpia después.
    """
    # Crear base de datos en memoria
    test_database = SqliteDatabase(':memory:')
    
    # Vincular modelos a la base de datos de prueba
    test_database.bind(MODELS, bind_refs=False, bind_backrefs=False)
    
    # Crear tablas
    test_database.create_tables(MODELS)
    
    yield test_database
    
    # Limpiar después de la prueba
    test_database.drop_tables(MODELS)
    test_database.close()


@pytest.fixture
def sample_category(test_db):
    """Fixture que crea una categoría de ejemplo."""
    return Category.create(
        name="Electrónica",
        description="Productos electrónicos y tecnología"
    )


@pytest.fixture
def sample_category_2(test_db):
    """Fixture que crea una segunda categoría de ejemplo."""
    return Category.create(
        name="Alimentos",
        description="Productos alimenticios"
    )


@pytest.fixture
def sample_product(test_db, sample_category):
    """Fixture que crea un producto de ejemplo."""
    return Product.create(
        name="Laptop HP",
        barcode="LAP001",
        category=sample_category,
        unit="unidad",
        location="Pasillo A - Estante 1",
        purchase_price=Decimal('1200.00'),
        sale_price=Decimal('1500.00'),
        expiration_date=None,
        active=True
    )


@pytest.fixture
def sample_product_2(test_db, sample_category_2):
    """Fixture que crea un segundo producto de ejemplo."""
    return Product.create(
        name="Arroz Premium",
        barcode="ARR001",
        category=sample_category_2,
        unit="kg",
        location="Pasillo B - Estante 2",
        purchase_price=Decimal('2.50'),
        sale_price=Decimal('3.00'),
        expiration_date=datetime.now().date() + timedelta(days=180),
        active=True
    )


@pytest.fixture
def sample_batch(test_db, sample_product):
    """Fixture que crea un lote de ejemplo."""
    return ProductBatch.create(
        product=sample_product,
        quantity=10,
        expiration_date=datetime.now().date() + timedelta(days=365),
        purchase_date=datetime.now(),
        purchase_price=Decimal('1200.00'),
        batch_number=0,
        active=True
    )


@pytest.fixture
def sample_batch_2(test_db, sample_product):
    """Fixture que crea un segundo lote de ejemplo."""
    return ProductBatch.create(
        product=sample_product,
        quantity=5,
        expiration_date=datetime.now().date() + timedelta(days=180),
        purchase_date=datetime.now(),
        purchase_price=Decimal('1150.00'),
        batch_number=1,
        active=True
    )


@pytest.fixture
def sample_inventory(test_db, sample_product):
    """Fixture que crea un registro de inventario."""
    return Inventory.create(
        product=sample_product,
        quantity=15,
        last_updated=datetime.now()
    )


@pytest.fixture
def sample_sale(test_db):
    """Fixture que crea una venta de ejemplo."""
    return Sale.create(
        timestamp=datetime.now(),
        total=Decimal('3000.00')
    )


@pytest.fixture
def sample_sale_item(test_db, sample_sale, sample_product):
    """Fixture que crea un item de venta."""
    return SaleItem.create(
        sale=sample_sale,
        product=sample_product,
        quantity=2,
        unit_price=Decimal('1500.00'),
        subtotal=Decimal('3000.00')
    )
